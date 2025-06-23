# Costco Deals Finder

A web application that helps users track and analyze Costco deals and savings.

## Project Structure

- `frontend/`: SvelteKit-based web interface
- `backend/`: Cloudflare Worker with D1 database
- `crawler/`: Python-based data collection system

## Key Features

- **Deal Search**: Search through all historical deals by keyword.
- **Image Toggling**: Enable or disable product image loading to save bandwidth.
- **Daily Deals**: View all active deals for the current day.

## Technical Stack

- Frontend: SvelteKit + TypeScript
- Backend: Cloudflare Workers + D1
- Testing: Vitest (for TypeScript/JavaScript) + Playwright (for E2E)
- Data Pipeline: Python + Playwright
- CI/CD: GitHub Actions

## Development Setup

### Prerequisites

- Node.js (v18 or later)
- Python 3.8+
- Cloudflare Workers CLI (wrangler)
- Git

### Getting Started

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd costco-deals-finder
   ```

2. Install root dependencies:

   ```bash
   npm install
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your Cloudflare credentials
   ```

4. Install and set up each component:

   **Frontend:**

   ```bash
   cd frontend
   npm install
   ```

   **Backend:**

   ```bash
   cd backend
   npm install
   # Create local D1 database
   wrangler d1 create costco-dev
   # Apply migrations
   wrangler d1 execute costco-dev --file=./migrations/0000_init.sql
   ```

   **Crawler:**

   ```bash
   cd crawler
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. Start development servers:

   ```bash
   # Frontend (in one terminal)
   cd frontend
   npm run dev

   # Backend (in another terminal)
   cd backend
   npm run dev
   ```

## Environment Variables & Secrets

- **Root `.env`**: Contains shared configuration and Cloudflare credentials
- **Frontend**: Uses environment variables from root `.env` prefixed with `PUBLIC_`
- **Backend**: Uses `wrangler.toml`/`wrangler.dev.toml` for config, and `wrangler secret` for secrets
- **CI/CD**: Store secrets in GitHub Actions Secrets

## Project Status

🚧 Under Development 🚧

### Completed Tasks (Phase 1)

- [x] Initialize project structure
- [x] Set up development environment
- [x] Configure TypeScript and SvelteKit
- [x] Set up local D1 stub for development
- [x] Configure environment variables strategy
- [x] Set up GitHub repository and CI/CD
  - [x] Configure GitHub Actions
  - [x] Set up deployment workflows
  - [x] Set up testing workflows
  - [ ] Configure GitHub Secrets (future task)

### Completed Tasks (Phase 2)

- [x] Design and implement database schema
- [x] Create Cloudflare Worker API endpoints
- [x] Set up testing framework
- [x] Implement deal ingestion pipeline (crawler and NDJSON output)

### Next Steps

- [x] Complete Phase 4: Frontend Development (Step 1)
  - [x] Home page displays today's deals in a responsive grid of DealCards
  - [x] Navbar for navigation (Home, Historical Deals, Search)
  - [x] Frontend fetches deals using user's local date (timezone-aware)
  - [x] /api/deals/today endpoint supports a date parameter for local time
- [ ] Step 2: Historical Deals UI
  - [ ] Create /history page with date picker
  - [ ] Fetch and display deals for a selected date
- [ ] Continue backend and integration improvements

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
