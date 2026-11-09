"""The lab world (C3) with the Gen3 standing at its origin (C2), and bridges for the cameras and the block poses.
Arguments: gui (Gazebo window), vision (add the wrist camera to the arm)."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    lab = get_package_share_directory("c3_world")
    sim = os.path.join(get_package_share_directory("c2_sim"), "launch", "sim.launch.py")

    bridge_args = ["/overhead_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/overhead_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
                   "/side_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/wrist_mounted_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/wrist_mounted_camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/wrist_mounted_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo"]
    bridge_args += [f"/model/block_{k}/pose@geometry_msgs/msg/PoseStamped[gz.msgs.Pose" for k in "ABCD"]

    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true"),
        DeclareLaunchArgument("vision", default_value="false"),
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.join(lab, "models")),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sim),
            launch_arguments={"world": os.path.join(lab, "worlds", "lab.sdf"),
                              "gui": LaunchConfiguration("gui"),
                              "vision": LaunchConfiguration("vision"),
                              "sensors_in_world": "true"}.items()),
        Node(package="ros_gz_bridge", executable="parameter_bridge", output="screen",
             parameters=[{"use_sim_time": True}], arguments=bridge_args),
    ])
