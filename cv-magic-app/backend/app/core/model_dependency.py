"""
Model selection dependency for handling dynamic model switching via headers
"""

from fastapi import Header, HTTPException, status, Request, Depends
from typing import Optional
import logging
from contextvars import ContextVar
from app.core.dependencies import get_current_user
from app.models.auth import UserData

logger = logging.getLogger(__name__)

# Context variable to store the model for the current request
request_model: ContextVar[Optional[str]] = ContextVar('request_model', default=None)


async def get_current_model(
    request: Request,
    current_user: UserData = Depends(get_current_user),
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
    
    logger.info(f"🔍 [MODEL_DEPENDENCY] Initializing model for user: {current_user.email}")
    logger.info(f"- Header model: {x_current_model}")
    logger.info(f"- User ID: {current_user.id}")
    
    model_to_use = None
    
    if x_current_model:
        try:
            from app.ai.ai_service import ai_service
            # Optional: allow header override after validating
            success = ai_service.switch_model(x_current_model)
            if success:
                logger.info(f"🔄 Switched to model from header: {x_current_model}")
                model_to_use = x_current_model
            else:
                logger.warning(f"⚠️ Failed to switch to header model {x_current_model}")
        except Exception as e:
            logger.warning(f"⚠️ Error switching to header model {x_current_model}: {e}")
    
    # If still not set, resolve from persisted user preference
    if not model_to_use:
        if not current_user or not getattr(current_user, "id", None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

        try:
            from app.database import SessionLocal
            from app.services.user_model_service import user_model_service
            from app.ai.ai_service import ai_service
            
            # Initialize AI providers for this user (will use cache if available)
            ai_service.initialize_for_user(current_user)
            logger.info(f"✅ [MODEL_DEPENDENCY] AI providers initialized for user {current_user.email}")
            
            db = SessionLocal()
            try:
                pref = user_model_service.get_user_model(db, str(current_user.id))
            finally:
                db.close()
            if pref:
                provider, model = pref
                logger.info(f"🔍 [MODEL_DEPENDENCY] Found saved preference: {provider}/{model}")
                
                # Check if provider is available
                if provider in ai_service._providers:
                    # Validate by switching in-memory so providers are aligned
                    ok = ai_service.switch_provider(provider, model)
                    if ok:
                        model_to_use = model
                        logger.info(f"✅ [MODEL_DEPENDENCY] Successfully restored user preference: {provider}/{model}")
                    else:
                        logger.warning(f"⚠️ [MODEL_DEPENDENCY] Failed to switch to saved preference: {provider}/{model}")
                else:
                    logger.warning(f"⚠️ [MODEL_DEPENDENCY] Saved provider {provider} not available, available providers: {list(ai_service._providers.keys())}")
            if not model_to_use:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No AI model selected or no valid API key configured. Please set provider and model via /ai/set-current-model and configure your API keys."
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error resolving user model preference: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to resolve AI model")
    
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
