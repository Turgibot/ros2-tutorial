cmake_minimum_required(VERSION 3.8)
project(d1_towers)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(towers cpp/towers.cpp)
ament_target_dependencies(towers rclcpp geometry_msgs std_msgs)
install(TARGETS towers DESTINATION lib/${PROJECT_NAME})

install(PROGRAMS py/towers.py DESTINATION lib/${PROJECT_NAME})

ament_package()
