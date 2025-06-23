#!/bin/bash

# A script to run the full data processing pipeline for Costco deals.
# It extracts data from a local HTML file and ingests it to BOTH the
# local development environment (via API) and the production D1 database (via direct SQL import).
#
# Usage:
#   From the crawler/ directory:
#   ./scripts/run_pipeline.sh <path_to_html_file>
#
# Example:
#   ./scripts/run_pipeline.sh data/raw/savings_122624_012025.html

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Preamble ---
# Get the directory of the script to ensure paths are correct, then cd to crawler/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd "$SCRIPT_DIR/.."

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

# --- Argument Parsing ---
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_html_file>"
  echo "Example: $0 data/raw/savings_122624_012025.html"
  exit 1
fi

HTML_FILE=$1

echo "---"
echo "STEP 1: Extracting deals from HTML file..."
echo "Input: $HTML_FILE"

# --- Script Selection Logic ---
HTML_FILE_BASENAME=$(basename "$HTML_FILE")
EXTRACTOR_SCRIPT=""

# Regex to find a date like 122624 (MMDDYY) from savings_122624...
if [[ "$HTML_FILE_BASENAME" =~ savings_([0-9]{6}) ]]; then
    DATE_MMDDYY="${BASH_REMATCH[1]}"
    # Convert MMDDYY to YYYYMMDD for numerical comparison
    # Assuming all years are in the 21st century (20xx)
    MM=${DATE_MMDDYY:0:2}
    DD=${DATE_MMDDYY:2:2}
    YY=${DATE_MMDDYY:4:2}
    DATE_YYYYMMDD="20${YY}${MM}${DD}"

    THRESHOLD_DATE="20241020"

    if [ "$DATE_YYYYMMDD" -lt "$THRESHOLD_DATE" ]; then
        EXTRACTOR_SCRIPT="src/crawlers/extract_costco_offers_local_v2024.py"
    else
        EXTRACTOR_SCRIPT="src/crawlers/extract_costco_offers_local_v2025.py"
    fi
else
    echo "Warning: Could not determine date from filename '$HTML_FILE_BASENAME'. Defaulting to v2025 extractor."
    EXTRACTOR_SCRIPT="src/crawlers/extract_costco_offers_local_v2025.py"
fi

echo "Selected extractor based on filename: $EXTRACTOR_SCRIPT"
# --- End Script Selection ---

# Run extraction and capture the full output line to get the generated filename
EXTRACT_OUTPUT=$(python3 "$EXTRACTOR_SCRIPT" "$HTML_FILE")
if [ $? -ne 0 ]; then
    echo "Error during extraction. Aborting."
    exit 1
fi

# Extract the filename from the output "Wrote X deals to /path/to/file.ndjson"
NDJSON_FILE=$(echo "$EXTRACT_OUTPUT" | awk -F' to ' '{print $2}')

# Check if we got a filename and if the file exists
if [ -z "$NDJSON_FILE" ] || [ ! -f "$NDJSON_FILE" ]; then
  echo "Could not determine the output NDJSON file from the extraction script."
  echo "Extraction script output: $EXTRACT_OUTPUT"
  exit 1
fi

echo "Successfully extracted deals."
echo "Output: $NDJSON_FILE"
echo "---"

# --- Ingestion ---

# Step 2: Ingest to local dev server via API
echo "STEP 2: Ingesting deals to local server via API..."
python3 src/processors/ingest_deals.py --file "$NDJSON_FILE"
if [ $? -ne 0 ]; then
    echo "Error during local API ingestion. Aborting."
    exit 1
fi
echo "Successfully ingested to local server."
echo "---"

# Step 3: Convert the same NDJSON to SQL for D1
echo "STEP 3: Converting deals to SQL format for D1..."
CONVERT_OUTPUT=$(python3 src/processors/convert_deals_to_sql.py --file "$NDJSON_FILE")
if [ $? -ne 0 ]; then
  echo "Error during SQL conversion. Aborting."
  exit 1
fi
SQL_FILE=$(echo "$CONVERT_OUTPUT" | grep "Wrote SQL to" | awk -F' to ' '{print $2}')
if [ -z "$SQL_FILE" ] || [ ! -f "$SQL_FILE" ]; then
  echo "Could not determine the output SQL file from the conversion script."
  echo "Conversion script output: $CONVERT_OUTPUT"
  exit 1
fi
echo "Successfully converted to SQL."
echo "Output: $SQL_FILE"
echo "---"

# Step 4: Ingest the SQL file directly to D1
echo "STEP 4: Ingesting SQL directly to D1..."
node src/processors/ingest_to_d1.js "$SQL_FILE"
if [ $? -ne 0 ]; then
    echo "Error during D1 ingestion. Aborting."
    exit 1
fi

echo "---"
echo "Pipeline completed successfully!"
echo "Data ingested to both local server and production D1." 