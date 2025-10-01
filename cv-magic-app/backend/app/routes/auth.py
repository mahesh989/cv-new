"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from app.models.auth import LoginRequest, TokenResponse, UserData, RegisterRequest
from app.core.auth import authenticate_user, create_access_token, create_refresh_token
from app.core.dependencies import get_current_user
from app.config import settings
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_database
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse)
async def register(payload: RegisterRequest, db: Session = Depends(get_database)):
    """Register a new user and return auth tokens"""
    # Normalize email
    email = payload.email.strip().lower()

    # Check if user already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    # Create new user
    user = User(
        username=email.split("@")[0],
        email=email,
        full_name=payload.name,
        is_active=True,
        is_verified=False,
    )
    user.set_password(payload.password)

    db.add(user)
    db.commit()
    db.refresh(user)

    # Ensure user-specific directories exist
    from app.utils.user_path_utils import ensure_user_directories
    ensure_user_directories(user.email)

    # Create tokens
    user_data = {"id": str(user.id), "email": user.email}
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
        user=UserData(
            id=str(user.id),
            email=user.email,
            name=user.full_name or user.username,
            created_at=user.created_at,
            is_active=user.is_active,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_database)):
    """
    User login endpoint
    
    Args:
        credentials: Login credentials (email and password, both can be empty)
        
    Returns:
        TokenResponse with access token and user data
    """
    # Authenticate user (checks DB; admin fallback supported)
    user = authenticate_user(credentials.email, credentials.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ensure user-specific directories exist immediately on login
    from app.utils.user_path_utils import ensure_user_directories
    # Enforce user directory creation; raise error on failure
    base_path = ensure_user_directories(user.email)
    if not base_path or not base_path.exists():
        raise HTTPException(status_code=500, detail="Failed to initialize user storage directories")

    # Create tokens
    user_dict = {"id": user.id, "email": user.email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user.id)
    
    # Return token response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,  # Convert to seconds
        user=user
    )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """User logout endpoint"""
    return {"message": "Logout endpoint - to be implemented"}


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh JWT token endpoint"""
    return {"message": "Token refresh endpoint - to be implemented"}


@router.get("/profile", response_model=UserData)
async def get_profile(current_user: UserData = Depends(get_current_user)):
    """
    Get user profile endpoint
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile data
    """
    return current_user


@router.put("/profile")
async def update_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Update user profile endpoint"""
    return {"message": "Profile update endpoint - to be implemented"}


@router.get("/debug-token")
async def debug_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Debug endpoint to check token status"""
    from app.core.auth import verify_token
    try:
        token_data = verify_token(credentials.credentials)
        return {
            "status": "valid",
            "user_id": token_data.user_id,
            "email": token_data.email,
            "expires_at": token_data.exp.isoformat(),
            "issued_at": token_data.iat.isoformat()
        }
    except HTTPException as e:
        return {
            "status": "invalid",
            "error": e.detail,
            "status_code": e.status_code
        }


@router.post("/refresh-session")
async def refresh_session():
    """Create a new session token for development"""
    from app.core.auth import create_demo_user, create_access_token, create_refresh_token
    from app.models.auth import TokenResponse
    
    # Create a fresh demo user and tokens
    user = create_demo_user()
    user_dict = {"id": user.id, "email": user.email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
        user=user
    )
