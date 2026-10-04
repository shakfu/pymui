#!/bin/bash
# Build the C reference demo without CMake. Run from this directory.
set -e

OS_NAME=`uname -o 2>/dev/null || uname -s`

if [ $OS_NAME == "Msys" ]; then
    GLFLAG="-lopengl32"
elif [ $OS_NAME == "Darwin" ]; then
    GLFLAG="-framework OpenGL"
else
    GLFLAG="-lGL"
fi

CFLAGS="-I.. -I../.. -Wall -std=c11 -pedantic `sdl2-config --cflags --libs` $GLFLAG -lm -O3 -g"

gcc main.c ../renderer.c ../../microui.c -o microui_demo $CFLAGS
