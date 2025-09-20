cmake_minimum_required(VERSION 3.29)

project(pymui VERSION 1.4.8)

set(CMAKE_C_STANDARD 17)

# set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR})

add_subdirectory(microui)
add_subdirectory(src)

