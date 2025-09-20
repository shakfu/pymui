
project(libmicroui_sdl VERSION 2.0.2)

if(CMAKE_HOST_APPLE)
    execute_process(
        COMMAND brew --prefix
        OUTPUT_VARIABLE homebrew_prefix
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    if(DEFINED homebrew_prefix)
        set(LOCAL_PREFIX ${homebrew_prefix})
    endif()
endif()


add_library(
    microui_sdl
    STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/renderer.c
)

target_include_directories(
    microui_sdl
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${LOCAL_PREFIX}/include
)

target_compile_definitions(
    microui_sdl
    PUBLIC
    -D_THREAD_SAFE
)

target_compile_options(
    microui_sdl
    PUBLIC
    -Wall
    -pedantic
)

target_link_directories(
    microui_sdl
    PUBLIC
    ${LOCAL_PREFIX}/lib
)


target_link_libraries(
    microui_sdl
    PUBLIC
    microui
    "$<$<PLATFORM_ID:Darwin>:-framework OpenGL>"
    -lSDL2
)

add_subdirectory(demo)

