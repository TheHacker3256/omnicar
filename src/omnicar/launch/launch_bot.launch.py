import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.substitutions import Command


def generate_launch_description():
    package_name='omnicar'

    controller_params = os.path.join(get_package_share_directory(package_name), 'config','my_controllers.yaml')
    robot_description = Command(['ros2 param get --hide-type /robot_state_publisher robot_description'])

    rsp = IncludeLaunchDescription(
      PythonLaunchDescriptionSource([os.path.join(get_package_share_directory(package_name),'launch','rsp.launch.py')]), 
      launch_arguments={'use_sim_time': 'false', 'sim_mode': 'false'}.items()
    )

    controller_manager = Node(
      package='controller_manager',
      executable='ros2_control_node',
      parameters=[{'robot_description': robot_description}, controller_params],
    )
    delayed_controller_manager = TimerAction(period=5.0,actions=[controller_manager])



    diff_drive_spawner = Node(
    package="controller_manager",
    executable="spawner",
    arguments=["diff_cont"],
    )
    delayed_diff_drive_spawner = RegisterEventHandler(
      event_handler=OnProcessStart(
        target_action=controller_manager,
        on_start=[diff_drive_spawner],
      )
    )


    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_broad"],
    )
    delayed_joint_broad_spawner = RegisterEventHandler(
      event_handler=OnProcessStart(
        target_action=controller_manager,
        on_start=[joint_broad_spawner],
      )
    )

    # Launch them all!
    return LaunchDescription([
      rsp,
      delayed_controller_manager,
      delayed_diff_drive_spawner,
      delayed_joint_broad_spawner
    ])
