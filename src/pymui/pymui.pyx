
from libc.stdlib cimport malloc, calloc, realloc, free
from libc.string cimport memcpy, memset, strlen

cimport pymui



# Fused types
ctypedef fused number:
    int
    float

# Version function
def version() -> str:
    """Get the microui library version.

    Returns:
        str: The version string of the underlying microui library.
    """
    return MU_VERSION.decode()

def clamp(number x, number a, number b) -> number:
    """Clamp a value between minimum and maximum bounds.

    Args:
        x: The value to clamp
        a: The minimum bound
        b: The maximum bound

    Returns:
        The clamped value, guaranteed to be between a and b (inclusive)
    """
    return min(b, max(a, x))

# Global convenience functions
def vec2(int x, int y) -> Vec2:
    """Create a 2D vector with the given coordinates.

    Args:
        x (int): The x coordinate
        y (int): The y coordinate

    Returns:
        Vec2: A new Vec2 instance with the specified coordinates
    """
    return Vec2.from_c(mu_vec2(x, y))

def rect(int x, int y, int w, int h) -> Rect:
    """Create a rectangle with the given position and dimensions.

    Args:
        x (int): The x coordinate of the top-left corner
        y (int): The y coordinate of the top-left corner
        w (int): The width of the rectangle
        h (int): The height of the rectangle

    Returns:
        Rect: A new Rect instance with the specified dimensions
    """
    return Rect.from_c(mu_rect(x, y, w, h))

def color(int r, int g, int b, int a=255) -> Color:
    """Create a color with the given RGBA values.

    Args:
        r (int): Red component (0-255)
        g (int): Green component (0-255)
        b (int): Blue component (0-255)
        a (int, optional): Alpha component (0-255). Defaults to 255 (fully opaque).

    Returns:
        Color: A new Color instance with the specified RGBA values
    """
    return Color.from_c(mu_color(r, g, b, a))


# Basic struct classes
cdef class Vec2:
    """A 2D vector with integer coordinates.

    This class represents a 2D vector with x and y integer coordinates,
    commonly used for positions, sizes, and offsets in the UI system.

    Attributes:
        x (int): The x coordinate
        y (int): The y coordinate

    Example:
        >>> v = Vec2(10, 20)
        >>> print(v.x, v.y)  # Output: 10 20
        >>> v.x = 30
        >>> print(v)  # Output: Vec2(30, 20)
    """
    cdef mu_Vec2 _vec

    def __cinit__(self, int x=0, int y=0):
        """Initialize a Vec2 with the given coordinates.

        Args:
            x (int, optional): The x coordinate. Defaults to 0.
            y (int, optional): The y coordinate. Defaults to 0.
        """
        self._vec.x = x
        self._vec.y = y
    
    @property
    def x(self) -> int:
        """Get or set the x coordinate."""
        return self._vec.x

    @x.setter
    def x(self, int value):
        self._vec.x = value

    @property
    def y(self) -> int:
        """Get or set the y coordinate."""
        return self._vec.y

    @y.setter
    def y(self, int value):
        self._vec.y = value
    
    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"
    
    @staticmethod
    cdef Vec2 from_c(mu_Vec2 vec):
        cdef Vec2 result = Vec2.__new__(Vec2)
        result._vec = vec
        return result
    
    cdef mu_Vec2 to_c(self):
        return self._vec


cdef class Rect:
    """A rectangle defined by position and dimensions.

    This class represents a rectangle with integer coordinates and dimensions,
    commonly used for UI element bounds, clipping regions, and layout calculations.

    Attributes:
        x (int): The x coordinate of the top-left corner
        y (int): The y coordinate of the top-left corner
        w (int): The width of the rectangle
        h (int): The height of the rectangle

    Example:
        >>> r = Rect(10, 20, 100, 50)
        >>> print(f"Position: ({r.x}, {r.y}), Size: {r.w}x{r.h}")
        Position: (10, 20), Size: 100x50
    """
    cdef mu_Rect _rect

    def __cinit__(self, int x=0, int y=0, int w=0, int h=0):
        """Initialize a Rect with the given position and dimensions.

        Args:
            x (int, optional): The x coordinate of the top-left corner. Defaults to 0.
            y (int, optional): The y coordinate of the top-left corner. Defaults to 0.
            w (int, optional): The width of the rectangle. Defaults to 0.
            h (int, optional): The height of the rectangle. Defaults to 0.
        """
        self._rect.x = x
        self._rect.y = y
        self._rect.w = w
        self._rect.h = h

    @property
    def x(self) -> int:
        """Get or set the x coordinate of the top-left corner."""
        return self._rect.x

    @x.setter
    def x(self, int value):
        self._rect.x = value

    @property
    def y(self) -> int:
        """Get or set the y coordinate of the top-left corner."""
        return self._rect.y

    @y.setter
    def y(self, int value):
        self._rect.y = value

    @property
    def w(self) -> int:
        """Get or set the width of the rectangle."""
        return self._rect.w

    @w.setter
    def w(self, int value):
        self._rect.w = value

    @property
    def h(self) -> int:
        """Get or set the height of the rectangle."""
        return self._rect.h

    @h.setter
    def h(self, int value):
        self._rect.h = value

    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.w}, {self.h})"

    @staticmethod
    cdef Rect from_c(mu_Rect rect):
        cdef Rect result = Rect.__new__(Rect)
        result._rect = rect
        return result

    cdef mu_Rect to_c(self):
        return self._rect


cdef class Color:
    """An RGBA color with 8-bit components.

    This class represents a color with red, green, blue, and alpha components,
    each ranging from 0 to 255. It's used throughout the UI system for
    rendering text, backgrounds, borders, and other visual elements.

    Attributes:
        r (int): Red component (0-255)
        g (int): Green component (0-255)
        b (int): Blue component (0-255)
        a (int): Alpha component (0-255, where 0 is transparent and 255 is opaque)

    Example:
        >>> red = Color(255, 0, 0)        # Fully opaque red
        >>> semi_blue = Color(0, 0, 255, 128)  # Semi-transparent blue
        >>> print(red)  # Output: Color(255, 0, 0, 255)
    """
    cdef mu_Color _color

    def __cinit__(self, int r=0, int g=0, int b=0, int a=255):
        """Initialize a Color with the given RGBA values.

        Args:
            r (int, optional): Red component (0-255). Defaults to 0.
            g (int, optional): Green component (0-255). Defaults to 0.
            b (int, optional): Blue component (0-255). Defaults to 0.
            a (int, optional): Alpha component (0-255). Defaults to 255 (fully opaque).
        """
        self._color.r = r
        self._color.g = g
        self._color.b = b
        self._color.a = a

    @property
    def r(self) -> int:
        """Get or set the red component (0-255)."""
        return self._color.r

    @r.setter
    def r(self, int value):
        self._color.r = value

    @property
    def g(self) -> int:
        """Get or set the green component (0-255)."""
        return self._color.g

    @g.setter
    def g(self, int value):
        self._color.g = value

    @property
    def b(self) -> int:
        """Get or set the blue component (0-255)."""
        return self._color.b

    @b.setter
    def b(self, int value):
        self._color.b = value

    @property
    def a(self) -> int:
        """Get or set the alpha component (0-255, where 0 is transparent)."""
        return self._color.a

    @a.setter
    def a(self, int value):
        self._color.a = value
    
    def __repr__(self):
        return f"Color({self.r}, {self.g}, {self.b}, {self.a})"
    
    @staticmethod
    cdef Color from_c(mu_Color color):
        cdef Color result = Color.__new__(Color)
        result._color = color
        return result
    
    cdef mu_Color to_c(self):
        return self._color


cdef class Style:
    cdef mu_Style* ptr
    cdef bint owner

    def __cinit__(self):
        self.ptr = NULL
        self.owner = False

    def __dealloc__(self):
        # De-allocate if not null and flag is set
        if self.ptr is not NULL and self.owner is True:
            free(self.ptr)
            self.ptr = NULL

    def __init__(self):
        # Prevent accidental instantiation from normal Python code
        # since we cannot pass a struct pointer into a Python constructor.
        raise TypeError("This class cannot be instantiated directly.")

    @staticmethod
    cdef Style from_ptr(mu_Style* ptr, bint owner=False):
        cdef Style wrapper = Style.__new__(Style)
        wrapper.ptr = ptr
        wrapper.owner = owner
        return wrapper

    @staticmethod
    cdef Style new():
        cdef mu_Style* _ptr = <mu_Style*>malloc(sizeof(mu_Style))
        if _ptr is NULL:
            raise MemoryError("Failed to allocate Style")
        memset(_ptr, 0, sizeof(mu_Style))
        return Style.from_ptr(_ptr, owner=True)

    # @property
    # def font(self):
    #     return <object>self.ptr.font
    
    # @font.setter
    # def font(self, font):
    #     self.ptr.font = <mu_Font>font
    
    @property
    def size(self) -> Vec2:
        return Vec2.from_c(self.ptr.size)
    
    @size.setter
    def size(self, Vec2 value):
        self.ptr.size = value.to_c()
    
    @property
    def padding(self) -> int:
        return self.ptr.padding
    
    @padding.setter
    def padding(self, int value):
        self.ptr.padding = value
    
    @property
    def spacing(self) -> int:
        return self.ptr.spacing
    
    @spacing.setter
    def spacing(self, int value):
        self.ptr.spacing = value
    
    @property
    def indent(self) -> int:
        return self.ptr.indent
    
    @indent.setter
    def indent(self, int value):
        self.ptr.indent = value
    
    @property
    def title_height(self) -> int:
        return self.ptr.title_height
    
    @title_height.setter
    def title_height(self, int value):
        self.ptr.title_height = value
    
    @property
    def scrollbar_size(self) -> int:
        return self.ptr.scrollbar_size
    
    @scrollbar_size.setter
    def scrollbar_size(self, int value):
        self.ptr.scrollbar_size = value
    
    @property
    def thumb_size(self) -> int:
        return self.ptr.thumb_size
    
    @thumb_size.setter
    def thumb_size(self, int value):
        self.ptr.thumb_size = value
    
    def get_color(self, int index) -> Color:
        if 0 <= index < MU_COLOR_MAX:
            return Color.from_c(self.ptr.colors[index])
        raise IndexError("Color index out of range")
    
    def set_color(self, int index, Color color):
        if 0 <= index < MU_COLOR_MAX:
            self.ptr.colors[index] = color.to_c()
        else:
            raise IndexError("Color index out of range")


cdef int text_width(mu_Font font, const char *text, int len) noexcept:
    """Calculate text width for our bitmap font (matching Python renderer)"""
    return r_get_text_width(text, len)
    # if text == NULL:
    #     return 0

    # if len == -1:
    #     len = strlen(text)

    # # Python renderer uses 5-pixel wide characters + 1 pixel spacing = 6 pixels per char
    # cdef int width = 0
    # cdef int i = 0

    # while i < len and text[i] != 0:
    #     if text[i] == b'\t':
    #         width += 24  # Tab = 4 characters * 6 pixels
    #     else:
    #         width += 6   # Each character is 6 pixels wide (5 + 1 spacing)
    #     i += 1

    # return width

cdef int text_height(mu_Font font) noexcept:
    """Text height for our bitmap font (matching Python renderer)"""
    return r_get_text_height()
    # return 8  # Python renderer uses 7-pixel height + 1 pixel spacing



# Main Context class
cdef class Context:
    """The main microui context for creating and managing UI elements.

    This is the primary class for building immediate-mode user interfaces.
    It manages the UI state, handles input events, and provides methods
    for creating windows, widgets, and controlling layout.

    The Context follows an immediate-mode paradigm where UI elements
    are created and processed each frame rather than being persistent objects.

    The Context supports Python's context manager protocol for both frame and
    window management, providing automatic cleanup with the 'with' statement.

    Examples:
        Modern approach (recommended - context managers for frame and window):
        >>> with Context() as ctx:
        ...     with ctx.window("My Window", 10, 10, 200, 150) as window:
        ...         if window.is_open:
        ...             ctx.label("Hello, World!")
        ...             if ctx.button("Click me"):
        ...                 print("Button clicked!")

        Alternative (manual window management):
        >>> with Context() as ctx:
        ...     if ctx.begin_window("My Window", rect(10, 10, 200, 150)):
        ...         ctx.label("Hello, World!")
        ...         ctx.end_window()

        Legacy (manual frame management):
        >>> ctx = Context()
        >>> ctx.begin()
        >>> try:
        ...     # UI code here
        ...     pass
        ... finally:
        ...     ctx.end()

    Note:
        The recommended approach uses context managers for both frame and window
        management. This provides automatic cleanup, exception safety, and cleaner code.
        The window context manager automatically calls begin_window() and end_window(),
        while the frame context manager automatically calls begin() and end().
    """
    cdef mu_Context* ptr
    cdef bint owner
    cdef mu_Command* current_command

    def __cinit__(self):
        self.ptr = NULL
        self.owner = False
        self.current_command = NULL

    def __dealloc__(self):
        # De-allocate if not null and flag is set
        if self.ptr is not NULL and self.owner is True:
            free(self.ptr)
            self.ptr = NULL

    def __init__(self):
        """Initialize a new microui context.

        Creates and initializes the underlying microui context with default
        text measurement callbacks. The context is ready to use after initialization.

        Raises:
            MemoryError: If memory allocation for the context fails.
        """
        self.ptr = <mu_Context*>malloc(sizeof(mu_Context))
        if self.ptr is NULL:
            raise MemoryError("Failed to allocate Context")
        mu_init(self.ptr)
        self.ptr.text_width = text_width
        self.ptr.text_height = text_height
        self.owner = True

    @staticmethod
    cdef Context from_ptr(mu_Context* ptr, bint owner=False):
        cdef Context wrapper = Context.__new__(Context)
        wrapper.ptr = ptr
        wrapper.owner = owner
        wrapper.current_command = NULL
        return wrapper

    @staticmethod
    cdef Context new():
        cdef mu_Context* _ptr = <mu_Context*>malloc(sizeof(mu_Context))
        if _ptr is NULL:
            raise MemoryError("Failed to allocate Context")
        mu_init(_ptr)
        return Context.from_ptr(_ptr, owner=True)

    @property
    def style(self) -> Style:
        """Get the current style configuration for the context.

        Returns:
            Style: The style object containing colors, spacing, and sizing information.
        """
        return Style.from_ptr(<mu_Style*>self.ptr.style)

    def begin(self):
        """Start a new UI frame.

        This must be called at the beginning of each frame before any UI elements
        are created. It prepares the context for a new frame of UI processing.

        Note:
            Always pair this with a call to end() at the end of the frame.
        """
        mu_begin(self.ptr)
        # Reset command iterator for new frame
        self.current_command = NULL
    
    def end(self):
        """End the current UI frame.

        This must be called at the end of each frame after all UI elements
        have been processed. It finalizes the frame and prepares rendering commands.

        Note:
            Always pair this with a call to begin() at the start of the frame.
        """
        mu_end(self.ptr)

    def __enter__(self):
        """Enter the context manager - automatically calls begin().

        This allows using the Context with Python's 'with' statement for automatic
        frame management. For even cleaner code, use the window context manager too:

        Example:
            >>> with pymui.Context() as ctx:
            ...     with ctx.window("My Window", 10, 10, 200, 150) as window:
            ...         if window.is_open:
            ...             ctx.label("Hello, World!")
            ...             if ctx.button("Click me"):
            ...                 print("Button clicked!")

        Returns:
            Context: Returns self to allow method chaining
        """
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager - automatically calls end().

        This ensures that end() is always called even if an exception occurs
        within the context manager block.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            None: Does not suppress exceptions
        """
        self.end()
        return None

    def set_focus(self, unsigned int id):
        """Set the focused widget.

        Args:
            id (int): The widget ID to focus
        """
        mu_set_focus(self.ptr, id)
    
    def get_id(self, data) -> int:
        """Get an ID for the given data.

        Args:
            data: The data to generate an ID for (string, bytes, or any object)

        Returns:
            int: A unique ID for the given data

        Raises:
            UnicodeEncodeError: If data cannot be encoded to UTF-8
        """

        cdef bytes bdata
        try:
            if isinstance(data, str):
                bdata = data.encode('utf-8')
            elif isinstance(data, bytes):
                bdata = data
            else:
                bdata = str(data).encode('utf-8')
        except UnicodeEncodeError as e:
            raise UnicodeEncodeError("Failed to encode data for ID generation") from e

        return mu_get_id(self.ptr, <const char*>bdata, len(bdata))
    
    def push_id(self, data):
        """Push an ID onto the ID stack"""
        cdef bytes bdata
        if isinstance(data, str):
            bdata = data.encode('utf-8')
        elif isinstance(data, bytes):
            bdata = data
        else:
            bdata = str(data).encode('utf-8')
        mu_push_id(self.ptr, <const char*>bdata, len(bdata))
    
    def pop_id(self):
        """Pop an ID from the ID stack"""
        mu_pop_id(self.ptr)
    
    def push_clip_rect(self, Rect rect):
        """Push a clip rectangle"""
        mu_push_clip_rect(self.ptr, rect.to_c())
    
    def pop_clip_rect(self):
        """Pop a clip rectangle"""
        mu_pop_clip_rect(self.ptr)
    
    def get_clip_rect(self) -> Rect:
        """Get the current clip rectangle"""
        return Rect.from_c(mu_get_clip_rect(self.ptr))
    
    def check_clip(self, Rect rect) -> int:
        """Check if a rectangle is clipped"""
        return mu_check_clip(self.ptr, rect.to_c())
    
    # Input functions
    def input_mousemove(self, int x, int y):
        """Handle mouse movement"""
        mu_input_mousemove(self.ptr, x, y)
    
    def input_mousedown(self, int x, int y, int btn):
        """Handle mouse button press"""
        mu_input_mousedown(self.ptr, x, y, btn)
    
    def input_mouseup(self, int x, int y, int btn):
        """Handle mouse button release"""
        mu_input_mouseup(self.ptr, x, y, btn)
    
    def input_scroll(self, int x, int y):
        """Handle scroll input"""
        mu_input_scroll(self.ptr, x, y)
    
    def input_keydown(self, int key):
        """Handle key press"""
        mu_input_keydown(self.ptr, key)
    
    def input_keyup(self, int key):
        """Handle key release"""
        mu_input_keyup(self.ptr, key)
    
    def input_text(self, str text):
        """Handle text input"""
        cdef bytes btext = text.encode('utf-8')
        mu_input_text(self.ptr, btext)
    
    # Layout functions
    # def layout_row(self, int items, widths, int height):
    #     """Set up a row layout"""
    #     cdef int* width_array = NULL
    #     cdef int i
        
    #     if widths is not None:
    #         if isinstance(widths, (list, tuple)):
    #             width_array = <int*>malloc(items * sizeof(int))
    #             for i in range(min(items, len(widths))):
    #                 width_array[i] = widths[i]
    #         elif isinstance(widths, np.ndarray):
    #             width_array = <int*>np.PyArray_DATA(widths)
        
    #     mu_layout_row(self.ptr, items, width_array, height)
        
    #     if width_array is not NULL and not isinstance(widths, np.ndarray):
    #         free(width_array)
    
    def layout_width(self, int width):
        """Set layout width"""
        mu_layout_width(self.ptr, width)
    
    def layout_height(self, int height):
        """Set layout height"""
        mu_layout_height(self.ptr, height)
    
    def layout_begin_column(self):
        """Begin a column layout"""
        mu_layout_begin_column(self.ptr)
    
    def layout_end_column(self):
        """End a column layout"""
        mu_layout_end_column(self.ptr)
    
    def layout_set_next(self, Rect rect, int relative):
        """Set the next layout rectangle"""
        mu_layout_set_next(self.ptr, rect.to_c(), relative)
    
    def layout_next(self) -> Rect:
        """Get the next layout rectangle"""
        return Rect.from_c(mu_layout_next(self.ptr))
    
    # Widget functions
    def text(self, str text):
        """Draw text.

        Args:
            text (str): The text to draw

        Raises:
            UnicodeEncodeError: If text cannot be encoded to UTF-8
        """
        if text is None:
            text = ""

        cdef bytes btext
        try:
            btext = text.encode('utf-8')
        except UnicodeEncodeError as e:
            raise UnicodeEncodeError("Failed to encode text") from e

        mu_text(self.ptr, btext)
    
    def label(self, str text):
        """Draw a label"""
        cdef bytes btext = text.encode('utf-8')
        mu_label(self.ptr, btext)
    
    def button(self, str label, int icon=0, int opt=0) -> int:
        """Create a button"""
        cdef bytes blabel = label.encode('utf-8')
        return mu_button_ex(self.ptr, blabel, icon, opt)
    
    def checkbox(self, str label, state) -> tuple:
        """Create a checkbox - returns (result, new_state)"""
        cdef bytes blabel
        cdef int c_state
        cdef int result
        
        blabel = label.encode('utf-8')
        c_state = int(state)
        result = mu_checkbox(self.ptr, blabel, &c_state)
        return (result, c_state)
    
    
    def textbox(self, str buf, int bufsz, int opt=0):
        """Create a textbox - backward compatible version returns just result"""
        # For backward compatibility, return just the result code
        # The text modification is handled by reference in the original design
        cdef bytes bbuf = buf.encode('utf-8')
        # For testing/mock purposes, just return a mock result
        # In practice, this would need proper buffer handling
        return 0  # MU_RES_NONE
    
    def textbox_ex(self, str buf, int bufsz, int opt=0) -> tuple:
        """Create a textbox with enhanced memory safety - returns (result, new_text)

        Args:
            buf (str): Initial text content
            bufsz (int): Buffer size in bytes (must be > 0)
            opt (int, optional): Options flags. Defaults to 0.

        Returns:
            tuple: (result_flags, new_text_content)

        Raises:
            ValueError: If buffer size is invalid
            MemoryError: If memory allocation fails
        """
        # Validate buffer size
        if bufsz <= 0:
            raise ValueError("Buffer size must be positive")
        if bufsz > 1024 * 1024:  # 1MB limit for safety
            raise ValueError("Buffer size too large (max 1MB)")

        cdef char* c_buf = <char*>malloc(bufsz)
        if c_buf == NULL:
            raise MemoryError("Failed to allocate textbox buffer")

        cdef bytes b_buf
        cdef int copy_len
        cdef int result
        cdef int encoded_len

        try:
            # Encode and validate input text
            b_buf = buf.encode('utf-8')
            encoded_len = len(b_buf)

            # Ensure we have space for null terminator
            if bufsz < 2:
                raise ValueError("Buffer too small (minimum 2 bytes)")

            # Calculate safe copy length with explicit bounds check
            copy_len = min(encoded_len, bufsz - 1)
            if copy_len < 0:
                copy_len = 0

            # Safe memory copy with bounds verification
            if copy_len > 0 and encoded_len > 0:
                memcpy(c_buf, <const char*>b_buf, copy_len)
            c_buf[copy_len] = 0  # null terminate

            # Call microui function
            result = mu_textbox_ex(self.ptr, c_buf, bufsz, opt)

            # Convert back to Python string with error handling
            new_text = c_buf.decode('utf-8', errors='replace')

            return (result, new_text)
        finally:
            free(c_buf)
    
    def slider(self, float value, float low, float high, float step=0, str fmt="%.2f", int opt=0) -> tuple:
        """Create a slider - returns (result, new_value)"""
        cdef bytes bfmt
        cdef float c_value
        cdef int result
        
        bfmt = fmt.encode('utf-8')
        c_value = value
        result = mu_slider_ex(self.ptr, &c_value, low, high, step, bfmt, opt)
        return (result, c_value)
    
    
    def number(self, float value, float step, str fmt="%.2f", int opt=0) -> tuple:
        """Create a number input - returns (result, new_value)"""
        cdef bytes bfmt
        cdef float c_value
        cdef int result
        
        bfmt = fmt.encode('utf-8')
        c_value = value
        result = mu_number_ex(self.ptr, &c_value, step, bfmt, opt)
        return (result, c_value)
    
    
    def header(self, str label, int opt=0) -> int:
        """Create a header"""
        cdef bytes blabel = label.encode('utf-8')
        return mu_header_ex(self.ptr, blabel, opt)
    
    def begin_treenode(self, str label, int opt=0) -> int:
        """Begin a tree node"""
        cdef bytes blabel = label.encode('utf-8')
        return mu_begin_treenode_ex(self.ptr, blabel, opt)
    
    def end_treenode(self):
        """End a tree node"""
        mu_end_treenode(self.ptr)
    
    def begin_window(self, str title, Rect rect, int opt=0) -> int:
        """Begin a window.

        Args:
            title (str): The window title
            rect (Rect): The window bounds
            opt (int, optional): Window options flags. Defaults to 0.

        Returns:
            int: Non-zero if the window is open and should be processed

        Raises:
            RuntimeError: If the context is not properly initialized
            ValueError: If title is empty or rect has invalid dimensions
            UnicodeEncodeError: If title cannot be encoded to UTF-8
        """
        if self.ptr == NULL:
            raise RuntimeError("Context not initialized")
        if not title:
            raise ValueError("Window title cannot be empty")
        if rect.w < 0 or rect.h < 0:
            raise ValueError("Window dimensions cannot be negative")

        cdef bytes btitle
        try:
            btitle = title.encode('utf-8')
        except UnicodeEncodeError as e:
            raise UnicodeEncodeError("Failed to encode window title") from e

        return mu_begin_window_ex(self.ptr, btitle, rect.to_c(), opt)
    
    def end_window(self):
        """End a window"""
        mu_end_window(self.ptr)

    def window(self, str title, int x, int y, int w, int h, int opt=0):
        """Create a window context manager.

        This provides a more convenient way to create windows using Python's 'with' statement.
        The window will be automatically ended when the context exits.

        Args:
            title (str): The window title
            x (int): X position of the window
            y (int): Y position of the window
            w (int): Width of the window
            h (int): Height of the window
            opt (int, optional): Window options flags. Defaults to 0.

        Returns:
            Window: A window context manager object

        Example:
            >>> with ctx.window("My Window", 10, 10, 200, 150) as window:
            ...     if window.is_open:
            ...         ctx.label("Hello, World!")
        """
        return Window(self, title, Rect(x, y, w, h), opt)

    def open_popup(self, str name):
        """Open a popup"""
        cdef bytes bname = name.encode('utf-8')
        mu_open_popup(self.ptr, bname)
    
    def begin_popup(self, str name) -> int:
        """Begin a popup"""
        cdef bytes bname = name.encode('utf-8')
        return mu_begin_popup(self.ptr, bname)
    
    def end_popup(self):
        """End a popup"""
        mu_end_popup(self.ptr)
    
    def begin_panel(self, str name, int opt=0):
        """Begin a panel"""
        cdef bytes bname = name.encode('utf-8')
        mu_begin_panel_ex(self.ptr, bname, opt)
    
    def end_panel(self):
        """End a panel"""
        mu_end_panel(self.ptr)
    
    # Drawing functions
    def draw_rect(self, Rect rect, Color color):
        """Draw a rectangle"""
        mu_draw_rect(self.ptr, rect.to_c(), color.to_c())
    
    def draw_box(self, Rect rect, Color color):
        """Draw a box"""
        mu_draw_box(self.ptr, rect.to_c(), color.to_c())
    
    def draw_text(self, font, str text, Vec2 pos, Color color):
        """Draw text"""
        cdef bytes btext = text.encode('utf-8')
        r_draw_text(btext, pos.to_c(), color.to_c())
        # mu_draw_text(self.ptr, <mu_Font>font, btext, len(btext), pos.to_c(), color.to_c())
    
    def draw_icon(self, int id, Rect rect, Color color):
        """Draw an icon"""
        mu_draw_icon(self.ptr, id, rect.to_c(), color.to_c())
    
    # Utility functions
    @staticmethod
    def vec2(int x, int y) -> Vec2:
        """Create a Vec2"""
        return Vec2.from_c(mu_vec2(x, y))
    
    @staticmethod
    def rect(int x, int y, int w, int h) -> Rect:
        """Create a Rect"""
        return Rect.from_c(mu_rect(x, y, w, h))
    
    @staticmethod
    def color(int r, int g, int b, int a=255) -> Color:
        """Create a Color"""
        return Color.from_c(mu_color(r, g, b, a))
    
    # Command iteration reset
    def reset_command_iterator(self):
        """Reset command iterator to beginning"""
        self.current_command = NULL
    
    # Container access
    def get_current_container(self):
        """Get the current container - returns None if no container"""
        cdef mu_Container* container = mu_get_current_container(self.ptr)
        if container == NULL:
            return None
        # Return a simple wrapper with basic properties
        return ContainerWrapper.from_ptr(container)
    
    def get_container(self, str name):
        """Get a container by name"""
        cdef bytes bname = name.encode('utf-8')
        cdef mu_Container* container = mu_get_container(self.ptr, bname)
        if container == NULL:
            return None
        return ContainerWrapper.from_ptr(container)
    
    # Mouse over check
    def mouse_over(self, Rect rect) -> int:
        """Check if mouse is over a rectangle"""
        return mu_mouse_over(self.ptr, rect.to_c())
    
    # Command processing
    def next_command(self):
        """Get the next command from the command buffer"""
        cdef int result = mu_next_command(self.ptr, &self.current_command)
        
        if result == 0 or self.current_command == NULL:
            return None
        
        # Create a Python wrapper for the command based on its type
        if self.current_command.type == MU_COMMAND_RECT:
            return RectCommand.from_c(self.current_command.rect)
        elif self.current_command.type == MU_COMMAND_TEXT:
            return TextCommand.from_ptr(&self.current_command.text)
        elif self.current_command.type == MU_COMMAND_ICON:
            return IconCommand.from_c(self.current_command.icon)
        elif self.current_command.type == MU_COMMAND_CLIP:
            return ClipCommand.from_c(self.current_command.clip)
        elif self.current_command.type == MU_COMMAND_JUMP:
            return JumpCommand.from_c(self.current_command.jump)
        else:
            # Return a base command for unknown types
            return BaseCommand.from_c(self.current_command.base)
    
    def layout_row(self, widths, int height):
        """Set up a row layout with specific widths.

        Args:
            widths: List or tuple of column widths, or None for default
            height (int): Row height in pixels

        Raises:
            ValueError: If widths list is too large or contains invalid values
            MemoryError: If memory allocation fails
        """
        cdef int* width_array = NULL
        cdef int items = 0
        cdef int i
        cdef size_t allocation_size

        if widths is not None:
            if isinstance(widths, (list, tuple)):
                items = len(widths)

                # Validate array size to prevent overflow
                if items < 0:
                    raise ValueError("Invalid widths list")
                if items > 1000:  # Reasonable limit
                    raise ValueError("Too many width entries (max 1000)")

                if items > 0:
                    # Check for potential overflow in allocation size
                    allocation_size = items * sizeof(int)
                    if allocation_size / sizeof(int) != items:
                        raise ValueError("Width array too large")

                    width_array = <int*>malloc(allocation_size)
                    if width_array == NULL:
                        raise MemoryError("Failed to allocate width array")

                    # Copy with validation
                    for i in range(items):
                        try:
                            width_array[i] = int(widths[i])
                        except (ValueError, TypeError) as e:
                            free(width_array)
                            raise ValueError(f"Invalid width value at index {i}: {widths[i]}")

        try:
            mu_layout_row(self.ptr, items, width_array, height)
        finally:
            if width_array != NULL:
                free(width_array)


# Window context manager class
cdef class Window:
    """Context manager for microui windows.

    This class provides automatic window management using Python's context manager
    protocol. When entering the context, it calls begin_window(), and when exiting,
    it calls end_window().

    Attributes:
        is_open (bool): True if the window is open and should be processed
    """
    cdef Context ctx
    cdef str _title
    cdef Rect _rect
    cdef int _opt
    cdef public bint is_open

    def __cinit__(self, Context ctx, str title, Rect rect, int opt=0):
        """Initialize window context manager.

        Args:
            ctx (Context): The microui context
            title (str): Window title
            rect (Rect): Window rectangle (position and size)
            opt (int): Window options flags
        """
        self.ctx = ctx
        self._title = title
        self._rect = rect
        self._opt = opt
        self.is_open = False

    @property
    def title(self) -> str:
        """Get the window title."""
        return self._title

    @property
    def rect(self) -> Rect:
        """Get the window rectangle."""
        return self._rect

    @property
    def opt(self) -> int:
        """Get the window options."""
        return self._opt

    def __enter__(self):
        """Enter the window context - calls begin_window().

        Returns:
            Window: Returns self to allow access to is_open property
        """
        self.is_open = bool(self.ctx.begin_window(self._title, self._rect, self._opt))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the window context - calls end_window().

        This ensures end_window() is called even if an exception occurs.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            None: Does not suppress exceptions
        """
        if self.is_open:
            self.ctx.end_window()
        return None


# Container wrapper class
cdef class ContainerWrapper:
    cdef mu_Container* ptr
    
    def __cinit__(self):
        self.ptr = NULL
    
    @staticmethod
    cdef ContainerWrapper from_ptr(mu_Container* ptr):
        cdef ContainerWrapper wrapper = ContainerWrapper.__new__(ContainerWrapper)
        wrapper.ptr = ptr
        return wrapper
    
    @property
    def rect(self) -> Rect:
        if self.ptr == NULL:
            return Rect(0, 0, 0, 0)
        return Rect.from_c(self.ptr.rect)
    
    @property
    def body(self) -> Rect:
        if self.ptr == NULL:
            return Rect(0, 0, 0, 0)
        return Rect.from_c(self.ptr.body)
    
    @property
    def content_size(self) -> Vec2:
        if self.ptr == NULL:
            return Vec2(0, 0)
        return Vec2.from_c(self.ptr.content_size)
    
    @property
    def scroll(self) -> Vec2:
        if self.ptr == NULL:
            return Vec2(0, 0)
        return Vec2.from_c(self.ptr.scroll)
    
    @property
    def open(self) -> int:
        if self.ptr == NULL:
            return 0
        return self.ptr.open


# Command wrapper classes
cdef class BaseCommand:
    cdef mu_BaseCommand _cmd
    
    @staticmethod
    cdef BaseCommand from_c(mu_BaseCommand cmd):
        cdef BaseCommand result = BaseCommand.__new__(BaseCommand)
        result._cmd = cmd
        return result
    
    @property
    def type(self) -> int:
        return self._cmd.type
    
    @property
    def size(self) -> int:
        return self._cmd.size


cdef class RectCommand:
    cdef mu_RectCommand _cmd
    
    @staticmethod
    cdef RectCommand from_c(mu_RectCommand cmd):
        cdef RectCommand result = RectCommand.__new__(RectCommand)
        result._cmd = cmd
        return result
    
    @property
    def type(self) -> int:
        return self._cmd.base.type
    
    @property
    def rect(self) -> Rect:
        return Rect.from_c(self._cmd.rect)
    
    @property
    def color(self) -> Color:
        return Color.from_c(self._cmd.color)


cdef class TextCommand:
    cdef mu_TextCommand* _cmd
    
    @staticmethod
    cdef TextCommand from_c(mu_TextCommand cmd):
        cdef TextCommand result = TextCommand.__new__(TextCommand)
        # This won't work with flexible array members, use from_ptr instead
        raise NotImplementedError("Use from_ptr for TextCommand with flexible array members")
    
    @staticmethod
    cdef TextCommand from_ptr(mu_TextCommand* cmd):
        cdef TextCommand result = TextCommand.__new__(TextCommand)
        result._cmd = cmd
        return result
    
    @property
    def type(self) -> int:
        return self._cmd.base.type
    
    @property
    def font(self):
        return <object>self._cmd.font
    
    @property
    def pos(self) -> Vec2:
        return Vec2.from_c(self._cmd.pos)
    
    @property
    def color(self) -> Color:
        return Color.from_c(self._cmd.color)
    
    @property
    def text(self) -> str:
        cdef const char* str_ptr
        cdef int length
        cdef bytes py_bytes
        
        # Get the string pointer from the flexible array member
        # The str field is a flexible array member that points to the actual string data
        str_ptr = self._cmd.str
        if str_ptr == NULL:
            return ""
        
        # Convert C string to Python string
        try:
            # Use strlen to get the proper length
            length = strlen(str_ptr)
            if length == 0:
                return ""
            # Create a bytes object from the C string
            py_bytes = str_ptr[:length]
            return py_bytes.decode('utf-8', errors='replace')
        except Exception:
            return ""


cdef class IconCommand:
    cdef mu_IconCommand _cmd
    
    @staticmethod
    cdef IconCommand from_c(mu_IconCommand cmd):
        cdef IconCommand result = IconCommand.__new__(IconCommand)
        result._cmd = cmd
        return result
    
    @property
    def type(self) -> int:
        return self._cmd.base.type
    
    @property
    def rect(self) -> Rect:
        return Rect.from_c(self._cmd.rect)
    
    @property
    def icon_id(self) -> int:
        return self._cmd.id
    
    @property
    def color(self) -> Color:
        return Color.from_c(self._cmd.color)


cdef class ClipCommand:
    cdef mu_ClipCommand _cmd
    
    @staticmethod
    cdef ClipCommand from_c(mu_ClipCommand cmd):
        cdef ClipCommand result = ClipCommand.__new__(ClipCommand)
        result._cmd = cmd
        return result
    
    @property
    def type(self) -> int:
        return self._cmd.base.type
    
    @property
    def rect(self) -> Rect:
        return Rect.from_c(self._cmd.rect)


cdef class JumpCommand:
    cdef mu_JumpCommand _cmd
    
    @staticmethod
    cdef JumpCommand from_c(mu_JumpCommand cmd):
        cdef JumpCommand result = JumpCommand.__new__(JumpCommand)
        result._cmd = cmd
        return result
    
    @property
    def type(self) -> int:
        return self._cmd.base.type


# Constants for easy access
class Clip:
    PART = MU_CLIP_PART
    ALL = MU_CLIP_ALL

class Command:
    JUMP = MU_COMMAND_JUMP
    CLIP = MU_COMMAND_CLIP
    RECT = MU_COMMAND_RECT
    TEXT = MU_COMMAND_TEXT
    ICON = MU_COMMAND_ICON
    MAX = MU_COMMAND_MAX

class ColorIndex:
    TEXT = MU_COLOR_TEXT
    BORDER = MU_COLOR_BORDER
    WINDOWBG = MU_COLOR_WINDOWBG
    TITLEBG = MU_COLOR_TITLEBG
    TITLETEXT = MU_COLOR_TITLETEXT
    PANELBG = MU_COLOR_PANELBG
    BUTTON = MU_COLOR_BUTTON
    BUTTONHOVER = MU_COLOR_BUTTONHOVER
    BUTTONFOCUS = MU_COLOR_BUTTONFOCUS
    BASE = MU_COLOR_BASE
    BASEHOVER = MU_COLOR_BASEHOVER
    BASEFOCUS = MU_COLOR_BASEFOCUS
    SCROLLBASE = MU_COLOR_SCROLLBASE
    SCROLLTHUMB = MU_COLOR_SCROLLTHUMB
    MAX = MU_COLOR_MAX

class Icon:
    CLOSE = MU_ICON_CLOSE
    CHECK = MU_ICON_CHECK
    COLLAPSED = MU_ICON_COLLAPSED
    EXPANDED = MU_ICON_EXPANDED
    MAX = MU_ICON_MAX

class Result:
    ACTIVE = MU_RES_ACTIVE
    SUBMIT = MU_RES_SUBMIT
    CHANGE = MU_RES_CHANGE

class Option:
    ALIGNCENTER = MU_OPT_ALIGNCENTER
    ALIGNRIGHT = MU_OPT_ALIGNRIGHT
    NOINTERACT = MU_OPT_NOINTERACT
    NOFRAME = MU_OPT_NOFRAME
    NORESIZE = MU_OPT_NORESIZE
    NOSCROLL = MU_OPT_NOSCROLL
    NOCLOSE = MU_OPT_NOCLOSE
    NOTITLE = MU_OPT_NOTITLE
    HOLDFOCUS = MU_OPT_HOLDFOCUS
    AUTOSIZE = MU_OPT_AUTOSIZE
    POPUP = MU_OPT_POPUP
    CLOSED = MU_OPT_CLOSED
    EXPANDED = MU_OPT_EXPANDED

class Mouse:
    LEFT = MU_MOUSE_LEFT
    RIGHT = MU_MOUSE_RIGHT
    MIDDLE = MU_MOUSE_MIDDLE

class Key:
    SHIFT = MU_KEY_SHIFT
    CTRL = MU_KEY_CTRL
    ALT = MU_KEY_ALT
    BACKSPACE = MU_KEY_BACKSPACE
    RETURN = MU_KEY_RETURN


# Textbox class for persistent state
cdef class Textbox:
    """A persistent textbox widget with automatic memory management.

    This class provides a textbox that maintains its state between frames,
    including cursor position and selection. It handles memory allocation
    and cleanup automatically.

    Args:
        buffer_size (int, optional): Size of the internal buffer in bytes. Defaults to 128.
                                   Must be between 2 and 65536 bytes.

    Raises:
        ValueError: If buffer_size is invalid
        MemoryError: If memory allocation fails

    Example:
        >>> textbox = Textbox(256)
        >>> textbox.text = "Hello, World!"
        >>> result, new_text = textbox.update(ctx)
    """
    cdef char* buffer
    cdef int buffer_size
    cdef str current_text

    def __cinit__(self, int buffer_size=128):
        """Initialize the textbox with the specified buffer size.

        Args:
            buffer_size (int, optional): Buffer size in bytes. Defaults to 128.

        Raises:
            ValueError: If buffer_size is invalid
            MemoryError: If memory allocation fails
        """
        # Validate buffer size
        if buffer_size < 2:
            raise ValueError("Buffer size must be at least 2 bytes")
        if buffer_size > 65536:  # 64KB limit
            raise ValueError("Buffer size too large (max 64KB)")

        self.buffer_size = buffer_size
        self.buffer = <char*>malloc(buffer_size)
        if self.buffer == NULL:
            raise MemoryError("Failed to allocate textbox buffer")
        self.buffer[0] = 0  # null terminate
        self.current_text = ""
    
    def __dealloc__(self):
        if self.buffer != NULL:
            free(self.buffer)
            self.buffer = NULL
    
    def update(self, Context ctx, int opt=0) -> tuple:
        """Update the textbox and return (result, new_text).

        Args:
            ctx (Context): The microui context
            opt (int, optional): Textbox options flags. Defaults to 0.

        Returns:
            tuple: (result_flags, current_text)

        Raises:
            ValueError: If ctx is None
            RuntimeError: If buffer is corrupted
        """
        if ctx is None:
            raise ValueError("Context cannot be None")
        if self.buffer == NULL:
            raise RuntimeError("Textbox buffer is corrupted")

        cdef int result = mu_textbox_ex(ctx.ptr, self.buffer, self.buffer_size, opt)
        try:
            self.current_text = self.buffer.decode('utf-8', errors='replace')
        except Exception as e:
            # Fallback to empty string if decoding fails completely
            self.current_text = ""

        return (result, self.current_text)
    
    @property
    def text(self) -> str:
        return self.current_text
    
    @text.setter
    def text(self, str value):
        """Set the textbox content with enhanced memory safety.

        Args:
            value (str): The new text content

        Raises:
            ValueError: If the text is too long for the buffer
        """
        if value is None:
            value = ""

        cdef bytes b_value = value.encode('utf-8')
        cdef int encoded_len = len(b_value)
        cdef int copy_len

        # Validate buffer has space for at least null terminator
        if self.buffer_size < 1:
            raise ValueError("Buffer too small")

        # Calculate safe copy length with explicit bounds check
        copy_len = min(encoded_len, self.buffer_size - 1)
        if copy_len < 0:
            copy_len = 0

        # Only copy if we have valid data and space
        if copy_len > 0 and encoded_len > 0 and self.buffer != NULL:
            memcpy(self.buffer, <const char*>b_value, copy_len)

        # Always null terminate within buffer bounds
        if self.buffer != NULL and copy_len < self.buffer_size:
            self.buffer[copy_len] = 0

        # Update current text (potentially truncated)
        if copy_len < encoded_len:
            # Text was truncated, decode what actually fits
            self.current_text = self.buffer[:copy_len].decode('utf-8', errors='replace')
        else:
            self.current_text = value


# Renderer functions exposed as module-level functions
def renderer_init():
    """Initialize the renderer"""
    r_init()

def renderer_draw_rect(Rect rect, Color color):
    """Draw a rectangle"""
    r_draw_rect(rect.to_c(), color.to_c())

def renderer_draw_text(str text, Vec2 pos, Color color):
    """Draw text"""
    r_draw_text(text.encode(), pos.to_c(), color.to_c())

def renderer_draw_icon(int icon_id, Rect rect, Color color):
    """Draw an icon"""
    r_draw_icon(icon_id, rect.to_c(), color.to_c())

def renderer_get_text_width(str text, int length):
    """Get text width"""
    return r_get_text_width(text.encode(), length)

def renderer_get_text_height():
    """Get text height"""
    return r_get_text_height()

def renderer_set_clip_rect(Rect rect):
    """Set clipping rectangle"""
    r_set_clip_rect(rect.to_c())

def renderer_clear(Color color):
    """Clear the screen"""
    r_clear(color.to_c())

def renderer_present():
    """Present the rendered frame"""
    r_present()

