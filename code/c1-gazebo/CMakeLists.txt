cmake_minimum_required(VERSION 3.8)
project(c1_gazebo)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)

install(DIRECTORY worlds launch DESTINATION share/${PROJECT_NAME})

add_executable(box_height cpp/box_height.cpp)
ament_target_dependencies(box_height rclcpp geometry_msgs)
install(TARGETS box_height DESTINATION lib/${PROJECT_NAME})

install(PROGRAMS py/box_height.py DESTINATION lib/${PROJECT_NAME})

ament_package()
