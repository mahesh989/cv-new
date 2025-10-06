"""
AI Configuration Management

This module handles all AI configuration including:
- Reading API keys from environment variables
- Managing current model selection
- Providing model configurations
- Handling model switching
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for a specific AI model"""
    provider: str
    model: str
    name: str
    description: str
    max_tokens: int
    input_cost_per_1k: float
    output_cost_per_1k: float


class AIConfig:
    """
    Centralized AI configuration manager.
    
    This class handles:
    - Loading API keys from environment variables
    - Managing the current active model
    - Providing model configurations
    - Switching between models
    """
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Current model selection
        self._current_provider: Optional[str] = None
        self._current_model: Optional[str] = None
        
        # Model configurations
        self._model_configs = self._load_model_configurations()
        
        # Set default model from environment or use fallback
        self._set_default_model()
    
    def _load_model_configurations(self) -> Dict[str, Dict[str, ModelConfig]]:
        """Load all available model configurations"""
        return {
            "openai": {
                "gpt-4o": ModelConfig(
                    provider="openai",
                    model="gpt-4o",
                    name="GPT-4o",
                    description="Most advanced GPT-4 model with improved performance",
                    max_tokens=128000,
                    input_cost_per_1k=0.005,
                    output_cost_per_1k=0.015
                ),
                "gpt-4o-mini": ModelConfig(
                    provider="openai",
                    model="gpt-4o-mini",
                    name="GPT-4o Mini",
                    description="Faster and more cost-effective GPT-4 variant",
                    max_tokens=128000,
                    input_cost_per_1k=0.00015,
                    output_cost_per_1k=0.0006
                ),
                "gpt-4-turbo": ModelConfig(
                    provider="openai",
                    model="gpt-4-turbo",
                    name="GPT-4 Turbo",
                    description="High-performance GPT-4 with larger context window",
                    max_tokens=128000,
                    input_cost_per_1k=0.01,
                    output_cost_per_1k=0.03
                ),
                "gpt-3.5-turbo": ModelConfig(
                    provider="openai",
                    model="gpt-3.5-turbo",
                    name="GPT-3.5 Turbo",
                    description="Fast and cost-effective model for most tasks",
                    max_tokens=16384,
                    input_cost_per_1k=0.001,
                    output_cost_per_1k=0.002
                ),
                "gpt-5-nano": ModelConfig(
                    provider="openai",
                    model="gpt-5-nano",
                    name="GPT-5 Nano",
                    description="Latest nano model with flexible service tier for optimized performance",
                    max_tokens=200000,
                    input_cost_per_1k=0.00005,
                    output_cost_per_1k=0.0002
                )
            },
            "anthropic": {
                "claude-3-5-sonnet-20241022": ModelConfig(
                    provider="anthropic",
                    model="claude-3-5-sonnet-20241022",
                    name="Claude 3.5 Sonnet",
                    description="Most intelligent model with best performance on complex tasks",
                    max_tokens=200000,
                    input_cost_per_1k=0.003,
                    output_cost_per_1k=0.015
                ),
                "claude-3-5-haiku-20241022": ModelConfig(
                    provider="anthropic",
                    model="claude-3-5-haiku-20241022",
                    name="Claude 3.5 Haiku",
                    description="Fastest model for everyday tasks",
                    max_tokens=200000,
                    input_cost_per_1k=0.00025,
                    output_cost_per_1k=0.00125
                ),
                "claude-3-opus-20240229": ModelConfig(
                    provider="anthropic",
                    model="claude-3-opus-20240229",
                    name="Claude 3 Opus",
                    description="Most powerful model for highly complex tasks",
                    max_tokens=200000,
                    input_cost_per_1k=0.015,
                    output_cost_per_1k=0.075
                )
            },
            "deepseek": {
                "deepseek-chat": ModelConfig(
                    provider="deepseek",
                    model="deepseek-chat",
                    name="DeepSeek Chat",
                    description="General-purpose chat model with strong reasoning capabilities",
                    max_tokens=32000,
                    input_cost_per_1k=0.00014,
                    output_cost_per_1k=0.00028
                ),
                "deepseek-coder": ModelConfig(
                    provider="deepseek",
                    model="deepseek-coder",
                    name="DeepSeek Coder",
                    description="Specialized model for code generation and programming tasks",
                    max_tokens=32000,
                    input_cost_per_1k=0.00014,
                    output_cost_per_1k=0.00028
                ),
                "deepseek-reasoner": ModelConfig(
                    provider="deepseek",
                    model="deepseek-reasoner",
                    name="DeepSeek Reasoner",
                    description="Advanced reasoning model for complex analytical tasks",
                    max_tokens=32000,
                    input_cost_per_1k=0.00055,
                    output_cost_per_1k=0.0022
                )
            }
        }
    
    def _set_default_model(self):
        """Set the default model from environment variables or use fallback"""
        # Try to get from environment variables
        default_provider = os.getenv("DEFAULT_AI_PROVIDER", "openai")
        default_model = os.getenv("DEFAULT_AI_MODEL")
        
        # If specific model is set, use it
        if default_model and default_provider in self._model_configs:
            if default_model in self._model_configs[default_provider]:
                self._current_provider = default_provider
                self._current_model = default_model
                return
        
        # No automatic fallback - require user to configure via frontend
        logger.warning("No AI providers auto-configured - user must select provider and configure API keys via frontend")
        self._current_provider = None
        self._current_model = None
    
    def _auto_select_provider(self):
        """Auto-select a provider if none is currently set"""
        # Check for available API keys and select the first available provider
        for provider in self._model_configs.keys():
            api_key = self.get_api_key(provider)
            if api_key:
                # Get the first available model for this provider
                available_models = self.get_available_models(provider)
                if available_models:
                    self._current_provider = provider
                    self._current_model = available_models[0]
                    logger.info(f"Auto-selected provider: {provider} with model: {self._current_model}")
                    return
        
        # If no provider with API key is found, log warning
        logger.warning("No AI providers available - please configure API keys")
        self._current_provider = None
        self._current_model = None
    
    def get_api_key(self, provider: str, user: Optional[Any] = None) -> Optional[str]:
        """Get API key for a specific provider and user"""
        # First try user-specific API key manager if user is provided
        if user:
            try:
                from app.services.user_api_key_manager import user_api_key_manager
                user_key = user_api_key_manager.get_api_key(user, provider)
                if user_key:
                    return user_key
            except Exception as e:
                logger.warning(f"Failed to get user-specific API key for {provider}: {e}")
        
        # Fallback to dynamic API key manager (for backward compatibility)
        try:
            from app.services.api_key_manager import api_key_manager
            dynamic_key = api_key_manager.get_api_key(provider)
            if dynamic_key:
                return dynamic_key
        except Exception as e:
            logger.warning(f"Failed to get dynamic API key for {provider}: {e}")
        
        # No environment variable fallback - user must configure via frontend
        return None
    
    def get_current_model(self) -> Tuple[str, str]:
        """Get current provider and model"""
        return self._current_provider, self._current_model
    
    def get_current_provider(self) -> str:
        """Get current provider name"""
        if self._current_provider is None:
            # Try to auto-select a provider if none is set
            self._auto_select_provider()
        return self._current_provider
    
    def get_current_model_name(self) -> str:
        """Get current model name"""
        return self._current_model
    
    def set_current_model(self, provider: str, model: str) -> bool:
        """Set the current active model"""
        if provider in self._model_configs and model in self._model_configs[provider]:
            self._current_provider = provider
            self._current_model = model
            return True
        return False
    
    def get_model_config(self, provider: Optional[str] = None, model: Optional[str] = None) -> Optional[ModelConfig]:
        """Get configuration for a specific model or the current model"""
        provider = provider or self._current_provider
        model = model or self._current_model
        
        if provider in self._model_configs and model in self._model_configs[provider]:
            return self._model_configs[provider][model]
        return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self._model_configs.keys())
    
    def get_available_models(self, provider: str) -> List[str]:
        """Get list of available models for a provider"""
        return list(self._model_configs.get(provider, {}).keys())
    
    def get_all_available_models(self) -> Dict[str, List[str]]:
        """Get all available models grouped by provider"""
        return {
            provider: list(models.keys())
            for provider, models in self._model_configs.items()
        }
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for provider in self._model_configs.keys():
            api_key = self.get_api_key(provider)
            status[provider] = {
                "available": bool(api_key),
                "api_key_configured": bool(api_key),
                "models": list(self._model_configs[provider].keys())
            }
        return status


# Global configuration instance
ai_config = AIConfig()
