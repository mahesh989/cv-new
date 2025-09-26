"""
Enhanced AI Service with API Key Validation

This module extends the existing AI service to include API key validation
and error handling for missing API keys.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status

from app.ai.ai_service import AIServiceManager
from app.services.api_key_manager import api_key_manager
from app.ai.base_provider import AIResponse

logger = logging.getLogger(__name__)


class EnhancedAIService:
    """
    Enhanced AI service with API key validation and error handling.
    
    This service wraps the existing AIServiceManager and adds:
    - API key validation before AI calls
    - Provider-specific error messages
    - Dynamic API key management
    """
    
    def __init__(self):
        self.ai_service = AIServiceManager()
        self.api_key_manager = api_key_manager
    
    def _validate_provider_api_key(self, provider: str) -> Tuple[bool, str]:
        """
        Validate API key for a specific provider
        
        Args:
            provider: AI provider name
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            # Check if API key exists
            if not self.api_key_manager.has_api_key(provider):
                return False, f"No API key configured for {provider}. Please add your API key to use this provider."
            
            # Validate the API key
            is_valid, message = self.api_key_manager.validate_api_key(provider)
            return is_valid, message
            
        except Exception as e:
            logger.error(f"Error validating API key for {provider}: {e}")
            return False, f"Failed to validate API key for {provider}: {str(e)}"
    
    def _get_provider_from_model(self, model_id: str) -> Optional[str]:
        """
        Get provider name from model ID
        
        Args:
            model_id: Model identifier
            
        Returns:
            str: Provider name or None
        """
        # Map model IDs to providers
        model_to_provider = {
            # OpenAI models
            'gpt-4o': 'openai',
            'gpt-4o-mini': 'openai',
            'gpt-4-turbo': 'openai',
            'gpt-3.5-turbo': 'openai',
            'gpt-5-nano': 'openai',
            
            # Anthropic models
            'claude-3.5-sonnet': 'anthropic',
            'claude-3.5-sonnet-20241022': 'anthropic',
            'claude-3-haiku': 'anthropic',
            'claude-3-5-haiku-20241022': 'anthropic',
            'claude-3-opus': 'anthropic',
            'claude-3-opus-20240229': 'anthropic',
            
            # DeepSeek models
            'deepseek-chat': 'deepseek',
            'deepseek-coder': 'deepseek',
            'deepseek-reasoner': 'deepseek'
        }
        
        return model_to_provider.get(model_id)
    
    def _get_provider_display_name(self, provider: str) -> str:
        """Get display name for provider"""
        display_names = {
            'openai': 'OpenAI',
            'anthropic': 'Anthropic (Claude)',
            'deepseek': 'DeepSeek'
        }
        return display_names.get(provider, provider.title() if provider else "Unknown")
    
    async def generate_response_with_validation(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate AI response with API key validation
        
        Args:
            prompt: Input prompt
            system_prompt: System prompt
            temperature: Temperature setting
            max_tokens: Maximum tokens
            provider_name: Specific provider to use
            model_name: Specific model to use
            **kwargs: Additional arguments
            
        Returns:
            AIResponse: AI response or raises HTTPException
            
        Raises:
            HTTPException: If API key is missing or invalid
        """
        try:
            # Determine provider to use
            if provider_name:
                target_provider = provider_name
            elif model_name:
                target_provider = self._get_provider_from_model(model_name)
                if not target_provider:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unknown model: {model_name}"
                    )
            else:
                # Use current provider from AI service
                target_provider = self.ai_service.config.get_current_provider()
            
            # Validate API key for the provider
            is_valid, message = self._validate_provider_api_key(target_provider)
            
            if not is_valid:
                provider_display = self._get_provider_display_name(target_provider)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "API_KEY_REQUIRED",
                        "message": f"API key required for {provider_display}",
                        "provider": target_provider,
                        "provider_display": provider_display,
                        "details": message,
                        "action_required": "Please configure your API key for this provider"
                    }
                )
            
            # Proceed with AI call
            response = await self.ai_service.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                provider_name=provider_name,
                **kwargs
            )
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in enhanced AI service: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service error: {str(e)}"
            )
    
    async def analyze_cv_content_with_validation(
        self,
        cv_text: str,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze CV content with API key validation
        
        Args:
            cv_text: CV text to analyze
            provider_name: Specific provider to use
            
        Returns:
            Dict[str, Any]: Analysis results
            
        Raises:
            HTTPException: If API key is missing or invalid
        """
        try:
            # Use the enhanced generate_response method
            response = await self.generate_response_with_validation(
                prompt=cv_text,
                system_prompt="You are an expert CV analyst. Analyze the CV content and provide insights.",
                provider_name=provider_name
            )
            
            return {
                "analysis": response.content,
                "provider": response.provider,
                "model": response.model,
                "cost": response.cost,
                "tokens_used": response.tokens_used
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error analyzing CV content: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"CV analysis error: {str(e)}"
            )
    
    async def compare_cv_with_job_with_validation(
        self,
        cv_text: str,
        job_description: str,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare CV with job description with API key validation
        
        Args:
            cv_text: CV text
            job_description: Job description
            provider_name: Specific provider to use
            
        Returns:
            Dict[str, Any]: Comparison results
            
        Raises:
            HTTPException: If API key is missing or invalid
        """
        try:
            comparison_prompt = f"""
            Compare the following CV with the job description:
            
            CV:
            {cv_text}
            
            Job Description:
            {job_description}
            
            Provide a detailed analysis of the match.
            """
            
            # Use the enhanced generate_response method
            response = await self.generate_response_with_validation(
                prompt=comparison_prompt,
                system_prompt="You are an expert job matching analyst. Compare the CV with the job description and provide detailed insights.",
                provider_name=provider_name
            )
            
            return {
                "comparison": response.content,
                "provider": response.provider,
                "model": response.model,
                "cost": response.cost,
                "tokens_used": response.tokens_used
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error comparing CV with job: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"CV-Job comparison error: {str(e)}"
            )
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers with API key information"""
        try:
            # Get AI service provider status
            ai_status = self.ai_service.get_provider_status()
            
            # Get API key manager status
            api_key_status = self.api_key_manager.get_provider_status()
            
            # Combine the information
            combined_status = {}
            for provider in ['openai', 'anthropic', 'deepseek']:
                combined_status[provider] = {
                    "ai_service_available": ai_status.get(provider, {}).get("available", False),
                    "api_key_configured": api_key_status.get(provider, {}).get("has_api_key", False),
                    "api_key_valid": api_key_status.get(provider, {}).get("is_valid", False),
                    "last_validated": api_key_status.get(provider, {}).get("last_validated"),
                    "created_at": api_key_status.get(provider, {}).get("created_at"),
                    "models": ai_status.get(provider, {}).get("models", [])
                }
            
            return combined_status
            
        except Exception as e:
            logger.error(f"Error getting provider status: {e}")
            return {}


# Global enhanced AI service instance
enhanced_ai_service = EnhancedAIService()
