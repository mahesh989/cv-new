"""
Enhanced analysis routes for CV-JD comparison
"""
import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..enhanced_database import enhanced_db
from ..models.enhanced import (
    AnalysisResponse, AnalysisListResponse, AnalysisResultResponse,
    SuccessResponse, ErrorResponse, AnalysisType
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analysis-enhanced", tags=["Analysis Enhanced"])


class AnalysisRequest(BaseModel):
    """Request model for CV-JD analysis"""
    cv_id: str = Field(..., description="CV ID to analyze")
    jd_id: str = Field(..., description="Job description ID to compare with")
    analysis_type: AnalysisType = Field(default=AnalysisType.SKILL_MATCH, description="Type of analysis")
    include_suggestions: bool = Field(default=True, description="Include improvement suggestions")



async def perform_cv_jd_analysis(analysis_id: str):
    """Background task to perform CV-JD analysis"""
    try:
        # Get analysis info
        analysis_info = enhanced_db.get_analysis(analysis_id)
        if not analysis_info:
            logger.error(f"Analysis not found: {analysis_id}")
            return
        
        # Get CV and JD content
        cv_content = enhanced_db.get_cv_content(analysis_info.cv_id)
        jd_content = enhanced_db.get_jd_content(analysis_info.jd_id)
        
        if not cv_content or not jd_content:
            logger.error(f"CV or JD content not available for analysis: {analysis_id}")
            return
        
        # Perform analysis based on type
        result = {}
        
        if analysis_info.analysis_type == AnalysisType.SKILL_MATCH:
            result = await analyze_skill_match(cv_content, jd_content)
        elif analysis_info.analysis_type == AnalysisType.EXPERIENCE_MATCH:
            result = await analyze_experience_match(cv_content, jd_content)
        elif analysis_info.analysis_type == AnalysisType.OVERALL_FIT:
            result = await analyze_overall_fit(cv_content, jd_content)
        
        if result:
            # Save analysis results
            enhanced_db.save_analysis_result(analysis_id, result)
            logger.info(f"Analysis completed successfully: {analysis_id}")
        else:
            logger.error(f"Analysis failed: {analysis_id}")
            
    except Exception as e:
        logger.error(f"Error performing analysis {analysis_id}: {str(e)}")


async def analyze_skill_match(cv_content: str, jd_content: str) -> dict:
    """Analyze skill matching between CV and JD"""
    try:
        # Extract skills from CV and JD
        from ..services.cv_processor import cv_processor
        from ..services.jd_extractor import jd_extractor
        
        # Get basic info from both
        cv_info = cv_processor.extract_basic_info(cv_content)
        jd_info = jd_extractor.extract_key_information(jd_content)
        
        # Simple skill matching (can be enhanced with AI/ML later)
        cv_skills = set()
        jd_skills = set()
        
        # Extract skills from CV content (simple keyword matching)
        cv_lower = cv_content.lower()
        jd_lower = jd_content.lower()
        
        # Common technical skills
        technical_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'express',
            'django', 'flask', 'fastapi', 'sql', 'mysql', 'postgresql', 'mongodb',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'linux', 'windows',
            'html', 'css', 'bootstrap', 'tailwind', 'sass', 'typescript', 'php',
            'c++', 'c#', 'go', 'rust', 'swift', 'kotlin', 'flutter', 'dart',
            'machine learning', 'ai', 'data science', 'pandas', 'numpy', 'tensorflow',
            'pytorch', 'scikit-learn', 'jupyter', 'anaconda', 'r', 'scala'
        ]
        
        # Common soft skills
        soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
            'creative', 'adaptable', 'organized', 'time management', 'project management',
            'collaboration', 'mentoring', 'presentation', 'writing', 'research'
        ]
        
        # Find skills in CV
        for skill in technical_skills + soft_skills:
            if skill in cv_lower:
                cv_skills.add(skill)
        
        # Find skills in JD
        for skill in technical_skills + soft_skills:
            if skill in jd_lower:
                jd_skills.add(skill)
        
        # Calculate match metrics
        matched_skills = cv_skills.intersection(jd_skills)
        missing_skills = jd_skills - cv_skills
        additional_skills = cv_skills - jd_skills
        
        match_percentage = (len(matched_skills) / len(jd_skills) * 100) if jd_skills else 0
        
        return {
            "analysis_type": "skill_match",
            "cv_skills": list(cv_skills),
            "jd_skills": list(jd_skills),
            "matched_skills": list(matched_skills),
            "missing_skills": list(missing_skills),
            "additional_skills": list(additional_skills),
            "match_percentage": round(match_percentage, 2),
            "total_cv_skills": len(cv_skills),
            "total_jd_skills": len(jd_skills),
            "matched_count": len(matched_skills),
            "suggestions": [
                f"Consider learning: {', '.join(list(missing_skills)[:5])}" if missing_skills else "Great skill match!",
                f"Highlight your {', '.join(list(matched_skills)[:3])} experience" if matched_skills else ""
            ],
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in skill match analysis: {str(e)}")
        return {}


async def analyze_experience_match(cv_content: str, jd_content: str) -> dict:
    """Analyze experience matching between CV and JD"""
    try:
        # Simple experience analysis
        cv_lower = cv_content.lower()
        jd_lower = jd_content.lower()
        
        # Look for experience indicators
        experience_keywords = [
            'years', 'experience', 'worked', 'developed', 'managed', 'led',
            'built', 'created', 'implemented', 'designed', 'architected',
            'senior', 'junior', 'intern', 'associate', 'lead', 'principal'
        ]
        
        cv_experience_indicators = sum(1 for keyword in experience_keywords if keyword in cv_lower)
        jd_experience_indicators = sum(1 for keyword in experience_keywords if keyword in jd_lower)
        
        # Simple scoring
        experience_match = min(cv_experience_indicators / max(jd_experience_indicators, 1), 1.0) * 100
        
        return {
            "analysis_type": "experience_match",
            "cv_experience_score": cv_experience_indicators,
            "jd_experience_requirements": jd_experience_indicators,
            "experience_match_percentage": round(experience_match, 2),
            "suggestions": [
                "Quantify your achievements with numbers and metrics",
                "Use action verbs to describe your experience",
                "Highlight relevant project outcomes"
            ],
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in experience match analysis: {str(e)}")
        return {}


async def analyze_overall_fit(cv_content: str, jd_content: str) -> dict:
    """Analyze overall fit between CV and JD"""
    try:
        # Combine skill and experience analysis
        skill_result = await analyze_skill_match(cv_content, jd_content)
        experience_result = await analyze_experience_match(cv_content, jd_content)
        
        if not skill_result or not experience_result:
            return {}
        
        # Calculate overall score
        skill_weight = 0.7
        experience_weight = 0.3
        
        overall_score = (
            skill_result['match_percentage'] * skill_weight +
            experience_result['experience_match_percentage'] * experience_weight
        )
        
        # Generate fit level
        if overall_score >= 80:
            fit_level = "Excellent"
        elif overall_score >= 60:
            fit_level = "Good"
        elif overall_score >= 40:
            fit_level = "Fair"
        else:
            fit_level = "Poor"
        
        return {
            "analysis_type": "overall_fit",
            "overall_score": round(overall_score, 2),
            "fit_level": fit_level,
            "skill_match": skill_result,
            "experience_match": experience_result,
            "recommendations": [
                f"Focus on improving {fit_level.lower()} match areas",
                "Tailor your CV to highlight relevant skills",
                "Consider additional training for missing skills"
            ],
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in overall fit analysis: {str(e)}")
        return {}


@router.post("/analyze", response_model=AnalysisResponse)
async def create_analysis(
    background_tasks: BackgroundTasks,
    request: AnalysisRequest
):
    """Create new CV-JD analysis"""
    
    try:
        # Validate CV and JD exist
        cv_info = enhanced_db.get_cv(request.cv_id)
        if not cv_info:
            raise HTTPException(status_code=404, detail="CV not found")
        
        jd_info = enhanced_db.get_jd(request.jd_id)
        if not jd_info:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Check if content is available
        cv_content = enhanced_db.get_cv_content(request.cv_id)
        jd_content = enhanced_db.get_jd_content(request.jd_id)
        
        if not cv_content:
            raise HTTPException(status_code=400, detail="CV content not available")
        if not jd_content:
            raise HTTPException(status_code=400, detail="Job description content not available")
        
        # Create analysis record
        analysis_response = enhanced_db.save_analysis(
            cv_id=request.cv_id,
            jd_id=request.jd_id,
            analysis_type=request.analysis_type
        )
        
        # Perform analysis in background
        background_tasks.add_task(perform_cv_jd_analysis, analysis_response.id)
        
        logger.info(f"Analysis created: {analysis_response.id}")
        
        return analysis_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating analysis: {str(e)}")


@router.get("/list", response_model=AnalysisListResponse)
async def list_analyses(page: int = 1, limit: int = 10):
    """List all analyses with pagination"""
    
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        analyses = enhanced_db.list_analyses(page=page, limit=limit)
        total = enhanced_db.count_analyses()
        
        return AnalysisListResponse(
            analyses=analyses,
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")


@router.get("/{analysis_id}", response_model=AnalysisResultResponse)
async def get_analysis_result(analysis_id: str):
    """Get analysis result by ID"""
    
    try:
        # Get analysis info
        analysis_info = enhanced_db.get_analysis(analysis_id)
        if not analysis_info:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get analysis result
        result = enhanced_db.get_analysis_result(analysis_id)
        if not result:
            # Check if analysis is still being processed
            if analysis_info.processing_status.value == 'pending':
                raise HTTPException(status_code=202, detail="Analysis is still being processed")
            else:
                raise HTTPException(status_code=404, detail="Analysis result not available")
        
        return AnalysisResultResponse(
            id=analysis_info.id,
            cv_id=analysis_info.cv_id,
            jd_id=analysis_info.jd_id,
            analysis_type=analysis_info.analysis_type,
            result=result,
            processing_status=analysis_info.processing_status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting analysis result: {str(e)}")


@router.delete("/{analysis_id}", response_model=SuccessResponse)
async def delete_analysis(analysis_id: str):
    """Delete analysis"""
    
    try:
        deleted = enhanced_db.delete_analysis(analysis_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        logger.info(f"Analysis deleted: {analysis_id}")
        return SuccessResponse(message="Analysis deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting analysis: {str(e)}")


@router.post("/{analysis_id}/reprocess", response_model=SuccessResponse)
async def reprocess_analysis(analysis_id: str, background_tasks: BackgroundTasks):
    """Reprocess analysis"""
    
    try:
        # Check if analysis exists
        analysis_info = enhanced_db.get_analysis(analysis_id)
        if not analysis_info:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Reprocess analysis in background
        background_tasks.add_task(perform_cv_jd_analysis, analysis_id)
        
        logger.info(f"Analysis reprocessing started: {analysis_id}")
        return SuccessResponse(message="Analysis reprocessing started")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reprocessing analysis: {str(e)}")


@router.get("/cv/{cv_id}/analyses")
async def get_cv_analyses(cv_id: str, page: int = 1, limit: int = 10):
    """Get all analyses for a specific CV"""
    
    try:
        # Check if CV exists
        cv_info = enhanced_db.get_cv(cv_id)
        if not cv_info:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Get analyses for this CV
        analyses = enhanced_db.list_analyses_by_cv(cv_id, page=page, limit=limit)
        total = enhanced_db.count_analyses_by_cv(cv_id)
        
        return {
            "cv_id": cv_id,
            "analyses": analyses,
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting CV analyses: {str(e)}")


@router.get("/jd/{jd_id}/analyses")
async def get_jd_analyses(jd_id: str, page: int = 1, limit: int = 10):
    """Get all analyses for a specific JD"""
    
    try:
        # Check if JD exists
        jd_info = enhanced_db.get_jd(jd_id)
        if not jd_info:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        # Get analyses for this JD
        analyses = enhanced_db.list_analyses_by_jd(jd_id, page=page, limit=limit)
        total = enhanced_db.count_analyses_by_jd(jd_id)
        
        return {
            "jd_id": jd_id,
            "analyses": analyses,
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting JD analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting JD analyses: {str(e)}")
