# PyMUI Architecture Documentation

## Overview

PyMUI is a Cython-based Python wrapper for the [microui](https://github.com/rxi/microui) immediate-mode UI library. This document describes the overall architecture, design decisions, and key components of the PyMUI project.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Memory Management](#memory-management)
5. [Build System](#build-system)
6. [Testing Architecture](#testing-architecture)
7. [Performance Considerations](#performance-considerations)
8. [Security Model](#security-model)
9. [Extension Points](#extension-points)

## System Architecture

### High-Level Overview

```
        
   Python App           Demo/Tests           Scripts       
                                                           
  - User Code          - SDL Demo           - Benchmarks   
  - UI Logic           - Test Suite         - Memory Test  
        
                                                       
         
                                 
                    
                       PyMUI Cython  
                       Wrapper       
                                     
                      - pymui.pyx    
                      - __init__.py  
                    
                                 
                    
                       microui C     
                       Library       
                                     
                      - microui.c    
                      - microui.h    
                    
                                 
                    
                       Platform      
                       Renderer      
                                     
                      - SDL2         
                      - OpenGL       
                    
```

### Layer Responsibilities

**Python Application Layer:**
- User interface logic
- Event handling
- Application-specific state management
- Widget composition and layout

**PyMUI Wrapper Layer:**
- Python-C interoperability
- Memory safety guarantees
- Python-friendly API design
- Error handling and validation

**microui Core Layer:**
- Immediate-mode UI operations
- Widget rendering logic
- Layout calculations
- Event processing

**Platform Layer:**
- Window management
- Graphics rendering
- Input handling
- Resource management

## Core Components

### 1. Context Management (`pymui.Context`)

The Context class is the central coordinator for all UI operations:

```python
class Context:
    """Main microui context for UI operations."""

    def begin(self) -> None:
        """Begin a new frame."""

    def end(self) -> None:
        """End the current frame."""

    # Widget methods...
```

**Key Responsibilities:**
- Frame lifecycle management
- Widget state tracking
- Layout system coordination
- Memory pool management

**Design Patterns:**
- RAII pattern for frame management
- Command pattern for widget operations
- State pattern for UI state tracking

### 2. Data Structures

#### Vec2 - 2D Vector
```python
class Vec2:
    """2D integer vector for positions and dimensions."""
    def __init__(self, x: int, y: int) -> None: ...

    x: int  # X coordinate
    y: int  # Y coordinate
```

#### Rect - Rectangle
```python
class Rect:
    """Rectangle with position and dimensions."""
    def __init__(self, x: int, y: int, w: int, h: int) -> None: ...

    x: int  # X position
    y: int  # Y position
    w: int  # Width
    h: int  # Height
```

#### Color - RGBA Color
```python
class Color:
    """RGBA color representation."""
    def __init__(self, r: int, g: int, b: int, a: int = 255) -> None: ...

    r: int  # Red (0-255)
    g: int  # Green (0-255)
    b: int  # Blue (0-255)
    a: int  # Alpha (0-255)
```

#### Textbox - Text Input
```python
class Textbox:
    """Text input widget with buffer management."""
    def __init__(self, size: int) -> None: ...

    text: str  # Current text content
```

### 3. Widget System

The widget system follows immediate-mode principles:

**Immediate Mode Characteristics:**
- No retained widget objects
- Stateless widget functions
- Direct rendering each frame
- Event handling integrated with rendering

**Widget Categories:**
- **Display Widgets:** `text()`, `label()`
- **Input Widgets:** `button()`, `checkbox()`, `slider()`
- **Text Widgets:** `textbox_ex()`
- **Layout Widgets:** `layout_row()`, `layout_width()`, `layout_height()`
- **Container Widgets:** `begin_window()`, `end_window()`

## Data Flow

### Frame Processing Cycle

```
1. ctx.begin()
    Initialize frame state
    Reset widget counters
    Clear previous frame data

2. Widget Operations
    Layout calculations
    Event processing
    State updates
    Rendering commands

3. ctx.end()
    Finalize layout
    Process events
    Prepare render data

4. Renderer (External)
    Process render commands
    Draw to screen
    Present frame
```

### Event Flow

```
Input Events → Platform Layer → microui → PyMUI → Python App
                                   ↓
Widget State ← Widget Functions ← Layout System
```

### Memory Flow

```
Python Objects → Cython Wrapper → C Structures → microui
       ↓                              ↓
 Garbage Collection            Stack/Static Memory
```

## Memory Management

### Memory Safety Strategy

**Buffer Management:**
- Fixed-size buffers for text inputs
- Automatic truncation on overflow
- UTF-8 encoding validation
- Null termination guarantees

**Object Lifecycle:**
- Python garbage collection for wrapper objects
- RAII pattern for resource management
- Explicit cleanup in destructors
- Stack allocation for temporary data

**Memory Leak Prevention:**
- Comprehensive test suite
- Automated leak detection in CI
- Property-based testing
- Static analysis integration

### Memory Layout

```
Python Heap:        Cython Objects (Vec2, Rect, Color, etc.)
                           
                           
C Stack:           microui context structures
                           
                           
C Static:          Font atlas, style data
```

## Build System

### Hybrid Build Architecture

The project uses a sophisticated hybrid build system:

```
CMake (C/C++ Build)
 microui compilation
 SDL renderer compilation
 Cython code generation

Python Build (scikit-build-core)
 Cython compilation
 Extension module linking
 Package distribution
```

### Build Dependencies

**Core Dependencies:**
- `scikit-build-core`: Modern Python build backend
- `cython`: Python-C interoperability
- `cmake`: C/C++ build system
- `ninja`: Fast parallel builds

**Runtime Dependencies:**
- `pysdl2`: SDL2 Python bindings
- `python>=3.10`: Minimum Python version

### Build Targets

```bash
make build         # Full build
make test          # Run test suite
make demo          # Run SDL demo
make memory-test   # Memory leak detection
make performance-test # Performance benchmarks
make clean         # Clean artifacts
```

## Testing Architecture

### Test Categories

**Unit Tests (`test_pymui.py`):**
- Core functionality validation
- API contract testing
- Error condition handling
- Basic integration tests

**Property-Based Tests (`test_property_*.py`):**
- Edge case discovery
- Invariant verification
- Fuzz testing
- Memory safety validation

**Performance Tests (`test_performance.py`):**
- Benchmark suite
- Regression detection
- Memory usage monitoring
- Throughput analysis

**Memory Safety Tests (`test_memory_safety.py`):**
- Leak detection
- Buffer overflow protection
- Unicode safety
- Resource cleanup

### Test Infrastructure

**Fixtures:**
- Shared context instances
- Common test data
- Setup/teardown automation

**Utilities:**
- Memory monitoring
- Performance measurement
- Error injection
- Mock objects

## Performance Considerations

### Optimization Strategies

**Memory Efficiency:**
- Stack allocation for temporary objects
- Object pooling for frequent allocations
- Lazy initialization of expensive resources
- Compact data structures

**CPU Efficiency:**
- Minimal Python-C transitions
- Batch operations where possible
- Cache-friendly data layouts
- SIMD-friendly algorithms (where applicable)

**I/O Efficiency:**
- Buffered text operations
- Efficient string encoding
- Minimal system calls
- Asynchronous where appropriate

### Performance Monitoring

**Benchmarking:**
- Automated performance tests
- Regression detection
- Memory usage tracking
- Throughput measurement

**Profiling:**
- CPU profiling integration
- Memory profiling tools
- Call graph analysis
- Hot path identification

## Security Model

### Input Validation

**Buffer Overflow Protection:**
- Size validation for all inputs
- Automatic truncation of oversized data
- Null termination guarantees
- UTF-8 validation

**String Safety:**
- Unicode normalization
- Encoding validation
- Length limit enforcement
- Character set filtering

### Memory Safety

**Bounds Checking:**
- Array access validation
- Pointer arithmetic safety
- Stack overflow protection
- Heap corruption detection

**Resource Management:**
- Automatic cleanup
- Reference counting
- Leak detection
- Resource limits

### Error Handling

**Graceful Degradation:**
- Non-fatal error recovery
- Default value substitution
- Error state isolation
- User notification

**Security Boundaries:**
- Input sanitization
- Output encoding
- Resource isolation
- Permission checking

## Extension Points

### Renderer Interface

The architecture supports multiple renderers:

```python
class Renderer:
    """Abstract renderer interface."""

    def begin_frame(self) -> None: ...
    def end_frame(self) -> None: ...
    def draw_rect(self, rect: Rect, color: Color) -> None: ...
    def draw_text(self, pos: Vec2, text: str, color: Color) -> None: ...
```

**Current Implementations:**
- SDL2 renderer (reference implementation)
- Debug renderer (testing)

**Potential Extensions:**
- OpenGL renderer
- Vulkan renderer
- Web renderer (WebAssembly)
- Terminal renderer

### Widget Extensions

**Custom Widget Development:**
```python
def custom_widget(ctx: Context, state: Any) -> tuple[int, Any]:
    """Custom widget implementation."""
    # Layout calculations
    # Event handling
    # Rendering
    return result_flags, new_state
```

**Widget Categories for Extension:**
- Data visualization widgets
- Custom input controls
- Specialized containers
- Animation widgets

### Platform Integration

**Event System Extensions:**
- Custom event types
- Event filtering
- Event recording/playback
- Gesture recognition

**Resource System Extensions:**
- Custom font loading
- Image resource management
- Audio integration
- Asset pipelines

## Future Architecture Considerations

### Scalability

**Large UI Support:**
- Virtual scrolling
- Lazy widget instantiation
- Hierarchical culling
- Level-of-detail rendering

**Multi-threading:**
- Background layout calculation
- Asynchronous resource loading
- Thread-safe state management
- Lock-free data structures

### Portability

**Platform Support:**
- Mobile platforms (iOS, Android)
- Web platforms (WebAssembly)
- Embedded systems
- Game engines

**Language Bindings:**
- JavaScript/TypeScript
- Rust
- Go
- C#

### Advanced Features

**Animation System:**
- Smooth transitions
- Easing functions
- Timeline management
- Keyframe interpolation

**Accessibility:**
- Screen reader support
- Keyboard navigation
- High contrast themes
- Voice control

**Developer Tools:**
- Visual debugger
- Performance profiler
- Layout inspector
- Theme editor

## Conclusion

The PyMUI architecture balances simplicity, performance, and safety through careful layering and design patterns. The immediate-mode approach provides predictable behavior and minimal complexity, while the Cython wrapper ensures memory safety and Python integration. The modular design supports extension and customization while maintaining a clean separation of concerns.

This architecture enables PyMUI to serve as both a production-ready UI library and a foundation for further development and experimentation in immediate-mode UI systems.