-- Migración: Agregar campo image_url a categorías
-- Ejecutar en MySQL después de verificar que no hay datos críticos

ALTER TABLE categories 
ADD COLUMN image_url VARCHAR(500) NULL 
AFTER description;

-- Opcional: Agregar índice si se hará búsqueda por imagen
-- CREATE INDEX idx_categories_image ON categories(image_url);
