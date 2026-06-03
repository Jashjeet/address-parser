"""Reassemble pytorch_model.bin from chunks.

Cross-platform (Linux/macOS/Windows). Run once after `git clone` in the repo root:
    python reassemble.py
"""
import glob
import hashlib
import os
import sys

EXPECTED_SHA256 = "1bf014f5849eb38bcb7b1c95c539b2b0289beff96920b65c2cbfe6db5e9330aa"
TARGET = "pytorch_model.bin"


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    os.chdir(here)

    if os.path.exists(TARGET):
        print(f"{TARGET} already exists; nothing to do.")
        return 0

    parts = sorted(glob.glob("pytorch_model.bin.part_*"))
    if not parts:
        print(f"No pytorch_model.bin.part_* chunks found in {here}", file=sys.stderr)
        return 1

    print(f"Reassembling {TARGET} from {len(parts)} chunks...")
    h = hashlib.sha256()
    with open(TARGET, "wb") as out:
        for p in parts:
            with open(p, "rb") as f:
                while True:
                    chunk = f.read(1 << 20)
                    if not chunk:
                        break
                    out.write(chunk)
                    h.update(chunk)

    got = h.hexdigest()
    if got != EXPECTED_SHA256:
        print("ERROR: SHA-256 mismatch", file=sys.stderr)
        print(f"  expected: {EXPECTED_SHA256}", file=sys.stderr)
        print(f"  got:      {got}", file=sys.stderr)
        return 1

    print(f"OK: {TARGET} reassembled and SHA-256 verified ({got})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
