"""
DeepSeek AI Model Configuration
===============================

This file contains DeepSeek model configurations used throughout the application.
Change the models here to update them everywhere at once.

Usage:
    from src.ai_config import AI_MODELS, get_model_config
    
    # Use default model for a specific task
    model = AI_MODELS['DEFAULT']
    
    # Get full configuration for a model
    config = get_model_config('ANALYSIS')
"""

import os
from typing import Dict, Any, Optional

# =============================================================================
# AI MODEL CONFIGURATIONS
# =============================================================================

# Available AI Models (DeepSeek Only)
AI_MODELS = {
    # DeepSeek Models
    'DEEPSEEK_CHAT': 'deepseek-chat',
    'DEEPSEEK_CODER': 'deepseek-coder', 
    'DEEPSEEK_REASONER': 'deepseek-reasoner',
    
    # Aliases for backward compatibility
    'DEFAULT': 'deepseek-chat',
    'ANALYSIS': 'deepseek-chat',
    'CREATIVE': 'deepseek-chat',
    'FAST': 'deepseek-chat',
}

# Model configurations for different tasks (DeepSeek Only)
MODEL_CONFIGS = {
    # Default model (used when no specific model is specified)
    'DEFAULT': {
        'model': AI_MODELS['DEEPSEEK_CHAT'],
        'max_tokens': 4000,
        'temperature': 0.3,
        'provider': 'deepseek'
    },
    
    # Analysis tasks (skill extraction, ATS scoring, etc.)
    'ANALYSIS': {
        'model': AI_MODELS['DEEPSEEK_CHAT'],
        'max_tokens': 2000,
        'temperature': 0.2,
        'provider': 'deepseek'
    },
    
    # Detailed analysis (comprehensive reports)
    'DETAILED_ANALYSIS': {
        'model': AI_MODELS['DEEPSEEK_CHAT'],
        'max_tokens': 3000,
        'temperature': 0.1,
        'provider': 'deepseek'
    },
    
    # Fast processing (quick responses)
    'FAST': {
        'model': AI_MODELS['DEEPSEEK_CHAT'],
        'max_tokens': 1000,
        'temperature': 0.1,
        'provider': 'deepseek'
    },
    
    # Creative tasks (recommendations, CV generation)
    'CREATIVE': {
        'model': AI_MODELS['DEEPSEEK_CHAT'],
        'max_tokens': 4000,
        'temperature': 0.3,
        'provider': 'deepseek'
    },
    
    # Fallback model (same as default since we only have DeepSeek)
    'FALLBACK': {
        'model': AI_MODELS['DEEPSEEK_CHAT'],
        'max_tokens': 2000,
        'temperature': 0.2,
        'provider': 'deepseek'
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_model_config(task: str = 'DEFAULT') -> Dict[str, Any]:
    """
    Get model configuration for a specific task.
    
    Args:
        task: Task type ('DEFAULT', 'ANALYSIS', 'DETAILED_ANALYSIS', 'FAST', 'CREATIVE', 'FALLBACK')
    
    Returns:
        Dictionary containing model configuration
    """
    return MODEL_CONFIGS.get(task, MODEL_CONFIGS['DEFAULT']).copy()

def get_model_name(task: str = 'DEFAULT') -> str:
    """
    Get model name for a specific task.
    
    Args:
        task: Task type
    
    Returns:
        Model name string
    """
    return get_model_config(task)['model']

def get_model_params(task: str = 'DEFAULT', **overrides) -> Dict[str, Any]:
    """
    Get model parameters for a specific task with optional overrides.
    
    Args:
        task: Task type
        **overrides: Parameter overrides (max_tokens, temperature, etc.)
    
    Returns:
        Dictionary containing model parameters
    """
    config = get_model_config(task)
    config.update(overrides)
    return config

def get_provider(task: str = 'DEFAULT') -> str:
    """
    Get provider name for a specific task.
    
    Args:
        task: Task type
    
    Returns:
        Provider name ('deepseek')
    """
    return 'deepseek'

# =============================================================================
# ENVIRONMENT-BASED OVERRIDES
# =============================================================================

def apply_environment_overrides():
    """
    Apply environment variable overrides to model configurations.
    This allows runtime configuration changes without code changes.
    """
    global MODEL_CONFIGS
    
    # Override default model via environment variable
    default_model = os.getenv('AI_DEFAULT_MODEL')
    if default_model:
        MODEL_CONFIGS['DEFAULT']['model'] = default_model
        print(f"🔧 [AI_CONFIG] Overriding default model to: {default_model}")
    
    # Override analysis model
    analysis_model = os.getenv('AI_ANALYSIS_MODEL')
    if analysis_model:
        MODEL_CONFIGS['ANALYSIS']['model'] = analysis_model
        print(f"🔧 [AI_CONFIG] Overriding analysis model to: {analysis_model}")
    
    # Override detailed analysis model
    detailed_model = os.getenv('AI_DETAILED_MODEL')
    if detailed_model:
        MODEL_CONFIGS['DETAILED_ANALYSIS']['model'] = detailed_model
        print(f"🔧 [AI_CONFIG] Overriding detailed analysis model to: {detailed_model}")
    
    # Override creative model
    creative_model = os.getenv('AI_CREATIVE_MODEL')
    if creative_model:
        MODEL_CONFIGS['CREATIVE']['model'] = creative_model
        print(f"🔧 [AI_CONFIG] Overriding creative model to: {creative_model}")

# Apply environment overrides on import
apply_environment_overrides()

# =============================================================================
# DYNAMIC MODEL STATE MANAGEMENT
# =============================================================================

class ModelStateManager:
    """
    Global state manager for DeepSeek models.
    This ensures that all API calls use the correct DeepSeek model.
    """
    
    def __init__(self):
        self._current_model = AI_MODELS['DEEPSEEK_CHAT']  # Default DeepSeek model
        self._current_task_config = 'DEFAULT'
        
    def set_model(self, model_name: str):
        """Set the current DeepSeek model for all AI operations."""
        # Validate if it's a known DeepSeek model
        if model_name in AI_MODELS.values() or 'deepseek' in model_name.lower():
            self._current_model = model_name
        else:
            print(f"⚠️ [MODEL_STATE] Warning: {model_name} is not a DeepSeek model, using default")
            self._current_model = AI_MODELS['DEEPSEEK_CHAT']
            
        # Update all task configurations to use this model
        for task in MODEL_CONFIGS:
            MODEL_CONFIGS[task]['model'] = self._current_model
            MODEL_CONFIGS[task]['provider'] = 'deepseek'
            
        print(f"🔄 [MODEL_STATE] Global model updated to: {self._current_model}")
        
    def get_current_model(self) -> str:
        """Get the currently selected model."""
        return self._current_model
        
    def get_provider_for_model(self, model: str) -> str:
        """Get the provider for a specific model (always DeepSeek)."""
        return 'deepseek'
            
    def get_current_provider(self) -> str:
        """Get the provider for the current model (always DeepSeek)."""
        return 'deepseek'

# Global model state manager
model_state = ModelStateManager()

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    print("🤖 AI Model Configuration")
    print("=" * 50)
    
    print("\n📋 Available Models:")
    for name, model in AI_MODELS.items():
        print(f"  {name}: {model}")
    
    print("\n⚙️ Task Configurations:")
    for task, config in MODEL_CONFIGS.items():
        print(f"  {task}: {config['model']} ({config['provider']})")
    
    print("\n🔧 Environment Variables (for runtime overrides):")
    print("  AI_DEFAULT_MODEL - Override default model")
    print("  AI_ANALYSIS_MODEL - Override analysis model")
    print("  AI_DETAILED_MODEL - Override detailed analysis model")
    print("  AI_CREATIVE_MODEL - Override creative model")
    
    print("\n💡 Usage Examples:")
    print("  from src.ai_config import get_model_name, get_model_params")
    print("  model = get_model_name('ANALYSIS')  # Get model name")
    print("  params = get_model_params('ANALYSIS', max_tokens=3000)  # Get params with override")
