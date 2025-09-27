"""
Admin authentication utilities
"""
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException, status
from app.config import settings
from app.models.auth import UserData
import jwt


class AdminAuth:
    """Admin authentication service"""
    
    ADMIN_EMAIL = "admin@cvapp.com"
    ADMIN_PASSWORD = "admin123"  # Change this in production
    ADMIN_USERNAME = "admin"
    
    @staticmethod
    def authenticate_admin(email: str, password: str) -> bool:
        """Authenticate admin credentials"""
        return (email == AdminAuth.ADMIN_EMAIL and 
                password == AdminAuth.ADMIN_PASSWORD)
    
    @staticmethod
    def create_admin_user() -> UserData:
        """Create admin user data"""
        return UserData(
            id="admin",
            email=AdminAuth.ADMIN_EMAIL,
            name="Admin User",
            created_at=datetime.now(timezone.utc),
            is_active=True,
            is_admin=True,
            is_verified=True
        )
    
    @staticmethod
    def create_admin_token() -> str:
        """Create admin-specific JWT token"""
        expire = datetime.now(timezone.utc) + timedelta(hours=8)
        
        payload = {
            "user_id": "admin",
            "email": AdminAuth.ADMIN_EMAIL,
            "role": "admin",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }
        
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def is_admin_token(token_data) -> bool:
        """Check if token belongs to admin"""
        return (token_data.user_id == "admin" and 
                token_data.email == AdminAuth.ADMIN_EMAIL)
