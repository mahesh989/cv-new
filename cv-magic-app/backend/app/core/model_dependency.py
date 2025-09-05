"""
Model selection dependency for handling dynamic model switching via headers
"""

from fastapi import Header, HTTPException, status
from typing import Optional
from app.ai.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)


async def get_current_model(
    x_current_model: Optional[str] = Header(None, alias="X-Current-Model")
) -> str:
    """
    Get the current model from headers or use the default from AI service
    
    Args:
        x_current_model: Model ID from X-Current-Model header
        
    Returns:
        Current model ID to use for AI operations
    """
    if x_current_model:
        # Validate that the model exists and switch to it
        try:
            # Try to switch to the model specified in header
            success = ai_service.switch_model(x_current_model)
            if success:
                logger.info(f"🔄 Switched to model from header: {x_current_model}")
                return x_current_model
            else:
                logger.warning(f"⚠️ Failed to switch to header model {x_current_model}, using current")
        except Exception as e:
            logger.warning(f"⚠️ Error switching to header model {x_current_model}: {e}")
    
    # Fall back to current model from AI service
    current_status = ai_service.get_current_status()
    return current_status.get('current_model', 'gpt-3.5-turbo')


async def ensure_model_available(model_id: str) -> bool:
    """
    Ensure the specified model is available and switch to it if needed
    
    Args:
        model_id: Model ID to ensure is available
        
    Returns:
        True if model is available, False otherwise
    """
    try:
        success = ai_service.switch_model(model_id)
        if success:
            logger.info(f"✅ Model {model_id} is available and active")
            return True
        else:
            logger.warning(f"⚠️ Model {model_id} is not available")
            return False
    except Exception as e:
        logger.error(f"❌ Error ensuring model {model_id} is available: {e}")
        return False
