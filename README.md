# PyMUI

**A Python wrapper for the microui immediate-mode UI library**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#building)

PyMUI provides Python bindings for [microui](https://github.com/rxi/microui), a tiny (~1100 SLOC) portable immediate-mode UI library written in ANSI C. This wrapper allows you to create lightweight, responsive user interfaces in Python while maintaining the performance and simplicity of the original C library.

## Features

- 🐍 **Pythonic API** - Clean, intuitive Python interface
- ⚡ **High Performance** - Direct Cython bindings to C library
- 🎯 **Immediate Mode** - No retained widget objects, simple state management
- 🏗️ **Flexible Layout** - Dynamic row-based layout system
- 🎨 **Customizable** - Full control over styling and rendering
- 🔧 **Memory Safe** - Comprehensive bounds checking and error handling
- 📦 **Easy Integration** - Works with any rendering backend (SDL2, OpenGL, etc.)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/pymui.git
cd pymui

# Install with uv (recommended)
uv sync --dev
uv build

# Or with pip
pip install .
```

### Basic Usage

```python
import pymui

# Recommended: Use context managers for both frame and window management
with pymui.Context() as ctx:
    # Window context manager (automatically calls begin_window/end_window)
    with ctx.window("My Window", 10, 10, 200, 150) as window:
        if window.is_open:
            # Create a button
            if ctx.button("Click me!"):
                print("Button was clicked!")

            # Create a checkbox
            result, checked = ctx.checkbox("Enable feature", True)

            # Create a slider
            result, value = ctx.slider(50.0, 0.0, 100.0)

# Alternative: Manual window management
with pymui.Context() as ctx:
    if ctx.begin_window("Manual Window", pymui.Rect(10, 10, 200, 150)):
        # UI elements here...
        ctx.end_window()

# Legacy: Manual frame management
ctx = pymui.Context()
ctx.begin()
try:
    # UI code here...
    pass
finally:
    ctx.end()
```

## Core Concepts

### Immediate Mode UI

PyMUI follows the immediate-mode paradigm where UI elements are created and processed every frame:

```python
# No widget objects to manage - just call functions each frame
for frame in main_loop():
    with pymui.Context() as ctx:  # Automatic begin/end
        # UI is rebuilt each frame
        if ctx.button("Dynamic Button"):
            handle_click()

    render_frame(ctx)
```

### Context Manager vs Manual Frame Management

PyMUI supports both automatic and manual frame management:

```python
# 🎯 Recommended: Context Manager (Automatic)
with pymui.Context() as ctx:
    # begin() called automatically
    if ctx.button("Safe Button"):
        print("Clicked!")
    # end() called automatically, even on exceptions

# 🔧 Manual Management (Advanced)
ctx = pymui.Context()
ctx.begin()
try:
    if ctx.button("Manual Button"):
        print("Clicked!")
finally:
    ctx.end()  # Must always call end()
```

**Benefits of Context Manager:**
- **Automatic cleanup** - `end()` always called, even on exceptions
- **Cleaner code** - No need to remember begin/end pairs
- **Exception safety** - Proper cleanup guaranteed
- **Pythonic** - Follows Python's context manager idiom

### Context Manager Best Practices

```python
# ✅ Good: Use context manager for each frame
def render_frame():
    with pymui.Context() as ctx:
        # All UI code here
        if ctx.begin_window("Window", pymui.rect(10, 10, 200, 150)):
            ctx.label("Hello!")
            ctx.end_window()

# ✅ Good: Exception handling is automatic
def risky_ui_operation():
    with pymui.Context() as ctx:
        if ctx.begin_window("Risk", pymui.rect(10, 10, 200, 150)):
            if some_condition():
                raise ValueError("Something went wrong")
            ctx.label("This might not execute")
            ctx.end_window()
        # ctx.end() called automatically even if exception occurs

# ❌ Avoid: Manual management without proper exception handling
def bad_manual_approach():
    ctx = pymui.Context()
    ctx.begin()
    # If exception occurs here, end() won't be called!
    risky_operation()
    ctx.end()

# ✅ Better: Manual with proper exception handling
def good_manual_approach():
    ctx = pymui.Context()
    ctx.begin()
    try:
        risky_operation()
    finally:
        ctx.end()  # Always called
```

### Window Context Manager

PyMUI provides an additional context manager for windows that automatically handles `begin_window()` and `end_window()` calls:

```python
# 🎯 Recommended: Window context manager
with pymui.Context() as ctx:
    with ctx.window("My App", 10, 10, 300, 200) as window:
        if window.is_open:
            ctx.label("Content goes here")
            if ctx.button("Click me"):
                print("Button clicked!")
        # end_window() called automatically

# 🔧 Alternative: Manual window management
with pymui.Context() as ctx:
    if ctx.begin_window("Manual", pymui.Rect(10, 10, 300, 200)):
        ctx.label("Content goes here")
        ctx.end_window()  # Must remember to call this

# 🏗️ Multiple windows with context managers
with pymui.Context() as ctx:
    with ctx.window("Window 1", 10, 10, 200, 150) as w1:
        if w1.is_open:
            ctx.label(f"Window: {w1.title}")

    with ctx.window("Window 2", 220, 10, 200, 150) as w2:
        if w2.is_open:
            ctx.label(f"Size: {w2.rect.w}x{w2.rect.h}")
```

**Window Context Manager Benefits:**
- **Automatic cleanup** - `end_window()` always called
- **Exception safety** - Cleanup on errors
- **Window state access** - `window.is_open`, `window.title`, `window.rect`, `window.opt`
- **Cleaner code** - No manual begin/end window pairs
- **Convenient API** - `ctx.window(title, x, y, w, h, opt=0)`

### Layout System

PyMUI uses a flexible row-based layout system:

```python
with pymui.Context() as ctx:
    if ctx.begin_window("Layout Demo", pymui.Rect(10, 10, 300, 200)):
        # Two columns: 100px wide, remaining space
        ctx.layout_row([100, -1], 25)

        ctx.label("Name:")
        result, name = ctx.textbox("", 64)

        # Three equal columns
        ctx.layout_row([80, 80, 80], 25)

        if ctx.button("OK"):
            print("OK clicked")
        if ctx.button("Cancel"):
            print("Cancel clicked")
        if ctx.button("Help"):
            print("Help clicked")

        ctx.end_window()
```

### State Management

Since immediate-mode UIs rebuild every frame, you manage state in your application:

```python
class AppState:
    def __init__(self):
        self.counter = 0
        self.text = ""
        self.enabled = True

state = AppState()

def update_ui():
    with pymui.Context() as ctx:
        with ctx.window("Counter", 10, 10, 200, 100) as window:
            if window.is_open:
                ctx.label(f"Count: {state.counter}")

                if ctx.button("Increment"):
                    state.counter += 1

                result, state.enabled = ctx.checkbox("Enabled", state.enabled)
```

## Complete Example: Todo App

```python
#!/usr/bin/env python3
import pymui
import sdl2

class TodoApp:
    def __init__(self):
        self.todos = ["Learn PyMUI", "Build an app"]
        self.new_todo = ""
        self.ctx = pymui.Context()

    def add_todo(self):
        if self.new_todo.strip():
            self.todos.append(self.new_todo.strip())
            self.new_todo = ""

    def remove_todo(self, index):
        if 0 <= index < len(self.todos):
            del self.todos[index]

    def update(self):
        with self.ctx:  # Frame context manager
            with self.ctx.window("Todo App", 50, 50, 400, 300) as window:
                if window.is_open:
                    # Header
                    self.ctx.layout_row([-1], 25)
                    self.ctx.label("My Todo List")

                    # Todo list
                    for i, todo in enumerate(self.todos):
                        self.ctx.layout_row([-50, -1], 25)
                        self.ctx.label(todo)

                        self.ctx.push_id(f"del_{i}")
                        if self.ctx.button("Delete"):
                            self.remove_todo(i)
                        self.ctx.pop_id()

                    # Add new todo
                    self.ctx.layout_row([-80, -1], 25)
                    result, self.new_todo = self.ctx.textbox(self.new_todo, 128)

                    if self.ctx.button("Add") or (result & pymui.Result.SUBMIT):
                        self.add_todo()

# Run the app (with SDL2 renderer)
if __name__ == "__main__":
    app = TodoApp()
    # ... SDL2 setup and main loop ...
```

## Available Widgets

### Basic Controls

```python
# Text display
ctx.text("Hello World")
ctx.label("Label text")

# Buttons
if ctx.button("Click me"):
    print("Button pressed")

# Checkboxes
result, checked = ctx.checkbox("Enable feature", current_state)

# Sliders
result, value = ctx.slider(current_value, min_val, max_val)

# Text input
result, text = ctx.textbox(current_text, buffer_size)
```

### Layout Controls

```python
# Windows
if ctx.begin_window("Window Title", pymui.Rect(x, y, w, h)):
    # Window content here
    ctx.end_window()

# Tree nodes (collapsible sections)
if ctx.begin_treenode("Section"):
    # Collapsible content
    ctx.end_treenode()

# Headers
if ctx.header("Section Header"):
    # Header content

# Panels (scrollable areas)
ctx.begin_panel("Panel Name")
# Panel content
ctx.end_panel()
```

### Layout Functions

```python
# Set row layout: [col1_width, col2_width, ...], row_height
ctx.layout_row([100, -1, 50], 25)  # 100px, remaining, 50px

# Set individual dimensions
ctx.layout_width(200)
ctx.layout_height(30)

# Columns
ctx.layout_begin_column()
# Column content
ctx.layout_end_column()
```

## Data Types

### Core Types

```python
# 2D Vector
pos = pymui.Vec2(x=10, y=20)
print(f"Position: {pos.x}, {pos.y}")

# Rectangle
rect = pymui.Rect(x=10, y=20, w=100, h=50)

# Color (RGBA)
color = pymui.Color(r=255, g=128, b=0, a=255)  # Orange
color = pymui.Color(255, 128, 0)  # Alpha defaults to 255

# Convenience functions
pos = pymui.vec2(10, 20)
rect = pymui.rect(10, 20, 100, 50)
color = pymui.color(255, 128, 0, 255)
```

### Text Input

```python
# Simple textbox
textbox = pymui.Textbox(buffer_size=128)
textbox.text = "Initial text"
current_text = textbox.text

# In UI context
result, new_text = ctx.textbox_ex(current_text, buffer_size=128)
if result & pymui.Result.SUBMIT:
    print(f"User submitted: {new_text}")
```

## Styling

PyMUI supports comprehensive styling through the style system:

```python
# Get current style
style = ctx.style

# Modify colors
style.set_color(pymui.ColorIndex.BUTTON, pymui.Color(100, 150, 200))
style.set_color(pymui.ColorIndex.TEXT, pymui.Color(255, 255, 255))

# Available color indices
colors = [
    pymui.ColorIndex.TEXT,
    pymui.ColorIndex.BORDER,
    pymui.ColorIndex.WINDOWBG,
    pymui.ColorIndex.TITLEBG,
    pymui.ColorIndex.BUTTON,
    pymui.ColorIndex.BUTTONHOVER,
    # ... and more
]
```

## Building and Development

### Prerequisites

- Python 3.10 or higher
- CMake 3.15+
- C compiler (GCC, Clang, or MSVC)
- SDL2 development libraries (for demos)

### Building from Source

```bash
# Clone with submodules
git clone --recursive https://github.com/your-repo/pymui.git
cd pymui

# Install dependencies
uv sync --dev

# Build the project
make build

# Run tests
make test

# Run the demo
make demo
```

### Development Commands

```bash
# Build
make build

# Run tests (safe subset)
make test

# Run all tests (including potentially unstable ones)
make test-all

# Run only core safe tests
make test-safe

# Run memory leak detection
make memory-test

# Run performance benchmarks
make performance-test

# Clean build artifacts
make clean
```

### Project Structure

```
pymui/
├── src/pymui/          # Main Python package
│   ├── pymui.pyx      # Cython wrapper
│   └── __init__.py    # Package init
├── microui/           # Upstream C library (submodule)
├── tests/            # Test suite
├── scripts/          # Development tools
├── doc/              # Documentation
├── .github/          # CI/CD workflows
└── examples/         # Usage examples
```

## Testing

PyMUI includes a comprehensive test suite:

```bash
# Core functionality tests
uv run pytest tests/test_pymui.py

# Property-based testing (edge cases)
uv run pytest tests/test_property_minimal.py

# Memory safety tests
uv run pytest tests/test_memory_safety.py

# Performance benchmarks
python scripts/benchmark.py

# Memory leak detection
python scripts/memory_leak_test.py
```

## Performance

PyMUI is designed for high performance:

- **Zero-copy operations** where possible
- **Minimal Python overhead** through Cython
- **Memory-efficient** - no retained widget objects
- **Fast layout calculations** - immediate-mode processing

### Benchmarks

Typical performance on modern hardware:

- Context creation: ~0.1ms
- Basic widgets (10 buttons): ~0.05ms
- Complex UI (50 widgets): ~0.2ms
- Memory usage: <1MB for most applications

## Integration Examples

### With SDL2

```python
import sdl2
import pymui

def main():
    # SDL2 setup
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
    window = sdl2.SDL_CreateWindow(
        b"PyMUI Demo",
        sdl2.SDL_WINDOWPOS_CENTERED,
        sdl2.SDL_WINDOWPOS_CENTERED,
        800, 600,
        sdl2.SDL_WINDOW_SHOWN
    )

    ctx = pymui.Context()

    running = True
    while running:
        # Handle events
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event):
            if event.type == sdl2.SDL_QUIT:
                running = False
            # Pass events to PyMUI context

        # Update UI
        with ctx:  # Context manager handles begin/end
            if ctx.begin_window("Demo", pymui.Rect(10, 10, 200, 150)):
                if ctx.button("Quit"):
                    running = False
                ctx.end_window()

        # Render (implement your renderer)
        render_ui(ctx)

    sdl2.SDL_Quit()

if __name__ == "__main__":
    main()
```

### Custom Renderer

```python
class CustomRenderer:
    def render_frame(self, ctx):
        """Render a complete frame"""
        # Get render commands from context
        commands = ctx.get_render_commands()  # hypothetical API

        for cmd in commands:
            if cmd.type == "rect":
                self.draw_rect(cmd.rect, cmd.color)
            elif cmd.type == "text":
                self.draw_text(cmd.text, cmd.pos, cmd.color)

    def draw_rect(self, rect, color):
        # Implement rectangle drawing
        pass

    def draw_text(self, text, pos, color):
        # Implement text rendering
        pass
```

## Contributing

We welcome contributions! Here's how to get started:

### Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/your-username/pymui.git
cd pymui

# Set up development environment
uv sync --dev

# Install pre-commit hooks (optional)
pre-commit install
```

### Development Workflow

1. **Create a branch** for your feature/fix
2. **Write tests** for new functionality
3. **Run the test suite** to ensure nothing breaks
4. **Update documentation** if needed
5. **Submit a pull request**

### Code Style

- Follow existing code patterns in the codebase
- Use comprehensive docstrings for public APIs
- Add type hints where appropriate
- Write tests for new features
- Keep changes focused and atomic

### Testing Guidelines

```bash
# Run tests before submitting
make test

# For new features, add tests in appropriate files:
# - tests/test_pymui.py (basic functionality)
# - tests/test_memory_safety.py (memory safety)
# - tests/test_property_minimal.py (edge cases)

# Run memory leak detection for memory-related changes
make memory-test

# Run performance tests for performance-related changes
make performance-test
```

### Architecture Guidelines

- **Core API**: Keep the core API minimal and focused
- **Memory Safety**: All new features must include proper bounds checking
- **Performance**: Maintain the immediate-mode performance characteristics
- **Documentation**: Update architectural docs for significant changes

## API Reference

### Context Methods

#### Window Management
- `begin_window(title, rect, opt=0) -> int`
- `end_window()`
- `window(title, x, y, w, h, opt=0) -> Window` - **Context manager for automatic window management**
- `get_current_container() -> Container`

#### Window Context Manager
- `Window.title -> str` - Window title (read-only)
- `Window.rect -> Rect` - Window rectangle (read-only)
- `Window.opt -> int` - Window options (read-only)
- `Window.is_open -> bool` - Whether window is open and should be processed

#### Layout
- `layout_row(widths, height)`
- `layout_width(width)`
- `layout_height(height)`
- `layout_begin_column()`
- `layout_end_column()`
- `layout_next() -> Rect`

#### Widgets
- `button(label, icon=0, opt=0) -> int`
- `checkbox(label, state) -> tuple[int, int]`
- `slider(value, low, high, step=0, fmt="%.2f", opt=0) -> tuple[int, float]`
- `textbox_ex(buf, bufsz, opt=0) -> tuple[int, str]`
- `label(text)`
- `text(text)`

#### Tree/Panel
- `begin_treenode(label) -> int`
- `end_treenode()`
- `header(label, opt=0) -> int`
- `begin_panel(name)`
- `end_panel()`

#### State Management
- `push_id(id)`
- `pop_id()`

### Result Flags

```python
pymui.Result.NONE     # No interaction
pymui.Result.ACTIVE   # Widget is active
pymui.Result.SUBMIT   # Widget was submitted (Enter key, etc.)
pymui.Result.CHANGE   # Widget value changed
```

### Options

```python
pymui.Option.ALIGNCENTER   # Center-align content
pymui.Option.ALIGNRIGHT    # Right-align content
pymui.Option.NOINTERACT    # Disable interaction
pymui.Option.NOFRAME       # Don't draw frame
pymui.Option.NORESIZE      # Disable resizing
pymui.Option.NOSCROLL      # Disable scrolling
pymui.Option.NOCLOSE       # Disable close button
pymui.Option.NOTITLE       # Don't draw title
pymui.Option.HOLDFOCUS     # Hold focus
pymui.Option.AUTOSIZE      # Auto-size to content
pymui.Option.POPUP         # Popup window
pymui.Option.CLOSED        # Window is closed
pymui.Option.EXPANDED      # Header is expanded
```

## Troubleshooting

### Common Issues

**Import Error**: `ImportError: cannot import name 'pymui'`
```bash
# Make sure you've built the project
make build

# Check that build artifacts exist
ls src/pymui/pymui.*.so
```

**Segmentation Fault**: Usually caused by calling UI functions without proper context
```python
# ✅ Recommended: Use context manager
with pymui.Context() as ctx:
    # UI code here - begin/end handled automatically
    pass

# ✅ Alternative: Manual begin/end pairs
ctx = pymui.Context()
ctx.begin()
try:
    # UI code here
    pass
finally:
    ctx.end()
```

**Performance Issues**:
- Minimize string operations in tight loops
- Use `push_id`/`pop_id` for unique widget identification
- Consider caching expensive calculations outside the UI loop

### Getting Help

- Check the [documentation](doc/)
- Review [examples](examples/)
- Search [issues](https://github.com/your-repo/pymui/issues)
- Read the [microui usage guide](doc/usage.md)

## License

PyMUI is released under the MIT License. See [LICENSE](LICENSE) for details.

The underlying microui library is also MIT licensed.

## Acknowledgments

- [rxi](https://github.com/rxi) for creating the excellent microui library
- The Cython team for making Python-C integration seamless
- Contributors and testers who helped improve PyMUI

---

**Happy UI building with PyMUI! 🎨🐍**