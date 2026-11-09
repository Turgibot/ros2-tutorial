"""The lab world (C3) with the Gen3 standing at its origin (C2), and bridges for the cameras and the block poses.
Arguments: gui (Gazebo window), vision (add the wrist camera to the arm)."""
import os
import tempfile
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    lab = get_package_share_directory("c3_world")
    sim = os.path.join(get_package_share_directory("c2_sim"), "launch", "sim.launch.py")

    bridge_args = ["/overhead_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/overhead_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
                   "/side_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/wrist_mounted_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/wrist_mounted_camera/depth_image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/wrist_mounted_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo"]
    bridge_args += [f"/model/block_{k}/pose@geometry_msgs/msg/PoseStamped[gz.msgs.Pose" for k in "ABCD"]
    # the service that moves a model (used in D2 to carry a block with the hand)
    bridge_args += ["/world/lab/set_pose@ros_gz_interfaces/srv/SetEntityPose"]

    world = os.path.join(lab, "worlds", "lab.sdf")
    if LaunchConfiguration("static_blocks").perform(context) == "true":
        # D2 and D3: the blocks are static models, moved only by set_pose (see lesson D2). The world file is the
        # same, with <static>true</static> added to every <include>.
        text = open(world).read().replace("</include>", "  <static>true</static>\n    </include>")
        world = os.path.join(tempfile.gettempdir(), "lab_static.sdf")
        open(world, "w").write(text)

    return [
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.join(lab, "models")),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sim),
            launch_arguments={"world": world,
                              "gui": LaunchConfiguration("gui"),
                              "vision": LaunchConfiguration("vision"),
                              "sensors_in_world": "true",
                              "physics_engine": LaunchConfiguration("physics_engine")}.items()),
        Node(package="ros_gz_bridge", executable="parameter_bridge", output="screen",
             parameters=[{"use_sim_time": True}], arguments=bridge_args),
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("gui", default_value="true"),
        DeclareLaunchArgument("vision", default_value="false"),
        DeclareLaunchArgument("physics_engine", default_value="gz-physics-bullet-featherstone-plugin"),
        DeclareLaunchArgument("static_blocks", default_value="false", description="true: blocks that only set_pose moves (D2)"),
        OpaqueFunction(function=launch_setup),
    ])
