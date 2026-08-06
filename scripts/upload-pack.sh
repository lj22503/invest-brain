#!/usr/bin/env bash
# Upload a knowledge pack to Vercel Blob.
# Usage: ./upload-pack.sh <pack_id> <pack_dir>
#
# Requires:
#   - vercel CLI logged in
#   - BLOB_READ_WRITE_TOKEN env var (Vercel Storage token)
#
# 输出末尾会提示需要设置的环境变量名 + 占位 URL，便于后续在 Vercel dashboard 替换。

set -euo pipefail

PACK_ID="${1:-}"
PACK_DIR="${2:-}"

if [[ -z "$PACK_ID" || -z "$PACK_DIR" ]]; then
    echo "Usage: $0 <pack_id> <pack_dir>"
    exit 1
fi

if [[ ! -d "$PACK_DIR" ]]; then
    echo "Pack dir not found: $PACK_DIR"
    exit 1
fi

if [[ -z "${BLOB_READ_WRITE_TOKEN:-}" ]]; then
    echo "BLOB_READ_WRITE_TOKEN required (Vercel Storage token)"
    exit 1
fi

# 版本号：UTC 时间戳，YYYY.MM.DD.HHMM（冒号不可用）
VERSION=$(date -u +%Y.%m.%d.%H%M)

# 上传 manifest
echo "Uploading manifest..."
vercel blob put \
    --token "$BLOB_READ_WRITE_TOKEN" \
    "${PACK_DIR}/manifest.json" \
    "investbrain/packs/${PACK_ID}/${VERSION}/manifest.json"

# 上传 content_files 列表中的所有 JSON
if command -v jq >/dev/null 2>&1; then
    mapfile -t CONTENT_FILES < <(jq -r '.content_files[]?' "${PACK_DIR}/manifest.json" 2>/dev/null || true)
    if [[ ${#CONTENT_FILES[@]} -gt 0 ]]; then
        echo "Uploading ${#CONTENT_FILES[@]} content file(s)..."
        for f in "${CONTENT_FILES[@]}"; do
            src="${PACK_DIR}/${f}"
            if [[ -f "$src" ]]; then
                vercel blob put \
                    --token "$BLOB_READ_WRITE_TOKEN" \
                    "$src" \
                    "investbrain/packs/${PACK_ID}/${VERSION}/${f}"
            else
                echo "  skip (missing): $src"
            fi
        done
    fi
else
    echo "(jq not installed, skipping content_files upload — upload them manually if needed)"
fi

echo ""
echo "✓ Pack uploaded: ${PACK_ID} v${VERSION}"
echo ""
echo "Next step: set env var in Vercel project:"
echo "  PACK_${PACK_ID^^}_BLOB_URL=https://<public-blob-host>/investbrain/packs/${PACK_ID}/${VERSION}/manifest.json"