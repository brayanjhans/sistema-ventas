import asyncio
import sys
sys.path.insert(0, 'C:\\laragon\\www\\sistema-ventas\\backend')

from app.database import async_session_maker
from app.models.product import Product
from app.models.order import Order, OrderItem
from sqlalchemy import select

async def test_order_creation():
    async with async_session_maker() as db:
        try:
            # Verificar que existe el producto 7
            result = await db.execute(select(Product).where(Product.id == 7))
            product = result.scalar_one_or_none()
            
            if not product:
                print("ERROR: Producto 7 no existe")
                return
            
            print(f"Producto encontrado: {product.name}, Stock: {product.stock}")
            
            # Intentar crear una orden de prueba
            from decimal import Decimal
            import time
            import random
            
            timestamp = int(time.time())
            random_num = random.randint(1000, 9999)
            order_number = f"ORD-{timestamp}-{random_num}"
            
            new_order = Order(
                order_number=order_number,
                user_id=1,
                shipping_full_name="Test User",
                shipping_phone="123456789",
                shipping_address="Calle 123",
                shipping_district="Lima",
                shipping_city="Lima",
                shipping_reference="",
                subtotal=Decimal("1222.00"),
                tax=Decimal("0.00"),
                shipping_cost=Decimal("0.00"),
                total=Decimal("1222.00"),
                status="PENDING_PAYMENT",
                notes=""
            )
            
            db.add(new_order)
            await db.flush()
            
            print(f"Orden creada con ID: {new_order.id}")
            
            # Crear item
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name=product.name,
                product_price=product.price,
                quantity=1,
                subtotal=Decimal(str(product.price))
            )
            
            db.add(order_item)
            
            # Actualizar stock
            product.stock -= 1
            
            await db.commit()
            await db.refresh(new_order)
            
            print(f"✅ ÉXITO! Orden {new_order.order_number} creada correctamente")
            
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_order_creation())
