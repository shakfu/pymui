cmake_minimum_required(VERSION 3.28)

# Version lives in pyproject.toml only.
project(pymui LANGUAGES C)

set(CMAKE_C_STANDARD 17)

# set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR})

add_subdirectory(microui)
add_subdirectory(src)

