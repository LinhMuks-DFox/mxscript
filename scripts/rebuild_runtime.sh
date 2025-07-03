#!/usr/bin/env bash
set -e
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/runtime/build"
BIN_DIR="$ROOT_DIR/bin"

rm -rf "$BUILD_DIR" "$BIN_DIR/libruntime.so"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
cmake ..
cmake --build .

