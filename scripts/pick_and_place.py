#!/usr/bin/env python3
"""
Devotics Arm V1 — Autonomous Pick & Place Demo
Commands arm and gripper trajectories sequentially using ROS 2 Action Clients.
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class DevoticsMissionController(Node):
    def __init__(self):
        super().__init__('devotics_mission_controller')

        # Create Action Clients for Arm and Gripper
        self.arm_client = ActionClient(
            self, FollowJointTrajectory, '/devotics_arm_controller/follow_joint_trajectory'
        )
        self.gripper_client = ActionClient(
            self, FollowJointTrajectory, '/gripper_controller/follow_joint_trajectory'
        )

        self.get_logger().info("Waiting for Devotics controllers...")
        self.arm_client.wait_for_server()
        self.gripper_client.wait_for_server()
        self.get_logger().info("All controllers connected! Starting autonomous sequence...")

    def move_arm(self, joint_positions, duration_sec):
        """Sends a target pose to the 6-DOF arm and waits until it arrives."""
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = [
            'joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6'
        ]

        point = JointTrajectoryPoint()
        point.positions = joint_positions
        point.time_from_start = Duration(sec=int(duration_sec), nanosec=0)
        goal_msg.trajectory.points.append(point)

        self.get_logger().info(f"Moving arm to {joint_positions} in {duration_sec}s...")
        send_goal_future = self.arm_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Arm goal rejected!")
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        self.get_logger().info("Arm motion complete.")
        return True

    def move_gripper(self, finger_position, duration_sec=1.0):
        """Opens or closes the parallel gripper (0.03 = open, 0.0 = closed)."""
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ['left_finger_joint', 'right_finger_joint']

        point = JointTrajectoryPoint()
        point.positions = [finger_position, finger_position]
        point.time_from_start = Duration(sec=int(duration_sec), nanosec=0)
        goal_msg.trajectory.points.append(point)

        state = "OPENING" if finger_position > 0.01 else "CLOSING"
        self.get_logger().info(f"{state} gripper...")
        send_goal_future = self.gripper_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Gripper goal rejected!")
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        self.get_logger().info(f"Gripper {state} complete.")
        return True


def main(args=None):
    rclpy.init(args=args)
    controller = DevoticsMissionController()

    # Named joint targets [j1, j2, j3, j4, j5, j6]
    HOME_POSE = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    READY_POSE = [0.0, -0.5, 0.8, 0.0, 0.0, 0.0]
    PICKUP_APPROACH = [0.0, -1.2, 1.8, -0.6, 0.0, 0.0]

    try:
        # Step 1: Move to Ready Pose
        controller.move_arm(READY_POSE, duration_sec=3)
        time.sleep(1.0)

        # Step 2: Open Gripper
        controller.move_gripper(finger_position=0.03, duration_sec=1)
        time.sleep(1.0)

        # Step 3: Descend to Pickup Approach Pose
        controller.move_arm(PICKUP_APPROACH, duration_sec=3)
        time.sleep(1.0)

        # Step 4: Grasp Object (Close Gripper)
        controller.move_gripper(finger_position=0.0, duration_sec=1)
        time.sleep(1.0)

        # Step 5: Lift up to Ready Pose
        controller.move_arm(READY_POSE, duration_sec=2)
        time.sleep(1.0)

        # Step 6: Return to Home
        controller.move_arm(HOME_POSE, duration_sec=3)
        controller.get_logger().info("🎉 Autonomous Pick & Place Mission Successfully Completed!")

    except KeyboardInterrupt:
        controller.get_logger().warn("Mission interrupted by user.")
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
