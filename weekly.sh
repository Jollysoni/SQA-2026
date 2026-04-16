
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SQA_DIR="$SCRIPT_DIR"

DAILY_SCRIPT="$SCRIPT_DIR/daily.sh"

# Source files — these are the INITIAL files for Day 1
INITIAL_CURRENT="$SQA_DIR/Phase3/tests/currentaccounts.txt"
INITIAL_MASTER="$SQA_DIR/Phase4/tests/old_master_accounts.txt"

# All available session input files
ALL_INPUTS_DIR="$SQA_DIR/Phase3/tests/inputs"

# Weekly output root
WEEKLY_OUT="$SCRIPT_DIR/weekly_output"
mkdir -p "$WEEKLY_OUT"

# Check if per-day sub-folders already exist
USE_SUBDIRS=0
for d in 1 2 3 4 5 6 7; do
    if [ -d "$ALL_INPUTS_DIR/day$d" ]; then
        USE_SUBDIRS=1
        break
    fi
done

if [ "$USE_SUBDIRS" -eq 0 ]; then
    echo "No day sub-folders found — splitting input files across 7 days automatically."

    # Collect all input files into an array
    input_files=()
    for f in "$ALL_INPUTS_DIR"/*.txt; do
        [ -f "$f" ] && input_files+=("$f")
    done

    total=${#input_files[@]}
    if [ "$total" -eq 0 ]; then
        echo "ERROR: No .txt session files found in $ALL_INPUTS_DIR"
        exit 1
    fi

    # Create day sub-folders and distribute files round-robin
    for d in 1 2 3 4 5 6 7; do
        mkdir -p "$ALL_INPUTS_DIR/day$d"
    done

    idx=0
    for f in "${input_files[@]}"; do
        day=$(( (idx % 7) + 1 ))
        cp "$f" "$ALL_INPUTS_DIR/day$day/"
        idx=$((idx + 1))
    done

    echo "  $total file(s) distributed across 7 day folders."
fi


# Run daily.sh seven times, feeding outputs into the next day
current_accounts="$INITIAL_CURRENT"
master_accounts="$INITIAL_MASTER"

for day in 1 2 3 4 5 6 7; do
    echo ""
    echo "============================================================"
    echo "  WEEK DAY $day"
    echo "============================================================"

    day_input_dir="$ALL_INPUTS_DIR/day$day"
    day_output_dir="$WEEKLY_OUT/day$day"
    mkdir -p "$day_output_dir"

    # Run the daily script for this day
    bash "$DAILY_SCRIPT" \
        "$current_accounts" \
        "$master_accounts" \
        "$day_input_dir" \
        "$day_output_dir"

    # The outputs of this day become the inputs for the next day
    current_accounts="$day_output_dir/new_current_accounts.txt"
    master_accounts="$day_output_dir/new_master_accounts.txt"

    echo "  Day $day complete."
    echo "  Current accounts for next day: $current_accounts"
    echo "  Master accounts for next day:  $master_accounts"
done

echo ""
echo "============================================================"
echo "  WEEKLY RUN COMPLETE"
echo "  Final master accounts: $master_accounts"
echo "  Final current accounts: $current_accounts"
echo "============================================================"
