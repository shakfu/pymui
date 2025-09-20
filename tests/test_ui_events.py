#!/usr/bin/env python3

import sys
import sdl2
import sdl2.ext
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
}

# Global test state
slider_val = 50.0
checkbox_state = False

def test_ui_window(ctx):
    """Test window with sliders and checkboxes"""
    global slider_val, checkbox_state

    # Properly initialize frame
    ctx.begin()

    if ctx.begin_window("UI Test", pymui.rect(50, 50, 300, 200)):
        ctx.layout_row([100, -1], 0)

        # Test slider
        ctx.label("Slider:")
        result, new_val = ctx.slider(slider_val, 0.0, 100.0)
        if result & pymui.Result.CHANGE:
            print(f"Slider changed from {slider_val} to {new_val}")
            slider_val = new_val

        # Test checkbox
        ctx.label("Checkbox:")
        result, new_state = ctx.checkbox("Test Check", checkbox_state)
        if result & pymui.Result.CHANGE:
            print(f"Checkbox changed from {checkbox_state} to {new_state}")
            checkbox_state = new_state

        # Test button for comparison
        if ctx.button("Test Button"):
            print("Button clicked!")

        # Show current values
        ctx.label(f"Slider value: {slider_val:.2f}")
        ctx.label(f"Checkbox state: {checkbox_state}")

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
        # Initialize renderer
        pymui.renderer_init()

        # Initialize microui context
        ctx = pymui.Context()

        print("Starting UI event test...")
        print("Try moving the slider, clicking the checkbox, and clicking the button")
        print("Press Escape or close window to exit")

        # Main loop
        running = True
        frame_count = 0

        while running:
            frame_count += 1

            # Handle SDL events
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                elif event.type == sdl2.SDLK_ESCAPE:
                    running = False
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    ctx.input_mousemove(event.motion.x, event.motion.y)
                elif event.type == sdl2.SDL_MOUSEWHEEL:
                    ctx.input_scroll(0, event.wheel.y * -30)
                elif event.type == sdl2.SDL_TEXTINPUT:
                    text = event.text.text.decode('utf-8', errors='replace')
                    ctx.input_text(text)
                elif event.type in (sdl2.SDL_MOUSEBUTTONDOWN, sdl2.SDL_MOUSEBUTTONUP):
                    btn = button_map.get(event.button.button)
                    if btn:
                        print(f"Mouse {'down' if event.type == sdl2.SDL_MOUSEBUTTONDOWN else 'up'} at ({event.button.x}, {event.button.y})")
                        if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
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
            test_ui_window(ctx)
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

        print("Test completed")

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