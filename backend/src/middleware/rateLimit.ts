import type { MiddlewareHandler } from 'hono';
import { HTTPException } from 'hono/http-exception';

export interface RateLimitOptions {
  /** Milliseconds for each window, e.g. 60_000 for 1 min */
  windowMs: number;
  /** Maximum number of requests allowed per window */
  max: number;
}

interface RateInfo {
  expiresAt: number;
  count: number;
}

/**
 * Simple in-memory IP+route rate-limiting middleware for Cloudflare Workers.
 * NOTE: Each Worker isolate has its own counter, so limits are approximate
 * across the entire edge. Good enough for small sites without paid WAF rules.
 */
export function rateLimit({ windowMs, max }: RateLimitOptions): MiddlewareHandler {
  // Map key: `${ip}:${path}` => RateInfo
  const store = new Map<string, RateInfo>();

  return async (c, next) => {
    const ip =
      c.req.header('CF-Connecting-IP') ||
      c.req.header('X-Forwarded-For')?.split(',')[0].trim() ||
      'unknown';

    const route = c.req.path; // includes leading /
    const key = `${ip}:${route}`;
    const now = Date.now();

    let info = store.get(key);
    if (!info || info.expiresAt <= now) {
      // reset window
      info = { count: 0, expiresAt: now + windowMs };
      store.set(key, info);
    }

    info.count += 1;

    // Log every request with route and ip
    console.info(`[rate-limit] ${ip} -> ${route} (${info.count}/${max})`);

    if (info.count > max) {
      // Build nice HTML response
      const html = `<!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8" />
          <title>Too Many Requests</title>
          <style>
            body { font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; background-color: #f8fafc; }
            .card { text-align: center; padding: 2rem 3rem; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); background: white; }
            h1 { font-size: 2rem; margin-bottom: 0.5rem; color: #dc2626; }
            p { margin: 0.5rem 0; color: #475569; }
          </style>
        </head>
        <body>
          <div class="card">
            <h1>429: Too Many Requests</h1>
            <p>You have exceeded the allowed request rate.</p>
            <p>Please wait a minute and try again.</p>
          </div>
        </body>
        </html>`;

      throw new HTTPException(429, {
        res: new Response(html, {
          status: 429,
          headers: {
            'Content-Type': 'text/html; charset=utf-8',
            'Retry-After': Math.ceil((info.expiresAt - now) / 1000).toString(),
          },
        }),
      });
    }

    await next();
  };
}
