import asyncio
import requests
from sqlalchemy import select
from app.database import engine
from app.models.category import Category

async def check_url():
    async with engine.connect() as conn:
        # Get category image url
        result = await conn.execute(select(Category.image_url).where(Category.image_url.is_not(None)).limit(1))
        image_url = result.scalar()
        
        if not image_url:
            print("No category images found in DB")
            return

        full_url = f"http://localhost:8000{image_url}"
        print(f"Testing URL: {full_url}")
        
        try:
            response = requests.get(full_url)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {response.headers}")
            if response.status_code == 200:
                print("✅ Access Successful!")
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_url())
