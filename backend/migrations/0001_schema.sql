-- Master list of items (one row per Costco item)
CREATE TABLE IF NOT EXISTS product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku VARCHAR(20) UNIQUE NOT NULL,   -- "1694426"
    name TEXT NOT NULL,                -- canonical name
    category TEXT,                     -- Snacks, Home, Health …
    brand TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Every advertised sale window for a product
CREATE TABLE IF NOT EXISTS offer_period (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES product(id),
    region TEXT DEFAULT 'US',          -- scope: "US" | "Warehouse-Only" | ZIP later
    sale_type TEXT NOT NULL CHECK (sale_type IN ('dollar','percent')),  -- 'dollar' | 'percent'
    discount_low NUMERIC(7,2) NOT NULL,    -- store 4.00 or 25.00
    discount_high NUMERIC(7,2) NOT NULL CHECK (discount_low <= discount_high),  -- =low if fixed
    currency CHAR(3) DEFAULT 'USD',    -- keeps it future-proof
    limit_qty INTEGER,                 -- LIMIT 2
    details TEXT,                      -- "186 ct. Item …"
    starts DATE NOT NULL,
    ends DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, starts, ends, region)  -- ensures no duplicates
);

-- Optional fine-grained snapshots (crawler writes every crawl)
CREATE TABLE IF NOT EXISTS offer_snapshot (
    offer_period_id INTEGER REFERENCES offer_period(id) ON DELETE CASCADE,
    seen_at TIMESTAMP NOT NULL,
    discount_low NUMERIC(7,2),
    discount_high NUMERIC(7,2),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(offer_period_id, seen_at)
);

-- Alias table (if you discover same item under multiple SKUs)
CREATE TABLE IF NOT EXISTS alias (
    product_id INTEGER REFERENCES product(id) ON DELETE CASCADE,
    alt_sku VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
-- Product price history
CREATE INDEX IF NOT EXISTS idx_offer_product_time
    ON offer_period (product_id, starts DESC);

-- Time-range queries for snapshots
CREATE INDEX IF NOT EXISTS idx_snapshot_period_time
    ON offer_snapshot (offer_period_id, seen_at DESC);

-- Additional useful indexes
CREATE INDEX IF NOT EXISTS idx_product_sku ON product(sku);
CREATE INDEX IF NOT EXISTS idx_product_category ON product(category);
CREATE INDEX IF NOT EXISTS idx_offer_period_region ON offer_period(region); 