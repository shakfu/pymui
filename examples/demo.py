#!/usr/bin/env python3
"""Port of microui's SDL demo (microui/sdl/demo/main.c) to pymui.app.App."""

import sys

from pymui import ColorIndex, Option, Rect, Result, Vec2
from pymui.app import App

COLORS = [
    ("text:", ColorIndex.TEXT),
    ("border:", ColorIndex.BORDER),
    ("windowbg:", ColorIndex.WINDOWBG),
    ("titlebg:", ColorIndex.TITLEBG),
    ("titletext:", ColorIndex.TITLETEXT),
    ("panelbg:", ColorIndex.PANELBG),
    ("button:", ColorIndex.BUTTON),
    ("buttonhover:", ColorIndex.BUTTONHOVER),
    ("buttonfocus:", ColorIndex.BUTTONFOCUS),
    ("base:", ColorIndex.BASE),
    ("basehover:", ColorIndex.BASEHOVER),
    ("basefocus:", ColorIndex.BASEFOCUS),
    ("scrollbase:", ColorIndex.SCROLLBASE),
    ("scrollthumb:", ColorIndex.SCROLLTHUMB),
]


class Demo(App):
    def __init__(self):
        super().__init__("pymui demo", 800, 600)
        self.log: list[str] = []
        self.log_updated = False
        self.checks = [1, 0, 1]
        self.input = ""

    def write_log(self, text):
        self.log.append(text)
        del self.log[:-100]
        self.log_updated = True

    def frame(self, ctx):
        self.style_window(ctx)
        self.log_window(ctx)
        self.test_window(ctx)

    def test_window(self, ctx):
        with ctx.window("Demo Window", 40, 40, 300, 450) as w:
            if not w.is_open:
                return
            win = ctx.get_current_container()
            r = win.rect
            win.rect = Rect(r.x, r.y, max(r.w, 240), max(r.h, 300))

            if ctx.header("Window Info"):
                r = win.rect
                ctx.layout_row([54, -1], 0)
                ctx.label("Position:")
                ctx.label(f"{r.x}, {r.y}")
                ctx.label("Size:")
                ctx.label(f"{r.w}, {r.h}")

            if ctx.header("Test Buttons", Option.EXPANDED):
                ctx.layout_row([86, -110, -1], 0)
                ctx.label("Test buttons 1:")
                if ctx.button("Button 1"):
                    self.write_log("Pressed button 1")
                if ctx.button("Button 2"):
                    self.write_log("Pressed button 2")
                ctx.label("Test buttons 2:")
                if ctx.button("Button 3"):
                    self.write_log("Pressed button 3")
                if ctx.button("Popup"):
                    ctx.open_popup("Test Popup")
                with ctx.popup("Test Popup") as is_open:
                    if is_open:
                        ctx.button("Hello")
                        ctx.button("World")

            if ctx.header("Tree and Text", Option.EXPANDED):
                ctx.layout_row([140, -1], 0)
                with ctx.column():
                    with ctx.treenode("Test 1") as t1:
                        if t1:
                            with ctx.treenode("Test 1a") as t:
                                if t:
                                    ctx.label("Hello")
                                    ctx.label("world")
                            with ctx.treenode("Test 1b") as t:
                                if t:
                                    if ctx.button("Button 1"):
                                        self.write_log("Pressed button 1")
                                    if ctx.button("Button 2"):
                                        self.write_log("Pressed button 2")
                    with ctx.treenode("Test 2") as t:
                        if t:
                            ctx.layout_row([54, 54], 0)
                            for i in range(3, 7):
                                if ctx.button(f"Button {i}"):
                                    self.write_log(f"Pressed button {i}")
                    with ctx.treenode("Test 3") as t:
                        if t:
                            for i in range(3):
                                res, self.checks[i] = ctx.checkbox(
                                    f"Checkbox {i + 1}", self.checks[i]
                                )
                                if res & Result.CHANGE:
                                    self.write_log(
                                        f"Checkbox {i + 1} -> {self.checks[i]}"
                                    )
                with ctx.column():
                    ctx.layout_row([-1], 0)
                    ctx.text(
                        "Lorem ipsum dolor sit amet, consectetur adipiscing "
                        "elit. Maecenas lacinia, sem eu lacinia molestie, mi risus "
                        "faucibus ipsum, eu varius magna felis a nulla."
                    )

            if ctx.header("Background Color", Option.EXPANDED):
                bg = self.bg
                ctx.layout_row([-78, -1], 74)
                with ctx.column():
                    ctx.layout_row([46, -1], 0)
                    for name in ("r", "g", "b"):
                        ctx.label(f"{name.upper()}:")
                        _, v = ctx.slider(getattr(bg, name), 0, 255, key=name)
                        setattr(bg, name, int(v))
                r = ctx.layout_next()
                ctx.draw_rect(r, bg)
                ctx.draw_control_text(
                    f"#{bg.r:02X}{bg.g:02X}{bg.b:02X}",
                    r,
                    ColorIndex.TEXT,
                    Option.ALIGNCENTER,
                )

    def log_window(self, ctx):
        with ctx.window("Log Window", 350, 40, 300, 200) as w:
            if not w.is_open:
                return
            ctx.layout_row([-1], -25)
            with ctx.panel("Log Output") as panel:
                ctx.layout_row([-1], -1)
                ctx.text("\n".join(self.log))
            if self.log_updated:
                panel.scroll = Vec2(panel.scroll.x, panel.content_size.y)
                self.log_updated = False

            ctx.layout_row([-70, -1], 0)
            res, self.input = ctx.textbox(self.input, 128, key="log input")
            submitted = bool(res & Result.SUBMIT)
            if ctx.button("Submit"):
                submitted = True
            if submitted and self.input.strip():
                self.write_log(self.input.strip())
                self.input = ""

    def style_window(self, ctx):
        with ctx.window("Style Editor", 350, 250, 300, 240) as w:
            if not w.is_open:
                return
            sw = int(ctx.get_current_container().body.w * 0.14)
            ctx.layout_row([80, sw, sw, sw, sw, -1], 0)
            style = ctx.style
            for label, idx in COLORS:
                ctx.label(label)
                color = style.get_color(idx)
                with ctx.id_scope(idx):
                    for ch in ("r", "g", "b", "a"):
                        _, v = ctx.slider(
                            getattr(color, ch), 0, 255, 0, "%.0f", Option.ALIGNCENTER
                        )
                        setattr(color, ch, int(v))
                style.set_color(idx, color)
                ctx.draw_rect(ctx.layout_next(), color)


def main():
    Demo().run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
