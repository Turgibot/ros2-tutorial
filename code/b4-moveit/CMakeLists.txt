cmake_minimum_required(VERSION 3.8)
project(b4_moveit)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(shape_msgs REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(parameter_traits REQUIRED)  # needed before MoveIt on Jazzy
find_package(moveit_ros_planning_interface REQUIRED)

foreach(prog move_pose add_box)
  add_executable(${prog} cpp/${prog}.cpp)
  ament_target_dependencies(${prog} rclcpp geometry_msgs shape_msgs moveit_msgs tf2
                            moveit_ros_planning_interface)
  install(TARGETS ${prog} DESTINATION lib/${PROJECT_NAME})
endforeach()

# Python programs, copied as they are, so ros2 run finds them
install(PROGRAMS py/move_pose.py py/add_box.py DESTINATION lib/${PROJECT_NAME})

ament_package()
