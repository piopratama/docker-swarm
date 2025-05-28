CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    product_name TEXT NOT NULL,
    total_price NUMERIC
);
