"""
AI API Routes

This module provides FastAPI endpoints for AI operations including:
- Model switching and configuration
- AI analysis and completions
- Provider status and management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from app.ai.ai_service import ai_service
from app.core.dependencies import get_current_user
from app.models.auth import UserData
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Management"])


# Pydantic models for request/response
class ChatCompletionRequest(BaseModel):
    """Request model for chat completion"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    provider: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """Response model for chat completion"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = {}


class ProviderSwitchRequest(BaseModel):
    """Request model for switching providers"""
    provider: str
    model: Optional[str] = None


class ModelSwitchRequest(BaseModel):
    """Request model for switching models"""
    model: str


class CVAnalysisRequest(BaseModel):
    """Request model for CV analysis"""
    cv_text: str
    provider: Optional[str] = None


class JobComparisonRequest(BaseModel):
    """Request model for CV-Job comparison"""
    cv_text: str
    job_description: str
    provider: Optional[str] = None


# AI Status and Configuration Endpoints

@router.get("/status")
async def get_ai_status(current_user: UserData = Depends(get_current_user)):
    """
    Get current AI service status including available providers and models
    """
    try:
        current_status = ai_service.get_current_status()
        provider_status = ai_service.get_provider_status()
        available_models = ai_service.get_all_available_models()
        
        return {
            "current_status": current_status,
            "providers": provider_status,
            "available_models": available_models
        }
    except Exception as e:
        logger.error(f"Failed to get AI status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI status"
        )


@router.get("/providers")
async def get_providers(current_user: UserData = Depends(get_current_user)):
    """
    Get list of available AI providers
    """
    try:
        providers = ai_service.get_available_providers()
        provider_status = ai_service.get_provider_status()
        
        return {
            "available_providers": providers,
            "provider_details": provider_status
        }
    except Exception as e:
        logger.error(f"Failed to get providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve providers"
        )


@router.get("/models")
async def get_models(current_user: UserData = Depends(get_current_user)):
    """
    Get all available models grouped by provider
    """
    try:
        models = ai_service.get_all_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve models"
        )


@router.get("/current")
async def get_current_configuration(current_user: UserData = Depends(get_current_user)):
    """
    Get current provider and model configuration
    """
    try:
        current_status = ai_service.get_current_status()
        return current_status
    except Exception as e:
        logger.error(f"Failed to get current configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve current configuration"
        )


# AI Configuration Management Endpoints

@router.post("/switch-provider")
async def switch_provider(
    request: ProviderSwitchRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Switch to a different AI provider and optionally a specific model
    """
    try:
        success = ai_service.switch_provider(request.provider, request.model)
        
        if success:
            current_status = ai_service.get_current_status()
            return {
                "message": f"Successfully switched to {request.provider}",
                "current_status": current_status
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to switch to provider {request.provider}"
            )
    except Exception as e:
        logger.error(f"Failed to switch provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/switch-model")
async def switch_model(
    request: ModelSwitchRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Switch to a different model within the current provider
    """
    try:
        success = ai_service.switch_model(request.model)
        
        if success:
            current_status = ai_service.get_current_status()
            return {
                "message": f"Successfully switched to model {request.model}",
                "current_status": current_status
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to switch to model {request.model}"
            )
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# AI Generation Endpoints

@router.post("/chat", response_model=ChatCompletionResponse)
async def chat_completion(
    request: ChatCompletionRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Generate AI response using the current or specified provider
    """
    try:
        response = await ai_service.generate_response(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            provider_name=request.provider
        )
        
        return ChatCompletionResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            tokens_used=response.tokens_used,
            cost=response.cost,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}"
        )


# CV Analysis Endpoints

@router.post("/analyze-cv")
async def analyze_cv(
    request: CVAnalysisRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Analyze CV content to extract skills, experience, and other information
    """
    try:
        response = await ai_service.analyze_cv_content(request.cv_text)
        
        return {
            "analysis": response.content,
            "model_used": response.model,
            "provider_used": response.provider,
            "tokens_used": response.tokens_used,
            "cost": response.cost,
            "analyzed_at": "2025-01-01T00:00:00Z"  # You might want to add actual timestamp
        }
        
    except Exception as e:
        logger.error(f"CV analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV analysis failed: {str(e)}"
        )


@router.post("/compare-cv-job")
async def compare_cv_with_job(
    request: JobComparisonRequest,
    current_user: UserData = Depends(get_current_user)
):
    """
    Compare CV with job description to find matches and provide recommendations
    """
    try:
        response = await ai_service.compare_cv_with_job(
            request.cv_text, 
            request.job_description
        )
        
        return {
            "comparison": response.content,
            "model_used": response.model,
            "provider_used": response.provider,
            "tokens_used": response.tokens_used,
            "cost": response.cost,
            "compared_at": "2025-01-01T00:00:00Z"  # You might want to add actual timestamp
        }
        
    except Exception as e:
        logger.error(f"CV comparison failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV comparison failed: {str(e)}"
        )


# Health Check Endpoint

@router.get("/health")
async def ai_health_check():
    """
    Check AI service health without requiring authentication
    """
    try:
        available_providers = ai_service.get_available_providers()
        current_provider = ai_service.get_current_provider()
        
        return {
            "status": "healthy" if current_provider else "degraded",
            "available_providers_count": len(available_providers),
            "available_providers": available_providers,
            "current_provider_available": current_provider is not None
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
