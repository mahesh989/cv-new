"""
User API Keys Model

This module defines the database model for storing user-specific API keys
with encryption for security.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from cryptography.fernet import Fernet
import base64
import os


class UserAPIKey(Base):
    """User-specific API key model with encryption"""
    
    __tablename__ = "user_api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)  # Use string to avoid FK type mismatches
    provider = Column(String(50), nullable=False, index=True)  # openai, anthropic, deepseek
    encrypted_key = Column(Text, nullable=False)  # Encrypted API key
    key_hash = Column(String(255), nullable=False)  # Hash for validation
    is_valid = Column(Boolean, default=False)
    last_validated = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Note: User relationship removed due to type mismatch (UUID vs String)
    
    def __init__(self, user_id: str, provider: str, api_key: str):
        """
        Initialize a new user API key with encryption
        
        Args:
            user_id: User ID
            provider: AI provider name
            api_key: Plain text API key
        """
        self.user_id = user_id
        self.provider = provider
        self.encrypted_key = self._encrypt_key(api_key)
        self.key_hash = self._hash_key(api_key)
        self.is_valid = False
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for this user"""
        # Use user-specific encryption key derived from user ID and a secret
        secret = os.getenv("API_KEY_ENCRYPTION_SECRET", "default-secret-change-in-production")
        user_specific_secret = f"{secret}-{self.user_id}"
        
        # Generate a consistent key from the user-specific secret
        key = base64.urlsafe_b64encode(user_specific_secret.encode()[:32].ljust(32, b'0'))
        return key
    
    def _encrypt_key(self, api_key: str) -> str:
        """Encrypt the API key"""
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(api_key.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise ValueError(f"Failed to encrypt API key: {e}")
    
    def _decrypt_key(self) -> str:
        """Decrypt the API key"""
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted_data = base64.urlsafe_b64decode(self.encrypted_key.encode())
            decrypted = fernet.decrypt(encrypted_data)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {e}")
    
    def _hash_key(self, api_key: str) -> str:
        """Hash the API key for validation"""
        import hashlib
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def get_api_key(self) -> str:
        """Get the decrypted API key"""
        return self._decrypt_key()
    
    def update_api_key(self, new_api_key: str):
        """Update the API key with new encryption"""
        self.encrypted_key = self._encrypt_key(new_api_key)
        self.key_hash = self._hash_key(new_api_key)
        self.is_valid = False  # Reset validation status
        self.updated_at = datetime.utcnow()
    
    def mark_as_valid(self):
        """Mark the API key as valid"""
        self.is_valid = True
        self.last_validated = datetime.utcnow()
    
    def mark_as_invalid(self):
        """Mark the API key as invalid"""
        self.is_valid = False
    
    def __repr__(self):
        return f"<UserAPIKey(user_id={self.user_id}, provider='{self.provider}', is_valid={self.is_valid})>"
