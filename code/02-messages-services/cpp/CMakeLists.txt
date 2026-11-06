cmake_minimum_required(VERSION 3.8)
project(a2_services)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(a2_interfaces REQUIRED)

add_executable(server src/server.cpp)
ament_target_dependencies(server rclcpp a2_interfaces)
add_executable(client src/client.cpp)
ament_target_dependencies(client rclcpp a2_interfaces)

install(TARGETS server client DESTINATION lib/${PROJECT_NAME})
ament_package()
