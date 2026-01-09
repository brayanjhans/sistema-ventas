from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.product import Product, ProductImage
from app.models.category import Category
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, 
    ProductListResponse, ProductListItem, ProductImageResponse
)
from app.utils.dependencies import get_current_admin_user
from app.utils.helpers import slugify
from app.utils.image_upload import save_upload_file, delete_image_files
from typing import Optional
import math

router = APIRouter(prefix="/admin/products", tags=["Admin - Products"])

@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """List all products with pagination and filters. Admin only."""
    
    # Base query with eager loading of images and category
    query = select(Product).options(
        selectinload(Product.images),
        selectinload(Product.category)
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
    
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Product.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    products = result.scalars().all()
    
    # Build response items
    items = []
    for product in products:
        # Get primary image if exists
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
            image_url=primary_image.thumbnail_url if primary_image else None,
            category=product.category
        ))
    
    pages = math.ceil(total / limit) if total > 0 else 0
    
    return ProductListResponse(
        items=items,
        total=total,
        page=page,
        pages=pages,
        limit=limit
    )

@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Create new product. Admin only."""
    
    # Verify category exists
    stmt = select(Category).where(Category.id == product_data.category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Generate slug
    slug = slugify(product_data.name)
    
    # Check slug uniqueness
    stmt = select(Product).where(Product.slug == slug)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with slug '{slug}' already exists"
        )
    
    # Create product
    new_product = Product(
        name=product_data.name,
        slug=slug,
        description=product_data.description,
        category_id=product_data.category_id,
        price=product_data.price,
        stock=product_data.stock,
        is_active=product_data.is_active
    )
    
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product, ['images'])
    
    return ProductResponse.model_validate(new_product)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Get product by ID with images. Admin only."""
    
    stmt = select(Product).options(selectinload(Product.images)).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return ProductResponse.model_validate(product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Update product. Admin only."""
    
    # Get product
    stmt = select(Product).options(selectinload(Product.images)).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = product_data.model_dump(exclude_unset=True)
    
    # If category changed, verify it exists
    if 'category_id' in update_data:
        stmt = select(Category).where(Category.id == update_data['category_id'])
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # If name changed, regenerate slug
    if 'name' in update_data:
        new_slug = slugify(update_data['name'])
        
        # Check uniqueness
        stmt = select(Product).where(
            Product.slug == new_slug,
            Product.id != product_id
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with slug '{new_slug}' already exists"
            )
        
        update_data['slug'] = new_slug
    
    # Apply updates
    for field, value in update_data.items():
        setattr(product, field, value)
    
    await db.commit()
    await db.refresh(product)
    
    return ProductResponse.model_validate(product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Soft delete product. Admin only."""
    
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.is_active = False
    await db.commit()
    
    return None

@router.post("/{product_id}/images", response_model=ProductImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    is_primary: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Upload image for product. Admin only."""
    
    # Verify product exists
    stmt = select(Product).options(selectinload(Product.images)).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Save image
    image_url, thumbnail_url = await save_upload_file(file)
    
    # If is_primary, unmark other images
    if is_primary:
        for img in product.images:
            img.is_primary = False
    
    # Create image record
    display_order = len(product.images)
    new_image = ProductImage(
        product_id=product_id,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        is_primary=is_primary,
        display_order=display_order
    )
    
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    
    return ProductImageResponse.model_validate(new_image)

@router.delete("/{product_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image(
    product_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """Delete product image. Admin only."""
    
    stmt = select(ProductImage).where(
        ProductImage.id == image_id,
        ProductImage.product_id == product_id
    )
    result = await db.execute(stmt)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Delete files
    delete_image_files(image.image_url, image.thumbnail_url)
    
    # Delete record
    await db.delete(image)
    await db.commit()
    
    return None


@router.delete("/delete/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Eliminar o desactivar un producto (solo admin).
    - Si el producto tiene pedidos asociados: SOFT DELETE (marca como inactivo)
    - Si no tiene pedidos: ELIMINA permanentemente el producto y sus imágenes
    """
    print(f"🗑️ DELETE REQUEST - Product ID: {product_id}")
    
    # Buscar el producto con sus imágenes
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.images))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    product_name = product.name
    print(f"✅ Producto encontrado: {product_name}")
    
    # Verificar si tiene pedidos asociados
    from app.models.order import OrderItem
    result_orders = await db.execute(
        select(OrderItem).where(OrderItem.product_id == product_id)
    )
    has_orders = result_orders.scalar_one_or_none() is not None
    
    if has_orders:
        # SOFT DELETE: Solo marcar como inactivo
        print(f"⚠️ El producto tiene pedidos asociados. Haciendo SOFT DELETE...")
        product.is_active = False
        await db.commit()
        await db.refresh(product)
        
        print(f"✅ Producto '{product_name}' marcado como INACTIVO (soft delete)")
        return {
            "message": f"Producto '{product_name}' desactivado correctamente",
            "deleted": False,
            "soft_delete": True,
            "reason": "El producto tiene pedidos asociados"
        }
    
    # HARD DELETE: Eliminar permanentemente
    print(f"🔥 El producto NO tiene pedidos. Eliminando PERMANENTEMENTE...")
    
    # Eliminar imágenes físicas del servidor
    image_urls = [img.image_url for img in product.images]
    if image_urls:
        print(f"📁 Eliminando {len(image_urls)} imágenes...")
        for url in image_urls:
            try:
                delete_image_files(url)
            except Exception as e:
                print(f"⚠️ Error al eliminar imagen {url}: {e}")
    
    # Eliminar producto PERMANENTEMENTE de la base de datos
    await db.delete(product)
    await db.commit()
    
    print(f"✅ Producto '{product_name}' eliminado PERMANENTEMENTE")
    
    return {
        "message": f"Producto '{product_name}' eliminado permanentemente",
        "deleted": True,
        "soft_delete": False
    }
