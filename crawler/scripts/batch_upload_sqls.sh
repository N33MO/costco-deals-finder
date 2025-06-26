#!/bin/bash

# Batch upload SQL files to Cloudflare D1 using the existing Node helper.
# -----------------------------------------------------------------------------
# This script finds all *.sql files in the backend/migrations/data directory
# (or a user-supplied directory) and pipes them one by one into
#   node src/processors/ingest_to_d1.js <file>
# which imports the statements directly to the production database.
#
# Usage:
#   From the costco-deals-finder/crawler/ directory:
#     ./scripts/batch_upload_sqls.sh            # default location
#     ./scripts/batch_upload_sqls.sh /path/to/sqls
#
# The script exits on the first failure to keep data consistent.
# -----------------------------------------------------------------------------

set -euo pipefail

# --- Resolve directories ------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."        # -> costco-deals-finder/crawler

# Default directory (relative to project root) unless user passes one
SQL_DIR="${1:-$PROJECT_ROOT/../backend/migrations/data}"

if [[ ! -d "$SQL_DIR" ]]; then
  echo "SQL directory not found: $SQL_DIR" >&2
  exit 1
fi

echo "Batch uploading SQL files from: $SQL_DIR"

# # Activate Python venv if present (ingest_to_d1.js relies on node only,
# # but other scripts in the pipeline may expect the venv)
# VENV_PATH="$PROJECT_ROOT/../../venv"
# if [[ -f "$VENV_PATH/bin/activate" ]]; then
#   source "$VENV_PATH/bin/activate"
# fi

# Process each .sql file (run in alphanumeric order)
shopt -s nullglob
SQL_FILES=("$SQL_DIR"/*.sql)

if [[ ${#SQL_FILES[@]} -eq 0 ]]; then
  echo "No .sql files found in $SQL_DIR" >&2
  exit 1
fi

for file in "${SQL_FILES[@]}"; do
  echo "---\nUploading $(basename "$file")"
  node "$PROJECT_ROOT/src/processors/ingest_to_d1.js" "$file"
  echo "Completed $(basename "$file")"
  echo "---"
done

echo "All SQL files uploaded successfully." 