"""
display_v0.launch.py — Devotics Arm V0 RViz Display Launch

Purpose:
    Visualize the Devotics Arm V0 in RViz WITHOUT a physical robot connected.
    Uses joint_state_publisher_gui so you can manually drag sliders to move
    the virtual arm and verify the URDF structure and TF tree.

What this starts:
    1. robot_state_publisher  — reads URDF, publishes /tf from /joint_states
    2. joint_state_publisher_gui  — GUI sliders to publish /joint_states
    3. rviz2  — 3D visualization

RViz setup (first time):
    - Add display: RobotModel  (Topic: /robot_description)
    - Add display: TF
    - Set Fixed Frame: world
    - Save the config to config/rviz_v0.rviz

Run:
    ros2 launch devotics_arm_description display_v0.launch.py
"""

import os
import xacro

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
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

    # ----------------------------------------------------------------
    # Optional: path to a saved RViz config
    # If the file does not exist yet, RViz opens with default settings.
    # ----------------------------------------------------------------
    rviz_config = os.path.join(pkg, 'config', 'rviz_v0.rviz')

    return LaunchDescription([

        # 1. robot_state_publisher
        #    Reads robot_description (URDF) + /joint_states → publishes /tf
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description_str,
                'publish_frequency': 50.0,   # Hz — TF update rate
            }]
        ),

        # 2. joint_state_publisher_gui
        #    GUI sliders → publishes /joint_states (for display-only testing)
        #    This node is ONLY used when there is no physical robot connected.
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
        ),

        # 3. RViz 2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        ),

    ])
