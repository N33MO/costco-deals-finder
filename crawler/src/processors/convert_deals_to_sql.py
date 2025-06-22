#!/usr/bin/env python3
"""
ingest_deals.py
---------------
Preprocess, validate, and transform deals NDJSON for ingestion.
Outputs a single SQL file (with three INSERTs: product, offer_period, offer_snapshot) and a .ndjson file for unavailable deals.
No D1 upload logic.

Usage:
  python ingest_deals.py --file raw_deals.ndjson --sql-out processed_deals.sql [--unavailable-out unavailable_deals.ndjson]
"""

import json
import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv

def write_ndjson(data: List[Dict[str, Any]], file_path: str) -> None:
    """Write data to an NDJSON file."""
    try:
        with open(file_path, 'w') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
    except Exception as e:
        print(f"Error writing to {file_path}: {str(e)}")
        sys.exit(1)

def validate_deal(deal: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a deal against database requirements.
    Returns (is_valid, reason) tuple.
    """
    # Check for required fields
    if not deal.get('sku'):
        return False, "Missing SKU"
    
    if not deal.get('name'):
        return False, "Missing product name"
    
    if not deal.get('discount'):
        return False, "Missing discount"
    
    if not deal.get('discount_type'):
        return False, "Missing discount type"
    
    if not deal.get('valid_period'):
        return False, "Missing valid period"
    
    if not deal.get('valid_period', {}).get('starts') or not deal.get('valid_period', {}).get('ends'):
        return False, "Invalid valid period dates"
    
    # Check for valid discount type
    if deal['discount_type'] not in ['dollar', 'percent']:
        return False, f"Invalid discount type: {deal['discount_type']}"
    
    # Check for valid discount value
    try:
        discount = float(deal['discount'])
        if discount <= 0:
            return False, f"Invalid discount value: {discount}"
    except (ValueError, TypeError):
        return False, f"Invalid discount value: {deal['discount']}"
    
    return True, ""

def transform_product(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a deal from NDJSON format to match database schema.
    Returns a dictionary with 'product' data.
    """
    # Flatten for SQL/NDJSON output
    return {
        "sku": deal["sku"],
        "name": deal["name"],
        "category": deal.get("category", "Other"),
        "brand": deal.get("brand"),
        "image_url": deal.get("image_url"),
    }

def transform_offer_period(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a deal from NDJSON format to match database schema.
    Returns a dictionary with 'offer_period' data.
    """
    # Flatten for SQL/NDJSON output
    return {
        "product_id": f"(SELECT id FROM product WHERE sku = '{deal['sku']}')",
        "region": deal.get("region", "US"),
        "channel": deal.get("channel", "Unknown"),
        "sale_type": deal["discount_type"],
        "discount_low": deal["discount"],
        "discount_high": deal["discount"],
        "currency": deal.get("currency", "USD"),
        "limit_qty": extract_limit_qty(deal.get("details", "")),
        "details": deal.get("details", ""),
        "starts": deal["valid_period"]["starts"],
        "ends": deal["valid_period"]["ends"],
    }

def transform_offer_snapshot(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a deal from NDJSON format to match database schema.
    Returns a dictionary with 'offer_snapshot' data.
    """
    # Flatten for SQL/NDJSON output
    return {
        "offer_period_id": (
            f"(SELECT id FROM offer_period WHERE "
            f"product_id = (SELECT id FROM product WHERE sku = '{deal['sku']}'))"
        ),
        "seen_at": deal.get("seen_at"),
        "discount_low": deal["discount"],
        "discount_high": deal["discount"],
        "details": deal.get("details", ""),
    }

def extract_limit_qty(details: str) -> int | None:
    """Extract limit quantity from details string."""
    import re
    match = re.search(r"Limit\s+(\d+)", details)
    return int(match.group(1)) if match else None

def make_sql_insert(data: List[Dict[str, Any]], table_name: str, skip_cols=None) -> str:
    if not data:
        return ""
    skip_cols = skip_cols or []
    columns = [col for col in data[0].keys() if col not in skip_cols]
    values = []
    for row in data:
        row_values = []
        for col in columns:
            val = row.get(col)
            # embed raw SQL expressions without quoting
            if isinstance(val, str) and val.strip().startswith('(SELECT') and val.strip().endswith(')'):
                row_values.append(val)
            elif val is None or val == "":
                row_values.append("NULL")
            elif isinstance(val, (int, float)):
                row_values.append(str(val))
            else:
                escaped_val = str(val).replace("'", "''")
                row_values.append(f"'{escaped_val}'")
        values.append(f"({', '.join(row_values)})")
    return f"INSERT OR IGNORE INTO {table_name} ({', '.join(columns)}) VALUES {', '.join(values)};"

def main():
    parser = argparse.ArgumentParser(description='Preprocess deals for ingestion (outputs SQL and unavailable NDJSON)')
    parser.add_argument('--file', required=True, help='Path to the NDJSON file containing deals')
    parser.add_argument('--sql-out', help='Output SQL file (all tables)', default=None)
    parser.add_argument('--unavailable-file', help='Path to save unavailable deals (default: unprocessed_YYYYMMDD-YYYYMMDD.ndjson)')
    args = parser.parse_args()

    # Determine processed output directory relative to this script
    script_dir = Path(__file__).parent
    processed_dir = (script_dir / '..' / '..' / 'data' / 'processed').resolve()
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Derive base name from input file
    input_path = Path(args.file)
    base = input_path.stem

    # Set SQL output path if not provided
    args.sql_out = args.sql_out or str(processed_dir / f"{base}.sql")

    # Set unavailable deals output path if not provided
    if not args.unavailable_file:
        args.unavailable_file = str(processed_dir / f"unavailable_{base}.ndjson")
    else:
        # ensure custom path goes into processed_dir
        args.unavailable_file = str(processed_dir / Path(args.unavailable_file).name)

    # Read and validate deals
    with open(args.file, 'r') as f:
        deals = [json.loads(line) for line in f if line.strip()]

    # Transform and split into tables
    available, unavailable = [], []
    for deal in deals:
        is_valid, reason = validate_deal(deal)
        if not is_valid:
            deal["validation_error"] = reason
            unavailable.append(deal)
            continue
        available.append(deal)

    # Transform available deals into three tables
    products = [transform_product(d) for d in available]
    offer_periods = [transform_offer_period(d) for d in available]
    offer_snapshots = [transform_offer_snapshot(d) for d in available]

    # Write unavailable deals NDJSON if any
    if unavailable:
        write_ndjson(unavailable, args.unavailable_file)
        print(f"Saved {len(unavailable)} unavailable deals to {args.unavailable_file}")
    
    # Report statistics
    print(f"\nDeal Statistics:")
    print(f"Total deals: {len(deals)}")
    print(f"Valid deals: {len(available)}")
    print(f"Unavailable deals: {len(unavailable)}")
    
    # Generate SQL for each table
    sql = ""
    sql += make_sql_insert(products, "product") + "\n"
    sql += make_sql_insert(offer_periods, "offer_period") + "\n"
    sql += make_sql_insert(offer_snapshots, "offer_snapshot") + "\n"

    # Write SQL file
    with open(args.sql_out, 'w') as f:
        f.write(sql)
    print(f"Wrote SQL to {args.sql_out}")

    print(f"Total deals: {len(deals)} | Available: {len(available)} | Unavailable: {len(unavailable)}")

if __name__ == "__main__":
    main()