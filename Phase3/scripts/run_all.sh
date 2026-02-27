#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ATM="$ROOT_DIR/bank-atm"

ACCOUNTS="$ROOT_DIR/tests/currentaccounts.txt"
INPUT_DIR="$ROOT_DIR/tests/inputs"
OUT_ATF_DIR="$ROOT_DIR/tests/outputs/atf"
OUT_CONSOLE_DIR="$ROOT_DIR/tests/outputs/console"

mkdir -p "$OUT_ATF_DIR" "$OUT_CONSOLE_DIR"

found_any=0

while IFS= read -r infile; do
  found_any=1
  rel="${infile#$INPUT_DIR/}"
  safe="${rel//\//__}"   # keep unique names even with subfolders

  echo "Running test $rel"

  "$ATM" "$ACCOUNTS" "$OUT_ATF_DIR/$safe.atf" \
    < "$infile" \
    > "$OUT_CONSOLE_DIR/$safe.out" 2>&1

done < <(find "$INPUT_DIR" -type f | sort)

if [ "$found_any" -eq 0 ]; then
  echo "No test input files found under: $INPUT_DIR"
  exit 1
fi

echo "All tests executed."
