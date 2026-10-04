#!/usr/bin/env python3
"""Tour of the pymui API: widgets, IDs, scopes, custom widgets, guards, fonts.

Run: uv run python examples/showcase.py
"""

from __future__ import annotations

import math
import sys
import time
from contextlib import ExitStack
from pathlib import Path

import pymui
from pymui import Color, ColorIndex, Context, DuplicateIDError, Mouse, Option, Rect, Result
from pymui.app import App

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]
UNICODE_SAMPLE = "Grüße · Ελληνικά · Привет · 中文 (not in DejaVu: drawn as boxes)"
ACCENT = Color(90, 160, 230)


# --- custom widgets, built from update_control and draw_* primitives -------


def toggle(ctx: Context, label: str, on: bool) -> bool:
    """Switch with a sliding knob. Returns the new state."""
    wid = ctx.get_id(label)
    r = ctx.layout_next()
    ctx.update_control(wid, r)
    if ctx.mouse_pressed & Mouse.LEFT and ctx.focus == wid:
        on = not on
    track = Rect(r.x, r.y + 4, 34, r.h - 8)
    ctx.draw_control_frame(wid, track, ColorIndex.BASE)
    knob_x = track.x + track.w - track.h if on else track.x
    ctx.draw_rect(Rect(knob_x, track.y, track.h, track.h), ACCENT if on else ctx.style.get_color(ColorIndex.BUTTON))
    ctx.draw_control_text(label, Rect(r.x + 42, r.y, r.w - 42, r.h), ColorIndex.TEXT)
    return on


def drag_value(ctx: Context, key: str, value: float, lo: float, hi: float) -> float:
    """Horizontal drag bar: hold the left button and move the mouse."""
    wid = ctx.get_id(key)
    r = ctx.layout_next()
    ctx.update_control(wid, r)
    if ctx.focus == wid and ctx.mouse_down & Mouse.LEFT:
        value = pymui.clamp(value + ctx.mouse_delta.x * (hi - lo) / max(r.w, 1), lo, hi)
    ctx.draw_control_frame(wid, r, ColorIndex.BASE)
    fill = int(r.w * (value - lo) / (hi - lo))
    ctx.draw_rect(Rect(r.x, r.y, fill, r.h), Color(ACCENT.r, ACCENT.g, ACCENT.b, 110))
    ctx.draw_control_text(f"{key}: {value:.0f}", r, ColorIndex.TEXT, Option.ALIGNCENTER)
    return value


def progress(ctx: Context, fraction: float) -> None:
    r = ctx.layout_next()
    ctx.draw_rect(r, ctx.style.get_color(ColorIndex.BASE))
    ctx.draw_rect(Rect(r.x, r.y, int(r.w * fraction), r.h), ACCENT)
    ctx.draw_box(r, ctx.style.get_color(ColorIndex.BORDER))
    ctx.draw_control_text(f"{fraction:.0%}", r, ColorIndex.TEXT, Option.ALIGNCENTER)


def swatch(ctx: Context, color: Color) -> None:
    r = ctx.layout_next()
    ctx.draw_rect(r, color)
    ctx.draw_box(r, ctx.style.get_color(ColorIndex.BORDER))


def min_size(ctx: Context, w: int, h: int) -> None:
    """Keep the current window at least w x h. Assign whole Rects: fields are copies."""
    win = ctx.get_current_container()
    r = win.rect
    if r.w < w or r.h < h:
        win.rect = Rect(r.x, r.y, max(r.w, w), max(r.h, h))


# --- the application ---------------------------------------------------------


class Showcase(App):
    WINDOWS = ["Widgets", "Custom widgets", "Layout", "Safety", "Style and font", "Status"]

    def __init__(self) -> None:
        super().__init__("pymui showcase", 1180, 760)
        self.log: list[str] = []
        self.log_updated = False
        self.t0 = time.perf_counter()
        self.frames = 0
        self.fps = 0.0
        self.last_tick = self.t0
        # Widgets
        self.enabled = True
        self.volume = 40.0
        self.count = 3.0
        self.name = ""
        self.show_extra = False
        self.auto_toggle = False
        self.extra = 25.0
        self.stable = 50.0
        self.todos = [{"id": 1, "text": "Read the README", "done": True},
                      {"id": 2, "text": "Drag the lower slider", "done": False}]
        self.next_id = 3
        self.new_todo = ""
        # Custom widgets
        self.dark = True
        self.snap = False
        self.drag = 30.0
        self.mix = [Color(230, 90, 60), Color(60, 180, 120)]
        # Layout
        self.fruit = "none"
        self.columns = [0.5, 0.25]
        # Safety
        self.pending_case: str | None = None
        self.pending_outside = False
        # Style and font
        self.font_path = next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
        self.use_font = False
        self.font_size = 15.0
        self.default_style: dict[str, int] | None = None

    # -- helpers ---------------------------------------------------------------

    def write_log(self, text: str) -> None:
        self.log.append(text)
        del self.log[:-200]
        self.log_updated = True

    def tick(self) -> None:
        self.frames += 1
        now = time.perf_counter()
        dt, self.last_tick = now - self.last_tick, now
        if dt > 0:
            self.fps = 0.9 * self.fps + 0.1 / dt

    # -- frame -----------------------------------------------------------------

    def frame(self, ctx: Context) -> None:
        self.tick()
        if self.default_style is None:
            s = ctx.style
            self.default_style = {k: getattr(s, k) for k in ("padding", "spacing", "indent", "scrollbar_size")}
        self.widgets_window(ctx)
        self.custom_window(ctx)
        self.layout_window(ctx)
        self.safety_window(ctx)
        self.style_window(ctx)
        self.status_window(ctx)
        if self.pending_outside:  # runs between windows, where widgets are invalid
            self.pending_outside = False
            try:
                ctx.label("outside any window")
            except RuntimeError as e:
                self.write_log(f"RuntimeError: {e}")

    def widgets_window(self, ctx: Context) -> None:
        with ctx.window("Widgets", 10, 10, 370, 470) as win:
            if not win.is_open:
                return
            min_size(ctx, 300, 200)
            if ctx.header("Controls", Option.EXPANDED):
                ctx.layout_row([110, -1], 0)
                ctx.label("Button:")
                if ctx.button("Say hello"):
                    self.write_log(f"Hello, {self.name or 'stranger'}!")
                ctx.label("Checkbox:")
                _, self.enabled = ctx.checkbox("Enabled", self.enabled)
                ctx.label("Slider:")
                _, self.volume = ctx.slider(self.volume, 0, 100, 1, "%.0f%%", key="volume")
                ctx.label("Number:")
                _, self.count = ctx.number(self.count, 1, "%.0f", key="count")
                ctx.label("Name (Return):")
                res, self.name = ctx.textbox(self.name, 64, key="name")
                if res & Result.SUBMIT:
                    self.write_log(f"Name set to {self.name!r}")
            if ctx.header("Stable IDs", Option.EXPANDED):
                ctx.layout_row([-1], 0)
                _, self.show_extra = ctx.checkbox("Insert a slider above", self.show_extra)
                _, self.auto_toggle = ctx.checkbox("Toggle it every second", self.auto_toggle)
                if self.auto_toggle:
                    self.show_extra = int(time.perf_counter() - self.t0) % 2 == 0
                if self.show_extra:
                    _, self.extra = ctx.slider(self.extra, 0, 100)
                _, self.stable = ctx.slider(self.stable, 0, 100)
                ctx.text("Drag the last slider while the one above comes and goes. "
                         "Its default ID comes from its call site, so the drag holds.")
            if ctx.header("Todo list", Option.EXPANDED):
                for item in list(self.todos):
                    with ctx.id_scope(item["id"]):  # stable per item, not per row index
                        ctx.layout_row([24, -40, -1], 0)
                        _, item["done"] = ctx.checkbox("", item["done"])
                        ctx.label(("[done] " if item["done"] else "") + item["text"])
                        if ctx.button("x"):
                            self.todos.remove(item)
                ctx.layout_row([-60, -1], 0)
                res, self.new_todo = ctx.textbox(self.new_todo, 128, key="new todo")
                if (ctx.button("Add") or res & Result.SUBMIT) and self.new_todo.strip():
                    self.todos.append({"id": self.next_id, "text": self.new_todo.strip(), "done": False})
                    self.next_id += 1
                    self.new_todo = ""

    def custom_window(self, ctx: Context) -> None:
        with ctx.window("Custom widgets", 390, 10, 330, 300) as win:
            if not win.is_open:
                return
            ctx.layout_row([-1], 24)
            self.dark = toggle(ctx, "Dark backdrop", self.dark)
            self.snap = toggle(ctx, "Snap drag bar to tens", self.snap)
            self.drag = drag_value(ctx, "drag", self.drag, 0, 100)
            if self.snap and not ctx.mouse_down:
                self.drag = round(self.drag / 10) * 10
            ctx.layout_row([-1], 18)
            progress(ctx, (math.sin(time.perf_counter() - self.t0) + 1) / 2)
            ctx.layout_row([60, -1], 0)
            for i, c in enumerate(self.mix):
                with ctx.id_scope(("mix", i)):
                    with ctx.column():
                        ctx.layout_row([-1], 54)
                        swatch(ctx, c)
                    with ctx.column():
                        ctx.layout_row([20, -1], 0)
                        for ch in "rgb":
                            ctx.label(ch.upper())
                            _, v = ctx.slider(getattr(c, ch), 0, 255, 1, "%.0f")
                            setattr(c, ch, int(v))
            self.bg = Color(30, 32, 36) if self.dark else Color(150, 155, 160)

    def layout_window(self, ctx: Context) -> None:
        with ctx.window("Layout", 390, 320, 330, 430) as win:
            if not win.is_open:
                return
            ctx.layout_row([-1], 0)
            ctx.label("Row widths: 80 px, fill minus 60, rest")
            ctx.layout_row([80, -60, -1], 0)
            ctx.button("80 px")
            ctx.button("fill")
            ctx.button("rest")
            ctx.layout_row([-1], 0)
            ctx.label("Two columns:")
            ctx.layout_row([150, -1], 90)
            with ctx.column():
                ctx.layout_row([-1], 0)
                with ctx.treenode("Tree", Option.EXPANDED) as expanded:
                    if expanded:
                        with ctx.treenode("Leaf A") as a:
                            if a:
                                ctx.label("inside A")
                        with ctx.treenode("Leaf B") as b:
                            if b:
                                ctx.label("inside B")
            with ctx.column():
                ctx.layout_row([-1], 0)
                ctx.text("Columns nest a layout in one cell; each closes when its block ends.")
            ctx.layout_row([-1], 0)
            if ctx.button(f"Fruit: {self.fruit} (popup)"):
                ctx.open_popup("fruit menu")
            with ctx.popup("fruit menu") as is_open:
                if is_open:
                    for fruit in ("apple", "pear", "plum"):
                        if ctx.button(fruit):
                            self.fruit = fruit
                            win_popup = ctx.get_current_container()
                            win_popup.open = False
            ctx.layout_row([-1], -1)
            with ctx.panel("Log") as panel:
                ctx.layout_row([-1], 0)
                ctx.text("\n".join(self.log) or "(log is empty)")
            if self.log_updated:
                panel.scroll = pymui.Vec2(panel.scroll.x, panel.content_size.y)
                self.log_updated = False

    CASES = {
        "Duplicate ID": "two buttons labelled 'Twin'",
        "Mismatched end": "end_panel() with a window open",
        "Bad format": "slider fmt='%s', which reaches sprintf",
        "Bad color": "Color(300, 0, 0)",
        "Deep nesting": "40 nested id_scope() blocks (max 32)",
        "Raise in tree node": "exception inside `with ctx.treenode`",
        "Widget outside window": "label() between windows",
    }

    def run_case(self, ctx: Context, name: str) -> None:
        """Trigger one guarded error inside this window and log what was raised."""
        if name == "Widget outside window":
            self.pending_outside = True
            return
        try:
            if name == "Duplicate ID":
                ctx.button("Twin")
                ctx.button("Twin")
            elif name == "Mismatched end":
                ctx.end_panel()
            elif name == "Bad format":
                ctx.slider(1, 0, 2, fmt="%s", key="bad fmt")
            elif name == "Bad color":
                Color(300, 0, 0)
            elif name == "Deep nesting":
                with ExitStack() as scopes:  # unwinds the scopes that did open
                    for i in range(40):
                        scopes.enter_context(ctx.id_scope(i))
            elif name == "Raise in tree node":
                with ctx.treenode("Raises", Option.EXPANDED):
                    raise ValueError("raised inside a tree node; it was still closed")
        except (DuplicateIDError, RuntimeError, ValueError) as e:
            self.write_log(f"{type(e).__name__}: {e}")
        else:
            self.write_log(f"{name}: nothing raised")

    def safety_window(self, ctx: Context) -> None:
        with ctx.window("Safety", 730, 10, 440, 300) as win:
            if not win.is_open:
                return
            ctx.layout_row([-1], 0)
            ctx.text("microui calls abort() on misuse. pymui raises first; "
                     "each button triggers one case and logs the exception.")
            ctx.layout_row([170, -1], 0)
            for name, what in self.CASES.items():
                if ctx.button(name):
                    self.pending_case = name
                ctx.label(what)
            if self.pending_case is not None:
                name, self.pending_case = self.pending_case, None
                ctx.layout_row([-1], 0)
                self.run_case(ctx, name)

    def style_window(self, ctx: Context) -> None:
        with ctx.window("Style and font", 730, 320, 440, 270) as win:
            if not win.is_open:
                return
            style = ctx.style
            ctx.layout_row([110, -1], 0)
            for prop, hi in (("padding", 12), ("spacing", 12), ("indent", 40), ("scrollbar_size", 24)):
                ctx.label(prop)
                _, v = ctx.slider(getattr(style, prop), 0, hi, 1, "%.0f", key=prop)
                setattr(style, prop, int(v))
            ctx.layout_row([110, 70, 70, 70, -1], 0)
            ctx.label("button color")
            c = style.get_color(ColorIndex.BUTTON)
            for ch in "rgb":
                _, v = ctx.slider(getattr(c, ch), 0, 255, 1, "%.0f", key=("button", ch))
                setattr(c, ch, int(v))
            style.set_color(ColorIndex.BUTTON, c)
            if ctx.button("Reset"):
                for k, v in (self.default_style or {}).items():
                    setattr(style, k, v)
                style.set_color(ColorIndex.BUTTON, Color(75, 75, 75))
            ctx.layout_row([150, -1], 0)
            if self.font_path is None:
                ctx.label("No TrueType font found.")
                return
            res, use = ctx.checkbox("TrueType font", self.use_font)
            _, size = ctx.number(self.font_size, 0.5, "%.0f px", key="font size")
            size = pymui.clamp(round(size), 10, 20)
            old_size = self.font_size
            self.use_font, self.font_size = use, size
            if res & Result.CHANGE or (use and size != old_size):
                if use:
                    pymui.load_font(self.font_path, size)
                else:
                    pymui.reset_font()
                self.write_log(f"font: {Path(self.font_path).name if use else 'built-in'} {size:.0f} px")
            ctx.layout_row([-1], 0)
            ctx.text(UNICODE_SAMPLE)
            ctx.label(f"sample width: {pymui.renderer_get_text_width(UNICODE_SAMPLE)} px")

    def status_window(self, ctx: Context) -> None:
        with ctx.window("Status", 10, 485, 370, 270) as win:
            if not win.is_open:
                return
            ctx.layout_row([110, -1], 0)
            for k, v in (
                ("fps", f"{self.fps:.0f}"),
                ("frame", self.frames),
                ("window", f"{self.width} x {self.height}"),
                ("mouse", f"{ctx.mouse_pos.x}, {ctx.mouse_pos.y}"),
                ("hover / focus", f"{ctx.hover:08x} / {ctx.focus:08x}"),
                ("font", "TrueType" if pymui.font_loaded() else "built-in"),
            ):
                ctx.label(k)
                ctx.label(str(v))
            ctx.layout_row([-1], 0)
            if ctx.button("Reopen closed windows"):
                for name in self.WINDOWS:
                    ctx.get_container(name).open = True
            ctx.layout_row([170, -1], 0)
            for name in self.WINDOWS[:-1]:
                if ctx.button(f"Raise {name}"):
                    ctx.bring_to_front(ctx.get_container(name))


def main() -> int:
    Showcase().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
