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

# Tauri externalBin 要求产物命名为 <name>-<target-triple>.exe（相对 src-tauri）。
# externalBin 配置为不带扩展名的 "sidecar"，Windows 下对应文件为 sidecar-<triple>.exe
if [[ -n "$TARGET_TRIPLE" ]]; then
    TRIPLED_NAME="sidecar-${TARGET_TRIPLE}"
    if [[ "$TARGET_TRIPLE" == *"windows"* ]]; then
        TRIPLED_NAME="${TRIPLED_NAME}.exe"
    fi
    cp "dist/${OUT_NAME}" "dist/${TRIPLED_NAME}"
    echo "✓ Tripled for Tauri externalBin: dist/${TRIPLED_NAME}"
fi
