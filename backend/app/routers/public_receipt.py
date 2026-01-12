from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import uuid

from app.database import get_db
from app.models.order import Order
from app.utils.dependencies import get_optional_current_user

router = APIRouter(prefix="/public/orders", tags=["Public Orders - Receipt"])

# Directory for receipt uploads
UPLOAD_DIR = Path("uploads/receipts")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/{order_id}/upload-receipt")
async def upload_receipt(
    order_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
current_user = Depends(get_optional_current_user)
):
    """
    Subir comprobante de pago para un pedido.
    El pedido debe estar en estado PENDING_PAYMENT.
    """
    
    # Validar tipo de archivo
    allowed_types = {'image/jpeg', 'image/png', 'image/jpg', 'image/webp'}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imágenes (JPG, PNG, WEBP)"
        )
    
    # Buscar el pedido
    stmt = select(Order).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    # Generar nombre único para el archivo
    ext = Path(file.filename).suffix.lower()
    filename = f"{order.order_number}_{uuid.uuid4()}{ext}"
    file_path = UPLOAD_DIR / filename
    
    # Guardar archivo
    content = await file.read()
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Actualizar pedido
    order.receipt_url = f"/uploads/receipts/{filename}"
    order.status = "WAITING_CONTACT"  # Cambiar estado a espera de contacto
    
    await db.commit()
    await db.refresh(order)
    
    return {
        "message": "Comprobante subido exitosamente",
        "receipt_url": order.receipt_url,
        "order_status": order.status
    }
