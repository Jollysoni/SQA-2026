#!/usr/bin/env bash
set -euo pipefail
EXP_DIR="${1:?expected directory required}"
OUT_DIR="${2:?output directory required}"

for exp in "$EXP_DIR"/*.txt; do
  base="$(basename "$exp" .txt)"
  diff -u "$exp" "$OUT_DIR/$base.atf"
done
