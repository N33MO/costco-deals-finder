#!/usr/bin/env python3
"""
fill_missing_skus.py
-------------------
Usage:
  python fill_missing_skus.py <target_ndjson>

Fills missing SKUs in the specified NDJSON file by:
1. Using the SKU of another item with the exact same name (from other NDJSONs).
2. If not found, using the SKU of an item where the target name is a prefix of the reference name (from other NDJSONs), using the most frequent SKU, breaking ties by latest valid_period["starts"].
3. If not found, using the SKU of an item with similar name and similar details (from other NDJSONs).
4. Logging every changed SKU.

Output: Writes a new NDJSON file with '_sku_filled' suffix and a log file of changes.
"""
import json
from pathlib import Path
import difflib
import logging
import sys
from collections import Counter
from datetime import datetime

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
LOG_FILE = Path(__file__).parent / "fill_missing_skus.log"

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s')

def load_reference_deals(processed_dir, exclude_file):
    """Load all deals from all NDJSON files except the target file."""
    all_deals = []
    for ndjson_file in processed_dir.glob("*.ndjson"):
        if ndjson_file.resolve() == exclude_file.resolve():
            continue
        with open(ndjson_file, "r") as f:
            for line in f:
                deal = json.loads(line)
                all_deals.append(deal)
    return all_deals

def find_sku_by_exact_name(name, all_deals):
    for deal in all_deals:
        if deal['sku'] and deal['name'] == name:
            return deal['sku']
    return None

def find_sku_by_prefix_or_suffix(target_name, all_deals):
    """
    Find all deals where target_name is a prefix or suffix of deal['name'].
    Return the most frequent SKU among those, breaking ties by latest valid_period['starts'].
    """
    prefix_suffix_matches = [deal for deal in all_deals if deal['sku'] and (deal['name'].startswith(target_name) or deal['name'].endswith(target_name))]
    if not prefix_suffix_matches:
        return None
    sku_counts = Counter(deal['sku'] for deal in prefix_suffix_matches)
    most_common = sku_counts.most_common()
    if not most_common:
        return None
    top_count = most_common[0][1]
    top_skus = [sku for sku, count in most_common if count == top_count]
    if len(top_skus) == 1:
        return top_skus[0]
    # Tie: pick the one with latest valid_period['starts']
    latest_date = None
    chosen_sku = None
    for deal in prefix_suffix_matches:
        if deal['sku'] in top_skus:
            starts = deal.get('valid_period', {}).get('starts')
            if starts:
                try:
                    date_obj = datetime.strptime(starts, "%Y-%m-%d")
                    if latest_date is None or date_obj > latest_date:
                        latest_date = date_obj
                        chosen_sku = deal['sku']
                except Exception:
                    continue
    return chosen_sku or top_skus[0]

def find_sku_by_similarity(name, details, all_deals, name_thresh=0.85, details_thresh=0.7):
    best_score = 0
    best_sku = None
    for deal in all_deals:
        if deal['sku']:
            name_score = difflib.SequenceMatcher(None, deal['name'], name).ratio()
            details_score = difflib.SequenceMatcher(None, deal.get('details',''), details).ratio()
            if name_score > name_thresh and details_score > details_thresh:
                avg_score = (name_score + details_score) / 2
                if avg_score > best_score:
                    best_score = avg_score
                    best_sku = deal['sku']
    return best_sku

def process_target_file(target_file, reference_deals):
    output_file = target_file.with_name(target_file.stem + "_sku_filled.ndjson")
    changes = []
    with open(target_file, "r") as f, open(output_file, "w") as out:
        for i, line in enumerate(f):
            deal = json.loads(line)
            if not deal.get('sku'):
                # 1. Try exact name
                new_sku = find_sku_by_exact_name(deal['name'], reference_deals)
                reason = 'exact name' if new_sku else None
                # 2. Try prefix or suffix match
                if not new_sku:
                    new_sku = find_sku_by_prefix_or_suffix(deal['name'], reference_deals)
                    reason = 'prefix/suffix match' if new_sku else None
                # 3. Try similarity
                if not new_sku:
                    new_sku = find_sku_by_similarity(deal['name'], deal.get('details',''), reference_deals)
                    reason = 'fuzzy match' if new_sku else None
                if new_sku:
                    old_deal = dict(deal)  # copy for logging
                    deal['sku'] = new_sku
                    log_msg = (
                        f"[SKU FILLED] file={target_file.name} line={i} reason={reason}\n"
                        f"  OLD: {json.dumps(old_deal, ensure_ascii=False)}\n"
                        f"  NEW: {json.dumps(deal, ensure_ascii=False)}"
                    )
                    logging.info(log_msg)
                    changes.append(log_msg)
            out.write(json.dumps(deal, ensure_ascii=False) + "\n")
    print(f"Done. Changes logged to {LOG_FILE}\nOutput: {output_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python fill_missing_skus.py <target_ndjson>")
        sys.exit(1)
    target_file = Path(sys.argv[1]).expanduser().resolve()
    if not target_file.exists():
        print(f"File not found: {target_file}")
        sys.exit(1)
    reference_deals = load_reference_deals(PROCESSED_DIR, target_file)
    process_target_file(target_file, reference_deals)

if __name__ == "__main__":
    main() 