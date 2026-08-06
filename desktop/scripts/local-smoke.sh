#!/usr/bin/env bash
# desktop/scripts/local-smoke.sh
# Local dev: build sidecar → spawn → health check → kill
# 退出码：0 = pass / 非零 = fail

set -euo pipefail

cd "$(dirname "$0")/.."

echo "→ Building sidecar..."
bash sidecar/build_sidecar.sh

# 平台相关的二进制名
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    SIDECAR_BIN="sidecar/dist/sidecar.exe"
else
    SIDECAR_BIN="sidecar/dist/sidecar"
fi

if [[ ! -f "$SIDECAR_BIN" ]]; then
    echo "✗ sidecar binary not found at $SIDECAR_BIN"
    exit 1
fi

# Spawn
PORT="${PORT:-8765}"
SIDECAR_PORT="$PORT" "$SIDECAR_BIN" &
SIDECAR_PID=$!

cleanup() {
    kill "$SIDECAR_PID" 2>/dev/null || true
    wait "$SIDECAR_PID" 2>/dev/null || true
}
trap cleanup EXIT

# 等 ready
sleep 1

echo "→ Health check at http://127.0.0.1:$PORT/health"
RESP=$(curl -sf "http://127.0.0.1:$PORT/health")

if echo "$RESP" | grep -q '"status":"ok"'; then
    echo "✓ Sidecar healthy: $RESP"
    exit 0
else
    echo "✗ Unexpected response: $RESP"
    exit 1
fi