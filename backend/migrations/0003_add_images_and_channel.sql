-- Add image_url to product table
ALTER TABLE product ADD COLUMN image_url TEXT;

-- Add channel to offer_period table
ALTER TABLE offer_period ADD COLUMN channel TEXT;