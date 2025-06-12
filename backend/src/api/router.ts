import { Hono } from 'hono';
import { Database } from '../db';
import { cors } from 'hono/cors';
import { prettyJSON } from 'hono/pretty-json';
import type { Context } from 'hono';
import { HTTPException } from 'hono/http-exception';

export type Env = {
  DB: D1Database;
};

const app = new Hono<{ Bindings: Env }>();

// Middleware
app.use('*', cors());
app.use('*', prettyJSON());

// Error handling middleware
app.onError((err: Error, c: Context) => {
  console.error(`${err}`);
  const status = err instanceof HTTPException ? err.status : 500;
  return c.json(
    {
      error: {
        message: err.message,
        status,
      },
    },
    status
  );
});

// Health check endpoint
app.get('/', (c: Context) => c.text('Costco Deals Finder API'));

// Get current deals
app.get('/api/deals/today', async (c: Context) => {
  const region = c.req.query('region') || 'US';
  const db = new Database(c.env.DB);

  try {
    const offers = await db.getCurrentOffers(region);
    return c.json({
      data: offers,
      meta: {
        count: offers.length,
        region,
        timestamp: new Date().toISOString(),
      },
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new HTTPException(500, { message: `Failed to fetch current deals: ${error.message}` });
    }
    throw new HTTPException(500, { message: 'An unexpected error occurred' });
  }
});

// Ingest deals
app.post('/api/ingest', async (c: Context) => {
  const db = new Database(c.env.DB);
  const body = await c.req.json();

  // Validate request body
  if (!Array.isArray(body)) {
    throw new HTTPException(400, { message: 'Request body must be an array of deals' });
  }

  try {
    const result = await db.ingestDeals(body);
    return c.json({
      status: 'success',
      message: result.message,
      details: result.details,
    });
  } catch (error) {
    if (error instanceof Error) {
      throw new HTTPException(500, { message: `Failed to ingest deals: ${error.message}` });
    }
    throw new HTTPException(500, { message: 'An unexpected error occurred' });
  }
});

export default app;
