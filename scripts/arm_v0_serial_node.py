#!/usr/bin/env python3
"""
arm_v0_serial_node.py — Devotics Arm V0 ROS 2 → USB Serial Bridge

Purpose:
    Translates ROS 2 joint position commands (in radians) into text serial
    commands understood by the ESP32 firmware, and sends them over USB.

    Also publishes the COMMANDED (estimated) joint state back to /joint_states
    so that robot_state_publisher can update the TF tree and RViz can display
    the arm's approximate position.

IMPORTANT LIMITATION:
    MG90S servos have NO position feedback encoder.
    The published /joint_states reflects COMMANDED positions, not measured ones.
    Do NOT interpret these as true encoder-measured joint angles.

Topics:
    Subscribe:  /arm_v0/joint_command  [sensor_msgs/msg/JointState]
    Publish:    /joint_states           [sensor_msgs/msg/JointState]

Serial protocol (to ESP32):
    Command format:  "J{n} {deg}\\n"
    Examples:
        "J1 90\\n"   →  base servo to 90 degrees
        "J2 120\\n"  →  shoulder servo to 120 degrees
        "J3 60\\n"   →  elbow servo to 60 degrees
        "J4 110\\n"  →  gripper servo to 110 degrees (open)

Parameters (from arm_v0_calibration.yaml):
    serial_port      — e.g. /dev/ttyUSB0
    baud_rate        — 115200
    joints           — list of joint configurations (see YAML)

Joint-to-servo conversion:
    servo_deg = servo_home + direction * (ros_rad * 180.0 / pi) + offset_deg
    servo_deg = clamp(servo_deg, servo_min, servo_max)

    ROS 0 rad  = servo 90° (home) for all joints.

Run via launch file:
    ros2 launch devotics_arm_description arm_v0_control.launch.py

Or run directly (for debugging):
    ros2 run devotics_arm_description arm_v0_serial_node.py \\
      --ros-args --params-file config/arm_v0_calibration.yaml
"""

import math
import serial
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Time


# ---------------------------------------------------------------------------
# Joint descriptor — loaded from arm_v0_calibration.yaml
# ---------------------------------------------------------------------------
class JointConfig:
    """Holds calibration data for one servo joint."""
    def __init__(self, ros_name: str, servo_id: str, gpio: int,
                 servo_min: int, servo_home: int, servo_max: int,
                 direction: int, offset_deg: float):
        self.ros_name   = ros_name
        self.servo_id   = servo_id    # e.g. "J1"
        self.gpio       = gpio
        self.servo_min  = servo_min   # degrees
        self.servo_home = servo_home  # degrees (= ROS 0 rad)
        self.servo_max  = servo_max   # degrees
        self.direction  = direction   # +1 or -1
        self.offset_deg = offset_deg  # calibration trim (degrees)

    def ros_rad_to_servo_deg(self, ros_rad: float) -> int:
        """
        Convert a ROS joint angle (radians) to ESP32 servo degrees.

        Formula:
            servo_deg = servo_home + direction * (ros_rad * 180/pi) + offset_deg

        Returns clamped integer degrees in [servo_min, servo_max].
        """
        ros_deg   = math.degrees(ros_rad)
        servo_deg = self.servo_home + self.direction * ros_deg + self.offset_deg
        servo_deg = int(round(servo_deg))
        servo_deg = max(self.servo_min, min(self.servo_max, servo_deg))
        return servo_deg

    def servo_deg_to_ros_rad(self, servo_deg: int) -> float:
        """
        Inverse: convert servo degrees back to ROS radians.
        Used to populate the estimated /joint_states.
        """
        ros_deg = (servo_deg - self.servo_home - self.offset_deg) / self.direction
        return math.radians(ros_deg)


# ---------------------------------------------------------------------------
# Main ROS 2 Node
# ---------------------------------------------------------------------------
class ArmV0SerialNode(Node):
    """
    ROS 2 node that bridges joint commands to ESP32 over USB serial.
    """

    def __init__(self):
        super().__init__('arm_v0_serial_node')

        # ------------------------------------------------------------------
        # Declare parameters (values come from arm_v0_calibration.yaml)
        # ------------------------------------------------------------------
        self.declare_parameter('serial_port',    '/dev/ttyUSB0')
        self.declare_parameter('baud_rate',      115200)
        self.declare_parameter('serial_timeout', 2.0)

        # ------------------------------------------------------------------
        # Load joint configurations from parameter list
        # ------------------------------------------------------------------
        self.declare_parameter('joint_names', [
            'base_joint', 'shoulder_joint', 'elbow_joint', 'gripper_joint'
        ])
        joint_names = self.get_parameter('joint_names').get_parameter_value().string_array_value

        self._joints: list[JointConfig] = []
        self._joint_map: dict[str, JointConfig] = {}  # ros_name → JointConfig

        for name in joint_names:
            prefix = name
            self.declare_parameter(f'{prefix}.servo_id',    'J1')
            self.declare_parameter(f'{prefix}.gpio',         0)
            self.declare_parameter(f'{prefix}.servo_min',   30)
            self.declare_parameter(f'{prefix}.servo_home',  90)
            self.declare_parameter(f'{prefix}.servo_max',  150)
            self.declare_parameter(f'{prefix}.direction',    1)
            self.declare_parameter(f'{prefix}.offset_deg',  0.0)

            jcfg = JointConfig(
                ros_name   = name,
                servo_id   = self.get_parameter(f'{prefix}.servo_id').get_parameter_value().string_value,
                gpio       = self.get_parameter(f'{prefix}.gpio').get_parameter_value().integer_value,
                servo_min  = self.get_parameter(f'{prefix}.servo_min').get_parameter_value().integer_value,
                servo_home = self.get_parameter(f'{prefix}.servo_home').get_parameter_value().integer_value,
                servo_max  = self.get_parameter(f'{prefix}.servo_max').get_parameter_value().integer_value,
                direction  = self.get_parameter(f'{prefix}.direction').get_parameter_value().integer_value,
                offset_deg = self.get_parameter(f'{prefix}.offset_deg').get_parameter_value().double_value,
            )
            self._joints.append(jcfg)
            self._joint_map[name] = jcfg

        if not self._joints:
            self.get_logger().error(
                'No joints loaded from parameters! Check arm_v0_calibration.yaml'
            )

        self.get_logger().info(
            f'Loaded {len(self._joints)} joints: '
            + ', '.join(j.ros_name for j in self._joints)
        )

        # ------------------------------------------------------------------
        # Track estimated joint state (commanded position, not measured)
        # Start at home (servo 90° = ROS 0 rad for all joints)
        # ------------------------------------------------------------------
        self._current_rad: dict[str, float] = {
            j.ros_name: 0.0 for j in self._joints
        }

        # ------------------------------------------------------------------
        # Open serial port
        # ------------------------------------------------------------------
        port     = self.get_parameter('serial_port').get_parameter_value().string_value
        baud     = self.get_parameter('baud_rate').get_parameter_value().integer_value
        timeout  = self.get_parameter('serial_timeout').get_parameter_value().double_value

        self._serial: serial.Serial | None = None
        self._serial_ok = False

        try:
            self._serial = serial.serial_for_url(port, baudrate=baud, timeout=timeout)
            time.sleep(2.0)   # wait for ESP32 to reset after USB connection
            self._serial_ok = True
            self.get_logger().info(f'Serial connection opened: {port} @ {baud} baud')
        except serial.SerialException as e:
            self.get_logger().error(
                f'FAILED to open serial port {port}: {e}\n'
                '  → Check: is the ESP32 connected?\n'
                '  → Check: is the port correct in arm_v0_calibration.yaml?\n'
                '  → Check: sudo chmod 666 /dev/ttyUSB0  (or add user to dialout group)'
            )

        # ------------------------------------------------------------------
        # ROS Publisher: /joint_states
        # robot_state_publisher listens to this to update /tf → RViz
        # ------------------------------------------------------------------
        self._js_pub = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        # ------------------------------------------------------------------
        # ROS Subscriber: /arm_v0/joint_command
        # Receive desired joint positions (radians) from the user/planner
        # ------------------------------------------------------------------
        self._cmd_sub = self.create_subscription(
            JointState,
            '/arm_v0/joint_command',
            self._joint_command_callback,
            10
        )

        # ------------------------------------------------------------------
        # Timer: publish /joint_states at 20 Hz even when no new commands
        # This keeps robot_state_publisher and RViz updated.
        # ------------------------------------------------------------------
        self._js_timer = self.create_timer(0.05, self._publish_joint_states)

        self.get_logger().info('Devotics Arm V0 serial node ready.')
        self.get_logger().info('Listening on: /arm_v0/joint_command')
        self.get_logger().info('Publishing:   /joint_states')
        if not self._serial_ok:
            self.get_logger().warn(
                'Serial port unavailable — joint commands will be logged but NOT sent to hardware.'
            )

    # -----------------------------------------------------------------------
    # Command callback
    # -----------------------------------------------------------------------
    def _joint_command_callback(self, msg: JointState):
        """
        Receive a JointState command message.

        The message can contain any subset of the arm joints.
        Unspecified joints keep their last commanded position.

        Example to move only the base joint:
            ros2 topic pub --once /arm_v0/joint_command sensor_msgs/msg/JointState \\
              "{name: ['base_joint'], position: [0.5]}"
        """
        if len(msg.name) != len(msg.position):
            self.get_logger().warn(
                f'Malformed JointState: {len(msg.name)} names but {len(msg.position)} positions'
            )
            return

        for joint_name, ros_rad in zip(msg.name, msg.position):
            if joint_name not in self._joint_map:
                self.get_logger().warn(f'Unknown joint name: {joint_name!r} — ignoring')
                continue

            jcfg = self._joint_map[joint_name]

            # Convert ROS radians → servo degrees
            servo_deg = jcfg.ros_rad_to_servo_deg(ros_rad)

            # Build serial command: "J1 90\n"
            command = f'{jcfg.servo_id} {servo_deg}\n'

            self.get_logger().info(
                f'{joint_name}: {math.degrees(ros_rad):.1f}° (ROS) → '
                f'{jcfg.servo_id}={servo_deg}° (servo) → "{command.strip()}"'
            )

            # Send over serial
            if self._serial_ok:
                try:
                    self._serial.write(command.encode('ascii'))
                    self._serial.flush()
                except serial.SerialException as e:
                    self.get_logger().error(f'Serial write failed: {e}')
                    self._serial_ok = False

            # Update estimated state (commanded, not measured)
            # Back-convert from clamped servo degrees so the published state
            # accurately reflects what was actually sent to the servo.
            self._current_rad[joint_name] = jcfg.servo_deg_to_ros_rad(servo_deg)

        # Publish immediately so RViz reflects the new commanded pose with zero delay
        self._publish_joint_states()

    # -----------------------------------------------------------------------
    # Joint state publisher (timer callback)
    # -----------------------------------------------------------------------
    def _publish_joint_states(self):
        """
        Publish the current COMMANDED joint positions as /joint_states.

        NOTE: These are estimated positions based on the last sent command,
        NOT measured encoder values (MG90S servos have no encoders).
        """
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name     = [j.ros_name for j in self._joints]
        msg.position = [self._current_rad[j.ros_name] for j in self._joints]
        msg.velocity = []   # unknown
        msg.effort   = []   # unknown
        self._js_pub.publish(msg)

    # -----------------------------------------------------------------------
    # Cleanup
    # -----------------------------------------------------------------------
    def destroy_node(self):
        if self._serial and self._serial.is_open:
            self._serial.close()
            self.get_logger().info('Serial port closed.')
        super().destroy_node()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)

    node = ArmV0SerialNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down (KeyboardInterrupt).')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
