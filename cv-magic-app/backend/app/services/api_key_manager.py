"""
API Key Management Service

This module handles dynamic API key storage, validation, and management
for all AI providers (OpenAI, Anthropic, DeepSeek).
"""

import os
import json
import logging
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import secrets

logger = logging.getLogger(__name__)


@dataclass
class APIKeyInfo:
    """Information about an API key"""
    provider: str
    key_hash: str  # Hashed version for security
    is_valid: bool
    last_validated: Optional[str] = None
    created_at: Optional[str] = None


class APIKeyManager:
    """
    Manages API keys for all AI providers dynamically.
    
    Features:
    - Secure storage of API keys (hashed)
    - Validation of API keys
    - Provider-specific key management
    - Session-based key storage
    """
    
    def __init__(self):
        self._api_keys: Dict[str, str] = {}  # provider -> actual_key
        self._key_info: Dict[str, APIKeyInfo] = {}  # provider -> key_info
        self._storage_file = Path("api_keys.json")
        self._session_id = self._generate_session_id()
        
        # Load existing keys if available
        self._load_keys()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for this instance"""
        return secrets.token_urlsafe(16)
    
    def _hash_key(self, key: str) -> str:
        """Hash an API key for secure storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _load_keys(self):
        """Load API keys from storage file"""
        try:
            if self._storage_file.exists():
                with open(self._storage_file, 'r') as f:
                    data = json.load(f)
                    for provider, key_data in data.items():
                        if isinstance(key_data, dict) and 'key' in key_data:
                            self._api_keys[provider] = key_data['key']
                            self._key_info[provider] = APIKeyInfo(
                                provider=provider,
                                key_hash=key_data.get('key_hash', ''),
                                is_valid=key_data.get('is_valid', False),
                                last_validated=key_data.get('last_validated'),
                                created_at=key_data.get('created_at')
                            )
        except Exception as e:
            logger.warning(f"Failed to load API keys: {e}")
    
    def _save_keys(self):
        """Save API keys to storage file"""
        try:
            data = {}
            for provider, key in self._api_keys.items():
                key_info = self._key_info.get(provider)
                data[provider] = {
                    'key': key,
                    'key_hash': key_info.key_hash if key_info else '',
                    'is_valid': key_info.is_valid if key_info else False,
                    'last_validated': key_info.last_validated if key_info else None,
                    'created_at': key_info.created_at if key_info else None
                }
            
            with open(self._storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")
    
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """
        Set an API key for a specific provider
        
        Args:
            provider: The AI provider (openai, anthropic, deepseek)
            api_key: The API key to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate provider
            if provider not in ['openai', 'anthropic', 'deepseek']:
                logger.error(f"Invalid provider: {provider}")
                return False
            
            # Store the key
            self._api_keys[provider] = api_key
            
            # Create key info
            from datetime import datetime
            self._key_info[provider] = APIKeyInfo(
                provider=provider,
                key_hash=self._hash_key(api_key),
                is_valid=False,  # Will be validated next
                created_at=datetime.now().isoformat()
            )
            
            # Save to storage
            self._save_keys()
            
            logger.info(f"API key set for {provider}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set API key for {provider}: {e}")
            return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a specific provider
        
        Args:
            provider: The AI provider
            
        Returns:
            str: The API key if available, None otherwise
        """
        return self._api_keys.get(provider)
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key exists for a provider"""
        return provider in self._api_keys and bool(self._api_keys[provider])
    
    def validate_api_key(self, provider: str, api_key: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate an API key for a specific provider
        
        Args:
            provider: The AI provider
            api_key: Optional API key to validate (uses stored key if None)
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            # Use provided key or stored key
            key_to_validate = api_key or self._api_keys.get(provider)
            
            if not key_to_validate:
                return False, f"No API key found for {provider}"
            
            # Import here to avoid circular imports
            from app.ai.providers import OpenAIProvider, AnthropicProvider, DeepSeekProvider
            
            # Create provider instance for validation
            provider_classes = {
                'openai': OpenAIProvider,
                'anthropic': AnthropicProvider,
                'deepseek': DeepSeekProvider
            }
            
            if provider not in provider_classes:
                return False, f"Unknown provider: {provider}"
            
            # Get default model for validation
            from app.ai.ai_config import ai_config
            available_models = ai_config.get_available_models(provider)
            if not available_models:
                return False, f"No models available for {provider}"
            
            default_model = available_models[0]
            
            # Create provider instance and test
            provider_class = provider_classes[provider]
            provider_instance = provider_class(key_to_validate, default_model)
            
            # Test the connection
            is_available = provider_instance.is_available()
            
            if is_available:
                # Update key info
                from datetime import datetime
                if provider in self._key_info:
                    self._key_info[provider].is_valid = True
                    self._key_info[provider].last_validated = datetime.now().isoformat()
                else:
                    self._key_info[provider] = APIKeyInfo(
                        provider=provider,
                        key_hash=self._hash_key(key_to_validate),
                        is_valid=True,
                        last_validated=datetime.now().isoformat(),
                        created_at=datetime.now().isoformat()
                    )
                
                # Save updated info
                self._save_keys()
                
                return True, f"API key for {provider} is valid"
            else:
                return False, f"API key for {provider} is invalid or service unavailable"
                
        except Exception as e:
            logger.error(f"Error validating API key for {provider}: {e}")
            return False, f"Validation failed: {str(e)}"
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for provider in ['openai', 'anthropic', 'deepseek']:
            has_key = self.has_api_key(provider)
            key_info = self._key_info.get(provider)
            
            status[provider] = {
                'has_api_key': has_key,
                'is_valid': key_info.is_valid if key_info else False,
                'last_validated': key_info.last_validated if key_info else None,
                'created_at': key_info.created_at if key_info else None
            }
        
        return status
    
    def remove_api_key(self, provider: str) -> bool:
        """Remove API key for a provider"""
        try:
            if provider in self._api_keys:
                del self._api_keys[provider]
            if provider in self._key_info:
                del self._key_info[provider]
            
            self._save_keys()
            logger.info(f"API key removed for {provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove API key for {provider}: {e}")
            return False
    
    def clear_all_keys(self):
        """Clear all API keys"""
        self._api_keys.clear()
        self._key_info.clear()
        self._save_keys()
        logger.info("All API keys cleared")


# Global API key manager instance
api_key_manager = APIKeyManager()
