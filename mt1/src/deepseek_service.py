"""
DeepSeek API Service
==================

This module provides integration with DeepSeek AI models.
"""

import os
import httpx
import asyncio
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DeepSeekService:
    """
    Service class for interacting with DeepSeek API.
    """
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "sk-deepseek-dummy-key-replace-with-actual")
        self.base_url = "https://api.deepseek.com"
        self.client = None
        
        # Initialize HTTP client
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize the HTTP client for DeepSeek API."""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=120.0
            )
            logger.info("DeepSeek client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize DeepSeek client: {e}")
            
    async def _make_request(self, model: str, messages: list, temperature: float = 0.3, max_tokens: int = 4000) -> str:
        """
        Make a request to DeepSeek API.
        
        Args:
            model: DeepSeek model name
            messages: List of message objects
            temperature: Response randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        try:
            if not self.client:
                raise Exception("DeepSeek client not initialized")
                
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            logger.info(f"Making DeepSeek API request with model: {model}")
            
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise Exception("Invalid response format from DeepSeek API")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"DeepSeek API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            raise
    
    async def generate_response(self, prompt: str, model: str = "deepseek-chat", 
                               temperature: float = 0.3, max_tokens: int = 4000) -> str:
        """
        Generate a response using DeepSeek models.
        
        Args:
            prompt: The input prompt
            model: DeepSeek model to use
            temperature: Response randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        messages = [{"role": "user", "content": prompt}]
        return await self._make_request(model, messages, temperature, max_tokens)
    
    async def chat_completion(self, messages: list, model: str = "deepseek-chat",
                             temperature: float = 0.3, max_tokens: int = 4000) -> str:
        """
        Generate a chat completion using DeepSeek models.
        
        Args:
            messages: List of message objects with role and content
            model: DeepSeek model to use
            temperature: Response randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated response text
        """
        return await self._make_request(model, messages, temperature, max_tokens)
    
    def get_available_models(self) -> list:
        """
        Get list of available DeepSeek models.
        
        Returns:
            List of model names
        """
        return [
            "deepseek-chat",
            "deepseek-coder", 
            "deepseek-reasoner"
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the DeepSeek service.
        
        Returns:
            Dictionary containing service status
        """
        return {
            "service": "deepseek",
            "available": self.client is not None,
            "api_key_configured": bool(self.api_key and self.api_key != "sk-deepseek-dummy-key-replace-with-actual"),
            "base_url": self.base_url,
            "available_models": self.get_available_models()
        }
    
    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()


# Global instance
deepseek_service = DeepSeekService()
