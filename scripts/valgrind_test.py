#!/usr/bin/env python3
"""Exercise pymui allocation paths under Valgrind.

Usage:
    uv run valgrind --tool=memcheck --leak-check=full python scripts/valgrind_test.py
"""

import pymui


def test_basic_operations():
    """Test basic pymui operations under Valgrind."""
    # Context lifecycle. Widget calls must sit inside a window: microui
    # asserts on an empty clip stack otherwise.
    for i in range(10):
        ctx = pymui.Context()
        ctx.begin()

        if ctx.begin_window(f"Window {i}", pymui.Rect(10, 10, 200, 150)):
            ctx.text(f"Text {i}")
            ctx.label(f"Label {i}")
            ctx.button(f"Button {i}")
            ctx.end_window()

        ctx.end()
        del ctx

    # Object creation
    for i in range(100):
        vec = pymui.Vec2(i, i + 1)
        rect = pymui.Rect(i, i + 1, i + 2, i + 3)
        color = pymui.Color(i % 256, (i + 1) % 256, (i + 2) % 256)
        del vec, rect, color

    # Textbox buffer allocation
    for i in range(50):
        tb = pymui.Textbox(64)
        tb.text = f"Test {i}"
        tb.text
        del tb


if __name__ == "__main__":
    test_basic_operations()
    print("Valgrind test completed")
