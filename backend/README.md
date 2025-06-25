# Backend

Cloudflare Worker with D1 database for the Costco Deals Finder.

## Development

### Prerequisites

- Node.js (v18 or later)
- Cloudflare Workers CLI (wrangler)
- Cloudflare account with Workers and D1 enabled

### Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create `.env` file:

   ```bash
   cp .env.example .env
   ```

3. Set up local D1 database:

   ```bash
   wrangler d1 create costco-dev
   ```

4. Apply migrations:

   ```bash
   wrangler d1 execute costco-dev --file=./migrations/0001_schema.sql
   ```

5. Start development server:
   ```bash
   npm run dev
   ```

### Environment Variables & Secrets

- Non-secret variables (e.g., ENVIRONMENT) are set in `wrangler.toml` or `wrangler.dev.toml`.
- **Secrets** (API keys, etc.) should be set using Wrangler:
  ```bash
  wrangler secret put SECRET_NAME
  ```
  These are not stored in code and are available to your Worker at runtime.

### Testing

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run unit tests only
npm run test:unit

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode
npm run test:ci
```

## Project Structure

- `src/`: Source code
  - `api/`: API route handlers
  - `db/`: Database access layer
  - `types/`: TypeScript type definitions
  - `index.ts`: Main Worker entry point
- `test/`: Test files
  - `unit/`: Unit tests
    - `api/`: API route tests
  - `helpers/`: Test utilities
  - `migrations/`: Test database schema
- `migrations/`: Production database migrations

## API Endpoints

- All endpoints return deal periods with accurate local date formatting, supporting the frontend's timeline visualization and tooltips.
- The search endpoint returns all historical deals for a product, including overlapping and cross-year periods, for use in the DealHistoryCard timeline UI.

### GET /api/deals/today
Get today's active deals.

**Query Parameters:**
- `region` (optional): Filter deals by region (default: 'US')
- `date` (optional): Date in YYYY-MM-DD format (from user's local timezone; defaults to UTC if not provided)

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "product_id": 1,
      "region": "US",
      "sale_type": "dollar",
      "discount_low": 5.00,
      "discount_high": 5.00,
      "currency": "USD",
      "limit_qty": 2,
      "details": "Test details",
      "starts": "2024-03-20",
      "ends": "2024-04-03",
      "created_at": "2024-03-20T00:00:00Z",
      "updated_at": "2024-03-20T00:00:00Z"
    }
  ],
  "meta": {
    "count": 1,
    "region": "US",
    "timestamp": "2024-03-20T00:00:00Z"
  }
}
```

### GET /api/deals/search
Search for deals by a keyword. The search is performed on the product name.

**Query Parameters:**
- `q` (required): The search query string.

**Response:**
Returns an array of all historical deals for products matching the search query, sorted by the most recent start date. The response format is identical to `GET /api/deals/today`.
- Each deal includes start and end dates in `YYYY-MM-DD` format (local time), discount, channel, and other details for timeline and tooltip display.

## Database Schema

See `migrations/0001_schema.sql` for the complete schema.

## Features

- [x] Basic API structure with Hono
- [x] D1 database integration
- [x] Unit testing setup
- [ ] Integration testing
- [x] Deal ingestion pipeline (data is ingested via the Python-based crawler and loaded into the D1 database for API access)
- [x] Search functionality
- [ ] Historical data support
- [ ] Rate limiting
- [ ] Authentication
- [x] /api/deals/today supports a 'date' parameter for local time (frontend sends user's local date)
