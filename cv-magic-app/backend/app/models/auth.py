"""
Authentication models and schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class RegisterRequest(BaseModel):
    """Registration request model"""
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


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


class RegisterResponse(BaseModel):
    """Registration response model"""
    message: str
    user_id: str
    email: str
    success: bool = True


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
    exp: datetime
    iat: datetime
