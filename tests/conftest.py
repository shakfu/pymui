"""
Pytest configuration and fixtures for pymui tests.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
ROOTDIR = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(ROOTDIR))

try:
    from pymui import pymui
except ImportError:
    import pymui


@pytest.fixture
def ctx():
    """Provide a pymui Context instance for tests."""
    context = pymui.Context()
    return context


@pytest.fixture
def clean_ctx():
    """Provide a fresh pymui Context for each test that needs isolation."""
    context = pymui.Context()
    yield context
    # Context cleanup happens automatically via __dealloc__