#!/bin/bash

# Batch convert all savings_*.ndjson and hotbuys_*.ndjson files in data/processed/ to .sql using convert_deals_to_sql.py
# Usage: ./batch_convert_ndjson_to_sql.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."
PROCESSED_DIR="$PROJECT_ROOT/crawler/data/processed"
CONVERTER_SCRIPT="$PROJECT_ROOT/crawler/src/processors/convert_deals_to_sql.py"
VENV_PATH="$PROJECT_ROOT/venv"

# --- Environment Setup ---
# The Python virtual environment should be at the project root.
# From this script's location (after cd), that's two levels up.
VENV_PATH="../../venv"
if [ -f "$VENV_PATH/bin/activate" ]; then
  echo "Activating Python virtual environment from $VENV_PATH..."
  source "$VENV_PATH/bin/activate"
else
  echo "Warning: Virtual environment not found at $VENV_PATH. Using system Python."
  echo "This may cause ModuleNotFound errors if dependencies are not installed globally."
fi

cd "$PROCESSED_DIR"

FILES=(savings_*.ndjson hotbuys_*.ndjson)
TOTAL=0
CONVERTED=0
SKIPPED=0

for NDJSON in "${FILES[@]}"; do
  # Skip if file does not exist (globs may not match)
  [ -e "$NDJSON" ] || continue
  ((TOTAL++))
  BASENAME="${NDJSON%.ndjson}"
  SQL_FILE="../sqls/$BASENAME.sql"
  if [ -f "$SQL_FILE" ]; then
    echo "[SKIP] $NDJSON → $SQL_FILE already exists."
    ((SKIPPED++))
    continue
  fi
  echo "[CONVERT] $NDJSON → $SQL_FILE"
  python3 "$CONVERTER_SCRIPT" --file "$NDJSON" --sql-out "$SQL_FILE" --ignore-unavailable
  if [ $? -eq 0 ]; then
    ((CONVERTED++))
  else
    echo "[ERROR] Failed to convert $NDJSON"
  fi
done

echo "---"
echo "Batch conversion complete."
echo "Total files found: $TOTAL"
echo "Converted: $CONVERTED"
echo "Skipped (already had .sql): $SKIPPED" 