cmake_minimum_required(VERSION 3.8)
project(d2_pickplace)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(d2_interfaces REQUIRED)

add_executable(pick_place_client cpp/pick_place_client.cpp)
ament_target_dependencies(pick_place_client rclcpp rclcpp_action d2_interfaces)
install(TARGETS pick_place_client DESTINATION lib/${PROJECT_NAME})

# Python programs, copied as they are (gen3.py is next to them: the kinematics of B3)
install(PROGRAMS py/pick_place_server.py py/pick_place_client.py DESTINATION lib/${PROJECT_NAME})
install(FILES py/gen3.py DESTINATION lib/${PROJECT_NAME})

ament_package()
