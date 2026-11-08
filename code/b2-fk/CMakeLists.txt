cmake_minimum_required(VERSION 3.8)
project(b2_fk)

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)

# C++ programs (no ROS libraries: only the C++ standard library and Eigen)
add_executable(fk2 cpp/fk2.cpp)
add_executable(fk_gen3 cpp/fk_gen3.cpp)
target_link_libraries(fk_gen3 Eigen3::Eigen)
install(TARGETS fk2 fk_gen3 DESTINATION lib/${PROJECT_NAME})

# Python programs: copied as they are, so `ros2 run` can find them
install(PROGRAMS py/fk2.py py/fk_gen3.py DESTINATION lib/${PROJECT_NAME})

ament_package()
