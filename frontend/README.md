# Frontend

SvelteKit-based web interface for the Costco Deals Finder.

## Development

### Prerequisites

- Node.js (v18 or later)
- npm or yarn

### Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Create `.env` file:

   ```bash
   cp .env.example .env
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

### Building

```bash
npm run build
```

### Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```

## Project Structure

- `src/`: Source code
  - `lib/`: Shared utilities and components
  - `routes/`: Page components
  - `app.html`: HTML template
  - `app.d.ts`: TypeScript declarations
  - `app.css`: Global styles

## Features

- [x] Responsive home page with grid of DealCards for today's deals
- [x] Navbar for navigation (Home, Historical Deals, Search)
- [x] Fetches deals using user's local date (timezone-aware)
- [ ] Historical deals by date
- [x] Search and filtering
- [x] User preferences
- [ ] Accessibility support

## Features Overview

- **Search Page**: A dedicated `/search` route allows users to find products by keyword. It fetches all historical deals for matching items and displays them.
- **Image Loading Toggle**: A global toggle in the navbar allows users to enable or disable the loading of product images. This preference is managed by a Svelte store (`src/lib/stores/settings.ts`) and is disabled by default to save bandwidth.
