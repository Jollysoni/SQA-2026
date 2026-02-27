#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

EXP_ATF_DIR="$ROOT_DIR/tests/expected/atf"
EXP_CONSOLE_DIR="$ROOT_DIR/tests/expected/console"

OUT_ATF_DIR="$ROOT_DIR/tests/outputs/atf"
OUT_CONSOLE_DIR="$ROOT_DIR/tests/outputs/console"

fail=0

echo "Checking ATF outputs..."
for exp in $(find "$EXP_ATF_DIR" -type f | sort); do
  base="$(basename "$exp")"
  if [ ! -f "$OUT_ATF_DIR/$base.atf" ]; then
    echo "Missing actual ATF: $base.atf"
    fail=1
    continue
  fi
  if ! diff -u "$exp" "$OUT_ATF_DIR/$base.atf" >/dev/null; then
    echo "ATF MISMATCH: $base"
    diff -u "$exp" "$OUT_ATF_DIR/$base.atf" || true
    fail=1
  fi
done

echo "Checking console outputs..."
for exp in $(find "$EXP_CONSOLE_DIR" -type f | sort); do
  base="$(basename "$exp")"   # base already includes .out
  if [ ! -f "$OUT_CONSOLE_DIR/$base" ]; then
    echo "Missing actual console: $base"
    fail=1
    continue
  fi
  if ! diff -u "$exp" "$OUT_CONSOLE_DIR/$base" >/dev/null; then
    echo "CONSOLE MISMATCH: $base"
    diff -u "$exp" "$OUT_CONSOLE_DIR/$base" || true
    fail=1
  fi
done

if [ "$fail" -eq 0 ]; then
  echo "All output checks passed."
else
  echo "Some tests failed output comparison."
  exit 1
fi
