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
- [x] **DealHistoryCard Timeline**: Visualizes all historical deals for a product in a year-by-year, month-by-month timeline. Partial month coverage is shown with triangle highlights, and full months are fully highlighted.
- [x] **Interactive Tooltips**: Hover over any highlighted month to see detailed deal info, including discount, valid period, limit, and channel, with visually distinct highlights.
- [x] **Accurate Local Date Handling**: All deal periods are displayed using local time, ensuring correct month alignment regardless of timezone.

## Features Overview

- **Search Page**: A dedicated `/search` route allows users to find products by keyword. It fetches all historical deals for matching items and displays them.
- **Timeline Visualization**: Each product's deal history is shown as a timeline, with each year as a row and each month as a box. Partial month coverage is indicated with a triangle highlight, and full months are fully highlighted. Hovering a highlighted month shows a tooltip with all deal details.
- **Image Loading Toggle**: A global toggle in the navbar allows users to enable or disable the loading of product images. This preference is managed by a Svelte store (`src/lib/stores/settings.ts`) and is disabled by default to save bandwidth.

### Environment Variables

The frontend expects an **optional** environment variable `VITE_API_URL`.

• Leave it empty when the site is hosted on the same origin as the Worker (Pages + custom domain).
• Set it to the full origin of the Worker when they live on different sub-domains during local dev or multi-origin deploys, e.g.

```dotenv
VITE_API_URL=http://localhost:8787         # local dev
VITE_API_URL=https://api.deals.example.com # production
```

The helper `src/lib/api.ts` automatically prefixes requests with this base URL.
