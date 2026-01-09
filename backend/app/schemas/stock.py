from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class StockAdjustmentRequest(BaseModel):
    adjustment: int = Field(..., description="Cantidad a sumar (positivo) o restar (negativo)")
    reason: str = Field(..., min_length=3, description="Razón del ajuste de stock")

class StockHistoryItem(BaseModel):
    id: int
    product_name: str
    action_type: str
    old_stock: int
    new_stock: int
    difference: int
    reason: str
    user_email: str
    created_at: datetime

    class Config:
        from_attributes = True
