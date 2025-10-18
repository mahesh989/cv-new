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
        # Increase timeout for nano models (GPT-5-nano) that may take longer to respond
        timeout = 900.0 if model_name in ["gpt-5-nano"] or model_name.startswith("o3") else 60.0
        self.client = openai.OpenAI(api_key=api_key, timeout=timeout)
    
    def _get_provider_name(self) -> str:
        """Return the provider name"""
        return "openai"
    
    def _validate_api_key(self) -> bool:
        """Validate if the API key is working"""
        try:
            # Check if API key format is correct
            if not self.api_key or not self.api_key.startswith('sk-'):
                logger.error("OpenAI API key format is invalid")
                return False
            
            # Try a simple API call to validate the key
            # Use a lightweight endpoint instead of models.list()
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI API key validation failed: {e}")
            # Log more specific error information
            if hasattr(e, 'response') and e.response:
                logger.error(f"HTTP Status: {e.response.status_code}")
                logger.error(f"Response: {e.response.text}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
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
            
            # Map custom model names to actual OpenAI model names and set special parameters
            actual_model = self.model_name
            request_params = {
                "model": actual_model,
                "messages": messages,
                "temperature": temperature,
            }
            
            # Add service_tier for nano models (GPT-5-nano and O3 models)
            if self.model_name in ["gpt-5-nano"] or self.model_name.startswith("o3"):
                request_params["service_tier"] = "flex"
            
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
            "gpt-3.5-turbo",
            "gpt-5-nano"
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
            },
            "gpt-5-nano": {
                "name": "GPT-5 Nano",
                "description": "Latest nano model with flexible service tier for optimized performance",
                "max_tokens": 200000,
                "input_cost_per_1k": 5e-05,
                "output_cost_per_1k": 0.0002
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
