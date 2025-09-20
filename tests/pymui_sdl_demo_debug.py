#!/usr/bin/env python3

import sys
from pathlib import Path
import ctypes
import sdl2
import sdl2.ext

ROOTDIR = Path(__file__).parent.parent / "src"

try:
    from pymui import pymui
except ImportError:
    # Handle imports when running in development
    sys.path.insert(0, str(ROOTDIR))
    from pymui import pymui


# Global state
logbuf = []
logbuf_updated = False
bg = [90.0, 95.0, 100.0]  # Background color RGB


def write_log(text):
    """Add text to the log buffer"""
    global logbuf_updated
    logbuf.append(text)
    if len(logbuf) > 100:  # Keep log manageable
        logbuf.pop(0)
    logbuf_updated = True
    print(f"LOG: {text}")  # Debug output


def test_window(ctx):
    """Create the main demo window"""
    global bg

    # Demo Window
    if ctx.begin_window("Demo Window", pymui.rect(40, 40, 300, 450)):
        win = ctx.get_current_container()
        if win:
            # Ensure minimum window size
            if win.rect.w < 240:
                win.rect.w = 240
            if win.rect.h < 300:
                win.rect.h = 300

        # Window Info section
        if ctx.header("Window Info"):
            win = ctx.get_current_container()
            if win:
                ctx.layout_row([54, -1], 0)
                ctx.label("Position:")
                ctx.label(f"{win.rect.x}, {win.rect.y}")
                ctx.label("Size:")
                ctx.label(f"{win.rect.w}, {win.rect.h}")

        # Test Buttons section
        if ctx.header("Test Buttons", pymui.Option.EXPANDED):
            ctx.layout_row([86, -110, -1], 0)
            ctx.label("Test buttons 1:")
            if ctx.button("Button 1"):
                write_log("Pressed button 1")
            if ctx.button("Button 2"):
                write_log("Pressed button 2")
            ctx.label("Test buttons 2:")
            if ctx.button("Button 3"):
                write_log("Pressed button 3")
            if ctx.button("Popup"):
                ctx.open_popup("Test Popup")
            if ctx.begin_popup("Test Popup"):
                ctx.button("Hello")
                ctx.button("World")
                ctx.end_popup()

        # Tree and Text section
        if ctx.header("Tree and Text", pymui.Option.EXPANDED):
            ctx.layout_row([140, -1], 0)
            ctx.layout_begin_column()

            if ctx.begin_treenode("Test 1"):
                if ctx.begin_treenode("Test 1a"):
                    ctx.label("Hello")
                    ctx.label("world")
                    ctx.end_treenode()
                if ctx.begin_treenode("Test 1b"):
                    if ctx.button("Button 1"):
                        write_log("Pressed button 1")
                    if ctx.button("Button 2"):
                        write_log("Pressed button 2")
                    ctx.end_treenode()
                ctx.end_treenode()

            if ctx.begin_treenode("Test 2"):
                ctx.layout_row([54, 54], 0)
                if ctx.button("Button 3"):
                    write_log("Pressed button 3")
                if ctx.button("Button 4"):
                    write_log("Pressed button 4")
                if ctx.button("Button 5"):
                    write_log("Pressed button 5")
                if ctx.button("Button 6"):
                    write_log("Pressed button 6")
                ctx.end_treenode()

            if ctx.begin_treenode("Test 3"):
                # Note: checkbox returns (result, new_state)
                result, checks_0 = ctx.checkbox("Checkbox 1", getattr(test_window, 'checks_0', True))
                test_window.checks_0 = checks_0
                result, checks_1 = ctx.checkbox("Checkbox 2", getattr(test_window, 'checks_1', False))
                test_window.checks_1 = checks_1
                result, checks_2 = ctx.checkbox("Checkbox 3", getattr(test_window, 'checks_2', True))
                test_window.checks_2 = checks_2
                ctx.end_treenode()

            ctx.layout_end_column()

            ctx.layout_begin_column()
            ctx.layout_row([-1], 0)
            ctx.text("Lorem ipsum dolor sit amet, consectetur adipiscing "
                    "elit. Maecenas lacinia, sem eu lacinia molestie, mi risus faucibus "
                    "ipsum, eu varius magna felis a nulla.")
            ctx.layout_end_column()

        # Background Color section
        if ctx.header("Background Color", pymui.Option.EXPANDED):
            ctx.layout_row([-78, -1], 74)

            # Sliders column
            ctx.layout_begin_column()
            ctx.layout_row([46, -1], 0)

            ctx.label("Red:")
            result, bg[0] = ctx.slider(bg[0], 0, 255)
            if result & pymui.Result.CHANGE:
                write_log(f"Red slider changed to {bg[0]}")
            ctx.label("Green:")
            result, bg[1] = ctx.slider(bg[1], 0, 255)
            if result & pymui.Result.CHANGE:
                write_log(f"Green slider changed to {bg[1]}")
            ctx.label("Blue:")
            result, bg[2] = ctx.slider(bg[2], 0, 255)
            if result & pymui.Result.CHANGE:
                write_log(f"Blue slider changed to {bg[2]}")

            ctx.layout_end_column()

            # Color preview
            r = ctx.layout_next()
            ctx.draw_rect(r, pymui.color(int(bg[0]), int(bg[1]), int(bg[2]), 255))
            hex_color = f"#{int(bg[0]):02X}{int(bg[1]):02X}{int(bg[2]):02X}"
            # Note: draw_control_text would need to be exposed in the wrapper
            # For now we'll skip this

        ctx.end_window()


def log_window(ctx):
    """Create the log window"""
    global logbuf_updated

    if ctx.begin_window("Log Window", pymui.rect(350, 40, 300, 200)):
        # Output text panel
        ctx.layout_row([-1], -25)
        ctx.begin_panel("Log Output")
        panel = ctx.get_current_container()
        ctx.layout_row([-1], -1)
        log_text = "\n".join(logbuf) if logbuf else ""
        ctx.text(log_text)
        ctx.end_panel()

        if logbuf_updated and panel:
            panel.scroll.y = panel.content_size.y
            logbuf_updated = False

        # Input textbox + submit button
        ctx.layout_row([-70, -1], 0)

        # Initialize textbox if not exists
        if not hasattr(log_window, 'textbox'):
            log_window.textbox = pymui.Textbox(128)

        # Update textbox
        result, new_text = log_window.textbox.update(ctx)
        submitted = bool(result & pymui.Result.SUBMIT)

        if ctx.button("Submit"):
            submitted = True

        if submitted:
            if log_window.textbox.text.strip():
                write_log(log_window.textbox.text.strip())
                log_window.textbox.text = ""  # Clear the textbox

        ctx.end_window()


def process_frame(ctx):
    """Process one frame of UI"""
    ctx.begin()
    log_window(ctx)
    test_window(ctx)
    ctx.end()


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


def main():
    """Main function"""
    global bg

    # Initialize SDL
    if sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING) != 0:
        print(f"SDL_Init Error: {sdl2.SDL_GetError()}")
        return 1

    try:
        # Initialize renderer
        pymui.renderer_init()

        # Initialize microui context
        ctx = pymui.Context()

        print("Starting debug demo...")
        print("Try clicking buttons, moving sliders, and typing in the textbox")
        print("Press Escape to exit")

        # Main loop
        running = True
        while running:
            # Handle SDL events - use direct SDL_PollEvent like C version
            event = sdl2.SDL_Event()
            while sdl2.SDL_PollEvent(ctypes.byref(event)):
                if event.type == sdl2.SDL_QUIT:
                    running = False
                elif event.type == sdl2.SDL_KEYDOWN and event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                    running = False
                elif event.type == sdl2.SDL_MOUSEMOTION:
                    ctx.input_mousemove(event.motion.x, event.motion.y)
                elif event.type == sdl2.SDL_MOUSEWHEEL:
                    ctx.input_scroll(0, event.wheel.y * -30)
                elif event.type == sdl2.SDL_TEXTINPUT:
                    # Convert bytes to string properly
                    text_bytes = event.text.text
                    # Find null terminator
                    null_pos = text_bytes.find(b'\x00')
                    if null_pos >= 0:
                        text_bytes = text_bytes[:null_pos]
                    text = text_bytes.decode('utf-8', errors='replace')
                    ctx.input_text(text)
                elif event.type in (sdl2.SDL_MOUSEBUTTONDOWN, sdl2.SDL_MOUSEBUTTONUP):
                    btn = button_map.get(event.button.button)
                    if btn:
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
            process_frame(ctx)

            # Render
            pymui.renderer_clear(pymui.color(int(bg[0]), int(bg[1]), int(bg[2]), 255))

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

    finally:
        sdl2.SDL_Quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
