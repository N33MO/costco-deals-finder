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
- [ ] Search and filtering
- [ ] User preferences
- [ ] Accessibility support
