cmake_minimum_required(VERSION 3.18)
project(test_package CXX)
set(CMAKE_CXX_STANDARD 11)

find_package(gurobi REQUIRED CONFIG)
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE gurobi::gurobi)
