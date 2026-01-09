from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.settings import Settings
from app.schemas.settings import SettingsUpdate, SettingsResponse
from app.utils.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin/settings", tags=["Admin - Settings"])

@router.get("", response_model=SettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Get system settings. Creates default settings if none exist.
    """
    stmt = select(Settings).limit(1)
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings
        settings = Settings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings

@router.put("", response_model=SettingsResponse)
async def update_settings(
    settings_data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin_user)
):
    """
    Update system settings.
    """
    stmt = select(Settings).limit(1)
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = Settings()
        db.add(settings)
    
    # Update fields
    for field, value in settings_data.model_dump().items():
        setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    
    return settings
