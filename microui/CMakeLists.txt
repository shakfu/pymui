cmake_minimum_required(VERSION 3.29)

project(libmicroui VERSION 2.0.2)

set(CMAKE_C_STANDARD 11)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

add_library(
    microui
    STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/microui.c
)

target_compile_options(
    microui
    PUBLIC
    -Wall
    -pedantic
)

target_include_directories(
    microui
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)


add_subdirectory(sdl)


