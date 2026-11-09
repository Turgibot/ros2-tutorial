"""Gazebo server with the hello world (paused), plus the ros_gz bridge for /clock, the box pose (PoseStamped) and the world-control service."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    default_world = os.path.join(get_package_share_directory("c1_gazebo"), "worlds", "hello.sdf")
    world = DeclareLaunchArgument("world_file", default_value=default_world)
    # -s: server only (no window). No -r, so the world starts paused.
    gz = ExecuteProcess(cmd=["gz", "sim", "-s", LaunchConfiguration("world_file")], output="screen")
    bridge = Node(
        package="ros_gz_bridge", executable="parameter_bridge", output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/model/box/pose@geometry_msgs/msg/PoseStamped[gz.msgs.Pose",
            "/world/hello/control@ros_gz_interfaces/srv/ControlWorld",
        ])
    return LaunchDescription([world, gz, bridge])
