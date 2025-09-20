
project(libmicroui_sdl_demo VERSION 2.0.2)


add_executable(
    microui_sdl_demo
    ${CMAKE_CURRENT_SOURCE_DIR}/main.c
)

target_compile_options(
    microui_sdl_demo
    PUBLIC
    -Wall
    -pedantic
    -O3
    -g
)

target_link_libraries(
    microui_sdl_demo
    PUBLIC
    m
    microui
    microui_sdl
)