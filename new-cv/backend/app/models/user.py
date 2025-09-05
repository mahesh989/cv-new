"""
User-related database models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from passlib.context import CryptContext
from .base import Base
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    def set_password(self, password: str) -> None:
        """Hash and set the user's password"""
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the hashed password"""
        return pwd_context.verify(password, self.hashed_password)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class UserSession(Base):
    """User session model for JWT token management"""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    token_jti = Column(String(255), unique=True, index=True, nullable=False)  # JWT ID
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    is_blacklisted = Column(Boolean, default=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    
    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, jti='{self.token_jti}')>"
