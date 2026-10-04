"""App event translation, driven by synthetic SDL events (no window needed)."""

import pytest
import sdl2

import pymui
from pymui import Key, Mouse
from pymui.app import App


def make_event(type_, **fields):
    ev = sdl2.SDL_Event()
    ev.type = type_
    for path, value in fields.items():
        obj = ev
        *parents, leaf = path.split("__")
        for p in parents:
            obj = getattr(obj, p)
        setattr(obj, leaf, value)
    return ev


def test_mouse_events():
    app = App()
    app.handle_event(make_event(sdl2.SDL_MOUSEMOTION, motion__x=12, motion__y=34))
    assert (app.ctx.mouse_pos.x, app.ctx.mouse_pos.y) == (12, 34)
    app.handle_event(
        make_event(
            sdl2.SDL_MOUSEBUTTONDOWN,
            button__button=sdl2.SDL_BUTTON_RIGHT,
            button__x=12,
            button__y=34,
        )
    )
    assert app.ctx.mouse_down == Mouse.RIGHT
    assert app.ctx.mouse_pressed == Mouse.RIGHT
    app.handle_event(
        make_event(
            sdl2.SDL_MOUSEBUTTONUP,
            button__button=sdl2.SDL_BUTTON_RIGHT,
            button__x=12,
            button__y=34,
        )
    )
    assert app.ctx.mouse_down == 0


def test_unmapped_button_ignored():
    app = App()
    app.handle_event(
        make_event(sdl2.SDL_MOUSEBUTTONDOWN, button__button=sdl2.SDL_BUTTON_X1)
    )
    assert app.ctx.mouse_down == 0


def test_key_events():
    app = App()
    app.handle_event(make_event(sdl2.SDL_KEYDOWN, key__keysym__sym=sdl2.SDLK_LSHIFT))
    app.handle_event(make_event(sdl2.SDL_KEYDOWN, key__keysym__sym=sdl2.SDLK_KP_ENTER))
    assert app.ctx.key_down == Key.SHIFT | Key.RETURN
    app.handle_event(make_event(sdl2.SDL_KEYUP, key__keysym__sym=sdl2.SDLK_LSHIFT))
    assert app.ctx.key_down == Key.RETURN
    app.handle_event(make_event(sdl2.SDL_KEYDOWN, key__keysym__sym=sdl2.SDLK_a))
    assert app.ctx.key_down == Key.RETURN


def test_text_input_reaches_focused_textbox():
    app = App()
    ctx = app.ctx
    text = [""]
    r = pymui.Rect(10, 10, 100, 20)

    def ui():
        with ctx:
            with ctx.window("W", 0, 0, 200, 100, pymui.Option.NOTITLE):
                ctx.layout_set_next(r, 0)
                _, text[0] = ctx.textbox(text[0], key="t")

    ctx.input_mousemove(20, 20)
    ui()
    ui()
    ctx.input_mousedown(20, 20, Mouse.LEFT)
    ui()
    ctx.input_mouseup(20, 20, Mouse.LEFT)
    ev = make_event(sdl2.SDL_TEXTINPUT)
    ev.text.text = "hé".encode()
    app.handle_event(ev)
    ui()
    assert text[0] == "hé"


def test_quit_and_resize():
    app = App(width=640, height=480)
    app.running = True
    app.handle_event(
        make_event(
            sdl2.SDL_WINDOWEVENT,
            window__event=sdl2.SDL_WINDOWEVENT_SIZE_CHANGED,
            window__data1=1024,
            window__data2=768,
        )
    )
    assert (app.width, app.height) == (1024, 768)
    app.handle_event(make_event(sdl2.SDL_QUIT))
    assert app.running is False


def test_default_bg_not_shared():
    a, b = App(), App()
    a.bg.r = 0
    assert b.bg.r == 90


class FakeClock:
    def __init__(self):
        self.now = 100.0
        self.slept = []

    def perf_counter(self):
        return self.now

    def sleep(self, dt):
        self.slept.append(round(dt, 6))
        self.now += dt


def test_frame_rate_cap(monkeypatch):
    import pymui.app

    clock = FakeClock()
    monkeypatch.setattr(pymui.app.time, "perf_counter", clock.perf_counter)
    monkeypatch.setattr(pymui.app.time, "sleep", clock.sleep)
    app = App(max_fps=100)  # 10 ms per frame
    app._limit_rate()  # first frame: schedule only
    assert clock.slept == []
    clock.now += 0.002  # fast frame: wait out the slot
    app._limit_rate()
    assert clock.slept == [0.008]
    clock.now += 0.004
    app._limit_rate()
    assert clock.slept == [0.008, 0.006]  # cadence kept, no drift
    clock.now += 0.050  # slow frame: no sleep, schedule restarts
    app._limit_rate()
    assert clock.slept == [0.008, 0.006]
    clock.now += 0.001
    app._limit_rate()
    assert clock.slept[-1] == 0.009


def test_frame_rate_cap_disabled_and_validated(monkeypatch):
    import pymui.app

    clock = FakeClock()
    monkeypatch.setattr(pymui.app.time, "perf_counter", clock.perf_counter)
    monkeypatch.setattr(pymui.app.time, "sleep", clock.sleep)
    app = App(max_fps=None)
    for _ in range(3):
        app._limit_rate()
    assert clock.slept == []
    for bad in (0, -5):
        with pytest.raises(ValueError):
            App(max_fps=bad)
        with pytest.raises(ValueError):
            app.max_fps = bad
