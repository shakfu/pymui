#!/usr/bin/env python3

import sys
import ctypes
import sdl2
from pathlib import Path

ROOTDIR = Path(__file__).parent.parent / "src"

try:
    from pymui import pymui
except ImportError:
    sys.path.insert(0, str(ROOTDIR))
    from pymui import pymui


# Test state
slider_value = 50.0
checkbox_state = False

def test_window(ctx):
    """Test window with debug output"""
    global slider_value, checkbox_state

    # Properly initialize frame
    ctx.begin()

    if ctx.begin_window("Debug Test", pymui.rect(100, 100, 400, 300)):
        # Simple button test first
        ctx.layout_row([150, -1], 0)
        ctx.label("Button test:")
        if ctx.button("Click me!"):
            print("*** BUTTON WAS CLICKED! ***")

        # Slider test with detailed debugging
        ctx.label("Slider test:")
        old_value = slider_value
        result, new_value = ctx.slider(slider_value, 0.0, 100.0)

        # Debug slider result
        if result != 0:
            print(f"Slider result: {result} (binary: {bin(result)})")
            if result & pymui.Result.ACTIVE:
                print("  - ACTIVE flag set")
            if result & pymui.Result.CHANGE:
                print("  - CHANGE flag set")
            if result & pymui.Result.SUBMIT:
                print("  - SUBMIT flag set")

        if new_value != old_value:
            print(f"Slider value changed: {old_value:.2f} -> {new_value:.2f}")
            slider_value = new_value

        # Checkbox test with detailed debugging
        ctx.label("Checkbox test:")
        old_state = checkbox_state
        result, new_state = ctx.checkbox("Test checkbox", checkbox_state)

        # Debug checkbox result
        if result != 0:
            print(f"Checkbox result: {result} (binary: {bin(result)})")
            if result & pymui.Result.ACTIVE:
                print("  - ACTIVE flag set")
            if result & pymui.Result.CHANGE:
                print("  - CHANGE flag set")
            if result & pymui.Result.SUBMIT:
                print("  - SUBMIT flag set")

        if new_state != old_state:
            print(f"Checkbox state changed: {old_state} -> {new_state}")
            checkbox_state = new_state

        # Show current values
        ctx.label("Current values:")
        ctx.text(f"Slider: {slider_value:.2f}")
        ctx.text(f"Checkbox: {'✓' if checkbox_state else '✗'}")

        # Show mouse position for debugging
        # Note: We'd need to access the context's internal state for this
        ctx.label("Debug info:")
        ctx.text("Move mouse over UI elements")
        ctx.text("and click to test interactions")

        ctx.end_window()

    # Properly end frame
    ctx.end()


def main():
    """Main function with detailed debugging"""
    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        return 1

    try:
        print("Initializing renderer...")
        pymui.renderer_init()
        print("Creating microui context...")
        ctx = pymui.Context()
        print("Starting debug test - interact with UI elements to see debug output")

        running = True
        frame_count = 0

        while running:
            frame_count += 1

            # Handle SDL events
            event = sdl2.SDL_Event()
            mouse_events = 0
            while sdl2.SDL_PollEvent(ctypes.byref(event)):
                if event.type == sdl2.SDL_QUIT:
                    print("Quit event received")
                    running = False
                elif event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    print("Escape pressed")
                    running = False
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    ctx.input_mousemove(event.motion.x, event.motion.y)
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    mouse_events += 1
                    print(f"Mouse down at ({event.button.x}, {event.button.y}), button={event.button.button}")
                    if event.button.button == sdl2.SDL_BUTTON_LEFT:
                        ctx.input_mousedown(event.button.x, event.button.y, pymui.Mouse.LEFT)
                elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                    mouse_events += 1
                    print(f"Mouse up at ({event.button.x}, {event.button.y}), button={event.button.button}")
                    if event.button.button == sdl2.SDL_BUTTON_LEFT:
                        ctx.input_mouseup(event.button.x, event.button.y, pymui.Mouse.LEFT)

            # Process frame
            ctx.begin()
            test_window(ctx)
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

                if cmd.type == pymui.Command.TEXT:
                    pymui.renderer_draw_text(cmd.text.encode('utf-8'), cmd.pos, cmd.color)
                elif cmd.type == pymui.Command.RECT:
                    pymui.renderer_draw_rect(cmd.rect, cmd.color)
                elif cmd.type == pymui.Command.ICON:
                    pymui.renderer_draw_icon(cmd.icon_id, cmd.rect, cmd.color)
                elif cmd.type == pymui.Command.CLIP:
                    pymui.renderer_set_clip_rect(cmd.rect)

            pymui.renderer_present()

            # Debug output every 60 frames (approximately 1 second)
            if frame_count % 60 == 0:
                print(f"Frame {frame_count}: {cmd_count} render commands, {mouse_events} mouse events this frame")

        print("Debug test completed")

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