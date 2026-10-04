"""Guards that turn microui aborts, out-of-bounds reads and silent ID clashes into exceptions."""

import pytest

import pymui
from pymui import DuplicateIDError, Mouse, Option, Rect

ABS = 0


def frame(ctx, ui, title="W", opt=0):
    with ctx:
        with ctx.window(title, 0, 0, 400, 300, opt) as win:
            if win.is_open:
                ui(ctx)


# --- default IDs follow the call site ------------------------------------


def test_conditional_widget_does_not_shift_later_ids():
    vals = {"a": 10.0, "b": 10.0}
    show_a = [False]

    def ui(ctx):
        if show_a[0]:
            ctx.layout_set_next(Rect(10, 200, 200, 20), ABS)
            _, vals["a"] = ctx.slider(vals["a"], 0, 100)
        ctx.layout_set_next(Rect(10, 10, 200, 20), ABS)
        _, vals["b"] = ctx.slider(vals["b"], 0, 100)

    ctx = pymui.Context()
    opt = Option.NOTITLE
    ctx.input_mousemove(100, 20)
    frame(ctx, ui, opt=opt)
    frame(ctx, ui, opt=opt)
    ctx.input_mousedown(100, 20, Mouse.LEFT)
    frame(ctx, ui, opt=opt)  # "b" focused
    show_a[0] = True  # a widget appears before "b" mid-drag
    ctx.input_mousemove(190, 20)
    frame(ctx, ui, opt=opt)
    assert vals["b"] > 80
    assert vals["a"] == 10.0


def test_same_call_site_in_loop_gets_distinct_ids():
    def ui(ctx):
        for _ in range(5):
            ctx.slider(1, 0, 2)
            ctx.textbox("")
            ctx.number(1, 1)

    frame(pymui.Context(), ui)  # would raise DuplicateIDError on a clash


# --- duplicate IDs --------------------------------------------------------


@pytest.mark.parametrize(
    "ui",
    [
        lambda c: (c.button("Same"), c.button("Same")),
        lambda c: (c.checkbox("Same", 0), c.checkbox("Same", 1)),
        lambda c: (c.header("Same"), c.header("Same")),
        lambda c: (c.button("Same"), c.header("Same")),
        lambda c: (c.slider(1, 0, 2, key="k"), c.slider(1, 0, 2, key="k")),
        lambda c: (c.textbox("", key="k"), c.number(1, 1, key="k")),
        lambda c: (c.button("", pymui.Icon.CHECK), c.button("", pymui.Icon.CHECK)),
    ],
)
def test_duplicate_widget_ids_raise(ui):
    with pytest.raises(DuplicateIDError):
        frame(pymui.Context(), ui)


def test_duplicate_textbox_object_raises():
    tb = pymui.Textbox(32)
    with pytest.raises(DuplicateIDError):
        frame(pymui.Context(), lambda c: (tb.update(c), tb.update(c)))


def test_duplicates_allowed_in_distinct_scopes():
    def ui(ctx):
        for i in range(3):
            with ctx.id_scope(i):
                ctx.button("Delete")
                ctx.checkbox("Done", 0)
        ctx.button("Delete", key="other")
        ctx.button("", pymui.Icon.CHECK)
        ctx.button("", pymui.Icon.CLOSE)
        ctx.button("Menu")
        with ctx.popup("Menu"):  # container and control IDs do not clash
            pass

    frame(pymui.Context(), ui)


def test_window_begun_twice_raises():
    ctx = pymui.Context()
    with pytest.raises(DuplicateIDError):
        with ctx:
            with ctx.window("W", 0, 0, 100, 100):
                pass
            with ctx.window("W", 0, 0, 100, 100):
                pass


def test_ids_reset_each_frame():
    ctx = pymui.Context()
    for _ in range(3):
        frame(ctx, lambda c: c.button("Once"))


# --- frame and scope pairing ---------------------------------------------


def test_begin_twice_and_end_without_begin():
    ctx = pymui.Context()
    with pytest.raises(RuntimeError):
        ctx.end()
    ctx.begin()
    with pytest.raises(RuntimeError):
        ctx.begin()
    ctx.end()
    assert not ctx.in_frame


@pytest.mark.parametrize(
    "ui",
    [
        lambda c: c.end_window(),
        lambda c: c.end_panel(),
        lambda c: c.end_popup(),
        lambda c: c.end_treenode(),
        lambda c: c.pop_id(),
        lambda c: c.pop_clip_rect(),
        lambda c: c.layout_end_column(),
        lambda c: (c.begin_treenode("t", Option.EXPANDED), c.end_panel()),
        lambda c: (c.push_id("x"), c.layout_begin_column(), c.pop_id()),
    ],
)
def test_mismatched_end_raises(ui):
    ctx = pymui.Context()
    with pytest.raises(RuntimeError, match="closing"):
        frame(ctx, ui)
    frame(ctx, lambda c: c.label("recovered"))


def test_end_with_open_scope_discards_frame():
    ctx = pymui.Context()
    ctx.begin()
    ctx.begin_window("W", Rect(0, 0, 100, 100))
    ctx.push_id("x")
    with pytest.raises(RuntimeError, match="window, id"):
        ctx.end()
    assert not ctx.in_frame
    assert ctx.next_command() is None
    frame(ctx, lambda c: c.label("ok"))
    assert ctx.next_command() is not None


def test_original_exception_survives_failed_close():
    ctx = pymui.Context()
    with pytest.raises(KeyError):
        with ctx:
            with ctx.window("W", 0, 0, 100, 100):
                with ctx.treenode("t", Option.EXPANDED):
                    ctx.push_id("left open")  # makes end_treenode mismatch
                    raise KeyError("original")


def test_commands_unavailable_during_frame():
    ctx = pymui.Context()
    ctx.begin()
    with pytest.raises(RuntimeError):
        ctx.next_command()
    ctx.end()


def test_window_requires_frame():
    with pytest.raises(RuntimeError):
        pymui.Context().begin_window("W", Rect(0, 0, 10, 10))


# --- capacity limits (each would abort in microui) -----------------------


def test_id_stack_overflow():
    def ui(ctx):
        for i in range(40):
            ctx.push_id(i)

    with pytest.raises(RuntimeError, match="ID stack full"):
        frame(pymui.Context(), ui)


def test_layout_stack_overflow():
    def ui(ctx):
        for _ in range(20):
            ctx.layout_begin_column()

    with pytest.raises(RuntimeError, match="layout stack full"):
        frame(pymui.Context(), ui)


def test_clip_stack_overflow():
    def ui(ctx):
        for _ in range(40):
            ctx.push_clip_rect(Rect(0, 0, 10, 10))

    with pytest.raises(RuntimeError, match="clip stack full"):
        frame(pymui.Context(), ui)


def test_too_many_windows():
    ctx = pymui.Context()
    with pytest.raises(RuntimeError, match="too many windows"):
        with ctx:
            for i in range(40):
                with ctx.window(f"W{i}", 0, 0, 10, 10):
                    pass


def test_container_pool_exhausted():
    def ui(ctx):
        ctx.layout_row([-1], 5)
        for i in range(60):
            with ctx.panel(f"p{i}"):
                pass

    with pytest.raises(RuntimeError, match="containers"):
        frame(pymui.Context(), ui)


def test_treenode_pool_exhausted():
    # The pool holds headers toggled away from their default; fill it by
    # clicking 48 collapsed headers open, then show one more.
    count = [48]

    def ui(ctx):
        for i in range(count[0]):
            ctx.layout_set_next(Rect(0, i * 6, 100, 6), ABS)
            ctx.header(f"h{i}")

    ctx = pymui.Context()
    opt = Option.NOTITLE | Option.NOSCROLL
    for i in range(48):
        y = i * 6 + 3
        ctx.input_mousemove(50, y)
        frame(ctx, ui, opt=opt)
        frame(ctx, ui, opt=opt)
        ctx.input_mousedown(50, y, Mouse.LEFT)
        frame(ctx, ui, opt=opt)
        ctx.input_mouseup(50, y, Mouse.LEFT)
    count[0] = 49
    with pytest.raises(RuntimeError, match="expanded"):
        frame(ctx, ui, opt=opt)


def test_command_buffer_full():
    line = "x" * 1000

    def ui(ctx):
        body = ctx.get_current_container().body
        for _ in range(1000):  # visible, so microui does not cull it
            ctx.draw_text(line, pymui.Vec2(body.x, body.y), pymui.Color())

    with pytest.raises(RuntimeError, match="command buffer full"):
        frame(pymui.Context(), ui)


def test_large_text_within_budget():
    frame(pymui.Context(), lambda c: c.text("x" * 100_000))


# --- other invalid input --------------------------------------------------


def test_panel_closed_option_rejected():
    with pytest.raises(ValueError):
        frame(pymui.Context(), lambda c: c.begin_panel("p", Option.CLOSED))


def test_draw_outside_window_raises():
    ctx = pymui.Context()
    with pytest.raises(RuntimeError):
        with ctx:
            ctx.draw_rect(Rect(0, 0, 1, 1), pymui.Color())


def test_draw_icon_range():
    with pytest.raises(ValueError):
        frame(pymui.Context(), lambda c: c.draw_icon(99, Rect(0, 0, 9, 9), pymui.Color()))


def test_unbound_objects_do_not_segfault():
    ctx = pymui.Context.__new__(pymui.Context)
    frame(ctx, lambda c: c.label("ok"))
    with pytest.raises(ValueError):
        pymui.Style.__new__(pymui.Style).padding


# --- text input buffering -------------------------------------------------


def typed(ctx, n_frames):
    out = [""]
    r = Rect(10, 10, 300, 20)

    def ui(c):
        c.layout_set_next(r, ABS)
        _, out[0] = c.textbox(out[0], 4096, key="t")

    ctx.input_mousemove(20, 20)
    frame(ctx, ui, opt=Option.NOTITLE)
    frame(ctx, ui, opt=Option.NOTITLE)
    ctx.input_mousedown(20, 20, Mouse.LEFT)
    frame(ctx, ui, opt=Option.NOTITLE)
    ctx.input_mouseup(20, 20, Mouse.LEFT)
    return out, ui


def test_long_text_input_spans_frames():
    ctx = pymui.Context()
    out, ui = typed(ctx, 0)
    text = "abcé中" * 20  # 160 bytes, mixed 1/2/3-byte characters
    for ch in text:
        ctx.input_text(ch)  # many SDL events within one frame
    for _ in range(10):
        frame(ctx, ui, opt=Option.NOTITLE)
    assert out[0] == text


def test_text_input_nul_truncates_and_cap():
    ctx = pymui.Context()
    ctx.input_text("ab\0cd")
    with pytest.raises(ValueError):
        ctx.input_text("x" * (64 * 1024 + 1))
