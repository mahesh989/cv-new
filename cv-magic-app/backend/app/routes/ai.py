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
from app.database import get_database
from sqlalchemy.orm import Session
from app.core.model_dependency import get_current_model
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
    logger.info(f"🔵 [AI_STATUS] Getting AI status for user: {current_user.email}")
    try:
        current_status = ai_service.get_current_status()
        provider_status = ai_service.get_provider_status()
        available_models = ai_service.get_all_available_models()
        
        logger.info(f"🔵 [AI_STATUS] Current status: {current_status}")
        logger.info(f"🔵 [AI_STATUS] Provider status: {provider_status}")
        logger.info(f"🔵 [AI_STATUS] Available models: {available_models}")
        
        return {
            "current_status": current_status,
            "providers": provider_status,
            "available_models": available_models
        }
    except Exception as e:
        logger.error(f"🔴 [AI_STATUS] Failed to get AI status: {e}")
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
    Get all available models grouped by provider with detailed information
    """
    try:
        models = ai_service.get_all_available_models()
        
        # Get detailed model information
        detailed_models = {}
        for provider_name, model_list in models.items():
            detailed_models[provider_name] = []
            for model_id in model_list:
                model_config = ai_service.config.get_model_config(provider_name, model_id)
                if model_config:
                    detailed_models[provider_name].append({
                        "id": model_id,
                        "name": model_config.name,
                        "description": model_config.description,
                        "max_tokens": model_config.max_tokens,
                        "input_cost_per_1k": model_config.input_cost_per_1k,
                        "output_cost_per_1k": model_config.output_cost_per_1k
                    })
        
        return {"models": detailed_models}
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


@router.post("/set-current-model")
async def set_current_model(
    request: ModelSwitchRequest,
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Persist per-user selected provider+model. The frontend should call this on login or when switching.
    """
    try:
        from app.services.user_model_service import user_model_service
        if not hasattr(request, "model") or not request.model:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model is required")
        if not hasattr(request, "provider"):
            # Try using current provider if not supplied
            current_provider = ai_service.config.get_current_provider()
            if not current_provider:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider is required")
            provider = current_provider
        else:
            provider = getattr(request, "provider") or ai_service.config.get_current_provider()
        if not provider:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider is required")

        # Validate by switching in-memory
        ok = ai_service.switch_provider(provider, request.model)
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid provider/model: {provider}/{request.model}")

        # Persist for the user
        user_model_service.set_user_model(db, str(current_user.id), provider, request.model)

        return {
            "message": "Current model set",
            "provider": provider,
            "model": request.model,
            "current_status": ai_service.get_current_status()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set current model: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# AI Generation Endpoints

@router.post("/chat", response_model=ChatCompletionResponse)
async def chat_completion(
    request: ChatCompletionRequest,
    current_user: UserData = Depends(get_current_user),
    current_model: str = Depends(get_current_model)
):
    """
    Generate AI response using the current or specified provider
    Automatically uses the model specified in X-Current-Model header
    """
    try:
        logger.info(f"🟢 [AI_CHAT] user={current_user.email} provider={ai_service.config.get_current_provider()} model={ai_service.get_current_model_name()}")
        response = await ai_service.generate_response(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            provider_name=request.provider,
            user=current_user
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
    current_user: UserData = Depends(get_current_user),
    current_model: str = Depends(get_current_model)
):
    """
    Analyze CV content to extract skills, experience, and other information
    """
    try:
        logger.info(f"🟢 [AI_ANALYZE_CV] user={current_user.email} provider={ai_service.config.get_current_provider()} model={ai_service.get_current_model_name()}")
        response = await ai_service.analyze_cv_content(request.cv_text, user=current_user)
        
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
    current_user: UserData = Depends(get_current_user),
    current_model: str = Depends(get_current_model)
):
    """
    Compare CV with job description to find matches and provide recommendations
    """
    try:
        logger.info(f"🟢 [AI_COMPARE_CV_JOB] user={current_user.email} provider={ai_service.config.get_current_provider()} model={ai_service.get_current_model_name()}")
        response = await ai_service.compare_cv_with_job(
            request.cv_text, 
            request.job_description,
            user=current_user
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
