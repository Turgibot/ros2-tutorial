cmake_minimum_required(VERSION 3.8)
project(a2_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SymbolicAction.msg"
  "srv/CheckAction.srv"
  DEPENDENCIES   # srv/CheckAction.srv uses the message above, which lives in this same package
)
ament_package()
