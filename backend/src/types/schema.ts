export interface Product {
  id: number;
  sku: string;
  name: string;
  category: string | null;
  brand: string | null;
  created_at: string;
  updated_at: string;
}

export interface OfferPeriod {
  id: number;
  product_id: number;
  region: string;
  sale_type: 'dollar' | 'percent';
  discount_low: number;
  discount_high: number;
  currency: string;
  limit_qty: number | null;
  details: string | null;
  starts: string;
  ends: string;
  created_at: string;
  updated_at: string;
}

export interface OfferSnapshot {
  offer_period_id: number;
  seen_at: string;
  discount_low: number | null;
  discount_high: number | null;
  details: string | null;
  created_at: string;
}

export interface Alias {
  product_id: number;
  alt_sku: string;
  created_at: string;
}

// Type for creating a new product
export type CreateProduct = Omit<Product, 'id' | 'created_at' | 'updated_at'>;

// Type for creating a new offer period
export type CreateOfferPeriod = Omit<OfferPeriod, 'id' | 'created_at' | 'updated_at'>;

// Type for creating a new offer snapshot
export type CreateOfferSnapshot = Omit<OfferSnapshot, 'created_at'>;

// Type for creating a new alias
export type CreateAlias = Omit<Alias, 'created_at'>;
