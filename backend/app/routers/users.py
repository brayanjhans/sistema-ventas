from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.services.auth_service import AuthService
from typing import Optional
import shutil
import os
import uuid

router = APIRouter(prefix="/users", tags=["Users"])

UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def get_current_user_from_token(
    token: str = Depends(lambda: None), # Placeholder, handled by middleware or future oauth2
    db: AsyncSession = Depends(get_db)
) -> User:
    # This is a temporary helper until full OAuth2 dependency is set up
    # In a real scenario, this would decode the token and fetch user
    # For now, we rely on the client sending a valid token and maybe simple validation
    # OR better: reuse logic from auth.py if available, or just fetch by ID for now if passed
    # Actually, we need to decode the token here to get the user ID
    from app.utils.auth import decode_token
    from fastapi.security import OAuth2PasswordBearer
    
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
    
    # We need a way to get the token. 
    # Since we don't have the fully decoupled dependency yet, let's implement a basic one here
    pass

# We need a proper dependency to get current user. 
# Let's create a reusable one in `app/dependencies.py` if it doesn't exist, or locally here.
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    from app.utils.auth import decode_token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")
        
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/me/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, detail="File must be an image")
    
    # Generate unique filename
    extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(500, detail=f"Could not save file: {str(e)}")
        
    # Update user in DB
    # Construct public URL (assuming static file serving is set up)
    # URL format: /uploads/avatars/filename
    # Note: In production, this might need full domain prepended
    avatar_url = f"/uploads/avatars/{filename}"
    
    current_user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(current_user)
    
    return current_user
