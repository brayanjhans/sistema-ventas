from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.product import Product
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.stock import StockAdjustmentRequest, StockHistoryItem
from app.utils.dependencies import get_current_admin_user
import json

router = APIRouter(prefix="/admin/stock", tags=["Admin - Stock"])

@router.patch("/products/{product_id}", status_code=status.HTTP_200_OK)
async def adjust_product_stock(
    product_id: int,
    adjustment_data: StockAdjustmentRequest,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Adjust the stock of a product.
    """
    # 1. Get Product
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    old_stock = product.stock
    new_stock = old_stock + adjustment_data.adjustment
    
    if new_stock < 0:
        raise HTTPException(status_code=400, detail=f"Stock insuficiente. Stock actual: {old_stock}")

    # 2. Update Product
    product.stock = new_stock
    
    # 3. Create Audit Log
    log_entry = AuditLog(
        user_id=current_admin.id,
        action_type="ADJUST_STOCK",
        entity_type="product",
        entity_id=product.id,
        old_value=json.dumps({"stock": old_stock}),
        new_value=json.dumps({
            "stock": new_stock,
            "difference": adjustment_data.adjustment,
            "reason": adjustment_data.reason
        })
    )
    db.add(log_entry)
    
    await db.commit()
    await db.refresh(product)
    
    return {"message": "Stock actualizado", "current_stock": product.stock}

@router.get("/history", response_model=list[StockHistoryItem])
async def get_stock_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Get stock adjustment history from audit logs.
    """
    # Join with User and Product (snapshot-ish via entity_id) if needed, 
    # but for now we join User to get who did it.
    # Note: Product name might be lost if deleted, but AuditLog assumes persistence usually.
    # Ideally checking entity_type='product' and action_type='ADJUST_STOCK'
    
    # Simple query on AuditLogs
    query = (
        select(AuditLog, User.email, Product.name)
        .join(User, AuditLog.user_id == User.id)
        .outerjoin(Product, AuditLog.entity_id == Product.id) # Outer join in case product deleted
        .where(AuditLog.action_type == "ADJUST_STOCK")
        .order_by(desc(AuditLog.created_at))
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    history_items = []
    for log, email, product_name in rows:
        # Parse JSON
        try:
            old_val = json.loads(log.old_value) if log.old_value else {}
            new_val = json.loads(log.new_value) if log.new_value else {}
            
            item = StockHistoryItem(
                id=log.id,
                product_name=product_name or f"Producto ID {log.entity_id}",
                action_type=log.action_type,
                old_stock=old_val.get("stock", 0),
                new_stock=new_val.get("stock", 0),
                difference=new_val.get("difference", 0),
                reason=new_val.get("reason", "Sin razón"),
                user_email=email,
                created_at=log.created_at
            )
            history_items.append(item)
        except Exception as e:
            print(f"Error parsing log {log.id}: {e}")
            continue
            
    return history_items
