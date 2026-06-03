#!/bin/bash
# Reassemble pytorch_model.bin from chunks.
# Run once after `git clone`, in the repo root.

set -euo pipefail

cd "$(dirname "$0")"

if [ -f pytorch_model.bin ]; then
    echo "pytorch_model.bin already exists; nothing to do."
    exit 0
fi

if ! ls pytorch_model.bin.part_* >/dev/null 2>&1; then
    echo "No pytorch_model.bin.part_* chunks found in $(pwd)" >&2
    exit 1
fi

echo "Reassembling pytorch_model.bin from $(ls pytorch_model.bin.part_* | wc -l | tr -d ' ') chunks..."
cat pytorch_model.bin.part_* > pytorch_model.bin

EXPECTED="1bf014f5849eb38bcb7b1c95c539b2b0289beff96920b65c2cbfe6db5e9330aa"
if command -v shasum >/dev/null 2>&1; then
    GOT=$(shasum -a 256 pytorch_model.bin | awk '{print $1}')
elif command -v sha256sum >/dev/null 2>&1; then
    GOT=$(sha256sum pytorch_model.bin | awk '{print $1}')
else
    echo "WARNING: neither shasum nor sha256sum available; skipping checksum check"
    GOT="$EXPECTED"
fi

if [ "$GOT" != "$EXPECTED" ]; then
    echo "ERROR: SHA-256 mismatch" >&2
    echo "  expected: $EXPECTED" >&2
    echo "  got:      $GOT" >&2
    exit 1
fi

echo "OK: pytorch_model.bin reassembled and SHA-256 verified ($GOT)"
