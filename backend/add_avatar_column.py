import asyncio
from app.database import engine, Base
from sqlalchemy import text
from app.models.user import User

async def add_avatar_column():
    print("Starting migration: Add avatar_url to users table...")
    async with engine.begin() as conn:
        try:
            # Check if column exists
            print("Checking if column exists...")
            result = await conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = 'users' "
                "AND COLUMN_NAME = 'avatar_url'"
            ))
            exists = result.scalar() > 0
            
            if exists:
                print("Column 'avatar_url' already exists. Skipping.")
            else:
                print("Adding 'avatar_url' column...")
                await conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500) NULL"))
                print("Column 'avatar_url' added successfully.")
                
        except Exception as e:
            print(f"Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    asyncio.run(add_avatar_column())
