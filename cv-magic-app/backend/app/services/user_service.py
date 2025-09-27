"""
User service for database operations
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.auth import UserData, UserResponse
from app.database import get_database
import secrets
import hashlib


class UserService:
    """User service for database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_active=True,
            is_verified=False,
            is_admin=False,
            role="user"
        )
        
        # Set password
        user.set_password(password)
        
        # Add to database
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not user.verify_password(password):
            return None
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        self.db.commit()
        
        return user
    
    def verify_user_email(self, user_id: int) -> bool:
        """Verify user email"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_verified = True
        self.db.commit()
        return True
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
    
    def activate_user(self, user_id: int) -> bool:
        """Activate user account"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        self.db.commit()
        return True
    
    def make_admin(self, user_id: int) -> bool:
        """Make user an admin"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_admin = True
        user.role = "admin"
        self.db.commit()
        return True
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove admin privileges"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_admin = False
        user.role = "user"
        self.db.commit()
        return True
    
    def get_all_users(self) -> list[User]:
        """Get all users (admin only)"""
        return self.db.query(User).all()
    
    def get_active_users(self) -> list[User]:
        """Get all active users"""
        return self.db.query(User).filter(User.is_active == True).all()
    
    def get_admin_users(self) -> list[User]:
        """Get all admin users"""
        return self.db.query(User).filter(User.is_admin == True).all()
    
    def to_user_data(self, user: User) -> UserData:
        """Convert User model to UserData"""
        return UserData(
            id=str(user.id),
            email=user.email,
            name=user.full_name or user.username,
            created_at=user.created_at,
            is_active=user.is_active,
            is_admin=user.is_admin,
            is_verified=user.is_verified
        )
    
    def to_user_response(self, user: User) -> UserResponse:
        """Convert User model to UserResponse"""
        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
