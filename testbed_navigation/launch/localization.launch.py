import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    default_params = os.path.join(
        get_package_share_directory('testbed_navigation'), 'config', 'amcl_params.yaml')

    args = [
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('initial_x', default_value='0.0'),
        DeclareLaunchArgument('initial_y', default_value='5.0'),
        DeclareLaunchArgument('initial_yaw', default_value='0.0'),
    ]

    use_sim_time = ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            LaunchConfiguration('params_file'),
            {
                'use_sim_time': use_sim_time,
                'set_initial_pose': True,
                'initial_pose.x': ParameterValue(LaunchConfiguration('initial_x'), value_type=float),
                'initial_pose.y': ParameterValue(LaunchConfiguration('initial_y'), value_type=float),
                'initial_pose.z': 0.0,
                'initial_pose.yaw': ParameterValue(LaunchConfiguration('initial_yaw'), value_type=float),
            },
        ],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['amcl'],
        }],
    )

    return LaunchDescription(args + [amcl, lifecycle_manager])