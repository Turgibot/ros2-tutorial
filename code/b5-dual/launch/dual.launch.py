"""Two Gen3 arms (fake hardware) + MoveIt + RViz. Modelled on robot.launch.py of the single-arm MoveIt package."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
import os

CONTROLLERS = ["left_joint_trajectory_controller", "right_joint_trajectory_controller"]


def generate_launch_description():
    share = get_package_share_directory("b5_dual")

    # MoveItConfigsBuilder reads config/dual.urdf.xacro, dual.srdf, kinematics.yaml, joint_limits.yaml,
    # moveit_controllers.yaml and ompl_planning.yaml from this package.
    moveit_config = (
        MoveItConfigsBuilder("dual", package_name="b5_dual")
        .robot_description(mappings={"use_fake_hardware": "true"})
        .planning_scene_monitor(publish_robot_description=True, publish_robot_description_semantic=True)
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    move_group = Node(package="moveit_ros_move_group", executable="move_group", output="screen",
                      parameters=[moveit_config.to_dict()])
    robot_state_publisher = Node(package="robot_state_publisher", executable="robot_state_publisher",
                                 output="both", parameters=[moveit_config.robot_description])
    ros2_control = Node(package="controller_manager", executable="ros2_control_node", output="both",
                        parameters=[os.path.join(share, "config", "ros2_controllers.yaml")],
                        remappings=[("/controller_manager/robot_description", "/robot_description")])
    spawners = [Node(package="controller_manager", executable="spawner",
                     arguments=[name, "-c", "/controller_manager"])
                for name in ["joint_state_broadcaster"] + CONTROLLERS]
    rviz = Node(package="rviz2", executable="rviz2", output="log",
                arguments=["-d", os.path.join(share, "config", "moveit.rviz")],
                condition=IfCondition(LaunchConfiguration("launch_rviz")),
                parameters=[moveit_config.robot_description, moveit_config.robot_description_semantic,
                            moveit_config.robot_description_kinematics, moveit_config.planning_pipelines,
                            moveit_config.joint_limits])

    return LaunchDescription([
        DeclareLaunchArgument("launch_rviz", default_value="true", description="Launch RViz?"),
        ros2_control, robot_state_publisher, *spawners, move_group, rviz,
    ])
