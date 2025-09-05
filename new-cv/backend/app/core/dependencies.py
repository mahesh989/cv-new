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
    # Verify the token
    token_data = verify_token(credentials.credentials)
    
    # For now, since we're using demo users, just return a demo user
    # In production, you would fetch the user from the database using token_data.user_id
    user = create_demo_user()
    user.id = token_data.user_id  # Use the user_id from the token
    user.email = token_data.email  # Use the email from the token
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
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
        user = create_demo_user()
        user.id = token_data.user_id
        user.email = token_data.email
        return user
    except HTTPException:
        return None
