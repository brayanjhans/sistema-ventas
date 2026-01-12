import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy import select
from app.database import async_session_maker
from app.models.product import Product

async def check_product():
    async with async_session_maker() as db:
        # Check product 19
        stmt = select(Product).where(Product.id == 19)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if product:
            print(f"Product ID: {product.id}")
            print(f"Name: {product.name}")
            print(f"Slug: '{product.slug}'")  # Quotes to see if there are spaces
            print(f"Active: {product.is_active}")
            print(f"Stock: {product.stock}")
        else:
            print("Product 19 not found")

        # Also search by slug to be sure
        slug = "desayuno-sorpresa"
        stmt = select(Product).where(Product.slug == slug)
        result = await db.execute(stmt)
        p_slug = result.scalar_one_or_none()
        
        if p_slug:
            print(f"\nFound by slug '{slug}': ID {p_slug.id}")
        else:
            print(f"\nNOT FOUND by slug '{slug}'")

if __name__ == "__main__":
    asyncio.run(check_product())
