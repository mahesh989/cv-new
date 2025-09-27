"""
Authentication models and schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import re


class LoginRequest(BaseModel):
    """Login request model"""
    email: str
    password: str


class UserRegistration(BaseModel):
    """User registration model"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserData(BaseModel):
    """User data model"""
    id: str
    email: str
    name: str
    created_at: datetime
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False


class UserResponse(BaseModel):
    """User response model for registration"""
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: UserData


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
    exp: datetime
    iat: datetime
    role: Optional[str] = "user"


class EmailVerificationRequest(BaseModel):
    """Email verification request"""
    token: str


class AdminLoginRequest(BaseModel):
    """Admin login request"""
    email: str
    password: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: str


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
