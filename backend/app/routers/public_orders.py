from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.order_schemas import OrderCreate, OrderResponse, OrderItemResponse
from app.utils.dependencies import get_optional_current_user

router = APIRouter(prefix="/public/orders", tags=["Public Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Crear un nuevo pedido desde el carrito.
    
    - Valida stock disponible para cada producto
    - Crea el pedido y los items
    - Actualiza el stock de los productos
    - Retorna el pedido creado con order_number
    """
    
    # Si no hay usuario autenticado, usar usuario predeterminado (ID 1)
    user_id = current_user.id if current_user else 1
    
    # Validar que todos los productos existan y tengan stock
    product_ids = [item.product_id for item in order_data.items]
    result = await db.execute(
        select(Product).where(
            Product.id.in_(product_ids),
            Product.is_active == True
        )
    )
    products = result.scalars().all()
    
    if len(products) != len(product_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uno o más productos no están disponibles"
        )
    
    # Crear diccionario de productos para fácil acceso
    products_dict = {p.id: p for p in products}
    
    # Validar stock y calcular totales
    subtotal = Decimal("0.00")
    order_items_data = []
    
    for item_data in order_data.items:
        product = products_dict.get(item_data.product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Producto {item_data.product_id} no encontrado"
            )
        
        # Validar stock
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}"
            )
        
        # Calcular subtotal del item
        item_subtotal = Decimal(str(product.price)) * item_data.quantity
        subtotal += item_subtotal
        
        order_items_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_price": product.price,
            "quantity": item_data.quantity,
            "subtotal": item_subtotal
        })
    
    # Calcular total (por ahora sin impuestos ni costos de envío)
    tax = Decimal("0.00")
    shipping_cost = Decimal("0.00")
    total = subtotal + tax + shipping_cost
    
    # Generar número de pedido único
    import time
    import random
    timestamp = int(time.time())
    random_num = random.randint(1000, 9999)
    order_number = f"ORD-{timestamp}-{random_num}"
    
    # Crear el pedido
    new_order = Order(
        order_number=order_number,
        user_id=user_id,
        shipping_full_name=order_data.customer_name,
        shipping_phone=order_data.customer_phone,
        shipping_address=order_data.shipping_address,
        shipping_district=order_data.district,
        shipping_city=order_data.city,
        shipping_reference=order_data.reference,
        subtotal=subtotal,
        tax=tax,
        shipping_cost=shipping_cost,
        total=total,
        status="PENDING_PAYMENT",
        payment_method=order_data.payment_method if hasattr(order_data, 'payment_method') else None,
        notes=order_data.notes
    )
    
    db.add(new_order)
    await db.flush()  # Para obtener el ID del pedido
    
    # Crear los items del pedido y actualizar stock
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            **item_data
        )
        db.add(order_item)
        
        # Actualizar stock del producto
        product = products_dict[item_data["product_id"]]
        product.stock -= item_data["quantity"]
    
    # Guardar todos los cambios
    try:
        await db.commit()
        await db.refresh(new_order)
        
        # Retornar el pedido creado
        return OrderResponse(
            id=new_order.id,
            order_number=new_order.order_number,
            user_id=new_order.user_id,
            shipping_full_name=new_order.shipping_full_name,
            shipping_phone=new_order.shipping_phone,
            shipping_address=new_order.shipping_address,
            shipping_district=new_order.shipping_district,
            shipping_city=new_order.shipping_city,
            shipping_reference=new_order.shipping_reference,
            subtotal=new_order.subtotal,
            tax=new_order.tax,
            shipping_cost=new_order.shipping_cost,
            total=new_order.total,
            status=new_order.status,
            notes=new_order.notes,
            created_at=new_order.created_at,
            updated_at=new_order.updated_at
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el pedido: {str(e)}"
        )

