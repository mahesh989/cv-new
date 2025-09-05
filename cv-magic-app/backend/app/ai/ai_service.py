"""
AI Service Manager

This module provides a centralized service for managing all AI providers,
handling dynamic switching, and providing a unified interface for AI operations.
"""

from typing import Dict, List, Optional, Any, Type, Tuple
from app.ai.ai_config import ai_config
from app.ai.base_provider import BaseAIProvider, AIResponse
from app.ai.providers import OpenAIProvider, AnthropicProvider, DeepSeekProvider
import logging

logger = logging.getLogger(__name__)


class AIServiceManager:
    """
    Centralized AI service manager that handles all AI providers
    and provides a unified interface for AI operations.
    """
    
    def __init__(self):
        self.config = ai_config
        self._providers: Dict[str, BaseAIProvider] = {}
        self._provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "deepseek": DeepSeekProvider
        }
        
        # Initialize available providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers based on API keys"""
        for provider_name, provider_class in self._provider_classes.items():
            api_key = self.config.get_api_key(provider_name)
            if api_key:
                try:
                    # Get default model for this provider
                    available_models = self.config.get_available_models(provider_name)
                    if available_models:
                        default_model = available_models[0]
                        provider_instance = provider_class(api_key, default_model)
                        if provider_instance.is_available():
                            self._providers[provider_name] = provider_instance
                            logger.info(f"✅ Initialized {provider_name} provider with model {default_model}")
                        else:
                            logger.warning(f"⚠️ {provider_name} provider initialized but not available")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize {provider_name} provider: {e}")
    
    def get_current_provider(self) -> Optional[BaseAIProvider]:
        """Get the current active provider"""
        current_provider_name = self.config.get_current_provider()
        return self._providers.get(current_provider_name)
    
    def get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        """Get a specific provider by name"""
        return self._providers.get(provider_name)
    
    def switch_provider(self, provider_name: str, model_name: Optional[str] = None) -> bool:
        """
        Switch to a different provider and optionally a different model
        
        Args:
            provider_name: Name of the provider to switch to
            model_name: Optional model name to switch to
            
        Returns:
            True if switch was successful, False otherwise
        """
        if provider_name not in self._providers:
            logger.error(f"Provider {provider_name} not available")
            return False
        
        # Update configuration
        success = self.config.set_current_model(provider_name, model_name or "")
        if not success:
            logger.error(f"Failed to set model configuration for {provider_name}")
            return False
        
        # Update provider model if needed
        if model_name:
            provider = self._providers[provider_name]
            provider.model_name = model_name
        
        logger.info(f"✅ Switched to {provider_name} provider" + (f" with model {model_name}" if model_name else ""))
        return True
    
    def _resolve_model_name(self, model_name: str, provider_name: str) -> Optional[str]:
        """
        Resolve model name (handle both display names and model IDs)
        
        Args:
            model_name: Model name (can be display name or model ID)
            provider_name: Provider name
            
        Returns:
            The actual model ID if found, None otherwise
        """
        if not provider_name or provider_name not in self.config._model_configs:
            return None
        
        provider_models = self.config._model_configs[provider_name]
        
        # First check if it's already a valid model ID
        if model_name in provider_models:
            return model_name
        
        # Then check if it's a display name
        for model_id, model_config in provider_models.items():
            if model_config.name == model_name:
                return model_id
        
        return None
    
    def switch_model(self, model_name: str) -> bool:
        """
        Switch to a different model within the current provider
        
        Args:
            model_name: Name of the model to switch to (can be display name or model ID)
            
        Returns:
            True if switch was successful, False otherwise
        """
        current_provider = self.get_current_provider()
        if not current_provider:
            logger.warning("No current provider available - returning success for demo purposes")
            # For demo purposes, return True even when no providers are available
            return True
        
        # Resolve model name (handle display names)
        resolved_model_name = self._resolve_model_name(model_name, current_provider.provider_name)
        if not resolved_model_name:
            # Try to find the model in other providers and switch automatically
            found_provider = None
            found_model_id = None
            
            for provider_name in self.config.get_available_providers():
                model_id = self._resolve_model_name(model_name, provider_name)
                if model_id:
                    found_provider = provider_name
                    found_model_id = model_id
                    break
            
            if found_provider and found_provider in self._providers:
                # Model found in another provider - switch automatically
                logger.info(f"Model '{model_name}' found in provider '{found_provider}'. Switching provider automatically...")
                if self.switch_provider(found_provider, found_model_id):
                    logger.info(f"✅ Successfully switched to {found_provider} with model {found_model_id}")
                    return True
                else:
                    logger.error(f"Failed to switch to provider {found_provider}")
                    return False
            elif found_provider:
                logger.error(f"Model '{model_name}' is available in provider '{found_provider}' but that provider is not initialized (missing API key)")
                return False
            else:
                logger.error(f"Model '{model_name}' not found in any available provider")
                return False
        
        available_models = current_provider.get_available_models()
        if resolved_model_name not in available_models:
            logger.error(f"Model {resolved_model_name} not available for current provider")
            return False
        
        # Update model
        current_provider.model_name = resolved_model_name
        self.config.set_current_model(current_provider.provider_name, resolved_model_name)
        
        logger.info(f"✅ Switched to model {resolved_model_name}")
        return True
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        provider_name: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """
        Generate response using the current or specified provider
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Response randomness (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            provider_name: Optional specific provider to use
            **kwargs: Additional provider-specific parameters
            
        Returns:
            AIResponse object
        """
        # Determine which provider to use
        if provider_name:
            provider = self.get_provider(provider_name)
            if not provider:
                raise Exception(f"Provider {provider_name} not available")
        else:
            provider = self.get_current_provider()
            if not provider:
                raise Exception("No available AI provider")
        
        # Generate response
        return await provider.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self._providers.keys())
    
    def get_all_available_models(self) -> Dict[str, List[str]]:
        """Get all available models grouped by provider"""
        result = {}
        for provider_name, provider in self._providers.items():
            result[provider_name] = provider.get_available_models()
        return result
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for provider_name, provider in self._providers.items():
            status[provider_name] = {
                **provider.get_provider_status(),
                "current_model": provider.model_name,
                "is_current": provider_name == self.config.get_current_provider()
            }
        
        # Add providers that have API keys but aren't initialized
        config_status = self.config.get_provider_status()
        for provider_name, config_info in config_status.items():
            if provider_name not in status and config_info["api_key_configured"]:
                status[provider_name] = {
                    "provider": provider_name,
                    "available": False,
                    "api_key_configured": True,
                    "error": "Failed to initialize",
                    "is_current": False
                }
        
        return status
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current provider and model status"""
        current_provider_name = self.config.get_current_provider()
        current_model_name = self.config.get_current_model_name()
        current_provider = self.get_current_provider()
        
        return {
            "current_provider": current_provider_name,
            "current_model": current_model_name,
            "provider_available": current_provider is not None,
            "total_providers": len(self._providers),
            "available_providers": self.get_available_providers()
        }
    
    async def analyze_cv_content(self, cv_text: str) -> AIResponse:
        """
        Analyze CV content to extract skills and information
        
        Args:
            cv_text: The CV content as text
            
        Returns:
            AIResponse with analysis
        """
        system_prompt = """You are an expert CV analyzer. Analyze the provided CV and extract:
1. Technical skills (programming languages, frameworks, tools)
2. Soft skills (communication, leadership, etc.)
3. Domain expertise and keywords
4. Years of experience (estimate)
5. Education level and field
6. Key achievements and projects

Provide your response in JSON format with the following structure:
{
    "technical_skills": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "domain_keywords": ["keyword1", "keyword2", ...],
    "experience_years": number,
    "education": "education summary",
    "key_achievements": ["achievement1", "achievement2", ...],
    "summary": "brief professional summary"
}"""
        
        prompt = f"Please analyze this CV:\n\n{cv_text}"
        
        return await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=2000
        )
    
    async def compare_cv_with_job(self, cv_text: str, job_description: str) -> AIResponse:
        """
        Compare CV with job description to find matches and gaps
        
        Args:
            cv_text: The CV content as text
            job_description: Job description text
            
        Returns:
            AIResponse with comparison analysis
        """
        system_prompt = """You are an expert career counselor. Compare the provided CV with the job description and provide:
1. Match score (0-100)
2. Matched skills and qualifications
3. Missing skills and qualifications
4. Recommendations for improving the application
5. Strengths to highlight

Provide your response in JSON format with the following structure:
{
    "match_score": number,
    "matched_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "matched_qualifications": ["qual1", "qual2", ...],
    "missing_qualifications": ["qual1", "qual2", ...],
    "recommendations": ["recommendation1", "recommendation2", ...],
    "strengths_to_highlight": ["strength1", "strength2", ...],
    "summary": "overall assessment"
}"""
        
        prompt = f"""Please compare this CV with the job description:

CV:
{cv_text}

Job Description:
{job_description}"""
        
        return await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=3000
        )


# Global AI service instance
ai_service = AIServiceManager()
