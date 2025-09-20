#!/usr/bin/env python3

import sys

try:
    from pymui import pymui
    print("pymui imported successfully")

    # Test basic objects
    ctx = pymui.Context()
    print("Context created successfully")

    rect = pymui.rect(10, 10, 100, 100)
    print(f"Rect created: {rect}")

    color = pymui.color(255, 0, 0)
    print(f"Color created: {color}")

    # Test renderer init
    pymui.renderer_init()
    print("Renderer initialized successfully")

    print("All basic tests passed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)