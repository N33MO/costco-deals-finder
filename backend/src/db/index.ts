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
  async getCurrentOffers(region: string = 'US'): Promise<OfferPeriod[]> {
    const now = new Date().toISOString().split('T')[0];
    const result = await this.db
      .prepare(
        `
                SELECT * FROM offer_period 
                WHERE region = ? AND starts <= ? AND ends >= ?
                ORDER BY starts DESC
            `
      )
      .bind(region, now, now)
      .all<OfferPeriod>();
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
}
