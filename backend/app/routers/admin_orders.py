from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from typing import List, Optional

from app.database import get_db
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.order_schemas import (
    OrderResponse,
    OrderListResponse,
    OrderStatusUpdate
)
from app.utils.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])


@router.get("", response_model=List[OrderListResponse])
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Listar todos los pedidos (solo admin).
    
    - Paginación con skip y limit
    - Filtro por estado
    - Búsqueda por order_number o nombre de cliente
    """
    
    stmt = select(Order)
    
    # Filtrar por estado si se proporciona
    if status:
        stmt = stmt.where(Order.status == status)
    
    # Búsqueda por número de pedido o nombre de cliente
    if search:
        stmt = stmt.where(
            or_(
                Order.order_number.ilike(f"%{search}%"),
                Order.shipping_full_name.ilike(f"%{search}%")
            )
        )
    
    # Ordenar y paginar
    stmt = stmt.order_by(desc(Order.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    orders = result.scalars().all()
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Obtener detalle completo de un pedido (solo admin).
    
    - Incluye todos los items del pedido
    """
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualizar el estado de un pedido (solo admin).
    
    - Cambia el estado del pedido
    - Opcionalmente actualiza las notas
    """
    
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    # Actualizar estado
    order.status = status_update.status
    
    # Actualizar notas si se proporcionan
    if status_update.notes:
        order.notes = status_update.notes
    
    try:
        await db.commit()
        await db.refresh(order)
        
        # Recargar con items para la respuesta
        from sqlalchemy.orm import selectinload
        result = await db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        order = result.scalar_one()
        
        return order
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estado: {str(e)}"
        )

