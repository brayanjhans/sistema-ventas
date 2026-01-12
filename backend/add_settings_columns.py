import asyncio
from sqlalchemy import text
from app.database import engine

async def add_columns():
    async with engine.begin() as conn:
        print("Adding new columns to settings table...")
        
        # List of columns to add
        columns = [
            ("shipping_base_cost", "FLOAT DEFAULT 0.0"),
            ("free_shipping_threshold", "FLOAT DEFAULT 0.0"),
            ("business_hours", "TEXT"),
            ("social_facebook", "TEXT"),
            ("social_instagram", "TEXT"),
            ("social_tiktok", "TEXT")
        ]

        for col_name, col_type in columns:
            try:
                # Try to add column
                await conn.execute(text(f"ALTER TABLE settings ADD COLUMN {col_name} {col_type}"))
                print(f"✅ Added column {col_name}")
            except Exception as e:
                # Ignore if column likely exists (error messages vary by DB)
                print(f"⚠️  Could not add column {col_name} (might already exist): {e}")

    print("Database update complete.")

if __name__ == "__main__":
    asyncio.run(add_columns())
