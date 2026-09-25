"""
arm_v0_control.launch.py — Devotics Arm V0 Physical Robot Control Launch

Purpose:
    Launch the ROS 2 system to control the PHYSICAL Devotics Arm V0 via
    USB serial to the ESP32.

What this starts:
    1. robot_state_publisher  — URDF → /tf from /joint_states
    2. arm_v0_serial_node     — /arm_v0/joint_command → serial → ESP32
                                 publishes estimated /joint_states

What you can then do:
    # Command a single joint (e.g. base_joint to 0.5 rad):
    ros2 topic pub --once /arm_v0/joint_command sensor_msgs/msg/JointState \\
      "{name: ['base_joint'], position: [0.5]}"

    # Send arm to home:
    ros2 topic pub --once /arm_v0/joint_command sensor_msgs/msg/JointState \\
      "{name: ['base_joint','shoulder_joint','elbow_joint','gripper_joint'], \\
        position: [0.0, 0.0, 0.0, 0.0]}"

Before running:
    1. Connect ESP32 via USB.
    2. Check serial port: ls /dev/ttyUSB*
    3. Update 'serial_port' in config/arm_v0_calibration.yaml if needed.
    4. Make sure ESP32 firmware is loaded and running.

Run:
    ros2 launch devotics_arm_description arm_v0_control.launch.py

Optional — also open RViz to watch the virtual arm:
    ros2 launch devotics_arm_description arm_v0_control.launch.py rviz:=true
"""

import os
import xacro

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg = get_package_share_directory('devotics_arm_description')

    # ----------------------------------------------------------------
    # Process the V0 Xacro → robot_description string
    # ----------------------------------------------------------------
    xacro_file = os.path.join(pkg, 'urdf', 'devotics_arm_v0.urdf.xacro')
    robot_description_doc = xacro.process_file(xacro_file)
    robot_description_str = robot_description_doc.toxml()

    # Calibration / parameter file
    calibration_file = os.path.join(pkg, 'config', 'arm_v0_calibration.yaml')

    # Optional RViz config
    rviz_config = os.path.join(pkg, 'config', 'rviz_v0.rviz')

    # Launch argument: open RViz alongside the controller?
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='false',
        description='Set to true to also open RViz for visualization'
    )

    # Launch argument: open joint slider GUI to command the physical arm?
    # Set to true for manual slider control; keep false for automated scripts.
    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='false',
        description='Set to true to open joint slider GUI to control the physical arm'
    )

    return LaunchDescription([

        rviz_arg,
        gui_arg,

        # 1. robot_state_publisher
        #    Converts /joint_states + URDF → /tf frames for RViz
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description_str,
                'publish_frequency': 50.0,
            }]
        ),

        # 2. arm_v0_serial_node
        #    Subscribes: /arm_v0/joint_command  (sensor_msgs/JointState)
        #    Publishes:  /joint_states           (sensor_msgs/JointState)
        #    Sends:      serial commands to ESP32 over USB
        Node(
            package='devotics_arm_description',
            executable='arm_v0_serial_node.py',
            name='arm_v0_serial_node',
            output='screen',
            parameters=[calibration_file],
            emulate_tty=True,  # enables colored output
        ),

        # 3. joint_state_publisher_gui (optional — default true)
        #    Publishes to /arm_v0/joint_command so dragging sliders commands the physical arm!
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            remappings=[
                ('joint_states', '/arm_v0/joint_command'),
            ],
            condition=IfCondition(LaunchConfiguration('gui')),
        ),

        # 4. RViz (optional — only if rviz:=true)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),

    ])
