"""
API Key Management Routes

This module provides REST API endpoints for managing API keys
for all AI providers dynamically.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from app.services.user_api_key_manager import user_api_key_manager
from app.core.dependencies import get_current_user
from app.models.auth import UserData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/api-keys", tags=["API Keys"])


class APIKeyRequest(BaseModel):
    """Request model for setting API key"""
    provider: str = Field(..., description="AI provider (openai, anthropic, deepseek)")
    api_key: str = Field(..., description="API key for the provider")


class APIKeyResponse(BaseModel):
    """Response model for API key operations"""
    success: bool
    message: str
    provider: Optional[str] = None
    is_valid: Optional[bool] = None


class ProviderStatusResponse(BaseModel):
    """Response model for provider status"""
    provider: str
    has_api_key: bool
    is_valid: bool
    last_validated: Optional[str] = None
    created_at: Optional[str] = None


class AllProvidersStatusResponse(BaseModel):
    """Response model for all providers status"""
    providers: Dict[str, ProviderStatusResponse]
    session_id: str


@router.post("/set", response_model=APIKeyResponse)
async def set_api_key(
    request: APIKeyRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Set API key for authenticated users"""
    return await _set_user_api_key_internal(request, current_user)


@router.post("/set-initial", response_model=APIKeyResponse)
async def set_initial_api_key(
    request: APIKeyRequest,
    current_user: UserData = Depends(get_current_user)
):
    """Set initial API key for a user - requires authentication"""
    return await _set_user_api_key_internal(request, current_user)


async def _set_user_api_key_internal(request: APIKeyRequest, current_user: UserData):
    """
    Set API key for a specific user and provider
    
    Args:
        request: API key request data
        current_user: Current authenticated user
        
    Returns:
        APIKeyResponse: Result of the operation
    """
    try:
        # Validate provider
        valid_providers = ['openai', 'anthropic', 'deepseek']
        if request.provider not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
            )
        
        # Set the API key using user-specific manager
        success, message = user_api_key_manager.set_api_key(
            current_user, request.provider, request.api_key
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        # Clear AI service cache for this user since API key changed
        try:
            from app.ai.ai_service import ai_service
            ai_service.clear_user_cache(current_user.email)
            logger.info(f"🗑️ [API_KEYS] Cleared AI service cache for user {current_user.email}")
        except Exception as e:
            logger.warning(f"⚠️ [API_KEYS] Failed to clear AI service cache: {e}")
        
        # Validate the key
        is_valid, validation_message = user_api_key_manager.validate_api_key(
            current_user, request.provider, request.api_key
        )
        
        # Refresh AI providers to pick up the new API key
        try:
            from app.ai.ai_service import ai_service
            ai_service.refresh_providers(current_user)
            logger.info(f"🔄 Refreshed AI providers after setting {request.provider} API key for user {current_user.email}")
            
            # Auto-set default model preference if user doesn't have one
            try:
                from app.database import SessionLocal
                from app.services.user_model_service import user_model_service
                
                db = SessionLocal()
                try:
                    existing_pref = user_model_service.get_user_model(db, str(current_user.id))
                    if not existing_pref:
                        # User doesn't have a model preference, set default for this provider
                        default_models = {
                            "openai": "gpt-3.5-turbo",
                            "anthropic": "claude-3-haiku-20240307", 
                            "deepseek": "deepseek-chat"
                        }
                        default_model = default_models.get(request.provider, "gpt-3.5-turbo")
                        
                        # Set the default model preference
                        user_model_service.set_user_model(db, str(current_user.id), request.provider, default_model)
                        logger.info(f"🎯 [API_KEYS] Auto-set default model preference: {request.provider}/{default_model} for user {current_user.email}")
                    else:
                        logger.info(f"ℹ️ [API_KEYS] User {current_user.email} already has model preference: {existing_pref[0]}/{existing_pref[1]}")
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"⚠️ [API_KEYS] Failed to set default model preference: {e}")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to refresh AI providers: {e}")
        
        return APIKeyResponse(
            success=True,
            message=f"{message}. {validation_message}",
            provider=request.provider,
            is_valid=is_valid
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting API key for user {current_user.email} and provider {request.provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Removed global API key management - only user-specific keys are supported


@router.post("/validate/{provider}", response_model=APIKeyResponse)
async def validate_api_key(
    provider: str,
    current_user: UserData = Depends(get_current_user)
):
    """
    Validate API key for a specific provider and user
    
    Args:
        provider: AI provider name
        current_user: Current authenticated user
        
    Returns:
        APIKeyResponse: Validation result
    """
    try:
        # Validate provider
        valid_providers = ['openai', 'anthropic', 'deepseek']
        if provider not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
            )
        
        # Check if API key exists for this user
        if not user_api_key_manager.has_api_key(current_user, provider):
            return APIKeyResponse(
                success=False,
                message=f"No API key found for {provider}",
                provider=provider,
                is_valid=False
            )
        
        # Validate the key
        is_valid, message = user_api_key_manager.validate_api_key(current_user, provider)
        
        return APIKeyResponse(
            success=True,
            message=message,
            provider=provider,
            is_valid=is_valid
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating API key for user {current_user.email} and provider {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/status", response_model=AllProvidersStatusResponse)
async def get_providers_status(
    current_user: UserData = Depends(get_current_user)
):
    """
    Get status of all AI providers for the current user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        AllProvidersStatusResponse: Status of all providers
    """
    try:
        status_data = user_api_key_manager.get_provider_status(current_user)
        
        providers = {}
        for provider, data in status_data.items():
            providers[provider] = ProviderStatusResponse(
                provider=provider,
                has_api_key=data['has_api_key'],
                is_valid=data['is_valid'],
                last_validated=data['last_validated'],
                created_at=data['created_at']
            )
        
        return AllProvidersStatusResponse(
            providers=providers,
            session_id=f"user_{current_user.id}"
        )
        
    except Exception as e:
        logger.error(f"Error getting providers status for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Removed status-initial route - global API key management no longer supported


@router.delete("/{provider}", response_model=APIKeyResponse)
async def remove_api_key(
    provider: str,
    current_user: UserData = Depends(get_current_user)
):
    """
    Remove API key for a specific provider and user
    
    Args:
        provider: AI provider name
        current_user: Current authenticated user
        
    Returns:
        APIKeyResponse: Result of the operation
    """
    try:
        # Validate provider
        valid_providers = ['openai', 'anthropic', 'deepseek']
        if provider not in valid_providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
            )
        
        # Remove the API key using user-specific manager
        success, message = user_api_key_manager.remove_api_key(current_user, provider)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        return APIKeyResponse(
            success=True,
            message=message,
            provider=provider,
            is_valid=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing API key for user {current_user.email} and provider {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/", response_model=APIKeyResponse)
async def clear_all_api_keys(
    current_user: UserData = Depends(get_current_user)
):
    """
    Clear all API keys for the current user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        APIKeyResponse: Result of the operation
    """
    try:
        success, message = user_api_key_manager.clear_all_keys(current_user)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=message
            )
        
        return APIKeyResponse(
            success=True,
            message=message,
            provider=None,
            is_valid=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing all API keys for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
