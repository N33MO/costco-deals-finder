#!/bin/bash

# This script applies all savings and hotbuys data migrations to the local D1 database.
# Usage: ./apply_data_migrations.sh

DB_NAME="costco-test"

# Resolve all paths relative to this script's location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$SCRIPT_DIR/../.."
DATA_MIGRATIONS_DIR="$REPO_ROOT/backend/migrations/data"
CONFIG_FILE="$REPO_ROOT/backend/wrangler.dev.toml"

echo "Applying data migrations to database: $DB_NAME"

echo "Data migrations: $DATA_MIGRATIONS_DIR"
echo "Config: $CONFIG_FILE"

# Apply savings data
for f in "$DATA_MIGRATIONS_DIR"/savings_*.sql; do
    [ -e "$f" ] || continue
    echo "Applying $f"
    wrangler d1 execute $DB_NAME --file "$f" --local --config "$CONFIG_FILE"
done

# Apply hotbuys data
for f in "$DATA_MIGRATIONS_DIR"/hotbuys_*.sql; do
    [ -e "$f" ] || continue
    echo "Applying $f"
    wrangler d1 execute $DB_NAME --file "$f" --local --config "$CONFIG_FILE"
done

echo "Data migrations applied successfully." 