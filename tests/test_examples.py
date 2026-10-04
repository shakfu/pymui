"""Run the examples headless so they keep working as the API changes."""

import importlib.util
from pathlib import Path

import pytest

import pymui

EXAMPLES = Path(__file__).parent.parent / "examples"


def load(name):
    spec = importlib.util.spec_from_file_location(name, EXAMPLES / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_frames(app, n):
    for _ in range(n):
        with app.ctx:
            app.frame(app.ctx)
    assert not app.ctx.in_frame


@pytest.fixture(autouse=True)
def builtin_font():
    yield
    pymui.reset_font()


def test_demo_runs():
    app = load("demo").Demo()
    run_frames(app, 5)
    app.write_log("hello")
    run_frames(app, 2)


def test_showcase_runs():
    app = load("showcase").Showcase()
    app.show_extra = app.auto_toggle = True
    run_frames(app, 10)


EXPECTED = {
    "Duplicate ID": "DuplicateIDError",
    "Mismatched end": "RuntimeError",
    "Bad format": "ValueError",
    "Bad color": "ValueError",
    "Deep nesting": "RuntimeError",
    "Raise in tree node": "ValueError",
    "Widget outside window": "RuntimeError",
}


@pytest.mark.parametrize("case", list(EXPECTED))
def test_showcase_safety_case(case):
    app = load("showcase").Showcase()
    assert set(app.CASES) == set(EXPECTED)
    run_frames(app, 2)
    app.pending_case = case
    run_frames(app, 2)  # "outside window" runs one frame later
    assert app.log[-1].startswith(EXPECTED[case] + ":"), app.log
    run_frames(app, 2)  # the frame after an error is normal


def test_showcase_font_toggle():
    app = load("showcase").Showcase()
    if app.font_path is None:
        pytest.skip("no TrueType font found")
    app.use_font = True
    pymui.load_font(app.font_path, app.font_size)
    run_frames(app, 3)
    assert pymui.font_loaded()
