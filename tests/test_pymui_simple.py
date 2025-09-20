#!/usr/bin/env python3
"""
Simplified Python version of the microui demo using pymui
This version doesn't require SDL2 and just prints UI commands for testing
"""

import sys
from pymui import Context, Rect, Color, Vec2, Option, Result, Mouse, Key, ColorIndex


class MockRenderer:
    """Mock renderer that just prints commands for testing"""
    
    def __init__(self):
        self.font_width = 8
        self.font_height = 12
    
    def get_text_width(self, text, length=-1):
        """Get text width"""
        if length == -1:
            length = len(text)
        return length * self.font_width
    
    def get_text_height(self):
        """Get text height"""
        return self.font_height


class Demo:
    """Main demo application"""
    
    def __init__(self):
        # Initialize microui context
        self.ctx = Context()
        
        # Set up text rendering callbacks
        self.renderer = MockRenderer()
        # self.ctx.text_width = self.text_width
        # self.ctx.text_height = self.text_height
        
        # Demo state
        self.logbuf = ""
        self.logbuf_updated = False
        self.bg = [90.0, 95.0, 100.0]  # Use floats for sliders
        self.input_buf = ""
        
        # Track commands for testing
        self.commands = []
    
    # def text_width(self, font, text, length=-1):
    #     """Text width callback"""
    #     if length == -1:
    #         length = len(text)
    #     return self.renderer.get_text_width(text, length)
    
    # def text_height(self, font):
    #     """Text height callback"""
    #     return self.renderer.get_text_height()
    
    def write_log(self, text):
        """Write text to log buffer"""
        if self.logbuf:
            self.logbuf += "\n"
        self.logbuf += text
        self.logbuf_updated = True
        print(f"LOG: {text}")
    
    def test_window(self):
        """Create the main demo window"""
        if self.ctx.begin_window("Demo Window", Rect(40, 40, 300, 450)):
            print("Created Demo Window")
            
            # Window info
            if self.ctx.header("Window Info"):
                print("  Window Info header expanded")
            
            # Test buttons
            if self.ctx.header("Test Buttons", Option.EXPANDED):
                print("  Test Buttons header expanded")
                
                # Note: layout_row is commented out in pymui, so we'll use layout_width/height
                self.ctx.layout_width(86)
                self.ctx.label("Test buttons 1:")
                self.ctx.layout_width(-110)
                if self.ctx.button("Button 1"):
                    self.write_log("Pressed button 1")
                self.ctx.layout_width(-1)
                if self.ctx.button("Button 2"):
                    self.write_log("Pressed button 2")
                
                self.ctx.layout_width(86)
                self.ctx.label("Test buttons 2:")
                self.ctx.layout_width(-110)
                if self.ctx.button("Button 3"):
                    self.write_log("Pressed button 3")
                self.ctx.layout_width(-1)
                if self.ctx.button("Popup"):
                    self.ctx.open_popup("Test Popup")
                
                if self.ctx.begin_popup("Test Popup"):
                    self.ctx.button("Hello")
                    self.ctx.button("World")
                    self.ctx.end_popup()
            
            # Tree and text
            if self.ctx.header("Tree and Text", Option.EXPANDED):
                print("  Tree and Text header expanded")
                
                # Left column - tree
                self.ctx.layout_begin_column()
                self.ctx.layout_width(140)
                
                if self.ctx.begin_treenode("Test 1"):
                    print("    Tree node 'Test 1' expanded")
                    if self.ctx.begin_treenode("Test 1a"):
                        print("      Tree node 'Test 1a' expanded")
                        self.ctx.label("Hello")
                        self.ctx.label("world")
                        self.ctx.end_treenode()
                    if self.ctx.begin_treenode("Test 1b"):
                        print("      Tree node 'Test 1b' expanded")
                        if self.ctx.button("Button 1"):
                            self.write_log("Pressed button 1")
                        if self.ctx.button("Button 2"):
                            self.write_log("Pressed button 2")
                        self.ctx.end_treenode()
                    self.ctx.end_treenode()
                
                if self.ctx.begin_treenode("Test 2"):
                    print("    Tree node 'Test 2' expanded")
                    self.ctx.layout_width(54)
                    if self.ctx.button("Button 3"):
                        self.write_log("Pressed button 3")
                    self.ctx.layout_width(54)
                    if self.ctx.button("Button 4"):
                        self.write_log("Pressed button 4")
                    self.ctx.layout_width(54)
                    if self.ctx.button("Button 5"):
                        self.write_log("Pressed button 5")
                    self.ctx.layout_width(54)
                    if self.ctx.button("Button 6"):
                        self.write_log("Pressed button 6")
                    self.ctx.end_treenode()
                
                if self.ctx.begin_treenode("Test 3"):
                    print("    Tree node 'Test 3' expanded")
                    checks = [1, 0, 1]  # Static state
                    self.ctx.checkbox("Checkbox 1", checks[0])
                    self.ctx.checkbox("Checkbox 2", checks[1])
                    self.ctx.checkbox("Checkbox 3", checks[2])
                    self.ctx.end_treenode()
                
                self.ctx.layout_end_column()
                
                # Right column - text
                self.ctx.layout_begin_column()
                self.ctx.layout_width(-1)
                self.ctx.text("Lorem ipsum dolor sit amet, consectetur adipiscing "
                            "elit. Maecenas lacinia, sem eu lacinia molestie, mi risus faucibus "
                            "ipsum, eu varius magna felis a nulla.")
                self.ctx.layout_end_column()
            
            # Background color sliders
            if self.ctx.header("Background Color", Option.EXPANDED):
                print("  Background Color header expanded")
                
                # Sliders
                self.ctx.layout_begin_column()
                self.ctx.layout_width(46)
                self.ctx.label("Red:")
                self.ctx.layout_width(-1)
                self.ctx.slider(self.bg[0], 0, 255)
                
                self.ctx.layout_width(46)
                self.ctx.label("Green:")
                self.ctx.layout_width(-1)
                self.ctx.slider(self.bg[1], 0, 255)
                
                self.ctx.layout_width(46)
                self.ctx.label("Blue:")
                self.ctx.layout_width(-1)
                self.ctx.slider(self.bg[2], 0, 255)
                self.ctx.layout_end_column()
                
                # Color preview
                r = self.ctx.layout_next()
                self.ctx.draw_rect(r, Color(int(self.bg[0]), int(self.bg[1]), int(self.bg[2]), 255))
                color_text = f"#{int(self.bg[0]):02X}{int(self.bg[1]):02X}{int(self.bg[2]):02X}"
                print(f"    Color preview: {color_text}")
            
            self.ctx.end_window()
    
    def log_window(self):
        """Create the log window"""
        if self.ctx.begin_window("Log Window", Rect(350, 40, 300, 200)):
            print("Created Log Window")
            
            # Output text panel
            self.ctx.layout_height(-25)
            self.ctx.begin_panel("Log Output")
            self.ctx.layout_height(-1)
            self.ctx.text(self.logbuf)
            self.ctx.end_panel()
            
            # Input textbox + submit button
            submitted = False
            self.ctx.layout_width(-70)
            
            # Note: textbox handling is simplified here
            result = self.ctx.textbox(self.input_buf, 128)
            if result & Result.SUBMIT:
                submitted = True
            
            self.ctx.layout_width(-1)
            if self.ctx.button("Submit"):
                submitted = True
            
            if submitted and self.input_buf:
                self.write_log(self.input_buf)
                self.input_buf = ""
            
            self.ctx.end_window()
    
    def style_window(self):
        """Create the style editor window"""
        colors = [
            ("text:", ColorIndex.TEXT),
            ("border:", ColorIndex.BORDER),
            ("windowbg:", ColorIndex.WINDOWBG),
            ("titlebg:", ColorIndex.TITLEBG),
            ("titletext:", ColorIndex.TITLETEXT),
            ("panelbg:", ColorIndex.PANELBG),
            ("button:", ColorIndex.BUTTON),
            ("buttonhover:", ColorIndex.BUTTONHOVER),
            ("buttonfocus:", ColorIndex.BUTTONFOCUS),
            ("base:", ColorIndex.BASE),
            ("basehover:", ColorIndex.BASEHOVER),
            ("basefocus:", ColorIndex.BASEFOCUS),
            ("scrollbase:", ColorIndex.SCROLLBASE),
            ("scrollthumb:", ColorIndex.SCROLLTHUMB),
        ]
        
        if self.ctx.begin_window("Style Editor", Rect(350, 250, 300, 240)):
            print("Created Style Editor Window")
            
            # Note: get_current_container is not available, so we'll use a fixed width
            sw = 40  # Fixed width for sliders
            
            for label, color_idx in colors:
                self.ctx.layout_width(80)
                self.ctx.label(label)
                color = self.ctx.style.get_color(color_idx)
                
                # Create sliders for RGBA values
                self.ctx.layout_width(sw)
                self.ctx.slider(float(color.r), 0, 255)
                self.ctx.layout_width(sw)
                self.ctx.slider(float(color.g), 0, 255)
                self.ctx.layout_width(sw)
                self.ctx.slider(float(color.b), 0, 255)
                self.ctx.layout_width(sw)
                self.ctx.slider(float(color.a), 0, 255)
                
                self.ctx.layout_width(-1)
                self.ctx.draw_rect(self.ctx.layout_next(), color)
            
            self.ctx.end_window()
    
    def process_frame(self):
        """Process one frame of the UI"""
        print("\n--- Processing Frame ---")
        self.ctx.begin()
        self.style_window()
        self.log_window()
        self.test_window()
        self.ctx.end()
        print("--- Frame Complete ---\n")
    
    def run(self):
        """Main application loop - simplified for testing"""
        print("Starting PyMUI Demo (Mock Renderer)")
        print("This demo shows the UI structure without actual rendering")
        
        # Process a few frames to show the UI
        for i in range(3):
            print(f"\nFrame {i + 1}:")
            self.process_frame()
        
        print("\nDemo completed successfully!")
        print("To see the actual UI, run demo_python.py with SDL2 support")


def test_demo():
    """Main entry point"""
    try:
        demo = Demo()
        demo.run()
        assert True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        assert False

def main():
    """Main entry point"""
    try:
        demo = Demo()
        demo.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 