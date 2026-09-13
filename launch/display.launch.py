import os
import xacro

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    package_path = get_package_share_directory(
        'devotics_arm_description'
    )

    xacro_path = os.path.join(
        package_path,
        'urdf',
        'devotics_arm.urdf.xacro'
    )

    robot_description_doc = xacro.process_file(xacro_path)
    robot_description = robot_description_doc.toxml()

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[
                {'robot_description': robot_description}
            ]
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            output='screen'
        )

    ])
