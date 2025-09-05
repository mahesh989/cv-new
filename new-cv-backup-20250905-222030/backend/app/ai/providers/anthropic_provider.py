"""
Anthropic (Claude) Provider Implementation

This module implements the Anthropic provider for the AI service system.
"""

import anthropic
from typing import Dict, List, Optional, Any
from app.ai.base_provider import BaseAIProvider, AIResponse
import logging

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseAIProvider):
    """Anthropic (Claude) provider implementation"""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-haiku-20241022"):
        super().__init__(api_key, model_name)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def _get_provider_name(self) -> str:
        """Return the provider name"""
        return "anthropic"
    
    def _validate_api_key(self) -> bool:
        """Validate if the API key is working"""
        try:
            # Try a simple completion as a test
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception as e:
            logger.error(f"Anthropic API key validation failed: {e}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AIResponse:
        """Generate response using Anthropic Claude"""
        
        try:
            # Prepare request parameters
            request_params = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens or 4000,  # Claude requires max_tokens
            }
            
            # Add system prompt if provided
            if system_prompt:
                request_params["system"] = system_prompt
            
            # Add any additional parameters
            request_params.update(kwargs)
            
            # Make API call
            response = self.client.messages.create(**request_params)
            
            # Extract response data
            content = response.content[0].text if response.content else ""
            tokens_used = None
            
            # Try to get token usage if available
            if hasattr(response, 'usage'):
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Calculate cost (approximate)
            cost = self._calculate_cost(tokens_used) if tokens_used else None
            
            return AIResponse(
                content=content,
                model=self.model_name,
                provider=self.provider_name,
                tokens_used=tokens_used,
                cost=cost,
                metadata={
                    "stop_reason": response.stop_reason,
                    "response_id": response.id,
                    "role": response.role
                }
            )
            
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229"
        ]
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        model_info = {
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet",
                "description": "Most intelligent model with best performance on complex tasks",
                "max_tokens": 200000,
                "input_cost_per_1k": 0.003,
                "output_cost_per_1k": 0.015
            },
            "claude-3-5-haiku-20241022": {
                "name": "Claude 3.5 Haiku",
                "description": "Fastest model for everyday tasks",
                "max_tokens": 200000,
                "input_cost_per_1k": 0.00025,
                "output_cost_per_1k": 0.00125
            },
            "claude-3-opus-20240229": {
                "name": "Claude 3 Opus",
                "description": "Most powerful model for highly complex tasks",
                "max_tokens": 200000,
                "input_cost_per_1k": 0.015,
                "output_cost_per_1k": 0.075
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
