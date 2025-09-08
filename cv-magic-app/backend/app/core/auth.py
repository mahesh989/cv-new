"""
JWT token utilities and authentication helpers
"""
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.config import settings
from app.models.auth import TokenData, UserData
import uuid


def create_access_token(user_data: Dict[str, Any]) -> str:
    """
    Create a JWT access token for the user
    
    Args:
        user_data: Dictionary containing user information
        
    Returns:
        Encoded JWT token string
    """
    # Set expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    
    # Create token payload
    payload = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    # Encode and return token
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token for the user
    
    Args:
        user_id: User ID
        
    Returns:
        Encoded JWT refresh token string
    """
    # Set expiration time for refresh token (longer duration)
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    
    # Create token payload
    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    
    # Encode and return token
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_token(token: str) -> TokenData:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData object containing decoded token information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode the token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Extract user information
        user_id = payload.get("user_id")
        email = payload.get("email", "")
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        iat = datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc)
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create and return TokenData
        return TokenData(
            user_id=user_id,
            email=email,
            exp=exp,
            iat=iat
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_demo_user() -> UserData:
    """
    Create a demo user for development purposes (empty credentials login)
    
    Returns:
        UserData object for the demo user
    """
    user_id = str(uuid.uuid4())
    return UserData(
        id=user_id,
        email="demo@cvapp.com",
        name="Demo User",
        created_at=datetime.now(timezone.utc),
        is_active=True
    )


def authenticate_user(email: str, password: str) -> Optional[UserData]:
    """
    Authenticate user - for now, allows empty credentials
    
    Args:
        email: User email (can be empty)
        password: User password (can be empty)
        
    Returns:
        UserData if authentication successful, None otherwise
    """
    # For development: allow any credentials (including empty ones)
    # TODO: Replace with proper authentication logic later
    return create_demo_user()
