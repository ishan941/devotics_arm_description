import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_description = get_package_share_directory('devotics_arm_description')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # 1. Process Xacro with sim_mode:=true
    xacro_file = os.path.join(pkg_description, 'urdf', 'devotics_arm.urdf.xacro')
    robot_description_doc = xacro.process_file(xacro_file, mappings={'sim_mode': 'true'})
    robot_description = {'robot_description': robot_description_doc.toxml(), 'use_sim_time': True}

    # 2. Robot State Publisher Node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # 3. Gazebo Sim Launch (with table and cube world)
    world_file = os.path.join(pkg_description, 'worlds', 'table_cube.sdf')
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )


    # 4. Spawner Node (ros_gz_sim 'create')
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name', 'devotics_arm',
            '-topic', 'robot_description',
            '-z', '0.05'
        ]
    )

    # 5. Bridge Gazebo Clock to ROS 2 Clock
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen'
    )

    # 6. Controller Spawners
    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )

    arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['devotics_arm_controller'],
        output='screen'
    )

    gripper_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['gripper_controller'],
        output='screen'
    )

    return LaunchDescription([
        node_robot_state_publisher,
        gazebo_sim,
        spawn_robot,
        clock_bridge,
        joint_state_broadcaster_spawner,
        arm_controller_spawner,
        gripper_controller_spawner
    ])
