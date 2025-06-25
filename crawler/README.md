# Crawler

Python-based data collection system for the Costco Deals Finder.

## Development

### Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Cloudflare account with Workers and D1 enabled

### Setup

1. Create and activate virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file:

   ```bash
   cp .env.example .env
   ```

4. Update ChromeDriver:
   ```bash
   ./update_chromedriver.sh
   ```

## Project Structure

- `src/`: Source code
  - `crawlers/`: Crawler implementations
  - `processors/`: Data processing utilities
  - `utils/`: Shared utilities
- `data/`: Data storage
  - `raw/`: Raw HTML snapshots
  - `processed/`: Processed data files
- `scripts/`: Utility scripts
  - `update_chromedriver.sh`: ChromeDriver update script
  - `run_backfill.sh`: Historical data collection script

## Features

- [ ] Live deal crawling
- [ ] Historical data collection
- [ ] Data validation and cleaning
- [ ] Automated scheduling
- [ ] Error handling and retries

## Usage

### Live Crawling

```bash
python src/crawlers/live_offers.py
```

### Historical Data Collection

```bash
./scripts/run_backfill.sh
```

### Data Processing

```bash
python src/processors/transform_local_deals.py
```

## Output Format

- The crawler outputs data in NDJSON format with accurate local date formatting for start and end dates (YYYY-MM-DD), ensuring correct timeline visualization in the frontend.
- This data is used to power the DealHistoryCard timeline and interactive tooltips in the web UI.

```json
{
  "sku": "string",
  "name": "string",
  "discount": "string",
  "details": "string",
  "starts": "YYYY-MM-DD",
  "ends": "YYYY-MM-DD"
}
```
