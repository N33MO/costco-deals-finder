#!/bin/bash

# This script reapplies the necessary migrations to the local D1 database.
# It's useful when the local database is reset or lost.

DB_NAME="costco-test"

# Resolve all paths relative to this script's location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$SCRIPT_DIR/../.."
SCHEMA_MIGRATIONS_DIR="$REPO_ROOT/backend/migrations"
DATA_MIGRATIONS_DIR="$REPO_ROOT/backend/migrations/data"
CONFIG_FILE="$REPO_ROOT/backend/wrangler.dev.toml"

echo "Applying migrations to database: $DB_NAME"

echo "Schema: $MIGRATIONS_DIR"
echo "Config: $CONFIG_FILE"

# Apply schema
wrangler d1 execute $DB_NAME --file "$MIGRATIONS_DIR/0001_schema.sql" --local --config "$CONFIG_FILE"
wrangler d1 execute $DB_NAME --file "$MIGRATIONS_DIR/0003_add_images_and_channel.sql" --local --config "$CONFIG_FILE"

echo "Schema migrations applied successfully."

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

echo "Migrations applied successfully." 