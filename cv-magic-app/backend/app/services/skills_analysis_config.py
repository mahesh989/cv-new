"""
Skills Analysis Configuration Service

Manages dynamic configuration for skills analysis parameters
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SkillsAnalysisConfig:
    """Configuration for skills analysis parameters"""
    
    # AI Model Parameters
    temperature: float = 0.0
    max_tokens: int = 4000
    
    # Analysis Parameters
    use_structured_analysis: bool = True
    extract_explicit_skills: bool = True
    extract_implied_skills: bool = True
    include_domain_keywords: bool = True
    
    # Caching Parameters
    enable_caching: bool = True
    cache_duration_hours: int = 24
    
    # File Management
    save_analysis_results: bool = True
    auto_detect_company: bool = True
    
    # Logging Parameters
    enable_detailed_logging: bool = True
    log_raw_responses: bool = True
    
    # Performance Parameters
    timeout_seconds: int = 300
    max_retry_attempts: int = 3


class SkillsAnalysisConfigService:
    """Service for managing skills analysis configuration"""
    
    def __init__(self):
        self.default_config = SkillsAnalysisConfig()
        self.custom_configs: Dict[str, SkillsAnalysisConfig] = {}
    
    def get_config(self, config_name: Optional[str] = None) -> SkillsAnalysisConfig:
        """
        Get configuration for skills analysis
        
        Args:
            config_name: Optional custom configuration name
            
        Returns:
            SkillsAnalysisConfig instance
        """
        if config_name and config_name in self.custom_configs:
            logger.info(f"🔧 [CONFIG] Using custom config: {config_name}")
            return self.custom_configs[config_name]
        
        logger.info("🔧 [CONFIG] Using default configuration")
        return self.default_config
    
    def create_custom_config(
        self, 
        config_name: str, 
        **kwargs
    ) -> SkillsAnalysisConfig:
        """
        Create a custom configuration
        
        Args:
            config_name: Name for the custom configuration
            **kwargs: Configuration parameters to override
            
        Returns:
            Custom SkillsAnalysisConfig instance
        """
        # Start with default config
        custom_config = SkillsAnalysisConfig()
        
        # Apply custom parameters
        for key, value in kwargs.items():
            if hasattr(custom_config, key):
                setattr(custom_config, key, value)
                logger.info(f"🔧 [CONFIG] Set {key} = {value}")
            else:
                logger.warning(f"⚠️ [CONFIG] Unknown parameter: {key}")
        
        # Store custom config
        self.custom_configs[config_name] = custom_config
        logger.info(f"✅ [CONFIG] Created custom config: {config_name}")
        
        return custom_config
    
    def get_ai_parameters(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """Get AI model parameters from configuration"""
        config = self.get_config(config_name)
        return {
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "timeout_seconds": config.timeout_seconds,
            "max_retry_attempts": config.max_retry_attempts
        }
    
    def get_analysis_parameters(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """Get analysis parameters from configuration"""
        config = self.get_config(config_name)
        return {
            "use_structured_analysis": config.use_structured_analysis,
            "extract_explicit_skills": config.extract_explicit_skills,
            "extract_implied_skills": config.extract_implied_skills,
            "include_domain_keywords": config.include_domain_keywords
        }
    
    def get_caching_parameters(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """Get caching parameters from configuration"""
        config = self.get_config(config_name)
        return {
            "enable_caching": config.enable_caching,
            "cache_duration_hours": config.cache_duration_hours
        }
    
    def get_file_parameters(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """Get file management parameters from configuration"""
        config = self.get_config(config_name)
        return {
            "save_analysis_results": config.save_analysis_results,
            "auto_detect_company": config.auto_detect_company
        }
    
    def get_logging_parameters(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """Get logging parameters from configuration"""
        config = self.get_config(config_name)
        return {
            "enable_detailed_logging": config.enable_detailed_logging,
            "log_raw_responses": config.log_raw_responses
        }
    
    def list_configs(self) -> Dict[str, Any]:
        """List all available configurations"""
        configs = {
            "default": {
                "name": "default",
                "description": "Default configuration",
                "parameters": self._config_to_dict(self.default_config)
            }
        }
        
        for name, config in self.custom_configs.items():
            configs[name] = {
                "name": name,
                "description": f"Custom configuration: {name}",
                "parameters": self._config_to_dict(config)
            }
        
        return configs
    
    def _config_to_dict(self, config: SkillsAnalysisConfig) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "use_structured_analysis": config.use_structured_analysis,
            "extract_explicit_skills": config.extract_explicit_skills,
            "extract_implied_skills": config.extract_implied_skills,
            "include_domain_keywords": config.include_domain_keywords,
            "enable_caching": config.enable_caching,
            "cache_duration_hours": config.cache_duration_hours,
            "save_analysis_results": config.save_analysis_results,
            "auto_detect_company": config.auto_detect_company,
            "enable_detailed_logging": config.enable_detailed_logging,
            "log_raw_responses": config.log_raw_responses,
            "timeout_seconds": config.timeout_seconds,
            "max_retry_attempts": config.max_retry_attempts
        }
    
    def update_default_config(self, **kwargs) -> SkillsAnalysisConfig:
        """Update the default configuration"""
        for key, value in kwargs.items():
            if hasattr(self.default_config, key):
                setattr(self.default_config, key, value)
                logger.info(f"🔧 [CONFIG] Updated default {key} = {value}")
            else:
                logger.warning(f"⚠️ [CONFIG] Unknown parameter: {key}")
        
        return self.default_config


# Global instance
skills_analysis_config_service = SkillsAnalysisConfigService()

# Predefined configurations
def setup_predefined_configs():
    """Setup predefined configurations for different use cases"""
    
    # Fast analysis configuration
    skills_analysis_config_service.create_custom_config(
        "fast",
        temperature=0.0,
        max_tokens=2000,
        extract_implied_skills=False,
        enable_detailed_logging=False,
        timeout_seconds=120
    )
    
    # Detailed analysis configuration
    skills_analysis_config_service.create_custom_config(
        "detailed",
        temperature=0.0,
        max_tokens=6000,
        extract_explicit_skills=True,
        extract_implied_skills=True,
        include_domain_keywords=True,
        enable_detailed_logging=True,
        log_raw_responses=True,
        timeout_seconds=600
    )
    
    # Mobile optimized configuration
    skills_analysis_config_service.create_custom_config(
        "mobile",
        temperature=0.0,
        max_tokens=3000,
        save_analysis_results=False,
        enable_detailed_logging=False,
        timeout_seconds=180
    )
    
    logger.info("✅ [CONFIG] Predefined configurations setup complete")

# Initialize predefined configurations
setup_predefined_configs()
