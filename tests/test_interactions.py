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


# SDL button mapping
button_map = {
    sdl2.SDL_BUTTON_LEFT: pymui.Mouse.LEFT,
    sdl2.SDL_BUTTON_RIGHT: pymui.Mouse.RIGHT,
    sdl2.SDL_BUTTON_MIDDLE: pymui.Mouse.MIDDLE,
}

# SDL key mapping
key_map = {
    sdl2.SDLK_LSHIFT: pymui.Key.SHIFT,
    sdl2.SDLK_RSHIFT: pymui.Key.SHIFT,
    sdl2.SDLK_LCTRL: pymui.Key.CTRL,
    sdl2.SDLK_RCTRL: pymui.Key.CTRL,
    sdl2.SDLK_LALT: pymui.Key.ALT,
    sdl2.SDLK_RALT: pymui.Key.ALT,
    sdl2.SDLK_RETURN: pymui.Key.RETURN,
    sdl2.SDLK_BACKSPACE: pymui.Key.BACKSPACE,
    sdl2.SDLK_ESCAPE: pymui.Key.BACKSPACE,  # Use backspace for escape for now
}

# Test variables
slider_value = 50.0
checkbox_state = False

def test_window(ctx):
    """Simple test window with interactive elements"""
    global slider_value, checkbox_state

    # Properly initialize frame
    ctx.begin()

    if ctx.begin_window("Interaction Test", pymui.rect(50, 50, 350, 250)):
        ctx.layout_row([120, -1], 0)

        # Slider test
        ctx.label("Slider Value:")
        result, new_val = ctx.slider(slider_value, 0.0, 100.0)
        if result & pymui.Result.CHANGE:
            print(f"Slider changed: {slider_value:.2f} -> {new_val:.2f}")
            slider_value = new_val

        # Checkbox test
        ctx.label("Checkbox:")
        result, new_state = ctx.checkbox("Test checkbox", checkbox_state)
        if result & pymui.Result.CHANGE:
            print(f"Checkbox changed: {checkbox_state} -> {new_state}")
            checkbox_state = new_state

        # Button test (for comparison)
        ctx.label("Button:")
        if ctx.button("Click me!"):
            print("Button was clicked!")

        # Display current values
        ctx.label("Current values:")
        ctx.label(f"Slider: {slider_value:.2f}")
        ctx.label(f"Checkbox: {'✓' if checkbox_state else '✗'}")

        # Instructions
        ctx.label("Instructions:")
        ctx.text("Try interacting with the slider,\ncheckbox, and button above.\nPress ESC to exit.")

        ctx.end_window()

    # Properly end frame
    ctx.end()


def main():
    """Main function"""
    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        return 1

    try:
        print("Initializing renderer...")
        pymui.renderer_init()
        print("Creating context...")
        ctx = pymui.Context()
        print("Starting main loop - try interacting with the UI elements!")

        running = True
        while running:
            # Handle SDL events using direct polling (like C version)
            event = sdl2.SDL_Event()
            while sdl2.SDL_PollEvent(ctypes.byref(event)):
                if event.type == sdl2.SDL_QUIT:
                    print("Quit event received")
                    running = False
                elif event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    print("Escape key pressed")
                    running = False
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    ctx.input_mousemove(event.motion.x, event.motion.y)
                elif event.type == sdl2.SDL_MOUSEWHEEL:
                    ctx.input_scroll(0, event.wheel.y * -30)
                elif event.type == sdl2.SDL_TEXTINPUT:
                    # Handle text input properly
                    text_bytes = event.text.text
                    null_pos = text_bytes.find(b'\x00')
                    if null_pos >= 0:
                        text_bytes = text_bytes[:null_pos]
                    text = text_bytes.decode('utf-8', errors='replace')
                    ctx.input_text(text)
                elif event.type in (sdl2.SDL_MOUSEBUTTONDOWN, sdl2.SDL_MOUSEBUTTONUP):
                    btn = button_map.get(event.button.button)
                    if btn:
                        if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                            print(f"Mouse down at ({event.button.x}, {event.button.y})")
                            ctx.input_mousedown(event.button.x, event.button.y, btn)
                        else:
                            ctx.input_mouseup(event.button.x, event.button.y, btn)
                elif event.type in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP):
                    key = key_map.get(event.key.keysym.sym)
                    if key:
                        if event.type == sdl2.SDL_KEYDOWN:
                            ctx.input_keydown(key)
                        else:
                            ctx.input_keyup(key)

            # Process frame
            ctx.begin()
            test_window(ctx)
            ctx.end()

            # Render
            pymui.renderer_clear(pymui.color(64, 64, 64, 255))

            # Process commands
            ctx.reset_command_iterator()
            while True:
                cmd = ctx.next_command()
                if cmd is None:
                    break

                if cmd.type == pymui.Command.TEXT:
                    pymui.renderer_draw_text(cmd.text.encode('utf-8'), cmd.pos, cmd.color)
                elif cmd.type == pymui.Command.RECT:
                    pymui.renderer_draw_rect(cmd.rect, cmd.color)
                elif cmd.type == pymui.Command.ICON:
                    pymui.renderer_draw_icon(cmd.icon_id, cmd.rect, cmd.color)
                elif cmd.type == pymui.Command.CLIP:
                    pymui.renderer_set_clip_rect(cmd.rect)

            pymui.renderer_present()

        print("Test completed successfully!")

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