cmake_minimum_required(VERSION 3.8)
project(a6_frames)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)

# C++ programs
add_executable(orbit cpp/orbit.cpp)
ament_target_dependencies(orbit rclcpp geometry_msgs tf2_ros)
add_executable(where cpp/where.cpp)
ament_target_dependencies(where rclcpp geometry_msgs tf2 tf2_ros)
install(TARGETS orbit where DESTINATION lib/${PROJECT_NAME})

# Python programs: copied as they are, so `ros2 run` can find them
install(PROGRAMS py/orbit.py py/where.py DESTINATION lib/${PROJECT_NAME})

ament_package()
