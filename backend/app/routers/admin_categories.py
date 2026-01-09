from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.category import Category
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
)
from app.utils.dependencies import get_current_admin_user
from app.utils.helpers import slugify
from app.utils.image_upload import save_upload_file, delete_image_files
from typing import Optional
import math

router = APIRouter(prefix="/admin/categories", tags=["Admin - Categories"])

@router.get("", response_model=CategoryListResponse)
async def list_categories(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    List all categories with pagination and filters.
    Only accessible by ADMIN.
    """
    # Base query
    query = select(Category)
    
    # Apply filters
    if search:
        query = query.where(Category.name.ilike(f"%{search}%"))
    
    if is_active is not None:
        query = query.where(Category.is_active == is_active)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Category.created_at.desc())
    
    # Execute query
    result = await db.execute(query)
    categories = result.scalars().all()
    
    # Calculate pages
    pages = math.ceil(total / limit) if total > 0 else 0
    
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(cat) for cat in categories],
        total=total,
        page=page,
        pages=pages,
        limit=limit
    )

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Create new category.
    Slug is auto-generated from name.
    Only accessible by ADMIN.
    """
    # Generate slug from name
    slug = slugify(category_data.name)
    
    # Check if slug already exists
    stmt = select(Category).where(Category.slug == slug)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with slug '{slug}' already exists"
        )
    
    # Create new category
    new_category = Category(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        is_active=category_data.is_active
    )
    
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    
    return CategoryResponse.model_validate(new_category)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Get category by ID.
    Only accessible by ADMIN.
    """
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return CategoryResponse.model_validate(category)

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Update category.
    Only accessible by ADMIN.
    """
    # Get existing category
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Update fields
    update_data = category_data.model_dump(exclude_unset=True)
    
    # If name is updated, regenerate slug
    if 'name' in update_data:
        new_slug = slugify(update_data['name'])
        
        # Check if new slug conflicts with another category
        stmt = select(Category).where(
            Category.slug == new_slug,
            Category.id != category_id
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with slug '{new_slug}' already exists"
            )
        
        update_data['slug'] = new_slug
    
    # Apply updates
    for field, value in update_data.items():
        setattr(category, field, value)
    
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.model_validate(category)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Soft delete category (marks as inactive).
    Only accessible by ADMIN.
    """
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Soft delete
    category.is_active = False
    
    await db.commit()
    
    return None

@router.post("/{category_id}/image", response_model=CategoryResponse)
async def upload_category_image(
    category_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Upload image for category.
    Only accessible by ADMIN.
    """
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Delete old image if exists
    if category.image_url:
        try:
            delete_image_files(category.image_url)
        except Exception as e:
            print(f"Error deleting old image: {e}")
            
    # Save new image
    image_url, _ = await save_upload_file(file)
    
    # Update category
    category.image_url = image_url
    
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.model_validate(category)
