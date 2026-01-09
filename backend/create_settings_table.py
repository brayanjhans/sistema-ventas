import asyncio
from app.database import engine, Base
from app.models.settings import Settings

async def create_tables():
    print("Creating settings table...")
    async with engine.begin() as conn:
        await conn.run_sync(Settings.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_tables())
