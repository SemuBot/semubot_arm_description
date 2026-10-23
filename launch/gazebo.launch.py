from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_path
import os

JOINTS = ['shoulder_pitch', 'shoulder_roll', 'shoulder_yaw', 'elbow', 'wrist_yaw', 'wrist_roll',
          'thumb', 'index', 'middle', 'ring', 'little']


def generate_launch_description():
    pkg = get_package_share_path('semubot_arm_description')
    urdf_path = os.path.join(pkg, 'urdf', 'semubot_arm.urdf.xacro')
    robot_description = ParameterValue(
        Command(['xacro ', urdf_path, ' sim:=true side:=', LaunchConfiguration('side')]), value_type=str)

    gazebo = IncludeLaunchDescription(
        PathJoinSubstitution([str(get_package_share_path('ros_gz_sim')), 'launch', 'gz_sim.launch.py']),
        launch_arguments={'gz_args': '-r empty.sdf'}.items())

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}])

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-topic', 'robot_description', '-name', 'semubot_arm'])

    # Clock + joint states out, one cmd_pos topic in per joint (unused sides are harmless)
    commands = [f'/{side}_{joint}_joint/cmd_pos@std_msgs/msg/Float64]gz.msgs.Double'
                for side in ('right', 'left') for joint in JOINTS]
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/world/empty/model/semubot_arm/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            *commands,
        ],
        remappings=[('/world/empty/model/semubot_arm/joint_state', '/joint_states')])

    return LaunchDescription([
        DeclareLaunchArgument('side', default_value='both', choices=['right', 'left', 'both']),
        # Lets Gazebo resolve package://semubot_arm_description/... mesh paths
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.dirname(pkg)),
        gazebo,
        robot_state_publisher,
        spawn,
        bridge,
    ])
