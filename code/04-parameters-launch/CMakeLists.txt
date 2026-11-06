cmake_minimum_required(VERSION 3.8)
project(a4_params)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# C++ programs
add_executable(announcer cpp/announcer.cpp)
ament_target_dependencies(announcer rclcpp std_msgs)
add_executable(listener cpp/listener.cpp)
ament_target_dependencies(listener rclcpp std_msgs)
install(TARGETS announcer listener DESTINATION lib/${PROJECT_NAME})

# Python programs: copied as they are, so `ros2 run` and `ros2 launch` can find them
install(PROGRAMS py/announcer.py py/listener.py DESTINATION lib/${PROJECT_NAME})

# Launch and parameter files
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

ament_package()
