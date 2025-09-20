
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/src/pymui)

find_package(
	Python
	COMPONENTS Interpreter Development.Module
	REQUIRED)

add_custom_command(
	OUTPUT "${CMAKE_BINARY_DIR}/pymui.c"
	MAIN_DEPENDENCY "${CMAKE_CURRENT_SOURCE_DIR}/pymui/pymui.pyx"
	VERBATIM
	COMMAND
		Python::Interpreter -m cython
		"${CMAKE_CURRENT_SOURCE_DIR}/pymui/pymui.pyx" --output-file
		"${CMAKE_BINARY_DIR}/pymui.c")

python_add_library(
    pymui
    MODULE
    "${CMAKE_BINARY_DIR}/pymui.c"
    WITH_SOABI
)

add_dependencies(
	pymui
	microui
	microui_sdl
)

target_include_directories(
    pymui
    PUBLIC
    ${CMAKE_SOURCE_DIR}/microui
    ${CMAKE_SOURCE_DIR}/microui/sdl
)

target_link_libraries(
    pymui
    PUBLIC
    microui
    microui_sdl
)

