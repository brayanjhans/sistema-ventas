import asyncio
from sqlalchemy import text
from app.database import engine

async def run_migration():
    print("Iniciando migración...")
    async with engine.begin() as conn:
        try:
            # Check if column exists
            result = await conn.execute(text("SHOW COLUMNS FROM categories LIKE 'image_url'"))
            if result.scalar():
                print("✅ La columna 'image_url' ya existe.")
            else:
                print("⚠️ La columna 'image_url' no existe. Agregando...")
                await conn.execute(text("ALTER TABLE categories ADD COLUMN image_url VARCHAR(500) NULL"))
                print("✅ Columna 'image_url' agregada correctamente.")
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_migration())
    finally:
        # loop.close() # Avoid closing explicitly if it causes issues
        pass
