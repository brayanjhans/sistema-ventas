from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    WAITING_CONTACT = "WAITING_CONTACT"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"


# ==================== REQUEST SCHEMAS ====================

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    # Datos del cliente (para clientes sin registro también)
    customer_name: str = Field(min_length=1, max_length=255)
    customer_email: Optional[EmailStr] = None
    customer_phone: str = Field(min_length=1, max_length=20)
    
    # Datos de envío
    shipping_address: str = Field(min_length=1, max_length=500)
    district: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    reference: Optional[str] = Field(None, max_length=255)
    
    # Notas adicionales
    notes: Optional[str] = None
    
    # Método de pago
    payment_method: Optional[str] = Field(None, max_length=20)
    
    # Items del pedido
    items: List[OrderItemCreate] = Field(min_length=1)
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== RESPONSE SCHEMAS ====================

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int
    subtotal: Decimal
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    
    # Datos de envío
    shipping_full_name: str
    shipping_phone: str
    shipping_address: str
    shipping_district: str
    shipping_city: str
    shipping_reference: Optional[str]
    
    # Montos
    subtotal: Decimal
    tax: Decimal
    shipping_cost: Decimal
    total: Decimal
    
    # Estado
    status: str
    notes: Optional[str]
    
    # Items (opcional, para detalle completo)
    items: Optional[List[OrderItemResponse]] = None
    
    # Fechas
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    id: int
    order_number: str
    shipping_full_name: str  # Nombre del cliente
    total: Decimal
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
