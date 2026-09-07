# Changelog

## [Unreleased]

### Fixed
- Added OpenGL linking (`-lGL`) for Linux in `microui/sdl/CMakeLists.txt`
- Added `-fPIC` compile option to `microui` and `microui_sdl` libraries to support building shared libraries
- Updated `Makefile` to use `uv pip install -e .` for building, which properly integrates with scikit-build-core
- Added `install(TARGETS pymui DESTINATION pymui)` to `src/CMakeLists.txt`. Without an install rule scikit-build-core staged nothing, so `uv build` produced a wheel containing only the Python files: `import pymui` then failed with `No module named 'pymui.pymui'`. Every local workflow uses `uv pip install -e .`, whose redirecting finder points at the build tree, so the gap only appeared when CI installed the wheel itself.
