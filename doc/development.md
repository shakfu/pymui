# PyMUI Development Guide

Structure and design are in [architecture.md](architecture.md).

## Prerequisites

- Python 3.10+ (`.python-version` pins 3.13 for local work)
- `uv`
- CMake 3.28+ and a C11 compiler
- SDL2 development headers and OpenGL (`libsdl2-dev` on Debian/Ubuntu,
  `brew install sdl2` on macOS)

CI builds on Ubuntu only. The CMake files look up the Homebrew prefix on
macOS; Windows is untested.

## Setup

```bash
git clone <repository-url>
cd pymui
uv sync --dev
make build
make test
make demo
```

microui is vendored under `microui/`; there are no submodules.

`make build` does an editable install. It does not rebuild on import, so run
it again after editing `.pyx`, `.pxd` or C sources.

## Make targets

| Target | Runs |
|-|-|
| `build` | `clean`, then `uv pip install -e .` |
| `test` | `pytest` over `tests/` |
| `demo` | `examples/demo.py` |
| `showcase` | `examples/showcase.py` |
| `lint` / `format` | `ruff check --fix src/` / `ruff format src/` |
| `typecheck` | `mypy src/` |
| `memory-test` | `scripts/memory_leak_test.py --verbose` |
| `performance-test` | `scripts/benchmark.py` |
| `clean` | removes `build/`, the built extension, caches |

## Adding a wrapper method

1. Declare the C function in `src/pymui/pymui.pxd`.
2. In `pymui.pyx`, guard before calling into microui (see
   [architecture.md#guards](architecture.md#guards)):
   - `_require_frame()`, `_require_layout()` or `_require_clip()` for the
     state the call needs.
   - `_reserve(ids, clips, layouts, containers, roots, cmd)` for what the call
     pushes at its peak. The arguments are positional: Cython rejects keyword
     arguments in these `cdef` calls.
   - `_claim(id, what)` for each control ID; `_claim_container` for containers.
   - `_open(tag)` after a successful begin, `_close(tag)` before the end.
   - Validate any value that reaches `sprintf` or a fixed-size buffer.
3. If microui derives the widget's ID from a pointer, pass a pointer to a
   `Context` field (as `_real_slot` does), never to a C local.
4. Update `pymui.pyi` and, for new module names, `__init__.py`.
5. Test behavior in `tests/test_widgets.py` and each guard in
   `tests/test_safety.py`.

## Writing tests

Tests run without a display: text measurement uses the baked font atlas, and
nothing renders unless a test creates a window.

Driving input:

- Place widgets with `ctx.layout_set_next(rect, 0)` (absolute coordinates) so
  click positions are known.
- Hover resolves one frame late. Move the mouse, run two frames, then press:
  see `Harness.click` in `tests/test_widgets.py`.
- `App.handle_event` takes synthetic `sdl2.SDL_Event` structs; see
  `tests/test_app.py`.

`tests/test_font.py` needs a TrueType font. It looks for DejaVu Sans
(`fonts-dejavu-core` on Debian/Ubuntu, installed in CI) and skips otherwise.
The font is global state: tests that load one restore the bitmap font.

Hypothesis tests live in `tests/test_property_based*.py`. Generate the domain
you want directly; heavy `.filter()` use trips Hypothesis's `filter_too_much`
health check intermittently.

## Memory checks

```bash
make memory-test                                   # RSS and tracemalloc growth per scenario
uv run python scripts/memory_leak_test.py --iterations 2000 --threshold 5.0
```

Valgrind, as CI runs it:

```bash
CFLAGS="-g -O0" make build                         # keep symbols for file:line
PYTHONMALLOC=malloc uv run valgrind --tool=memcheck --leak-check=full \
    --log-file=valgrind_output.log python scripts/valgrind_test.py
uv run python scripts/check_valgrind.py valgrind_output.log
```

`check_valgrind.py` counts only leak records with a frame in the pymui
extension; CPython's own static allocations are ignored.

AddressSanitizer, for the C code (renderer, font parsing), in a separate
environment so the instrumented build does not replace your editable one:

```bash
uv venv /tmp/asan-venv --python 3.13
CFLAGS="-fsanitize=address -fno-omit-frame-pointer -g -O1" LDFLAGS="-fsanitize=address" \
    uv pip install --python /tmp/asan-venv/bin/python . pytest hypothesis psutil
LD_PRELOAD=$(gcc -print-file-name=libasan.so) ASAN_OPTIONS=detect_leaks=0 \
    /tmp/asan-venv/bin/python -m pytest tests
```

## Benchmarks

```bash
uv run python scripts/benchmark.py --save-baseline   # writes performance_baseline.txt
uv run python scripts/benchmark.py --compare
```

`tests/test_performance.py` runs the same suite and fails if any benchmark
raises or averages over 10 ms.

## CI

`.github/workflows/memory-leak-detection.yml` runs on pushes and pull requests
to `main`, `master` and `develop`, and nightly:

- Python 3.10 to 3.13: build the wheel, install it, then run `pytest`,
  `memory_leak_test.py` and `benchmark.py` against the installed wheel.
  Steps use `uv run --no-sync`; a plain `uv run` would reinstall the editable
  project over the wheel.
- Valgrind job (nightly, manual, or a PR title containing `[valgrind]`): the
  commands above.

## Troubleshooting

| Symptom | Cause |
|-|-|
| `No module named 'pymui.pymui'` | extension not built; run `make build` |
| Change to `.pyx` has no effect | editable install does not rebuild; run `make build` |
| `Fatal error: ... assertion ... failed` from microui | a guard is missing; report it with the call that triggered it |
| `DuplicateIDError` | two widgets share a label or key in one scope; pass `key=` or use `ctx.id_scope()` |
| `RuntimeError: must be called inside a window or panel` | widget or draw call outside `ctx.window(...)` |
