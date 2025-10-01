"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.auth import LoginRequest, RegisterRequest, TokenResponse, UserData
from app.models.user import User
from app.core.auth import authenticate_user, create_access_token, create_refresh_token
from app.core.dependencies import get_current_user, get_database
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse)
async def register(register_data: RegisterRequest, db: Session = Depends(get_database)):
    """
    User registration endpoint
    
    Args:
        register_data: Registration data (email, password, full_name)
        db: Database session
        
    Returns:
        TokenResponse with access token and user data
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == register_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=register_data.email,
        username=register_data.email.split('@')[0],  # Use email prefix as username
        full_name=register_data.full_name or register_data.email.split('@')[0],
        is_active=True,
        is_verified=True  # Auto-verify for now
    )
    
    # Set password (this will hash it)
    new_user.set_password(register_data.password)
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create user data for response
    user_data = UserData(
        id=str(new_user.id),
        email=new_user.email,
        name=new_user.full_name or new_user.email.split('@')[0],
        created_at=new_user.created_at,
        is_active=new_user.is_active
    )
    
    # Create tokens
    user_dict = {"id": user_data.id, "email": user_data.email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user_data.id)
    
    # Ensure user-specific directories exist
    from app.utils.user_path_utils import ensure_user_directories
    base_path = ensure_user_directories(user_data.email)
    if not base_path or not base_path.exists():
        raise HTTPException(status_code=500, detail="Failed to initialize user storage directories")
    
    # Return token response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,  # Convert to seconds
        user=user_data
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_database)):
    """
    User login endpoint - requires valid credentials
    
    Args:
        credentials: Login credentials (email and password)
        db: Database session
        
    Returns:
        TokenResponse with access token and user data
    """
    # Find user in database
    user = db.query(User).filter(User.email == credentials.email.lower().strip()).first()
    
    if not user or not user.verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create user data for response
    user_data = UserData(
        id=str(user.id),
        email=user.email,
        name=user.full_name or user.email.split('@')[0],
        created_at=user.created_at,
        is_active=user.is_active
    )
    
    # Ensure user-specific directories exist immediately on login
    from app.utils.user_path_utils import ensure_user_directories
    base_path = ensure_user_directories(user_data.email)
    if not base_path or not base_path.exists():
        raise HTTPException(status_code=500, detail="Failed to initialize user storage directories")

    # Create tokens
    user_dict = {"id": user_data.id, "email": user_data.email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user_data.id)
    
    # Return token response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,  # Convert to seconds
        user=user_data
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
