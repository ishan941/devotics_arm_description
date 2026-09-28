#!/usr/bin/env python3
"""
arm_v0_moveit_bridge.py — MoveIt 2 Trajectory Execution Bridge for Devotics Arm V0

Connects MoveIt 2's FollowJointTrajectory Action Server directly to the
ESP32 Wi-Fi TCP socket. When you click "Execute" in RViz, this node
receives the trajectory and streams smooth motion commands to the physical servos.
"""

import math
import time
import serial
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from control_msgs.action import FollowJointTrajectory
from sensor_msgs.msg import JointState


class ArmV0MoveItBridge(Node):
    def __init__(self):
        super().__init__('arm_v0_moveit_bridge')

        # -------------------------------------------------------------
        # Parameters & Connection
        # -------------------------------------------------------------
        self.declare_parameter('serial_port', 'socket://192.168.18.37:8888')
        self.declare_parameter('baud_rate', 115200)
        self.serial_url = self.get_parameter('serial_port').get_parameter_value().string_value

        self.get_logger().info(f"Connecting to ESP32 at {self.serial_url} ...")
        try:
            self.ser = serial.serial_for_url(self.serial_url, timeout=2.0)
            self.get_logger().info("✅ Connected to ESP32 Wi-Fi bridge successfully!")
        except Exception as e:
            self.get_logger().error(f"❌ Failed to connect to ESP32: {e}")
            self.ser = None

        # -------------------------------------------------------------
        # Joint Configuration & Limits
        # -------------------------------------------------------------
        self.arm_joints = ['base_joint', 'shoulder_joint', 'elbow_joint']
        self.gripper_joints = ['gripper_joint']

        # Current joint positions (radians) — Start at HOME (upright)
        self.current_pos = {
            'base_joint': 0.0,
            'shoulder_joint': 0.0,
            'elbow_joint': 0.0,
            'gripper_joint': 0.0
        }

        # Servo calibration limits
        self.limits = {
            'base_joint':     {'min': 30,  'max': 150, 'id': 'J1'},
            'shoulder_joint': {'min': 60,  'max': 175, 'id': 'J2'},
            'elbow_joint':    {'min': 60,  'max': 175, 'id': 'J3'},
            'gripper_joint':  {'min': 60,  'max': 110, 'id': 'J4'}
        }

        # -------------------------------------------------------------
        # Joint State Publisher (20 Hz for RViz Mirroring)
        # -------------------------------------------------------------
        self.cb_group = ReentrantCallbackGroup()
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.05, self.publish_joint_states, callback_group=self.cb_group)

        # -------------------------------------------------------------
        # FollowJointTrajectory Action Servers
        # -------------------------------------------------------------
        self.arm_action_server = ActionServer(
            self,
            FollowJointTrajectory,
            '/arm_v0_controller/follow_joint_trajectory',
            execute_callback=self.execute_arm_trajectory,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.cb_group
        )

        self.gripper_action_server = ActionServer(
            self,
            FollowJointTrajectory,
            '/gripper_v0_controller/follow_joint_trajectory',
            execute_callback=self.execute_gripper_trajectory,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.cb_group
        )

        self.get_logger().info("🚀 MoveIt 2 Hardware Bridge Action Server ready for 'Execute' commands!")

    def goal_callback(self, goal_request):
        self.get_logger().info("📥 Trajectory execution goal received from MoveIt!")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().warn("⚠️ Trajectory execution goal cancelled by user!")
        return CancelResponse.ACCEPT

    def rad_to_servo(self, joint_name: str, rad_val: float) -> int:
        deg = math.degrees(rad_val)
        servo = int(round(90.0 + deg))
        cfg = self.limits[joint_name]
        return max(cfg['min'], min(cfg['max'], servo))

    def send_servo_cmd(self, joint_name: str, servo_deg: int):
        if self.ser is not None and self.ser.is_open:
            servo_id = self.limits[joint_name]['id']
            cmd = f"{servo_id} {servo_deg}\n"
            try:
                self.ser.write(cmd.encode('utf-8'))
            except Exception as e:
                self.get_logger().error(f"Write error: {e}")

    def execute_arm_trajectory(self, goal_handle):
        trajectory = goal_handle.request.trajectory
        points = trajectory.points
        joint_names = trajectory.joint_names

        self.get_logger().info(f"▶ Executing arm trajectory: {len(points)} waypoints...")
        start_time = time.time()

        for pt_idx, pt in enumerate(points):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().warn("Trajectory cancelled mid-execution.")
                result = FollowJointTrajectory.Result()
                result.error_code = FollowJointTrajectory.Result.PATH_TOLERANCE_VIOLATED
                return result

            # Target time for this waypoint
            pt_target_time = pt.time_from_start.sec + pt.time_from_start.nanosec * 1e-9
            elapsed = time.time() - start_time
            wait_time = pt_target_time - elapsed
            if wait_time > 0:
                time.sleep(wait_time)

            # Send angles to servos
            for i, name in enumerate(joint_names):
                if name in self.current_pos:
                    self.current_pos[name] = pt.positions[i]
                    servo_val = self.rad_to_servo(name, pt.positions[i])
                    self.send_servo_cmd(name, servo_val)

        goal_handle.succeed()
        self.get_logger().info("✅ Arm trajectory completed successfully on physical robot!")
        result = FollowJointTrajectory.Result()
        result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
        return result

    def execute_gripper_trajectory(self, goal_handle):
        trajectory = goal_handle.request.trajectory
        points = trajectory.points
        joint_names = trajectory.joint_names

        self.get_logger().info(f"▶ Executing gripper motion: {len(points)} waypoints...")
        start_time = time.time()

        for pt in points:
            pt_target_time = pt.time_from_start.sec + pt.time_from_start.nanosec * 1e-9
            elapsed = time.time() - start_time
            wait_time = pt_target_time - elapsed
            if wait_time > 0:
                time.sleep(wait_time)

            for i, name in enumerate(joint_names):
                if name in self.current_pos:
                    self.current_pos[name] = pt.positions[i]
                    servo_val = self.rad_to_servo(name, pt.positions[i])
                    self.send_servo_cmd(name, servo_val)

        goal_handle.succeed()
        self.get_logger().info("✅ Gripper motion completed successfully!")
        result = FollowJointTrajectory.Result()
        result.error_code = FollowJointTrajectory.Result.SUCCESSFUL
        return result

    def publish_joint_states(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self.current_pos.keys())
        msg.position = list(self.current_pos.values())
        self.joint_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ArmV0MoveItBridge()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
