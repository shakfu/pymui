.phony: all build clean demo test test-all test-safe memory-test performance-test

all: build


build: clean
	@mkdir -p build && cd build && \
		cmake .. && \
		cmake --build . --config Release

clean:
	@rm -rf build src/pymui/pymui.*.so
	@find . -type d -name __pycache__ -exec rm -rf {} \; -prune
	@find . -type d -path ".*_cache"  -exec rm -rf {} \; -prune

demo:
	@uv run python tests/pymui_sdl_demo.py

test:
	@uv run pytest

test-safe:
	@echo "Running only safe tests (no UI context operations)..."
	@uv run pytest tests/test_pymui.py tests/test_property_minimal.py tests/test_memory_safety.py tests/test_context_manager.py tests/test_window_context_manager.py

test-all:
	@echo "Running ALL tests (including potentially unstable UI context tests)..."
	@uv run pytest --ignore=none

memory-test:
	@echo "Running memory leak detection..."
	@uv run python scripts/memory_leak_test.py --verbose

performance-test:
	@echo "Running performance benchmarks..."
	@uv run python scripts/benchmark.py
