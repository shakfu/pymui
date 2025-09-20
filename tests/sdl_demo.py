#!/usr/bin/env python3

import sys

try:
    import sdl2
    import sdl2.ext
    print("SDL2 imported successfully")

    # Test SDL initialization
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        sys.exit(1)

    print("SDL initialized successfully")

    # Test events
    events = sdl2.ext.get_events()
    print(f"Got {len(events)} events")

    sdl2.SDL_Quit()
    print("SDL test completed successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)