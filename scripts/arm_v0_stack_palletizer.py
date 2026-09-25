#!/usr/bin/env python3
"""
arm_v0_stack_palletizer.py — 4-Object Stacking Demo for Devotics Arm V0

Task:
    Transfer 4 stacked objects from the PICK station (Left, J1 = -30°)
    to form a new stack at the PLACE station (Right, J1 = +20°).

Sequence logic:
    Item 1: Pick from Height 4 (Top)    → Place at Height 1 (Table)
    Item 2: Pick from Height 3 (Mid-Hi) → Place at Height 2 (On Item 1)
    Item 3: Pick from Height 2 (Mid-Lo) → Place at Height 3 (On Item 2)
    Item 4: Pick from Height 1 (Table)  → Place at Height 4 (Top of Stack)

Height profiles (Shoulder J2, Elbow J3 in degrees relative to 90°):
    Level 1 (Table / Lowest):  Shoulder +47.0°, Elbow +47.0°
    Level 2 (1 unit high):     Shoulder +37.0°, Elbow +37.0°
    Level 3 (2 units high):    Shoulder +27.0°, Elbow +27.0°
    Level 4 (3 units / Top):   Shoulder +17.0°, Elbow +17.0°
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


class ArmV0Palletizer(Node):
    def __init__(self, mode='interactive', settle_time=1.5):
        super().__init__('arm_v0_stack_palletizer')
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

        # Base angles
        self.PICK_YAW  = -30.0  # Left (degrees)
        self.PLACE_YAW =  20.0  # Right (degrees)

        # Gripper angles
        self.GRIPPER_OPEN  =  20.0  # J4 = 110°
        self.GRIPPER_CLOSE = -30.0  # J4 = 60° (tight grip)

        # 4 distinct height levels [Shoulder J2, Elbow J3] in degrees relative to 90°
        # Each servo is 1 cm high (10 mm).
        # In this link configuration (~40mm links), 1 cm vertical delta ≈ 7.5° angle delta:
        self.height_levels = {
            1: [48.0, 48.0],  # Level 1: Table surface (Lowest / 0 cm)
            2: [45.0, 45.0],  # Level 2: +1 cm high (On top of 1st servo)
            3: [41.0, 41.0],  # Level 3: +2 cm high (On top of 2nd servo)
            4: [38.0, 38.0],  # Level 4: +3 cm high (Top of 4-servo stack)
        }

    def send_raw(self, base_deg, shoulder_deg, elbow_deg, gripper_deg, desc=""):
        if desc:
            self.get_logger().info(f'▶ {desc}')

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = [
            deg2rad(base_deg),
            deg2rad(shoulder_deg),
            deg2rad(elbow_deg),
            deg2rad(gripper_deg)
        ]
        self.cmd_pub.publish(msg)

    def step(self, base, shoulder, elbow, gripper, desc):
        if self.mode == 'interactive':
            input(f'\n[Enter] to execute: {desc} ... ')
        self.send_raw(base, shoulder, elbow, gripper, desc)
        time.sleep(self.settle_time)

    def transfer_item(self, item_num: int, from_level: int, to_level: int):
        self.get_logger().info(f'\n========================================')
        self.get_logger().info(f' TRANSFERRING ITEM {item_num}/4')
        self.get_logger().info(f' From Pick Level {from_level} → Place Level {to_level}')
        self.get_logger().info(f'========================================')

        pick_sh, pick_el   = self.height_levels[from_level]
        place_sh, place_el = self.height_levels[to_level]

        # 1. Open gripper high
        self.step(0.0, 0.0, 0.0, self.GRIPPER_OPEN,
                  f"Open gripper up in the air (Ready for item {item_num})")

        # 2. Swing base to pick station
        self.step(self.PICK_YAW, 0.0, 0.0, self.GRIPPER_OPEN,
                  f"Swing base to PICK station ({self.PICK_YAW}°) high")

        # 3. Descend to pick level
        self.step(self.PICK_YAW, pick_sh, pick_el, self.GRIPPER_OPEN,
                  f"Descend to Level {from_level} (Sh={pick_sh}°, El={pick_el}°)")

        # 4. Grasp
        self.step(self.PICK_YAW, pick_sh, pick_el, self.GRIPPER_CLOSE,
                  f"Grasp Item {item_num}")

        # 5. Lift up vertically
        self.step(self.PICK_YAW, 0.0, 0.0, self.GRIPPER_CLOSE,
                  f"Lift Item {item_num} straight up")

        # 6. Swing to place station
        self.step(self.PLACE_YAW, 0.0, 0.0, self.GRIPPER_CLOSE,
                  f"Swing to PLACE station ({self.PLACE_YAW}°)")

        # 7. Descend to place level
        self.step(self.PLACE_YAW, place_sh, place_el, self.GRIPPER_CLOSE,
                  f"Descend to stack Level {to_level} (Sh={place_sh}°, El={place_el}°)")

        # 8. Release
        self.step(self.PLACE_YAW, place_sh, place_el, self.GRIPPER_OPEN,
                  f"Release Item {item_num} onto Level {to_level}")

        # 9. Retract high
        self.step(self.PLACE_YAW, 0.0, 0.0, self.GRIPPER_OPEN,
                  f"Retract arm high away from stack")

    def run(self):
        time.sleep(1.0)
        self.get_logger().info('Devotics Arm V0 — 4-Object Stack Palletizer Node Started.')

        # Standby home
        self.step(0.0, 0.0, 0.0, 0.0, "Standby HOME")

        # 4 transfers: (item_number, pick_level, place_level)
        # Stack 4 items from left to right:
        transfers = [
            (1, 4, 1),  # Take top item (4) -> place at table base (1)
            (2, 3, 2),  # Take 3rd item     -> place on top of 1st (2)
            (3, 2, 3),  # Take 2nd item     -> place on top of 2nd (3)
            (4, 1, 4),  # Take bottom item  -> place on top of stack (4)
        ]

        try:
            for item_num, pick_lvl, place_lvl in transfers:
                if not rclpy.ok():
                    break
                self.transfer_item(item_num, pick_lvl, place_lvl)

            self.step(0.0, 0.0, 0.0, 0.0, "All 4 items stacked! Returning to HOME.")
            self.get_logger().info("Palletizing routine completed successfully!")

        except KeyboardInterrupt:
            self.get_logger().info("Interrupted. Returning to safe HOME...")
            self.send_raw(0.0, 0.0, 0.0, 0.0, "Safe HOME")
            time.sleep(1.0)


def main():
    parser = argparse.ArgumentParser(description='Devotics Arm V0 4-Item Stacking Palletizer')
    parser.add_argument('--mode', choices=['once', 'interactive'], default='interactive',
                        help='Run mode: interactive (step-by-step with [Enter]) or once (automatic)')
    parser.add_argument('--speed', type=float, default=1.5,
                        help='Settle time (seconds) between poses (default: 1.5)')

    non_ros_args = rclpy.utilities.remove_ros_args(sys.argv)[1:]
    args = parser.parse_args(args=non_ros_args)

    rclpy.init()
    node = ArmV0Palletizer(mode=args.mode, settle_time=args.speed)
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
