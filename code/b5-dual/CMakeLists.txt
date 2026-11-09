cmake_minimum_required(VERSION 3.8)
project(b5_dual)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(parameter_traits REQUIRED)  # needed before MoveIt on Jazzy
find_package(moveit_ros_planning_interface REQUIRED)

# the configuration: robot description, MoveIt files, launch file
install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})

# C++ program
add_executable(move_arm cpp/move_arm.cpp)
ament_target_dependencies(move_arm rclcpp geometry_msgs moveit_msgs tf2 moveit_ros_planning_interface)
install(TARGETS move_arm DESTINATION lib/${PROJECT_NAME})

# Python program, copied as it is so ros2 run finds it
install(PROGRAMS py/move_arm.py DESTINATION lib/${PROJECT_NAME})

ament_package()
