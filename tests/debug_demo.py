#!/usr/bin/env python3

import sys

try:
    print("Starting debug demo...")
    import sdl2
    import sdl2.ext
    from pymui import pymui

    print("Imports successful")

    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        sys.exit(1)

    print("SDL initialized")

    # Initialize renderer
    pymui.renderer_init()
    print("Renderer initialized")

    # Initialize microui context
    ctx = pymui.Context()
    print("Context created")

    print("Starting main loop...")
    frame_count = 0

    while frame_count < 10:  # Just run for 10 frames for testing
        frame_count += 1
        print(f"Frame {frame_count}")

        # Handle SDL events
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                print("Quit event received")
                sys.exit(0)

        # Process frame
        ctx.begin()

        # Simple window
        if ctx.begin_window("Test Window", pymui.rect(100, 100, 200, 150)):
            ctx.label("Hello World")
            if ctx.button("Test Button"):
                print("Button pressed!")
            ctx.end_window()

        ctx.end()

        # Render
        pymui.renderer_clear(pymui.color(64, 64, 64, 255))

        # Process commands
        ctx.reset_command_iterator()
        cmd_count = 0
        while True:
            cmd = ctx.next_command()
            if cmd is None:
                break
            cmd_count += 1

        print(f"  Processed {cmd_count} commands")

        pymui.renderer_present()

    print("Demo completed successfully!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    try:
        sdl2.SDL_Quit()
    except:
        pass