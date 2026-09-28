#!/usr/bin/env python3
"""
arm_v0_ik_commander.py — Analytical Inverse Kinematics Commander for Devotics Arm V0

Features:
- Takes desired 3D Cartesian coordinates (X, Y, Z in cm)
- Calculates exact joint angles using analytical 2-link + yaw Inverse Kinematics
- Validates workspace reachability and safe servo limits
- Sends joint commands to /arm_v0/joint_command
- Interactive prompt:
    > Enter target: 8.0 -3.0 2.5
    > home
    > open
    > close
    > q
"""

import sys
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class ArmV0IKCommander(Node):
    def __init__(self):
        super().__init__('arm_v0_ik_commander')

        self.cmd_pub = self.create_publisher(
            JointState,
            '/arm_v0/joint_command',
            10
        )

        self.joint_names = [
            'base_joint',
            'shoulder_joint',
            'elbow_joint',
            'gripper_joint'
        ]

        # -------------------------------------------------------------
        # Physical Link Lengths (meters) — measured from real arm
        # -------------------------------------------------------------
        self.d_base = 0.055  # 5.5 cm: table to shoulder axis (dim_F + dim_A)
        self.L1     = 0.040  # 4.0 cm: shoulder to elbow axis (dim_B)
        self.L2     = 0.085  # 8.5 cm: elbow axis to fingertip (dim_C + dim_D = 4.0 + 4.5)

        # Joint safe limits (radians)
        self.j1_min = math.radians(-60.0)
        self.j1_max = math.radians(60.0)

        # Shoulder can pitch forward up to 85° for deep reach to table
        self.j2_min = math.radians(-30.0)
        self.j2_max = math.radians(85.0)

        # Elbow can pitch down up to 85°
        self.j3_min = math.radians(-30.0)
        self.j3_max = math.radians(85.0)

        # Track last sent angles (start at HOME)
        self.current_q = [0.0, 0.0, 0.0, 0.0]

    def solve_ik(self, x: float, y: float, z: float):
        """
        Analytical Inverse Kinematics for Devotics Arm V0.
        Kinematic equations:
            r = L1 * sin(q2) + L2 * sin(q2 + q3)
            z_rel = L1 * cos(q2) + L2 * cos(q2 + q3)
        """
        # 1. Base yaw angle (q1)
        q1 = math.atan2(y, x)
        if not (self.j1_min <= q1 <= self.j1_max):
            return None, f"Base angle {math.degrees(q1):.1f}° exceeds limit [-60°, +60°]"

        r = math.sqrt(x**2 + y**2)
        z_rel = z - self.d_base

        dist_sq = r**2 + z_rel**2
        dist = math.sqrt(dist_sq)

        # Distance reachability check
        if dist > (self.L1 + self.L2):
            return None, f"Target too far! Distance={dist*100:.1f} cm (Max reach={(self.L1+self.L2)*100:.1f} cm)"
        if dist < abs(self.L1 - self.L2):
            return None, f"Target too close! Distance={dist*100:.1f} cm (Min reach={abs(self.L1-self.L2)*100:.1f} cm)"

        # 2. Law of Cosines for elbow angle q3:
        # r^2 + z_rel^2 = L1^2 + L2^2 + 2*L1*L2*cos(q3)
        cos_q3 = (dist_sq - self.L1**2 - self.L2**2) / (2.0 * self.L1 * self.L2)
        cos_q3 = max(-1.0, min(1.0, cos_q3))

        # Try both solutions: positive q3 (bend down) and negative q3 (bend up)
        q3_candidates = [math.acos(cos_q3), -math.acos(cos_q3)]

        for q3 in q3_candidates:
            if not (self.j3_min <= q3 <= self.j3_max):
                continue

            # Solve for q2:
            # Using the sum-of-angles expansion:
            # r     = (L1 + L2*cos(q3)) * sin(q2) + (L2*sin(q3)) * cos(q2)
            # z_rel = (L1 + L2*cos(q3)) * cos(q2) - (L2*sin(q3)) * sin(q2)
            A = self.L1 + self.L2 * math.cos(q3)
            B = self.L2 * math.sin(q3)

            # Let phi = atan2(B, A):
            # r     = sqrt(A^2 + B^2) * sin(q2 + phi)
            # z_rel = sqrt(A^2 + B^2) * cos(q2 + phi)
            # Therefore: q2 + phi = atan2(r, z_rel)
            phi = math.atan2(B, A)
            q2 = math.atan2(r, z_rel) - phi

            # Normalize q2 to [-pi, pi]
            q2 = (q2 + math.pi) % (2.0 * math.pi) - math.pi

            if self.j2_min <= q2 <= self.j2_max:
                return (q1, q2, q3), "OK"

        return None, (
            f"No solution within servo limits [-30°, +60°]! "
            f"Required elbow={math.degrees(math.acos(cos_q3)):.1f}°. "
            f"Try a target further forward (e.g. X = 9.5 to 11.0 cm)."
        )

    def send_command(self, q1, q2, q3, q4):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [q1, q2, q3, q4]
        self.cmd_pub.publish(msg)
        self.current_q = [q1, q2, q3, q4]

    def run_interactive(self):
        print("\n=======================================================")
        print("  DEVOTICS ARM V0 — INVERSE KINEMATICS COMMANDER")
        print("=======================================================")
        print(f"Arm link lengths: L1 = {self.L1*100:.1f} cm, L2 = {self.L2*100:.1f} cm")
        print(f"Max reach: {(self.L1+self.L2)*100:.1f} cm | Shoulder height: {self.d_base*100:.1f} cm")
        print("\nCommands:")
        print("  X Y Z    -> Move to coordinate in cm (e.g., '8.0 0.0 5.0')")
        print("  home     -> Move to default upright pose")
        print("  open     -> Open gripper")
        print("  close    -> Close gripper")
        print("  q / exit -> Quit")
        print("=======================================================\n")

        gripper_pos = 0.0  # neutral

        while rclpy.ok():
            try:
                cmd = input("IK Command (X Y Z cm) > ").strip().lower()
                if not cmd:
                    continue

                if cmd in ['q', 'exit', 'quit']:
                    print("Exiting IK Commander.")
                    break

                if cmd == 'home':
                    self.send_command(0.0, 0.0, 0.0, 0.0)
                    gripper_pos = 0.0
                    print("▶ Moved to HOME (all joints centered).")
                    continue

                if cmd == 'open':
                    gripper_pos = math.radians(20.0)
                    self.send_command(self.current_q[0], self.current_q[1], self.current_q[2], gripper_pos)
                    print("▶ Gripper OPENED.")
                    continue

                if cmd == 'close':
                    gripper_pos = math.radians(-30.0)
                    self.send_command(self.current_q[0], self.current_q[1], self.current_q[2], gripper_pos)
                    print("▶ Gripper CLOSED.")
                    continue

                parts = cmd.split()
                if len(parts) != 3:
                    print("❌ Please enter 3 numbers: X Y Z in cm (e.g. '8.0 -2.0 4.0')")
                    continue

                x_cm = float(parts[0])
                y_cm = float(parts[1])
                z_cm = float(parts[2])

                # Convert cm to meters for math
                x_m = x_cm / 100.0
                y_m = y_cm / 100.0
                z_m = z_cm / 100.0

                angles, status = self.solve_ik(x_m, y_m, z_m)
                if angles is None:
                    print(f"❌ IK Error: {status}")
                    continue

                q1, q2, q3 = angles
                print(f"✅ IK Solved:")
                print(f"   Base (J1)     = {math.degrees(q1):+6.1f}° (servo {int(round(90+math.degrees(q1)))}°)")
                print(f"   Shoulder (J2) = {math.degrees(q2):+6.1f}° (servo {int(round(90+math.degrees(q2)))}°)")
                print(f"   Elbow (J3)    = {math.degrees(q3):+6.1f}° (servo {int(round(90+math.degrees(q3)))}°)")

                self.send_command(q1, q2, q3, gripper_pos)
                print("▶ Sent to arm!")

            except ValueError:
                print("❌ Invalid input! Please enter numbers like: 8.0 0.0 5.0")
            except (KeyboardInterrupt, EOFError):
                break


def main():
    rclpy.init()
    node = ArmV0IKCommander()
    node.run_interactive()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
