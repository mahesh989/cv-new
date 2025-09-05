"""
Authentication models and schemas
"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request model - allows empty credentials for now"""
    email: Optional[str] = ""
    password: Optional[str] = ""


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
