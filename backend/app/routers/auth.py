from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, Token, RefreshTokenRequest,
    UserResponse, GoogleAuthRequest
)
from app.services.auth_service import AuthService
from app.utils.auth import decode_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user with email/password.
    Returns access token and user info.
    """
    try:
        # Create user
        new_user = await AuthService.register_user(db, user_data)
        
        # Generate tokens
        tokens = AuthService.create_tokens(new_user)
        
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role.value
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=dict)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email/password.
    Returns access token and user info.
    """
    user = await AuthService.authenticate_user(
        db,
        credentials.email,
        credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    tokens = AuthService.create_tokens(user)
    
    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "token_type": tokens.token_type,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value
        }
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    payload = AuthService.verify_refresh_token(request.refresh_token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user to generate new tokens
    user = await AuthService.get_user_by_email(db, payload.get("sub"))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate new tokens
    tokens = AuthService.create_tokens(user)
    
    return tokens

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(lambda: None),  # Will implement OAuth2 dependency later
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user info.
    Requires valid access token in Authorization header.
    """
    # This will be improved with proper OAuth2 dependency
    # For now, just a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint will be implemented with OAuth2 dependency"
    )

@router.post("/google-auth", response_model=dict)
async def google_auth(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login or register with Google OAuth.
    Requires Google JWT credential.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        import os
        
        # Verify Google Token
        # Note: In production you should verify the AUDIENCE matches your Client ID
        # client_id = os.getenv('GOOGLE_CLIENT_ID')
        # idinfo = id_token.verify_oauth2_token(request.credential, requests.Request(), client_id)
        
        # For development/MVP we accept the token validated by Google's library
        # (Assuming the client is trustworthy or we verify audience if env var is set)
        
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        idinfo = id_token.verify_oauth2_token(request.credential, requests.Request(), client_id)

        email = idinfo.get('email')
        google_id = idinfo.get('sub')
        name = idinfo.get('name')
        
        if not email:
            raise HTTPException(400, "Invalid Google Token: No email found")

        # Check if user exists
        user = await AuthService.get_user_by_email(db, email)
        
        if user:
            # Update user if not linked yet
            if not user.google_id:
                user.google_id = google_id
                # user.auth_provider = 'GOOGLE' # Optional: Keep original or switch? Let's just link.
                await db.commit()
                await db.refresh(user)
        else:
            # Register new user
            from app.models.user import User, UserRole, AuthProvider
            new_user = User(
                email=email,
                full_name=name,
                role=UserRole.USER,
                auth_provider=AuthProvider.GOOGLE,
                google_id=google_id,
                is_active=True
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            user = new_user

        # Generate tokens
        tokens = AuthService.create_tokens(user)
        
        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "avatar_url": user.avatar_url,
                "auth_provider": user.auth_provider.value
            }
        }
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, f"Invalid Google Token: {str(e)}")
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Google Auth Error: {str(e)}")
