"""
User-specific API key management service
"""
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from cryptography.fernet import Fernet
from app.models.user_data import UserAPIKey
from app.database import get_database
import base64
import os


class UserAPIKeyService:
    """User-specific API key management service"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._encryption_key = self._get_or_create_encryption_key()
        self._cipher = Fernet(self._encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for user"""
        # In production, this should be stored securely per user
        # For now, we'll use a base key with user_id as salt
        base_key = os.getenv("API_KEY_ENCRYPTION_KEY", "default-encryption-key-32-chars")
        user_salt = f"{self.user_id}-{base_key}"
        
        # Create a deterministic key from user_id and base key
        import hashlib
        key_hash = hashlib.sha256(user_salt.encode()).digest()
        return base64.urlsafe_b64encode(key_hash)
    
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Set API key for specific user and provider"""
        try:
            db = next(get_database())
            
            # Encrypt the API key
            encrypted_key = self._cipher.encrypt(api_key.encode()).decode()
            
            # Check if key already exists
            existing_key = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == int(self.user_id),
                UserAPIKey.provider == provider
            ).first()
            
            if existing_key:
                # Update existing key
                existing_key.encrypted_key = encrypted_key
                existing_key.is_valid = True
                existing_key.updated_at = datetime.now(timezone.utc)
            else:
                # Create new key
                user_api_key = UserAPIKey(
                    user_id=int(self.user_id),
                    provider=provider,
                    encrypted_key=encrypted_key,
                    is_valid=True
                )
                db.add(user_api_key)
            
            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set API key: {str(e)}"
            )
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get decrypted API key for user and provider"""
        try:
            db = next(get_database())
            
            user_key = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == int(self.user_id),
                UserAPIKey.provider == provider,
                UserAPIKey.is_valid == True
            ).first()
            
            if user_key:
                # Decrypt the API key
                decrypted_key = self._cipher.decrypt(user_key.encrypted_key.encode()).decode()
                return decrypted_key
            
            return None
            
        except Exception as e:
            print(f"Warning: Failed to get API key: {e}")
            return None
    
    def get_all_api_keys(self) -> List[Dict[str, Any]]:
        """Get all API keys for user (without actual key values)"""
        try:
            db = next(get_database())
            
            keys = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == int(self.user_id)
            ).all()
            
            return [
                {
                    "id": key.id,
                    "provider": key.provider,
                    "is_valid": key.is_valid,
                    "last_validated": key.last_validated.isoformat() if key.last_validated else None,
                    "created_at": key.created_at.isoformat(),
                    "updated_at": key.updated_at.isoformat()
                }
                for key in keys
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get API keys: {str(e)}"
            )
    
    def validate_api_key(self, provider: str) -> bool:
        """Validate API key for provider"""
        try:
            api_key = self.get_api_key(provider)
            if not api_key:
                return False
            
            # Here you would implement actual validation logic
            # For now, we'll just check if the key exists and is not empty
            if len(api_key.strip()) == 0:
                return False
            
            # Update validation timestamp
            db = next(get_database())
            user_key = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == int(self.user_id),
                UserAPIKey.provider == provider
            ).first()
            
            if user_key:
                user_key.last_validated = datetime.now(timezone.utc)
                db.commit()
            
            return True
            
        except Exception as e:
            print(f"Warning: Failed to validate API key: {e}")
            return False
    
    def invalidate_api_key(self, provider: str) -> bool:
        """Invalidate API key for provider"""
        try:
            db = next(get_database())
            
            user_key = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == int(self.user_id),
                UserAPIKey.provider == provider
            ).first()
            
            if user_key:
                user_key.is_valid = False
                user_key.updated_at = datetime.now(timezone.utc)
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to invalidate API key: {str(e)}"
            )
    
    def delete_api_key(self, provider: str) -> bool:
        """Delete API key for provider"""
        try:
            db = next(get_database())
            
            user_key = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == int(self.user_id),
                UserAPIKey.provider == provider
            ).first()
            
            if user_key:
                db.delete(user_key)
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete API key: {str(e)}"
            )
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers for user"""
        try:
            db = next(get_database())
            
            keys = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == int(self.user_id)
            ).all()
            
            status_dict = {}
            for key in keys:
                status_dict[key.provider] = key.is_valid
            
            return status_dict
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get provider status: {str(e)}"
            )
    
    def cleanup_user_api_keys(self):
        """Clean up all API keys for user (for account deletion)"""
        try:
            db = next(get_database())
            
            # Delete all API keys for user
            db.query(UserAPIKey).filter(
                UserAPIKey.user_id == int(self.user_id)
            ).delete()
            
            db.commit()
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cleanup API keys: {str(e)}"
            )
