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
   wrangler d1 execute costco-dev --file=./migrations/0000_init.sql
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
# Unit tests
npm run test

# Integration tests
npm run test:integration
```

## Project Structure

- `src/`: Source code
  - `db/`: Database migrations and utilities
  - `lib/`: Shared utilities
  - `worker.ts`: Main Worker implementation
- `test/`: Test files
  - `unit/`: Unit tests
  - `integration/`: Integration tests
- `migrations/`: SQL migration files

## API Endpoints

- `GET /api/deals/today`: Get today's deals
- `POST /api/deals/ingest`: Ingest new deals (protected)
- `GET /api/deals/search`: Search deals
- `GET /api/deals/history`: Get historical deals

## Database Schema

See `migrations/0000_init.sql` for the complete schema.

## Features

- [ ] Deal ingestion pipeline
- [ ] Search functionality
- [ ] Historical data support
- [ ] Rate limiting
- [ ] Authentication
