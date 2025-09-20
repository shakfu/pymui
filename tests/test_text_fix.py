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


def test_text_rendering(ctx):
    """Test window to verify text rendering fix"""
    # Properly initialize frame
    ctx.begin()

    if ctx.begin_window("Text Test", pymui.rect(100, 100, 300, 200)):
        ctx.layout_row([150, -1], 0)

        # Test various text elements
        ctx.label("Label text:")
        ctx.label("Should be clean")

        ctx.label("Button text:")
        if ctx.button("Button Text"):
            print("Button clicked - text should be clean")

        ctx.label("Tree text:")
        if ctx.begin_treenode("Tree Node"):
            ctx.label("Child text")
            ctx.end_treenode()

        # Test text with special characters
        ctx.label("Special chars:")
        ctx.text("Text with symbols: !@#$%")

        ctx.end_window()

    # Properly end frame
    ctx.end()


def main():
    """Main function to test text rendering"""
    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        return 1

    try:
        print("Testing text rendering fix...")
        pymui.renderer_init()
        ctx = pymui.Context()

        frame_count = 0
        max_frames = 120  # Run for ~2 seconds at 60fps

        while frame_count < max_frames:
            frame_count += 1

            # Handle SDL events
            event = sdl2.SDL_Event()
            while sdl2.SDL_PollEvent(ctypes.byref(event)):
                if event.type == sdl2.SDL_QUIT:
                    print("Quit event received")
                    return 0
                elif event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    print("Escape pressed")
                    return 0
                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    if event.button.button == sdl2.SDL_BUTTON_LEFT:
                        ctx.input_mousedown(event.button.x, event.button.y, pymui.Mouse.LEFT)
                elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                    if event.button.button == sdl2.SDL_BUTTON_LEFT:
                        ctx.input_mouseup(event.button.x, event.button.y, pymui.Mouse.LEFT)

            # Process frame
            ctx.begin()
            test_text_rendering(ctx)
            ctx.end()

            # Render and capture text commands for debugging
            pymui.renderer_clear(pymui.color(64, 64, 64, 255))

            # Process commands and check text
            ctx.reset_command_iterator()
            text_commands = 0
            while True:
                cmd = ctx.next_command()
                if cmd is None:
                    break

                if cmd.type == pymui.Command.TEXT:
                    text_commands += 1
                    # Check for garbage characters on first few frames
                    if frame_count <= 5:
                        text = cmd.text
                        if '@' in text or '[' in text or ']' in text:
                            print(f"WARNING: Found potential garbage in text: '{text}'")
                        elif frame_count == 1 and text_commands <= 3:
                            print(f"Clean text found: '{text}'")

                    pymui.renderer_draw_text(cmd.text.encode('utf-8'), cmd.pos, cmd.color)
                elif cmd.type == pymui.Command.RECT:
                    pymui.renderer_draw_rect(cmd.rect, cmd.color)
                elif cmd.type == pymui.Command.ICON:
                    pymui.renderer_draw_icon(cmd.icon_id, cmd.rect, cmd.color)
                elif cmd.type == pymui.Command.CLIP:
                    pymui.renderer_set_clip_rect(cmd.rect)

            pymui.renderer_present()

            # Report on first frame
            if frame_count == 1:
                print(f"Frame 1: {text_commands} text commands processed")

        print("Text rendering test completed - no issues detected!")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        sdl2.SDL_Quit()


if __name__ == "__main__":
    sys.exit(main())