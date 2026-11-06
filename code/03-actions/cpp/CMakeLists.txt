cmake_minimum_required(VERSION 3.8)
project(a3_actions)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(a3_interfaces REQUIRED)

add_executable(server src/server.cpp)
ament_target_dependencies(server rclcpp rclcpp_action a3_interfaces)
add_executable(client src/client.cpp)
ament_target_dependencies(client rclcpp rclcpp_action a3_interfaces)

install(TARGETS server client DESTINATION lib/${PROJECT_NAME})
ament_package()
