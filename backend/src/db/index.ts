import { D1Database } from '@cloudflare/workers-types';
import {
  Product,
  OfferPeriod,
  OfferSnapshot,
  Alias,
  CreateProduct,
  CreateOfferPeriod,
  CreateOfferSnapshot,
  CreateAlias,
} from '../types/schema';

// Add type definitions for D1's transaction API
interface D1Transaction {
  prepare<T = unknown>(query: string): D1PreparedStatement<T>;
}

interface D1PreparedStatement<T = unknown> {
  bind(...values: unknown[]): D1PreparedStatement<T>;
  first<T = unknown>(): Promise<T | null>;
  all<T = unknown>(): Promise<D1Result<T>>;
  run(): Promise<D1Result<T>>;
}

interface D1Result<T = unknown> {
  success: boolean;
  error?: string;
  results?: T[];
  meta?: {
    duration: number;
    changes: number;
    last_row_id: number;
  };
}

// Extend D1Database type to include transaction API
declare module '@cloudflare/workers-types' {
  interface D1Database {
    transaction<T>(callback: (tx: D1Transaction) => Promise<T>): Promise<T>;
  }
}

export class Database {
  constructor(private db: D1Database) {}

  // Product methods
  async getProductBySku(sku: string): Promise<Product | null> {
    const result = await this.db
      .prepare('SELECT * FROM product WHERE sku = ?')
      .bind(sku)
      .first<Product>();
    return result;
  }

  async createProduct(product: CreateProduct): Promise<Product> {
    const result = await this.db
      .prepare(
        `
                INSERT INTO product (sku, name, category, brand)
                VALUES (?, ?, ?, ?)
                RETURNING *
            `
      )
      .bind(product.sku, product.name, product.category, product.brand)
      .first<Product>();
    if (!result) throw new Error('Failed to create product');
    return result;
  }

  // Offer Period methods
  async getCurrentOffers(
    region: string = 'US',
    date?: string
  ): Promise<
    Array<
      OfferPeriod & {
        sku: string;
        name: string;
        category: string | null;
        brand: string | null;
        image_url: string | null;
      }
    >
  > {
    const now = date || new Date().toISOString().split('T')[0];
    const result = await this.db
      .prepare(
        `
          SELECT
            offer_period.*,
            product.sku,
            product.name,
            product.category,
            product.brand,
            product.image_url
          FROM offer_period
          JOIN product ON offer_period.product_id = product.id
          WHERE offer_period.region = ? AND offer_period.starts <= ? AND offer_period.ends >= ?
          ORDER BY offer_period.starts DESC
        `
      )
      .bind(region, now, now)
      .all<
        OfferPeriod & {
          sku: string;
          name: string;
          category: string | null;
          brand: string | null;
          image_url: string | null;
        }
      >();
    return result.results;
  }

  async createOfferPeriod(offer: CreateOfferPeriod): Promise<OfferPeriod> {
    const result = await this.db
      .prepare(
        `
                INSERT INTO offer_period (
                    product_id, region, sale_type, discount_low, discount_high,
                    currency, limit_qty, details, starts, ends
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                RETURNING *
            `
      )
      .bind(
        offer.product_id,
        offer.region,
        offer.sale_type,
        offer.discount_low,
        offer.discount_high,
        offer.currency,
        offer.limit_qty,
        offer.details,
        offer.starts,
        offer.ends
      )
      .first<OfferPeriod>();
    if (!result) throw new Error('Failed to create offer period');
    return result;
  }

  // Offer Snapshot methods
  async createOfferSnapshot(snapshot: CreateOfferSnapshot): Promise<OfferSnapshot> {
    const result = await this.db
      .prepare(
        `
                INSERT INTO offer_snapshot (
                    offer_period_id, seen_at, discount_low, discount_high, details
                )
                VALUES (?, ?, ?, ?, ?)
                RETURNING *
            `
      )
      .bind(
        snapshot.offer_period_id,
        snapshot.seen_at,
        snapshot.discount_low,
        snapshot.discount_high,
        snapshot.details
      )
      .first<OfferSnapshot>();
    if (!result) throw new Error('Failed to create offer snapshot');
    return result;
  }

  // Alias methods
  async getProductByAltSku(altSku: string): Promise<Product | null> {
    const result = await this.db
      .prepare(
        `
                SELECT p.* FROM product p
                JOIN alias a ON p.id = a.product_id
                WHERE a.alt_sku = ?
            `
      )
      .bind(altSku)
      .first<Product>();
    return result;
  }

  async createAlias(alias: CreateAlias): Promise<Alias> {
    const result = await this.db
      .prepare(
        `
                INSERT INTO alias (product_id, alt_sku)
                VALUES (?, ?)
                RETURNING *
            `
      )
      .bind(alias.product_id, alias.alt_sku)
      .first<Alias>();
    if (!result) throw new Error('Failed to create alias');
    return result;
  }

  async ingestDeals(
    deals: Array<{
      product: {
        sku: string;
        name: string;
        category?: string;
        brand?: string | null;
        image_url?: string | null;
      };
      offer_period: {
        region: string;
        channel?: string | null;
        sale_type: 'dollar' | 'percent';
        discount_low: number;
        discount_high: number;
        currency: string;
        limit_qty?: number | null;
        details?: string;
        starts: string;
        ends: string;
      };
      snapshot: {
        seen_at: string;
        discount_low: number;
        discount_high: number;
        details?: string;
      };
    }>
  ): Promise<{
    success: boolean;
    message: string;
    details?: { count: number; timestamp: string };
  }> {
    // Process deals in batches
    const batchSize = 10; // Process 10 deals at a time
    for (let i = 0; i < deals.length; i += batchSize) {
      const batch = deals.slice(i, i + batchSize);
      const batchPromises = batch.map(async deal => {
        // 1. Insert or update product
        const productResult = await this.db
          .prepare(
            `INSERT INTO product (sku, name, category, brand, image_url)
              VALUES (?, ?, ?, ?, ?)
              ON CONFLICT(sku) DO UPDATE SET
                name = excluded.name,
                category = COALESCE(excluded.category, product.category),
                brand = COALESCE(excluded.brand, product.brand),
                image_url = COALESCE(excluded.image_url, product.image_url),
                updated_at = CURRENT_TIMESTAMP
              RETURNING id`
          )
          .bind(
            deal.product.sku,
            deal.product.name,
            deal.product.category || null,
            deal.product.brand || null,
            deal.product.image_url || null
          )
          .first<{ id: number }>();

        if (!productResult) {
          throw new Error(`Failed to insert/update product: ${deal.product.sku}`);
        }

        const productId = productResult.id;

        // 2. Insert offer period
        const offerResult = await this.db
          .prepare(
            `INSERT INTO offer_period (
              product_id, region, sale_type, discount_low, discount_high,
              currency, limit_qty, details, starts, ends, channel
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_id, starts, ends, region) DO UPDATE SET
              sale_type = excluded.sale_type,
              discount_low = excluded.discount_low,
              discount_high = excluded.discount_high,
              currency = excluded.currency,
              limit_qty = excluded.limit_qty,
              details = excluded.details,
              channel = COALESCE(excluded.channel, offer_period.channel),
              updated_at = CURRENT_TIMESTAMP
            RETURNING id`
          )
          .bind(
            productId,
            deal.offer_period.region,
            deal.offer_period.sale_type,
            deal.offer_period.discount_low,
            deal.offer_period.discount_high,
            deal.offer_period.currency,
            deal.offer_period.limit_qty || null,
            deal.offer_period.details || null,
            deal.offer_period.starts,
            deal.offer_period.ends,
            deal.offer_period.channel || null
          )
          .first<{ id: number }>();

        if (!offerResult) {
          throw new Error(`Failed to insert/update offer period for product: ${deal.product.sku}`);
        }

        const offerPeriodId = offerResult.id;

        // 3. Insert snapshot
        await this.db
          .prepare(
            `INSERT INTO offer_snapshot (
              offer_period_id, seen_at, discount_low, discount_high, details
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(offer_period_id, seen_at) DO UPDATE SET
              discount_low = excluded.discount_low,
              discount_high = excluded.discount_high,
              details = excluded.details`
          )
          .bind(
            offerPeriodId,
            deal.snapshot.seen_at,
            deal.snapshot.discount_low,
            deal.snapshot.discount_high,
            deal.snapshot.details || null
          )
          .run();
      });

      // Wait for all operations in the batch to complete
      await Promise.all(batchPromises);
    }

    return {
      success: true,
      message: `Successfully ingested ${deals.length} deals`,
      details: {
        count: deals.length,
        timestamp: new Date().toISOString(),
      },
    };
  }
}
