
project(libmicroui_sdl VERSION 2.0.2)

# Wheels link the static SDL2 from scripts/build_sdl2.sh.
if(DEFINED ENV{CIBUILDWHEEL})
    list(PREPEND CMAKE_PREFIX_PATH "${CMAKE_SOURCE_DIR}/build/sdl2")
endif()
find_package(SDL2 REQUIRED CONFIG)
if(TARGET SDL2::SDL2)
    set(SDL2_TARGET SDL2::SDL2)
else()
    set(SDL2_TARGET SDL2::SDL2-static)
endif()

# libGL.so.1 is on the manylinux allowlist; GLVND's libOpenGL.so.0 is not.
set(OpenGL_GL_PREFERENCE LEGACY)
find_package(OpenGL REQUIRED)

add_library(
    microui_sdl
    STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/renderer.c
)

target_include_directories(
    microui_sdl
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_compile_definitions(
    microui_sdl
    PUBLIC
    -D_THREAD_SAFE
)

set_target_properties(microui_sdl PROPERTIES POSITION_INDEPENDENT_CODE ON)

target_link_libraries(
    microui_sdl
    PUBLIC
    microui
    ${SDL2_TARGET}
    OpenGL::GL
    $<$<NOT:$<PLATFORM_ID:Windows>>:m>  # stb_truetype
)

# The C demo is a development aid; wheels do not ship it.
if(NOT SKBUILD)
    add_subdirectory(demo)
endif()

