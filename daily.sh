#!/bin/bash
# What this script does:
#   1. Runs the Front End once per .txt file in input_dir, saving each
#      session's output as a separate .atf file.
#   2. Concatenates all .atf files into one Merged Daily Bank Account
#      Transaction File.
#   3. Runs the Back End with the merged file to produce a new Master
#      Bank Accounts File and a new Current Bank Accounts File.
# =============================================================================

set -euo pipefail

# Resolve paths relative to wherever this script lives
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SQA_DIR="$SCRIPT_DIR"

FRONTEND="$SQA_DIR/Phase3/bank-atm"
BACKEND="$SQA_DIR/Phase4/src/main.py"

# Arguments
CURRENT_ACCOUNTS="${1:?Usage: daily.sh <current_accounts_file> <master_accounts_file> <input_dir> <output_dir>}"
MASTER_ACCOUNTS="${2:?Usage: daily.sh <current_accounts_file> <master_accounts_file> <input_dir> <output_dir>}"
INPUT_DIR="${3:?Usage: daily.sh <current_accounts_file> <master_accounts_file> <input_dir> <output_dir>}"
OUTPUT_DIR="${4:?Usage: daily.sh <current_accounts_file> <master_accounts_file> <input_dir> <output_dir>}"

# Set up output sub-directories
ATF_DIR="$OUTPUT_DIR/atf_sessions"      # individual per-session .atf files
mkdir -p "$ATF_DIR"

MERGED_FILE="$OUTPUT_DIR/merged_transactions.atf"
NEW_MASTER="$OUTPUT_DIR/new_master_accounts.txt"
NEW_CURRENT="$OUTPUT_DIR/new_current_accounts.txt"


# Step 1 — Run the Front End for every session input file
echo "=== STEP 1: Running Front End sessions ==="

session_index=0
found_any=0

for input_file in "$INPUT_DIR"/*.txt; do
    [ -f "$input_file" ] || continue          # skip if no .txt files exist
    found_any=1
    base="$(basename "$input_file" .txt)"
    atf_out="$ATF_DIR/${session_index}_${base}.atf"

    echo "  Session $session_index: $base"
    "$FRONTEND" "$CURRENT_ACCOUNTS" "$atf_out" < "$input_file"

    session_index=$((session_index + 1))
done

if [ "$found_any" -eq 0 ]; then
    echo "ERROR: No .txt session files found in $INPUT_DIR"
    exit 1
fi

echo "  $session_index session(s) completed."

# Step 2 — Concatenate all .atf files into one Merged Transaction File

echo "=== STEP 2: Merging transaction files ==="

> "$MERGED_FILE"    # create/empty the merged file

for atf_file in "$ATF_DIR"/*.atf; do
    [ -f "$atf_file" ] || continue
    cat "$atf_file" >> "$MERGED_FILE"
done

echo "  Merged file written to: $MERGED_FILE"

# Step 3 — Run the Back End with the merged file

echo "=== STEP 3: Running Back End ==="

python3 "$BACKEND" "$MASTER_ACCOUNTS" "$MERGED_FILE" "$NEW_MASTER"

echo "  New master accounts written to: $NEW_MASTER"


# Step 4 — Derive the new Current Accounts File from the new Master
#           (strip the transaction-count and plan fields so the Front End
#            can read it in its simpler fixed-width format)

echo "=== STEP 4: Generating new Current Accounts File ==="

while IFS= read -r line; do
    # Pass the END_OF_FILE sentinel through unchanged
    if echo "$line" | grep -q "END_OF_FILE"; then
        echo "$line" >> "$NEW_CURRENT"
        continue
    fi
    # Extract fields: acct(5) + space + name(20) + space + status(1) + space + balance(8)
    # That is columns 0-33 of the master record (positions 0..33 inclusive = 34 chars)
    printf '%s\n' "${line:0:34}" >> "$NEW_CURRENT"
done < "$NEW_MASTER"

echo "  New current accounts written to: $NEW_CURRENT"
echo "=== Daily run complete ==="
