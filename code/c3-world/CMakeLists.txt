cmake_minimum_required(VERSION 3.8)
project(c3_world)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)

install(DIRECTORY worlds models launch DESTINATION share/${PROJECT_NAME})

add_executable(check_settled cpp/check_settled.cpp)
ament_target_dependencies(check_settled rclcpp geometry_msgs)
install(TARGETS check_settled DESTINATION lib/${PROJECT_NAME})

install(PROGRAMS py/check_settled.py py/save_image.py DESTINATION lib/${PROJECT_NAME})

ament_package()
