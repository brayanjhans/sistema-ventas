"""
Script to clean all test data from the database.
Removes: orders, order_items, products, categories
Keeps: admin user, settings
"""
import asyncio
from sqlalchemy import text
from app.database import async_session_maker

async def clean_database():
    """Remove all test data from database"""
    async with async_session_maker() as session:
        try:
            print("🧹 Iniciando limpieza de base de datos...")
            print("⚠️  Este proceso eliminará TODOS los datos de prueba")
            print("✅ Se mantendrán: usuario admin y configuraciones del sistema\n")
            
            # Disable foreign key checks temporarily (for MySQL)
            await session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            
            # Delete orders and order items first
            result = await session.execute(text("DELETE FROM order_items"))
            print(f"✅ Eliminados {result.rowcount} items de órdenes")
            
            result = await session.execute(text("DELETE FROM orders"))
            print(f"✅ Eliminadas {result.rowcount} órdenes")
            
            # Delete products
            result = await session.execute(text("DELETE FROM products"))
            print(f"✅ Eliminados {result.rowcount} productos")
            
            # Delete categories
            result = await session.execute(text("DELETE FROM categories"))
            print(f"✅ Eliminadas {result.rowcount} categorías")
            
            # Reset auto-increment counters
            await session.execute(text("ALTER TABLE orders AUTO_INCREMENT = 1"))
            await session.execute(text("ALTER TABLE order_items AUTO_INCREMENT = 1"))
            await session.execute(text("ALTER TABLE products AUTO_INCREMENT = 1"))
            await session.execute(text("ALTER TABLE categories AUTO_INCREMENT = 1"))
            print("✅ Contadores reiniciados")
            
            # Re-enable foreign key checks
            await session.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
            
            # Commit changes
            await session.commit()
            
            print("\n✨ Base de datos limpiada exitosamente!")
            print("📝 Ahora puedes cargar tus propios datos reales.")
            print("👤 Usuario admin se mantiene activo.")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error durante la limpieza: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(clean_database())
