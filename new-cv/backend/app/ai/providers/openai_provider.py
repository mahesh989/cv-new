"""
OpenAI Provider Implementation

This module implements the OpenAI provider for the AI service system.
"""

import openai
from typing import Dict, List, Optional, Any
from app.ai.base_provider import BaseAIProvider, AIResponse
import logging

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key, model_name)
        self.client = openai.OpenAI(api_key=api_key)
    
    def _get_provider_name(self) -> str:
        """Return the provider name"""
        return "openai"
    
    def _validate_api_key(self) -> bool:
        """Validate if the API key is working"""
        try:
            # Try to list models as a test
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {e}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response using OpenAI"""
        
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add user prompt
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request parameters
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            # Add any additional parameters
            request_params.update(kwargs)
            
            # Make API call
            response = self.client.chat.completions.create(**request_params)
            
            # Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            # Calculate cost (approximate)
            cost = self._calculate_cost(tokens_used) if tokens_used else None
            
            return AIResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                tokens_used=tokens_used,
                cost=cost,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id,
                    "created": response.created
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        model_info = {
            "gpt-4o": {
                "name": "GPT-4o",
                "description": "Most advanced GPT-4 model with improved performance",
                "max_tokens": 128000,
                "input_cost_per_1k": 0.005,
                "output_cost_per_1k": 0.015
            },
            "gpt-4o-mini": {
                "name": "GPT-4o Mini", 
                "description": "Faster and more cost-effective GPT-4 variant",
                "max_tokens": 128000,
                "input_cost_per_1k": 0.00015,
                "output_cost_per_1k": 0.0006
            },
            "gpt-4-turbo": {
                "name": "GPT-4 Turbo",
                "description": "High-performance GPT-4 with larger context window",
                "max_tokens": 128000,
                "input_cost_per_1k": 0.01,
                "output_cost_per_1k": 0.03
            },
            "gpt-3.5-turbo": {
                "name": "GPT-3.5 Turbo",
                "description": "Fast and cost-effective model for most tasks",
                "max_tokens": 16384,
                "input_cost_per_1k": 0.001,
                "output_cost_per_1k": 0.002
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
