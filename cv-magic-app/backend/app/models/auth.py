"""
Authentication models and schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import re


class LoginRequest(BaseModel):
    """Login request model with validation"""
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError('Email is required')
        email = v.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Invalid email format. Please enter a valid email address')
        return email
    
    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('Password is required')
        return v


class UserRegistration(BaseModel):
    """User registration model with comprehensive validation"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('Username is required')
        if len(v.strip()) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v.strip()) > 50:
            raise ValueError('Username must be less than 50 characters')
        if not re.match(r'^[a-zA-Z0-9_]+$', v.strip()):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError('Email is required')
        email = v.strip().lower()
        if len(email) > 100:
            raise ValueError('Email must be less than 100 characters')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Invalid email format. Please enter a valid email address')
        return email
    
    @validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('Password is required')
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Full name must be at least 2 characters long')
            if len(v.strip()) > 100:
                raise ValueError('Full name must be less than 100 characters')
            return v.strip()
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
