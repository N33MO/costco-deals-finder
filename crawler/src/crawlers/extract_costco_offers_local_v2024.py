#!/usr/bin/env python3
"""
extract_costco_offers_local_v2024.py
------------------------------------
• Input : a local HTML file you saved from a 2024 version of Costco's offers page.
• Output: NDJSON file named deals_YYYYMMDD-YYYYMMDD.ndjson containing lines like
          {"link":"…product.4000137876.html","sku":"1720981",
           "name":"Bounty Advanced Paper Towels","discount":5.0,
           "category": "Home & Kitchen",
           "details":"12/101 Sheets. Item 1720981, 1720886",
           "valid_period": {"starts": "2024-10-09", "ends": "2024-11-03"}}

Usage
  python extract_costco_offers_local_v2024.py savings_100924_110324.html
"""
from bs4 import BeautifulSoup, Tag
from pathlib import Path
import re, json, sys, datetime as dt

if len(sys.argv) != 2:
    sys.exit("usage: extract_costco_offers_local_v2024.py <saved_html>")

html_file = Path(sys.argv[1]).expanduser()
soup = BeautifulSoup(html_file.read_text("utf-8"), "lxml")

# ────────────────────────────────────────────────────────────────────────────
# Helpers
ITEM_RE = re.compile(r"Item\s+([\d, ]+)")
NOW_ISO = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def clean_archive_url(url: str) -> str:
    """Removes web.archive.org prefix from a URL if present."""
    # This pattern is designed to find the archive prefix, e.g., /web/20241217051439/
    # or /web/20241009103332im_/, and we take the part of the string that comes after it.
    parts = re.split(r'/web/\d+(?:im_)?/', url)
    return parts[-1]

# Category mapping based on product names and details (reused from original script)
CATEGORY_KEYWORDS = {
    "Home & Kitchen": ["plate", "cup", "utensil", "cookware", "kitchen", "appliance", "vacuum", "fan", "light", "furniture", "paper towels"],
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
    valid_p = soup.find("p", class_="eco-webvalid-header")
    if not valid_p:
        return {"starts": None, "ends": None}
    
    valid_text = valid_p.get_text(strip=True)
    
    # Format: "Valid August 28 to September 22, 2024"
    #      or "Valid August 28 to 31, 2024"
    pattern = r"Valid\s+([A-Za-z]+)\s+(\d{1,2})\s+to\s+(?:([A-Za-z]+)\s+)?(\d{1,2}),\s+(\d{4})"
    match = re.search(pattern, valid_text)

    if not match:
        return {"starts": None, "ends": None}
    
    start_month_str, start_day_str, end_month_str, end_day_str, year_str = match.groups()

    if not end_month_str:
        end_month_str = start_month_str # Same month

    try:
        start_date_str = f"{start_month_str} {start_day_str} {year_str}"
        end_date_str = f"{end_month_str} {end_day_str} {year_str}"
        
        start_date = dt.datetime.strptime(start_date_str, "%B %d %Y").strftime("%Y-%m-%d")
        end_date = dt.datetime.strptime(end_date_str, "%B %d %Y").strftime("%Y-%m-%d")
        
        return {"starts": start_date, "ends": end_date}
    except ValueError:
        return {"starts": None, "ends": None}

def parse_discount_v2024(tile: Tag) -> tuple[float, str] | None:
    """
    Examine the price table inside a tile and return (value, kind).
    """
    price_table = tile.find("table", class_="eco-price")
    if not price_table:
        return None

    symbol_span = price_table.find("span", class_="eco-dollarSign")
    dollar_span = price_table.find("span", class_="eco-dollar")
    
    if not dollar_span:
        return None
        
    try:
        value = float(dollar_span.text.strip())
        kind = "percent" if symbol_span and "%" in symbol_span.text else "dollar"
        return value, kind
    except (ValueError, TypeError):
        return None

def extract_offer_channel_v2024(tile: Tag) -> str:
    """
    Extract the offer channel from the tile's eco-header.
    """
    header = tile.find("div", class_="eco-header")
    if not header:
        return "Unknown"
    
    text = header.get_text(strip=True).upper()
    if "IN-WAREHOUSE" in text and "ONLINE" in text:
        return "In-Warehouse & Online"
    elif "IN-WAREHOUSE" or "WAREHOUSE-ONLY" in text:
        return "Warehouse-Only"
    elif "ONLINE" in text:
        return "Online-Only"
    else:
        return "Unknown"

def extract_image_url_v2024(tile: Tag) -> str | None:
    """Extract the product image URL from the tile."""
    img_tag = tile.find("img", class_="eco-webImage")
    return clean_archive_url(img_tag["src"]) if img_tag and img_tag.has_attr("src") else None

# ────────────────────────────────────────────────────────────────────────────
deals = []

# Extract valid period once for all deals
valid_period = extract_valid_period(soup)

tiles = soup.find_all("li", class_="eco-coupons")
for tile in tiles:
    a_tag = tile.find("a", href=True)
    if not a_tag:
        continue
    link = clean_archive_url(a_tag["href"])

    image_url = extract_image_url_v2024(tile)
    
    parsed_discount = parse_discount_v2024(tile)
    if not parsed_discount:
        continue
    discount, discount_type = parsed_discount

    name_div = tile.find("div", class_="eco-sl1")
    name = name_div.get_text(strip=True) if name_div else "Unknown Product"

    details_parts = []
    sl2_div = tile.find("div", class_="eco-sl2")
    if sl2_div:
        details_parts.append(sl2_div.get_text(strip=True))

    items_div = tile.find("div", class_="eco-items")
    sku = None
    if items_div:
        items_text = items_div.get_text(strip=True)
        details_parts.append(items_text)
        # Extract first SKU found
        m_item = ITEM_RE.search(items_text)
        if m_item:
            sku = m_item.group(1).split(',')[0].strip()

    details = ". ".join(filter(None, details_parts))

    category = determine_category(name, details)
    offer_channel = extract_offer_channel_v2024(tile)

    deals.append({
        "link": link,
        "sku": sku,
        "name": name,
        "image_url": image_url,
        "category": category,
        "discount": discount,
        "discount_type": discount_type,
        "details": details,
        "seen_at": NOW_ISO,
        "valid_period": valid_period,
        "channel": offer_channel,
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
    output_file = output_path / f"{input_prefix}_unknown_period_v2024.ndjson"

with open(output_file, "w") as f:
    for d in deals:
        f.write(json.dumps(d) + "\n")

print(f"Wrote {len(deals)} deals to {output_file}") 