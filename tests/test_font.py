"""TrueType font loading and UTF-8 text measurement (headless)."""

from pathlib import Path

import pytest

import pymui
from pymui import Option, Rect

CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Debian/Ubuntu: fonts-dejavu-core
    "/usr/share/fonts/TTF/DejaVuSans.ttf",  # Arch
    "/Library/Fonts/Arial Unicode.ttf",  # macOS
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


@pytest.fixture
def font_path():
    for p in CANDIDATES:
        if Path(p).exists():
            return Path(p)
    pytest.skip("no TrueType font found; install fonts-dejavu-core")


@pytest.fixture(autouse=True)
def builtin_font():
    """The font is process-global; restore the built-in one for other tests."""
    pymui.reset_font()
    yield
    pymui.reset_font()


width = pymui.renderer_get_text_width


def test_builtin_font_draws_box_for_non_ascii():
    box = width("\x7f")
    assert box > 0
    assert width("é") == box
    assert width("中文") == 2 * box
    assert pymui.renderer_get_text_height() == 18


def test_load_font_changes_metrics(font_path):
    before = width("Hello")
    pymui.load_font(font_path, 16)
    assert pymui.font_loaded()
    assert width("Hello") != before
    assert width("é") > 0
    assert width("Αβγ") > 0  # Greek
    assert pymui.renderer_get_text_height() == 16
    pymui.reset_font()
    assert not pymui.font_loaded()
    assert width("Hello") == before


def test_load_font_from_bytes_and_str(font_path):
    pymui.load_font(font_path.read_bytes(), 20)
    a = width("Hello")
    pymui.load_font(str(font_path), 20)
    assert width("Hello") == a
    pymui.load_font(font_path, 10)
    assert width("Hello") < a


def test_length_counts_utf8_bytes(font_path):
    pymui.load_font(font_path, 16)
    assert width("Hello", 3) == width("Hel")
    # A cut multibyte sequence measures as U+FFFD, not as stray bytes.
    assert width("é", 1) == width("�")


@pytest.mark.parametrize(
    "make",
    [
        lambda d: b"",
        lambda d: b"\0" * 100,
        lambda d: d[:16],  # header only
        lambda d: d[:5000],  # tables point past the end
        lambda d: b"OTTO" + d[4:64],
    ],
)
def test_bad_font_data_rejected(font_path, make):
    pymui.load_font(font_path, 16)
    before = width("Hello")
    with pytest.raises(ValueError):
        pymui.load_font(make(font_path.read_bytes()))
    assert pymui.font_loaded()  # previous font kept
    assert width("Hello") == before


@pytest.mark.parametrize("size", [0, 5.9, 96.1, -1])
def test_font_size_range(font_path, size):
    with pytest.raises(ValueError):
        pymui.load_font(font_path, size)


def test_missing_file():
    with pytest.raises(OSError):
        pymui.load_font("/nonexistent/font.ttf")


def test_layout_uses_loaded_font(font_path):
    """microui measures through the renderer, so widths drive layout."""
    pymui.load_font(font_path, 24)
    ctx = pymui.Context()
    with ctx:
        with ctx.window("W", 0, 0, 400, 300, Option.NOTITLE):
            ctx.layout_row([-1], 0)
            ctx.text("one two three four five six seven eight nine ten")
    lines = 0
    while (cmd := ctx.next_command()) is not None:
        lines += cmd.type == pymui.Command.TEXT
    pymui.reset_font()
    with ctx:
        with ctx.window("W", 0, 0, 400, 300, Option.NOTITLE):
            ctx.layout_row([-1], 0)
            ctx.text("one two three four five six seven eight nine ten")
    builtin_lines = 0
    while (cmd := ctx.next_command()) is not None:
        builtin_lines += cmd.type == pymui.Command.TEXT
    assert lines > builtin_lines  # 24 px text wraps more


def test_truncated_utf8_in_textbox_is_safe(font_path):
    """Textbox truncation can split a character; measurement must cope."""
    pymui.load_font(font_path, 16)
    tb = pymui.Textbox(4)
    tb.text = "éé"  # 4 bytes into 3 usable: second char is cut
    with pymui.Context() as ctx:
        with ctx.window("W", 0, 0, 200, 100):
            ctx.layout_set_next(Rect(10, 10, 100, 20), 0)
            tb.update(ctx)


def test_draw_functions_require_window():
    for call in (
        lambda: pymui.renderer_draw_rect(Rect(0, 0, 1, 1), pymui.Color()),
        lambda: pymui.renderer_draw_text("x", pymui.Vec2(), pymui.Color()),
        lambda: pymui.renderer_clear(pymui.Color()),
        lambda: pymui.renderer_present(),
    ):
        pymui.renderer_shutdown()
        with pytest.raises(RuntimeError):
            call()
