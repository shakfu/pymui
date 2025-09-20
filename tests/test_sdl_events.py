#!/usr/bin/env python3

import sys
import ctypes
import sdl2

def main():
    """Test SDL events directly without pymui"""
    print("Testing SDL events directly...")

    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        return 1

    try:
        # Create window manually (similar to what renderer does)
        window = sdl2.SDL_CreateWindow(
            b"SDL Event Test",
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            800, 600,
            sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN
        )

        if not window:
            print(f"SDL_CreateWindow Error: {sdl2.SDL_GetError()}")
            return 1

        print("Window created - move mouse and click to see events, ESC to exit")

        gl_context = sdl2.SDL_GL_CreateContext(window)
        if not gl_context:
            print(f"SDL_GL_CreateContext Error: {sdl2.SDL_GetError()}")

        running = True
        event_count = 0

        while running and event_count < 100:  # Limit events for testing
            event = sdl2.SDL_Event()
            while sdl2.SDL_PollEvent(ctypes.byref(event)):
                event_count += 1
                print(f"Event {event_count}: type={event.type}")

                if event.type == sdl2.SDL_QUIT:
                    print("  -> SDL_QUIT")
                    running = False
                elif event.type == sdl2.SDL_KEYDOWN:
                    print(f"  -> SDL_KEYDOWN: key={event.key.keysym.sym}")
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        print("  -> Escape pressed, exiting")
                        running = False
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    print(f"  -> SDL_MOUSEMOTION: ({event.motion.x}, {event.motion.y})")
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    print(f"  -> SDL_MOUSEBUTTONDOWN: button={event.button.button} at ({event.button.x}, {event.button.y})")
                elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                    print(f"  -> SDL_MOUSEBUTTONUP: button={event.button.button} at ({event.button.x}, {event.button.y})")
                else:
                    print(f"  -> Other event type: {event.type}")

            # Clear screen to keep window responsive
            sdl2.SDL_GL_SwapWindow(window)

        print(f"Test completed - processed {event_count} events")

        # Cleanup
        if gl_context:
            sdl2.SDL_GL_DeleteContext(gl_context)
        if window:
            sdl2.SDL_DestroyWindow(window)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        sdl2.SDL_Quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())