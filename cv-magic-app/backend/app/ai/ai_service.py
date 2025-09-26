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
from app.core.model_dependency import get_request_model

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
    
    def refresh_providers(self):
        """Refresh all providers after API keys have been updated"""
        logger.info("🔄 Refreshing AI providers after API key changes")
        self._providers.clear()
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
        provider = self._providers.get(current_provider_name)
        
        # Debug logging to help diagnose issues
        if not provider:
            logger.error(f"❌ [AI_SERVICE] No provider found for '{current_provider_name}'")
            logger.error(f"❌ [AI_SERVICE] Available providers: {list(self._providers.keys())}")
            logger.error(f"❌ [AI_SERVICE] Current provider name: {current_provider_name}")
            logger.error(f"❌ [AI_SERVICE] Provider status: {self.get_provider_status()}")
        
        return provider
    
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
            logger.error("❌ No current provider available for model switching")
            # Don't silently succeed - this masks real problems
            available_providers = self.get_available_providers()
            if available_providers:
                logger.info(f"🔄 Available providers: {available_providers}")
                # Try to switch to the model in any available provider
                for provider_name in available_providers:
                    if self.switch_provider(provider_name, model_name):
                        return True
            return False
        
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
        # Check if there's a request-specific model set
        request_model_id = get_request_model()
        if request_model_id:
            # Ensure we're using the request-specific model
            logger.debug(f"Using request-specific model: {request_model_id}")
            # The model should already be switched by the dependency
            # but let's make sure the provider is correctly set
            current_provider_name = self.config.get_current_provider()
            provider = self._providers.get(current_provider_name)
            if provider and provider.model_name != request_model_id:
                # Need to ensure the model is correctly set
                model_config = self.config.get_model_config()
                if model_config and model_config.model == request_model_id:
                    provider.model_name = request_model_id
                    logger.debug(f"Updated provider model to match request: {request_model_id}")
        
        # Determine which provider to use
        if provider_name:
            provider = self.get_provider(provider_name)
            if not provider:
                available_providers = self.get_available_providers()
                logger.error(f"❌ Provider '{provider_name}' not available. Available providers: {available_providers}")
                raise Exception(f"Provider '{provider_name}' not available. Available providers: {available_providers}")
        else:
            provider = self.get_current_provider()
            if not provider:
                available_providers = self.get_available_providers()
                current_provider_name = self.config.get_current_provider()
                logger.error(f"❌ No available AI provider. Current: '{current_provider_name}', Available: {available_providers}")
                
                # Try to get first available provider as fallback
                if available_providers:
                    fallback_provider = available_providers[0]
                    logger.warning(f"🔄 Using fallback provider: {fallback_provider}")
                    provider = self.get_provider(fallback_provider)
                    if provider:
                        # Update current provider to the working one
                        self.config.set_current_model(fallback_provider, provider.model_name)
                    else:
                        raise Exception(f"No available AI provider. Current: '{current_provider_name}', Available: {available_providers}")
                else:
                    raise Exception(f"No available AI provider. Current: '{current_provider_name}', Available: {available_providers}")
        
        # Log the actual model being used
        logger.info(f"Generating response with provider: {provider.provider_name}, model: {provider.model_name}")
        
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
    
    def get_current_model_name(self) -> str:
        """Get the current model name"""
        current_provider = self.get_current_provider()
        if current_provider:
            return current_provider.model_name
        return self.config.get_current_model_name() or "unknown"
    
    @property
    def current_model(self) -> str:
        """Property to get the current model name for backward compatibility"""
        return self.get_current_model_name()
    
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
    
    async def analyze_job_description(self, job_description: str) -> AIResponse:
        """
        Analyze job description to extract required and preferred keywords
        
        Args:
            job_description: Job description text to analyze
            
        Returns:
            AIResponse with keyword analysis
        """
        system_prompt = """You are an expert job description analyzer. Your task is to extract keywords and skills from job descriptions and classify them as either "required" or "preferred" based on the language used.

CLASSIFICATION RULES:

REQUIRED KEYWORDS - Extract from text that uses definitive/mandatory language:
- "Minimum X years"
- "Experience in/with"
- "Strong [skill] skills"
- "Must have"
- "Required"
- "Essential"
- "Necessary"
- From sections like "Requirements", "Must Have", "Essential Criteria"

PREFERRED KEYWORDS - Extract from text that uses softer/optional language:
- "Knowledge of"
- "Appreciation of" 
- "Understanding of"
- "Familiarity with"
- "Nice to have"
- "Preferred"
- "Desirable"
- "Would be an advantage"
- From sections like "Preferred", "Nice to Have", "Desirable"

EXTRACTION GUIDELINES:
1. Focus on concrete, actionable keywords (technologies, tools, methodologies, skills)
2. Extract specific software names, programming languages, frameworks
3. Include relevant experience levels (e.g., "2+ years", "senior level")
4. Include both technical and soft skills
5. Keep keywords concise and matchable
6. Remove filler words and focus on the core skill/requirement

OUTPUT FORMAT:
Respond with a JSON object only, no additional text:
{
    "required_keywords": ["keyword1", "keyword2", ...],
    "preferred_keywords": ["keyword1", "keyword2", ...],
    "all_keywords": ["all_keywords_combined"],
    "experience_years": number_or_null
}"""
        
        prompt = f"""Analyze the following job description and extract required and preferred keywords/skills:

{job_description}

Remember to classify keywords based on the language context they appear in. Focus on extracting concrete, matchable skills and technologies."""
        
        return await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=2000
        )
    
    async def match_cv_against_jd_keywords(
        self, 
        cv_content: str, 
        required_keywords: List[str], 
        preferred_keywords: List[str]
    ) -> AIResponse:
        """
        Match CV content against job description keywords using AI-powered smart matching
        
        Args:
            cv_content: CV text content to analyze
            required_keywords: List of required keywords from JD analysis
            preferred_keywords: List of preferred keywords from JD analysis
            
        Returns:
            AIResponse with matching results
        """
        system_prompt = """You are an expert CV-JD matching analyst. Your task is to analyze a CV against job description keywords and determine which keywords are present in the CV content using intelligent matching.

MATCHING RULES:

SMART MATCHING LOGIC:
1. **Exact Matches**: Direct keyword matches (case-insensitive)
2. **Synonym Matches**: Related terms and synonyms
3. **Context Matches**: Keywords found in relevant context
4. **Skill Variations**: Different forms of the same skill
5. **Abbreviation Matches**: Full forms and abbreviations

EXAMPLES OF SMART MATCHING:
- "SQL" matches: "SQL", "sql", "Structured Query Language", "database queries"
- "Project Management" matches: "project management", "PM", "project coordination", "managed projects"
- "Communication" matches: "communication", "communicate", "verbal skills", "written communication"
- "Python" matches: "Python", "python", "Python programming", "Python development"
- "Data Analysis" matches: "data analysis", "analyzing data", "data analytics", "statistical analysis"

MATCHING GUIDELINES:
1. **Be Intelligent**: Look for semantic meaning, not just exact text
2. **Consider Context**: Keywords in relevant sections (experience, skills, education)
3. **Handle Variations**: Different tenses, forms, and expressions
4. **Be Thorough**: Check all sections of the CV for keyword presence
5. **Be Accurate**: Only mark as matched if the skill is genuinely present

OUTPUT FORMAT:
Respond with a JSON object only, no additional text:
{
    "matched_required_keywords": ["keyword1", "keyword2", ...],
    "matched_preferred_keywords": ["keyword1", "keyword2", ...],
    "missed_required_keywords": ["keyword1", "keyword2", ...],
    "missed_preferred_keywords": ["keyword1", "keyword2", ...],
    "match_counts": {
        "matched_required_count": number,
        "matched_preferred_count": number,
        "missed_required_count": number,
        "missed_preferred_count": number,
        "total_required_keywords": number,
        "total_preferred_keywords": number
    },
    "matching_notes": {
        "smart_matches_found": ["explanation of smart matches"],
        "context_analysis": "brief analysis of CV content relevance"
    }
}"""
        
        prompt = f"""Analyze the following CV content against the job description keywords and determine which keywords are present using intelligent matching.

JOB DESCRIPTION KEYWORDS TO MATCH:
Required Keywords: {required_keywords}
Preferred Keywords: {preferred_keywords}

CV CONTENT:
{cv_content}

INSTRUCTIONS:
1. Go through each required keyword and check if it exists in the CV (using smart matching)
2. Go through each preferred keyword and check if it exists in the CV (using smart matching)
3. Separate matched keywords from missed keywords
4. Provide accurate counts for all categories
5. Include notes about any smart matches or context analysis

Remember to use intelligent matching - look for semantic meaning, synonyms, variations, and context, not just exact text matches."""
        
        return await self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=3000
        )


# Global AI service instance
ai_service = AIServiceManager()
