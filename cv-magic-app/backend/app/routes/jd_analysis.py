"""
Job Description Analysis Routes

API endpoints for job description analysis with caching and file saving functionality.
Designed for Flutter app integration.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.auth import verify_token
from app.services.jd_analysis import JDAnalyzer, JDAnalysisResult, analyze_and_save_company_jd, load_jd_analysis
from app.utils.timestamp_utils import TimestampUtils
from app.ai.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Job Description Analysis"])


class JDAnalysisRequest(BaseModel):
    """Request model for JD analysis"""
    company_name: str
    force_refresh: bool = False
    temperature: float = 0.0


class JDAnalysisResponse(BaseModel):
    """Response model for JD analysis"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/analyze-jd/{company_name}")
async def analyze_jd_endpoint(
    company_name: str,
    request: Request,
    force_refresh: bool = False,
    temperature: float = 0.0
):
    """
    Analyze job description for a company and save results
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
        force_refresh: Force re-analysis even if cached result exists
        temperature: AI temperature for consistency (0.0-1.0)
    
    Returns:
        JSON response with analysis results
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"🎯 JD Analysis request: Company={company_name}, ForceRefresh={force_refresh}")
        
        # Short-circuit: if jd_original and an existing jd_analysis are present, reuse without re-analysis
        if not force_refresh:
            base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
            company_dir = base_dir / company_name
            try:
                jd_original = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json") or (company_dir / "jd_original.json" if (company_dir / "jd_original.json").exists() else None)
                jd_analysis = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_analysis", "json") or (company_dir / "jd_analysis.json" if (company_dir / "jd_analysis.json").exists() else None)
                if jd_original and jd_analysis and jd_analysis.exists():
                    result = load_jd_analysis(company_name)
                    if result:
                        response_data = {
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
                            "from_cache": True,
                            "skill_summary": result.get_skill_summary()
                        }
                        metadata = {
                            "analysis_duration": "N/A",
                            "ai_service_status": ai_service.get_current_status(),
                            "saved_path": None,
                            "reused": True
                        }
                        return JSONResponse(content={
                            "success": True,
                            "message": f"Reused existing JD analysis for {company_name}",
                            "data": response_data,
                            "metadata": metadata
                        })
            except Exception:
                # If any error during guard, continue to normal flow
                pass

        # Perform analysis
        result = await analyze_and_save_company_jd(
            company_name=company_name,
            force_refresh=force_refresh,
            temperature=temperature
        )
        
        # Prepare Flutter-friendly response with categorization
        response_data = {
            "company_name": company_name,
            # Backward compatibility - flat keyword lists
            "required_keywords": result.required_keywords,
            "preferred_keywords": result.preferred_keywords,
            "all_keywords": result.all_keywords,
            "experience_years": result.experience_years,
            # Enhanced categorized structure
            "required_skills": result.required_skills,
            "preferred_skills": result.preferred_skills,
            # Metadata
            "analysis_timestamp": result.analysis_timestamp,
            "ai_model_used": result.ai_model_used,
            "processing_status": result.processing_status,
            "from_cache": not force_refresh and result.analysis_timestamp != datetime.now().isoformat(),
            # Skill summary for quick overview
            "skill_summary": result.get_skill_summary()
        }
        
        metadata = {
            "analysis_duration": "N/A",  # Could be calculated if needed
            "ai_service_status": ai_service.get_current_status(),
            "saved_path": result.metadata.get("saved_path") if hasattr(result, 'metadata') else None
        }
        
        return JSONResponse(content={
            "success": True,
            "message": f"Job description analysis completed for {company_name}",
            "data": response_data,
            "metadata": metadata
        })
        
    except FileNotFoundError as e:
        logger.error(f"❌ JD file not found for {company_name}: {e}")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": f"Job description file not found for company '{company_name}'. Please ensure jd_original.txt exists in the company directory.",
                "message": "File not found"
            }
        )
    except Exception as e:
        logger.error(f"❌ JD analysis failed for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.get("/jd-analysis/{company_name}")
async def get_jd_analysis(
    company_name: str,
    request: Request
):
    """
    Retrieve saved job description analysis results
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
    
    Returns:
        JSON response with saved analysis results
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"📂 Retrieving JD analysis for {company_name}")
        
        # Load saved analysis
        result = load_jd_analysis(company_name)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No analysis found for company '{company_name}'. Please run analysis first.",
                    "message": "Analysis not found"
                }
            )
        
        # Prepare Flutter-friendly response with categorization
        response_data = {
            "company_name": company_name,
            # Backward compatibility - flat keyword lists
            "required_keywords": result.required_keywords,
            "preferred_keywords": result.preferred_keywords,
            "all_keywords": result.all_keywords,
            "experience_years": result.experience_years,
            # Enhanced categorized structure
            "required_skills": result.required_skills,
            "preferred_skills": result.preferred_skills,
            # Metadata
            "analysis_timestamp": result.analysis_timestamp,
            "ai_model_used": result.ai_model_used,
            "processing_status": result.processing_status,
            # Skill summary for quick overview
            "skill_summary": result.get_skill_summary()
        }
        
        return JSONResponse(content={
            "success": True,
            "message": f"Analysis results retrieved for {company_name}",
            "data": response_data,
            "metadata": {
                "from_cache": True,
                "analysis_age": "N/A"  # Could calculate from timestamp if needed
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve JD analysis for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to retrieve analysis: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.get("/jd-analysis/{company_name}/keywords")
async def get_jd_keywords(
    company_name: str,
    request: Request,
    keyword_type: str = "all"  # "all", "required", "preferred"
):
    """
    Get just the keywords from saved analysis (for quick access)
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
        keyword_type: Type of keywords to return ("all", "required", "preferred")
    
    Returns:
        JSON response with keywords only
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"🔑 Retrieving {keyword_type} keywords for {company_name}")
        
        # Load saved analysis
        result = load_jd_analysis(company_name)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No analysis found for company '{company_name}'",
                    "message": "Analysis not found"
                }
            )
        
        # Select keywords based on type
        if keyword_type == "required":
            keywords = result.required_keywords
        elif keyword_type == "preferred":
            keywords = result.preferred_keywords
        else:  # "all"
            keywords = result.all_keywords
        
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved {keyword_type} keywords for {company_name}",
            "data": {
                "company_name": company_name,
                "keyword_type": keyword_type,
                "keywords": keywords,
                "count": len(keywords)
            },
            "metadata": {
                "analysis_timestamp": result.analysis_timestamp,
                "ai_model_used": result.ai_model_used
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve keywords for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to retrieve keywords: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.get("/jd-analysis/{company_name}/status")
async def get_jd_analysis_status(
    company_name: str,
    request: Request
):
    """
    Check if analysis exists and get basic status info
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
    
    Returns:
        JSON response with analysis status
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        # Check if analysis file exists
        base_path = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
        analysis_file = base_path / company_name / "jd_analysis.json"
        jd_file = base_path / company_name / "jd_original.txt"
        
        analysis_exists = analysis_file.exists()
        jd_file_exists = jd_file.exists()
        
        status_data = {
            "company_name": company_name,
            "analysis_exists": analysis_exists,
            "jd_file_exists": jd_file_exists,
            "can_analyze": jd_file_exists,
            "needs_analysis": jd_file_exists and not analysis_exists
        }
        
        if analysis_exists:
            try:
                result = load_jd_analysis(company_name)
                if result:
                    status_data.update({
                        "analysis_timestamp": result.analysis_timestamp,
                        "ai_model_used": result.ai_model_used,
                        "keyword_counts": {
                            "required": len(result.required_keywords),
                            "preferred": len(result.preferred_keywords),
                            "total": len(result.all_keywords)
                        }
                    })
            except Exception as e:
                logger.warning(f"Failed to load analysis details for {company_name}: {e}")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Status retrieved for {company_name}",
            "data": status_data
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get status for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to get status: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.delete("/jd-analysis/{company_name}")
async def delete_jd_analysis(
    company_name: str,
    request: Request
):
    """
    Delete saved analysis results
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
    
    Returns:
        JSON response confirming deletion
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"🗑️ Deleting JD analysis for {company_name}")
        
        # Delete analysis file
        base_path = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
        analysis_file = base_path / company_name / "jd_analysis.json"
        
        if analysis_file.exists():
            analysis_file.unlink()
            logger.info(f"✅ Deleted analysis file: {analysis_file}")
            
            return JSONResponse(content={
                "success": True,
                "message": f"Analysis deleted for {company_name}",
                "data": {
                    "company_name": company_name,
                    "deleted_file": str(analysis_file)
                }
            })
        else:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No analysis found for company '{company_name}'",
                    "message": "Analysis not found"
                }
            )
        
    except Exception as e:
        logger.error(f"❌ Failed to delete analysis for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to delete analysis: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.get("/jd-analysis/{company_name}/technical")
async def get_technical_skills(
    company_name: str,
    request: Request,
    required_only: bool = False
):
    """
    Get technical skills from saved analysis
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
        required_only: If true, only return required technical skills
    
    Returns:
        JSON response with technical skills
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"🔧 Retrieving technical skills for {company_name} (required_only={required_only})")
        
        # Load saved analysis
        result = load_jd_analysis(company_name)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No analysis found for company '{company_name}'",
                    "message": "Analysis not found"
                }
            )
        
        # Get technical skills
        technical_skills = result.get_technical_skills(required_only=required_only)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved technical skills for {company_name}",
            "data": {
                "company_name": company_name,
                "skill_type": "technical",
                "required_only": required_only,
                "skills": technical_skills,
                "count": len(technical_skills)
            },
            "metadata": {
                "analysis_timestamp": result.analysis_timestamp,
                "ai_model_used": result.ai_model_used
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve technical skills for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to retrieve technical skills: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.get("/jd-analysis/{company_name}/soft-skills")
async def get_soft_skills(
    company_name: str,
    request: Request,
    required_only: bool = False
):
    """
    Get soft skills from saved analysis
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
        required_only: If true, only return required soft skills
    
    Returns:
        JSON response with soft skills
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"🤝 Retrieving soft skills for {company_name} (required_only={required_only})")
        
        # Load saved analysis
        result = load_jd_analysis(company_name)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No analysis found for company '{company_name}'",
                    "message": "Analysis not found"
                }
            )
        
        # Get soft skills
        soft_skills = result.get_soft_skills(required_only=required_only)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved soft skills for {company_name}",
            "data": {
                "company_name": company_name,
                "skill_type": "soft_skills",
                "required_only": required_only,
                "skills": soft_skills,
                "count": len(soft_skills)
            },
            "metadata": {
                "analysis_timestamp": result.analysis_timestamp,
                "ai_model_used": result.ai_model_used
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve soft skills for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to retrieve soft skills: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.get("/jd-analysis/{company_name}/experience")
async def get_experience_requirements(
    company_name: str,
    request: Request,
    required_only: bool = False
):
    """
    Get experience requirements from saved analysis
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
        required_only: If true, only return required experience
    
    Returns:
        JSON response with experience requirements
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"📅 Retrieving experience requirements for {company_name} (required_only={required_only})")
        
        # Load saved analysis
        result = load_jd_analysis(company_name)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No analysis found for company '{company_name}'",
                    "message": "Analysis not found"
                }
            )
        
        # Get experience requirements
        experience = result.get_experience_requirements(required_only=required_only)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved experience requirements for {company_name}",
            "data": {
                "company_name": company_name,
                "skill_type": "experience",
                "required_only": required_only,
                "requirements": experience,
                "count": len(experience),
                "experience_years": result.experience_years
            },
            "metadata": {
                "analysis_timestamp": result.analysis_timestamp,
                "ai_model_used": result.ai_model_used
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve experience requirements for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to retrieve experience requirements: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.get("/jd-analysis/{company_name}/domain-knowledge")
async def get_domain_knowledge(
    company_name: str,
    request: Request,
    required_only: bool = False
):
    """
    Get domain knowledge from saved analysis
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
        required_only: If true, only return required domain knowledge
    
    Returns:
        JSON response with domain knowledge
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"🏢 Retrieving domain knowledge for {company_name} (required_only={required_only})")
        
        # Load saved analysis
        result = load_jd_analysis(company_name)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No analysis found for company '{company_name}'",
                    "message": "Analysis not found"
                }
            )
        
        # Get domain knowledge
        domain_knowledge = result.get_domain_knowledge(required_only=required_only)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved domain knowledge for {company_name}",
            "data": {
                "company_name": company_name,
                "skill_type": "domain_knowledge",
                "required_only": required_only,
                "knowledge": domain_knowledge,
                "count": len(domain_knowledge)
            },
            "metadata": {
                "analysis_timestamp": result.analysis_timestamp,
                "ai_model_used": result.ai_model_used
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve domain knowledge for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to retrieve domain knowledge: {str(e)}",
                "message": "Internal server error"
            }
        )


@router.get("/jd-analysis/{company_name}/categorized")
async def get_categorized_skills(
    company_name: str,
    request: Request
):
    """
    Get all categorized skills from saved analysis
    
    Args:
        company_name: Company name (e.g., "Australia_for_UNHCR")
    
    Returns:
        JSON response with all categorized skills
    """
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid token"}
            )
        
        logger.info(f"📊 Retrieving categorized skills for {company_name}")
        
        # Load saved analysis
        result = load_jd_analysis(company_name)
        
        if not result:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"No analysis found for company '{company_name}'",
                    "message": "Analysis not found"
                }
            )
        
        # Get all categorized skills
        categorized_skills = result.get_all_categorized_skills()
        skill_summary = result.get_skill_summary()
        
        return JSONResponse(content={
            "success": True,
            "message": f"Retrieved categorized skills for {company_name}",
            "data": {
                "company_name": company_name,
                "categorized_skills": categorized_skills,
                "skill_summary": skill_summary,
                "experience_years": result.experience_years
            },
            "metadata": {
                "analysis_timestamp": result.analysis_timestamp,
                "ai_model_used": result.ai_model_used
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve categorized skills for {company_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Failed to retrieve categorized skills: {str(e)}",
                "message": "Internal server error"
            }
        )
