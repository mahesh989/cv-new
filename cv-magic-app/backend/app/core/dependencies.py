"""
Authentication dependencies for FastAPI
"""
from typing import Optional
from datetime import datetime, timezone
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
    import logging
    logger = logging.getLogger(__name__)
    
    from app.config import settings
    
    try:
        # Comprehensive debug logging
        token_preview = credentials.credentials[:20] + "..." if len(credentials.credentials) > 20 else credentials.credentials
        logger.info(f"🔒 [AUTH] Authentication attempt with token: {token_preview}")
        logger.info(f"🔒 [AUTH] Token length: {len(credentials.credentials)}")
        logger.info(f"🔒 [AUTH] Token scheme: {credentials.scheme}")
        
        # Verify the token
        logger.info(f"🔒 [AUTH] Calling verify_token...")
        token_data = verify_token(credentials.credentials)
        logger.info(f"🔒 [AUTH] Token verification successful")
        logger.info(f"🔒 [AUTH] Token data: user_id={token_data.user_id}, email={token_data.email}")
        
        # Build user object from token
        user = UserData(
            id=token_data.user_id,
            email=token_data.email,
            name=token_data.email.split("@")[0] if token_data.email else "user",
            created_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        logger.info(f"✅ [AUTH] Authentication successful for user: {user.email} (ID: {user.id})")
        return user
        
    except HTTPException as e:
        logger.error(f"❌ [AUTH] Authentication failed: {e.detail}")
        logger.error(f"❌ [AUTH] HTTPException status: {e.status_code}")
        logger.error(f"❌ [AUTH] HTTPException headers: {e.headers}")
        
        # In development mode, provide more helpful error messages
        if settings.DEVELOPMENT_MODE:
            if "expired" in str(e.detail).lower():
                logger.error(f"❌ [AUTH] Token expired - user needs to log in again")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired - please log in again",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                logger.error(f"❌ [AUTH] Invalid token - user needs to log in again")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token - please log in again",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        raise
    except Exception as e:
        logger.error(f"❌ [AUTH] Unexpected authentication error: {e}")
        logger.error(f"❌ [AUTH] Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ [AUTH] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed - please log in again",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
