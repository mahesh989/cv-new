"""
Authentication models and schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import re


class LoginRequest(BaseModel):
    """Login request model - requires valid credentials"""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """User registration request model"""
    email: str
    password: str
    full_name: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        # Simple email validation - must contain @ and .com
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Email must be a valid email address')
        if not v.endswith('.com'):
            raise ValueError('Email must end with .com')
        return v.lower().strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 1:
            raise ValueError('Password cannot be empty')
        return v


class UserData(BaseModel):
    """User data model"""
    id: str
    email: str
    name: str
    created_at: datetime
    is_active: bool = True


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
