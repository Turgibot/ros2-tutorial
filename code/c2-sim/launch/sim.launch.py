"""The Kinova Gen3 (7 DoF, Robotiq 2F-85) in Gazebo.

Based on kortex_bringup/launch/kortex_sim_control.launch.py, which always opens the Gazebo window and always loads
empty.sdf. Differences: `gui` switches the window off, `world` picks the world file, `gripper` defaults to
robotiq_2f_85, `x y z` set where the arm is spawned, and RViz is off by default. The controllers, the robot
description and the controller names are the same as in the upstream launch file, so a program written for this
one also works with the fake hardware and (in principle) with the real arm."""
import os
import re

from ament_index_python.packages import get_package_prefix
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription,
                            OpaqueFunction)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    gui = LaunchConfiguration("gui").perform(context)
    world = LaunchConfiguration("world").perform(context)
    gripper = LaunchConfiguration("gripper")
    launch_rviz = LaunchConfiguration("launch_rviz")
    use_sim_time = {"use_sim_time": True}

    controllers = PathJoinSubstitution([
        FindPackageShare("kortex_description"), "arms/gen3/7dof/config", "ros2_controllers.yaml"])
    robot_description_content = Command([
        PathJoinSubstitution([FindExecutable(name="xacro")]), " ",
        PathJoinSubstitution([FindPackageShare("kortex_description"), "robots", "kinova.urdf.xacro"]), " ",
        "robot_ip:=xxx.yyy.zzz.www name:=gen3 arm:=gen3 dof:=7 prefix:=\"\" sim_gazebo:=true ",
        "vision:=", LaunchConfiguration("vision"), " ",
        "gazebo_renderer:=ogre2 ",
        "simulation_controllers:=", controllers, " gripper:=", gripper])
    robot_description = robot_description_content.perform(context)
    if LaunchConfiguration("sensors_in_world").perform(context) == "true":
        # Gazebo may have only one Sensors system (the camera renderer). The robot description adds one, and so
        # does a world that has cameras of its own: two of them crash the simulator. Remove the robot's.
        robot_description = re.sub(r'<plugin filename="gz-sim-sensors-system".*?</plugin>', "", robot_description,
                                   flags=re.S)

    # Gazebo: -r runs at once, -s is the server only (no window; --headless-rendering lets cameras render without a display)
    engine = LaunchConfiguration("physics_engine").perform(context)
    gz_args = "-r -v 3 " + ("" if gui == "true" else "-s --headless-rendering ") + world + \
        (f" --physics-engine {engine}" if engine not in ("", "default") else "")
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([FindPackageShare("ros_gz_sim"), "/launch/gz_sim.launch.py"]),
        launch_arguments={"gz_args": gz_args}.items())

    spawn = Node(
        package="ros_gz_sim", executable="create", output="screen",
        arguments=["-string", robot_description, "-name", "gen3", "-allow_renaming", "true",
                   "-x", LaunchConfiguration("x"), "-y", LaunchConfiguration("y"), "-z", LaunchConfiguration("z")])

    clock_bridge = Node(
        package="ros_gz_bridge", executable="parameter_bridge", output="screen",
        arguments=["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"])

    rsp = Node(package="robot_state_publisher", executable="robot_state_publisher", output="both",
               parameters=[{"robot_description": robot_description}, use_sim_time])

    def spawner(*args):
        return Node(package="controller_manager", executable="spawner",
                    arguments=list(args) + ["-c", "/controller_manager"])

    rviz = Node(package="rviz2", executable="rviz2", output="log", condition=IfCondition(launch_rviz),
                arguments=["-d", PathJoinSubstitution([FindPackageShare("kortex_description"), "rviz",
                                                       "view_robot.rviz"])],
                parameters=[use_sim_time])

    robotiq_share = os.path.join(get_package_prefix("robotiq_description"), "share")
    resource_path = AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", robotiq_share)

    return [clock_bridge, rsp,
            spawner("joint_state_broadcaster"), spawner("joint_trajectory_controller"),
            spawner("twist_controller", "--inactive"), spawner("joint_group_velocity_controller", "--inactive"),
            spawner("robotiq_gripper_controller"),
            resource_path, gazebo, spawn, rviz]


def generate_launch_description():
    args = [
        DeclareLaunchArgument("gui", default_value="true", description="open the Gazebo window (false: server only)"),
        DeclareLaunchArgument("world", default_value="empty.sdf", description="world file (name or full path)"),
        DeclareLaunchArgument("gripper", default_value="robotiq_2f_85", description="robotiq_2f_85, robotiq_2f_140 or empty"),
        DeclareLaunchArgument("x", default_value="0.0"),
        DeclareLaunchArgument("y", default_value="0.0"),
        DeclareLaunchArgument("z", default_value="0.0"),
        DeclareLaunchArgument("vision", default_value="false", description="true: add the wrist camera (a Realsense) to the arm"),
        DeclareLaunchArgument("sensors_in_world", default_value="false",
                              description="true if the world file already has the Sensors system (the C3 lab does)"),
        DeclareLaunchArgument("physics_engine", default_value="gz-physics-bullet-featherstone-plugin",
                              description='physics engine plugin; "default" is the default of Gazebo (DART)'),
        DeclareLaunchArgument("launch_rviz", default_value="false"),
    ]
    return LaunchDescription(args + [OpaqueFunction(function=launch_setup)])
