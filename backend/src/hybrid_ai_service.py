import os
from dotenv import load_dotenv
import logging
from .deepseek_service import deepseek_service
from typing import Optional, Dict, Any, List

load_dotenv()

logger = logging.getLogger(__name__)

class DeepSeekAIService:
    """
    DeepSeek-only AI Service for all AI operations.
    """
    
    def __init__(self):
        self.deepseek_client = None
        self.provider = "deepseek"
        
        # Initialize DeepSeek client
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize DeepSeek client if API key is available."""
        try:
            deepseek_key = os.getenv("DEEPSEEK_API_KEY")
            if deepseek_key and deepseek_key != "sk-deepseek-dummy-key-replace-with-actual":
                self.deepseek_client = deepseek_service
                logger.info("DeepSeek client initialized successfully")
            else:
                raise ValueError("DeepSeek API key not found or invalid")
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {e}")
            raise RuntimeError("DeepSeek client initialization failed. Please check your DEEPSEEK_API_KEY.")
            
    async def _call_deepseek(self, prompt: str, model: str = 'deepseek-chat',
                            temperature: float = 0.3, max_tokens: int = 4000) -> str:
        """Make a call to DeepSeek API."""
        try:
            response = await self.deepseek_client.generate_response(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            raise
            
    async def generate_response(self, prompt: str, provider: Optional[str] = None,
                               model: Optional[str] = None, temperature: float = 0.3,
                               max_tokens: int = 4000) -> str:
        """
        Generate a response using DeepSeek.
        
        Args:
            prompt: The input prompt
            provider: Ignored (for backward compatibility)
            model: Specific DeepSeek model to use (optional, defaults to 'deepseek-chat')
            temperature: Response randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        if not self.deepseek_client:
            raise RuntimeError("DeepSeek client not initialized")
            
        # Use DeepSeek for all requests
        return await self._call_deepseek(prompt, model or 'deepseek-chat', temperature, max_tokens)
            
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers (DeepSeek only)."""
        return ["deepseek"] if self.deepseek_client else []
        
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the DeepSeek AI service."""
        return {
            "provider": self.provider,
            "available_providers": self.get_available_providers(),
            "deepseek_available": self.deepseek_client is not None,
            "status": "ready" if self.deepseek_client else "not_initialized"
        }

# Global instance (keeping the same name for backward compatibility)
hybrid_ai = DeepSeekAIService()
