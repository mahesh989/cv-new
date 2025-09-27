"""
User Feedback Routes for CV Management API
Phase 10: Post-Launch Optimization & Continuous Improvement
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_database
from app.models.auth import UserData
from app.core.dependencies import get_current_user
from app.services.post_launch_monitoring import get_post_launch_monitoring
from app.services.optimization_framework import get_optimization_framework
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """User feedback request model"""
    feedback_type: str = Field(..., description="Type of feedback (bug, feature, general, rating)")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: str = Field(..., min_length=10, max_length=1000, description="Feedback comment")
    category: Optional[str] = Field(None, description="Feedback category")
    priority: Optional[str] = Field("medium", description="Priority level")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class FeedbackResponse(BaseModel):
    """User feedback response model"""
    id: str
    feedback_type: str
    rating: int
    comment: str
    category: Optional[str]
    priority: str
    status: str
    created_at: datetime
    response: Optional[str] = None
    resolved_at: Optional[datetime] = None


class FeedbackAnalysis(BaseModel):
    """Feedback analysis response model"""
    total_feedback: int
    average_rating: float
    ratings_by_type: Dict[str, Dict[str, Any]]
    common_issues: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    trends: Dict[str, Any]


class OptimizationDashboard(BaseModel):
    """Optimization dashboard response model"""
    total_recommendations: int
    pending_recommendations: int
    implemented_recommendations: int
    failed_recommendations: int
    total_results: int
    successful_implementations: int
    average_improvement: float
    recommendations_by_type: Dict[str, int]
    recommendations_by_priority: Dict[str, int]
    recent_results: List[Dict[str, Any]]


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    current_user: UserData = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """
    Submit user feedback for analysis and improvement
    """
    try:
        # Collect feedback using monitoring service
        monitoring_service = get_post_launch_monitoring()
        feedback = monitoring_service.collect_user_feedback(
            user_id=int(current_user.id),
            feedback_type=request.feedback_type,
            rating=request.rating,
            comment=request.comment,
            metadata={
                "category": request.category,
                "priority": request.priority,
                "user_agent": getattr(request, 'user_agent', None),
                "ip_address": getattr(request, 'client_ip', None)
            }
        )
        
        # Create response
        response = FeedbackResponse(
            id=f"feedback_{int(datetime.now().timestamp())}",
            feedback_type=request.feedback_type,
            rating=request.rating,
            comment=request.comment,
            category=request.category,
            priority=request.priority,
            status="submitted",
            created_at=feedback.timestamp
        )
        
        logger.info(f"User {current_user.id} submitted feedback: {request.feedback_type}")
        return response
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
    current_user: UserData = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get feedback submitted by the current user
    """
    try:
        # Get user's feedback from monitoring service
        monitoring_service = get_post_launch_monitoring()
        user_feedback = [
            f for f in monitoring_service.user_feedback 
            if f.user_id == int(current_user.id)
        ]
        
        # Sort by timestamp (newest first)
        user_feedback.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        paginated_feedback = user_feedback[offset:offset + limit]
        
        # Convert to response format
        responses = []
        for feedback in paginated_feedback:
            response = FeedbackResponse(
                id=f"feedback_{int(feedback.timestamp.timestamp())}",
                feedback_type=feedback.feedback_type,
                rating=feedback.rating,
                comment=feedback.comment,
                category=feedback.metadata.get("category"),
                priority=feedback.metadata.get("priority", "medium"),
                status="submitted",
                created_at=feedback.timestamp
            )
            responses.append(response)
        
        return responses
        
    except Exception as e:
        logger.error(f"Error getting user feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user feedback"
        )


@router.get("/analysis", response_model=FeedbackAnalysis)
async def get_feedback_analysis(
    current_user: UserData = Depends(get_current_user)
):
    """
    Get comprehensive feedback analysis
    """
    try:
        # Get feedback analysis from monitoring service
        monitoring_service = get_post_launch_monitoring()
        analysis = monitoring_service.analyze_user_feedback()
        
        # Add trends analysis
        trends = _analyze_feedback_trends()
        
        response = FeedbackAnalysis(
            total_feedback=analysis.get("total_feedback", 0),
            average_rating=analysis.get("average_rating", 0.0),
            ratings_by_type=analysis.get("ratings_by_type", {}),
            common_issues=analysis.get("common_issues", []),
            recommendations=analysis.get("recommendations", []),
            trends=trends
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting feedback analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feedback analysis"
        )


@router.get("/optimization-dashboard", response_model=OptimizationDashboard)
async def get_optimization_dashboard(
    current_user: UserData = Depends(get_current_user)
):
    """
    Get optimization dashboard data
    """
    try:
        # Get dashboard data from optimization framework
        optimization_service = get_optimization_framework()
        dashboard_data = optimization_service.get_optimization_dashboard()
        
        response = OptimizationDashboard(
            total_recommendations=dashboard_data.get("total_recommendations", 0),
            pending_recommendations=dashboard_data.get("pending_recommendations", 0),
            implemented_recommendations=dashboard_data.get("implemented_recommendations", 0),
            failed_recommendations=dashboard_data.get("failed_recommendations", 0),
            total_results=dashboard_data.get("total_results", 0),
            successful_implementations=dashboard_data.get("successful_implementations", 0),
            average_improvement=dashboard_data.get("average_improvement", 0.0),
            recommendations_by_type=dashboard_data.get("recommendations_by_type", {}),
            recommendations_by_priority=dashboard_data.get("recommendations_by_priority", {}),
            recent_results=dashboard_data.get("recent_results", [])
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting optimization dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get optimization dashboard"
        )


@router.get("/recommendations")
async def get_optimization_recommendations(
    current_user: UserData = Depends(get_current_user),
    type_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    limit: int = 20
):
    """
    Get optimization recommendations
    """
    try:
        # Get recommendations from optimization framework
        optimization_service = get_optimization_framework()
        recommendations = optimization_service.recommendations
        
        # Apply filters
        if type_filter:
            recommendations = [r for r in recommendations if r.type.value == type_filter]
        
        if priority_filter:
            recommendations = [r for r in recommendations if r.priority.value == priority_filter]
        
        # Limit results
        recommendations = recommendations[:limit]
        
        # Format response
        response = []
        for rec in recommendations:
            response.append({
                "id": rec.id,
                "type": rec.type.value,
                "priority": rec.priority.value,
                "title": rec.title,
                "description": rec.description,
                "current_value": rec.current_value,
                "target_value": rec.target_value,
                "impact_score": rec.impact_score,
                "effort_score": rec.effort_score,
                "roi_score": rec.roi_score,
                "status": rec.status,
                "created_at": rec.created_at.isoformat(),
                "implementation_steps": rec.implementation_steps,
                "expected_improvement": rec.expected_improvement
            })
        
        return {"recommendations": response, "total": len(response)}
        
    except Exception as e:
        logger.error(f"Error getting optimization recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get optimization recommendations"
        )


@router.post("/implement-recommendation/{recommendation_id}")
async def implement_recommendation(
    recommendation_id: str,
    current_user: UserData = Depends(get_current_user)
):
    """
    Implement an optimization recommendation
    """
    try:
        # Implement recommendation using optimization framework
        optimization_service = get_optimization_framework()
        result = optimization_service.implement_recommendation(recommendation_id)
        
        response = {
            "recommendation_id": result.recommendation_id,
            "implemented_at": result.implemented_at.isoformat(),
            "before_value": result.before_value,
            "after_value": result.after_value,
            "improvement_percentage": result.improvement_percentage,
            "success": result.success,
            "notes": result.notes
        }
        
        logger.info(f"User {current_user.id} implemented recommendation {recommendation_id}")
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error implementing recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to implement recommendation"
        )


@router.get("/system-health")
async def get_system_health(
    current_user: UserData = Depends(get_current_user)
):
    """
    Get system health score and metrics
    """
    try:
        # Get system health from monitoring service
        monitoring_service = get_post_launch_monitoring()
        health_score = monitoring_service.get_system_health_score()
        
        return health_score
        
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system health"
        )


@router.get("/monitoring-summary")
async def get_monitoring_summary(
    current_user: UserData = Depends(get_current_user)
):
    """
    Get comprehensive monitoring summary
    """
    try:
        # Get monitoring summary from monitoring service
        monitoring_service = get_post_launch_monitoring()
        summary = monitoring_service.get_monitoring_summary()
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting monitoring summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get monitoring summary"
        )


def _analyze_feedback_trends() -> Dict[str, Any]:
    """Analyze feedback trends over time"""
    try:
        # Get feedback from monitoring service
        monitoring_service = get_post_launch_monitoring()
        feedback = monitoring_service.user_feedback
        
        if not feedback:
            return {"message": "No feedback data available for trend analysis"}
        
        # Group by time periods
        now = datetime.now(timezone.utc)
        last_7_days = [f for f in feedback if f.timestamp > now - timedelta(days=7)]
        last_30_days = [f for f in feedback if f.timestamp > now - timedelta(days=30)]
        
        # Calculate trends
        trends = {
            "feedback_volume": {
                "last_7_days": len(last_7_days),
                "last_30_days": len(last_30_days),
                "trend": "increasing" if len(last_7_days) > len(last_30_days) / 4 else "stable"
            },
            "rating_trends": {
                "last_7_days_avg": sum(f.rating for f in last_7_days) / len(last_7_days) if last_7_days else 0,
                "last_30_days_avg": sum(f.rating for f in last_30_days) / len(last_30_days) if last_30_days else 0
            },
            "feedback_types": {
                "bug_reports": len([f for f in feedback if f.feedback_type == "bug"]),
                "feature_requests": len([f for f in feedback if f.feedback_type == "feature"]),
                "general_feedback": len([f for f in feedback if f.feedback_type == "general"]),
                "ratings": len([f for f in feedback if f.feedback_type == "rating"])
            }
        }
        
        return trends
        
    except Exception as e:
        logger.error(f"Error analyzing feedback trends: {e}")
        return {"error": "Failed to analyze feedback trends"}
