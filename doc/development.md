# PyMUI Development Guide

## Quick Start

### Prerequisites

- Python 3.10 or higher
- `uv` package manager
- CMake 3.15 or higher
- SDL2 development libraries (for demos)
- C compiler (GCC, Clang, or MSVC)

### Setup Development Environment

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd pymui
   git submodule update --init --recursive
   ```

2. **Install dependencies:**
   ```bash
   uv sync --dev
   ```

3. **Build the project:**
   ```bash
   make build
   ```

4. **Run tests:**
   ```bash
   make test
   ```

5. **Run demo:**
   ```bash
   make demo
   ```

## Development Workflow

### Building and Testing

**Standard workflow:**
```bash
# Make changes to source code
make build              # Rebuild
make test              # Run tests
make demo              # Test demo
```

**Performance testing:**
```bash
make performance-test   # Run benchmarks
make memory-test       # Check for memory leaks
```

**Comprehensive testing:**
```bash
uv run pytest tests/   # All tests
uv run pytest tests/test_property_*.py  # Property-based tests
uv run pytest tests/test_memory_safety.py  # Memory safety tests
```

### Code Organization

```
pymui/
 src/pymui/          # Main package
    pymui.pyx      # Cython wrapper
    __init__.py    # Python package
 microui/           # Upstream C library
    microui.c
    microui.h
    sdl/          # SDL renderer
 tests/            # Test suite
    test_*.py     # Unit tests
    *demo*.py     # Demo applications
 scripts/          # Development scripts
    benchmark.py  # Performance testing
    memory_leak_test.py  # Memory testing
 doc/              # Documentation
 .github/          # CI/CD workflows
```

### Adding New Features

#### 1. Core Data Structures

**Example: Adding a new data type**

```python
# In pymui.pyx
cdef class NewType:
    """New data type for PyMUI."""

    cdef mu_new_type c_data

    def __init__(self, param1: int, param2: float):
        """Initialize new type."""
        self.c_data.param1 = param1
        self.c_data.param2 = param2

    @property
    def param1(self) -> int:
        """Get param1 value."""
        return self.c_data.param1

    @param1.setter
    def param1(self, value: int) -> None:
        """Set param1 value."""
        self.c_data.param1 = value
```

**Testing the new type:**
```python
# In tests/test_new_type.py
class TestNewType:
    def test_creation(self):
        obj = pymui.NewType(1, 2.0)
        assert obj.param1 == 1
        assert obj.param2 == 2.0

    def test_property_assignment(self):
        obj = pymui.NewType(1, 2.0)
        obj.param1 = 5
        assert obj.param1 == 5
```

#### 2. Widget Functions

**Example: Adding a new widget**

```python
# In pymui.pyx (Context class)
def new_widget(self, str label, int value, int opt=0) -> tuple:
    """
    Create a new widget.

    Args:
        label (str): Widget label
        value (int): Initial value
        opt (int, optional): Options flags

    Returns:
        tuple: (result_flags, new_value)
    """
    cdef bytes label_bytes = label.encode('utf-8')
    cdef char* label_cstr = label_bytes
    cdef int new_value = value

    cdef int result = mu_new_widget(&self.c_ctx, label_cstr, &new_value, opt)

    return result, new_value
```

**Testing the new widget:**
```python
# In tests/test_widgets.py
def test_new_widget(ctx):
    ctx.begin()
    result, value = ctx.new_widget("Test", 42)
    ctx.end()

    assert isinstance(result, int)
    assert isinstance(value, int)
```

#### 3. Property-Based Tests

**Adding property-based tests for new features:**

```python
# In tests/test_property_new.py
from hypothesis import given, strategies as st

@given(value=st.integers(min_value=0, max_value=1000),
       label=st.text(min_size=1, max_size=50))
def test_new_widget_properties(ctx, value, label):
    """Test new widget with various inputs."""
    assume(all(ord(c) < 65536 for c in label))  # Basic Unicode only

    ctx.begin()
    try:
        result, new_value = ctx.new_widget(label, value)
        assert isinstance(result, int)
        assert isinstance(new_value, int)
    except UnicodeEncodeError:
        pass  # Expected for some Unicode
    finally:
        ctx.end()
```

### Performance Optimization

#### Identifying Bottlenecks

**Use the benchmark script:**
```bash
python scripts/benchmark.py --save-baseline
# Make changes
python scripts/benchmark.py --compare
```

**Profile specific operations:**
```python
import cProfile
import pymui

def profile_operation():
    ctx = pymui.Context()
    for i in range(1000):
        ctx.begin()
        ctx.text(f"Text {i}")
        ctx.end()

cProfile.run('profile_operation()')
```

#### Common Optimization Patterns

**Minimize Python-C transitions:**
```python
# Slow: Multiple function calls
for i in range(1000):
    ctx.text(f"Item {i}")

# Better: Batch operations
text_items = [f"Item {i}" for i in range(1000)]
for text in text_items:
    ctx.text(text)
```

**Use appropriate data structures:**
```python
# Slow: Creating objects in loop
for i in range(1000):
    rect = pymui.Rect(i, i, 10, 10)

# Better: Reuse objects
rect = pymui.Rect(0, 0, 10, 10)
for i in range(1000):
    rect.x = i
    rect.y = i
```

### Memory Safety

#### Buffer Overflow Prevention

**Always validate buffer sizes:**
```python
def safe_textbox_operation(text: str, buffer_size: int):
    if buffer_size <= 0:
        raise ValueError("Buffer size must be positive")

    if buffer_size > 1024 * 1024:  # 1MB limit
        raise ValueError("Buffer size too large")

    textbox = pymui.Textbox(buffer_size)
    textbox.text = text  # Automatically truncated if needed
    return textbox.text
```

**Test boundary conditions:**
```python
def test_buffer_boundaries():
    tb = pymui.Textbox(16)

    # Test exact boundary
    tb.text = "A" * 15  # Leaves room for null terminator
    assert len(tb.text) <= 15

    # Test overflow
    tb.text = "B" * 100  # Much larger than buffer
    assert len(tb.text.encode('utf-8')) < 16
```

#### Memory Leak Detection

**Run memory tests regularly:**
```bash
make memory-test
```

**Add memory checks to new features:**
```python
def test_new_feature_memory_safety():
    """Test that new feature doesn't leak memory."""
    import gc
    import tracemalloc

    tracemalloc.start()
    baseline = tracemalloc.take_snapshot()

    # Perform operations
    for i in range(1000):
        # Your new feature operations
        pass

    gc.collect()
    current = tracemalloc.take_snapshot()
    top_stats = current.compare_to(baseline, 'lineno')

    # Check for significant growth
    growth = sum(stat.size_diff for stat in top_stats[:10])
    assert growth < 1024 * 1024  # Less than 1MB growth
```

### Error Handling

#### Graceful Error Recovery

**Handle encoding errors:**
```python
def safe_text_operation(ctx, text: str):
    try:
        ctx.text(text)
    except UnicodeEncodeError:
        # Fallback to safe representation
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        ctx.text(safe_text)
```

**Validate input parameters:**
```python
def validate_color_components(r, g, b, a=255):
    """Validate color component values."""
    for component, name in [(r, 'red'), (g, 'green'), (b, 'blue'), (a, 'alpha')]:
        if not isinstance(component, int):
            raise TypeError(f"{name} component must be an integer")
        if not 0 <= component <= 255:
            raise ValueError(f"{name} component must be in range 0-255")

    return pymui.Color(r, g, b, a)
```

### Documentation

#### Code Documentation

**Use comprehensive docstrings:**
```python
def complex_widget(self, data: list, options: dict) -> tuple:
    """
    Create a complex widget with multiple configuration options.

    This widget demonstrates advanced functionality including data binding,
    custom styling, and event handling.

    Args:
        data (list): List of data items to display. Each item should be
            a dictionary with 'label' and 'value' keys.
        options (dict): Configuration options:
            - 'style': Style configuration dictionary
            - 'selectable': Whether items can be selected (default: True)
            - 'multi_select': Allow multiple selection (default: False)

    Returns:
        tuple: (result_flags, selected_indices)
            - result_flags (int): Combination of MU_RES_* flags
            - selected_indices (list): List of selected item indices

    Raises:
        ValueError: If data format is invalid
        TypeError: If options contains invalid types

    Example:
        >>> data = [{'label': 'Item 1', 'value': 1}, {'label': 'Item 2', 'value': 2}]
        >>> options = {'style': {'color': pymui.Color(255, 0, 0)}}
        >>> result, selected = ctx.complex_widget(data, options)
    """
    # Implementation here...
```

#### Adding Examples

**Create focused examples:**
```python
# In examples/new_feature_example.py
#!/usr/bin/env python3
"""
Example demonstrating the new feature.

This example shows how to use the new feature in a practical context,
including proper setup, error handling, and cleanup.
"""

import sys
from pathlib import Path

# Add pymui to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pymui

def main():
    """Main example function."""
    ctx = pymui.Context()

    # Example usage
    ctx.begin()

    # Demonstrate new feature
    result = ctx.new_feature("example data")
    print(f"Result: {result}")

    ctx.end()

if __name__ == "__main__":
    main()
```

### CI/CD Integration

#### Adding New Tests to CI

**GitHub Actions workflow:**
```yaml
# In .github/workflows/test-new-feature.yml
name: Test New Feature

on:
  push:
    paths:
      - 'src/pymui/new_feature.py'
      - 'tests/test_new_feature.py'

jobs:
  test-new-feature:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run new feature tests
      run: |
        uv sync --dev
        uv run pytest tests/test_new_feature.py -v
```

#### Performance Regression Detection

**Add performance tests:**
```python
# In tests/test_performance.py
def benchmark_new_feature(self):
    """Benchmark new feature performance."""
    def operation():
        ctx = pymui.Context()
        ctx.begin()
        ctx.new_feature("test data")
        ctx.end()

    return self.benchmark(operation, iterations=1000)
```

### Debugging

#### Common Issues and Solutions

**Context assertion errors:**
```
Fatal error: assertion 'ctx->clip_stack.idx > 0' failed
```
**Solution:** Ensure proper begin/end pairing:
```python
ctx.begin()
try:
    # UI operations here
    pass
finally:
    ctx.end()
```

**Memory corruption:**
```
Segmentation fault
```
**Solution:** Check buffer sizes and string encoding:
```python
# Always validate string inputs
text = ensure_valid_utf8(user_input)
ctx.text(text)
```

**Build failures:**
```
Error: Cannot find microui.h
```
**Solution:** Update submodules:
```bash
git submodule update --init --recursive
```

#### Debugging Tools

**Use debug builds:**
```bash
export CFLAGS="-g -O0"
make build
```

**Memory debugging with Valgrind:**
```bash
valgrind --tool=memcheck --leak-check=full python demo.py
```

**Python debugging:**
```python
import pdb; pdb.set_trace()  # Set breakpoint
```

### Contributing Guidelines

#### Code Style

**Follow existing patterns:**
- Use Cython for performance-critical code
- Use Python for high-level interfaces
- Follow PEP 8 for Python code
- Use descriptive variable names
- Add comprehensive docstrings

**Testing requirements:**
- Unit tests for all new functionality
- Property-based tests for complex logic
- Memory safety tests for buffer operations
- Performance tests for critical paths

**Documentation requirements:**
- Update architecture.md for structural changes
- Add examples for new features
- Update CLAUDE.md for build/test changes
- Include inline documentation

#### Pull Request Process

1. **Create feature branch:**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement changes:**
   - Write code
   - Add tests
   - Update documentation

3. **Test thoroughly:**
   ```bash
   make test
   make memory-test
   make performance-test
   ```

4. **Submit pull request:**
   - Clear description
   - Link to relevant issues
   - Include test results

#### Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No memory leaks detected
- [ ] Performance impact assessed
- [ ] Documentation updated
- [ ] Examples provided
- [ ] Error handling comprehensive
- [ ] Security implications considered

## Troubleshooting

### Build Issues

**Common solutions:**
```bash
# Clean and rebuild
make clean
make build

# Update dependencies
uv sync --dev

# Check submodules
git submodule status
git submodule update --init --recursive
```

### Runtime Issues

**Check Python path:**
```python
import sys
print(sys.path)  # Ensure src/ is included
```

**Verify build artifacts:**
```bash
ls src/pymui/pymui.*.so  # Should exist after build
```

**Check SDL dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get install libsdl2-dev

# macOS
brew install sdl2

# Windows
# Install SDL2 development libraries
```

### Performance Issues

**Profile the code:**
```bash
python -m cProfile scripts/benchmark.py
```

**Check memory usage:**
```bash
python scripts/memory_leak_test.py --verbose
```

**Use smaller test cases:**
```python
# Reduce iterations for debugging
result = ctx.some_operation(iterations=10)  # Instead of 1000
```

This development guide provides the foundation for contributing to PyMUI while maintaining code quality, performance, and safety standards.