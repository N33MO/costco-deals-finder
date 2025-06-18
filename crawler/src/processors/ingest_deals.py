#!/usr/bin/env python3
"""
ingest_deals.py
---------------
Ingest transformed deals into the database via the ingestion endpoint.
Supports both local development and Cloudflare D1 database.

Usage:
  # For local database:
  python ingest_deals.py --file data/processed/deals_20240314-20240414.ndjson
  
  # For D1 database:
  python ingest_deals.py --file data/processed/deals_20240314-20240414.ndjson --d1
"""

import json
import sys
import requests
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
from dotenv import load_dotenv

def read_deals_file(file_path: str) -> List[Dict[str, Any]]:
    """Read deals from NDJSON file."""
    try:
        with open(file_path, 'r') as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        sys.exit(1)

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

def transform_deal(deal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a deal from NDJSON format to match database schema.
    Returns a dictionary with 'product' and 'offer_period' data.
    """
    # Extract product data
    product = {
        "sku": deal["sku"],
        "name": deal["name"],
        "category": deal.get("category", "Other"),
        "brand": None  # We'll set this to NULL for now
    }

    # Extract offer period data
    offer_period = {
        "region": deal.get("region", "US"),
        "sale_type": deal["discount_type"],
        "discount_low": deal["discount"],
        "discount_high": deal["discount"],  # Same as low since we don't have range
        "currency": "USD",
        "limit_qty": extract_limit_qty(deal["details"]),
        "details": deal["details"],
        "starts": deal["valid_period"]["starts"],
        "ends": deal["valid_period"]["ends"]
    }

    # Create offer snapshot
    snapshot = {
        "seen_at": deal["seen_at"],
        "discount_low": deal["discount"],
        "discount_high": deal["discount"],
        "details": deal["details"]
    }

    return {
        "product": product,
        "offer_period": offer_period,
        "snapshot": snapshot
    }

def extract_limit_qty(details: str) -> int | None:
    """Extract limit quantity from details string."""
    import re
    match = re.search(r"Limit\s+(\d+)", details)
    return int(match.group(1)) if match else None

def get_api_url(use_d1: bool) -> str:
    """Get the appropriate API URL based on the target database."""
    if use_d1:
        # Load environment variables from .env file
        load_dotenv()
        # Get the API URL from environment
        api_url = os.getenv("VITE_API_URL")
        if not api_url:
            print("Error: VITE_API_URL not found in .env file")
            sys.exit(1)
        return f"{api_url}/api/ingest"
    else:
        return os.getenv("INGEST_API_URL", "http://localhost:8787/api/ingest")

def ingest_deals(deals: List[Dict[str, Any]], api_url: str, use_d1: bool) -> None:
    """Ingest deals into the database via the ingestion endpoint."""
    try:
        # Transform deals to match database schema
        transformed_deals = [transform_deal(deal) for deal in deals]
        
        # Create headers with authentication
        headers = {
            "Content-Type": "application/json"
        }
        if use_d1:
            api_key = os.getenv("CF_D1_API_KEY")
            if not api_key:
                print("Warning: CF_D1_API_KEY not set, proceeding without Authorization header")
            else:
                headers["Authorization"] = f"Bearer {api_key}"
        
        print(f"Sending request to: {api_url}")
        
        # Send request to API
        response = requests.post(
            api_url,
            json=transformed_deals,
            headers=headers,
            verify=True,  # Use system's default SSL certificates
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Error ingesting deals: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)
        
        result = response.json()
        if result.get('status') == 'success':
            print(f"Successfully ingested {len(deals)} deals")
            if 'details' in result:
                print(f"Details: {result['details']}")
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
            if 'details' in result:
                print(f"Details: {result['details']}")
            sys.exit(1)
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {str(e)}")
        sys.exit(1)

def get_valid_period_filename(deals: List[Dict[str, Any]], prefix: str) -> str:
    """Generate filename based on valid period from deals."""
    if not deals:
        return f"{prefix}_unknown_period.ndjson"
    
    # Get valid period from first deal (all deals should have same period)
    valid_period = deals[0].get('valid_period', {})
    starts = valid_period.get('starts')
    ends = valid_period.get('ends')
    
    if starts and ends:
        start_date = starts.replace("-", "")
        end_date = ends.replace("-", "")
        return f"{prefix}_{start_date}-{end_date}.ndjson"
    else:
        return f"{prefix}_unknown_period.ndjson"

def main():
    parser = argparse.ArgumentParser(description='Ingest deals into the database')
    parser.add_argument('--file', required=True, help='Path to the NDJSON file containing deals')
    parser.add_argument('--d1', action='store_true', help='Use D1 database instead of local')
    parser.add_argument('--unavailable-file', help='Path to save unavailable deals (default: unprocessed_YYYYMMDD-YYYYMMDD.ndjson)')
    args = parser.parse_args()

    # Get API URL based on target database
    api_url = get_api_url(args.d1)
    print(f"Using API endpoint: {api_url}")

    try:
        # Read deals from file
        deals = read_deals_file(args.file)
        
        # Validate deals and separate them
        valid_deals = []
        unavailable_deals = []
        
        for deal in deals:
            is_valid, reason = validate_deal(deal)
            if is_valid:
                valid_deals.append(deal)
            else:
                # Add validation reason to the deal
                deal['validation_error'] = reason
                unavailable_deals.append(deal)
        
        # Report statistics
        print(f"\nDeal Statistics:")
        print(f"Total deals: {len(deals)}")
        print(f"Valid deals: {len(valid_deals)}")
        print(f"Unavailable deals: {len(unavailable_deals)}")
        
        if unavailable_deals:
            # Generate filename based on valid period
            unavailable_file = args.unavailable_file or get_valid_period_filename(unavailable_deals, "unprocessed")
            write_ndjson(unavailable_deals, unavailable_file)
            print(f"\nSaved {len(unavailable_deals)} unavailable deals to {unavailable_file}")
            
            # Print reasons for unavailability
            print("\nReasons for unavailability:")
            reasons = {}
            for deal in unavailable_deals:
                reason = deal['validation_error']
                reasons[reason] = reasons.get(reason, 0) + 1
            for reason, count in reasons.items():
                print(f"- {reason}: {count} deals")
        
        if not valid_deals:
            print("\nNo valid deals to ingest")
            sys.exit(1)
            
        # Ingest valid deals
        print("\nIngesting valid deals...")
        ingest_deals(valid_deals, api_url, args.d1)
        
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 