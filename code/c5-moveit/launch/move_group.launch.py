"""MoveIt's move_group for the Gen3 that runs in Gazebo (started by c3_world lab_arm.launch.py or c2_sim sim.launch.py).

Kinova's own sim.launch.py of the MoveIt package starts move_group only together with RViz and silences its log.
This one starts just move_group (and RViz if asked), on simulated time. It plans; the trajectories go to the
joint_trajectory_controller of the simulated arm, which has the same action name as the fake and the real arm."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
import os

PKG = "kinova_gen3_7dof_robotiq_2f_85_moveit_config"


def generate_launch_description():
    description_arguments = {
        "robot_ip": "xxx.yyy.zzz.www", "use_fake_hardware": "false", "gripper": "robotiq_2f_85",
        "dof": "7", "sim_gazebo": "true", "vision": "false",
    }
    moveit_config = (
        MoveItConfigsBuilder("gen3", package_name=PKG)
        .robot_description(mappings=description_arguments)
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(publish_robot_description=True, publish_robot_description_semantic=True)
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )
    use_sim_time = {"use_sim_time": True}

    move_group = Node(
        package="moveit_ros_move_group", executable="move_group", output="screen",
        parameters=[moveit_config.to_dict(), use_sim_time])

    rviz = Node(
        package="rviz2", executable="rviz2", name="rviz2_moveit", output="log",
        arguments=["-d", os.path.join(get_package_share_directory(PKG), "config", "moveit.rviz")],
        parameters=[moveit_config.robot_description, moveit_config.robot_description_semantic,
                    moveit_config.robot_description_kinematics, moveit_config.planning_pipelines,
                    moveit_config.joint_limits, use_sim_time],
        condition=IfCondition(LaunchConfiguration("launch_rviz")))

    return LaunchDescription([DeclareLaunchArgument("launch_rviz", default_value="false"), move_group, rviz])
