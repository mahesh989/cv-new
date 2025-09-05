"""
Base AI Provider Interface

This module defines the common interface that all AI providers must implement.
This ensures consistency across different AI services (OpenAI, Claude, DeepSeek, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum


class AIModelType(Enum):
    """Enum for different types of AI models"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"


class AIResponse:
    """Standardized response format for all AI providers"""
    
    def __init__(
        self, 
        content: str, 
        model: str, 
        provider: str, 
        tokens_used: Optional[int] = None,
        cost: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.model = model
        self.provider = provider
        self.tokens_used = tokens_used
        self.cost = cost
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format"""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "metadata": self.metadata
        }


class BaseAIProvider(ABC):
    """
    Abstract base class for all AI providers.
    
    All AI providers (OpenAI, Claude, DeepSeek, etc.) must inherit from this class
    and implement all abstract methods.
    """
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.provider_name = self._get_provider_name()
    
    @abstractmethod
    def _get_provider_name(self) -> str:
        """Return the name of this provider (e.g., 'openai', 'anthropic', 'deepseek')"""
        pass
    
    @abstractmethod
    def _validate_api_key(self) -> bool:
        """Validate if the API key is properly formatted and potentially working"""
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate a response from the AI model.
        
        Args:
            prompt: The user prompt/input
            system_prompt: Optional system prompt to set context
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIResponse object with standardized format
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Return list of available models for this provider"""
        pass
    
    @abstractmethod
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Return information about a specific model"""
        pass
    
    def is_available(self) -> bool:
        """Check if this provider is available (has API key and is reachable)"""
        try:
            return self._validate_api_key()
        except Exception:
            return False
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Return status information about this provider"""
        return {
            "provider": self.provider_name,
            "model": self.model_name,
            "available": self.is_available(),
            "api_key_configured": bool(self.api_key),
        }
