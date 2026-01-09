from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from app.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.category import Category
from app.utils.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin/analytics", tags=["Admin - Analytics"])


@router.get("/summary")
async def get_analytics_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Obtener resumen de métricas generales.
    """
    # Construir filtro de fechas
    query = select(Order).where(Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED]))
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.where(and_(
            Order.created_at >= start,
            Order.created_at <= end
        ))
    
    # Obtener pedidos
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Calcular métricas
    total_revenue = sum(float(order.total) for order in orders)
    total_orders = len(orders)
    
    # Calcular productos vendidos
    items_query = select(func.sum(OrderItem.quantity)).select_from(OrderItem).join(Order).where(
        Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED])
    )
    
    if start_date and end_date:
        items_query = items_query.where(and_(
            Order.created_at >= start,
            Order.created_at <= end
        ))
    
    items_result = await db.execute(items_query)
    total_products_sold = items_result.scalar() or 0
    
    # Promedio por pedido
    average_order = total_revenue / total_orders if total_orders > 0 else 0
    
    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_products_sold": int(total_products_sold),
        "average_order_value": round(average_order, 2)
    }


@router.get("/revenue")
async def get_revenue_chart(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    period: str = Query(default="day", regex="^(day|week|month)$"),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Obtener datos de ingresos agrupados por período.
    """
    query = select(Order).where(Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED]))
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.where(and_(
            Order.created_at >= start,
            Order.created_at <= end
        ))
    else:
        end = datetime.now()
        start = end - timedelta(days=30)
        query = query.where(and_(
            Order.created_at >= start,
            Order.created_at <= end
        ))
    
    query = query.order_by(Order.created_at)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    revenue_by_period = {}
    
    for order in orders:
        if period == "day":
            key = order.created_at.strftime("%Y-%m-%d")
        elif period == "week":
            key = order.created_at.strftime("%Y-W%W")
        else:
            key = order.created_at.strftime("%Y-%m")
        
        if key not in revenue_by_period:
            revenue_by_period[key] = 0
        
        revenue_by_period[key] += float(order.total)
    
    data = [
        {"period": period_key, "revenue": round(revenue, 2)}
        for period_key, revenue in sorted(revenue_by_period.items())
    ]
    
    return data


@router.get("/top-products")
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=50),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Obtener productos más vendidos.
    """
    query = (
        select(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.subtotal).label('total_revenue')
        )
        .select_from(OrderItem)
        .join(Product, OrderItem.product_id == Product.id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED]))
    )
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.where(and_(
            Order.created_at >= start,
            Order.created_at <= end
        ))
    
    query = (
        query
        .group_by(Product.id, Product.name)
        .order_by(desc('total_sold'))
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "quantity_sold": int(row.total_sold),
            "revenue": round(float(row.total_revenue), 2)
        }
        for row in rows
    ]


@router.get("/sales-by-category")
async def get_sales_by_category(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Obtener ventas agrupadas por categoría.
    """
    query = (
        select(
            Category.id,
            Category.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.subtotal).label('total_revenue')
        )
        .select_from(OrderItem)
        .join(Product, OrderItem.product_id == Product.id)
        .join(Category, Product.category_id == Category.id)
        .join(Order, OrderItem.order_id == Order.id)
        .where(Order.status.in_([OrderStatus.PAID, OrderStatus.DELIVERED]))
    )
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.where(and_(
            Order.created_at >= start,
            Order.created_at <= end
        ))
    
    query = (
        query
        .group_by(Category.id, Category.name)
        .order_by(desc('total_revenue'))
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "category_id": row.id,
            "category_name": row.name,
            "quantity_sold": int(row.total_sold),
            "revenue": round(float(row.total_revenue), 2)
        }
        for row in rows
    ]

@router.get("/low-stock")
async def get_low_stock_products(
    threshold: int = Query(default=5, ge=1),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Obtener productos con stock bajo (crítico).
    """
    query = (
        select(Product)
        .where(and_(Product.stock <= threshold, Product.is_active == True))
        .order_by(Product.stock.asc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "stock": p.stock,
            "price": p.price,
            "image": p.images[0].thumbnail_url if p.images else None
        }
        for p in products
    ]
