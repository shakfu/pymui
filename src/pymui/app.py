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

import time
from typing import Callable

from .pymui import (
    Color,
    Context,
    Event,
    EventType,
    poll_event,
    render,
    renderer_init_window,
    renderer_resize,
    renderer_shutdown,
)

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

    def handle_event(self, event: Event) -> None:
        """Forward one event to the context."""
        ctx = self.ctx
        t = event.type
        if t == EventType.QUIT:
            self.quit()
        elif t == EventType.MOUSEMOTION:
            ctx.input_mousemove(event.x, event.y)
        elif t == EventType.MOUSEWHEEL:
            ctx.input_scroll(0, event.y * -SCROLL_STEP)
        elif t == EventType.TEXT:
            ctx.input_text(event.text)
        elif t == EventType.MOUSEDOWN and event.button:
            ctx.input_mousedown(event.x, event.y, event.button)
        elif t == EventType.MOUSEUP and event.button:
            ctx.input_mouseup(event.x, event.y, event.button)
        elif t == EventType.KEYDOWN and event.key:
            ctx.input_keydown(event.key)
        elif t == EventType.KEYUP and event.key:
            ctx.input_keyup(event.key)
        elif t == EventType.RESIZE:
            self.width, self.height = event.x, event.y
            renderer_resize(self.width, self.height)

    def step(self, frame: Callable[[Context], None]) -> None:
        """Drain pending events, build one frame, and render it."""
        while (event := poll_event()) is not None:
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
        renderer_init_window(self.title, self.width, self.height, self.resizable)
        try:
            self.running = True
            while self.running:
                self.step(frame)
        finally:
            self.running = False
            renderer_shutdown()
