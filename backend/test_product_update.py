import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db_session
from app.models.product import Product
from app.schemas.product import ProductUpdate
from decimal import Decimal

async def test_update():
    async with get_db_session() as db:
        # Get product ID 18
        stmt = select(Product).options(selectinload(Product.images)).where(Product.id == 18)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            print("❌ Product 18 not found")
            return
        
        print(f"✅ Found product: {product.name}")
        print(f"Current data:")
        print(f"  - name: {product.name}")
        print(f"  - description: {product.description}")
        print(f"  - category_id: {product.category_id}")
        print(f"  - price: {product.price}")
        print(f"  - stock: {product.stock}")
        print(f"  - is_active: {product.is_active}")
        
        # Try to update
        update_data = {
            "name": "desayuno sorpresa",
            "description": "desayuno sorpresa , sorpresar inolvidables",
            "category_id": 1,  # Assuming desayunos category ID
            "price": Decimal("50.00"),
            "stock": 50,
            "is_active": True
        }
        
        print(f"\nTrying to update with:")
        for key, value in update_data.items():
            print(f"  - {key}: {value} (type: {type(value).__name__})")
        
        try:
            product_update = ProductUpdate(**update_data)
            print(f"\n✅ ProductUpdate schema validated successfully")
            print(f"Update data: {product_update.model_dump(exclude_unset=True)}")
        except Exception as e:
            print(f"\n❌ ProductUpdate schema validation failed:")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_update())
