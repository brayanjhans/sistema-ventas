-- Cleanup script to remove all test data
-- Keeps: admin user, settings
-- Removes: orders, order_items, products, categories

SET FOREIGN_KEY_CHECKS = 0;

-- Delete order items
DELETE FROM order_items;

-- Delete orders  
DELETE FROM orders;

-- Delete products
DELETE FROM products;

-- Delete categories
DELETE FROM categories;

-- Reset auto-increment counters
ALTER TABLE orders AUTO_INCREMENT = 1;
ALTER TABLE order_items AUTO_INCREMENT = 1;
ALTER TABLE products AUTO_INCREMENT = 1;
ALTER TABLE categories AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;

-- Show summary
SELECT 'Database cleaned successfully!' AS status;
SELECT COUNT(*) AS remaining_orders FROM orders;
SELECT COUNT(*) AS remaining_products FROM products;
SELECT COUNT(*) AS remaining_categories FROM categories;
SELECT COUNT(*) AS admin_users FROM users WHERE role = 'ADMIN';
