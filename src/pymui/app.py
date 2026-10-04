"""SDL2 window and event loop for pymui.

`App` owns the window, translates SDL events into microui input, runs one
UI frame per iteration, and renders with the bundled OpenGL renderer.

    from pymui.app import App

    def frame(ctx):
        with ctx.window("Hello", 10, 10, 200, 100) as win:
            if win.is_open and ctx.button("Quit"):
                app.quit()

    app = App("demo")
    app.run(frame)
"""

from __future__ import annotations

import ctypes
import time
from typing import Callable

import sdl2  # type: ignore[import-untyped]

from .pymui import (
    Color,
    Context,
    Key,
    Mouse,
    render,
    renderer_init_window,
    renderer_resize,
    renderer_shutdown,
)

BUTTONS = {
    sdl2.SDL_BUTTON_LEFT: Mouse.LEFT,
    sdl2.SDL_BUTTON_RIGHT: Mouse.RIGHT,
    sdl2.SDL_BUTTON_MIDDLE: Mouse.MIDDLE,
}

KEYS = {
    sdl2.SDLK_LSHIFT: Key.SHIFT,
    sdl2.SDLK_RSHIFT: Key.SHIFT,
    sdl2.SDLK_LCTRL: Key.CTRL,
    sdl2.SDLK_RCTRL: Key.CTRL,
    sdl2.SDLK_LALT: Key.ALT,
    sdl2.SDLK_RALT: Key.ALT,
    sdl2.SDLK_RETURN: Key.RETURN,
    sdl2.SDLK_KP_ENTER: Key.RETURN,
    sdl2.SDLK_BACKSPACE: Key.BACKSPACE,
}

# Pixels scrolled per wheel notch; matches the microui C demo.
SCROLL_STEP = 30


class App:
    """Run `frame(ctx)` once per frame in an SDL window.

    Override `frame` in a subclass, or pass a callable to `run`.

    Args:
        title: Window title.
        width, height: Initial window size in pixels.
        bg: Clear color. Mutable: assign `app.bg` to change it.
        resizable: Allow the user to resize the window.
        max_fps: Frame-rate cap, or None for none. The renderer requests
            vsync, but drivers and compositors may ignore it; without a cap
            the loop would then redraw as fast as the CPU allows.
    """

    def __init__(
        self,
        title: str = "pymui",
        width: int = 800,
        height: int = 600,
        *,
        bg: Color | None = None,
        resizable: bool = True,
        max_fps: float | None = 120,
    ) -> None:
        self.title = title
        self.width = width
        self.height = height
        self.resizable = resizable
        self.bg = bg if bg is not None else Color(90, 95, 100)
        self.ctx = Context()
        self.running = False
        self.max_fps = max_fps
        self._next_frame = 0.0

    @property
    def max_fps(self) -> float | None:
        return self._max_fps

    @max_fps.setter
    def max_fps(self, value: float | None) -> None:
        if value is not None and not value > 0:
            raise ValueError("max_fps must be positive or None")
        self._max_fps = value

    def frame(self, ctx: Context) -> None:
        """Build one frame of UI. Called between ctx.begin() and ctx.end()."""
        raise NotImplementedError("override frame() or pass a callable to run()")

    def quit(self) -> None:
        """Stop the loop after the current frame."""
        self.running = False

    def handle_event(self, event: sdl2.SDL_Event) -> None:
        """Forward one SDL event to the context."""
        ctx = self.ctx
        t = event.type
        if t == sdl2.SDL_QUIT:
            self.quit()
        elif t == sdl2.SDL_MOUSEMOTION:
            ctx.input_mousemove(event.motion.x, event.motion.y)
        elif t == sdl2.SDL_MOUSEWHEEL:
            ctx.input_scroll(0, event.wheel.y * -SCROLL_STEP)
        elif t == sdl2.SDL_TEXTINPUT:
            text = event.text.text.split(b"\0", 1)[0]
            ctx.input_text(text.decode("utf-8", errors="replace"))
        elif t in (sdl2.SDL_MOUSEBUTTONDOWN, sdl2.SDL_MOUSEBUTTONUP):
            btn = BUTTONS.get(event.button.button)
            if btn:
                x, y = event.button.x, event.button.y
                if t == sdl2.SDL_MOUSEBUTTONDOWN:
                    ctx.input_mousedown(x, y, btn)
                else:
                    ctx.input_mouseup(x, y, btn)
        elif t in (sdl2.SDL_KEYDOWN, sdl2.SDL_KEYUP):
            key = KEYS.get(event.key.keysym.sym)
            if key:
                if t == sdl2.SDL_KEYDOWN:
                    ctx.input_keydown(key)
                else:
                    ctx.input_keyup(key)
        elif (
            t == sdl2.SDL_WINDOWEVENT
            and event.window.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED
        ):
            self.width, self.height = event.window.data1, event.window.data2
            renderer_resize(self.width, self.height)

    def step(self, frame: Callable[[Context], None]) -> None:
        """Drain pending events, build one frame, and render it."""
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)):
            self.handle_event(event)
        with self.ctx:
            frame(self.ctx)
        render(self.ctx, self.bg)
        self._limit_rate()

    def _limit_rate(self) -> None:
        """Sleep until the next frame slot. A late frame resets the schedule
        instead of being followed by a burst of catch-up frames."""
        if self._max_fps is None:
            return
        interval = 1.0 / self._max_fps
        now = time.perf_counter()
        if now < self._next_frame:
            time.sleep(self._next_frame - now)
            self._next_frame += interval
        else:
            self._next_frame = now + interval

    def run(self, frame: Callable[[Context], None] | None = None) -> None:
        """Open the window and loop until `quit()` or the window closes.

        Raises:
            RuntimeError: If SDL or the window cannot be initialized.
        """
        frame = frame if frame is not None else self.frame
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            raise RuntimeError(f"SDL_Init failed: {sdl2.SDL_GetError().decode()}")
        try:
            renderer_init_window(self.title, self.width, self.height, self.resizable)
            try:
                self.running = True
                while self.running:
                    self.step(frame)
            finally:
                renderer_shutdown()
        finally:
            self.running = False
            sdl2.SDL_Quit()
