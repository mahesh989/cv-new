"""
Token service for email verification and password reset
"""
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.database import get_database
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class TokenService:
    """Token service for email verification and password reset"""
    
    def __init__(self):
        self.verification_token_expiry = timedelta(hours=24)  # 24 hours
        self.reset_token_expiry = timedelta(hours=1)  # 1 hour
    
    def generate_verification_token(self, user_id: int, email: str) -> str:
        """Generate email verification token"""
        try:
            # Create a secure random token
            token = secrets.token_urlsafe(32)
            
            # Hash the token for storage
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Store token in database (we'll use a simple approach for now)
            # In production, you might want to create a separate tokens table
            db = next(get_database())
            user = db.query(User).filter(User.id == user_id).first()
            
            if user:
                # Store token hash in user's verification field (we'll add this)
                # For now, we'll store it in a temporary field
                user.verification_token = token_hash
                user.verification_token_expires = datetime.now(timezone.utc) + self.verification_token_expiry
                db.commit()
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate verification token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate verification token"
            )
    
    def generate_reset_token(self, user_id: int, email: str) -> str:
        """Generate password reset token"""
        try:
            # Create a secure random token
            token = secrets.token_urlsafe(32)
            
            # Hash the token for storage
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Store token in database
            db = next(get_database())
            user = db.query(User).filter(User.id == user_id).first()
            
            if user:
                # Store token hash in user's reset field (we'll add this)
                # For now, we'll store it in a temporary field
                user.reset_token = token_hash
                user.reset_token_expires = datetime.now(timezone.utc) + self.reset_token_expiry
                db.commit()
            
            return token
            
        except Exception as e:
            logger.error(f"Failed to generate reset token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate reset token"
            )
    
    def verify_email_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify email verification token"""
        try:
            if not token:
                return None
            
            # Hash the provided token
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Find user with matching token
            db = next(get_database())
            user = db.query(User).filter(
                User.verification_token == token_hash,
                User.verification_token_expires > datetime.now(timezone.utc)
            ).first()
            
            if not user:
                return None
            
            # Mark email as verified
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            db.commit()
            
            return {
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "is_verified": True
            }
            
        except Exception as e:
            logger.error(f"Failed to verify email token: {str(e)}")
            return None
    
    def verify_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify password reset token"""
        try:
            if not token:
                return None
            
            # Hash the provided token
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Find user with matching token
            db = next(get_database())
            user = db.query(User).filter(
                User.reset_token == token_hash,
                User.reset_token_expires > datetime.now(timezone.utc)
            ).first()
            
            if not user:
                return None
            
            return {
                "user_id": user.id,
                "email": user.email,
                "username": user.username
            }
            
        except Exception as e:
            logger.error(f"Failed to verify reset token: {str(e)}")
            return None
    
    def invalidate_reset_token(self, token: str) -> bool:
        """Invalidate password reset token after use"""
        try:
            if not token:
                return False
            
            # Hash the provided token
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Find and invalidate token
            db = next(get_database())
            user = db.query(User).filter(User.reset_token == token_hash).first()
            
            if user:
                user.reset_token = None
                user.reset_token_expires = None
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to invalidate reset token: {str(e)}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        try:
            db = next(get_database())
            now = datetime.now(timezone.utc)
            
            # Clean up expired verification tokens
            expired_verification = db.query(User).filter(
                User.verification_token_expires < now
            ).all()
            
            for user in expired_verification:
                user.verification_token = None
                user.verification_token_expires = None
            
            # Clean up expired reset tokens
            expired_reset = db.query(User).filter(
                User.reset_token_expires < now
            ).all()
            
            for user in expired_reset:
                user.reset_token = None
                user.reset_token_expires = None
            
            db.commit()
            
            cleaned_count = len(expired_verification) + len(expired_reset)
            logger.info(f"Cleaned up {cleaned_count} expired tokens")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired tokens: {str(e)}")
            return 0
