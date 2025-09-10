"""
Skills Analysis Routes

Extracted from main.py to provide better organization and maintainability
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.auth import verify_token
from app.core.model_dependency import get_current_model
from app.services.skill_extraction import skill_extraction_service
from app.services.cv_content_service import cv_content_service
from app.services.skills_analysis_config import skills_analysis_config_service
from app.services.skill_extraction.prompt_templates import get_prompt as get_skill_prompt
from app.services.skill_extraction.response_parser import SkillExtractionParser
from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
from app.ai.ai_service import ai_service
from app.services.jd_analysis import analyze_and_save_company_jd
from app.services.cv_jd_matching import match_and_save_cv_jd
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Skills Analysis"])


def _detect_most_recent_company() -> Optional[str]:
    """Detect the most recent company folder in cv-analysis with a job_info_*.json or jd_original.txt.

    Returns the company folder name or None if not found.
    """
    try:
        base_path = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
        if not base_path.exists():
            return None

        candidates = []
        for d in base_path.iterdir():
            if d.is_dir() and d.name != "Unknown_Company":
                if list(d.glob("job_info_*.json")) or (d / "jd_original.txt").exists():
                    candidates.append(d)

        if not candidates:
            return None

        most_recent = max(candidates, key=lambda p: p.stat().st_mtime)
        return most_recent.name
    except Exception:
        return None


def _schedule_post_skill_pipeline(company_name: Optional[str]):
    """Fire-and-forget JD analysis and CV–JD match pipeline for the given company."""
    if not company_name:
        logger.warning("⚠️ [PIPELINE] No company detected; skipping JD analysis & CV–JD matching.")
        return

    logger.info(f"🚀 [PIPELINE] Scheduling JD analysis and CV–JD matching for '{company_name}'...")

    async def _run_pipeline(cname: str):
        try:
            logger.info(f"🔧 [PIPELINE] Starting JD analysis for {cname}")
            await analyze_and_save_company_jd(cname, force_refresh=False)
            logger.info(f"✅ [PIPELINE] JD analysis saved for {cname}")

            logger.info(f"🔧 [PIPELINE] Starting CV–JD matching for {cname}")
            await match_and_save_cv_jd(cname, cv_file_path=None, force_refresh=False)
            logger.info(f"✅ [PIPELINE] CV–JD match results saved for {cname}")
        except Exception as e:
            logger.warning(f"⚠️ [PIPELINE] Background pipeline error for {cname}: {e}")

    try:
        asyncio.create_task(_run_pipeline(company_name))
    except Exception as e:
        logger.warning(f"⚠️ [PIPELINE] Failed to schedule background pipeline: {e}")

@router.post("/skill-extraction/analyze")
async def analyze_skills(request: Request):
    """Extract skills from CV and JD using AI with caching"""
    try:
        data = await request.json()
        
        # Extract parameters
        cv_filename = data.get("cv_filename")
        jd_url = data.get("jd_url")
        user_id = data.get("user_id", 1)
        force_refresh = data.get("force_refresh", False)
        config_name = data.get("config_name")  # Optional custom config
        
        # Validate required parameters
        if not cv_filename:
            return JSONResponse(
                status_code=400, 
                content={"error": "cv_filename is required"}
            )
        
        if not jd_url:
            return JSONResponse(
                status_code=400,
                content={"error": "jd_url is required"}
            )
        
        logger.info(f"🎯 Skill extraction request: CV={cv_filename}, JD_URL={jd_url}, USER={user_id}, CONFIG={config_name}")
        
        # Perform skill analysis using the service (no fallback)
        result = await skill_extraction_service.analyze_skills(
            cv_filename=cv_filename,
            jd_url=jd_url,
            user_id=user_id,
            force_refresh=force_refresh
        )

        # Fire-and-forget: run JD analysis and CV–JD matching pipeline in background
        company_name = _detect_most_recent_company()
        _schedule_post_skill_pipeline(company_name)
        
        return JSONResponse(content={
            "success": True,
            "message": "Skill extraction completed successfully",
            "config_used": config_name or "default",
            **result
        })
        
    except Exception as e:
        logger.error(f"❌ Skill extraction endpoint error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Skill extraction failed: {str(e)}"}
        )


@router.post("/preliminary-analysis")
async def preliminary_analysis(
    request: Request,
    current_model: str = Depends(get_current_model)
):
    """Preliminary skills analysis from CV filename and JD text"""
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        data = await request.json()
        
        # Extract parameters
        cv_filename = data.get("cv_filename")
        jd_text = data.get("jd_text")
        config_name = data.get("config_name")  # Optional custom config
        user_id = getattr(token_data, 'user_id', 1)
        
        # Validate required parameters
        if not cv_filename:
            return JSONResponse(
                status_code=400, 
                content={"error": "cv_filename is required"}
            )
        
        if not jd_text:
            return JSONResponse(
                status_code=400,
                content={"error": "jd_text is required"}
            )
        
        logger.info(f"🎯 Preliminary analysis request: CV={cv_filename}, JD_length={len(jd_text)}, CONFIG={config_name}")
        
        # Get CV content dynamically (no fallback)
        cv_content_result = cv_content_service.get_cv_content(cv_filename, user_id, use_fallback=False)
        if not cv_content_result["success"]:
            return JSONResponse(
                status_code=404,
                content={
                    "error": cv_content_result.get('error', 'CV content not found'),
                    "suggestions": cv_content_result.get('suggestions', []),
                    "filename": cv_filename
                }
            )
        
        cv_content = cv_content_result["content"]
        logger.info(f"Using CV content from {cv_content_result['source']} for {cv_filename} (length: {len(cv_content)})")
        
        # Perform skills analysis with configuration
        result = await perform_preliminary_skills_analysis(
            cv_content=cv_content,
            jd_text=jd_text,
            cv_filename=cv_filename,
            current_model=current_model,
            config_name=config_name,
            user_id=user_id
        )
        # Trigger JD analysis + CV–JD matching pipeline here as well (fire-and-forget)
        try:
            company_name = _detect_most_recent_company()
            logger.info(f"🚀 [PIPELINE] (preliminary-analysis) detected company: {company_name}")
            _schedule_post_skill_pipeline(company_name)
        except Exception as e:
            logger.warning(f"⚠️ [PIPELINE] (preliminary-analysis) failed to schedule: {e}")
        
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else "Unknown error occurred"
        error_type = type(e).__name__
        traceback_info = traceback.format_exc()
        
        logger.error(f"❌ Preliminary analysis error ({error_type}): {error_msg}")
        logger.error(f"Traceback: {traceback_info}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Preliminary analysis failed ({error_type}): {error_msg}",
                "type": error_type
            }
        )


@router.get("/preliminary-analysis/cache")
async def get_cached_preliminary_analysis(request: Request):
    """Get cached preliminary analysis results"""
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        # For now, return no cached results (always perform fresh analysis)
        # This can be enhanced to implement actual caching
        return JSONResponse(content={"cached": False})
        
    except Exception as e:
        logger.error(f"❌ Cache retrieval error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to retrieve cache: {str(e)}"}
        )


@router.get("/preliminary-analysis/status")
async def get_preliminary_analysis_status(request: Request):
    """Get preliminary analysis status"""
    try:
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        token = auth_header.replace("Bearer ", "")
        token_data = verify_token(token)
        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        # Return status information
        return JSONResponse(content={
            "status": "ready",
            "message": "Preliminary analysis service is available",
            "timestamp": datetime.now().isoformat(),
            "available_configs": list(skills_analysis_config_service.list_configs().keys())
        })
        
    except Exception as e:
        logger.error(f"❌ Status check error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to check status: {str(e)}"}
        )


@router.get("/skill-extraction/files")
async def list_analysis_files(company_name: Optional[str] = None):
    """List saved skill extraction analysis files"""
    try:
        files_info = skill_extraction_service.result_saver.list_saved_analyses(company_name)
        
        return JSONResponse(content={
            "success": True,
            "message": "Analysis files listed successfully",
            **files_info
        })
        
    except Exception as e:
        logger.error(f"❌ List analysis files error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list analysis files: {str(e)}"}
        )


@router.get("/skills-analysis/configs")
async def list_analysis_configs():
    """List available analysis configurations"""
    try:
        configs = skills_analysis_config_service.list_configs()
        
        return JSONResponse(content={
            "success": True,
            "configurations": configs,
            "total_count": len(configs)
        })
        
    except Exception as e:
        logger.error(f"❌ List configs error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list configurations: {str(e)}"}
        )


@router.post("/skills-analysis/configs")
async def create_analysis_config(request: Request):
    """Create a custom analysis configuration"""
    try:
        data = await request.json()
        
        config_name = data.get("name")
        if not config_name:
            return JSONResponse(
                status_code=400,
                content={"error": "Configuration name is required"}
            )
        
        # Create custom configuration
        config = skills_analysis_config_service.create_custom_config(
            config_name, 
            **{k: v for k, v in data.items() if k != "name"}
        )
        
        return JSONResponse(content={
            "success": True,
            "message": f"Configuration '{config_name}' created successfully",
            "config": skills_analysis_config_service._config_to_dict(config)
        })
        
    except Exception as e:
        logger.error(f"❌ Create config error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to create configuration: {str(e)}"}
        )


async def perform_preliminary_skills_analysis(
    cv_content: str, 
    jd_text: str, 
    cv_filename: str, 
    current_model: str,
    config_name: Optional[str] = None,
    user_id: int = 1
) -> dict:
    """Perform preliminary skills analysis between CV and JD using AI prompts with detailed output"""
    try:
        # Get configuration
        config = skills_analysis_config_service.get_config(config_name)
        ai_params = skills_analysis_config_service.get_ai_parameters(config_name)
        logging_params = skills_analysis_config_service.get_logging_parameters(config_name)
        
        if logging_params["enable_detailed_logging"]:
            logger.info(f"🔍 [SKILLS_ANALYSIS] Starting AI-powered skills analysis for {cv_filename}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] CV content length: {len(cv_content)} chars")
            logger.info(f"🔍 [SKILLS_ANALYSIS] JD content length: {len(jd_text)} chars")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Using config: {config_name or 'default'}")
        
        # Get AI service instance
        from app.ai.ai_service import ai_service
        
        # Log current AI service status
        current_status = ai_service.get_current_status()
        if logging_params["enable_detailed_logging"]:
            logger.info(f"🔍 [SKILLS_ANALYSIS] Current AI provider: {current_status.get('current_provider')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Current AI model: {current_status.get('current_model')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Provider available: {current_status.get('provider_available')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Model from header: {current_model}")
        
        # Extract CV skills using enhanced structured prompt
        if logging_params["enable_detailed_logging"]:
            logger.info("🔍 [SKILLS_ANALYSIS] Extracting CV skills with detailed structured analysis...")
        
        cv_structured_prompt = get_skill_prompt('combined_structured', text=cv_content, document_type="CV")
        
        # Use configuration parameters
        cv_structured_response = await ai_service.generate_response(
            prompt=cv_structured_prompt,
            temperature=ai_params["temperature"],
            max_tokens=ai_params["max_tokens"]
        )
        cv_raw_response = cv_structured_response.content
        
        # Parse the structured response
        cv_parser = SkillExtractionParser()
        cv_parsed = cv_parser.parse_response(cv_raw_response, "CV")
        cv_technical_skills = cv_parsed.get('technical_skills', [])
        cv_soft_skills = cv_parsed.get('soft_skills', [])
        cv_domain_keywords = cv_parsed.get('domain_keywords', [])
        
        # Extract JD skills using enhanced structured prompt
        if logging_params["enable_detailed_logging"]:
            logger.info("🔍 [SKILLS_ANALYSIS] Extracting JD skills with detailed structured analysis...")
        
        jd_structured_prompt = get_skill_prompt('combined_structured', text=jd_text, document_type="Job Description")
        
        # Use configuration parameters
        jd_structured_response = await ai_service.generate_response(
            prompt=jd_structured_prompt,
            temperature=ai_params["temperature"],
            max_tokens=ai_params["max_tokens"]
        )
        jd_raw_response = jd_structured_response.content
        
        # Parse the structured response
        jd_parser = SkillExtractionParser()
        jd_parsed = jd_parser.parse_response(jd_raw_response, "JD")
        jd_technical_skills = jd_parsed.get('technical_skills', [])
        jd_soft_skills = jd_parsed.get('soft_skills', [])
        jd_domain_keywords = jd_parsed.get('domain_keywords', [])
        
        # Generate comprehensive analysis
        if logging_params["enable_detailed_logging"]:
            logger.info("🔍 [SKILLS_ANALYSIS] Using structured analysis as comprehensive analysis...")
        
        # Use the detailed structured responses as the comprehensive analysis
        cv_analysis = cv_raw_response
        jd_analysis = jd_raw_response
        
        # Debug logging
        if logging_params["enable_detailed_logging"]:
            logger.info(f"✅ [SKILLS_ANALYSIS] CV Technical Skills ({len(cv_technical_skills)}): {cv_technical_skills}")
            logger.info(f"✅ [SKILLS_ANALYSIS] CV Soft Skills ({len(cv_soft_skills)}): {cv_soft_skills}")
            logger.info(f"✅ [SKILLS_ANALYSIS] CV Domain Keywords ({len(cv_domain_keywords)}): {cv_domain_keywords}")
            logger.info(f"✅ [SKILLS_ANALYSIS] JD Technical Skills ({len(jd_technical_skills)}): {jd_technical_skills}")
            logger.info(f"✅ [SKILLS_ANALYSIS] JD Soft Skills ({len(jd_soft_skills)}): {jd_soft_skills}")
            logger.info(f"✅ [SKILLS_ANALYSIS] JD Domain Keywords ({len(jd_domain_keywords)}): {jd_domain_keywords}")
        
        result = {
            "cv_skills": {
                "technical_skills": cv_technical_skills,
                "soft_skills": cv_soft_skills,
                "domain_keywords": cv_domain_keywords
            },
            "jd_skills": {
                "technical_skills": jd_technical_skills,
                "soft_skills": jd_soft_skills,
                "domain_keywords": jd_domain_keywords
            },
            "cv_comprehensive_analysis": cv_analysis,
            "jd_comprehensive_analysis": jd_analysis,
            "expandable_analysis": {
                "cv_analysis": {
                    "title": "CV Analysis",
                    "content": cv_analysis,
                    "skills_summary": {
                        "technical": f"{len(cv_technical_skills)} technical skills",
                        "soft": f"{len(cv_soft_skills)} soft skills", 
                        "domain": f"{len(cv_domain_keywords)} domain keywords"
                    }
                },
                "jd_analysis": {
                    "title": "Job Description Analysis", 
                    "content": jd_analysis,
                    "skills_summary": {
                        "technical": f"{len(jd_technical_skills)} technical skills",
                        "soft": f"{len(jd_soft_skills)} soft skills",
                        "domain": f"{len(jd_domain_keywords)} domain keywords"
                    }
                }
            },
            "extracted_keywords": list(set(cv_technical_skills + jd_technical_skills + cv_soft_skills + jd_soft_skills + cv_domain_keywords + jd_domain_keywords)),
            "analysis_timestamp": datetime.now().isoformat(),
            "config_used": config_name or "default"
        }
        
        if logging_params["enable_detailed_logging"]:
            logger.info(f"✅ [SKILLS_ANALYSIS] Analysis completed successfully")
        
        # Save results to file if enabled
        file_params = skills_analysis_config_service.get_file_parameters(config_name)
        if file_params["save_analysis_results"]:
            try:
                result_saver = SkillExtractionResultSaver()
                
                # Get the most recent company folder (created during JD analysis)
                company_name = None
                if file_params["auto_detect_company"]:
                    try:
                        from pathlib import Path
                        cv_analysis_dir = Path("cv-analysis")
                        if cv_analysis_dir.exists():
                            # Find the most recently created company folder (excluding Unknown_Company)
                            company_folders = []
                            for company_folder in cv_analysis_dir.iterdir():
                                if (company_folder.is_dir() and 
                                    company_folder.name != "Unknown_Company" and
                                    list(company_folder.glob("job_info_*.json"))):
                                    company_folders.append(company_folder)
                            
                            if company_folders:
                                # Sort by creation time (most recent first)
                                most_recent_folder = max(company_folders, key=lambda p: p.stat().st_mtime)
                                company_name = most_recent_folder.name
                                if logging_params["enable_detailed_logging"]:
                                    logger.info(f"🏢 [COMPANY_DETECTION] Using most recent company folder: {company_name}")
                            else:
                                if logging_params["enable_detailed_logging"]:
                                    logger.warning(f"⚠️ [COMPANY_DETECTION] No valid company folders found")
                    except Exception as e:
                        if logging_params["enable_detailed_logging"]:
                            logger.warning(f"⚠️ [COMPANY_DETECTION] Failed to detect company folder: {e}")
                
                # Prepare data for saving (including the detailed raw responses)
                cv_skills_data = {
                    "technical_skills": cv_technical_skills,
                    "soft_skills": cv_soft_skills,
                    "domain_keywords": cv_domain_keywords,
                    "comprehensive_analysis": cv_analysis,
                    "raw_response": cv_raw_response if logging_params["log_raw_responses"] else ""
                }
                
                jd_skills_data = {
                    "technical_skills": jd_technical_skills,
                    "soft_skills": jd_soft_skills,
                    "domain_keywords": jd_domain_keywords,
                    "comprehensive_analysis": jd_analysis,
                    "raw_response": jd_raw_response if logging_params["log_raw_responses"] else ""
                }
                
                # Save to file with company name
                saved_file_path = result_saver.save_analysis_results(
                    cv_skills=cv_skills_data,
                    jd_skills=jd_skills_data,
                    jd_url="preliminary_analysis",
                    cv_filename=cv_filename,
                    user_id=user_id,
                    cv_data={"text": cv_content, "filename": cv_filename},
                    jd_data=None,
                    company_name=company_name
                )
                
                if logging_params["enable_detailed_logging"]:
                    logger.info(f"📁 [FILE_SAVE] Results saved to: {saved_file_path}")
                result["saved_file_path"] = saved_file_path
                
            except Exception as e:
                if logging_params["enable_detailed_logging"]:
                    logger.warning(f"⚠️ [FILE_SAVE] Failed to save results to file: {str(e)}")
                result["saved_file_path"] = None
        
        # NEW: Perform analyze match after skills analysis completes
        try:
            if logging_params["enable_detailed_logging"]:
                logger.info("🔍 [ANALYZE_MATCH] Starting analyze match assessment...")
            
            # Get analyze match prompt
            analyze_match_prompt = get_skill_prompt('analyze_match', cv_text=cv_content, job_text=jd_text)
            
            # Generate AI response for analyze match
            analyze_match_response = await ai_service.generate_response(
                prompt=analyze_match_prompt,
                temperature=0.3,
                max_tokens=4000
            )
            analyze_match_content = analyze_match_response.content
            
            if logging_params["enable_detailed_logging"]:
                logger.info(f"✅ [ANALYZE_MATCH] Analysis completed (length: {len(analyze_match_content)} chars)")
            
            # Save analyze match to the same file
            try:
                analyze_match_file_path = result_saver.append_analyze_match(analyze_match_content, company_name)
                if logging_params["enable_detailed_logging"]:
                    logger.info(f"📁 [ANALYZE_MATCH] Results appended to: {analyze_match_file_path}")
                result["analyze_match_file_path"] = analyze_match_file_path
            except Exception as e:
                if logging_params["enable_detailed_logging"]:
                    logger.warning(f"⚠️ [ANALYZE_MATCH] Failed to save analyze match: {str(e)}")
                result["analyze_match_file_path"] = None
            
            # Add analyze match to response
            result["analyze_match"] = {
                "raw_analysis": analyze_match_content,
                "company_name": company_name
            }
            
        except Exception as e:
            logger.error(f"❌ [ANALYZE_MATCH] Error in analyze match: {str(e)}")
            # Don't fail the entire request if analyze match fails
            result["analyze_match"] = {
                "error": f"Analyze match failed: {str(e)}",
                "raw_analysis": None
            }
        
        return result
        
    except Exception as e:
        logger.error(f"❌ [SKILLS_ANALYSIS] Error in preliminary skills analysis: {str(e)}")
        raise e
