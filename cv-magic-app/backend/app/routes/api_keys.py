"""
API Key Management Routes

This module provides REST API endpoints for managing API keys
for all AI providers dynamically.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from app.services.api_key_manager import api_key_manager
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
async def set_initial_api_key(request: APIKeyRequest):
    """Set API key for initial setup (no auth required)"""
    return await _set_api_key_internal(request)


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
        
        # Validate the key
        is_valid, validation_message = user_api_key_manager.validate_api_key(
            current_user, request.provider, request.api_key
        )
        
        # Refresh AI providers to pick up the new API key
        try:
            from app.ai.ai_service import ai_service
            ai_service.refresh_providers()
            logger.info(f"🔄 Refreshed AI providers after setting {request.provider} API key for user {current_user.email}")
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


async def _set_api_key_internal(request: APIKeyRequest):
    """
    Set API key for a specific provider
    
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
        
        # Set the API key
        success = api_key_manager.set_api_key(request.provider, request.api_key)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to set API key for {request.provider}"
            )
        
        # Validate the key
        is_valid, validation_message = api_key_manager.validate_api_key(
            request.provider, request.api_key
        )
        
        # Refresh AI providers to pick up the new API key
        try:
            from app.ai.ai_service import ai_service
            ai_service.refresh_providers()
            logger.info(f"🔄 Refreshed AI providers after setting {request.provider} API key")
        except Exception as e:
            logger.warning(f"⚠️ Failed to refresh AI providers: {e}")
        
        return APIKeyResponse(
            success=True,
            message=f"API key set for {request.provider}. {validation_message}",
            provider=request.provider,
            is_valid=is_valid
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting API key for {request.provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


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


@router.get("/status-initial", response_model=AllProvidersStatusResponse)
async def get_providers_status_initial():
    """
    Get status of all AI providers for initial setup (no auth required)
    
    Returns:
        AllProvidersStatusResponse: Status of all providers
    """
    try:
        status_data = api_key_manager.get_provider_status()
        
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
            session_id=api_key_manager._session_id
        )
        
    except Exception as e:
        logger.error(f"Error getting providers status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


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
