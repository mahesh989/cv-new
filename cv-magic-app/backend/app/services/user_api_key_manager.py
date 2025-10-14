"""
User-Specific API Key Management Service

This module handles user-specific API key storage, validation, and management
with encryption for security.
"""

import logging
from typing import Dict, Optional, Any, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.database import get_database
from app.models.user_api_keys import UserAPIKey
from app.models.auth import UserData

logger = logging.getLogger(__name__)


class UserAPIKeyManager:
    """
    Manages user-specific API keys with encryption and database persistence.
    
    Features:
    - User-specific API key storage
    - Encrypted storage using user-specific keys
    - Database persistence
    - Real-time validation
    - Provider-specific key management
    """
    
    def __init__(self):
        self._valid_providers = ['openai', 'anthropic', 'deepseek']
    
    def set_api_key(self, user: UserData, provider: str, api_key: str) -> Tuple[bool, str]:
        """
        Set an API key for a specific user and provider
        
        Args:
            user: User data
            provider: The AI provider (openai, anthropic, deepseek)
            api_key: The API key to set
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Validate provider
            if provider not in self._valid_providers:
                return False, f"Invalid provider. Must be one of: {', '.join(self._valid_providers)}"
            
            # Validate API key format
            if not api_key or len(api_key.strip()) < 10:
                return False, "API key appears to be invalid (too short)"
            
            user_id = str(user.id)
            
            # Use database session
            for db in get_database():
                # Check if key already exists for this user and provider
                existing_key = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider
                ).first()
                
                if existing_key:
                    # Update existing key
                    existing_key.update_api_key(api_key)
                    db.commit()
                    logger.info(f"Updated API key for user {user.email} and provider {provider}")
                    return True, f"API key updated for {provider}"
                else:
                    # Create new key
                    new_key = UserAPIKey(
                        user_id=user_id,
                        provider=provider,
                        api_key=api_key
                    )
                    db.add(new_key)
                    db.commit()
                    logger.info(f"Created new API key for user {user.email} and provider {provider}")
                    return True, f"API key set for {provider}"
            
            return False, "Database error: Could not establish connection"
            
        except IntegrityError as e:
            logger.error(f"Database integrity error setting API key: {e}")
            return False, "API key already exists for this provider"
        except Exception as e:
            logger.error(f"Failed to set API key for user {user.email} and provider {provider}: {e}")
            return False, f"Failed to set API key: {str(e)}"
    
    def get_api_key(self, user: UserData, provider: str) -> Optional[str]:
        """
        Get API key for a specific user and provider
        
        Args:
            user: User data
            provider: The AI provider
            
        Returns:
            str: The API key if available, None otherwise
        """
        try:
            user_id = str(user.id)
            
            for db in get_database():
                user_key = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider
                ).first()
                
                if user_key:
                    return user_key.get_api_key()
                return None
                
        except Exception as e:
            logger.error(f"Failed to get API key for user {user.email} and provider {provider}: {e}")
            return None
    
    def has_api_key(self, user: UserData, provider: str) -> bool:
        """Check if API key exists for a user and provider"""
        return self.get_api_key(user, provider) is not None
    
    def get_api_key_info(self, user: UserData, provider: str) -> Optional[UserAPIKey]:
        """
        Get API key info (including validation status) for a specific user and provider
        
        Args:
            user: User data
            provider: The AI provider
            
        Returns:
            UserAPIKey object if found, None otherwise
        """
        try:
            user_id = str(user.id)
            
            for db in get_database():
                user_key = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider
                ).first()
                
                return user_key
                
        except Exception as e:
            logger.error(f"Failed to get API key info for user {user.email} and provider {provider}: {e}")
            return None
    
    def validate_api_key(self, user: UserData, provider: str, api_key: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate API key for a specific user and provider
        
        Args:
            user: User data
            provider: The AI provider
            api_key: Optional API key to validate (if not provided, uses stored key)
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            # Get API key if not provided
            if api_key is None:
                api_key = self.get_api_key(user, provider)
                if not api_key:
                    return False, f"No API key found for {provider}"
            
            # Direct provider validation without global API key manager
            from app.ai.providers import OpenAIProvider, AnthropicProvider, DeepSeekProvider
            from app.ai.ai_config import ai_config
            
            # Create provider instance for validation
            provider_classes = {
                'openai': OpenAIProvider,
                'anthropic': AnthropicProvider,
                'deepseek': DeepSeekProvider
            }
            
            if provider not in provider_classes:
                return False, f"Unknown provider: {provider}"
            
            # Get default model for validation
            available_models = ai_config.get_available_models(provider)
            if not available_models:
                return False, f"No models available for {provider}"
            
            default_model = available_models[0]
            
            # Create provider instance and test
            provider_class = provider_classes[provider]
            provider_instance = provider_class(api_key, default_model)
            
            # Test the connection
            is_valid = provider_instance.is_available()
            message = f"API key for {provider} is {'valid' if is_valid else 'invalid or service unavailable'}"
            
            # Update validation status in database
            if is_valid:
                self._mark_key_as_valid(user, provider)
            else:
                self._mark_key_as_invalid(user, provider)
            
            return is_valid, message
            
        except Exception as e:
            logger.error(f"Failed to validate API key for user {user.email} and provider {provider}: {e}")
            return False, f"Validation failed: {str(e)}"
    
    def _mark_key_as_valid(self, user: UserData, provider: str):
        """Mark API key as valid in database"""
        try:
            user_id = str(user.id)
            
            for db in get_database():
                user_key = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider
                ).first()
                
                if user_key:
                    user_key.mark_as_valid()
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Failed to mark key as valid: {e}")
    
    def _mark_key_as_invalid(self, user: UserData, provider: str):
        """Mark API key as invalid in database"""
        try:
            user_id = str(user.id)
            
            for db in get_database():
                user_key = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider
                ).first()
                
                if user_key:
                    user_key.mark_as_invalid()
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Failed to mark key as invalid: {e}")
    
    def get_provider_status(self, user: UserData) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all providers for a specific user
        
        Args:
            user: User data
            
        Returns:
            Dict: Status information for all providers
        """
        try:
            user_id = str(user.id)
            status_data = {}
            
            for db in get_database():
                user_keys = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user_id
                ).all()
                
                # Create a map of provider -> key info
                key_map = {key.provider: key for key in user_keys}
                
                # Check status for all valid providers
                for provider in self._valid_providers:
                    if provider in key_map:
                        key_info = key_map[provider]
                        status_data[provider] = {
                            'has_api_key': True,
                            'is_valid': key_info.is_valid,
                            'last_validated': key_info.last_validated.isoformat() if key_info.last_validated else None,
                            'created_at': key_info.created_at.isoformat() if key_info.created_at else None
                        }
                    else:
                        status_data[provider] = {
                            'has_api_key': False,
                            'is_valid': False,
                            'last_validated': None,
                            'created_at': None
                        }
                
                return status_data
                
        except Exception as e:
            logger.error(f"Failed to get provider status for user {user.email}: {e}")
            return {}
    
    def remove_api_key(self, user: UserData, provider: str) -> Tuple[bool, str]:
        """
        Remove API key for a specific user and provider
        
        Args:
            user: User data
            provider: The AI provider
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            user_id = str(user.id)
            
            for db in get_database():
                user_key = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider
                ).first()
                
                if user_key:
                    db.delete(user_key)
                    db.commit()
                    logger.info(f"Removed API key for user {user.email} and provider {provider}")
                    return True, f"API key removed for {provider}"
                else:
                    return False, f"No API key found for {provider}"
                    
        except Exception as e:
            logger.error(f"Failed to remove API key for user {user.email} and provider {provider}: {e}")
            return False, f"Failed to remove API key: {str(e)}"
    
    def clear_all_keys(self, user: UserData) -> Tuple[bool, str]:
        """
        Clear all API keys for a specific user
        
        Args:
            user: User data
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            user_id = str(user.id)
            
            for db in get_database():
                user_keys = db.query(UserAPIKey).filter(
                    UserAPIKey.user_id == user_id
                ).all()
                
                for key in user_keys:
                    db.delete(key)
                
                db.commit()
                logger.info(f"Cleared all API keys for user {user.email}")
                return True, "All API keys cleared"
                
        except Exception as e:
            logger.error(f"Failed to clear API keys for user {user.email}: {e}")
            return False, f"Failed to clear API keys: {str(e)}"


# Global instance
user_api_key_manager = UserAPIKeyManager()
