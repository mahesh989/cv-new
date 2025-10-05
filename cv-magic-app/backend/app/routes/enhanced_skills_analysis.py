"""
Enhanced Skills Analysis Routes

Provides API endpoints for skill analysis with proper file selection and versioning.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional, List

from app.services.skill_extraction.enhanced_skill_extraction_service import enhanced_skill_extraction_service
# Optional legacy selector; endpoints guard when unavailable
try:
    from app.services.skill_analysis.skill_analysis_file_selector import skill_analysis_file_selector  # type: ignore
except Exception:  # pragma: no cover
    skill_analysis_file_selector = None  # type: ignore

router = APIRouter(prefix="/api/enhanced-skills", tags=["Enhanced Skills Analysis"])


@router.post("/analyze")
async def analyze_skills(
    cv_filename: str,
    jd_url: str,
    company: str,
    user_id: int = 1,
    is_rerun: bool = False,
    force_refresh: bool = False
) -> Dict:
    """
    Analyze CV and JD skills with version tracking
    
    Args:
        cv_filename: Name of the CV file
        jd_url: URL of the job description
        company: Company name for organization
        user_id: User ID (default: 1)
        is_rerun: Whether this is a rerun analysis
        force_refresh: Force fresh analysis bypassing cache
        
    Returns:
        Analysis results with file paths and metadata
    """
    try:
        result = await enhanced_skill_extraction_service.analyze_skills(
            cv_filename=cv_filename,
            jd_url=jd_url,
            company=company,
            user_id=user_id,
            is_rerun=is_rerun,
            force_refresh=force_refresh
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/versions/{company}")
async def list_analysis_versions(company: str) -> List[Dict]:
    """
    List available analysis versions for a company
    
    Args:
        company: Company name
        
    Returns:
        List of analysis versions with metadata
    """
    try:
        if not skill_analysis_file_selector:
            return []
        versions = skill_analysis_file_selector.list_available_versions(company)
        return versions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content/{company}")
async def get_analysis_content(
    company: str,
    is_rerun: bool = False
) -> Dict:
    """
    Get analysis content for a company
    
    Args:
        company: Company name
        is_rerun: Whether to get rerun analysis content
        
    Returns:
        Analysis content with metadata
    """
    try:
        if not skill_analysis_file_selector:
            raise HTTPException(status_code=404, detail="Analysis content not found (selector missing)")
        content = skill_analysis_file_selector.get_analysis_content(
            company=company,
            is_rerun=is_rerun
        )
        if not content["success"]:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis content not found for {company}"
            )
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{company}")
async def get_analysis_summary(
    company: str,
    is_rerun: bool = False
) -> Dict:
    """
    Get analysis summary for a company
    
    Args:
        company: Company name
        is_rerun: Whether to get rerun analysis summary
        
    Returns:
        Analysis summary with metadata
    """
    try:
        if not skill_analysis_file_selector:
            raise HTTPException(status_code=404, detail="Analysis files not found (selector missing)")
        files = skill_analysis_file_selector.get_analysis_files(
            company=company,
            is_rerun=is_rerun
        )
        
        if not files.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis files not found for {company}"
            )
        
        # Read summary file if exists
        summary = None
        if files.summary_path and files.summary_path.exists():
            with open(files.summary_path, 'r', encoding='utf-8') as f:
                summary = f.read()
        
        return {
            "success": True,
            "summary": summary,
            "context": files.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))