#!/usr/bin/env python3
"""
arm_v0_moveit.launch.py — MoveIt 2 Motion Planning for Devotics Arm V0

Features:
- Loads URDF (Xacro), SRDF, Kinematics (KDL), Joint Limits, and OMPL
- Launches MoveIt 2 move_group node
- Launches robot_state_publisher
- Optional interactive joint_state_publisher_gui (set gui:=false when using physical robot)
- Launches RViz2 with Motion Planning display
"""

import os
import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
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

    # 1. Declare Launch Arguments
    gui_arg = DeclareLaunchArgument(
        'gui',
        default_value='true',
        description='Launch joint_state_publisher_gui (set false when physical robot node is running)'
    )

    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz2'
    )

    use_gui = LaunchConfiguration('gui')
    use_rviz = LaunchConfiguration('rviz')

    # 2. Process Robot Description (URDF / Xacro)
    pkg_share = get_package_share_directory(pkg_name)
    xacro_file = os.path.join(pkg_share, 'urdf', 'devotics_arm_v0.urdf.xacro')
    doc = xacro.process_file(xacro_file)
    robot_description = {'robot_description': doc.toxml()}

    # 3. Load Robot Description Semantic (SRDF)
    srdf_content = load_file(pkg_name, 'config/devotics_arm_v0.srdf')
    robot_description_semantic = {'robot_description_semantic': srdf_content}

    # 4. Load Kinematics Configuration (KDL Solver)
    kinematics_yaml = load_yaml(pkg_name, 'config/v0_kinematics.yaml')
    robot_description_kinematics = {'robot_description_kinematics': kinematics_yaml}

    # 5. Load Joint Limits & Trajectory Generation Settings
    joint_limits_yaml = load_yaml(pkg_name, 'config/v0_joint_limits.yaml')
    robot_description_planning = {'robot_description_planning': joint_limits_yaml}

    # 6. Load OMPL Planning Pipeline Configuration
    ompl_planning_yaml = load_yaml(pkg_name, 'config/v0_ompl_planning.yaml')
    planning_pipelines = {
        'planning_pipelines': ['ompl'],
        'default_planning_pipeline': 'ompl',
        'ompl': ompl_planning_yaml,
    }

    # 7. MoveGroup Node Configuration
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
            {
                'publish_planning_scene': True,
                'publish_geometry_updates': True,
                'publish_state_updates': True,
                'publish_transforms_updates': True,
                'moveit_manage_controllers': False,
            }
        ]
    )

    # 8. Robot State Publisher Node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[robot_description]
    )

    # 9. Joint State Publisher GUI (for offline manual testing)
    joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen',
        condition=IfCondition(use_gui)
    )

    # 10. RViz2 Node
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
        gui_arg,
        rviz_arg,
        robot_state_publisher,
        joint_state_publisher_gui,
        move_group_node,
        rviz_node
    ])
