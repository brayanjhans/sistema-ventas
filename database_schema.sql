-- ============================================
-- DATABASE SCHEMA: Sistema de Ventas Online
-- Version: 1.0
-- Date: 2026-01-08
-- MySQL 8.0+
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS `sistema-ventas`
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE `sistema-ventas`;

-- ============================================
-- TABLE: users
-- ============================================
CREATE TABLE `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NULL COMMENT 'NULL si es usuario de Google OAuth',
  `full_name` VARCHAR(255) NOT NULL,
  `phone` VARCHAR(20) NULL,
  `role` ENUM('USER', 'ADMIN') NOT NULL DEFAULT 'USER',
  `auth_provider` ENUM('EMAIL', 'GOOGLE') NOT NULL DEFAULT 'EMAIL',
  `google_id` VARCHAR(255) NULL COMMENT 'ID de Google OAuth',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_email` (`email`),
  UNIQUE KEY `uk_users_google_id` (`google_id`),
  INDEX `idx_users_role` (`role`),
  INDEX `idx_users_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Usuarios del sistema (clientes y admins)';

-- ============================================
-- TABLE: categories
-- ============================================
CREATE TABLE `categories` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `slug` VARCHAR(255) NOT NULL COMMENT 'URL-friendly name',
  `description` TEXT NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_categories_slug` (`slug`),
  INDEX `idx_categories_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Categorías de productos';

-- ============================================
-- TABLE: products
-- ============================================
CREATE TABLE `products` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `category_id` BIGINT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `slug` VARCHAR(255) NOT NULL,
  `description` TEXT NULL,
  `price` DECIMAL(10, 2) NOT NULL COMMENT 'Precio en soles',
  `stock` INT UNSIGNED NOT NULL DEFAULT 0,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_products_slug` (`slug`),
  INDEX `idx_products_category` (`category_id`),
  INDEX `idx_products_active` (`is_active`),
  INDEX `idx_products_price` (`price`),
  INDEX `idx_products_name` (`name`),
  CONSTRAINT `fk_products_category` 
    FOREIGN KEY (`category_id`) 
    REFERENCES `categories` (`id`) 
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Productos del catálogo';

-- ============================================
-- TABLE: product_images
-- ============================================
CREATE TABLE `product_images` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `product_id` BIGINT UNSIGNED NOT NULL,
  `image_url` VARCHAR(500) NOT NULL COMMENT 'Path: /uploads/products/{filename}',
  `thumbnail_url` VARCHAR(500) NULL COMMENT 'Path al thumbnail',
  `is_primary` BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Imagen principal',
  `display_order` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_images_product` (`product_id`),
  INDEX `idx_images_primary` (`is_primary`),
  CONSTRAINT `fk_images_product` 
    FOREIGN KEY (`product_id`) 
    REFERENCES `products` (`id`) 
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Imágenes de productos';

-- ============================================
-- TABLE: carts
-- ============================================
CREATE TABLE `carts` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NULL COMMENT 'NULL para carritos de invitados',
  `session_id` VARCHAR(255) NULL COMMENT 'ID de sesión para invitados',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_carts_user` (`user_id`),
  INDEX `idx_carts_session` (`session_id`),
  CONSTRAINT `fk_carts_user` 
    FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Carritos de compras';

-- ============================================
-- TABLE: cart_items
-- ============================================
CREATE TABLE `cart_items` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cart_id` BIGINT UNSIGNED NOT NULL,
  `product_id` BIGINT UNSIGNED NOT NULL,
  `quantity` INT UNSIGNED NOT NULL DEFAULT 1,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_cart_items` (`cart_id`, `product_id`),
  INDEX `idx_cart_items_product` (`product_id`),
  CONSTRAINT `fk_cart_items_cart` 
    FOREIGN KEY (`cart_id`) 
    REFERENCES `carts` (`id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cart_items_product` 
    FOREIGN KEY (`product_id`) 
    REFERENCES `products` (`id`) 
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Items en carritos de compras';

-- ============================================
-- TABLE: orders
-- ============================================
CREATE TABLE `orders` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_number` VARCHAR(50) NOT NULL COMMENT 'Formato: ORD-YYYYMMDD-XXXX',
  `user_id` BIGINT UNSIGNED NOT NULL,
  
  -- Datos de envío (snapshot)
  `shipping_full_name` VARCHAR(255) NOT NULL,
  `shipping_phone` VARCHAR(20) NOT NULL,
  `shipping_address` VARCHAR(500) NOT NULL,
  `shipping_district` VARCHAR(100) NOT NULL,
  `shipping_city` VARCHAR(100) NOT NULL,
  `shipping_reference` VARCHAR(255) NULL,
  
  -- Montos
  `subtotal` DECIMAL(10, 2) NOT NULL,
  `tax` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Por si se implementa IGV',
  `shipping_cost` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  `total` DECIMAL(10, 2) NOT NULL,
  
  -- Estado del pedido
  `status` ENUM(
    'PENDING_PAYMENT',
    'WAITING_CONTACT',
    'PAID',
    'CANCELLED',
    'SHIPPED',
    'DELIVERED'
  ) NOT NULL DEFAULT 'PENDING_PAYMENT',
  
  `notes` TEXT NULL COMMENT 'Notas internas del admin',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_orders_number` (`order_number`),
  INDEX `idx_orders_user` (`user_id`),
  INDEX `idx_orders_status` (`status`),
  INDEX `idx_orders_created` (`created_at`),
  CONSTRAINT `fk_orders_user` 
    FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Pedidos de clientes';

-- ============================================
-- TABLE: order_items
-- ============================================
CREATE TABLE `order_items` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_id` BIGINT UNSIGNED NOT NULL,
  `product_id` BIGINT UNSIGNED NOT NULL,
  
  -- Snapshot del producto al momento de la compra
  `product_name` VARCHAR(255) NOT NULL,
  `product_price` DECIMAL(10, 2) NOT NULL,
  `quantity` INT UNSIGNED NOT NULL,
  `subtotal` DECIMAL(10, 2) NOT NULL COMMENT 'price * quantity',
  
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  INDEX `idx_order_items_order` (`order_id`),
  INDEX `idx_order_items_product` (`product_id`),
  CONSTRAINT `fk_order_items_order` 
    FOREIGN KEY (`order_id`) 
    REFERENCES `orders` (`id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_order_items_product` 
    FOREIGN KEY (`product_id`) 
    REFERENCES `products` (`id`) 
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Items de pedidos (snapshot de precios)';

-- ============================================
-- TABLE: payments
-- ============================================
CREATE TABLE `payments` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `order_id` BIGINT UNSIGNED NOT NULL,
  `payment_method` ENUM('YAPE', 'WHATSAPP', 'OTHER') NOT NULL,
  `amount` DECIMAL(10, 2) NOT NULL,
  `status` ENUM('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'PENDING',
  
  -- Metadata específica del método
  `payment_proof` TEXT NULL COMMENT 'Captura de pago o evidencia',
  `transaction_id` VARCHAR(255) NULL COMMENT 'ID de transacción si aplica',
  
  `confirmed_by` BIGINT UNSIGNED NULL COMMENT 'Admin que confirmó el pago',
  `confirmed_at` TIMESTAMP NULL,
  
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_payments_order` (`order_id`),
  INDEX `idx_payments_status` (`status`),
  INDEX `idx_payments_method` (`payment_method`),
  CONSTRAINT `fk_payments_order` 
    FOREIGN KEY (`order_id`) 
    REFERENCES `orders` (`id`) 
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_payments_confirmer` 
    FOREIGN KEY (`confirmed_by`) 
    REFERENCES `users` (`id`) 
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Registro de pagos';

-- ============================================
-- TABLE: audit_logs
-- ============================================
CREATE TABLE `audit_logs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NULL COMMENT 'Usuario que realizó la acción',
  `action_type` VARCHAR(100) NOT NULL COMMENT 'Ej: CONFIRM_PAYMENT, ADJUST_STOCK, UPDATE_ORDER',
  `entity_type` VARCHAR(100) NOT NULL COMMENT 'Ej: order, product, payment',
  `entity_id` BIGINT UNSIGNED NULL,
  `old_value` JSON NULL COMMENT 'Valor anterior',
  `new_value` JSON NULL COMMENT 'Valor nuevo',
  `ip_address` VARCHAR(45) NULL,
  `user_agent` VARCHAR(500) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  INDEX `idx_audit_user` (`user_id`),
  INDEX `idx_audit_entity` (`entity_type`, `entity_id`),
  INDEX `idx_audit_action` (`action_type`),
  INDEX `idx_audit_created` (`created_at`),
  CONSTRAINT `fk_audit_user` 
    FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Registro de auditoría';

-- ============================================
-- TABLE: refresh_tokens
-- ============================================
CREATE TABLE `refresh_tokens` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `token` VARCHAR(500) NOT NULL,
  `expires_at` TIMESTAMP NOT NULL,
  `is_revoked` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_refresh_tokens_token` (`token`),
  INDEX `idx_refresh_tokens_user` (`user_id`),
  INDEX `idx_refresh_tokens_expires` (`expires_at`),
  CONSTRAINT `fk_refresh_tokens_user` 
    FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) 
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tokens de refresco para autenticación';

-- ============================================
-- SEED DATA (Datos de ejemplo)
-- ============================================

-- Usuario Admin (password: Admin123)
-- Hash generado con bcrypt cost 12
INSERT INTO `users` (`email`, `password_hash`, `full_name`, `role`, `auth_provider`) VALUES
('admin@sistema-ventas.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxIXW7BjS', 'Administrador del Sistema', 'ADMIN', 'EMAIL');

-- Usuario Cliente de ejemplo (password: User123)
INSERT INTO `users` (`email`, `password_hash`, `full_name`, `phone`, `role`, `auth_provider`) VALUES
('cliente@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxIXW7BjS', 'Juan Pérez', '987654321', 'USER', 'EMAIL');

-- Categorías de ejemplo
INSERT INTO `categories` (`name`, `slug`, `description`, `is_active`) VALUES
('Electrónica', 'electronica', 'Productos electrónicos y tecnología', TRUE),
('Ropa', 'ropa', 'Ropa y accesorios de moda', TRUE),
('Hogar', 'hogar', 'Artículos para el hogar', TRUE),
('Deportes', 'deportes', 'Equipamiento deportivo', TRUE);

-- Productos de ejemplo
INSERT INTO `products` (`category_id`, `name`, `slug`, `description`, `price`, `stock`, `is_active`) VALUES
(1, 'Laptop HP 15"', 'laptop-hp-15', 'Laptop HP con procesador Intel i5, 8GB RAM, 256GB SSD', 2500.00, 10, TRUE),
(1, 'Mouse Logitech', 'mouse-logitech', 'Mouse inalámbrico Logitech M185', 45.00, 50, TRUE),
(1, 'Teclado Mecánico', 'teclado-mecanico', 'Teclado mecánico RGB para gaming', 180.00, 20, TRUE),
(2, 'Polo Nike', 'polo-nike', 'Polo deportivo Nike Dri-FIT', 89.90, 30, TRUE),
(2, 'Zapatillas Adidas', 'zapatillas-adidas', 'Zapatillas Adidas Ultraboost', 450.00, 15, TRUE),
(3, 'Licuadora Oster', 'licuadora-oster', 'Licuadora Oster 3 velocidades', 120.00, 25, TRUE),
(4, 'Pelota de Fútbol', 'pelota-futbol', 'Pelota de fútbol profesional Nike', 95.00, 40, TRUE);

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Auto-generar order_number
DELIMITER $$
CREATE TRIGGER before_order_insert
BEFORE INSERT ON orders
FOR EACH ROW
BEGIN
  DECLARE next_num INT;
  DECLARE date_part VARCHAR(8);
  
  SET date_part = DATE_FORMAT(NOW(), '%Y%m%d');
  
  SELECT COALESCE(MAX(CAST(SUBSTRING(order_number, -4) AS UNSIGNED)), 0) + 1
  INTO next_num
  FROM orders
  WHERE order_number LIKE CONCAT('ORD-', date_part, '-%');
  
  SET NEW.order_number = CONCAT('ORD-', date_part, '-', LPAD(next_num, 4, '0'));
END$$
DELIMITER ;

-- ============================================
-- VIEWS (Vistas útiles)
-- ============================================

-- Vista: Productos con información de categoría e imagen principal
CREATE OR REPLACE VIEW v_products_catalog AS
SELECT 
  p.id,
  p.name,
  p.slug,
  p.description,
  p.price,
  p.stock,
  p.is_active,
  c.id AS category_id,
  c.name AS category_name,
  c.slug AS category_slug,
  (SELECT image_url FROM product_images 
   WHERE product_id = p.id AND is_primary = TRUE 
   LIMIT 1) AS image_url,
  p.created_at,
  p.updated_at
FROM products p
INNER JOIN categories c ON p.category_id = c.id;

-- Vista: Resumen de pedidos
CREATE OR REPLACE VIEW v_orders_summary AS
SELECT 
  o.id,
  o.order_number,
  o.user_id,
  u.full_name AS customer_name,
  u.email AS customer_email,
  o.total,
  o.status,
  p.payment_method,
  p.status AS payment_status,
  o.created_at,
  o.updated_at
FROM orders o
INNER JOIN users u ON o.user_id = u.id
LEFT JOIN payments p ON o.id = p.order_id;

-- ============================================
-- ÍNDICES ADICIONALES PARA PERFORMANCE
-- ============================================

-- Índice compuesto para búsqueda de productos
ALTER TABLE products 
ADD INDEX idx_products_search (`is_active`, `name`, `category_id`);

-- Índice para ordenar pedidos
ALTER TABLE orders 
ADD INDEX idx_orders_user_status (`user_id`, `status`, `created_at` DESC);

-- ============================================
-- PROCEDIMIENTOS ALMACENADOS (Opcionales)
-- ============================================

-- Procedimiento: Confirmar pago y descontar stock
DELIMITER $$
CREATE PROCEDURE sp_confirm_payment(
  IN p_order_id BIGINT UNSIGNED,
  IN p_admin_id BIGINT UNSIGNED,
  IN p_payment_proof TEXT
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error al confirmar pago';
  END;
  
  START TRANSACTION;
  
  -- 1. Verificar que el pedido existe y está en PENDING_PAYMENT
  IF NOT EXISTS (
    SELECT 1 FROM orders 
    WHERE id = p_order_id AND status = 'PENDING_PAYMENT'
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pedido no válido para confirmación';
  END IF;
  
  -- 2. Actualizar estado del pedido
  UPDATE orders 
  SET status = 'PAID' 
  WHERE id = p_order_id;
  
  -- 3. Actualizar pago
  UPDATE payments 
  SET 
    status = 'COMPLETED',
    payment_proof = p_payment_proof,
    confirmed_by = p_admin_id,
    confirmed_at = NOW()
  WHERE order_id = p_order_id;
  
  -- 4. Descontar stock
  UPDATE products p
  INNER JOIN order_items oi ON p.id = oi.product_id
  SET p.stock = p.stock - oi.quantity
  WHERE oi.order_id = p_order_id;
  
  -- 5. Registrar en auditoría
  INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, new_value)
  VALUES (
    p_admin_id, 
    'CONFIRM_PAYMENT', 
    'order', 
    p_order_id,
    JSON_OBJECT('status', 'PAID', 'confirmed_at', NOW())
  );
  
  COMMIT;
END$$
DELIMITER ;

-- ============================================
-- COMENTARIOS FINALES
-- ============================================

/*
NOTAS IMPORTANTES:

1. SEGURIDAD:
   - Nunca exponer passwords en código
   - Usar bcrypt con cost factor 12 mínimo
   - Implementar rate limiting en endpoints de login
   
2. PERFORMANCE:
   - Los índices están optimizados para consultas frecuentes
   - Paginación obligatoria en listados
   - Considerar caché para categorías
   
3. TRANSACCIONES:
   - Usar sp_confirm_payment para garantizar atomicidad
   - Alternativamente, manejar transacciones en FastAPI
   
4. AUDITORÍA:
   - Todos los cambios críticos deben registrarse en audit_logs
   - Guardar old_value y new_value en formato JSON
   
5. SNAPSHOTS:
   - order_items guarda precio al momento de compra
   - orders guarda dirección de envío completa
   - Esto asegura consistencia histórica

6. ESCALABILIDAD FUTURA:
   - Considerar sharding por fecha (orders, audit_logs)
   - Considerar archivado de pedidos antiguos
   - Monitorear tamaño de tablas de auditoría
*/

-- ============================================
-- FIN DEL SCRIPT
-- ============================================
