import asyncio
from sqlalchemy import text
from app.database import engine

async def check_columns():
    async with engine.connect() as conn:
        try:
            # Simple query to check if columns work
            result = await conn.execute(text("SELECT shipping_base_cost, business_hours FROM settings LIMIT 1"))
            print("✅ Columns exist!")
        except Exception as e:
            print(f"❌ Error querying columns: {e}")

if __name__ == "__main__":
    # Fix for Windows Event Loop Closed
    try:
        asyncio.run(check_columns())
    except RuntimeError:
        pass
