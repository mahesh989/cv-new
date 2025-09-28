"""
User service for database operations
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.auth import UserData, UserResponse

logger = logging.getLogger(__name__)
from app.database import get_database
import secrets
import hashlib


class UserService:
    """User service for database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
        """Create a new user with comprehensive error handling and email verification"""
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                if existing_user.email == email:
                    if existing_user.is_verified:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"An account with email '{email}' already exists. Please use a different email or try logging in."
                        )
                    else:
                        # User exists but not verified - resend verification
                        self._generate_verification_token(existing_user)
                        self.db.commit()
                        self._send_verification_email(existing_user)
                        raise HTTPException(
                            status_code=status.HTTP_200_OK,
                            detail=f"Account with email '{email}' exists but is not verified. Verification email has been resent. Please check your email and verify your account."
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Username '{username}' is already taken. Please choose a different username."
                    )
            
            # Create new user
            from app.config import settings
            
            # In development mode with email disabled, auto-verify users
            is_auto_verified = (not settings.EMAIL_ENABLED and settings.DEVELOPMENT_MODE)
            
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                is_active=True,
                is_verified=is_auto_verified,  # Auto-verify in development mode
                is_admin=False,
                role="user"
            )
            
            # Set password
            user.set_password(password)
            
            # Generate verification token (even if auto-verified for consistency)
            self._generate_verification_token(user)
            
            # Add to database
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Send verification email (or simulate in development)
            email_sent = self._send_verification_email(user)
            
            # If auto-verified, clear the token since it's not needed
            if is_auto_verified:
                user.verification_token = None
                user.verification_token_expires = None
                self.db.commit()
                logger.info(f"Development mode: User {email} auto-verified")
            
            return user
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle database errors
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user account: {str(e)}"
            )
    
    def _generate_verification_token(self, user: User) -> None:
        """Generate verification token for user"""
        import secrets
        from datetime import datetime, timedelta
        
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Set token and expiration (24 hours)
        user.verification_token = token
        user.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
    
    def _send_verification_email(self, user: User) -> None:
        """Send verification email to user"""
        try:
            from app.services.email_service import email_service
            
            # Send verification email
            success = email_service.send_verification_email(
                user_email=user.email,
                user_name=user.full_name or user.username,
                verification_token=user.verification_token
            )
            
            if not success:
                logger.warning(f"Failed to send verification email to {user.email}")
                
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
    
    def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        try:
            from datetime import datetime
            
            # Find user by verification token
            user = self.db.query(User).filter(
                User.verification_token == token,
                User.verification_token_expires > datetime.utcnow()
            ).first()
            
            if not user:
                return False
            
            # Mark user as verified and clear token
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            
            self.db.commit()
            
            # Send welcome email
            try:
                from app.services.email_service import email_service
                email_service.send_welcome_email(
                    user_email=user.email,
                    user_name=user.full_name or user.username
                )
            except Exception as e:
                logger.error(f"Failed to send welcome email: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying email: {e}")
            self.db.rollback()
            return False
    
    def resend_verification_email(self, email: str) -> bool:
        """Resend verification email to user"""
        try:
            # Find user by email
            user = self.db.query(User).filter(
                User.email == email,
                User.is_verified == False
            ).first()
            
            if not user:
                return False
            
            # Generate new token and send email
            self._generate_verification_token(user)
            self.db.commit()
            self._send_verification_email(user)
            
            return True
            
        except Exception as e:
            logger.error(f"Error resending verification email: {e}")
            return False
    
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
