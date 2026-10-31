cmake_minimum_required(VERSION 3.8)
project(testbed_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config rviz
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS scripts/initial_pose_from_odom.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()