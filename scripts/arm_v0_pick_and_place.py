#!/usr/bin/env python3
"""
arm_v0_pick_and_place.py — Automated Pick-and-Place Demo for Devotics Arm V0

Features:
- Smooth automated sequence:
    1. HOME
    2. OPEN GRIPPER
    3. APPROACH PICK POSE
    4. GRASP (CLOSE GRIPPER)
    5. LIFT UP
    6. SWING TO PLACE POSE
    7. LOWER TO PLACE
    8. RELEASE (OPEN GRIPPER)
    9. RETRACT & RETURN HOME
- Modes:
    --once         Run the sequence one time and return to home (default)
    --loop         Continuously repeat the pick-and-place cycle
    --interactive  Wait for user to press [Enter] before executing each step
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


class ArmV0PickAndPlace(Node):
    def __init__(self, mode='once', settle_time=1.5):
        super().__init__('arm_v0_pick_and_place')
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
        # POSE DEFINITIONS (in degrees relative to servo home = 90°)
        # ROS Joint Angle = (servo_deg - 90°)
        # -------------------------------------------------------------
        # Safe ranges:
        #   base:     30° to 150°   (-60° to +60°)
        #   shoulder: 60° to 150°   (-30° to +60°)
        #   elbow:    60° to 150°   (-30° to +60°)
        #   gripper:  60° to 110°   (-30° to +20°)
        # -------------------------------------------------------------
        self.poses = {
            'HOME': {
                'desc': 'Standby home pose (all joints centered)',
                'angles': [0.0, 0.0, 0.0, 0.0],
            },
            'OPEN_GRIPPER_HIGH': {
                'desc': 'Open gripper wide in the air before approaching object',
                'angles': [0.0, 0.0, 0.0, deg2rad(20.0)],     # J4=110° (fully open)
            },
            'SWING_TO_PICK': {
                'desc': 'Rotate base to pick position while staying safely elevated',
                'angles': [deg2rad(-30.0), deg2rad(0.0), deg2rad(0.0), deg2rad(20.0)],
            },
            'DESCEND_TO_OBJECT': {
                'desc': 'Lower opened gripper deep down to tabletop level around object',
                # J2 = 90 + 55 = 145°, J3 = 90 + 50 = 140° (deep reach down)
                'angles': [deg2rad(-30.0), deg2rad(47.0), deg2rad(47.0), deg2rad(20.0)],
            },
            'GRASP': {
                'desc': 'Close fingers around the object (J4=70°)',
                'angles': [deg2rad(-30.0), deg2rad(47.0), deg2rad(47.0), deg2rad(-30.0)],
            },
            'LIFT_OBJECT': {
                'desc': 'Lift object vertically off the table',
                'angles': [deg2rad(-30.0), deg2rad(0.0), deg2rad(0.0), deg2rad(-30.0)],
            },
            'SWING_TO_PLACE': {
                'desc': 'Rotate base far to left (J1=140°)',
                'angles': [deg2rad(20.0), deg2rad(0.0), deg2rad(0.0), deg2rad(-30.0)],
            },
            'DESCEND_TO_PLACE': {
                'desc': 'Lower object deep down at place location',
                'angles': [deg2rad(20.0), deg2rad(47.0), deg2rad(47.0), deg2rad(-30.0)],
            },
            'RELEASE': {
                'desc': 'Open gripper to release the object (J4=110°)',
                'angles': [deg2rad(20.0), deg2rad(47.0), deg2rad(47.0), deg2rad(20.0)],
            },
            'RETRACT_HIGH': {
                'desc': 'Raise arm straight up away from released object',
                'angles': [deg2rad(20.0), deg2rad(0.0), deg2rad(0.0), deg2rad(20.0)],
            },
        }

        self.sequence = [
            'HOME',
            'OPEN_GRIPPER_HIGH',
            'SWING_TO_PICK',
            'DESCEND_TO_OBJECT',
            'GRASP',
            'LIFT_OBJECT',
            'SWING_TO_PLACE',
            'DESCEND_TO_PLACE',
            'RELEASE',
            'RETRACT_HIGH',
            'HOME'
        ]

    def send_pose(self, name: str):
        pose = self.poses[name]
        self.get_logger().info(f'▶ Step: [{name}] — {pose["desc"]}')

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = pose['angles']

        self.cmd_pub.publish(msg)

    def run(self):
        # Allow publishers to connect
        time.sleep(1.0)
        self.get_logger().info('Starting Devotics Arm V0 Automated Sequence...')
        self.get_logger().info(f'Mode: {self.mode}')

        try:
            iteration = 1
            while rclpy.ok():
                self.get_logger().info(f'========== CYCLE {iteration} ==========')
                for step_name in self.sequence:
                    if not rclpy.ok():
                        break

                    if self.mode == 'interactive':
                        input(f'\nPress [Enter] to execute step [{step_name}]... ')

                    self.send_pose(step_name)
                    time.sleep(self.settle_time)

                if self.mode == 'once':
                    self.get_logger().info('Pick-and-place sequence finished successfully!')
                    break

                iteration += 1
                self.get_logger().info(f'Pausing {self.settle_time * 2}s before next cycle...')
                time.sleep(self.settle_time * 2)

        except KeyboardInterrupt:
            self.get_logger().info('KeyboardInterrupt received. Moving to HOME...')
            self.send_pose('HOME')
            time.sleep(1.0)


def main():
    parser = argparse.ArgumentParser(description='Devotics Arm V0 Automated Pick and Place')
    parser.add_argument('--mode', choices=['once', 'loop', 'interactive'], default='once',
                        help='Run mode: once, loop, or interactive (step-by-step)')
    parser.add_argument('--speed', type=float, default=1.5,
                        help='Pause/settle time (seconds) between poses (default: 1.5)')

    non_ros_args = rclpy.utilities.remove_ros_args(sys.argv)[1:]
    args = parser.parse_args(args=non_ros_args)

    rclpy.init()
    node = ArmV0PickAndPlace(mode=args.mode, settle_time=args.speed)
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
