#!/usr/bin/env python3
"""
arm_v0_moveit.launch.py — MoveIt 2 Motion Planning & Hardware Execution for Devotics Arm V0

Features:
- Loads URDF (Xacro), SRDF, Kinematics (KDL), Joint Limits, and OMPL
- Connects MoveIt 2 controller manager to physical ESP32 via arm_v0_moveit_bridge.py
- Launches MoveIt 2 move_group with trajectory execution enabled
- Launches robot_state_publisher
- Launches RViz2 with Motion Planning display
"""

import os
import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro


def load_file(package_name, file_path):
    pkg_path = get_package_share_directory(package_name)
    abs_path = os.path.join(pkg_path, file_path)
    with open(abs_path, 'r') as f:
        return f.read()


def load_yaml(package_name, file_path):
    pkg_path = get_package_share_directory(package_name)
    abs_path = os.path.join(pkg_path, file_path)
    with open(abs_path, 'r') as f:
        return yaml.safe_load(f)


def generate_launch_description():
    pkg_name = 'devotics_arm_description'
    pkg_share = get_package_share_directory(pkg_name)

    # 1. Declare Launch Arguments
    hardware_arg = DeclareLaunchArgument(
        'hardware',
        default_value='true',
        description='Connect to physical ESP32 arm via Wi-Fi bridge'
    )

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz2'
    )

    use_hardware = LaunchConfiguration('hardware')
    use_rviz = LaunchConfiguration('rviz')

    # 2. Process Robot Description (URDF / Xacro)
    xacro_file = os.path.join(pkg_share, 'urdf', 'devotics_arm_v0.urdf.xacro')
    doc = xacro.process_file(xacro_file)
    robot_description = {'robot_description': doc.toxml()}

    # 3. Load Robot Description Semantic (SRDF)
    srdf_content = load_file(pkg_name, 'config/devotics_arm_v0.srdf')
    robot_description_semantic = {'robot_description_semantic': srdf_content}

    # 4. Load Kinematics Configuration (KDL Solver)
    kinematics_yaml = load_yaml(pkg_name, 'config/v0_kinematics.yaml')
    robot_description_kinematics = {'robot_description_kinematics': kinematics_yaml}

    # 5. Load Joint Limits & Trajectory Settings
    joint_limits_yaml = load_yaml(pkg_name, 'config/v0_joint_limits.yaml')
    robot_description_planning = {'robot_description_planning': joint_limits_yaml}

    # 6. Load OMPL Planning Pipeline Configuration
    ompl_planning_yaml = load_yaml(pkg_name, 'config/v0_ompl_planning.yaml')
    planning_pipelines = {
        'planning_pipelines': ['ompl'],
        'default_planning_pipeline': 'ompl',
        'ompl': ompl_planning_yaml,
    }

    # 7. Load Trajectory Execution Controllers
    controllers_yaml = load_yaml(pkg_name, 'config/v0_moveit_controllers.yaml')
    moveit_controllers = {
        'moveit_simple_controller_manager': controllers_yaml['moveit_simple_controller_manager'],
        'moveit_controller_manager': controllers_yaml['moveit_controller_manager'],
    }

    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.5,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.05,
        'trajectory_execution.execution_duration_monitoring': False,
    }

    # 8. MoveGroup Node
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            robot_description_planning,
            planning_pipelines,
            moveit_controllers,
            trajectory_execution,
            {
                'publish_planning_scene': True,
                'publish_geometry_updates': True,
                'publish_state_updates': True,
                'publish_transforms_updates': True,
            }
        ]
    )

    # 9. Hardware Bridge Node (Executes trajectory on physical ESP32 & publishes /joint_states)
    hardware_bridge_node = Node(
        package=pkg_name,
        executable='arm_v0_moveit_bridge.py',
        output='screen',
        condition=IfCondition(use_hardware)
    )

    # 10. Joint State Publisher GUI (Only if hardware is disabled)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        condition=UnlessCondition(use_hardware)
    )

    # 11. Robot State Publisher Node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[robot_description]
    )

    # 12. RViz2 Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='log',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            robot_description_planning
        ],
        condition=IfCondition(use_rviz)
    )

    return LaunchDescription([
        hardware_arg,
        rviz_arg,
        robot_state_publisher,
        joint_state_publisher_gui,
        hardware_bridge_node,
        move_group_node,
        rviz_node
    ])
