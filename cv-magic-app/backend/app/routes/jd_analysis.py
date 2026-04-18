"""
Job Description Analysis Routes

API endpoints for job description analysis with caching and file saving.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.models.auth import UserData
from app.services.jd_analysis import JDAnalyzer, JDAnalysisResult, analyze_and_save_company_jd, load_jd_analysis
from app.utils.timestamp_utils import TimestampUtils
from app.utils.user_path_utils import get_user_base_path
from app.ai.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Job Description Analysis"])


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class JDAnalysisRequest(BaseModel):
    company_name: str
    force_refresh: bool = False
    temperature: float = 0.0


class JDAnalysisResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ── Helpers ──────────────────────────────────────────────────────────────────

def _not_found(company_name: str) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": f"No analysis found for company '{company_name}'. Please run analysis first.",
            "message": "Analysis not found",
        },
    )


def _error_response(msg: str) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": msg, "message": "Internal server error"},
    )


def _jd_payload(result: JDAnalysisResult, company_name: str) -> dict:
    """Build the standard JD analysis response payload."""
    return {
        "company_name": company_name,
        "required_keywords": result.required_keywords,
        "preferred_keywords": result.preferred_keywords,
        "all_keywords": result.all_keywords,
        "experience_years": result.experience_years,
        "required_skills": result.required_skills,
        "preferred_skills": result.preferred_skills,
        "analysis_timestamp": result.analysis_timestamp,
        "ai_model_used": result.ai_model_used,
        "processing_status": result.processing_status,
        "skill_summary": result.get_skill_summary(),
    }


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/analyze-jd/{company_name}")
async def analyze_jd_endpoint(
    company_name: str,
    force_refresh: bool = False,
    temperature: float = 0.0,
    current_user: UserData = Depends(get_current_user),
):
    """Analyze job description for a company and save results."""
    try:
        logger.info(f"JD Analysis request: company={company_name}, force_refresh={force_refresh}")

        # Short-circuit: reuse cached analysis when available and not forced
        if not force_refresh:
            base_dir = get_user_base_path(current_user.email)
            company_dir = base_dir / company_name
            try:
                jd_original = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json") \
                              or (company_dir / "jd_original.json" if (company_dir / "jd_original.json").exists() else None)
                jd_analysis = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_analysis", "json") \
                              or (company_dir / "jd_analysis.json" if (company_dir / "jd_analysis.json").exists() else None)
                if jd_original and jd_analysis and jd_analysis.exists():
                    cached = load_jd_analysis(company_name)
                    if cached:
                        return JSONResponse(content={
                            "success": True,
                            "message": f"Reused existing JD analysis for {company_name}",
                            "data": {**_jd_payload(cached, company_name), "from_cache": True},
                            "metadata": {"ai_service_status": ai_service.get_current_status(), "reused": True},
                        })
            except Exception:
                pass  # Fall through to fresh analysis

        result = await analyze_and_save_company_jd(
            company_name=company_name, force_refresh=force_refresh, temperature=temperature
        )
        return JSONResponse(content={
            "success": True,
            "message": f"Job description analysis completed for {company_name}",
            "data": {**_jd_payload(result, company_name), "from_cache": False},
            "metadata": {
                "ai_service_status": ai_service.get_current_status(),
                "saved_path": result.metadata.get("saved_path") if hasattr(result, "metadata") else None,
            },
        })

    except FileNotFoundError as e:
        logger.error(f"JD file not found for {company_name}: {e}")
        return JSONResponse(status_code=404, content={
            "success": False,
            "error": f"Job description file not found for '{company_name}'. Ensure jd_original.txt exists.",
            "message": "File not found",
        })
    except Exception as e:
        logger.error(f"JD analysis failed for {company_name}: {e}")
        return _error_response(f"Analysis failed: {e}")


@router.get("/jd-analysis/{company_name}")
async def get_jd_analysis(
    company_name: str,
    current_user: UserData = Depends(get_current_user),
):
    """Retrieve saved job description analysis results."""
    try:
        result = load_jd_analysis(company_name)
        if not result:
            return _not_found(company_name)
        return JSONResponse(content={
            "success": True,
            "message": f"Analysis results retrieved for {company_name}",
            "data": _jd_payload(result, company_name),
            "metadata": {"from_cache": True},
        })
    except Exception as e:
        logger.error(f"Failed to retrieve JD analysis for {company_name}: {e}")
        return _error_response(f"Failed to retrieve analysis: {e}")


@router.get("/jd-analysis/{company_name}/keywords")
async def get_jd_keywords(
    company_name: str,
    keyword_type: str = "all",
    current_user: UserData = Depends(get_current_user),
):
    """Get keywords from saved analysis ('all', 'required', or 'preferred')."""
    try:
        result = load_jd_analysis(company_name)
        if not result:
            return _not_found(company_name)

        keywords = (
            result.required_keywords if keyword_type == "required"
            else result.preferred_keywords if keyword_type == "preferred"
            else result.all_keywords
        )
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved {keyword_type} keywords for {company_name}",
            "data": {"company_name": company_name, "keyword_type": keyword_type, "keywords": keywords, "count": len(keywords)},
            "metadata": {"analysis_timestamp": result.analysis_timestamp, "ai_model_used": result.ai_model_used},
        })
    except Exception as e:
        logger.error(f"Failed to retrieve keywords for {company_name}: {e}")
        return _error_response(f"Failed to retrieve keywords: {e}")


@router.get("/jd-analysis/{company_name}/status")
async def get_jd_analysis_status(
    company_name: str,
    current_user: UserData = Depends(get_current_user),
):
    """Check if analysis exists and return basic status info."""
    try:
        base_path = get_user_base_path(current_user.email)
        company_dir = base_path / company_name
        analysis_file = company_dir / "jd_analysis.json"
        jd_file = company_dir / "jd_original.txt"

        status_data: Dict[str, Any] = {
            "company_name": company_name,
            "analysis_exists": analysis_file.exists(),
            "jd_file_exists": jd_file.exists(),
            "can_analyze": jd_file.exists(),
            "needs_analysis": jd_file.exists() and not analysis_file.exists(),
        }
        if analysis_file.exists():
            try:
                r = load_jd_analysis(company_name)
                if r:
                    status_data.update({
                        "analysis_timestamp": r.analysis_timestamp,
                        "ai_model_used": r.ai_model_used,
                        "keyword_counts": {
                            "required": len(r.required_keywords),
                            "preferred": len(r.preferred_keywords),
                            "total": len(r.all_keywords),
                        },
                    })
            except Exception as e:
                logger.warning(f"Failed to load analysis details for {company_name}: {e}")

        return JSONResponse(content={"success": True, "message": f"Status retrieved for {company_name}", "data": status_data})
    except Exception as e:
        logger.error(f"Failed to get status for {company_name}: {e}")
        return _error_response(f"Failed to get status: {e}")


@router.delete("/jd-analysis/{company_name}")
async def delete_jd_analysis(
    company_name: str,
    current_user: UserData = Depends(get_current_user),
):
    """Delete saved analysis results."""
    try:
        base_path = get_user_base_path(current_user.email)
        analysis_file = base_path / company_name / "jd_analysis.json"

        if not analysis_file.exists():
            return _not_found(company_name)

        analysis_file.unlink()
        logger.info(f"Deleted analysis file: {analysis_file}")
        return JSONResponse(content={
            "success": True,
            "message": f"Analysis deleted for {company_name}",
            "data": {"company_name": company_name, "deleted_file": str(analysis_file)},
        })
    except Exception as e:
        logger.error(f"Failed to delete analysis for {company_name}: {e}")
        return _error_response(f"Failed to delete analysis: {e}")


@router.get("/jd-analysis/{company_name}/technical")
async def get_technical_skills(
    company_name: str,
    required_only: bool = False,
    current_user: UserData = Depends(get_current_user),
):
    """Get technical skills from saved analysis."""
    try:
        result = load_jd_analysis(company_name)
        if not result:
            return _not_found(company_name)
        skills = result.get_technical_skills(required_only=required_only)
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved technical skills for {company_name}",
            "data": {"company_name": company_name, "skill_type": "technical", "required_only": required_only, "skills": skills, "count": len(skills)},
            "metadata": {"analysis_timestamp": result.analysis_timestamp, "ai_model_used": result.ai_model_used},
        })
    except Exception as e:
        logger.error(f"Failed to retrieve technical skills for {company_name}: {e}")
        return _error_response(f"Failed to retrieve technical skills: {e}")


@router.get("/jd-analysis/{company_name}/soft-skills")
async def get_soft_skills(
    company_name: str,
    required_only: bool = False,
    current_user: UserData = Depends(get_current_user),
):
    """Get soft skills from saved analysis."""
    try:
        result = load_jd_analysis(company_name)
        if not result:
            return _not_found(company_name)
        skills = result.get_soft_skills(required_only=required_only)
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved soft skills for {company_name}",
            "data": {"company_name": company_name, "skill_type": "soft_skills", "required_only": required_only, "skills": skills, "count": len(skills)},
            "metadata": {"analysis_timestamp": result.analysis_timestamp, "ai_model_used": result.ai_model_used},
        })
    except Exception as e:
        logger.error(f"Failed to retrieve soft skills for {company_name}: {e}")
        return _error_response(f"Failed to retrieve soft skills: {e}")


@router.get("/jd-analysis/{company_name}/experience")
async def get_experience_requirements(
    company_name: str,
    required_only: bool = False,
    current_user: UserData = Depends(get_current_user),
):
    """Get experience requirements from saved analysis."""
    try:
        result = load_jd_analysis(company_name)
        if not result:
            return _not_found(company_name)
        experience = result.get_experience_requirements(required_only=required_only)
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved experience requirements for {company_name}",
            "data": {
                "company_name": company_name, "skill_type": "experience", "required_only": required_only,
                "requirements": experience, "count": len(experience), "experience_years": result.experience_years,
            },
            "metadata": {"analysis_timestamp": result.analysis_timestamp, "ai_model_used": result.ai_model_used},
        })
    except Exception as e:
        logger.error(f"Failed to retrieve experience requirements for {company_name}: {e}")
        return _error_response(f"Failed to retrieve experience requirements: {e}")


@router.get("/jd-analysis/{company_name}/domain-knowledge")
async def get_domain_knowledge(
    company_name: str,
    required_only: bool = False,
    current_user: UserData = Depends(get_current_user),
):
    """Get domain knowledge from saved analysis."""
    try:
        result = load_jd_analysis(company_name)
        if not result:
            return _not_found(company_name)
        knowledge = result.get_domain_knowledge(required_only=required_only)
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved domain knowledge for {company_name}",
            "data": {"company_name": company_name, "skill_type": "domain_knowledge", "required_only": required_only, "knowledge": knowledge, "count": len(knowledge)},
            "metadata": {"analysis_timestamp": result.analysis_timestamp, "ai_model_used": result.ai_model_used},
        })
    except Exception as e:
        logger.error(f"Failed to retrieve domain knowledge for {company_name}: {e}")
        return _error_response(f"Failed to retrieve domain knowledge: {e}")


@router.get("/jd-analysis/{company_name}/categorized")
async def get_categorized_skills(
    company_name: str,
    current_user: UserData = Depends(get_current_user),
):
    """Get all categorized skills from saved analysis."""
    try:
        result = load_jd_analysis(company_name)
        if not result:
            return _not_found(company_name)
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved categorized skills for {company_name}",
            "data": {
                "company_name": company_name,
                "categorized_skills": result.get_all_categorized_skills(),
                "skill_summary": result.get_skill_summary(),
                "experience_years": result.experience_years,
            },
            "metadata": {"analysis_timestamp": result.analysis_timestamp, "ai_model_used": result.ai_model_used},
        })
    except Exception as e:
        logger.error(f"Failed to retrieve categorized skills for {company_name}: {e}")
        return _error_response(f"Failed to retrieve categorized skills: {e}")
