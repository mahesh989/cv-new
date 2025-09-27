"""
Authentication dependencies for FastAPI
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.auth import verify_token
from app.models.auth import TokenData, UserData
from app.core.auth import create_demo_user

# Security scheme for extracting Bearer tokens
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserData:
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        UserData object for the authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    from app.config import settings
    
    try:
        # Debug logging
        token_preview = credentials.credentials[:20] + "..." if len(credentials.credentials) > 20 else credentials.credentials
        print(f"Auth attempt with token: {token_preview}")
        
        # Verify the token
        token_data = verify_token(credentials.credentials)
        
        # Check if this is an admin token
        from app.core.admin_auth import AdminAuth
        if AdminAuth.is_admin_token(token_data):
            print(f"✅ Admin auth successful: {token_data.email}")
            return AdminAuth.create_admin_user()
        
        # For regular users, fetch from database
        from app.database import get_database
        from app.services.user_service import UserService
        
        db = next(get_database())
        user_service = UserService(db)
        
        # Get user from database
        user = user_service.get_user_by_id(int(token_data.user_id))
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"✅ Auth successful for user: {user.email}")
        return user_service.to_user_data(user)
        
    except HTTPException as e:
        print(f"❌ Auth failed: {e.detail}")
        
        # In development mode, provide more helpful error messages
        if settings.DEVELOPMENT_MODE:
            if "expired" in str(e.detail).lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired - please log in again",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token - please log in again",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        raise


async def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserData:
    """
    Dependency to get admin user with admin privileges
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        UserData object for the admin user
        
    Raises:
        HTTPException: If user is not admin or token is invalid
    """
    user = await get_current_user(credentials)
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return user


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UserData]:
    """
    Dependency to optionally get the current authenticated user from JWT token
    Returns None if no valid token is provided instead of raising an exception
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        
    Returns:
        UserData object for the authenticated user or None
    """
    if credentials is None:
        return None
    
    try:
        token_data = verify_token(credentials.credentials)
        
        # Check if this is an admin token
        from app.core.admin_auth import AdminAuth
        if AdminAuth.is_admin_token(token_data):
            return AdminAuth.create_admin_user()
        
        # For regular users, fetch from database
        from app.database import get_database
        from app.services.user_service import UserService
        
        db = next(get_database())
        user_service = UserService(db)
        
        # Get user from database
        user = user_service.get_user_by_id(int(token_data.user_id))
        
        if user and user.is_active:
            return user_service.to_user_data(user)
        
        return None
    except HTTPException:
        return None
