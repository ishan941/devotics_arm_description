#!/usr/bin/env python3
"""
Tabletop Workspace Reachability Tester for Devotics Arm V1.
Tests whether the 300mm + 250mm link geometry can reach all 5 key benchtop target zones
with the gripper pointing vertically downward.
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from moveit_msgs.srv import GetPositionIK
from moveit_msgs.msg import PositionIKRequest, RobotState
from sensor_msgs.msg import JointState


class WorkspaceTester(Node):
    def __init__(self):
        super().__init__('workspace_tester')
        self.client = self.create_client(GetPositionIK, 'compute_ik')
        
        self.get_logger().info('Connecting to MoveIt compute_ik service...')
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('Waiting for compute_ik service... (Make sure demo.launch.py is running)')

    def test_point(self, name, x, y, z):
        req = GetPositionIK.Request()
        ik_req = PositionIKRequest()
        ik_req.group_name = 'devotics_arm'
        ik_req.avoid_collisions = True
        ik_req.timeout.sec = 2

        # 1. Non-singular seed: arm bent forward toward table
        base_angle = math.atan2(y, x)
        seed_state = RobotState()
        seed_js = JointState()
        seed_js.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']
        seed_js.position = [base_angle, 0.3, 1.2, 1.5, 0.0, 0.0]
        seed_state.joint_state = seed_js
        ik_req.robot_state = seed_state

        target_pose = PoseStamped()
        target_pose.header.frame_id = 'base_link'
        target_pose.header.stamp = self.get_clock().now().to_msg()
        target_pose.pose.position.x = float(x)
        target_pose.pose.position.y = float(y)
        target_pose.pose.position.z = float(z)

        # 2. Gripper pointing straight DOWN with natural radial approach yaw
        # Roll = 0, Pitch = 180 deg (pi), Yaw = base_angle
        # Quaternion for (r=0, p=pi, y=base_angle):
        half_yaw = base_angle / 2.0
        target_pose.pose.orientation.x = -math.sin(half_yaw)
        target_pose.pose.orientation.y = math.cos(half_yaw)
        target_pose.pose.orientation.z = 0.0
        target_pose.pose.orientation.w = 0.0

        ik_req.pose_stamped = target_pose
        req.ik_request = ik_req

        future = self.client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        res = future.result()

        if res.error_code.val == 1:  # SUCCESS
            joints_deg = [math.degrees(pos) for pos in res.solution.joint_state.position[:6]]
            self.get_logger().info(
                f"✅ {name:12s} at ({x:0.2f}, {y:0.2f}, {z:0.2f}m) -> REACHABLE\n"
                f"   Joints [deg]: {[round(j, 1) for j in joints_deg]}"
            )
            return True
        else:
            self.get_logger().error(f"❌ {name:12s} at ({x:0.2f}, {y:0.2f}, {z:0.2f}m) -> FAILED (Code: {res.error_code.val})")
            return False


def main():
    rclpy.init()
    tester = WorkspaceTester()

    test_targets = [
        ("Center Work", 0.35,  0.00, 0.28),
        ("Near Work",   0.25,  0.00, 0.28),
        ("Far Reach",   0.45,  0.00, 0.28),
        ("Left Flank",  0.35,  0.15, 0.28),
        ("Right Flank", 0.35, -0.15, 0.28),
    ]

    print("\n" + "="*60)
    print(" DEVOTICS ARM V1 — TABLETOP WORKSPACE REACHABILITY AUDIT")
    print("="*60)

    success_count = 0
    for name, x, y, z in test_targets:
        if tester.test_point(name, x, y, z):
            success_count += 1

    print("="*60)
    print(f"RESULTS: {success_count}/{len(test_targets)} Points Reachable ({success_count/len(test_targets)*100:.0f}%)")
    if success_count == len(test_targets):
        print("STAGE A VERIFICATION: PASSED. Kinematic geometry is validated!")
    else:
        print("STAGE A VERIFICATION: FAILED. Check joint limits or link lengths.")
    print("="*60 + "\n")

    tester.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
