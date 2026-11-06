cmake_minimum_required(VERSION 3.8)
project(a3_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Execute.action"
)
ament_package()
