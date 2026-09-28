#!/usr/bin/env python3
"""
arm_v0_ik_palletizer.py — Cartesian IK-Based 4-Object Palletizer for Devotics Arm V0

Task:
    Transfer 4 stacked objects from the Pick Station (Left: X=9cm, Y=5cm)
    to the Place Station (Right: X=9cm, Y=-5cm) using pure Inverse Kinematics.

Zero hardcoded angles!
All motions are specified in real-world centimeters (X, Y, Z).
"""

import sys
import time
import math
import argparse
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


def deg2rad(deg: float) -> float:
    return math.radians(deg)


class ArmV0IKPalletizer(Node):
    def __init__(self, mode='interactive', settle_time=1.5):
        super().__init__('arm_v0_ik_palletizer')
        self.mode = mode
        self.settle_time = settle_time

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
        self.d_base = 0.055  # 5.5 cm: table to shoulder axis (dim_F + dim_A = 3.0 + 2.5)
        self.L1     = 0.040  # 4.0 cm: shoulder to elbow axis (dim_B)
        self.L2     = 0.085  # 8.5 cm: elbow axis to fingertip (dim_C + dim_D = 4.0 + 4.5)

        # Joint limits (radians)
        self.j1_min = math.radians(-60.0)
        self.j1_max = math.radians(60.0)
        self.j2_min = math.radians(-30.0)
        self.j2_max = math.radians(85.0)
        self.j3_min = math.radians(-30.0)
        self.j3_max = math.radians(85.0)

        # -------------------------------------------------------------
        # Cartesian Task Space Definition (Centimeters)
        # -------------------------------------------------------------
        # Pick from RIGHT (negative Y)
        self.PICK_X  =  9.0   # cm
        self.PICK_Y  = -4.5   # cm (Right side)
        
        # Place at LEFT (positive Y)
        self.PLACE_X =  9.0   # cm
        self.PLACE_Y =  4.5   # cm (Left side)

        # Clearance height for lifting and swinging above the stack (cm)
        self.CLEARANCE_Z = 8.0  # cm

        # Layer heights directly measured from tabletop (Z in cm):
        # 4 items, each 1.0 cm thick:
        # Level 1 = 1.0 cm (bottom item sitting on table)
        # Level 2 = 2.0 cm
        # Level 3 = 3.0 cm
        # Level 4 = 4.0 cm (top item of stack)
        self.layer_cmd_z = {
            1: 1.0,
            2: 2.0,
            3: 3.0,
            4: 4.0,
        }

        # Gripper values (radians)
        self.GRIPPER_OPEN  = deg2rad(20.0)   # servo = 110°
        self.GRIPPER_CLOSE = deg2rad(-30.0)  # servo = 60°

        self.current_gripper = self.GRIPPER_OPEN

    def solve_ik(self, x_cm: float, y_cm: float, z_cm: float):
        """
        Convert (x, y, z) in cm to joint angles (q1, q2, q3) in radians.
        """
        x = x_cm / 100.0
        y = y_cm / 100.0
        z = z_cm / 100.0

        # 1. Base yaw (q1)
        q1 = math.atan2(y, x)
        if not (self.j1_min <= q1 <= self.j1_max):
            return None, f"Base angle {math.degrees(q1):.1f}° out of range"

        # 2. Planar projection (r, z_rel)
        r = math.sqrt(x**2 + y**2)
        z_rel = z - self.d_base
        dist_sq = r**2 + z_rel**2
        dist = math.sqrt(dist_sq)

        if dist > (self.L1 + self.L2) or dist < abs(self.L1 - self.L2):
            return None, f"Target ({x_cm}, {y_cm}, {z_cm}) out of reach (dist={dist*100:.1f} cm)"

        # 3. Law of Cosines for elbow (q3)
        cos_q3 = (dist_sq - self.L1**2 - self.L2**2) / (2.0 * self.L1 * self.L2)
        cos_q3 = max(-1.0, min(1.0, cos_q3))

        for q3 in [math.acos(cos_q3), -math.acos(cos_q3)]:
            if not (self.j3_min <= q3 <= self.j3_max):
                continue

            A = self.L1 + self.L2 * math.cos(q3)
            B = self.L2 * math.sin(q3)
            phi = math.atan2(B, A)
            q2 = math.atan2(r, z_rel) - phi
            q2 = (q2 + math.pi) % (2.0 * math.pi) - math.pi

            if self.j2_min <= q2 <= self.j2_max:
                return (q1, q2, q3), "OK"

        return None, "Joint limit exceeded"

    def move_to_xyz(self, x_cm: float, y_cm: float, z_cm: float, desc=""):
        angles, status = self.solve_ik(x_cm, y_cm, z_cm)
        if angles is None:
            self.get_logger().error(f"Cannot reach ({x_cm:.1f}, {y_cm:.1f}, {z_cm:.1f})! {status}")
            return False

        q1, q2, q3 = angles

        if self.mode == 'interactive':
            info = f"Target: ({x_cm:4.1f}, {y_cm:4.1f}, {z_cm:4.1f} cm) | J1={math.degrees(q1):+4.0f}°, J2={math.degrees(q2):+4.0f}°, J3={math.degrees(q3):+4.0f}°"
            input(f"\n[Enter] -> {desc}\n         {info} ... ")
        else:
            self.get_logger().info(f"▶ {desc} -> ({x_cm:.1f}, {y_cm:.1f}, {z_cm:.1f} cm)")

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [q1, q2, q3, self.current_gripper]
        self.cmd_pub.publish(msg)

        time.sleep(self.settle_time)
        return True

    def set_gripper(self, open_gripper: bool, desc=""):
        self.current_gripper = self.GRIPPER_OPEN if open_gripper else self.GRIPPER_CLOSE
        action = "OPEN" if open_gripper else "CLOSE"

        if self.mode == 'interactive':
            input(f"\n[Enter] -> Gripper {action} ({desc}) ... ")
        else:
            self.get_logger().info(f"▶ Gripper {action} ({desc})")

        # Re-publish current angles with new gripper state
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['gripper_joint']
        msg.position = [self.current_gripper]
        self.cmd_pub.publish(msg)

        time.sleep(self.settle_time)

    def transfer_item(self, item_num: int, pick_layer: int, place_layer: int):
        pick_z  = self.layer_cmd_z[pick_layer]
        place_z = self.layer_cmd_z[place_layer]

        self.get_logger().info(f"\n=======================================================")
        self.get_logger().info(f"  TRANSFERRING ITEM {item_num}/4")
        self.get_logger().info(f"  Pick  Layer {pick_layer} (Z = {pick_z:.1f} cm from tabletop)")
        self.get_logger().info(f"  Place Layer {place_layer} (Z = {place_z:.1f} cm from tabletop)")
        self.get_logger().info(f"=======================================================")

        # 1. Open gripper high
        self.set_gripper(True, f"Open before approaching item {item_num}")

        # 2. Move above pick stack (high clearance Z=8.0 cm)
        self.move_to_xyz(self.PICK_X, self.PICK_Y, self.CLEARANCE_Z,
                         f"Move above pick stack (Z={self.CLEARANCE_Z} cm)")

        # 3. Descend vertically to pick level
        self.move_to_xyz(self.PICK_X, self.PICK_Y, pick_z,
                         f"Descend vertically to pick Item {item_num} (Z={pick_z:.1f} cm)")

        # 4. Grasp
        self.set_gripper(False, f"Grasp Item {item_num}")

        # 5. Lift up vertically back to clearance
        self.move_to_xyz(self.PICK_X, self.PICK_Y, self.CLEARANCE_Z,
                         f"Lift Item {item_num} vertically to clearance (Z={self.CLEARANCE_Z} cm)")

        # 6. Swing across horizontally above place stack
        self.move_to_xyz(self.PLACE_X, self.PLACE_Y, self.CLEARANCE_Z,
                         f"Swing across to place station (Z={self.CLEARANCE_Z} cm)")

        # 7. Descend vertically to place level
        self.move_to_xyz(self.PLACE_X, self.PLACE_Y, place_z,
                         f"Descend vertically to place on Layer {place_layer} (Z={place_z:.1f} cm)")

        # 8. Release
        self.set_gripper(True, f"Release Item {item_num}")

        # 9. Retract vertically back to clearance
        self.move_to_xyz(self.PLACE_X, self.PLACE_Y, self.CLEARANCE_Z,
                         f"Retract vertically away from stack (Z={self.CLEARANCE_Z} cm)")

    def run(self):
        time.sleep(1.0)
        self.get_logger().info("=== Devotics Arm V0 Cartesian IK Palletizer Started ===")
        self.get_logger().info(f"Pick Station:  X={self.PICK_X} cm, Y={self.PICK_Y} cm (Right)")
        self.get_logger().info(f"Place Station: X={self.PLACE_X} cm, Y={self.PLACE_Y} cm (Left)")
        self.get_logger().info(f"Tabletop Z:    L1={self.layer_cmd_z[1]}cm, L2={self.layer_cmd_z[2]}cm, L3={self.layer_cmd_z[3]}cm, L4={self.layer_cmd_z[4]}cm")

        # Sequence of 4 transfers: (item_number, pick_layer, place_layer)
        # Level 1 = 1 cm (Table surface), Level 4 = 4 cm (Top of 4-item stack)
        transfers = [
            (1, 4, 1),  # Item 1: Pick from 4 cm (Top)    -> Place at 1 cm (Table)
            (2, 3, 2),  # Item 2: Pick from 3 cm (Mid-Hi) -> Place at 2 cm (On Item 1)
            (3, 2, 3),  # Item 3: Pick from 2 cm (Mid-Lo) -> Place at 3 cm (On Item 2)
            (4, 1, 4),  # Item 4: Pick from 1 cm (Table)  -> Place at 4 cm (Top of stack)
        ]

        try:
            for item_num, p_layer, d_layer in transfers:
                if not rclpy.ok():
                    break
                self.transfer_item(item_num, p_layer, d_layer)

            # Return to upright standby
            self.move_to_xyz(10.0, 0.0, 12.0, "All items stacked! Return to Standby.")
            self.get_logger().info("Cartesian IK Palletizing finished successfully!")

        except KeyboardInterrupt:
            self.get_logger().info("Interrupted. Moving to safe standby pose...")
            self.move_to_xyz(10.0, 0.0, 12.0, "Safe Standby")


def main():
    parser = argparse.ArgumentParser(description='Devotics Arm V0 Cartesian IK Palletizer')
    parser.add_argument('--mode', choices=['once', 'interactive'], default='interactive',
                        help='Run mode: interactive (step-by-step with [Enter]) or once (automatic)')
    parser.add_argument('--speed', type=float, default=1.5,
                        help='Settle time (seconds) between motions (default: 1.5)')

    non_ros_args = rclpy.utilities.remove_ros_args(sys.argv)[1:]
    args = parser.parse_args(args=non_ros_args)

    rclpy.init()
    node = ArmV0IKPalletizer(mode=args.mode, settle_time=args.speed)
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
