cmake_minimum_required(VERSION 3.8)
project(b3_ik)

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)

# C++ programs (no ROS libraries: only the C++ standard library and Eigen)
add_executable(ik2 cpp/ik2.cpp)
add_executable(ik_gen3 cpp/ik_gen3.cpp)
add_executable(null_motion cpp/null_motion.cpp)
foreach(t ik_gen3 null_motion)
  target_link_libraries(${t} Eigen3::Eigen)
  target_include_directories(${t} PRIVATE cpp)
endforeach()
install(TARGETS ik2 ik_gen3 null_motion DESTINATION lib/${PROJECT_NAME})

# Python programs: copied as they are (gen3.py next to them), so `ros2 run` can find them
install(PROGRAMS py/ik2.py py/ik_gen3.py py/null_motion.py py/gen3.py DESTINATION lib/${PROJECT_NAME})

ament_package()
