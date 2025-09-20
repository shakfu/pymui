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
    """Test text input with focus handling"""
    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        return 1

    try:
        print("Initializing renderer...")
        pymui.renderer_init()
        print("Creating context...")
        ctx = pymui.Context()
        print("Text input focus test - click on textbox first, then type")
        print("Press Escape to exit")

        running = True
        text_buf = ""
        text_submissions = 0

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
                        print(f"Mouse click at ({event.button.x}, {event.button.y})")
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
                    print(f"Text input received: '{text}'")
                    ctx.input_text(text)
                elif event.type == sdl2.SDL_KEYDOWN:
                    # Handle special keys
                    if event.key.keysym.sym == sdl2.SDLK_RETURN:
                        print("Return key pressed")
                        ctx.input_keydown(pymui.Key.RETURN)
                    elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE:
                        print("Backspace key pressed")
                        ctx.input_keydown(pymui.Key.BACKSPACE)

            # Process frame
            ctx.begin()

            # Text input test with multiple textboxes
            if ctx.begin_window("Text Input Focus Test", pymui.rect(50, 50, 400, 300)):
                ctx.label("Click on a textbox first, then type:")
                
                # First textbox
                ctx.label("Textbox 1:")
                result, text_buf = ctx.textbox_ex(text_buf, 128)
                if result & pymui.Result.SUBMIT:
                    text_submissions += 1
                    print(f"*** TEXTBOX 1 SUBMITTED! Count: {text_submissions}, Text: '{text_buf}' ***")
                
                # Second textbox
                ctx.label("Textbox 2:")
                if not hasattr(main, 'text_buf2'):
                    main.text_buf2 = ""
                result, main.text_buf2 = ctx.textbox_ex(main.text_buf2, 128)
                if result & pymui.Result.SUBMIT:
                    text_submissions += 1
                    print(f"*** TEXTBOX 2 SUBMITTED! Count: {text_submissions}, Text: '{main.text_buf2}' ***")
                
                if ctx.button("Submit All"):
                    text_submissions += 1
                    print(f"*** SUBMIT BUTTON CLICKED! Count: {text_submissions} ***")
                    print(f"Textbox 1: '{text_buf}'")
                    print(f"Textbox 2: '{main.text_buf2}'")
                
                # Show current values
                ctx.label(f"Textbox 1: '{text_buf}'")
                ctx.label(f"Textbox 2: '{main.text_buf2}'")
                ctx.label(f"Submissions: {text_submissions}")
                
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

        print(f"Test completed. Text submissions: {text_submissions}")

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
