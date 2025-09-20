#!/usr/bin/env python3

import sys
import sdl2
import sdl2.ext
import ctypes
from pathlib import Path

ROOTDIR = Path(__file__).parent.parent / "src"

try:
    from pymui import pymui
except ImportError:
    sys.path.insert(0, str(ROOTDIR))
    from pymui import pymui


def test_events_directly():
    """Test SDL event handling directly"""
    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        return

    print("Testing SDL event handling...")

    # Initialize renderer to create window
    pymui.renderer_init()
    print("Renderer initialized, window should be visible")

    # Test both event handling methods
    frame_count = 0
    while frame_count < 60:  # Run for ~1 second
        frame_count += 1

        print(f"\n--- Frame {frame_count} ---")

        # Method 1: Using SDL_PollEvent directly (similar to C code)
        event = sdl2.SDL_Event()
        direct_events = []
        while sdl2.SDL_PollEvent(ctypes.byref(event)):
            direct_events.append(event.type)

        if direct_events:
            print(f"Direct SDL_PollEvent got {len(direct_events)} events: {direct_events}")

        # Method 2: Using sdl2.ext.get_events()
        ext_events = sdl2.ext.get_events()
        if ext_events:
            print(f"sdl2.ext.get_events got {len(ext_events)} events: {[e.type for e in ext_events]}")

        # Clear screen and present to keep window responsive
        pymui.renderer_clear(pymui.color(32, 32, 32, 255))
        pymui.renderer_present()

    sdl2.SDL_Quit()
    print("Event test completed")


if __name__ == "__main__":
    test_events_directly()