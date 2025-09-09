"""
DeepSeek Provider Implementation

This module implements the DeepSeek provider for the AI service system.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from app.ai.base_provider import BaseAIProvider, AIResponse
import logging

logger = logging.getLogger(__name__)


class DeepSeekProvider(BaseAIProvider):
    """DeepSeek provider implementation"""
    
    def __init__(self, api_key: str, model_name: str = "deepseek-chat"):
        super().__init__(api_key, model_name)
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_provider_name(self) -> str:
        """Return the provider name"""
        return "deepseek"
    
    def _validate_api_key(self) -> bool:
        """Validate if the API key is working"""
        try:
            # Try to list models as a test
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"DeepSeek API key validation failed: {e}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response using DeepSeek"""
        
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            # Add any additional parameters
            payload.update(kwargs)
            
            # Make API call with extended read timeout (connect, read)
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=(15, 120)
            )
            
            if response.status_code != 200:
                raise Exception(f"DeepSeek API returned status {response.status_code}: {response.text}")
            
            response_data = response.json()
            
            # Extract response data
            content = response_data["choices"][0]["message"]["content"]
            tokens_used = response_data.get("usage", {}).get("total_tokens")
            
            # Calculate cost (approximate)
            cost = self._calculate_cost(tokens_used) if tokens_used else None
            
            return AIResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                tokens_used=tokens_used,
                cost=cost,
                metadata={
                    "finish_reason": response_data["choices"][0].get("finish_reason"),
                    "response_id": response_data.get("id"),
                    "created": response_data.get("created")
                }
            )
            
        except Exception as e:
            logger.error(f"DeepSeek API call failed: {e}")
            raise Exception(f"DeepSeek API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available DeepSeek models"""
        return [
            "deepseek-chat",
            "deepseek-coder", 
            "deepseek-reasoner"
        ]
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        model_info = {
            "deepseek-chat": {
                "name": "DeepSeek Chat",
                "description": "General-purpose chat model with strong reasoning capabilities",
                "max_tokens": 32000,
                "input_cost_per_1k": 0.00014,
                "output_cost_per_1k": 0.00028
            },
            "deepseek-coder": {
                "name": "DeepSeek Coder",
                "description": "Specialized model for code generation and programming tasks",
                "max_tokens": 32000,
                "input_cost_per_1k": 0.00014,
                "output_cost_per_1k": 0.00028
            },
            "deepseek-reasoner": {
                "name": "DeepSeek Reasoner",
                "description": "Advanced reasoning model for complex analytical tasks",
                "max_tokens": 32000,
                "input_cost_per_1k": 0.00055,
                "output_cost_per_1k": 0.0022
            }
        }
        
        return model_info.get(model_name, {})
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate approximate cost based on tokens"""
        model_info = self.get_model_info(self.model_name)
        if not model_info:
            return 0.0
        
        # Rough estimation: assume 70% input, 30% output tokens
        input_tokens = int(tokens_used * 0.7)
        output_tokens = int(tokens_used * 0.3)
        
        input_cost = (input_tokens / 1000) * model_info.get("input_cost_per_1k", 0)
        output_cost = (output_tokens / 1000) * model_info.get("output_cost_per_1k", 0)
        
        return input_cost + output_cost
