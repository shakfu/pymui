#!/usr/bin/env bash
# Build static SDL2 into build/sdl2 for wheel builds (cibuildwheel before-all).
# Linking SDL2 statically keeps one SDL instance per process and leaves the
# wheel repair tools nothing to vendor.
set -euo pipefail

VERSION=2.32.10
SHA256=5f5993c530f084535c65a6879e9b26ad441169b3e25d789d83287040a9ca5165
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PREFIX="$ROOT/build/sdl2"
WORK="$ROOT/build/sdl2-src"

mkdir -p "$WORK"
cd "$WORK"
curl -fsSL -o sdl2.tar.gz \
    "https://github.com/libsdl-org/SDL/releases/download/release-$VERSION/SDL2-$VERSION.tar.gz"
if command -v sha256sum >/dev/null; then
    echo "$SHA256  sdl2.tar.gz" | sha256sum -c -
else
    echo "$SHA256  sdl2.tar.gz" | shasum -a 256 -c -
fi
tar xzf sdl2.tar.gz

cmake -S "SDL2-$VERSION" -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$PREFIX" \
    -DCMAKE_OSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-11.0}" \
    -DSDL_SHARED=OFF \
    -DSDL_STATIC=ON \
    -DSDL_STATIC_PIC=ON \
    -DSDL_TEST=OFF \
    -DSDL_WAYLAND=OFF
cmake --build build --config Release --parallel
cmake --install build --config Release
