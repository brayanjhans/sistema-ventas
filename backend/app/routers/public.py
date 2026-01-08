from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from database import get_db
from app.models.product import Product, ProductImage
from app.models.category import Category
from app.schemas.product import ProductResponse, ProductListResponse, ProductListItem
from app.schemas.category import CategoryResponse
from typing import Optional
import math

router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/categories", response_model=list[CategoryResponse])
async def list_public_categories(
    db: AsyncSession = Depends(get_db)
):
    """Get all active categories for public access"""
    stmt = select(Category).where(Category.is_active == True).order_by(Category.name)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    
    return [CategoryResponse.model_validate(cat) for cat in categories]

@router.get("/products", response_model=ProductListResponse)
async def list_public_products(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: str = Query("newest", pattern="^(newest|price_asc|price_desc|name)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active products for public access with filters.
    
    Sort options:
    - newest: Most recent first
    - price_asc: Price low to high
    - price_desc: Price high to low
    - name: Alphabetical
    """
    
    # Base query - only active products
    query = select(Product).options(selectinload(Product.images)).where(
        Product.is_active == True,
        Product.stock > 0  # Only show products in stock
    )
    
    # Apply filters
    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    
    # Apply sorting
    if sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    elif sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "name":
        query = query.order_by(Product.name.asc())
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()
    
    # Build response items
    items = []
    for product in products:
        # Get primary image
        primary_image = next((img for img in product.images if img.is_primary), None)
        if not primary_image and product.images:
            primary_image = product.images[0]
        
        items.append(ProductListItem(
            id=product.id,
            name=product.name,
            slug=product.slug,
            category_id=product.category_id,
            price=product.price,
            stock=product.stock,
            is_active=product.is_active,
            image_url=primary_image.thumbnail_url if primary_image else None
        ))
    
    pages = math.ceil(total / limit) if total > 0 else 0
    
    return ProductListResponse(
        items=items,
        total=total,
        page=page,
        pages=pages,
        limit=limit
    )

@router.get("/products/{slug}", response_model=ProductResponse)
async def get_public_product(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get product detail by slug for public access"""
    
    stmt = select(Product).options(selectinload(Product.images)).where(
        Product.slug == slug,
        Product.is_active == True
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse.model_validate(product)
