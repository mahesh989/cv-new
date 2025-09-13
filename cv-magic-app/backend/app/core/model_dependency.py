"""
Model selection dependency for handling dynamic model switching via headers
"""

from fastapi import Header, HTTPException, status, Request
from typing import Optional
import logging
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Context variable to store the model for the current request
request_model: ContextVar[Optional[str]] = ContextVar('request_model', default=None)


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
    # Check if we already have a model set for this request
    existing_model = request_model.get()
    if existing_model:
        logger.debug(f"📌 Using existing request model: {existing_model}")
        return existing_model
    
    model_to_use = None
    
    if x_current_model:
        # Validate that the model exists and switch to it
        try:
            # Import ai_service lazily to avoid circular import
            from app.ai.ai_service import ai_service
            
            # Try to switch to the model specified in header
            success = ai_service.switch_model(x_current_model)
            if success:
                logger.info(f"🔄 Switched to model from header: {x_current_model}")
                model_to_use = x_current_model
            else:
                logger.warning(f"⚠️ Failed to switch to header model {x_current_model}, using current")
        except Exception as e:
            logger.warning(f"⚠️ Error switching to header model {x_current_model}: {e}")
    
    # Fall back to current model from AI service if not set
    if not model_to_use:
        # Import ai_service lazily to avoid circular import
        from app.ai.ai_service import ai_service
        current_status = ai_service.get_current_status()
        model_to_use = current_status.get('current_model', 'gpt-3.5-turbo')
    
    # Store the model in the request context
    request_model.set(model_to_use)
    
    return model_to_use


async def ensure_model_available(model_id: str) -> bool:
    """
    Ensure the specified model is available and switch to it if needed
    
    Args:
        model_id: Model ID to ensure is available
        
    Returns:
        True if model is available, False otherwise
    """
    try:
        # Import ai_service lazily to avoid circular import
        from app.ai.ai_service import ai_service
        
        success = ai_service.switch_model(model_id)
        if success:
            logger.info(f"✅ Model {model_id} is available and active")
            # Also update the context variable
            request_model.set(model_id)
            return True
        else:
            logger.warning(f"⚠️ Model {model_id} is not available")
            return False
    except Exception as e:
        logger.error(f"❌ Error ensuring model {model_id} is available: {e}")
        return False


def get_request_model() -> Optional[str]:
    """
    Get the current model set for this request
    
    Returns:
        The model ID if set, None otherwise
    """
    return request_model.get()
