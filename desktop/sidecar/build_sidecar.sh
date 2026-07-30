#!/usr/bin/env bash
# Build sidecar as single-file binary via PyInstaller.
# Usage: ./build_sidecar.sh [target_triple]
# Example: ./build_sidecar.sh x86_64-pc-windows-msvc

set -euo pipefail

cd "$(dirname "$0")"

TARGET_TRIPLE="${1:-}"
OUT_NAME="sidecar"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$TARGET_TRIPLE" == *"windows"* ]]; then
    OUT_NAME="sidecar.exe"
fi

pip install pyinstaller==6.*

pyinstaller \
    --onefile \
    --name sidecar \
    --distpath dist \
    --workpath build \
    --noconfirm \
    src/server.py

echo "✓ Built: dist/${OUT_NAME}"
ls -la dist/
