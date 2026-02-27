#!/usr/bin/env bash
# check_all.sh
# Compares actual test outputs against expected outputs using diff.
# Checks both ATF files and console output files.
#
# Usage: bash scripts/check_all.sh  (run after run_all.sh)
# Exit code 1 if any test fails, 0 if all pass.

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
  actual="$OUT_ATF_DIR/$base.atf"

  if [ ! -f "$actual" ]; then
    echo "  MISSING: $base.atf"
    fail=1
    continue
  fi

  if ! diff -u "$exp" "$actual" >/dev/null 2>&1; then
    echo "  FAIL: $base"
    diff -u "$exp" "$actual" || true
    fail=1
  else
    echo "  PASS: $base"
  fi
done

echo ""
echo "Checking console outputs..."
for exp in $(find "$EXP_CONSOLE_DIR" -type f | sort); do
  base="$(basename "$exp")"  # already includes .out extension
  actual="$OUT_CONSOLE_DIR/$base"

  if [ ! -f "$actual" ]; then
    echo "  MISSING: $base"
    fail=1
    continue
  fi

  if ! diff -u "$exp" "$actual" >/dev/null 2>&1; then
    echo "  FAIL: $base"
    diff -u "$exp" "$actual" || true
    fail=1
  else
    echo "  PASS: $base"
  fi
done

echo ""
if [ "$fail" -eq 0 ]; then
  echo "All output checks passed."
else
  echo "Some tests failed."
  exit 1
fi
