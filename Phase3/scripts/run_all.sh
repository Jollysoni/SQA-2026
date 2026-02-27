#!/usr/bin/env bash
# run_all.sh
# Runs the bank-atm program on every test input file and saves both the
# ATF output and console output for later comparison.
#
# Usage: bash scripts/run_all.sh
# Run check_all.sh afterward to validate results.

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
  safe="${rel//\//__}"

  echo "Running test: $rel"

  # Feed the input file into the ATM program, capture ATF and console output separately
  "$ATM" "$ACCOUNTS" "$OUT_ATF_DIR/$safe.atf" \
    < "$infile" \
    > "$OUT_CONSOLE_DIR/$safe.out" 2>&1

done < <(find "$INPUT_DIR" -type f | sort)

if [ "$found_any" -eq 0 ]; then
  echo "No test input files found under: $INPUT_DIR"
  exit 1
fi

echo "All tests executed."
