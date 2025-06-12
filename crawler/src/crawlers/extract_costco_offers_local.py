#!/usr/bin/env python3
"""
extract_tiles_costco.py
-----------------------
• Input : a local HTML file you saved from https://www.costco.com/online-offers.html
• Output: NDJSON file named deals_YYYYMMDD-YYYYMMDD.ndjson containing lines like
          {"link":"…product.100352100.html","sku":"1111161",
           "name":"Dixie Ultra 10 1/16\" Plates","discount":4.0,
           "category": "Home & Kitchen",
           "details":"186 ct. Item 1111161, Limit 2.",
           "valid_period": {"starts": "2025-05-14", "ends": "2025-06-08"}}

Usage
  python extract_tiles_costco.py  savings_051425_060825.html
"""
from bs4 import BeautifulSoup
from pathlib import Path
import re, json, sys, datetime as dt

if len(sys.argv) != 2:
    sys.exit("usage: extract_tiles_costco.py  <saved_html>")

html_file = Path(sys.argv[1]).expanduser()
soup      = BeautifulSoup(html_file.read_text("utf-8"), "lxml")

# ────────────────────────────────────────────────────────────────────────────
# Helpers
ITEM_RE    = re.compile(r"Item\s+(\d+)")
NOW_ISO    = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

# Category mapping based on product names and details
CATEGORY_KEYWORDS = {
    "Home & Kitchen": ["plate", "cup", "utensil", "cookware", "kitchen", "appliance", "vacuum", "fan", "light", "furniture"],
    "Electronics": ["tv", "laptop", "computer", "monitor", "camera", "phone", "tablet", "headphone"],
    "Health & Beauty": ["shampoo", "conditioner", "vitamin", "supplement", "medicine", "health", "beauty", "cosmetic"],
    "Grocery": ["food", "snack", "drink", "beverage", "coffee", "tea", "water", "juice", "cereal", "candy"],
    "Clothing": ["shirt", "pants", "dress", "shoe", "jacket", "sock", "underwear", "clothing", "apparel"],
    "Pet Supplies": ["pet", "dog", "cat", "animal", "treat", "toy"],
    "Office": ["paper", "pen", "pencil", "notebook", "office", "stationery"],
    "Automotive": ["tire", "car", "auto", "vehicle", "automotive"],
    "Sports & Outdoors": ["sport", "outdoor", "camping", "fishing", "hunting", "exercise", "fitness"],
    "Toys & Games": ["toy", "game", "play", "puzzle", "board game"],
    "Baby": ["baby", "infant", "diaper", "formula", "stroller"],
    "Lawn & Garden": ["garden", "lawn", "plant", "flower", "seed", "soil"]
}

def determine_category(name: str, details: str) -> str:
    """Determine the category based on product name and details."""
    text = (name + " " + details).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Other"

def extract_valid_period(soup: BeautifulSoup) -> dict:
    """Extract valid period from the HTML file."""
    # Look for text containing "Valid" followed by dates
    valid_text = None
    for text in soup.stripped_strings:
        if "Valid" in text:
            valid_text = text
            break
    
    if not valid_text:
        return {"starts": None, "ends": None}
    
    # Extract dates using regex
    date_pattern = r"(\d{1,2}/\d{1,2}/\d{2})"
    dates = re.findall(date_pattern, valid_text)
    
    if len(dates) != 2:
        return {"starts": None, "ends": None}
    
    # Convert dates to ISO format (YYYY-MM-DD)
    try:
        start_date = dt.datetime.strptime(dates[0], "%m/%d/%y").strftime("%Y-%m-%d")
        end_date = dt.datetime.strptime(dates[1], "%m/%d/%y").strftime("%Y-%m-%d")
        return {"starts": start_date, "ends": end_date}
    except ValueError:
        return {"starts": None, "ends": None}

def parse_discount(price_block: "Tag") -> tuple[float, str] | None:
    """
    Examine the small price banner inside a tile and return
    (value, kind) where kind is either 'dollar' or 'percent'.
    The HTML usually renders as:
        $ 4           OFF
        25 %          OFF
    We scan the child Text blocks to see which symbol appears.
    """
    # First try "After $X OFF"
    append_text_div = tile.find("div", {"data-testid": "Text_prices_and_percentages_append_text"})
    if append_text_div:
        txt = append_text_div.get_text(strip=True)
        m = re.search(r"After\s+\$?(\d+(?:\.\d+)?)\s+OFF", txt, re.IGNORECASE)
        if m:
            return float(m.group(1)), "dollar"
        m = re.search(r"After\s+(\d+)%\s+OFF", txt, re.IGNORECASE)
        if m:
            return float(m.group(1)), "percent"

    # Fallback to prices_and_percentages_prices
    symbol = None
    number = None
    dollar = None
    cents  = None
    price_blk = price_block.find("div", {"data-testid": "prices_and_percentages_prices"})
    for node in price_blk.find_all("div", {"data-testid": "Text"}):
        txt = node.get_text(strip=True)
        if txt in ("$", "%"):
            symbol = txt
            continue
        m = re.fullmatch(r"(\d+(?:\.\d+)?)", txt)
        if m:
            value = float(m.group(1))
            if dollar is None:
                dollar = value
            elif cents is None:
                cents = value
    
    if dollar is not None:
        number = dollar
        if cents is not None:
            number += cents / 100

    if number is None:
        return None
    kind = "percent" if symbol == "%" else "dollar"
    return number, kind

def extract_offer_channel(tile: "Tag") -> str:
    """
    Extract the offer channel from the tile.
    Returns one of: "Warehouse-Only", "In-Warehouse & Online", or "Online-Only"
    """
    strip_div = tile.find("div", {"data-testid": "strip"})
    if not strip_div:
        return "Unknown"
    
    text_div = strip_div.find("div", {"data-testid": "Text"})
    if not text_div:
        return "Unknown"
    
    channel_text = text_div.get_text(strip=True)
    
    # Map the text to our standardized channel names
    if "Warehouse-Only" in channel_text:
        return "Warehouse-Only"
    elif "In-Warehouse & Online" in channel_text:
        return "In-Warehouse & Online"
    elif "Online-Only" in channel_text:
        return "Online-Only"
    else:
        return "Unknown"

# ────────────────────────────────────────────────────────────────────────────
deals = []

# Extract valid period once for all deals
valid_period = extract_valid_period(soup)

tiles = soup.find_all("div", {"data-testid": "AdBuilder"})
for tile in tiles:
    # <a href="…product.100352100.html"> is the wrapper
    a      = tile.find("a", href=True)
    link   = a["href"] if a else None     # If link is missing, continue

    # discount: <div data-testid="prices_and_percentages_prices">
    price_blk = tile.find("div", {"data-testid": "prices_and_percentages_prices"})
    # parsed = parse_discount(price_blk) if price_blk else None
    parsed = parse_discount(tile) if price_blk else None    # we need to make sure there's a price block in the tile
    if not parsed:
        continue
    discount, discount_type = parsed

    txt_zone  = tile.find("div", {"data-testid": "below_the_ad_text_content"})
    name_lines = []
    for div in txt_zone.find_all("div", {"data-testid": "Text"}):
        # ▸ skip if this text lives inside the price box
        if div.find_parent("div", {"data-testid": "prices_and_percentages_prices"}):
            continue
        txt = div.get_text(strip=True)
        if txt:                           # ignore empty lines
            name_lines.append(txt)

    if not name_lines:
        continue                          # no real text → skip tile

    name    = name_lines[0]               # first = product name
    details = name_lines[-1]              # last = size, SKU, etc.

    # Try to extract Costco SKU from "Item 1111161" or from PNG filename
    m_item  = ITEM_RE.search(details)
    m_png   = re.search(r"_([0-9]{6,})\.png", tile.decode())
    sku     = m_item.group(1) if m_item else (m_png.group(1) if m_png else None)

    # Determine category based on product name and details
    category = determine_category(name, details)

    # Extract offer channel
    offer_channel = extract_offer_channel(tile)

    deals.append({
        "link":     link,
        "sku":      sku,
        "name":     name,
        "category": category,
        "discount": discount,          # numeric
        "discount_type": discount_type,  # 'dollar' or 'percent'
        "details":  details,
        "seen_at":  NOW_ISO,
        "valid_period": valid_period,
        "offer_channel": offer_channel  # Add the offer channel to the output
    })

# ────────────────────────────────────────────────────────────────────────────
# Write deals to file with valid period in filename
output_path = Path(__file__).parent.parent.parent / "data" / "processed"
output_path.mkdir(parents=True, exist_ok=True)
input_prefix = html_file.stem.split("_")[0] if "_" in html_file.stem else "deals"
if valid_period["starts"] and valid_period["ends"]:
    start_date = valid_period["starts"].replace("-", "")
    end_date = valid_period["ends"].replace("-", "")
    output_file = output_path / f"{input_prefix}_{start_date}-{end_date}.ndjson"
else:
    output_file = output_path / f"{input_prefix}_unknown_period.ndjson"

with open(output_file, "w") as f:
    for d in deals:
        f.write(json.dumps(d) + "\n")

print(f"Wrote {len(deals)} deals to {output_file}")