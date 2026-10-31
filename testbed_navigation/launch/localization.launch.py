import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    default_params = os.path.join(
        get_package_share_directory('testbed_navigation'), 'config', 'amcl_params.yaml')

    params_arg = DeclareLaunchArgument('params_file', default_value=default_params)
    sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[LaunchConfiguration('params_file'),
                    {'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'autostart': True,
            'node_names': ['amcl'],
        }],
    )

    initial_pose = Node(
        package='testbed_navigation',
        executable='initial_pose_from_odom.py',
        name='initial_pose_from_odom',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    return LaunchDescription(
        [params_arg, sim_time_arg, amcl, lifecycle_manager, initial_pose])