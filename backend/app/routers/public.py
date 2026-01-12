from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
import math

from app.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.category import Category
from app.schemas.order_schemas import OrderResponse
from app.schemas.product import ProductResponse, ProductListItem, ProductListResponse
from app.schemas.category import CategoryResponse

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/categories", response_model=List[CategoryResponse])
async def get_active_categories(db: AsyncSession = Depends(get_db)):
    """
    Obtener todas las categorías activas (público).
    """
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.name)
    )
    categories = result.scalars().all()
    return categories


@router.get("/products", response_model=ProductListResponse)
async def get_public_products(
    limit: int = Query(default=8, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = Query(default="newest", pattern="^(newest|price_asc|price_desc|name)$"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener productos públicos con filtros y paginación.
    Solo muestra productos activos y con stock disponible.
    """
    # 1. Base query for active products with stock
    base_query = select(Product).where(
        Product.is_active == True,
        Product.stock > 0
    )
    
    # 2. Apply filters
    if category_id:
        base_query = base_query.where(Product.category_id == category_id)
    
    if min_price is not None:
        base_query = base_query.where(Product.price >= min_price)
        
    if max_price is not None:
        base_query = base_query.where(Product.price <= max_price)
    
    if search:
        search_filter = (
            Product.name.ilike(f"%{search}%") | 
            Product.description.ilike(f"%{search}%")
        )
        base_query = base_query.where(search_filter)

    # 3. Calculate total count (before pagination)
    count_query = select(func.count()).select_from(base_query.subquery())
    result_count = await db.execute(count_query)
    total = result_count.scalar() or 0

    # 4. Apply sorting
    if sort_by == "newest":
        base_query = base_query.order_by(desc(Product.created_at))
    elif sort_by == "price_asc":
        base_query = base_query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        base_query = base_query.order_by(Product.price.desc())
    elif sort_by == "name":
        base_query = base_query.order_by(Product.name.asc())
    
    # 5. Apply pagination
    offset = (page - 1) * limit
    final_query = base_query.limit(limit).offset(offset).options(
        selectinload(Product.images),
        selectinload(Product.category)
    )
    
    result = await db.execute(final_query)
    products = result.scalars().all()
    
    # 6. Transform to ProductListItem (for response)
    # Note: ProductListItem expects 'image_url' which is the thumbnail of the primary image
    items = []
    for p in products:
        primary_image = next((img for img in p.images if img.is_primary), None)
        if not primary_image and p.images:
            primary_image = p.images[0]
            
        items.append(ProductListItem(
            id=p.id,
            name=p.name,
            slug=p.slug,
            category_id=p.category_id,
            category=p.category, # Include category object
            price=p.price,
            stock=p.stock,
            is_active=p.is_active,
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
async def get_product_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un producto por su slug (público).
    """
    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.category)
        )
        .where(Product.slug == slug, Product.is_active == True)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    return product


@router.get("/products/{product_id}/addons", response_model=List[ProductListItem])
async def get_product_addons(
    product_id: int,
    limit: int = Query(default=3, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener productos complementarios (add-ons) para un producto.
    
    Lógica:
    1. Productos de precio menor o similar (complementos)
    2. Categorías complementarias predefinidas (chocolates, vinos, tarjetas)
    3. Excluye el producto actual
    """
    # Obtener producto actual
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    current_product = result.scalar_one_or_none()
    
    if not current_product:
        return []
    
    # Definir categorías complementarias típicas (puedes ajustar según tu BD)
    # Chocolates, Vinos, Tarjetas, Peluches pequeños, etc.
    complementary_categories = ["Chocolates", "Vinos", "Tarjetas", "Dulces"]
    
    # Query para productos complementarios
    query = (
        select(Product)
        .options(selectinload(Product.images), selectinload(Product.category))
        .where(
            Product.is_active == True,
            Product.stock > 0,
            Product.id != product_id,
            # Precio menor o similar (hasta 50% del precio del producto principal)
            Product.price <= (current_product.price * 0.5)
        )
        .order_by(func.random())  # Aleatorio para variedad
        .limit(limit)
    )
    
    result = await db.execute(query)
    addons = result.scalars().all()
    
    # Mapear a ProductListItem
    return [
        ProductListItem(
            id=p.id,
            name=p.name,
            slug=p.slug,
            category_id=p.category_id,
            category=p.category,
            price=p.price,
            stock=p.stock,
            is_active=p.is_active,
            image_url=p.images[0].image_url if p.images else None
        )
        for p in addons
    ]


@router.get("/orders/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener detalles de un pedido por su número de orden (público).
    
    - No requiere autenticación
    - Retorna información completa del pedido
    - Incluye lista de items/productos
    """
    
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.order_number == order_number)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado"
        )
    
    return order
