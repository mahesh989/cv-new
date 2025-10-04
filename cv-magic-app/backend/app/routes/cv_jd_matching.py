"""
CV-JD Matching API Routes

This module provides FastAPI routes for CV-JD matching functionality.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from app.services.cv_jd_matching import (
    CVJDMatcher,
    CVJDMatchResult,
    match_and_save_cv_jd
)
from app.services.jd_analysis import load_jd_analysis
from app.core.auth import verify_token

logger = logging.getLogger(__name__)

# Create router
cv_jd_matching_router = APIRouter(prefix="/api/cv-jd-matching", tags=["CV-JD Matching"])

# Security
security = HTTPBearer()

@cv_jd_matching_router.post("/match/{company_name}")
async def match_cv_against_jd(
    company_name: str,
    force_refresh: bool = False,
    cv_file_path: Optional[str] = None,
    temperature: float = 0.0,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Match CV content against job description keywords for a specific company
    
    Args:
        company_name: Company name for the analysis
        force_refresh: Whether to force refresh the analysis
        cv_file_path: Optional custom CV file path
        temperature: AI temperature for consistency
        credentials: Authentication credentials
        
    Returns:
        Dictionary containing matching results
    """
    try:
        # Verify authentication
        verify_token(credentials.credentials)
        
        logger.info(f"🔍 Starting CV-JD matching for company: {company_name}")
        
        # Perform CV-JD matching
        result = await match_and_save_cv_jd(
            company_name=company_name,
            cv_file_path=cv_file_path,
            force_refresh=force_refresh,
            temperature=temperature
        )
        
        # Convert to dictionary and add metadata
        result_data = result.to_dict()
        result_data['from_cache'] = not force_refresh
        
        logger.info(f"✅ CV-JD matching completed for {company_name}")
        
        return {
            "success": True,
            "message": "CV-JD matching completed successfully",
            "data": result_data
        }
        
    except FileNotFoundError as e:
        logger.error(f"File not found for CV-JD matching: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Required file not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"CV-JD matching failed for {company_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CV-JD matching failed: {str(e)}"
        )

@cv_jd_matching_router.get("/results/{company_name}")
async def get_cv_jd_match_results(
    company_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get saved CV-JD matching results for a specific company
    
    Args:
        company_name: Company name for the results
        credentials: Authentication credentials
        
    Returns:
        Dictionary containing saved matching results
    """
    try:
        # Verify authentication
        verify_token(credentials.credentials)
        
        logger.info(f"📂 Loading CV-JD match results for company: {company_name}")
        
        # Load existing results
        matcher = CVJDMatcher()
        result = matcher._load_match_result(company_name)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No CV-JD match results found for company: {company_name}"
            )
        
        # Convert to dictionary
        result_data = result.to_dict()
        result_data['from_cache'] = True
        
        logger.info(f"✅ CV-JD match results loaded for {company_name}")
        
        return {
            "success": True,
            "message": "CV-JD match results loaded successfully",
            "data": result_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load CV-JD match results for {company_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load CV-JD match results: {str(e)}"
        )

@cv_jd_matching_router.get("/status/{company_name}")
async def get_cv_jd_matching_status(
    company_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get CV-JD matching status for a specific company
    
    Args:
        company_name: Company name to check
        credentials: Authentication credentials
        
    Returns:
        Dictionary containing matching status information
    """
    try:
        # Verify authentication
        verify_token(credentials.credentials)
        
        logger.info(f"📊 Checking CV-JD matching status for company: {company_name}")
        
        # Check file existence
        # Use correct base path with user directory
        from app.utils.user_path_utils import get_user_base_path
        # This route requires authentication - user_email should be provided
        if not user_email:
            raise ValueError("User authentication required for CV-JD matching")
        base_path = get_user_base_path(user_email)
        company_dir = base_path / "applied_companies" / company_name
        
        # Check CV file using dynamic selection
        from app.services.dynamic_cv_selector import dynamic_cv_selector
        latest_cv_paths = dynamic_cv_selector.get_latest_cv_paths_for_services()
        cv_file_path = Path(latest_cv_paths['txt_path']) if latest_cv_paths['txt_path'] else None
        cv_file_exists = cv_file_path and cv_file_path.exists()
        
        logger.info(f"📄 [CV_JD_MATCHING] Using dynamic CV from {latest_cv_paths['txt_source']} folder")
        
        # Check JD analysis file
        jd_analysis_file = company_dir / "jd_analysis.json"
        jd_analysis_exists = jd_analysis_file.exists()
        
        # Check CV-JD match results file
        match_results_file = company_dir / "cv_jd_match_results.json"
        match_results_exists = match_results_file.exists()
        
        # Determine if matching can be performed
        can_match = cv_file_exists and jd_analysis_exists
        needs_matching = can_match and not match_results_exists
        
        # Get file timestamps if they exist
        cv_file_timestamp = None
        jd_analysis_timestamp = None
        match_results_timestamp = None
        
        if cv_file_exists:
            cv_file_timestamp = cv_file_path.stat().st_mtime
        
        if jd_analysis_exists:
            jd_analysis_timestamp = jd_analysis_file.stat().st_mtime
        
        if match_results_exists:
            match_results_timestamp = match_results_file.stat().st_mtime
        
        status_data = {
            "company_name": company_name,
            "cv_file_exists": cv_file_exists,
            "jd_analysis_exists": jd_analysis_exists,
            "match_results_exists": match_results_exists,
            "can_match": can_match,
            "needs_matching": needs_matching,
            "cv_file_path": str(cv_file_path) if cv_file_exists else None,
            "jd_analysis_file_path": str(jd_analysis_file) if jd_analysis_exists else None,
            "match_results_file_path": str(match_results_file) if match_results_exists else None,
            "cv_file_timestamp": cv_file_timestamp,
            "jd_analysis_timestamp": jd_analysis_timestamp,
            "match_results_timestamp": match_results_timestamp
        }
        
        logger.info(f"✅ CV-JD matching status checked for {company_name}")
        
        return {
            "success": True,
            "message": "CV-JD matching status retrieved successfully",
            "data": status_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get CV-JD matching status for {company_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get CV-JD matching status: {str(e)}"
        )

@cv_jd_matching_router.get("/match-percentage/{company_name}")
async def get_match_percentage(
    company_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get match percentage summary for a specific company
    
    Args:
        company_name: Company name for the analysis
        credentials: Authentication credentials
        
    Returns:
        Dictionary containing match percentage data
    """
    try:
        # Verify authentication
        verify_token(credentials.credentials)
        
        logger.info(f"📊 Getting match percentage for company: {company_name}")
        
        # Load existing results
        matcher = CVJDMatcher()
        result = matcher._load_match_result(company_name)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No CV-JD match results found for company: {company_name}"
            )
        
        # Get match percentages
        percentages = result.get_match_percentage()
        
        # Get match counts
        match_counts = result.match_counts
        
        percentage_data = {
            "company_name": company_name,
            "match_percentages": percentages,
            "match_counts": match_counts,
            "matched_required_keywords": result.matched_required_keywords,
            "matched_preferred_keywords": result.matched_preferred_keywords,
            "missed_required_keywords": result.missed_required_keywords,
            "missed_preferred_keywords": result.missed_preferred_keywords,
            "analysis_timestamp": result.analysis_timestamp
        }
        
        logger.info(f"✅ Match percentage retrieved for {company_name}")
        
        return {
            "success": True,
            "message": "Match percentage retrieved successfully",
            "data": percentage_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get match percentage for {company_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match percentage: {str(e)}"
        )

@cv_jd_matching_router.delete("/results/{company_name}")
async def delete_cv_jd_match_results(
    company_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Delete CV-JD matching results for a specific company
    
    Args:
        company_name: Company name for the results to delete
        credentials: Authentication credentials
        
    Returns:
        Dictionary containing deletion confirmation
    """
    try:
        # Verify authentication
        verify_token(credentials.credentials)
        
        logger.info(f"🗑️ Deleting CV-JD match results for company: {company_name}")
        
        # Delete results file
        from app.utils.user_path_utils import get_user_base_path
        # This route requires authentication - user_email should be provided
        if not user_email:
            raise ValueError("User authentication required for CV-JD matching results")
        base_path = get_user_base_path(user_email)
        match_results_file = base_path / "applied_companies" / company_name / "cv_jd_match_results.json"
        
        if match_results_file.exists():
            match_results_file.unlink()
            logger.info(f"✅ CV-JD match results deleted for {company_name}")
            
            return {
                "success": True,
                "message": f"CV-JD match results deleted successfully for {company_name}",
                "data": {
                    "company_name": company_name,
                    "deleted_file": str(match_results_file)
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No CV-JD match results found for company: {company_name}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete CV-JD match results for {company_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete CV-JD match results: {str(e)}"
        )
