"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from app.models.auth import (
    LoginRequest, TokenResponse, UserData, UserRegistration, 
    UserResponse, EmailVerificationRequest, AdminLoginRequest
)
from app.core.auth import authenticate_user, create_access_token, create_refresh_token
from app.core.dependencies import get_current_user, get_admin_user
from app.core.admin_auth import AdminAuth
from app.database import get_database
from app.services.user_service import UserService
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegistration):
    """User registration endpoint"""
    db = next(get_database())
    user_service = UserService(db)
    
    try:
        # Create new user
        user = user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        return user_service.to_user_response(user)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    User login endpoint
    
    Args:
        credentials: Login credentials (email and password)
        
    Returns:
        TokenResponse with access token and user data
    """
    # Authenticate user
    user = authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
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


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(credentials: AdminLoginRequest):
    """
    Admin login endpoint
    
    Args:
        credentials: Admin login credentials
        
    Returns:
        TokenResponse with admin access token
    """
    # Authenticate admin
    if not AdminAuth.authenticate_admin(credentials.email, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create admin user data
    admin_user = AdminAuth.create_admin_user()
    
    # Create admin token
    access_token = AdminAuth.create_admin_token()
    refresh_token = create_refresh_token("admin")
    
    # Return token response
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
        user=admin_user
    )


@router.post("/verify-email")
async def verify_email(request: EmailVerificationRequest):
    """Email verification endpoint"""
    # For now, just return success
    # In production, you would verify the token and activate the user
    return {"message": "Email verification endpoint - to be implemented"}


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
