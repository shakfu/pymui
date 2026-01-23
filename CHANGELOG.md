# Changelog

## [Unreleased]

### Fixed
- Added OpenGL linking (`-lGL`) for Linux in `microui/sdl/CMakeLists.txt`
- Added `-fPIC` compile option to `microui` and `microui_sdl` libraries to support building shared libraries
- Updated `Makefile` to use `uv pip install -e .` for building, which properly integrates with scikit-build-core
