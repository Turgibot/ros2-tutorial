"""The lab world alone (table, four blocks, overhead camera), plus the bridge for the clock, the block poses and the camera.
Add gui:=true for the Gazebo window."""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


def launch_setup(context, *args, **kwargs):
    share = get_package_share_directory("c3_world")
    world = os.path.join(share, "worlds", "lab.sdf")
    gui = LaunchConfiguration("gui").perform(context) == "true"
    # -r: run at once; -s: server only; --headless-rendering: the camera renders without a display
    cmd = ["gz", "sim", "-r"] + ([] if gui else ["-s", "--headless-rendering"]) + [world]
    bridge_args = ["/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
                   "/overhead_camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
                   "/overhead_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
                   "/side_camera/image@sensor_msgs/msg/Image[gz.msgs.Image"]
    bridge_args += [f"/model/block_{k}/pose@geometry_msgs/msg/PoseStamped[gz.msgs.Pose" for k in "ABCD"]
    return [
        # model://block_A in the world file is found through this path
        AppendEnvironmentVariable("GZ_SIM_RESOURCE_PATH", os.path.join(share, "models")),
        ExecuteProcess(cmd=cmd, output="screen"),
        Node(package="ros_gz_bridge", executable="parameter_bridge", output="screen", arguments=bridge_args),
    ]


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument("gui", default_value="false"), OpaqueFunction(function=launch_setup)])
