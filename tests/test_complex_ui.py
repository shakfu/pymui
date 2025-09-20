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


def main():
    """Test complex UI elements"""
    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        return 1

    try:
        print("Initializing renderer...")
        pymui.renderer_init()
        print("Creating context...")
        ctx = pymui.Context()
        print("Complex UI test - test buttons, sliders, checkboxes")
        print("Press Escape to exit")

        running = True
        click_count = 0
        slider_val = 50.0
        checkbox_state = False
        text_buf = ""

        while running:
            # Handle SDL events
            event = sdl2.SDL_Event()
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
                    btn = pymui.Mouse.LEFT if event.button.button == sdl2.SDL_BUTTON_LEFT else 0
                    if btn:
                        ctx.input_mousedown(event.button.x, event.button.y, btn)
                elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                    btn = pymui.Mouse.LEFT if event.button.button == sdl2.SDL_BUTTON_LEFT else 0
                    if btn:
                        ctx.input_mouseup(event.button.x, event.button.y, btn)
                elif event.type == sdl2.SDL_TEXTINPUT:
                    # Convert bytes to string properly
                    text_bytes = event.text.text
                    # Find null terminator
                    null_pos = text_bytes.find(b'\x00')
                    if null_pos >= 0:
                        text_bytes = text_bytes[:null_pos]
                    text = text_bytes.decode('utf-8', errors='replace')
                    ctx.input_text(text)

            # Process frame
            ctx.begin()

            # Complex UI test
            if ctx.begin_window("Complex UI Test", pymui.rect(50, 50, 400, 300)):
                ctx.layout_row([100, -1], 0)
                
                # Button test
                ctx.label("Button:")
                if ctx.button("Click Me!"):
                    click_count += 1
                    print(f"*** BUTTON CLICKED! Count: {click_count} ***")
                
                # Slider test
                ctx.label("Slider:")
                result, new_val = ctx.slider(slider_val, 0.0, 100.0)
                if result & pymui.Result.CHANGE:
                    print(f"Slider changed from {slider_val} to {new_val}")
                    slider_val = new_val
                
                # Checkbox test
                ctx.label("Checkbox:")
                result, new_state = ctx.checkbox("Test Check", checkbox_state)
                if result & pymui.Result.CHANGE:
                    print(f"Checkbox changed from {checkbox_state} to {new_state}")
                    checkbox_state = new_state
                
                # Textbox test
                ctx.label("Textbox:")
                result, text_buf = ctx.textbox_ex(text_buf, 128)
                if result & pymui.Result.SUBMIT:
                    print(f"Text submitted: '{text_buf}'")
                
                # Show current values
                ctx.label(f"Button clicks: {click_count}")
                ctx.label(f"Slider value: {slider_val:.2f}")
                ctx.label(f"Checkbox state: {checkbox_state}")
                ctx.label(f"Text: '{text_buf}'")
                
                ctx.end_window()

            ctx.end()

            # Render
            pymui.renderer_clear(pymui.color(32, 32, 32, 255))

            # Process commands
            ctx.reset_command_iterator()
            while True:
                cmd = ctx.next_command()
                if cmd is None:
                    break

                if cmd.type == pymui.Command.TEXT:
                    pymui.renderer_draw_text(cmd.text, cmd.pos, cmd.color)
                elif cmd.type == pymui.Command.RECT:
                    pymui.renderer_draw_rect(cmd.rect, cmd.color)
                elif cmd.type == pymui.Command.ICON:
                    pymui.renderer_draw_icon(cmd.icon_id, cmd.rect, cmd.color)
                elif cmd.type == pymui.Command.CLIP:
                    pymui.renderer_set_clip_rect(cmd.rect)

            pymui.renderer_present()

        print(f"Test completed. Button clicks: {click_count}")

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
