"""
Authentication dependencies for FastAPI
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.auth import verify_token
from app.models.auth import TokenData, UserData

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
        
        # Build user object from token
        user = UserData(
            id=token_data.user_id,
            email=token_data.email,
            name=token_data.email.split("@")[0] if token_data.email else "user",
            created_at=None,
            is_active=True
        )
        
        print(f"✅ Auth successful for user: {user.email}")
        return user
        
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
        user = create_demo_user()
        user.id = token_data.user_id
        user.email = token_data.email
        return user
    except HTTPException:
        return None
