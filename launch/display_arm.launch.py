from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_path
import os


def generate_launch_description():
    pkg = get_package_share_path('semubot_arm_description')
    urdf_path = os.path.join(pkg, 'urdf', 'semubot_arm.urdf.xacro')
    rviz_path = os.path.join(pkg, 'config', 'semubot_arm.rviz')

    robot_description = ParameterValue(
        Command(['xacro ', urdf_path, ' side:=', LaunchConfiguration('side')]), value_type=str)
    gui = LaunchConfiguration('gui')

    return LaunchDescription([
        DeclareLaunchArgument('side', default_value='both', choices=['right', 'left', 'both']),
        DeclareLaunchArgument('gui', default_value='true',
                              description='Joint sliders (needs joint_state_publisher_gui)'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            condition=IfCondition(gui)),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            condition=UnlessCondition(gui)),
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', rviz_path]),
    ])
