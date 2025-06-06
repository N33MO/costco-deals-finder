-- Insert test products
INSERT INTO product (sku, name, category, brand) VALUES
('1234567', 'Kirkland Signature Organic Extra Virgin Olive Oil', 'Grocery', 'Kirkland Signature'),
('2345678', 'Charmin Ultra Soft Toilet Paper', 'Household', 'Charmin'),
('3456789', 'Member''s Mark Premium Paper Towels', 'Household', 'Member''s Mark');

-- Insert test offers
INSERT INTO offer_period (
    product_id, region, sale_type, discount_low, discount_high,
    currency, limit_qty, details, starts, ends
) VALUES
(1, 'US', 'dollar', 5.00, 5.00, 'USD', 2, '2-pack, 2L each', date('now', '-1 day'), date('now', '+14 days')),
(2, 'US', 'percent', 20.00, 20.00, 'USD', 1, '30 rolls', date('now', '-1 day'), date('now', '+30 days')),
(3, 'US', 'dollar', 3.00, 3.00, 'USD', NULL, '12 rolls', date('now'), date('now', '+10 days'));

-- Insert test snapshots
INSERT INTO offer_snapshot (
    offer_period_id, seen_at, discount_low, discount_high, details
) VALUES
(1, datetime('now', '-1 day'), 5.00, 5.00, '2-pack, 2L each'),
(2, datetime('now', '-1 day'), 20.00, 20.00, '30 rolls'),
(3, datetime('now'), 3.00, 3.00, '12 rolls'); 