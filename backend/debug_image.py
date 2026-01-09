import asyncio
from sqlalchemy import select
from app.database import engine, get_db
from app.models.category import Category
from pathlib import Path
import os

async def check_category_image():
    async with engine.connect() as conn:
        # Buscar categorías con imagen
        result = await conn.execute(select(Category.name, Category.image_url).where(Category.image_url.is_not(None)))
        categories = result.fetchall()
        
        print(f"Found {len(categories)} categories with images:")
        for name, image_url in categories:
            print(f"\nCategory: {name}")
            print(f"DB URL: {image_url}")
            
            # Check file existence
            if image_url:
                # Remove leading / if present for path joining
                rel_path = image_url.lstrip('/')
                full_path = Path(os.getcwd()) / rel_path
                exists = full_path.exists()
                print(f"Checking path: {full_path}")
                print(f"File exists: {'✅ YES' if exists else '❌ NO'}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_category_image())
