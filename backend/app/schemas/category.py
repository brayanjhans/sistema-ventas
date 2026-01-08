from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    is_active: bool = True

class CategoryCreate(CategoryBase):
    """Schema para crear categoría. El slug se genera automáticamente."""
    pass

class CategoryUpdate(BaseModel):
    """Schema para actualizar categoría. Todos los campos son opcionales."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255, pattern=r'^[a-z0-9-]+$')
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int
    page: int
    pages: int
    limit: int
