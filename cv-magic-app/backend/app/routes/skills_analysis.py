"""
Skills Analysis Routes

Extracted from main.py to provide better organization and maintainability
"""
import logging
from datetime import datetime
from fastapi.responses import JSONResponse
from typing import Optional, List

from fastapi import APIRouter, Request, Depends, HTTPException
from app.exceptions import TailoredCVNotFoundError
from fastapi.responses import JSONResponse

from app.core.auth import verify_token
from app.core.dependencies import get_current_user
from app.models.auth import UserData
from app.core.model_dependency import get_current_model
from app.services.skill_extraction import skill_extraction_service
from app.services.cv_content_service import CVContentService
from app.services.dynamic_cv_selector import dynamic_cv_selector
from app.services.skills_analysis_config import skills_analysis_config_service
from app.services.skill_extraction.prompt_templates import get_prompt as get_skill_prompt
from app.services.skill_extraction.response_parser import SkillExtractionParser
from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
from app.ai.ai_service import ai_service
from app.services.jd_analysis import analyze_and_save_company_jd
from app.services.cv_jd_matching import match_and_save_cv_jd
from app.services.context_aware_analysis_pipeline import ContextAwareAnalysisPipeline
from app.unified_latest_file_selector import get_selector_for_user
from app.services.jd_cache_manager import jd_cache_manager
from pathlib import Path
import asyncio
import json
import re
from app.utils.timestamp_utils import TimestampUtils

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Skills Analysis"])


class CVSkillsEmptyError(Exception):
    """Raised when CV skills extraction results in zero skills across all categories."""
    pass

# Helper functions for file validation
async def _extract_company_name_from_jd(jd_text: str) -> str:
    """Extract company name from job description text using AI with fallback to existing folders"""
    try:
        from app.services.job_extractor import extract_job_metadata
        metadata = await extract_job_metadata(jd_text)
        
        if metadata and "company" in metadata and metadata["company"]:
            ai_company_name = metadata["company"].strip()
            
            # Clean and limit the AI-extracted name
            ai_company_name = re.sub(r'[^\w\s-]', '', ai_company_name)
            ai_company_name = re.sub(r'\s+', '_', ai_company_name)
            
            # Limit length to prevent overly long names
            if len(ai_company_name) > 50:
                ai_company_name = ai_company_name[:50]
            
            # Check if this matches any existing company folder
            existing_company = _find_matching_company_folder(ai_company_name)
            if existing_company:
                logger.info(f"🎯 Found matching company folder: {existing_company}")
                return existing_company
            
            return ai_company_name
        
        # Fallback: try simple regex patterns for common company names
        patterns = [
            r'Australia\s+for\s+UNHCR',  # Specific pattern for Australia for UNHCR
            r'([A-Z][a-zA-Z\s&.-]+?)\s+logo',
            r'About\s+([A-Z][a-zA-Z\s&.-]{3,20}?)\s+is',
            r'([A-Z][a-zA-Z\s&.-]{3,20}?)\s+is\s+(?:Australia\'s|the)',
            r'Working\s+at\s+([A-Z][a-zA-Z\s&.-]{3,20}?),',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip() if len(match.groups()) > 0 else match.group(0).strip()
                # Clean company name for file naming
                company_name = re.sub(r'[^\w\s-]', '', company_name)
                company_name = re.sub(r'\s+', '_', company_name)
                
                # Check if this matches any existing company folder
                existing_company = _find_matching_company_folder(company_name)
                if existing_company:
                    logger.info(f"🎯 Found matching company folder: {existing_company}")
                    return existing_company
                
                return company_name
        
        # Final fallback: check if any existing company folders match parts of the JD text
        existing_company = _find_company_in_existing_folders(jd_text)
        if existing_company:
            logger.info(f"🎯 Found company in existing folders: {existing_company}")
            return existing_company
                
        return "Unknown_Company"
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to extract company name: {e}")
        return "Unknown_Company"

def _find_matching_company_folder(extracted_name: str) -> Optional[str]:
    """Find matching company folder for extracted name"""
    try:
        cv_analysis_path = Path("cv-analysis")
        if not cv_analysis_path.exists():
            return None
        
        extracted_lower = extracted_name.lower()
        
        for folder in cv_analysis_path.iterdir():
            if folder.is_dir() and folder.name != "cvs":
                folder_lower = folder.name.lower()
                
                # Exact match
                if folder_lower == extracted_lower:
                    return folder.name
                
                # Partial match (extracted name contains folder name or vice versa)
                if extracted_lower in folder_lower or folder_lower in extracted_lower:
                    return folder.name
        
        return None
        
    except Exception as e:
        logger.warning(f"⚠️ Error finding matching company folder: {e}")
        return None

def _find_company_in_existing_folders(jd_text: str) -> Optional[str]:
    """Find company name by checking if existing folder names appear in JD text"""
    try:
        cv_analysis_path = Path("cv-analysis")
        if not cv_analysis_path.exists():
            return None
        
        jd_lower = jd_text.lower()
        
        for folder in cv_analysis_path.iterdir():
            if folder.is_dir() and folder.name != "cvs":
                # Convert folder name back to readable format for searching
                folder_readable = folder.name.replace('_', ' ').lower()
                
                # Check if the readable folder name appears in the JD text
                if folder_readable in jd_lower:
                    return folder.name
                
                # Also check individual words
                folder_words = folder_readable.split()
                if len(folder_words) >= 2:
                    # Check if at least 2 words from folder name appear in JD
                    matches = sum(1 for word in folder_words if word in jd_lower and len(word) > 3)
                    if matches >= 2:
                        return folder.name
        
        return None
        
    except Exception as e:
        logger.warning(f"⚠️ Error finding company in existing folders: {e}")
        return None

def _validate_required_analysis_files(company_name: str, user_email: Optional[str] = None) -> Optional[str]:
    """Validate that required analysis files exist for the company under the user-scoped path"""
    try:
        from app.utils.timestamp_utils import TimestampUtils
        from app.utils.user_path_utils import get_user_base_path
        
        if not user_email:
            raise ValueError("User authentication required for file operations")
        base_path = get_user_base_path(user_email) / "applied_companies" / company_name
        
        # Check for timestamped files first, then fallback to non-timestamped
        jd_original_file = TimestampUtils.find_latest_timestamped_file(base_path, "jd_original", "json")
        if not jd_original_file:
            jd_original_file = base_path / "jd_original.json"
        
        job_info_file = TimestampUtils.find_latest_timestamped_file(base_path, f"job_info_{company_name}", "json")
        if not job_info_file:
            job_info_file = base_path / f"job_info_{company_name}.json"
        
        missing_files = []
        
        if not jd_original_file.exists():
            missing_files.append(f"jd_original.json")
            
        if not job_info_file.exists():
            missing_files.append(f"job_info_{company_name}.json")
        
        if missing_files:
            return f"Please analyze the job description first before running skills analysis."
            
        return None
        
    except Exception as e:
        logger.error(f"❌ Error validating required files: {e}")
        return f"Error validating required files: {str(e)}"


def _extract_match_rates_from_content(content: str) -> dict:
    """Extract match rates from preextracted comparison content"""
    rates = {
        "technical_skills": 0,
        "soft_skills": 0,
        "domain_keywords": 0,
        "overall": 0
    }
    
    try:
        # Extract overall match rate (new format)
        overall_match = re.search(r"Match Rate:\s*(\d+(?:\.\d+)?)%", content)
        if overall_match:
            rates["overall"] = int(float(overall_match.group(1)))
        
        # Extract from table format
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "Category" in line and "Match Rate" in line:
                # Found header, check next lines for data
                for j in range(i+1, min(i+10, len(lines))):
                    data_line = lines[j].strip()
                    if data_line:
                        # Try to parse table row
                        parts = [p.strip() for p in data_line.split()]
                        if len(parts) >= 6:  # Category, CV Total, JD Total, Matched, Missing, Match Rate
                            try:
                                category = parts[0].lower()
                                match_rate = float(parts[-1]) if parts[-1].replace('.', '').isdigit() else 0
                                
                                if "technical" in category:
                                    rates["technical_skills"] = int(match_rate)
                                elif "soft" in category:
                                    rates["soft_skills"] = int(match_rate)
                                elif "domain" in category:
                                    rates["domain_keywords"] = int(match_rate)
                            except:
                                pass
        
        # Legacy format support
        if rates["technical_skills"] == 0:
            tech_match = re.search(r"Technical Skills Match Rate:\s*(\d+)%", content)
            if tech_match:
                rates["technical_skills"] = int(tech_match.group(1))
        
        if rates["soft_skills"] == 0:
            soft_match = re.search(r"Soft Skills Match Rate:\s*(\d+)%", content)
            if soft_match:
                rates["soft_skills"] = int(soft_match.group(1))
        
        if rates["domain_keywords"] == 0:
            domain_match = re.search(r"Domain Keywords Match Rate:\s*(\d+)%", content)
            if domain_match:
                rates["domain_keywords"] = int(domain_match.group(1))
        
        # If overall not found, calculate it
        if rates["overall"] == 0 and any([rates["technical_skills"], rates["soft_skills"], rates["domain_keywords"]]):
            rates["overall"] = int((rates["technical_skills"] + rates["soft_skills"] + rates["domain_keywords"]) / 3)
    
    except Exception as e:
        logger.warning(f"Failed to extract match rates: {e}")
    
    return rates


def _detect_most_recent_company() -> Optional[str]:
    """Detect the most recent company folder in cv-analysis with a job_info_*.json or jd_original.txt.

    Returns the company folder name or None if not found.
    """
    try:
        base_path = Path("cv-analysis")
        if not base_path.exists():
            return None

        candidates = []
        for d in base_path.iterdir():
            if d.is_dir() and d.name != "Unknown_Company":
                # Check for timestamped files first, then fallback to non-timestamped
                from app.utils.timestamp_utils import TimestampUtils
                has_job_info = TimestampUtils.find_latest_timestamped_file(d, "job_info", "json") or list(d.glob("job_info_*.json"))
                has_jd_original = TimestampUtils.find_latest_timestamped_file(d, "jd_original", "json") or (d / "jd_original.json").exists()
                if has_job_info or has_jd_original:
                    candidates.append(d)

        if not candidates:
            return None

        most_recent = max(candidates, key=lambda p: p.stat().st_mtime)
        return most_recent.name
    except Exception:
        return None


def _schedule_post_skill_pipeline(company_name: Optional[str], token_data=None):
    """Fire-and-forget JD analysis and CV–JD match pipeline for the given company."""
    if not company_name:
        logger.warning("⚠️ [PIPELINE] No company detected; skipping JD analysis & CV–JD matching.")
        return

    logger.info(f"🚀 [PIPELINE] Scheduling JD analysis and CV–JD matching for '{company_name}'...")

    try:
        # Pass token_data to pipeline
        asyncio.create_task(_run_pipeline(company_name, token_data))
    except Exception as e:
        logger.warning(f"⚠️ [PIPELINE] Failed to schedule background pipeline: {e}")

async def _run_pipeline(cname: str, token_data=None):
    pipeline_results = {
        "jd_analysis": False,
        "cv_jd_matching": False,
        "component_analysis": False
    }
    
    # Step 1: JD Analysis (force refresh to guarantee availability)
    try:
        company_dir = Path("cv-analysis") / "applied_companies" / cname
        logger.info(f"🔧 [PIPELINE] Starting JD analysis for {cname} (force_refresh=True)")
        from app.services.jd_analysis.jd_analyzer import JDAnalyzer
        _analyzer = JDAnalyzer(user_email=user_email)
        from app.utils.user_path_utils import get_user_base_path
        # This route requires authentication - user_email should be provided
        if not user_email:
            raise ValueError("User authentication required for JD analysis")
        base_dir = get_user_base_path(user_email)
        jd_result_obj = await _analyzer.analyze_and_save_company_jd(cname, force_refresh=True, base_path=str(base_dir))
        jd_result = jd_result_obj.model_dump() if hasattr(jd_result_obj, 'model_dump') else jd_result_obj.__dict__
        saved_path = jd_result_obj.metadata.get("saved_path") if hasattr(jd_result_obj, 'metadata') and jd_result_obj.metadata else None
        logger.info(f"✅ [PIPELINE] JD analysis saved for {cname} at: {saved_path}")
        pipeline_results["jd_analysis"] = True
    except Exception as e:
        logger.error(f"❌ [PIPELINE] JD analysis failed for {cname}: {e}")
        # Continue with next steps even if this fails

    # Step 2: CV-JD Matching
    try:
        logger.info(f"🔧 [PIPELINE] Starting CV–JD matching for {cname}")
        # Prefer tailored CV if available; else fall back to dynamic latest
        try:
            from app.utils.user_path_utils import get_user_base_path
            user_email = getattr(token_data, 'email', None)
            if not user_email:
                raise ValueError("User authentication required for CV operations")
            base_dir_local = get_user_base_path(user_email)
            company_tailored_dir = base_dir_local / "applied_companies" / cname
            preferred_txt = None
            if company_tailored_dir.exists():
                txt_candidates = list(company_tailored_dir.glob(f"{cname}_tailored_cv_*.txt"))
                if txt_candidates:
                    preferred_txt = max(txt_candidates, key=lambda p: p.stat().st_mtime)
            cv_txt_path_for_match = str(preferred_txt) if preferred_txt else None
            if not cv_txt_path_for_match:
                from app.services.dynamic_cv_selector import dynamic_cv_selector as _dyn
                latest_cv_paths_for_match = _dyn.get_latest_cv_paths_for_services()
                cv_txt_path_for_match = latest_cv_paths_for_match.get('txt_path')
            if cv_txt_path_for_match:
                logger.info(f"📄 [PIPELINE] CV–JD matching will use CV TXT: {cv_txt_path_for_match}")
        except Exception as _sel_err:
            logger.warning(f"⚠️ [PIPELINE] Could not preselect CV TXT for matching: {_sel_err}")
            cv_txt_path_for_match = None

        # Pass JD analysis data directly when available
        jd_data_for_match = None
        try:
            jd_data_for_match = jd_result if 'jd_result' in locals() else None
        except Exception:
            jd_data_for_match = None

        # Force refresh so requirement bonus uses the newest match_counts
        await match_and_save_cv_jd(
            cname,
            cv_file_path=cv_txt_path_for_match,
            force_refresh=True,
            jd_analysis_data=jd_data_for_match
        )
        logger.info(f"✅ [PIPELINE] CV–JD match results saved for {cname}")
        pipeline_results["cv_jd_matching"] = True
    except Exception as e:
        logger.error(f"❌ [PIPELINE] CV-JD matching failed for {cname}: {e}")
        # Log detailed error for debugging
        import traceback
        logger.error(f"[PIPELINE] CV-JD matching traceback: {traceback.format_exc()}")
        # Continue with component analysis even if matching fails

    # Step 3: Component Analysis (includes ATS calculation) - Tailored-only via unified selector
    try:
        logger.info(f"🔍 [PIPELINE] Starting component analysis for {cname}")
        from app.services.ats.modular_ats_orchestrator import modular_ats_orchestrator
        from app.unified_latest_file_selector import get_selector_for_user
        
        # Get latest CV context across tailored+original, log paths, then read content
        try:
            # Create user-specific selector
            user_selector = get_selector_for_user(user_email)
            cv_ctx_debug = user_selector.get_latest_cv_across_all(cname)
            logger.info(
                "📄 [PIPELINE] Latest CV selected → type=%s, ts=%s, json=%s, txt=%s",
                cv_ctx_debug.file_type,
                cv_ctx_debug.timestamp,
                cv_ctx_debug.json_path,
                cv_ctx_debug.txt_path,
            )
            cv_text_for_analysis = user_selector.get_cv_content_across_all(cname)
            try:
                _preview = (cv_text_for_analysis or "")[:400].replace('\n', ' ')
                logger.info("🧪 [PIPELINE] CV content length=%d, preview='%s'", len(cv_text_for_analysis or ""), _preview)
            except Exception:
                pass
        except Exception as sel_err:
            logger.error(f"❌ [PIPELINE] CV selection failed for component analysis: {sel_err}")
            raise
        
        # Check if we have the minimum required files (JD + skills analysis must exist)
        from app.utils.user_path_utils import get_user_base_path
        # This route requires authentication - user_email should be provided
        if not user_email:
            raise ValueError("User authentication required for file validation")
        base_dir = get_user_base_path(user_email)
        from app.utils.timestamp_utils import TimestampUtils
        company_dir = base_dir / "applied_companies" / cname
        jd_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
        if not jd_file:
            jd_file = company_dir / "jd_original.json"
        
        skills_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{cname}_skills_analysis", "json")
        if not skills_file:
            skills_file = company_dir / f"{cname}_skills_analysis.json"
        
        # We can run component analysis if we have CV text, JD, and skills analysis
        if cv_text_for_analysis and jd_file.exists() and skills_file.exists():
            logger.info(f"📄 [PIPELINE] Required files found, proceeding with component analysis")
            component_result = await modular_ats_orchestrator.run_component_analysis(cname, cv_text=cv_text_for_analysis or None)
            logger.info(f"✅ [PIPELINE] Component analysis completed for {cname}")
            pipeline_results["component_analysis"] = True
            
            # Log extracted scores if available
            if isinstance(component_result, dict) and 'extracted_scores' in component_result:
                scores = component_result['extracted_scores']
                logger.info(f"📊 [PIPELINE] Component scores extracted: {len(scores)} scores")
                # Log key scores
                for key in ['skills_relevance', 'experience_alignment', 'industry_fit', 'role_seniority', 'technical_depth']:
                    if key in scores:
                        logger.info(f"📊 [PIPELINE] {key}: {scores[key]:.1f}")
            
            # Check if ATS was calculated
            if isinstance(component_result, dict) and 'ats_results' in component_result:
                final_score = component_result['ats_results'].get('final_ats_score')
                logger.info(f"🎯 [PIPELINE] ATS Score calculated: {final_score}")
        else:
            missing = []
            if not cv_text_for_analysis: missing.append("CV")
            if not jd_file.exists(): missing.append("JD")
            if not skills_file.exists(): missing.append("Skills")
            logger.warning(f"⚠️ [PIPELINE] Missing files for component analysis: {missing}")
            logger.info(f"🔄 [PIPELINE] Skipping component analysis for {cname} due to missing files")
            
    except Exception as component_error:
        logger.error(f"❌ [PIPELINE] Component analysis failed for {cname}: {component_error}")
        import traceback
        logger.error(f"[PIPELINE] Component analysis traceback: {traceback.format_exc()}")
    
    # Log pipeline summary
    successful_steps = [step for step, success in pipeline_results.items() if success]
    failed_steps = [step for step, success in pipeline_results.items() if not success]
    
    logger.info(f"📋 [PIPELINE] Pipeline summary for {cname}:")
    logger.info(f"   ✅ Successful: {successful_steps}")
    if failed_steps:
        logger.info(f"   ❌ Failed: {failed_steps}")
    else:
        logger.info(f"   🎉 All steps completed successfully!")

@router.post("/skill-extraction/analyze")
async def analyze_skills(request: Request, current_user: UserData = Depends(get_current_user)):
    """Extract skills from CV and JD using AI with caching"""
    try:
        # Ensure required directories exist before processing
        from ..utils.directory_utils import ensure_cv_analysis_directories
        ensure_cv_analysis_directories()
        
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
        try:
            result = await skill_extraction_service.analyze_skills(
                cv_filename=cv_filename,
                jd_url=jd_url,
                user_id=user_id,
                force_refresh=force_refresh
            )
        except CVSkillsEmptyError as e:
            logger.error(f"❌ CV skills empty: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "No CV skills could be extracted. Please review the CV content and try again.",
                    "error_type": "cv_skills_empty"
                }
            )

        # Fire-and-forget: run JD analysis and CV–JD matching pipeline in background
        company_name = _detect_most_recent_company()
        try:
            token_data = getattr(request, 'user', None)
        except Exception:
            token_data = None
        _schedule_post_skill_pipeline(company_name, token_data)
        
        # ALSO trigger job saving logic for the analyze endpoint
        try:
            import json
            from datetime import datetime
            if company_name:
                from app.utils.user_path_utils import get_user_base_path
                try:
                    user_email = getattr(token_data, 'email', None)
                except Exception:
                    user_email = None
                if not user_email:
                    raise ValueError("User authentication required for job saving")
                base_dir_local = get_user_base_path(user_email)
                company_dir = base_dir_local / "applied_companies" / company_name
                
                # Check for job_info files and add to saved_jobs.json (same logic as preliminary_analysis)
                job_info_files = list(company_dir.glob("job_info_*.json"))
                if not job_info_files:
                    # Fallback to job_info.json (legacy format)
                    legacy_job_info = company_dir / "job_info.json"
                    if legacy_job_info.exists():
                        job_info_files = [legacy_job_info]
                
                if job_info_files:
                    # Use the most recent job_info file
                    latest_job_info_file = max(job_info_files, key=lambda f: f.stat().st_mtime)
                    
                    with open(latest_job_info_file, 'r', encoding='utf-8') as f:
                        job_metadata = json.load(f)
                    
                    # Save to user-scoped saved jobs file
                    saved_jobs_file = base_dir_local / "saved_jobs" / "saved_jobs.json"
                    saved_jobs_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    if saved_jobs_file.exists():
                        with open(saved_jobs_file, 'r', encoding='utf-8') as f:
                            saved_jobs_data = json.load(f)
                    else:
                        saved_jobs_data = {"jobs": [], "last_updated": datetime.now().isoformat(), "total_jobs": 0}
                    
                    if not any(job.get("job_url") == job_metadata.get("job_url") for job in saved_jobs_data["jobs"]):
                        saved_jobs_data["jobs"].append(job_metadata)
                        saved_jobs_data["last_updated"] = datetime.now().isoformat()
                        saved_jobs_data["total_jobs"] = len(saved_jobs_data["jobs"])
                        
                        with open(saved_jobs_file, 'w', encoding='utf-8') as f:
                            json.dump(saved_jobs_data, f, indent=2, ensure_ascii=False)
                        logger.info(f"✅ [JOBS] Added job to shared jobs file: {job_metadata.get('job_title')} at {job_metadata.get('company_name')}")
                    else:
                        logger.info(f"♻️ [JOBS] Job already exists in saved_jobs.json: {job_metadata.get('job_title')} at {job_metadata.get('company_name')}")
        except Exception as e:
            logger.warning(f"⚠️ [JOBS] Failed to save job info: {e}")
        
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


@router.post("/context-aware-analysis")
async def context_aware_analysis(
    request: Request,
    current_model: str = Depends(get_current_model)
):
    """Context-aware analysis that intelligently selects CV and caches JD data"""
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
        jd_url = data.get("jd_url")
        company = data.get("company")
        is_rerun = data.get("is_rerun", False)  # New parameter for context awareness
        include_tailoring = data.get("include_tailoring", True)
        user_id = getattr(token_data, 'user_id', 1)
        
        # Validate required parameters
        if not jd_url:
            return JSONResponse(
                status_code=400, 
                content={"error": "jd_url is required"}
            )
        
        if not company:
            return JSONResponse(
                status_code=400,
                content={"error": "company is required"}
            )
        
        logger.info(f"🎯 Context-aware analysis request: Company={company}, JD={jd_url}, Rerun={is_rerun}")
        
        # Get CV selection context for user feedback
        cv_context = enhanced_dynamic_cv_selector.get_cv_for_analysis(company, is_rerun)
        logger.info(f"📄 Using {cv_context.cv_type} CV v{cv_context.version} (Source: {cv_context.source})")
        
        # Get JD cache status for user feedback
        jd_cached = jd_cache_manager.should_reuse_jd_analysis(jd_url, company)
        cache_stats = jd_cache_manager.get_cache_stats(company)
        logger.info(f"🗄️ JD Cache status: {'Reusing cached data' if jd_cached else 'Fresh analysis'}")
        
        # Run the context-aware analysis pipeline
        try:
            # Create user-specific pipeline instance
            pipeline = ContextAwareAnalysisPipeline(user_email=current_user.email)
            results = await pipeline.run_full_analysis(
                jd_url=jd_url,
                company=company,
                is_rerun=is_rerun,
                user_id=user_id,
                include_tailoring=include_tailoring
            )
        except TailoredCVNotFoundError as e:
            # Return a specific error response for missing tailored CV
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": str(e),
                    "error_type": "tailored_cv_not_found",
                    "company": company
                }
            )
        
        if results.success:
            logger.info(f"✅ Context-aware analysis completed in {results.processing_time:.2f}s")
            
            # Prepare response with rich context information
            response_data = {
                "success": True,
                "analysis_context": {
                    "company": company,
                    "jd_url": jd_url,
                    "is_rerun": is_rerun,
                    "cv_selection": cv_context.to_dict(),
                    "jd_cache_status": {
                        "cached": jd_cached,
                        "cache_stats": cache_stats
                    },
                    "processing_time": results.processing_time,
                    "steps_completed": results.steps_completed,
                    "steps_skipped": results.steps_skipped
                },
                "results": results.to_dict()['results'],
                "warnings": results.warnings
            }
            
            return JSONResponse(content=response_data)
        else:
            logger.error(f"❌ Context-aware analysis failed: {results.errors}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "errors": results.errors,
                    "warnings": results.warnings,
                    "analysis_context": results.context.to_dict() if results.context else None
                }
            )
        
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else "Unknown error occurred"
        error_type = type(e).__name__
        traceback_info = traceback.format_exc()
        
        logger.error(f"❌ Context-aware analysis error ({error_type}): {error_msg}")
        logger.error(f"Traceback: {traceback_info}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Context-aware analysis failed ({error_type}): {error_msg}",
                "type": error_type
            }
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
        
        # Extract company name from JD text to validate required files
        company_name = await _extract_company_name_from_jd(jd_text)
        logger.info(f"🏢 Extracted company name: {company_name}")
        
        # Validate required files exist before proceeding
        # Validate files under the authenticated user's path
        user_email = getattr(token_data, 'email', None)
        file_validation_error = _validate_required_analysis_files(company_name, user_email)
        if file_validation_error:
            logger.warning(f"❌ Required files validation failed: {file_validation_error}")
            return JSONResponse(
                status_code=400,
                content={"error": file_validation_error}
            )
        
        # NEW: Always use unified latest-across-all CV (tailored or original by newest timestamp)
        from app.unified_latest_file_selector import get_selector_for_user
        try:
            # Create user-specific selector
            user_selector = get_selector_for_user(user_email)
            cv_ctx = user_selector.get_latest_cv_across_all(company_name)
            logger.info(
                "📄 [PRELIM_ANALYSIS] Latest CV selected → type=%s, ts=%s, json=%s, txt=%s",
                cv_ctx.file_type, cv_ctx.timestamp, cv_ctx.json_path, cv_ctx.txt_path
            )
            cv_content = user_selector.get_cv_content_across_all(company_name)
            preview = (cv_content or "")[:400].replace('\n', ' ')
            logger.info("🧪 [PRELIM_ANALYSIS] CV content length=%d, preview='%s'", len(cv_content or ""), preview)
            cv_selection_info = {
                "txt_path": str(cv_ctx.txt_path) if cv_ctx.txt_path else None,
                "json_path": str(cv_ctx.json_path) if cv_ctx.json_path else None,
                "txt_source": cv_ctx.file_type,
                "json_source": cv_ctx.file_type,
            }
        except Exception as e:
            return JSONResponse(status_code=404, content={"error": f"Failed to load latest CV: {str(e)}"})
        
        # Perform skills analysis with configuration
        result = await perform_preliminary_skills_analysis(
            cv_content=cv_content,
            jd_text=jd_text,
            cv_filename=cv_filename,
            current_model=current_model,
            config_name=config_name,
            user_id=user_id
        )
        # Attach CV selection info for frontend display (under expandable_analysis)
        try:
            if cv_selection_info:
                expandable = result.get("expandable_analysis") or {}
                expandable["cv_selection"] = cv_selection_info
                result["expandable_analysis"] = expandable
        except Exception:
            pass
        # Persist inputs for downstream pipeline and trigger JD analysis + CV–JD matching
        try:
            # Derive company from the actual saved path when available
            saved_path = result.get("saved_file_path")
            company_name = None
            if saved_path:
                try:
                    company_name = Path(saved_path).parent.name
                except Exception:
                    company_name = None

            # Fallback to detector if we couldn't extract from saved path
            if not company_name:
                company_name = _detect_most_recent_company()
                logger.info(f"🏢 [PIPELINE] (preliminary-analysis) fallback detected company: {company_name}")

            # If we have a company, ensure required files exist for the pipeline
            if company_name:
                from app.utils.user_path_utils import get_user_base_path
                # Use authenticated user's email for user-scoped path
                try:
                    user_email = getattr(token_data, 'email', None)
                except Exception:
                    user_email = None
                if not user_email:
                    raise ValueError("User authentication required for pipeline operations")
                base_dir = get_user_base_path(user_email)
                company_dir = base_dir / "applied_companies" / company_name
                try:
                    company_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    # best-effort; continue
                    pass

            # Save JD content and job info to files
            try:
                import json
                from datetime import datetime
                from app.utils.timestamp_utils import TimestampUtils
                from app.services.job_extractor import extract_job_metadata
                
                # Check if JD file already exists
                existing_jd = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
                
                if not existing_jd:
                    # Only save if no JD file exists
                    timestamp = TimestampUtils.get_timestamp()
                    jd_file = company_dir / f"jd_original_{timestamp}.json"
                    # Save JD file
                    with open(jd_file, 'w', encoding='utf-8') as f:
                        json.dump({"text": jd_text or "", "saved_at": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
                    logger.info(f"💾 [PIPELINE] (preliminary-analysis) JD JSON saved to: {jd_file}")
                    
                    # Extract and save job metadata
                    job_metadata = await extract_job_metadata(jd_text)
                    if job_metadata:
                        # Save with timestamped, company-specific filename
                        job_info_file = company_dir / f"job_info_{company_name}_{timestamp}.json"
                        with open(job_info_file, 'w', encoding='utf-8') as f:
                            json.dump(job_metadata, f, indent=2, ensure_ascii=False)
                        logger.info(f"💾 [PIPELINE] Job info saved to: {job_info_file}")
                else:
                    logger.info(f"♻️ [PIPELINE] (preliminary-analysis) JD file already exists: {existing_jd}")
                
                # ALWAYS check for job_info files and add to saved_jobs.json (whether JD exists or not)
                job_info_files = list(company_dir.glob("job_info_*.json"))
                if not job_info_files:
                    # Fallback to job_info.json (legacy format)
                    legacy_job_info = company_dir / "job_info.json"
                    if legacy_job_info.exists():
                        job_info_files = [legacy_job_info]
                
                if job_info_files:
                    # Use the most recent job_info file
                    latest_job_info_file = max(job_info_files, key=lambda f: f.stat().st_mtime)
                    
                    with open(latest_job_info_file, 'r', encoding='utf-8') as f:
                        job_metadata = json.load(f)
                    
                    # Save to shared jobs file
                    # Save jobs under the user-scoped cv-analysis path
                    saved_jobs_file = base_dir / "saved_jobs" / "saved_jobs.json"
                    saved_jobs_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    if saved_jobs_file.exists():
                        with open(saved_jobs_file, 'r', encoding='utf-8') as f:
                            saved_jobs_data = json.load(f)
                    else:
                        saved_jobs_data = {"jobs": [], "last_updated": datetime.now().isoformat(), "total_jobs": 0}
                    
                    if not any(job.get("job_url") == job_metadata.get("job_url") for job in saved_jobs_data["jobs"]):
                        saved_jobs_data["jobs"].append(job_metadata)
                        saved_jobs_data["last_updated"] = datetime.now().isoformat()
                        saved_jobs_data["total_jobs"] = len(saved_jobs_data["jobs"])
                        
                        with open(saved_jobs_file, 'w', encoding='utf-8') as f:
                            json.dump(saved_jobs_data, f, indent=2, ensure_ascii=False)
                        logger.info(f"✅ [JOBS] Added job to shared jobs file: {job_metadata.get('job_title')} at {job_metadata.get('company_name')}")
                    else:
                        logger.info(f"♻️ [JOBS] Job already exists in saved_jobs.json: {job_metadata.get('job_title')} at {job_metadata.get('company_name')}")
                
            except Exception as e:
                logger.warning(f"⚠️ [PIPELINE] (preliminary-analysis) failed to save JD and job info: {e}")

                # Ensure CV file exists for the matcher - use dynamic CV selection
                try:
                    import json
                    # Avoid shadowing the module-level import used earlier
                    from app.services.dynamic_cv_selector import dynamic_cv_selector as _dynamic_cv_selector
                    
                    # Get the latest CV file dynamically
                    latest_cv_paths = _dynamic_cv_selector.get_latest_cv_paths_for_services()
                    cv_file = Path(latest_cv_paths['json_path']) if latest_cv_paths['json_path'] else None
                    
                    logger.info(f"📄 [PIPELINE] Using dynamic CV: {cv_file} from {latest_cv_paths['json_source']} folder")
                    
                    # Check if file exists and has structured data
                    should_save = True
                    if cv_file.exists():
                        try:
                            with open(cv_file, 'r', encoding='utf-8') as f:
                                existing_data = json.load(f)
                            # If file has structured CV data (not just text), don't overwrite it
                            if isinstance(existing_data, dict) and any(key in existing_data for key in ['personal_information', 'career_profile', 'skills', 'education', 'experience']):
                                logger.info(f"💾 [PIPELINE] (preliminary-analysis) Structured CV already exists, preserving it: {cv_file}")
                                should_save = False
                        except:
                            # If we can't read the file, we'll save the simple version
                            pass
                    
                    if should_save:
                        with open(cv_file, 'w', encoding='utf-8') as f:
                            json.dump({"text": cv_content or "", "saved_at": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
                        logger.info(f"💾 [PIPELINE] (preliminary-analysis) CV JSON saved to: {cv_file}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ [PIPELINE] (preliminary-analysis) failed to save CV file: {e}")

            logger.info(f"🚀 [PIPELINE] (preliminary-analysis) scheduling for company: {company_name}")
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


@router.get("/cv-context/{company}")
async def get_cv_context(company: str, is_rerun: bool = False):
    """Get CV selection context for UI feedback"""
    try:
        # Get CV selection context
        cv_context = enhanced_dynamic_cv_selector.get_cv_for_analysis(company, is_rerun)
        
        # Get available CV versions
        available_versions = enhanced_dynamic_cv_selector.list_available_cv_versions(company)
        
        # Get JD cache status
        cache_stats = jd_cache_manager.get_cache_stats(company)
        
        return JSONResponse(content={
            "success": True,
            "company": company,
            "cv_context": cv_context.to_dict(),
            "available_cv_versions": available_versions,
            "jd_cache_status": cache_stats,
            "recommendation": {
                "suggested_cv": cv_context.cv_type,
                "reason": cv_context.source,
                "version": cv_context.version
            }
        })
        
    except Exception as e:
        logger.error(f"❌ CV context error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get CV context: {str(e)}"}
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
async def list_analysis_files(company_name: Optional[str] = None, current_user: UserData = Depends(get_current_user)):
    """List saved skill extraction analysis files - user-specific path isolated"""
    try:
        from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
        user_result_saver = SkillExtractionResultSaver(user_email=current_user.email)
        files_info = user_result_saver.list_saved_analyses(company_name)
        
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


@router.post("/trigger-component-analysis/{company}")
async def trigger_component_analysis(company: str, current_user: UserData = Depends(get_current_user)):
    """Manually trigger component analysis for a specific company (for testing/debugging)"""
    try:
        logger.info(f"🔧 [MANUAL] Triggering component analysis for company: {company}")
        
        from app.services.ats.modular_ats_orchestrator import modular_ats_orchestrator
        from app.services.dynamic_cv_selector import dynamic_cv_selector
        
        # Use dynamic CV selection for the latest CV file
        latest_cv_paths = dynamic_cv_selector.get_latest_cv_paths_for_services()
        logger.info(f"🔧 [MANUAL] Using dynamic CV: {latest_cv_paths['json_source']} folder")
        
        # Check if required files exist
        from app.utils.user_path_utils import get_user_base_path
        user_email = getattr(token_data, 'email', None)
        if not user_email:
            raise ValueError("User authentication required for analysis listing")
        base_dir = get_user_base_path(user_email)
        
        # Use timestamped files with fallback
        from app.utils.timestamp_utils import TimestampUtils
        company_dir = base_dir / company
        jd_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
        if not jd_file:
            jd_file = company_dir / "jd_original.json"
        
        # Use timestamped match file with fallback
        match_file = TimestampUtils.find_latest_timestamped_file(company_dir, "cv_jd_match_results", "json")
        if not match_file:
            match_file = company_dir / "cv_jd_match_results.json"
        
        required_files = {
            "cv_file": Path(latest_cv_paths['json_path']) if latest_cv_paths['json_path'] else None,
            "jd_file": jd_file, 
            "match_file": match_file
        }
        
        missing_files = {k: str(v) for k, v in required_files.items() if not v.exists()}
        if missing_files:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Missing required files for component analysis",
                    "missing_files": missing_files,
                    "company": company
                }
            )
        
        # Run component analysis
        result = await modular_ats_orchestrator.run_component_analysis(company)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Component analysis completed for {company}",
            "company": company,
            "extracted_scores": result.get("extracted_scores", {}),
            "timestamp": result.get("timestamp"),
            "total_scores": len(result.get("extracted_scores", {}))
        })
        
    except Exception as e:
        logger.error(f"❌ [MANUAL] Component analysis failed for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Component analysis failed: {str(e)}",
                "company": company
            }
        )


@router.post("/trigger-complete-pipeline/{company}")
async def trigger_complete_pipeline(company: str, current_user: UserData = Depends(get_current_user)):
    """Manually trigger the complete analysis pipeline for a company (JD analysis → CV-JD matching → Component analysis → ATS calculation)"""
    try:
        logger.info(f"🚀 [MANUAL] Triggering complete pipeline for company: {company}")
        
        results = {
            "company": company,
            "steps": []
        }
        
# Step 1: JD Analysis
        try:
            logger.info(f"🔧 [MANUAL] Step 1: JD Analysis for {company}")
            # Save job info to shared jobs file
            from pathlib import Path
            import json
            from datetime import datetime

            saved_jobs_file = Path("cv-analysis/saved_jobs/saved_jobs.json")
            saved_jobs_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create initial jobs file if it doesn't exist
            if not saved_jobs_file.exists():
                initial_data = {
                    "jobs": [],
                    "last_updated": datetime.utcnow().isoformat(),
                    "total_jobs": 0
                }
                with open(saved_jobs_file, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)

            # Read current jobs
            with open(saved_jobs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Get job info from original JD file
            job_info_file = Path("cv-analysis") / "applied_companies" / company / "job_info.json"
            if job_info_file.exists():
                with open(job_info_file, 'r', encoding='utf-8') as f:
                    job_info = json.load(f)
                    
                    # Add job to jobs list if not already present
                    if not any(job.get("job_url") == job_info.get("job_url") for job in data["jobs"]):
                        data["jobs"].append(job_info)
                        data["last_updated"] = datetime.utcnow().isoformat()
                        data["total_jobs"] = len(data["jobs"])
                        
                        # Save updated jobs data
                        with open(saved_jobs_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        logger.info(f"✅ [JOBS] Added job to shared jobs file: {job_info.get('job_title')} at {job_info.get('company_name')}")

            from app.utils.user_path_utils import get_user_base_path
            user_email = getattr(token_data, 'email', None)
            if not user_email:
                raise ValueError("User authentication required for JD analysis")
            base_dir = get_user_base_path(user_email)
            await analyze_and_save_company_jd(company, force_refresh=True, base_path=str(base_dir))
            results["steps"].append({"step": "jd_analysis", "status": "success"})
        except Exception as e:
            logger.error(f"❌ [MANUAL] JD Analysis failed: {e}")
            results["steps"].append({"step": "jd_analysis", "status": "failed", "error": str(e)})
            
        # Step 2: CV-JD Matching
        try:
            logger.info(f"🔧 [MANUAL] Step 2: CV-JD Matching for {company}")
            await match_and_save_cv_jd(company, cv_file_path=None, force_refresh=True)
            results["steps"].append({"step": "cv_jd_matching", "status": "success"})
        except Exception as e:
            logger.error(f"❌ [MANUAL] CV-JD Matching failed: {e}")
            results["steps"].append({"step": "cv_jd_matching", "status": "failed", "error": str(e)})
            
        # Step 3: Component Analysis (includes ATS calculation)
        try:
            logger.info(f"🔧 [MANUAL] Step 3: Component Analysis for {company}")
            from app.services.ats.modular_ats_orchestrator import modular_ats_orchestrator
            component_result = await modular_ats_orchestrator.run_component_analysis(company)
            
            if isinstance(component_result, dict) and 'extracted_scores' in component_result:
                results["steps"].append({
                    "step": "component_analysis", 
                    "status": "success",
                    "scores_count": len(component_result.get('extracted_scores', {}))
                })
                
                # Check if ATS was calculated
                if 'ats_results' in component_result:
                    results["steps"].append({
                        "step": "ats_calculation",
                        "status": "success",
                        "final_score": component_result['ats_results'].get('final_ats_score')
                    })
            else:
                results["steps"].append({"step": "component_analysis", "status": "success"})
        except Exception as e:
            logger.error(f"❌ [MANUAL] Component Analysis failed: {e}")
            results["steps"].append({"step": "component_analysis", "status": "failed", "error": str(e)})
        
        # Check final status
        all_success = all(step.get("status") == "success" for step in results["steps"])
        results["overall_status"] = "success" if all_success else "partial_failure"
        
        return JSONResponse(content=results)
        
    except Exception as e:
        logger.error(f"❌ [MANUAL] Complete pipeline failed for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Pipeline failed: {str(e)}",
                "company": company
            }
        )


@router.post("/create-recommendation-file/{company}")
async def create_recommendation_file(company: str, force_update: bool = False):
    """Manually create or update a recommendation file for a company"""
    try:
        from app.services.ats_recommendation_service import ATSRecommendationService
        
        logger.info(f"🔧 [MANUAL] Creating recommendation file for company: {company}")
        
        # Create user-specific service instance
        ats_service = ATSRecommendationService(user_email=current_user.email)
        
        # Check if company has ATS data first
        companies_with_ats = ats_service.list_companies_with_ats_data()
        if company not in companies_with_ats:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "No ATS calculation data found for this company",
                    "company": company,
                    "companies_with_ats": companies_with_ats
                }
            )
        
        # Create/update the recommendation file
        success = ats_service.update_existing_recommendation(company, force_update)
        
        if success:
            recommendation_file = ats_service.get_recommendation_file_path(company)
            return JSONResponse(content={
                "success": True,
                "message": f"Recommendation file created/updated for {company}",
                "company": company,
                "file_path": str(recommendation_file),
                "force_update": force_update
            })
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Failed to create recommendation file or no update needed",
                    "company": company,
                    "force_update": force_update
                }
            )
    
    except Exception as e:
        logger.error(f"❌ [MANUAL] Failed to create recommendation file for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to create recommendation file: {str(e)}",
                "company": company
            }
        )


@router.post("/batch-create-recommendations")
async def batch_create_recommendations(companies: Optional[List[str]] = None, force_update: bool = False):
    """Batch create recommendation files for multiple companies"""
    try:
        from app.services.ats_recommendation_service import ATSRecommendationService
        
        logger.info(f"🔧 [BATCH] Creating recommendation files - Force update: {force_update}")
        
        # Create user-specific service instance
        ats_service = ATSRecommendationService(user_email=current_user.email)
        
        # Process companies
        results = ats_service.batch_create_recommendations(companies, force_update)
        
        successful_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Batch recommendation creation completed",
            "results": results,
            "summary": {
                "successful": successful_count,
                "total": total_count,
                "failed": total_count - successful_count
            },
            "force_update": force_update
        })
    
    except Exception as e:
        logger.error(f"❌ [BATCH] Batch recommendation creation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Batch creation failed: {str(e)}"
            }
        )


@router.get("/recommendation-files")
async def list_recommendation_files():
    """List all companies with recommendation files"""
    try:
        from app.services.ats_recommendation_service import ATSRecommendationService
        
        from app.utils.user_path_utils import get_user_base_path
        user_email = getattr(token_data, 'email', None)
        if not user_email:
            raise ValueError("User authentication required for recommendations listing")
        base_dir = get_user_base_path(user_email)
        companies_with_recommendations = []
        
        if base_dir.exists():
            # Create user-specific service instance
            ats_service = ATSRecommendationService(user_email=user_email)
            
            for company_dir in base_dir.iterdir():
                if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                    recommendation_file = ats_service.get_recommendation_file_path(company_dir.name)
                    
                    if recommendation_file.exists():
                        # Get file info
                        stat_info = recommendation_file.stat()
                        
                        # Read the recommendation data
                        try:
                            with open(recommendation_file, 'r', encoding='utf-8') as f:
                                recommendation_data = json.load(f)
                            
                            ats_entries = recommendation_data.get("ats_calculation_entries", [])
                            latest_entry = ats_entries[-1] if ats_entries else {}
                            
                            companies_with_recommendations.append({
                                "company": company_dir.name,
                                "file_path": str(recommendation_file),
                                "file_size": stat_info.st_size,
                                "last_modified": stat_info.st_mtime,
                                "ats_score": latest_entry.get("final_ats_score"),
                                "category_status": latest_entry.get("category_status"),
                                "recommendation": latest_entry.get("recommendation")
                            })
                            
                        except Exception as e:
                            logger.warning(f"Could not read recommendation file for {company_dir.name}: {e}")
                            companies_with_recommendations.append({
                                "company": company_dir.name,
                                "file_path": str(recommendation_file),
                                "file_size": stat_info.st_size,
                                "last_modified": stat_info.st_mtime,
                                "error": "Could not read file contents"
                            })
        
        return JSONResponse(content={
            "success": True,
            "companies_with_recommendations": companies_with_recommendations,
            "total_count": len(companies_with_recommendations)
        })
    
    except Exception as e:
        logger.error(f"❌ Failed to list recommendation files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to list recommendation files: {str(e)}"
            }
        )


@router.post("/create-ai-prompt/{company}")
async def create_ai_recommendation_prompt(company: str):
    """Create AI recommendation prompt file for a company"""
    try:
        from app.services.ats_recommendation_service import ATSRecommendationService
        
        logger.info(f"🤖 [AI PROMPT] Creating AI recommendation prompt for: {company}")
        
        # Create user-specific service instance
        ats_service = ATSRecommendationService(user_email=current_user.email)
        
        # Check if recommendation file exists
        recommendation_file = ats_service.get_recommendation_file_path(company)
        if not recommendation_file.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Recommendation file not found for this company",
                    "company": company,
                    "recommendation_file": str(recommendation_file),
                    "suggestion": "Create recommendation file first using /create-recommendation-file endpoint"
                }
            )
        
        # Create AI prompt file
        try:
            import sys
            from pathlib import Path
            backend_path = Path(__file__).parent.parent.parent
            sys.path.append(str(backend_path))
            
            from prompt.ai_recommendation_prompt_template import create_company_prompt_file
            prompt_file_path = create_company_prompt_file(company, str(recommendation_file))
            
            return JSONResponse(content={
                "success": True,
                "message": f"AI recommendation prompt created for {company}",
                "company": company,
                "prompt_file_path": prompt_file_path,
                "recommendation_file_path": str(recommendation_file)
            })
            
        except Exception as e:
            logger.error(f"❌ [AI PROMPT] Failed to create prompt for {company}: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": f"Failed to create AI prompt: {str(e)}",
                    "company": company
                }
            )
    
    except Exception as e:
        logger.error(f"❌ [AI PROMPT] Error in create_ai_recommendation_prompt for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"API error: {str(e)}",
                "company": company
            }
        )


@router.get("/ai-prompt-files")
async def list_ai_prompt_files():
    """List all AI recommendation prompt files"""
    try:
        from pathlib import Path
        
        prompt_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/prompt")
        prompt_files = []
        
        if prompt_dir.exists():
            for prompt_file in prompt_dir.glob("*_prompt_recommendation.py"):
                # Extract company name from filename
                company_name = prompt_file.stem.replace("_prompt_recommendation", "")
                
                # Get file info
                stat_info = prompt_file.stat()
                
                # Try to extract ATS score from file content
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for ATS Score comment line
                    ats_score = "N/A"
                    for line in content.split('\n'):
                        if line.strip().startswith("# ATS Score:"):
                            ats_score = line.split(":")[1].strip()
                            break
                    
                    prompt_files.append({
                        "company": company_name,
                        "file_path": str(prompt_file),
                        "file_size": stat_info.st_size,
                        "last_modified": stat_info.st_mtime,
                        "ats_score": ats_score
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not read prompt file for {company_name}: {e}")
                    prompt_files.append({
                        "company": company_name,
                        "file_path": str(prompt_file),
                        "file_size": stat_info.st_size,
                        "last_modified": stat_info.st_mtime,
                        "error": "Could not read file contents"
                    })
        
        return JSONResponse(content={
            "success": True,
            "prompt_files": prompt_files,
            "total_count": len(prompt_files)
        })
    
    except Exception as e:
        logger.error(f"❌ Failed to list AI prompt files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to list AI prompt files: {str(e)}"
            }
        )


@router.post("/generate-ai-recommendation/{company}")
async def generate_ai_recommendation(company: str, force_regenerate: bool = False):
    """Generate AI recommendation for a specific company"""
    try:
        from app.services.ai_recommendation_generator import ai_recommendation_generator
        
        logger.info(f"🤖 [API] Generating AI recommendation for: {company}")
        
        # Check if input recommendation file exists using user-specific path
        from app.utils.user_path_utils import get_user_base_path
        user_base_path = get_user_base_path(current_user.email)
        input_file = user_base_path / "applied_companies" / company / f"{company}_input_recommendation.json"
        if not input_file.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Input recommendation data not found for this company",
                    "company": company,
                    "input_file": str(input_file),
                    "suggestion": "Run skills analysis pipeline first to generate input recommendation data"
                }
            )
        
        # Generate AI recommendation using user-specific service
        from app.services.ai_recommendation_generator import AIRecommendationGenerator
        user_ai_recommendation_generator = AIRecommendationGenerator(user_email=current_user.email)
        success = await user_ai_recommendation_generator.generate_ai_recommendation(company, force_regenerate)
        
        if success:
            ai_file = user_ai_recommendation_generator.get_ai_recommendation_path(company)
            ai_info = user_ai_recommendation_generator.get_ai_recommendation_info(company)
            
            return JSONResponse(content={
                "success": True,
                "message": f"AI recommendation generated for {company}",
                "company": company,
                "ai_file_path": str(ai_file),
                "file_info": ai_info,
                "force_regenerate": force_regenerate
            })
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Failed to generate AI recommendation",
                    "company": company
                }
            )
    
    except Exception as e:
        logger.error(f"❌ [API] Error generating AI recommendation for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"API error: {str(e)}",
                "company": company
            }
        )


@router.post("/batch-generate-ai-recommendations")
async def batch_generate_ai_recommendations(
    companies: Optional[List[str]] = None, 
    force_regenerate: bool = False,
    max_concurrent: int = 2,
    current_user: UserData = Depends(get_current_user)
):
    """Generate AI recommendations for multiple companies in batch - user-specific path isolated"""
    try:
        from app.services.ai_recommendation_generator import AIRecommendationGenerator
        
        logger.info(f"🚀 [BATCH API] Starting batch AI recommendation generation for user: {current_user.email}")
        logger.info(f"   Companies: {companies or 'All with prompts'}")
        logger.info(f"   Force regenerate: {force_regenerate}")
        logger.info(f"   Max concurrent: {max_concurrent}")
        
        # Generate recommendations using user-specific service
        user_ai_recommendation_generator = AIRecommendationGenerator(user_email=current_user.email)
        results = await user_ai_recommendation_generator.batch_generate_recommendations(
            companies=companies,
            force_regenerate=force_regenerate,
            max_concurrent=max_concurrent
        )
        
        successful_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Batch AI recommendation generation completed",
            "results": results,
            "summary": {
                "successful": successful_count,
                "total": total_count,
                "failed": total_count - successful_count,
                "success_rate": f"{(successful_count/total_count*100):.1f}%" if total_count > 0 else "0%"
            },
            "settings": {
                "force_regenerate": force_regenerate,
                "max_concurrent": max_concurrent
            }
        })
    
    except Exception as e:
        logger.error(f"❌ [BATCH API] Batch AI recommendation generation failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Batch generation failed: {str(e)}"
            }
        )


@router.get("/ai-recommendation-files")
async def list_ai_recommendation_files(current_user: UserData = Depends(get_current_user)):
    """List all AI recommendation files - user-specific path isolated"""
    try:
        from app.services.ai_recommendation_generator import AIRecommendationGenerator
        
        user_ai_recommendation_generator = AIRecommendationGenerator(user_email=current_user.email)
        companies_with_ai = user_ai_recommendation_generator.list_companies_with_ai_recommendations()
        ai_files_info = []
        
        for company in companies_with_ai:
            ai_info = user_ai_recommendation_generator.get_ai_recommendation_info(company)
            if ai_info:
                ai_files_info.append(ai_info)
        
        return JSONResponse(content={
            "success": True,
            "ai_recommendation_files": ai_files_info,
            "total_count": len(ai_files_info)
        })
    
    except Exception as e:
        logger.error(f"❌ Failed to list AI recommendation files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to list AI recommendation files: {str(e)}"
            }
        )


@router.get("/ai-recommendation/{company}")
async def get_ai_recommendation(company: str):
    """Get AI recommendation content for a specific company"""
    try:
        from app.services.ai_recommendation_generator import ai_recommendation_generator
        
        ai_file = ai_recommendation_generator.get_ai_recommendation_path(company)
        
        if not ai_file.exists():
            return JSONResponse(
                status_code=404,
                content={
                    "error": "AI recommendation not found for this company",
                    "company": company,
                    "ai_file_path": str(ai_file)
                }
            )
        
        # Read AI recommendation content
        with open(ai_file, 'r', encoding='utf-8') as f:
            ai_data = json.load(f)
        
        return JSONResponse(content={
            "success": True,
            "company": company,
            "ai_recommendation": ai_data
        })
    
    except Exception as e:
        logger.error(f"❌ Failed to get AI recommendation for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to get AI recommendation: {str(e)}",
                "company": company
            }
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


@router.get("/analysis-results")
async def list_companies_with_results():
    """List all companies that have analysis results"""
    try:
        from app.utils.user_path_utils import get_user_base_path
        user_email = getattr(token_data, 'email', None)
        if not user_email:
            raise ValueError("User authentication required for companies listing")
        base_dir = get_user_base_path(user_email)
        
        if not base_dir.exists():
            return JSONResponse(content={
                "success": True,
                "companies": []
            })
        
        companies = []
        for company_dir in base_dir.iterdir():
            if company_dir.is_dir() and company_dir.name != "Unknown_Company":
                # Use timestamped analysis file with fallback
                from app.utils.timestamp_utils import TimestampUtils
                analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company_dir.name}_skills_analysis", "json")
                if not analysis_file:
                    analysis_file = company_dir / f"{company_dir.name}_skills_analysis.json"
                if analysis_file.exists():
                    # Get basic info about the analysis
                    try:
                        with open(analysis_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Check what analyses are available
                        analyses_available = {
                            "skills": bool(data.get("cv_skills") or data.get("jd_skills")),
                            "preextracted_comparison": bool(data.get("preextracted_comparison_entries")),
                            "component_analysis": bool(data.get("component_analysis_entries")),
                            "ats_calculation": bool(data.get("ats_calculation_entries"))
                        }
                        
                        # Get latest ATS score if available
                        ats_score = None
                        ats_entries = data.get("ats_calculation_entries", [])
                        if ats_entries:
                            ats_score = ats_entries[-1].get("final_ats_score")
                        
                        companies.append({
                            "name": company_dir.name,
                            "analyses_available": analyses_available,
                            "ats_score": ats_score,
                            "last_modified": analysis_file.stat().st_mtime
                        })
                    except Exception as e:
                        logger.warning(f"Failed to read analysis for {company_dir.name}: {e}")
        
        # Sort by last modified time (most recent first)
        companies.sort(key=lambda x: x["last_modified"], reverse=True)
        
        return JSONResponse(content={
            "success": True,
            "companies": companies,
            "total": len(companies)
        })
        
    except Exception as e:
        logger.error(f"❌ [API] Failed to list companies with results: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list companies: {str(e)}"}
        )


@router.get("/analysis-results/{company}")
async def get_analysis_results(company: str, request: Request = None):
    """Get complete analysis results for a company (skills, components, ATS) for frontend display"""
    try:
        logger.info(f"📊 [API] Fetching analysis results for company: {company}")
        
        # Build file path using timestamped files
        from app.utils.user_path_utils import get_user_base_path
        
        # Try to get user email from token, default to admin if not available
        user_email = None
        if request:
            try:
                auth_header = request.headers.get("authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.replace("Bearer ", "")
                    from app.core.auth import verify_token
                    token_data = verify_token(token)
                    if token_data:
                        user_email = getattr(token_data, 'email', None)
            except Exception as e:
                logger.warning(f"Failed to get user email from token, using default: {e}")
        
        base_dir = get_user_base_path(user_email)
        company_dir = base_dir / "applied_companies" / company
        
        # Use timestamped analysis file with fallback
        from app.utils.timestamp_utils import TimestampUtils
        analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_skills_analysis", "json")
        if not analysis_file:
            analysis_file = company_dir / f"{company}_skills_analysis.json"
        
        if not analysis_file.exists():
            return JSONResponse(
                status_code=404,
                content={"error": f"No analysis found for company: {company}"}
            )
        
        # Read analysis data
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract latest entries from each analysis type
        def _sorted(lst: list[str]) -> list[str]:
            try:
                return sorted(lst, key=lambda s: s.lower())
            except Exception:
                return sorted(lst)

        # Sort skills if present (covers existing stored files)
        cv_skills_raw = data.get("cv_skills", {})
        jd_skills_raw = data.get("jd_skills", {})
        cv_skills_sorted = {
            "technical_skills": _sorted(cv_skills_raw.get("technical_skills", [])),
            "soft_skills": _sorted(cv_skills_raw.get("soft_skills", [])),
            "domain_keywords": _sorted(cv_skills_raw.get("domain_keywords", [])),
        }
        jd_skills_sorted = {
            "technical_skills": _sorted(jd_skills_raw.get("technical_skills", [])),
            "soft_skills": _sorted(jd_skills_raw.get("soft_skills", [])),
            "domain_keywords": _sorted(jd_skills_raw.get("domain_keywords", [])),
        }

        # Get latest preextracted comparison
        latest_preextracted = None
        preextracted_entries = data.get("preextracted_comparison_entries", [])
        if preextracted_entries:
            latest = preextracted_entries[-1]
            content = latest.get("content", "")
            latest_preextracted = {
                "timestamp": latest.get("timestamp"),
                "model_used": latest.get("model_used"),
                "raw_content": content,
                "match_rates": _extract_match_rates_from_content(content)
            }

        # Get latest component analysis
        latest_component = None
        component_entries = data.get("component_analysis_entries", [])
        if component_entries:
            latest = component_entries[-1]
            latest_component = {
                "timestamp": latest.get("timestamp"),
                "extracted_scores": latest.get("extracted_scores", {}),
                "component_details": latest.get("component_analyses", {})
            }

        # Get latest ATS calculation
        latest_ats = None
        ats_entries = data.get("ats_calculation_entries", [])
        if ats_entries:
            latest_ats = ats_entries[-1]

        result = {
            "company": company,
            "skills_analysis": {
                "cv_skills": cv_skills_sorted,
                "jd_skills": jd_skills_sorted
            },
            "preextracted_comparison": latest_preextracted,
            "component_analysis": latest_component,
            "ats_score": latest_ats
        }
        
        # Get latest preextracted comparison
        preextracted_entries = data.get("preextracted_comparison_entries", [])
        if preextracted_entries:
            latest = preextracted_entries[-1]
            # Parse the content to extract match rates
            content = latest.get("content", "")
            result["preextracted_comparison"] = {
                "timestamp": latest.get("timestamp"),
                "model_used": latest.get("model_used"),
                "raw_content": content,
                # Extract match rates from content using regex
                "match_rates": _extract_match_rates_from_content(content)
            }
        
        # Get latest component analysis
        component_entries = data.get("component_analysis_entries", [])
        if component_entries:
            latest = component_entries[-1]
            result["component_analysis"] = {
                "timestamp": latest.get("timestamp"),
                "extracted_scores": latest.get("extracted_scores", {}),
                "component_details": latest.get("component_analyses", {})
            }
        
        # Get latest ATS calculation
        ats_entries = data.get("ats_calculation_entries", [])
        if ats_entries:
            latest = ats_entries[-1]
            result["ats_score"] = latest
        
        # Get AI recommendation content if available
        # Use timestamped AI recommendation file with fallback
        from app.utils.timestamp_utils import TimestampUtils
        # company_dir already set to base_dir / "applied_companies" / company above
        # Try multiple naming patterns for AI recommendations
        ai_recommendation_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_ai_recommendation", "json")
        if not ai_recommendation_file:
            # Try input_recommendation pattern
            ai_recommendation_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{company}_input_recommendation", "json")
        if not ai_recommendation_file:
            # Try non-timestamped files
            ai_recommendation_file = company_dir / f"{company}_ai_recommendation.json"
        if not ai_recommendation_file.exists():
            ai_recommendation_file = company_dir / f"{company}_input_recommendation.json"
        
        if ai_recommendation_file.exists():
            try:
                with open(ai_recommendation_file, 'r', encoding='utf-8') as f:
                    ai_data = json.load(f)
                
                # Handle different file formats
                if "recommendation_content" in ai_data:
                    # Standard AI recommendation format
                    result["ai_recommendation"] = {
                        "content": ai_data.get("recommendation_content"),
                        "generated_at": ai_data.get("generated_at"),
                        "model_info": ai_data.get("ai_model_info", {})
                    }
                else:
                    # Input recommendation format - extract recommendations
                    recommendations = []
                    
                    # Extract strategic decision from analyze_match_entries
                    if "analyze_match_entries" in ai_data and ai_data["analyze_match_entries"]:
                        for entry in ai_data["analyze_match_entries"]:
                            if "content" in entry and "STRATEGIC PURSUE" in entry["content"]:
                                # Extract strategic priorities section
                                content = entry["content"]
                                if "IF PURSUING - STRATEGIC PRIORITIES:" in content:
                                    priorities_section = content.split("IF PURSUING - STRATEGIC PRIORITIES:")[1]
                                    if "HONEST BOTTOM LINE:" in priorities_section:
                                        priorities_section = priorities_section.split("HONEST BOTTOM LINE:")[0]
                                    recommendations.append(f"🎯 Strategic Priorities:\n{priorities_section.strip()}")
                    
                    # Extract component analysis recommendations
                    if "component_analysis_entries" in ai_data and ai_data["component_analysis_entries"]:
                        for entry in ai_data["component_analysis_entries"]:
                            if "component_analyses" in entry and "skills" in entry["component_analyses"]:
                                skills_data = entry["component_analyses"]["skills"]
                                if "skills_analysis" in skills_data:
                                    skill_recommendations = []
                                    for skill in skills_data["skills_analysis"]:
                                        if "jd_application" in skill and skill.get("relevance_score", "0").isdigit() and int(skill.get("relevance_score", "0")) >= 80:
                                            skill_recommendations.append(f"• {skill['skill']}: {skill['jd_application']}")
                                    if skill_recommendations:
                                        recommendations.append(f"💡 Key Skills to Highlight:\n" + "\n".join(skill_recommendations))
                    
                    result["ai_recommendation"] = {
                        "content": "\n\n".join(recommendations) if recommendations else "Analysis completed - strategic insights available",
                        "generated_at": ai_data.get("timestamp") or (ai_data.get("analyze_match_entries", [{}])[0].get("timestamp") if ai_data.get("analyze_match_entries") else None),
                        "model_info": {"model": "comprehensive_analysis", "source": "input_recommendation"}
                    }
            except Exception as e:
                logger.warning(f"Failed to load AI recommendation for {company}: {e}")
                result["ai_recommendation"] = None
        else:
            result["ai_recommendation"] = None
        
        # Get tailored CV information if available from company-specific folder
        tailored_cv_dir = base_dir / "applied_companies" / company
        tailored_cv_file = TimestampUtils.find_latest_timestamped_file(tailored_cv_dir, f"{company}_tailored_cv", "json")
        
        if tailored_cv_file and tailored_cv_file.exists():
            try:
                result["tailored_cv"] = {
                    "file_path": str(tailored_cv_file),
                    "generated_at": tailored_cv_file.stat().st_mtime,
                    "available": True
                }
                logger.info(f"✅ [API] Found tailored CV for {company}: {tailored_cv_file}")
            except Exception as e:
                logger.warning(f"Failed to load tailored CV info for {company}: {e}")
                result["tailored_cv"] = None
        else:
            result["tailored_cv"] = None
            logger.debug(f"No tailored CV found for {company}")
        
        return JSONResponse(content={
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"❌ [API] Failed to get analysis results for {company}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to retrieve analysis results: {str(e)}"}
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

        # Enforce stop: if no CV skills extracted, abort early for frontend handling
        if not cv_technical_skills and not cv_soft_skills and not cv_domain_keywords:
            raise CVSkillsEmptyError("CV skills extraction returned zero items across all categories")
        
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
        
        # Sort skills alphabetically (case-insensitive) for consistent frontend display
        def _sorted(lst: list[str]) -> list[str]:
            try:
                return sorted(lst, key=lambda s: s.lower())
            except Exception:
                return sorted(lst)

        cv_technical_skills = _sorted(cv_technical_skills)
        cv_soft_skills = _sorted(cv_soft_skills)
        cv_domain_keywords = _sorted(cv_domain_keywords)
        jd_technical_skills = _sorted(jd_technical_skills)
        jd_soft_skills = _sorted(jd_soft_skills)
        jd_domain_keywords = _sorted(jd_domain_keywords)

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
                result_saver = SkillExtractionResultSaver(user_email=user_email)
                
                # Get the company name from existing job info files (reuse already extracted company name)
                company_name = None
                if file_params["auto_detect_company"]:
                    try:
                        from pathlib import Path
                        from app.utils.user_path_utils import get_user_base_path
                        from app.utils.timestamp_utils import TimestampUtils
                        import json
                        
                        # Use user-scoped path - require valid user email
                        if not user_email:
                            logger.error("❌ [COMPANY_DETECTION] No user email provided - cannot access user directories")
                            return {"error": "User authentication required"}
                        base_dir = get_user_base_path(user_email)
                        applied_companies_dir = base_dir / "applied_companies"
                        
                        if logging_params["enable_detailed_logging"]:
                            logger.info(f"🔍 [COMPANY_DETECTION] Looking in: {applied_companies_dir}")
                        
                        if applied_companies_dir.exists():
                            # Find the most recently created company folder with job_info files
                            company_folders = []
                            for company_folder in applied_companies_dir.iterdir():
                                if (company_folder.is_dir() and 
                                    company_folder.name != "Unknown_Company" and
                                    not company_folder.name.startswith("Unknown_Company_")):
                                    
                                    # Check for job_info files
                                    job_info_files = list(company_folder.glob("job_info_*.json"))
                                    if job_info_files:
                                        company_folders.append(company_folder)
                                        if logging_params["enable_detailed_logging"]:
                                            logger.info(f"📁 [COMPANY_DETECTION] Found company folder: {company_folder.name} with {len(job_info_files)} job_info files")
                            
                            if company_folders:
                                # Sort by creation time (most recent first)
                                most_recent_folder = max(company_folders, key=lambda p: p.stat().st_mtime)
                                company_name = most_recent_folder.name
                                if logging_params["enable_detailed_logging"]:
                                    logger.info(f"🏢 [COMPANY_DETECTION] Using most recent company folder: {company_name}")
                                    
                                    # Also log the job_info content for debugging
                                    job_info_files = list(most_recent_folder.glob("job_info_*.json"))
                                    if job_info_files:
                                        latest_job_info = max(job_info_files, key=lambda p: p.stat().st_mtime)
                                        try:
                                            with open(latest_job_info, 'r', encoding='utf-8') as f:
                                                job_data = json.load(f)
                                                logger.info(f"📋 [COMPANY_DETECTION] Job info company: {job_data.get('company_name', 'N/A')}")
                                        except Exception as e:
                                            logger.warning(f"⚠️ [COMPANY_DETECTION] Could not read job_info: {e}")
                            else:
                                if logging_params["enable_detailed_logging"]:
                                    logger.warning(f"⚠️ [COMPANY_DETECTION] No valid company folders found in {applied_companies_dir}")
                                    # List all folders for debugging
                                    all_folders = [f.name for f in applied_companies_dir.iterdir() if f.is_dir()]
                                    logger.info(f"📂 [COMPANY_DETECTION] Available folders: {all_folders}")
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
                    cv_comprehensive_analysis=cv_analysis,
                    jd_comprehensive_analysis=jd_analysis,
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
                temperature=0.0,
                max_tokens=4000
            )
            analyze_match_content = analyze_match_response.content
            
            if logging_params["enable_detailed_logging"]:
                logger.info(f"✅ [ANALYZE_MATCH] Analysis completed (length: {len(analyze_match_content)} chars)")
            
            # Save analyze match to the same file
            try:
                # Ensure we have a valid company name before saving
                if not company_name or company_name == "Unknown_Company":
                    # Fallback: try to extract company name from JD text if not found
                    company_name = await _extract_company_name_from_jd(jd_text)
                    if logging_params["enable_detailed_logging"]:
                        logger.info(f"🏢 [ANALYZE_MATCH] Using fallback company name: {company_name}")
                
                # Final validation - ensure we have a valid company name
                if company_name and company_name != "Unknown_Company" and not company_name.startswith("Unknown_Company_"):
                    try:
                        from app.utils.user_path_utils import validate_company_name
                        validate_company_name(company_name)
                        analyze_match_file_path = result_saver.append_analyze_match(analyze_match_content, company_name)
                        if logging_params["enable_detailed_logging"]:
                            logger.info(f"📁 [ANALYZE_MATCH] Results appended to: {analyze_match_file_path}")
                        result["analyze_match_file_path"] = analyze_match_file_path
                    except ValueError as ve:
                        if logging_params["enable_detailed_logging"]:
                            logger.warning(f"⚠️ [ANALYZE_MATCH] Company name validation failed: {ve}")
                        result["analyze_match_file_path"] = None
                else:
                    if logging_params["enable_detailed_logging"]:
                        logger.warning(f"⚠️ [ANALYZE_MATCH] No valid company name found (got: {company_name}), skipping save")
                    result["analyze_match_file_path"] = None
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
        
        # NEW STEP: Pre-Extracted Skills Comparison (auto-trigger after Analyze Match)
        try:
            if logging_params["enable_detailed_logging"]:
                logger.info("🔍 [PREEXTRACTED_COMPARISON] Starting pre-extracted skills semantic comparison...")

            # Validate skill inputs before comparison
            if not cv_technical_skills and not cv_soft_skills and not cv_domain_keywords:
                raise ValueError("No CV skills extracted - cannot perform comparison")
            if not jd_technical_skills and not jd_soft_skills and not jd_domain_keywords:
                raise ValueError("No JD skills extracted - cannot perform comparison")

            # Build input skill lists from the parsed results above
            pre_cv_skills = {
                "technical_skills": cv_technical_skills,
                "soft_skills": cv_soft_skills,
                "domain_keywords": cv_domain_keywords
            }
            pre_jd_skills = {
                "technical_skills": jd_technical_skills,
                "soft_skills": jd_soft_skills,
                "domain_keywords": jd_domain_keywords
            }

            # Use centralized AI service with the exact provided prompt
            from app.services.skill_extraction.preextracted_comparator import execute_skills_semantic_comparison
            preextracted_output = await execute_skills_semantic_comparison(
                ai_service,
                cv_skills=pre_cv_skills,
                jd_skills=pre_jd_skills,
                temperature=ai_params["temperature"],
                max_tokens=min(ai_params["max_tokens"], 3000)
            )

            if logging_params["enable_detailed_logging"]:
                logger.info(f"✅ [PREEXTRACTED_COMPARISON] Completed (length: {len(preextracted_output)} chars)")

            # Append to the same analysis file (same as analyze match)
            try:
                pre_file_path = result_saver.append_preextracted_comparison(
                  preextracted_output,
                  company_name or "Unknown_Company",
                  result.get("saved_file_path")
                )
                if logging_params["enable_detailed_logging"]:
                    logger.info(f"📁 [PREEXTRACTED_COMPARISON] Results appended to: {pre_file_path}")
                result["preextracted_comparison_file_path"] = pre_file_path
            except Exception as e:
                logger.error(f"❌ [PREEXTRACTED_COMPARISON] Failed to append results: {str(e)}")
                result["preextracted_comparison_file_path"] = None

            # Include raw formatted analysis in response payload
            result["preextracted_skills_comparison"] = {
                "raw_output": preextracted_output,
                "company_name": company_name
            }

            # Note: Component analysis moved to run after skill comparison completes
            # (see _schedule_post_skill_pipeline function)
            result["component_analysis"] = {"status": "scheduled_after_skill_comparison"}

        except Exception as e:
            logger.error(f"❌ [PREEXTRACTED_COMPARISON] Error: {str(e)}")
            result["preextracted_skills_comparison"] = {
                "error": f"Pre-extracted comparison failed: {str(e)}",
                "raw_output": None
            }
        
        return result
        
    except Exception as e:
        logger.error(f"❌ [SKILLS_ANALYSIS] Error in preliminary skills analysis: {str(e)}")
        raise e
