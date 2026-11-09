cmake_minimum_required(VERSION 3.8)
project(d3_skills)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(a3_interfaces REQUIRED)
find_package(std_msgs REQUIRED)

add_executable(run_plan cpp/run_plan.cpp)
ament_target_dependencies(run_plan rclcpp rclcpp_action a3_interfaces std_msgs)
install(TARGETS run_plan DESTINATION lib/${PROJECT_NAME})

install(PROGRAMS py/execute_server.py py/run_plan.py DESTINATION lib/${PROJECT_NAME})

ament_package()
