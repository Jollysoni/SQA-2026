#!/usr/bin/env bash
set -euo pipefail
FE="${1:?front-end executable required}"
ACCTS="${2:?current accounts file required}"
IN_DIR="${3:?input directory required}"
OUT_DIR="${4:?output directory required}"

mkdir -p "$OUT_DIR"
for f in "$IN_DIR"/*.txt; do
  base="$(basename "$f" .txt)"
  "$FE" "$ACCTS" "$OUT_DIR/$base.atf" < "$f" > "$OUT_DIR/$base.out"
done
