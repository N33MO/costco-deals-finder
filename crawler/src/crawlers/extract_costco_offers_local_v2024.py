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

if len(sys.argv) not in (2, 4):
    sys.exit("usage: extract_costco_offers_local_v2024.py <saved_html> [<start_YYYY-MM-DD> <end_YYYY-MM-DD>]")

html_file = Path(sys.argv[1]).expanduser()
# Read as UTF-8, replacing invalid bytes with the replacement character
html_text = html_file.read_text("utf-8", errors="replace")
soup = BeautifulSoup(html_text, "lxml")

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

def parse_time_tag(time_tag):
    """Return YYYY-MM-DD from <time> tag, using datetime if it matches text, else parse text."""
    dt_str = time_tag["datetime"].strip()
    text = time_tag.get_text(strip=True)
    # Try to parse both as dates and compare
    # Try several text formats
    formats = ["%B %d, %Y", "%B %d", "%d, %Y", "%B %d %Y", "%d %B %Y"]
    # First, parse datetime attr
    try:
        dt_date = dt.datetime.strptime(dt_str, "%Y-%m-%d").date()
    except Exception as e:
        print(f"[ERROR] Failed to parse <time> datetime attribute: {e}")
        sys.exit(1)
    # Try to parse text as date
    text_date = None
    for f in formats:
        try:
            # If text does not have year, try to get year from dt_str
            if "%Y" not in f:
                text_with_year = f"{text} {dt_date.year}"
                text_date = dt.datetime.strptime(text_with_year, f+" %Y").date()
            else:
                text_date = dt.datetime.strptime(text, f).date()
            break
        except Exception:
            continue
    if text_date is None:
        print(f"[ERROR] Could not parse <time> tag text: '{text}'")
        sys.exit(1)
    if text_date == dt_date:
        return dt_date.strftime("%Y-%m-%d")
    else:
        return text_date.strftime("%Y-%m-%d")

def extract_valid_period(soup: BeautifulSoup) -> dict:
    """Extract valid period from the HTML file, supporting all known formats with <time> tags and text. Use <time datetime=""> only if it matches the text, else parse the text. Exit on error."""
    # Try to find <p class="eco-webValid"> with two <time> tags
    valid_p = soup.find("p", class_="eco-webValid")
    if valid_p and valid_p.find("time"):
        times = valid_p.find_all("time")
        if len(times) == 2:
            start_date = parse_time_tag(times[0])
            end_date = parse_time_tag(times[1])
            return {"starts": start_date, "ends": end_date}
        else:
            print("[ERROR] Could not find two <time> tags in valid period section.")
            sys.exit(1)
    # Fallback: old format (eco-webvalid-header)
    valid_p = soup.find("p", class_="eco-webvalid-header")
    if valid_p:
        valid_text = valid_p.get_text(strip=True)
        pattern = r"Valid\s+([A-Za-z]+)\s+(\d{1,2})\s+to\s+(?:([A-Za-z]+)\s+)?(\d{1,2}),\s+(\d{4})"
        match = re.search(pattern, valid_text)
        if not match:
            print("[ERROR] Could not parse valid period from eco-webvalid-header.")
            sys.exit(1)
        start_month_str, start_day_str, end_month_str, end_day_str, year_str = match.groups()
        if not end_month_str:
            end_month_str = start_month_str # Same month
        try:
            start_date_str = f"{start_month_str} {start_day_str} {year_str}"
            end_date_str = f"{end_month_str} {end_day_str} {year_str}"
            start_date = dt.datetime.strptime(start_date_str, "%B %d %Y").strftime("%Y-%m-%d")
            end_date = dt.datetime.strptime(end_date_str, "%B %d %Y").strftime("%Y-%m-%d")
            return {"starts": start_date, "ends": end_date}
        except ValueError as e:
            print(f"[ERROR] Failed to parse valid period dates: {e}")
            sys.exit(1)
    # Fallback: new format 'Valid April 12 - May 7, 2023' or 'Valid April 12 - 15, 2023'
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        # Try full month for both start and end
        pattern1 = r"Valid\s+([A-Za-z]+)\s+(\d{1,2})\s*-\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})"
        match1 = re.search(pattern1, text)
        if match1:
            start_month_str, start_day_str, end_month_str, end_day_str, year_str = match1.groups()
            try:
                start_date_str = f"{start_month_str} {start_day_str} {year_str}"
                end_date_str = f"{end_month_str} {end_day_str} {year_str}"
                start_date = dt.datetime.strptime(start_date_str, "%B %d %Y").strftime("%Y-%m-%d")
                end_date = dt.datetime.strptime(end_date_str, "%B %d %Y").strftime("%Y-%m-%d")
                return {"starts": start_date, "ends": end_date}
            except ValueError as e:
                print(f"[ERROR] Failed to parse valid period dates: {e}")
                sys.exit(1)
        # Try same month for start and end
        pattern2 = r"Valid\s+([A-Za-z]+)\s+(\d{1,2})\s*-\s*(\d{1,2}),\s*(\d{4})"
        match2 = re.search(pattern2, text)
        if match2:
            month_str, start_day_str, end_day_str, year_str = match2.groups()
            try:
                start_date_str = f"{month_str} {start_day_str} {year_str}"
                end_date_str = f"{month_str} {end_day_str} {year_str}"
                start_date = dt.datetime.strptime(start_date_str, "%B %d %Y").strftime("%Y-%m-%d")
                end_date = dt.datetime.strptime(end_date_str, "%B %d %Y").strftime("%Y-%m-%d")
                return {"starts": start_date, "ends": end_date}
            except ValueError as e:
                print(f"[ERROR] Failed to parse valid period dates: {e}")
                sys.exit(1)
    print("[ERROR] Could not find a valid period in the HTML file.")
    sys.exit(1)

def parse_discount_v2024(tile: Tag) -> tuple[float, str] | None:
    """
    Examine the price table inside a tile and return (value, kind).
    Handles nested tags and multiple text nodes in the discount value.
    """
    price_table = tile.find("table", class_="eco-price")
    if not price_table:
        return None

    symbol_span = price_table.find("span", class_="eco-dollarSign")
    # Robustly extract the full text from all eco-dollar spans (handles nested tags)
    dollar_spans = price_table.find_all("span", class_="eco-dollar")
    dollar_text = "".join([s.get_text(strip=True) for s in dollar_spans])
    # Fallback: try to get all text from price_table if above fails
    if not dollar_text:
        dollar_text = price_table.get_text(strip=True)
    # Extract the first number (integer or float) from the text
    m = re.search(r"(\d+(?:\.\d+)?)", dollar_text)
    if not m:
        return None
    try:
        value = float(m.group(1))
        kind = "percent" if symbol_span and "%" in symbol_span.get_text() else "dollar"
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
    img_tag = tile.find("img")
    return clean_archive_url(img_tag["src"]) if img_tag and img_tag.has_attr("src") else None

# ────────────────────────────────────────────────────────────────────────────
deals = []

# Extract valid period from command line or HTML
if len(sys.argv) == 4:
    valid_period = {"starts": sys.argv[2], "ends": sys.argv[3]}
else:
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

# Print number of deals with null SKU
null_sku_count = sum(1 for d in deals if not d.get("sku"))
print(f"Number of deals with null SKU: {null_sku_count}") 