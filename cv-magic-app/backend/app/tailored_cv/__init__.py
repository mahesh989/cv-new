"""
Tailored CV Module

A comprehensive CV tailoring system that optimizes CVs based on job recommendations
and the CV optimization framework using AI-powered enhancement.

Features:
- CV structure validation and optimization
- Job recommendation integration
- AI-powered content enhancement using Impact Statement Formula
- ATS score optimization
- Company-specific tailoring
- Batch processing capabilities

Usage:
    from app.tailored_cv.services.cv_tailoring_service import cv_tailoring_service
    from app.tailored_cv.models.cv_models import CVTailoringRequest
    
    request = CVTailoringRequest(
        original_cv=original_cv_data,
        recommendations=recommendation_analysis
    )
    
    response = await cv_tailoring_service.tailor_cv(request)
"""

from .models.cv_models import (
    OriginalCV,
    TailoredCV,
    RecommendationAnalysis,
    CVTailoringRequest,
    CVTailoringResponse
)

from .services.cv_tailoring_service import CVTailoringService
from .routes.cv_tailoring_routes import router

__all__ = [
    "OriginalCV",
    "TailoredCV", 
    "RecommendationAnalysis",
    "CVTailoringRequest",
    "CVTailoringResponse",
    "CVTailoringService",
    "router"
]