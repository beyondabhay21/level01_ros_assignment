import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg = get_package_share_directory('testbed_navigation')
    default_params = os.path.join(pkg, 'config', 'nav2_params.yaml')
    default_rviz = os.path.join(pkg, 'rviz', 'nav.rviz')

    args = [
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='false'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz),
    ]

    use_sim_time = ParameterValue(LaunchConfiguration('use_sim_time'), value_type=bool)
    params = [LaunchConfiguration('params_file'), {'use_sim_time': use_sim_time}]

    controller_server = Node(
        package='nav2_controller', executable='controller_server',
        name='controller_server', output='screen', parameters=params)

    planner_server = Node(
        package='nav2_planner', executable='planner_server',
        name='planner_server', output='screen', parameters=params)

    behavior_server = Node(
        package='nav2_behaviors', executable='behavior_server',
        name='behavior_server', output='screen', parameters=params)

    bt_navigator = Node(
        package='nav2_bt_navigator', executable='bt_navigator',
        name='bt_navigator', output='screen', parameters=params)

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_navigation', output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['controller_server', 'planner_server',
                           'behavior_server', 'bt_navigator'],
        }])

    rviz = Node(
        package='rviz2', executable='rviz2', name='rviz_nav', output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(LaunchConfiguration('rviz')))

    return LaunchDescription(args + [
        controller_server, planner_server, behavior_server,
        bt_navigator, lifecycle_manager, rviz,
    ])