# PyMUI Architecture

PyMUI wraps [microui](https://github.com/rxi/microui), an immediate-mode UI
library in C, with Cython. It bundles microui's SDL2/OpenGL demo renderer and
adds a Python event loop on top.

## Layers

```text
application code          frame(ctx): windows, widgets, state
      |
pymui.app.App             SDL events -> ctx.input_*; one frame per loop, max_fps cap
      |
pymui.pymui (Cython)      Context, widgets, guards, render()
      |
microui.c                 layout, IDs, hover/focus, command list
microui/sdl/renderer.c    one SDL window, OpenGL 1.x quads, bitmap or TrueType text
```

| File | Role |
|-|-|
| `src/pymui/pymui.pyx` | Wrapper classes, guards, renderer bindings |
| `src/pymui/pymui.pxd` | C declarations for `microui.h` and `renderer.h` |
| `src/pymui/pymui.pyi` | Type stubs |
| `src/pymui/app.py` | `App`: window, event translation, main loop |
| `microui/microui.[ch]` | Vendored microui |
| `microui/sdl/renderer.[ch]` | Vendored demo renderer, extended with window management, UTF-8 decoding and TrueType text |
| `microui/sdl/stb_truetype.h` | stb_truetype v1.26 (public domain / MIT), commit `6e9f34d` |
| `examples/showcase.py` | Feature tour; `make showcase` |
| `examples/demo.py` | Port of microui's demo; `make demo` |

## Frame lifecycle

1. Input: `ctx.input_mousemove/mousedown/mouseup/scroll/keydown/keyup/text`.
   `poll_event()` translates SDL events into `Event` objects;
   `App.handle_event` maps those to these calls.
2. `ctx.begin()`, or `with ctx:`.
3. Widgets. Each call lays out, handles input, and appends draw commands.
4. `ctx.end()`. microui sorts windows by z-index and links their command
   segments with jump commands.
5. Render. `pymui.render(ctx, bg)` walks the command list in C and calls the
   `r_*` functions. `ctx.next_command()` yields Python command objects for
   custom renderers; `TextCommand` copies its string because the buffer is
   reused next frame.

Retained state between frames is microui's: container pool (window position,
size, scroll, open), tree-node pool (toggled headers), hover and focus IDs.
Widget values (slider value, checkbox state, text) live in the application and
are passed in and returned each frame.

## Widget IDs

microui keys hover and focus by a 32-bit FNV-1a hash of some bytes, seeded with
the top of its ID stack. Windows, panels and tree nodes push an ID; `id_scope`
pushes one explicitly.

| Widget | Default key |
|-|-|
| button, header, tree node | label (`button` with empty label: icon) |
| checkbox | label |
| slider, number, textbox | caller's code object, bytecode offset, and occurrence count in the current scope |
| any of the above | `key=` overrides |

microui itself hashes the *address* of the value for checkbox, slider and
number. The wrapper keeps those values in fixed per-`Context` fields, so the
address is constant and the pushed key alone separates widgets.

Every claimed ID is recorded per frame. A repeat raises `DuplicateIDError`.
Container IDs (windows, popups, panels) are tracked separately from control
IDs, since microui uses them only for container lookup.

## Guards

microui checks invariants with `abort()`, and some paths index an empty stack
(`items[idx - 1]`) without checking. The wrapper checks before each call that
can reach one:

- Frame and scope state: `_in_frame`, and a Python list of open scopes
  (`window`, `popup`, `panel`, `treenode`, `column`, `id`, `clip`). Every
  `end_*`/`pop_*` must match the innermost entry.
- Capacity: free slots in the ID (32), clip (32), layout (16) and container
  (32) stacks and the root list (32); a free pool slot (48 containers, 48
  tree nodes); and 2 KB plus the call's text in the 256 KB command buffer.
- Arguments: `fmt` strings for `sprintf`, color channels, buffer sizes,
  `layout_row` width count, icon IDs.

If an exception escapes a frame, `Context.__exit__` calls `abort_frame()`,
which resets the stacks and drops the frame's commands. `mu_end()` cannot be
used then: it aborts on non-empty stacks and patches root containers that
never finished.

Text input is buffered in Python because microui accepts 31 bytes per frame.
`begin()` moves as much as fits, cut on a UTF-8 boundary.

## Memory ownership

| Object | Owns | Notes |
|-|-|-|
| `Context` | `mu_Context` (malloc in `__cinit__`) | 270 KB, of which 256 KB is the command buffer |
| `Style`, `ContainerWrapper` | nothing | pointer into a `Context`, plus a reference that keeps it alive |
| `Textbox` | its text buffer | ID derives from the buffer address |
| `textbox_ex` | a per-call buffer | freed before return |
| `Vec2`, `Rect`, `Color`, commands | value copies | |

## Renderer

`renderer.c` holds one SDL window and GL context in static variables. All
renderer functions act on it, so a process has one window. `render()` and the
`renderer_draw_*` functions raise if no window exists.

Text is decoded as UTF-8; malformed sequences become U+FFFD. Two fonts:

| | Bitmap (default) | TrueType (`load_font`) |
|-|-|-|
| Source | `atlas.inl`, baked | any `.ttf`/`.otf`, rasterized by stb_truetype |
| Coverage | ASCII; other characters draw as a box | whatever the file covers; else its glyph 0 |
| Line height | 18 px | the requested pixel size |

Both share one 512x512 alpha texture: the baked atlas (icons, ASCII glyphs) in
the top-left 128x128, TrueType glyphs packed in rows below on first use. A
CPU copy is re-uploaded before the next draw after it changes. When the
texture or the 2048-slot glyph table fills, queued quads are flushed and the
glyph area is cleared and refilled.

The font is process-global and drives the text-measurement callbacks of every
`Context`, so layout follows it even without a window. stb_truetype trusts
font tables; `r_load_font` only checks that the table directory lies within
the data.

## Build

CMake builds `microui` and `microui_sdl` as static libraries; Cython generates
`pymui.c`, which links both into the `pymui.pymui` extension. scikit-build-core
drives CMake for `uv build` and `uv pip install -e .` (`make build`). Runtime
dependencies: SDL2 and OpenGL, linked; wheels link SDL2 statically.

## Tests

`make test` runs everything under `tests/`. Notable files:

| File | Covers |
|-|-|
| `test_widgets.py` | ID independence, context managers, custom-widget primitives |
| `test_safety.py` | each guard: duplicates, scope mismatch, capacity, input buffering |
| `test_app.py` | SDL event translation with synthetic events |
| `test_font.py` | font loading, rejection of bad data, UTF-8 measurement |
| `test_examples.py` | runs `showcase.py` and `demo.py` headless, each safety case |
| `test_property_based*.py` | Hypothesis tests of value types and widget inputs |
| `test_performance.py` | per-operation mean under 10 ms |

`scripts/memory_leak_test.py` and `scripts/valgrind_test.py` run in CI
(`.github/workflows/memory-leak-detection.yml`).

## Constraints

- One window per process (renderer state is global).
- One font at a time, process-wide; `TextCommand.font` is always `None`.
- No text shaping: no kerning, ligatures, combining marks or right-to-left.
- `mu_Real` is a C `float`: slider and number values carry about 7 significant
  digits.
- A `Context` is not safe for concurrent use from several threads.
