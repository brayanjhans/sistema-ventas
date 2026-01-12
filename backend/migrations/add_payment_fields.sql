-- Migration: Add payment tracking fields to orders table
-- Date: 2026-01-12
-- Description: Add payment_method and receipt_url columns for Yape payment flow

ALTER TABLE orders
ADD COLUMN payment_method VARCHAR(20) NULL AFTER status,
ADD COLUMN receipt_url VARCHAR(500) NULL AFTER payment_method;

-- Optional: Add index for payment method filtering
CREATE INDEX idx_orders_payment_method ON orders(payment_method);
