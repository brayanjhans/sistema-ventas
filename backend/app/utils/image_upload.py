import os
import uuid
from pathlib import Path
from PIL import Image
from fastapi import UploadFile, HTTPException, status
from typing import Tuple, Optional

UPLOAD_DIR = Path("uploads/products")
THUMBNAIL_DIR = Path("uploads/products/thumbnails")
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

def validate_image(file: UploadFile) -> None:
    """Validate image file type and size"""
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size (if available)
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

async def save_upload_file(file: UploadFile) -> Tuple[str, str]:
    """
    Save uploaded image and create thumbnail.
    Returns tuple: (image_url, thumbnail_url)
    """
    validate_image(file)
    
    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid.uuid4()}{ext}"
    
    # Save original image
    file_path = UPLOAD_DIR / filename
    thumbnail_path = THUMBNAIL_DIR / filename
    
    # Read file content
    content = await file.read()
    
    # Save original
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # Create thumbnail (300x300)
    try:
        with Image.open(file_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            
            # Create thumbnail
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            img.save(thumbnail_path, quality=85, optimize=True)
    except Exception as e:
        # Clean up original if thumbnail fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )
    
    # Return relative URLs
    image_url = f"/uploads/products/{filename}"
    thumbnail_url = f"/uploads/products/thumbnails/{filename}"
    
    return image_url, thumbnail_url

def delete_image_files(image_url: str, thumbnail_url: Optional[str] = None) -> None:
    """Delete image and thumbnail files from disk"""
    try:
        # Extract filename from URL
        filename = Path(image_url).name
        
        # Delete original
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
        
        # Delete thumbnail
        if thumbnail_url:
            thumb_filename = Path(thumbnail_url).name
            thumb_path = THUMBNAIL_DIR / thumb_filename
            if thumb_path.exists():
                thumb_path.unlink()
    except Exception as e:
        # Log error but don't raise (files might already be deleted)
        print(f"Error deleting image files: {e}")
