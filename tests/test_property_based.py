#!/usr/bin/env python3
"""
Property-based tests for pymui using Hypothesis.

These tests use property-based testing to find edge cases and ensure
robustness across a wide range of inputs.
"""

import sys
from pathlib import Path

# Add src to path for imports
ROOTDIR = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(ROOTDIR))

try:
    from hypothesis import given, strategies as st, assume, settings, HealthCheck
    from hypothesis.strategies import integers, text, floats, booleans, lists
except ImportError:
    import pytest
    pytest.skip("Hypothesis not available", allow_module_level=True)

try:
    from pymui import pymui
except ImportError:
    import pymui


class TestVec2Properties:
    """Property-based tests for Vec2 class."""

    @given(x=integers(min_value=-1000000, max_value=1000000),
           y=integers(min_value=-1000000, max_value=1000000))
    def test_vec2_creation_and_access(self, x, y):
        """Vec2 creation should preserve input values."""
        vec = pymui.Vec2(x, y)
        assert vec.x == x
        assert vec.y == y

    @given(x=integers(min_value=-1000000, max_value=1000000),
           y=integers(min_value=-1000000, max_value=1000000))
    def test_vec2_property_assignment(self, x, y):
        """Vec2 property assignment should work correctly."""
        vec = pymui.Vec2(0, 0)
        vec.x = x
        vec.y = y
        assert vec.x == x
        assert vec.y == y

    @given(x=integers(), y=integers())
    def test_vec2_repr_contains_values(self, x, y):
        """Vec2 repr should contain the coordinate values."""
        vec = pymui.Vec2(x, y)
        repr_str = repr(vec)
        assert str(x) in repr_str
        assert str(y) in repr_str
        assert "Vec2" in repr_str


class TestRectProperties:
    """Property-based tests for Rect class."""

    @given(x=integers(min_value=-1000000, max_value=1000000),
           y=integers(min_value=-1000000, max_value=1000000),
           w=integers(min_value=0, max_value=1000000),
           h=integers(min_value=0, max_value=1000000))
    def test_rect_creation_and_access(self, x, y, w, h):
        """Rect creation should preserve input values."""
        rect = pymui.Rect(x, y, w, h)
        assert rect.x == x
        assert rect.y == y
        assert rect.w == w
        assert rect.h == h

    @given(x=integers(), y=integers(), w=integers(), h=integers())
    def test_rect_property_assignment(self, x, y, w, h):
        """Rect property assignment should work correctly."""
        rect = pymui.Rect(0, 0, 1, 1)
        rect.x = x
        rect.y = y
        rect.w = w
        rect.h = h
        assert rect.x == x
        assert rect.y == y
        assert rect.w == w
        assert rect.h == h

    @given(x=integers(), y=integers(), w=integers(), h=integers())
    def test_rect_repr_contains_values(self, x, y, w, h):
        """Rect repr should contain all dimension values."""
        rect = pymui.Rect(x, y, w, h)
        repr_str = repr(rect)
        assert str(x) in repr_str
        assert str(y) in repr_str
        assert str(w) in repr_str
        assert str(h) in repr_str
        assert "Rect" in repr_str


class TestColorProperties:
    """Property-based tests for Color class."""

    @given(r=integers(min_value=0, max_value=255),
           g=integers(min_value=0, max_value=255),
           b=integers(min_value=0, max_value=255),
           a=integers(min_value=0, max_value=255))
    def test_color_creation_and_access(self, r, g, b, a):
        """Color creation should preserve input values."""
        color = pymui.Color(r, g, b, a)
        assert color.r == r
        assert color.g == g
        assert color.b == b
        assert color.a == a

    @given(r=integers(min_value=0, max_value=255),
           g=integers(min_value=0, max_value=255),
           b=integers(min_value=0, max_value=255))
    def test_color_default_alpha(self, r, g, b):
        """Color should default to alpha=255 when not specified."""
        color = pymui.Color(r, g, b)
        assert color.r == r
        assert color.g == g
        assert color.b == b
        assert color.a == 255

    @given(r=integers(min_value=0, max_value=255),
           g=integers(min_value=0, max_value=255),
           b=integers(min_value=0, max_value=255),
           a=integers(min_value=0, max_value=255))
    def test_color_property_assignment(self, r, g, b, a):
        """Color property assignment should work correctly."""
        color = pymui.Color(0, 0, 0, 0)
        color.r = r
        color.g = g
        color.b = b
        color.a = a
        assert color.r == r
        assert color.g == g
        assert color.b == b
        assert color.a == a


class TestContextProperties:
    """Property-based tests for Context class."""

    def setup_method(self):
        """Set up context for each test."""
        self.ctx = pymui.Context()

    @given(text_content=text(min_size=0, max_size=1000))
    def test_text_with_various_content(self, text_content):
        """Text function should handle various text content safely."""
        self.ctx.begin()
        try:
            self.ctx.text(text_content)
        except UnicodeEncodeError:
            # This is acceptable - some Unicode strings may not encode
            pass
        finally:
            self.ctx.end()

    @given(label_text=text(min_size=1, max_size=200))
    def test_label_with_various_content(self, label_text):
        """Label function should handle various text content safely."""
        # Filter out strings that would cause encoding issues
        assume(all(ord(c) < 65536 for c in label_text))  # Basic Multilingual Plane only

        self.ctx.begin()
        try:
            self.ctx.label(label_text)
        except (UnicodeEncodeError, ValueError):
            # These are acceptable for invalid inputs
            pass
        finally:
            self.ctx.end()

    @given(button_text=text(min_size=1, max_size=100),
           icon=integers(min_value=0, max_value=10),
           opt=integers(min_value=0, max_value=1000))
    def test_button_with_various_parameters(self, button_text, icon, opt):
        """Button function should handle various parameters safely."""
        assume(all(ord(c) < 65536 for c in button_text))

        self.ctx.begin()
        try:
            result = self.ctx.button(button_text, icon, opt)
            # Result should be an integer
            assert isinstance(result, int)
        except (UnicodeEncodeError, ValueError):
            pass
        finally:
            self.ctx.end()

    @given(value=floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
           low=floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
           high=floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
           step=floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    def test_slider_with_various_ranges(self, value, low, high, step):
        """Slider should handle various numeric ranges safely."""
        # Ensure low <= high
        if low > high:
            low, high = high, low

        self.ctx.begin()
        try:
            result, new_value = self.ctx.slider(value, low, high, step)

            # Result should be an integer (flags)
            assert isinstance(result, int)
            # New value should be a float
            assert isinstance(new_value, float)
            # New value should be within bounds (allowing for floating point precision)
            assert low - 0.001 <= new_value <= high + 0.001

        except (ValueError, OverflowError):
            # These are acceptable for extreme values
            pass
        finally:
            self.ctx.end()

    @given(state=booleans(),
           label_text=text(min_size=1, max_size=50))
    def test_checkbox_with_various_states(self, state, label_text):
        """Checkbox should handle various states and labels safely."""
        assume(all(ord(c) < 65536 for c in label_text))

        self.ctx.begin()
        try:
            result, new_state = self.ctx.checkbox(label_text, state)

            # Result should be an integer (flags)
            assert isinstance(result, int)
            # New state should be a boolean-like (0 or 1)
            assert new_state in [0, 1]

        except (UnicodeEncodeError, ValueError):
            pass
        finally:
            self.ctx.end()


class TestTextboxProperties:
    """Property-based tests for Textbox class."""

    @given(buffer_size=integers(min_value=2, max_value=1024))
    def test_textbox_creation_with_various_sizes(self, buffer_size):
        """Textbox creation should work with various buffer sizes."""
        textbox = pymui.Textbox(buffer_size)
        assert textbox.text == ""

    @given(buffer_size=integers(min_value=2, max_value=256),
           text_content=text(min_size=0, max_size=200))
    def test_textbox_text_assignment(self, buffer_size, text_content):
        """Textbox should handle text assignment safely."""
        assume(all(ord(c) < 65536 for c in text_content))  # Avoid exotic Unicode

        textbox = pymui.Textbox(buffer_size)
        try:
            textbox.text = text_content

            # Text should be accessible
            result_text = textbox.text
            assert isinstance(result_text, str)

            # If text fits in buffer, it should be preserved
            encoded_len = len(text_content.encode('utf-8'))
            if encoded_len < buffer_size - 1:
                assert result_text == text_content
            else:
                # Text may be truncated but should not crash
                assert len(result_text) <= len(text_content)

        except (UnicodeEncodeError, ValueError):
            # These are acceptable for problematic inputs
            pass


class TestLayoutProperties:
    """Property-based tests for layout operations."""

    def setup_method(self):
        """Set up context for each test."""
        self.ctx = pymui.Context()

    @given(width_list=lists(integers(min_value=-1, max_value=1000), min_size=1, max_size=10),
           height=integers(min_value=0, max_value=1000))
    def test_layout_row_with_various_widths(self, width_list, height):
        """Layout row should handle various width configurations."""
        self.ctx.begin()
        try:
            self.ctx.layout_row(width_list, height)
        except (ValueError, MemoryError):
            # These are acceptable for invalid inputs
            pass
        finally:
            self.ctx.end()

    @given(width=integers(min_value=-1000, max_value=1000),
           height=integers(min_value=-1000, max_value=1000))
    def test_layout_width_height(self, width, height):
        """Layout width/height should handle various values."""
        self.ctx.begin()
        try:
            self.ctx.layout_width(width)
            self.ctx.layout_height(height)
        except ValueError:
            pass
        finally:
            self.ctx.end()


class TestWindowProperties:
    """Property-based tests for window operations."""

    def setup_method(self):
        """Set up context for each test."""
        self.ctx = pymui.Context()

    @given(title=text(min_size=1, max_size=100),
           x=integers(min_value=-1000, max_value=1000),
           y=integers(min_value=-1000, max_value=1000),
           w=integers(min_value=0, max_value=1000),
           h=integers(min_value=0, max_value=1000),
           opt=integers(min_value=0, max_value=1000))
    def test_window_with_various_parameters(self, title, x, y, w, h, opt):
        """Window creation should handle various parameters safely."""
        assume(all(ord(c) < 65536 for c in title))

        self.ctx.begin()
        try:
            rect = pymui.Rect(x, y, w, h)
            result = self.ctx.begin_window(title, rect, opt)

            # Result should be an integer
            assert isinstance(result, int)

            if result:  # If window is open
                self.ctx.end_window()

        except (UnicodeEncodeError, ValueError):
            pass
        finally:
            self.ctx.end()


# Custom strategies for more focused testing
@st.composite
def valid_text_content(draw):
    """Generate valid text content for UI elements."""
    return draw(text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),  # ASCII printable
        min_size=0,
        max_size=100
    ))


@st.composite
def valid_color_components(draw):
    """Generate valid RGBA color components."""
    return draw(st.tuples(
        integers(min_value=0, max_value=255),  # R
        integers(min_value=0, max_value=255),  # G
        integers(min_value=0, max_value=255),  # B
        integers(min_value=0, max_value=255)   # A
    ))


class TestIntegrationProperties:
    """Property-based integration tests."""

    def setup_method(self):
        """Set up context for each test."""
        self.ctx = pymui.Context()

    @given(window_title=valid_text_content(),
           num_widgets=integers(min_value=1, max_value=10))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_complete_ui_workflow(self, window_title, num_widgets):
        """Test complete UI workflow with various configurations."""
        self.ctx.begin()

        try:
            if self.ctx.begin_window(window_title, pymui.Rect(10, 10, 300, 200)):
                # Create various widgets
                for i in range(num_widgets):
                    widget_type = i % 4

                    if widget_type == 0:
                        self.ctx.label(f"Label {i}")
                    elif widget_type == 1:
                        self.ctx.button(f"Button {i}")
                    elif widget_type == 2:
                        result, value = self.ctx.slider(float(i * 10), 0.0, 100.0)
                    elif widget_type == 3:
                        result, state = self.ctx.checkbox(f"Check {i}", i % 2 == 0)

                self.ctx.end_window()

        except (UnicodeEncodeError, ValueError, MemoryError):
            pass
        finally:
            self.ctx.end()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])