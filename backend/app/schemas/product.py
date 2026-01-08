from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    thumbnail_url: Optional[str]
    is_primary: bool
    display_order: int
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category_id: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    is_active: bool = True
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

class ProductCreate(ProductBase):
    """Schema para crear producto. El slug se genera automáticamente."""
    pass

class ProductUpdate(BaseModel):
    """Schema para actualizar producto. Todos los campos son opcionales."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    category_id: int
    price: Decimal
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageResponse] = []
    
    class Config:
        from_attributes = True

class ProductListItem(BaseModel):
    """Schema simplificado para listados (sin imágenes para eficiencia)"""
    id: int
    name: str
    slug: str
    category_id: int
    price: Decimal
    stock: int
    is_active: bool
    image_url: Optional[str] = None  # Solo imagen principal
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    items: List[ProductListItem]
    total: int
    page: int
    pages: int
    limit: int
