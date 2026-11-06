"""Starts two announcers (with settings from config/announcers.yaml) and one listener.

    ros2 launch a4_params announcers.launch.py              Python programs
    ros2 launch a4_params announcers.launch.py lang:=cpp    C++ programs
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    params_file = os.path.join(get_package_share_directory('a4_params'), 'config', 'announcers.yaml')
    lang = LaunchConfiguration('lang')

    def program(name):
        # Python programs were installed as name.py, C++ programs as name.
        return PythonExpression(["'", name, ".py' if '", lang, "' == 'py' else '", name, "'"])

    return LaunchDescription([
        DeclareLaunchArgument('lang', default_value='py', description="'py' or 'cpp': which programs to start"),
        Node(package='a4_params', executable=program('announcer'), name='planner_a',
             parameters=[params_file], output='screen'),
        Node(package='a4_params', executable=program('announcer'), name='planner_b',
             parameters=[params_file], output='screen'),
        Node(package='a4_params', executable=program('listener'), output='screen'),
    ])
