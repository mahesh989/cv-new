"""
Skills Analysis Routes

Extracted from main.py to provide better organization and maintainability
"""
import logging
from datetime import datetime
from fastapi.responses import JSONResponse
from app.utils.path_debug import path_debug
from typing import Optional, List, Any, Dict

from fastapi import APIRouter, Request, Depends, HTTPException
from app.exceptions import TailoredCVNotFoundError
from fastapi.responses import JSONResponse

from app.core.auth import verify_token
from app.core.dependencies import get_current_user
from app.models.auth import UserData
from app.core.model_dependency import get_current_model
from app.services.skill_extraction import skill_extraction_service
from app.services.cv_content_service import CVContentService
from app.services.skills_analysis_config import skills_analysis_config_service
from app.services.skill_extraction.prompt_templates import get_prompt as get_skill_prompt, get_skill_prompts
from app.services.skill_extraction.response_parser import SkillExtractionParser
from app.services.skill_extraction.result_saver import SkillExtractionResultSaver
from app.ai.ai_service import ai_service
from app.services.jd_analysis import analyze_and_save_company_jd
from app.services.cv_jd_matching import match_and_save_cv_jd
from app.services.context_aware_analysis_pipeline import ContextAwareAnalysisPipeline
from app.unified_latest_file_selector import get_selector_for_user, FileContext
from app.services.jd_cache_manager import jd_cache_manager
from pathlib import Path
import asyncio
import json
import re
from app.utils.timestamp_utils import TimestampUtils
from app.utils.user_path_utils import get_user_base_path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Skills Analysis"])


class CVSkillsEmptyError(Exception):
    """Raised when CV skills extraction results in zero skills across all categories."""
    pass

# Helper class to convert FileContext to legacy format for compatibility
class CVContextAdapter:
    """Adapter to convert FileContext to legacy cv_context format"""
    
    def __init__(self, file_context: FileContext):
        self.file_context = file_context
        self.cv_type = file_context.file_type or "original"
        self.version = file_context.timestamp or "latest"
        self.source = self._determine_source()
    
    def _determine_source(self) -> str:
        """Determine source based on file type"""
        if self.file_context.file_type == "tailored":
            return "tailored_cv"
        elif self.file_context.file_type == "original":
            return "original_cv"
        else:
            return "latest_cv"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format expected by legacy code"""
        return {
            "cv_type": self.cv_type,
            "version": self.version,
            "source": self.source,
            "json_path": str(self.file_context.json_path) if self.file_context.json_path else None,
            "txt_path": str(self.file_context.txt_path) if self.file_context.txt_path else None,
            "exists": self.file_context.exists,
            "file_type": self.file_context.file_type,
            "timestamp": self.file_context.timestamp,
            "company": self.file_context.company,
        }

# Helper function to get CV context using unified selector
def get_cv_context_for_analysis(user_email: str, company: str, is_rerun: bool = False) -> CVContextAdapter:
    """Get CV context for analysis using unified file selector"""
    selector = get_selector_for_user(user_email)
    if is_rerun:
        # For reruns, use latest CV across all types
        file_context = selector.get_latest_cv_across_all(company)
    else:
        # For fresh analysis, use the standard selection logic
        file_context = selector.get_latest_cv_for_company(company)
    return CVContextAdapter(file_context)

# Helper function to list available CV versions
def list_available_cv_versions(user_email: str, company: str) -> List[Dict[str, Any]]:
    """List available CV versions for a company using unified selector"""
    selector = get_selector_for_user(user_email)
    versions = []
    
    # Get tailored CVs
    tailored_path = selector.tailored_path
    if tailored_path and tailored_path.exists():
        tailored_files = list(tailored_path.glob(f"{company}_tailored_cv_*.txt"))
        for txt_file in tailored_files:
            json_file = txt_file.with_suffix('.json')
            timestamp_match = re.search(r'_(\d{8}_\d{6})', txt_file.stem)
            timestamp = timestamp_match.group(1) if timestamp_match else None
            versions.append({
                "type": "tailored",
                "version": timestamp or "unknown",
                "txt_path": str(txt_file),
                "json_path": str(json_file) if json_file.exists() else None,
                "timestamp": timestamp,
            })
    
    # Get original CVs
    original_path = selector.original_path
    if original_path and original_path.exists():
        # Check for base original CV
        base_json = original_path / "original_cv.json"
        if base_json.exists():
            base_txt = original_path / "original_cv.txt"
            versions.append({
                "type": "original",
                "version": "base",
                "txt_path": str(base_txt) if base_txt.exists() else None,
                "json_path": str(base_json),
                "timestamp": None,
            })
        
        # Check for timestamped original CVs
        original_files = list(original_path.glob(f"{company}_original_cv_*.txt"))
        for txt_file in original_files:
            json_file = txt_file.with_suffix('.json')
            timestamp_match = re.search(r'_(\d{8}_\d{6})', txt_file.stem)
            timestamp = timestamp_match.group(1) if timestamp_match else None
            versions.append({
                "type": "original",
                "version": timestamp or "unknown",
                "txt_path": str(txt_file),
                "json_path": str(json_file) if json_file.exists() else None,
                "timestamp": timestamp,
            })
    
    # Sort by timestamp (newest first)
    versions.sort(key=lambda v: v.get("timestamp") or "", reverse=True)
    return versions

# Helper function to get most recent company folder
async def _get_most_recent_company_folder(user_email: str) -> Optional[str]:
    """
    Get the most recently created company folder (by job_info file timestamp).
    This is a fallback when JD URL is not available.
    """
    try:
        from app.utils.user_path_utils import get_user_base_path
        
        base_path = get_user_base_path(user_email)
        applied_companies_path = base_path / "applied_companies"
        
        if not applied_companies_path.exists():
            return None
        
        most_recent_company = None
        most_recent_time = 0
        
        # Search through all company folders
        for company_folder in applied_companies_path.iterdir():
            if not company_folder.is_dir():
                continue
            
            # Look for job_info files in this company folder
            job_info_files = list(company_folder.glob("job_info_*.json"))
            
            for job_info_file in job_info_files:
                try:
                    mtime = job_info_file.stat().st_mtime
                    if mtime > most_recent_time:
                        most_recent_time = mtime
                        most_recent_company = company_folder.name
                except Exception:
                    continue
        
        if most_recent_company:
            logger.info(f"✅ [CV_CONTEXT] Found most recent company folder: {most_recent_company}")
        
        return most_recent_company
        
    except Exception as e:
        logger.error(f"Error getting most recent company folder: {e}")
        return None

# Helper function to get company name from saved job_info files by JD URL
async def get_company_from_saved_job_info(jd_url: str, user_email: str) -> Optional[Dict[str, str]]:
    """
    Look up company name and slug from saved job_info files by matching JD URL.
    This ensures we use the same company name that was extracted during 'Analyze & Save Job'.
    
    Args:
        jd_url: Job description URL to match
        user_email: User's email for path lookup
        
    Returns:
        Dict with 'company_name' and 'company_slug' if found, None otherwise
    """
    try:
        from app.utils.user_path_utils import get_user_base_path
        from app.utils.timestamp_utils import TimestampUtils
        import json
        
        base_path = get_user_base_path(user_email)
        applied_companies_path = base_path / "applied_companies"
        
        if not applied_companies_path.exists():
            return None
        
        # Search through all company folders
        for company_folder in applied_companies_path.iterdir():
            if not company_folder.is_dir():
                continue
            
            # Look for job_info files in this company folder
            job_info_files = list(company_folder.glob("job_info_*.json"))
            
            for job_info_file in job_info_files:
                try:
                    with open(job_info_file, 'r', encoding='utf-8') as f:
                        job_info = json.load(f)
                        
                    # Check if JD URL matches (check multiple possible fields)
                    extracted_info = job_info.get('extracted_info', {})
                    saved_jd_url = (job_info.get('jd_url') or 
                                   job_info.get('job_url') or 
                                   extracted_info.get('jd_url') or 
                                   extracted_info.get('job_url'))
                    
                    if saved_jd_url and saved_jd_url.strip() == jd_url.strip():
                        # Found matching job_info - return company name and slug
                        company_name = job_info.get('company_name') or extracted_info.get('company_name')
                        company_slug = job_info.get('company_slug') or company_folder.name
                        
                        if company_name:
                            logger.info(f"✅ Found saved company for JD URL: {company_name} (slug: {company_slug})")
                            return {
                                'company_name': company_name,
                                'company_slug': company_slug
                            }
                except Exception as e:
                    logger.debug(f"Error reading job_info file {job_info_file}: {e}")
                    continue
        
        logger.info(f"⚠️ No saved job_info found for JD URL: {jd_url}")
        return None
        
    except Exception as e:
        logger.error(f"Error looking up company from saved job_info: {e}")
        return None

# Helper function to normalize company name (check if it looks like URL-extracted)
def is_url_extracted_company(company: str) -> bool:
    """
    Check if company name looks like it was extracted from URL (e.g., 'www_ethicaljobs_com_au')
    
    Detection criteria:
    - Must contain 'www' AND ('com' or 'org' or 'net') AND have multiple underscores
    - OR contains domain patterns like 'com_au', 'org_uk', etc.
    """
    if not company:
        return False
    
    company_lower = company.lower()
    
    # Must have multiple underscores to be URL-like
    if company.count('_') < 2:
        return False
    
    # Strong indicators: www + domain extension
    has_www = 'www' in company_lower
    has_domain = any(ext in company_lower for ext in ['_com', '_org', '_net', '_co', '_io'])
    
    # Pattern: www_something_com_au or something_com_au
    if has_www and has_domain:
        return True
    
    # Pattern: domain_country (e.g., com_au, org_uk)
    domain_country_patterns = ['_com_', '_org_', '_net_', '_co_', '_io_']
    if any(pattern in company_lower for pattern in domain_country_patterns):
        return True
    
    # Pattern: ends with _com, _org, etc. (but not just one underscore)
    if company_lower.endswith(('_com', '_org', '_net', '_co', '_io')):
        return True
    
    return False

# Helper functions for file validation

# ============================================================================
# NEW: Single AI Method Integration
# Added: [DATE]
# ============================================================================

from app.services.company_extractor import CompanyExtractor, CompanyResult, Confidence
from app.ai.ai_service import AIServiceManager

async def _extract_company_name_from_jd_v2(
    jd_text: str, 
    jd_url: str, 
    user_email: str,
    user: Any = None
) -> tuple[str, CompanyResult]:
    """
    New version using single AI company extractor
    Returns both the folder name and full result object
    
    Args:
        jd_text: Job description text
        jd_url: Job description URL
        user_email: User's email for folder lookup
        user: User context for AI service initialization
        
    Returns:
        Tuple of (company_folder_name, CompanyResult)
    """
    try:
        # Initialize extractor
        ai_service = AIServiceManager()
        extractor = CompanyExtractor(ai_service)
        
        # Extract company name
        result = await extractor.extract(jd_url, jd_text, user)
        
        # Check for existing company folders
        from app.utils.user_path_utils import get_user_base_path
        applied_companies_path = get_user_base_path(user_email)
        existing_folders = []
        
        if applied_companies_path.exists():
            existing_folders = [
                d.name for d in applied_companies_path.iterdir() 
                if d.is_dir() and d.name != "cvs"
            ]
        
        # Match against existing folders
        matched = extractor.match_existing(result, existing_folders)
        
        company_name = matched if matched else result.normalized
        
        print(f"Company extraction: '{result.name}' → folder: '{company_name}' (confidence: {result.confidence.value})")
        
        return company_name, result
        
    except Exception as e:
        print(f"Error in company extraction: {str(e)}")
        return "Unknown_Company", CompanyResult(
            name="Unknown",
            confidence=Confidence.LOW,
            is_agency=False,
            normalized="Unknown_Company",
            display_name="Unknown"
        )


# Wrapper to maintain old signature
async def _extract_company_name_from_jd(jd_text: str, user_email: str, user: Any = None) -> str:
    """
    DEPRECATED: Use _extract_company_name_from_jd_v2 instead
    Maintained for backward compatibility
    
    This wrapper calls the new single AI method with empty URL
    Returns only the company folder name (old behavior)
    """
    company_name, _ = await _extract_company_name_from_jd_v2(jd_text, "", user_email, user)
    return company_name


# Original function preserved below for reference (now deprecated)
async def _extract_company_name_from_jd_original(jd_text: str, user_email: str) -> str:
    """Extract company name from job description text using AI with fallback to existing folders"""
    try:
        from app.services.job_extractor import extract_job_metadata
        metadata = await extract_job_metadata(jd_text)
        
        if metadata and "company" in metadata and metadata["company"]:
            ai_company_name = metadata["company"].strip()
            
            # Clean and limit the AI-extracted name
            ai_company_name = re.sub(r'^(?i)(organisation_|organization_|company_|org_)', '', ai_company_name)
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
                existing_company = _find_matching_company_folder(company_name, user_email)
                if existing_company:
                    logger.info(f"🎯 Found matching company folder: {existing_company}")
                    return existing_company
                return company_name
        
        # Final fallback: check if any existing company folders match parts of the JD text
        existing_company = _find_company_in_existing_folders(jd_text, user_email)
        if existing_company:
            logger.info(f"🎯 Found company in existing folders: {existing_company}")
            return existing_company
                
        return "Unknown_Company"
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to extract company name: {e}")
        return "Unknown_Company"

def _find_matching_company_folder(extracted_name: str, user_email: str) -> Optional[str]:
    """Find matching company folder for extracted name"""
    try:
        cv_analysis_path = get_user_base_path(user_email)
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

def _find_company_in_existing_folders(jd_text: str, user_email: str) -> Optional[str]:
    """Find company name by checking if existing folder names appear in JD text"""
    try:
        cv_analysis_path = get_user_base_path(user_email)
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


def _detect_most_recent_company(user_email: str) -> Optional[str]:
    """Detect the most recent company folder in the user's cv-analysis with a job_info_*.json or jd_original.json.

    Returns the company folder name or None if not found.
    """
    try:
        from app.utils.user_path_utils import get_user_base_path
        base_path = get_user_base_path(user_email)
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
        "component_analysis": False,
        "input_recommendation": False,
        "ai_recommendation": False,
        "tailored_cv": False
    }
    
    # Get user email and base directory first
    from app.utils.user_path_utils import get_user_base_path
    user_email = getattr(token_data, 'email', None) if token_data else None
    if not user_email:
        raise ValueError("User authentication required for pipeline operations")
    base_dir = get_user_base_path(user_email)
    
    # Step 1: JD Analysis (force refresh to guarantee availability)
    try:
        company_dir = base_dir / "applied_companies" / cname
        logger.info(f"🔧 [PIPELINE] Starting JD analysis for {cname} (force_refresh=True)")
        from app.services.jd_analysis.jd_analyzer import JDAnalyzer
        _analyzer = JDAnalyzer(user_email=user_email)
        jd_result_obj = await _analyzer.analyze_and_save_company_jd(cname, force_refresh=True, base_path=str(base_dir))
        jd_result = jd_result_obj.model_dump() if hasattr(jd_result_obj, 'model_dump') else jd_result_obj.__dict__
        saved_path = jd_result_obj.metadata.get("saved_path") if hasattr(jd_result_obj, 'metadata') and jd_result_obj.metadata else None
        logger.info(f"✅ [PIPELINE] JD analysis saved for {cname} at: {saved_path}")
        
        # CRITICAL FIX: Read JD URL and text from job_info file (not from JD analysis result)
        # The JD analysis result doesn't include the URL or text, so we must read from the job_info file
        jd_url_for_recording = ''
        jd_text_for_recording = ''
        job_title_for_recording = ''
        
        try:
            from app.utils.timestamp_utils import TimestampUtils
            
            # Find the job_info file
            job_info_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"job_info_{cname}", "json")
            if job_info_file and job_info_file.exists():
                with open(job_info_file, 'r', encoding='utf-8') as f:
                    job_info = json.load(f)
                    jd_url_for_recording = job_info.get('job_url', '') or ''
                    job_title_for_recording = job_info.get('job_title', '') or ''
                    logger.info(f"📝 [PIPELINE] Loaded JD info from {job_info_file.name}: url={jd_url_for_recording}, title={job_title_for_recording}")
            
            # Also read JD text from jd_original file
            jd_original_file = TimestampUtils.find_latest_timestamped_file(company_dir, "jd_original", "json")
            if jd_original_file and jd_original_file.exists():
                with open(jd_original_file, 'r', encoding='utf-8') as f:
                    jd_data = json.load(f)
                    # The jd_original file has the structure: {"jd_text": "...", "jd_url": "..."}
                    jd_text_for_recording = jd_data.get('jd_text', '') or ''
                    # Fallback to jd_url from jd_original if not in job_info
                    if not jd_url_for_recording:
                        jd_url_for_recording = jd_data.get('jd_url', '') or ''
                    logger.info(f"📝 [PIPELINE] Loaded JD text from {jd_original_file.name}: {len(jd_text_for_recording)} chars")
        except Exception as load_err:
            logger.warning(f"⚠️ [PIPELINE] Failed to load JD info for tracking: {load_err}")
        
        pipeline_results["jd_analysis"] = True
    except Exception as e:
        logger.error(f"❌ [PIPELINE] JD analysis failed for {cname}: {e}")
        # Continue with next steps even if this fails

    # Step 2: CV-JD Matching
    try:
        logger.info(f"🔧 [PIPELINE] Starting CV–JD matching for {cname}")
        # Use unified selector with JD tracking (respects first-time JD rule)
        try:
            from app.utils.user_path_utils import get_user_base_path
            user_email = getattr(token_data, 'email', None)
            if not user_email:
                raise ValueError("User authentication required for CV operations")
            
            # Get JD URL for tracking (from JD analysis result)
            jd_url_for_cv_selection = jd_url_for_recording if 'jd_url_for_recording' in locals() else ""
            jd_text_for_cv_selection = jd_text_for_recording if 'jd_text_for_recording' in locals() else ""
            
            # Use unified selector with JD tracking
            from app.unified_latest_file_selector import get_selector_for_user
            user_selector = get_selector_for_user(user_email)
            cv_context = user_selector.get_latest_cv_for_company(cname, jd_url_for_cv_selection, jd_text_for_cv_selection)
            cv_txt_path_for_match = str(cv_context.txt_path) if cv_context and cv_context.txt_path else None
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
            jd_analysis_data=jd_data_for_match,
            user_email=user_email
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
        from app.services.ats.modular_ats_orchestrator import get_modular_ats_orchestrator
        from app.unified_latest_file_selector import get_selector_for_user
        
        # Create user-specific orchestrator
        user_orchestrator = get_modular_ats_orchestrator(user_email=user_email)
        
        # Get latest CV context using JD tracking (respects first-time JD rule)
        try:
            # Get JD URL for tracking (from JD analysis result)
            jd_url_for_cv_selection = jd_url_for_recording if 'jd_url_for_recording' in locals() else ""
            jd_text_for_cv_selection = jd_text_for_recording if 'jd_text_for_recording' in locals() else ""
            
            # Create user-specific selector
            user_selector = get_selector_for_user(user_email)
            cv_ctx_debug = user_selector.get_latest_cv_for_company(cname, jd_url_for_cv_selection, jd_text_for_cv_selection)
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
            component_result = await user_orchestrator.run_component_analysis(cname, cv_text=cv_text_for_analysis or None)
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
    
    # Step 4: Create Input Recommendation File (required for AI recommendation generation)
    try:
        logger.info(f"📋 [PIPELINE] Creating input recommendation file for {cname}")
        from app.services.ats_recommendation_service import ATSRecommendationService
        recommendation_service = ATSRecommendationService(user_email=user_email)
        
        # Extract and save optimized recommendation
        recommendation_data = recommendation_service.extract_ats_recommendation_data(cname)
        if recommendation_data:
            saved_file = recommendation_service.save_optimized_recommendation(cname, recommendation_data)
            if saved_file:
                logger.info(f"✅ [PIPELINE] Input recommendation file created for {cname}: {saved_file}")
                pipeline_results["input_recommendation"] = True
            else:
                logger.warning(f"⚠️ [PIPELINE] Failed to save input recommendation for {cname}")
                pipeline_results["input_recommendation"] = False
        else:
            logger.warning(f"⚠️ [PIPELINE] Failed to extract recommendation data for {cname}")
            pipeline_results["input_recommendation"] = False
    except Exception as rec_error:
        logger.error(f"❌ [PIPELINE] Input recommendation creation failed for {cname}: {rec_error}", exc_info=True)
        pipeline_results["input_recommendation"] = False
    
    # Step 5: AI Recommendation Generation (if input recommendation was successful)
    if pipeline_results["input_recommendation"]:
        try:
            logger.info(f"🤖 [PIPELINE] Starting AI recommendation generation for {cname}")
            from app.services.ai_recommendation_generator import AIRecommendationGenerator
            
            ai_service = AIRecommendationGenerator(user_email=user_email)
            ai_success = await ai_service.generate_ai_recommendation(cname, force_regenerate=False)
            
            if ai_success:
                logger.info(f"✅ [PIPELINE] AI recommendation generated for {cname}")
                pipeline_results["ai_recommendation"] = True
            else:
                logger.warning(f"⚠️ [PIPELINE] AI recommendation generation failed for {cname}")
                pipeline_results["ai_recommendation"] = False
        except Exception as ai_error:
            logger.error(f"❌ [PIPELINE] AI recommendation generation failed for {cname}: {ai_error}")
            pipeline_results["ai_recommendation"] = False
    else:
        logger.info(f"⏭️ [PIPELINE] Skipping AI recommendation generation for {cname} (input recommendation failed)")
        pipeline_results["ai_recommendation"] = False
    
    # Step 6: Tailored CV Generation (if AI recommendation was successful)
    if pipeline_results["ai_recommendation"]:
        try:
            logger.info(f"🎯 [PIPELINE] Starting tailored CV generation for {cname}")
            from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
            
            cv_service = CVTailoringService(user_email=user_email)
            
            # Check if we have the required files for CV tailoring
            from app.utils.user_path_utils import get_user_base_path
            base_dir = get_user_base_path(user_email)
            company_dir = base_dir / "applied_companies" / cname
            
            # Check for AI recommendation file
            ai_rec_file = None
            for pattern in [f"{cname}_ai_recommendation_*.json", f"{cname}_ai_recommendation.json"]:
                files = list(company_dir.glob(pattern))
                if files:
                    ai_rec_file = max(files, key=lambda f: f.stat().st_mtime)
                    break
            
            if ai_rec_file and ai_rec_file.exists():
                logger.info(f"📄 [PIPELINE] Found AI recommendation file: {ai_rec_file}")
                
                # The AI recommendation generator should have already triggered CV tailoring
                # Let's check if a tailored CV was created in the correct location
                tailored_cv_dir = base_dir / "cvs" / "tailored"
                tailored_cv_files = list(tailored_cv_dir.glob(f"{cname}_tailored_cv_*.txt"))
                if tailored_cv_files:
                    latest_tailored = max(tailored_cv_files, key=lambda f: f.stat().st_mtime)
                    logger.info(f"✅ [PIPELINE] Tailored CV found: {latest_tailored}")
                    pipeline_results["tailored_cv"] = True
                else:
                    logger.warning(f"⚠️ [PIPELINE] No tailored CV found for {cname}")
                    pipeline_results["tailored_cv"] = False
            else:
                logger.warning(f"⚠️ [PIPELINE] No AI recommendation file found for {cname}")
                pipeline_results["tailored_cv"] = False
        except Exception as cv_error:
            logger.error(f"❌ [PIPELINE] Tailored CV generation failed for {cname}: {cv_error}")
            pipeline_results["tailored_cv"] = False
    else:
        logger.info(f"⏭️ [PIPELINE] Skipping tailored CV generation for {cname} (AI recommendation failed)")
        pipeline_results["tailored_cv"] = False
    
    # Record JD usage NOW (at end of pipeline) so entire pipeline run uses consistent CV selection
    try:
        if 'jd_url_for_recording' in locals():
            from app.services.jd_usage_tracker import JDUsageTracker
            tracker = JDUsageTracker(user_email)
            tracker.record_jd_usage(jd_url_for_recording, jd_text_for_recording, cname, job_title_for_recording)
            logger.info(f"📝 [PIPELINE] JD usage recorded for {cname} (at end of pipeline)")
    except Exception as e:
        logger.warning(f"⚠️ [PIPELINE] Failed to record JD usage: {e}")
    
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
        company_name = _detect_most_recent_company(user_email)
        try:
            token_data = getattr(request, 'user', None)
        except Exception:
            token_data = None
        _schedule_post_skill_pipeline(company_name, token_data)
        
        # ALSO trigger job saving logic for the analyze endpoint
        try:
            import json
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
    current_model: str = "gpt-4o"  # Default model
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
        user_email = token_data.email
        
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
        
        # CRITICAL: If company looks like it was extracted from URL, look up the actual company from saved job_info
        if is_url_extracted_company(company) and jd_url:
            logger.info(f"🔍 Company '{company}' looks URL-extracted, looking up from saved job_info...")
            saved_company = await get_company_from_saved_job_info(jd_url, user_email)
            if saved_company:
                company = saved_company['company_slug']  # Use the slug for folder name
                logger.info(f"✅ Using saved company: {saved_company['company_name']} (slug: {company})")
            else:
                logger.warning(f"⚠️ Could not find saved company for JD URL, using provided: {company}")
        
        logger.info(f"🎯 Context-aware analysis request: Company={company}, JD={jd_url}, Rerun={is_rerun}")
        
        # Get CV selection context for user feedback using unified selector
        cv_context = get_cv_context_for_analysis(user_email, company, is_rerun)
        logger.info(f"📄 Using {cv_context.cv_type} CV v{cv_context.version} (Source: {cv_context.source})")
        
        # Get JD cache status for user feedback
        jd_cached = jd_cache_manager.should_reuse_jd_analysis(jd_url, company)
        cache_stats = jd_cache_manager.get_cache_stats(company)
        logger.info(f"🗄️ JD Cache status: {'Reusing cached data' if jd_cached else 'Fresh analysis'}")
        
        # Run the context-aware analysis pipeline
        try:
            # Create user-specific pipeline instance
            pipeline = ContextAwareAnalysisPipeline(user_email=user_email)
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


@router.post("/initial-analysis")
async def initial_analysis(
    request: Request,
    current_user: UserData = Depends(get_current_user)
):
    """
    Run initial analysis up to analyze match, then stop for user decision
    
    This endpoint performs:
    1. JD Analysis
    2. CV Skills Extraction
    3. CV-JD Matching
    4. Analyze Match (decision point)
    
    After analyze match, the process stops and returns results with analyze_match_decision.
    The frontend should display the decision and allow user to proceed or skip.
    
    Use /continue-full-analysis/{company} to continue with expensive steps.
    """
    import uuid
    correlation_id = str(uuid.uuid4())[:8]
    
    try:
        data = await request.json()
        
        # ⭐ CORRELATION ID TRACKING
        logger.info(f"🔗 [ANALYSIS_FLOW] START - Correlation ID: {correlation_id}")
        logger.info(f"🔗 [ANALYSIS_FLOW] Company: {data.get('company')}, JD URL: {data.get('jd_url')}")
        print(f"🔗 [ANALYSIS_FLOW] START - Correlation ID: {correlation_id}")
        
        # Extract parameters
        jd_url = data.get("jd_url")
        company = data.get("company")
        is_rerun = data.get("is_rerun", False)
        user_id = getattr(current_user, 'id', 1)
        user_email = current_user.email
        
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
        
        # CRITICAL: If company looks like it was extracted from URL, look up the actual company from saved job_info
        if is_url_extracted_company(company) and jd_url:
            logger.info(f"🔍 Company '{company}' looks URL-extracted, looking up from saved job_info...")
            saved_company = await get_company_from_saved_job_info(jd_url, user_email)
            if saved_company:
                company = saved_company['company_slug']  # Use the slug for folder name
                logger.info(f"✅ Using saved company: {saved_company['company_name']} (slug: {company})")
            else:
                logger.warning(f"⚠️ Could not find saved company for JD URL, using provided: {company}")
        
        logger.info(f"🎯 Initial analysis request: Company={company}, JD={jd_url}, Rerun={is_rerun}")
        
        # Run initial analysis pipeline (stops after analyze match)
        try:
            pipeline = ContextAwareAnalysisPipeline(user_email=current_user.email)
            results = await pipeline.run_initial_analysis(
                jd_url=jd_url,
                company=company,
                is_rerun=is_rerun,
                user_id=user_id
            )
        except Exception as e:
            logger.error(f"❌ Initial analysis error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
        
        if results.success:
            logger.info(f"✅ Initial analysis completed in {results.processing_time:.2f}s")
            logger.info(f"📊 Analyze match decision: {results.analyze_match_decision}")
            
            # Prepare response
            response_data = {
                "success": True,
                "company": company,  # CRITICAL: Return the corrected company name to frontend
                "requires_user_decision": results.requires_user_decision,
                "analyze_match_decision": results.analyze_match_decision,
                "processing_time": results.processing_time,
                "steps_completed": results.steps_completed,
                "steps_skipped": results.steps_skipped,
                "results": {
                    "cv_skills": results.cv_skills,
                    "jd_skills": results.jd_skills,
                    "jd_analysis": results.jd_analysis,
                    "job_info": results.job_info,
                    "cv_jd_matching": results.cv_jd_matching
                },
                "warnings": results.warnings,
                "errors": results.errors
            }
            
            return JSONResponse(content=response_data)
        else:
            logger.error(f"❌ Initial analysis failed: {results.errors}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "errors": results.errors,
                    "warnings": results.warnings
                }
            )
    
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else "Unknown error occurred"
        error_type = type(e).__name__
        traceback_info = traceback.format_exc()
        
        logger.error(f"❌ Initial analysis error ({error_type}): {error_msg}")
        logger.error(f"Traceback: {traceback_info}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Initial analysis failed ({error_type}): {error_msg}",
                "type": error_type
            }
        )


@router.post("/continue-full-analysis/{company}")
async def continue_full_analysis(
    company: str,
    request: Request,
    current_user: UserData = Depends(get_current_user)
):
    """
    Continue full analysis from analyze match point (expensive steps)
    
    This endpoint performs the expensive analysis steps that should only run
    after user confirms they want to proceed:
    1. Component Analysis
    2. ATS Recommendations
    3. AI Recommendations
    4. CV Tailoring (if requested)
    
    Args:
        company: Company name (from URL path)
        
    Request body (optional):
        include_tailoring: bool (default: True) - Whether to include CV tailoring
    """
    try:
        # Try to get request body, but handle empty body gracefully
        try:
            data = await request.json()
        except Exception:
            data = {}
        include_tailoring = data.get("include_tailoring", True)
        jd_url = data.get("jd_url", "")
        user_email = current_user.email
        
        logger.info(f"🚀 Continue full analysis request: Company={company}, IncludeTailoring={include_tailoring}")
        
        # CRITICAL: Resolve company name if it looks URL-extracted
        # This ensures we find files saved under the actual company name
        if is_url_extracted_company(company) and jd_url:
            logger.info(f"🔍 Company '{company}' looks URL-extracted, resolving to actual company name...")
            saved_company = await get_company_from_saved_job_info(jd_url, user_email)
            if saved_company:
                original_company = company
                company = saved_company['company_slug']
                logger.info(f"✅ Resolved {original_company} -> {company} ({saved_company['company_name']})")
            else:
                logger.warning(f"⚠️ Could not resolve company name, trying with provided: {company}")
        
        # Continue full analysis pipeline
        try:
            pipeline = ContextAwareAnalysisPipeline(user_email=user_email)
            results = await pipeline.continue_from_analyze_match(
                company=company,
                include_tailoring=include_tailoring
            )
        except Exception as e:
            logger.error(f"❌ Continue full analysis error: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
        
        if results.success:
            logger.info(f"✅ Full analysis continuation completed in {results.processing_time:.2f}s")
            
            # Prepare response
            response_data = {
                "success": True,
                "processing_time": results.processing_time,
                "steps_completed": results.steps_completed,
                "steps_skipped": results.steps_skipped,
                "results": {
                    "cv_skills": results.cv_skills,
                    "jd_skills": results.jd_skills,
                    "jd_analysis": results.jd_analysis,
                    "job_info": results.job_info,
                    "cv_jd_matching": results.cv_jd_matching,
                    "component_analysis": results.component_analysis,
                    "ats_recommendations": results.ats_recommendations,
                    "ai_recommendations": results.ai_recommendations,
                    "tailored_cv_path": results.tailored_cv_path
                },
                "warnings": results.warnings,
                "errors": results.errors
            }
            
            return JSONResponse(content=response_data)
        else:
            logger.error(f"❌ Full analysis continuation failed: {results.errors}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "errors": results.errors,
                    "warnings": results.warnings
                }
            )
    
    except Exception as e:
        import traceback
        error_msg = str(e) if str(e) else "Unknown error occurred"
        error_type = type(e).__name__
        traceback_info = traceback.format_exc()
        
        logger.error(f"❌ Continue full analysis error ({error_type}): {error_msg}")
        logger.error(f"Traceback: {traceback_info}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Continue full analysis failed ({error_type}): {error_msg}",
                "type": error_type
            }
        )


@router.post("/preliminary-analysis")
async def preliminary_analysis(
    request: Request,
    current_model: str = "gpt-4o"  # Default model
):
    """Preliminary skills analysis from CV filename and JD text"""
    try:
        logger.info(f"📱 [FRONTEND] POST /api/preliminary-analysis - Frontend starting analysis")
        
        # Verify authentication
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"📱 [FRONTEND] POST /api/preliminary-analysis - No auth header")
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
        
        # Create user object from token data
        from app.models.auth import UserData
        from datetime import timezone
        current_user = UserData(
            id=token_data.user_id,
            email=token_data.email,
            name=token_data.email.split("@")[0] if token_data.email else "user",
            created_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        data = await request.json()
        
        # Extract parameters
        cv_filename = data.get("cv_filename")
        jd_text = data.get("jd_text")
        jd_url = data.get("jd_url", "")  # NEW: Add URL parameter (optional)
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
        
        # Get user email first for company name extraction
        user_email = getattr(token_data, 'email', None)
        
        # Extract company name from JD text to validate required files
        # Use new version with URL support
        company_name, company_result = await _extract_company_name_from_jd_v2(
            jd_text, 
            jd_url=jd_url or "",  # Use provided URL or empty string
            user_email=user_email,
            user=current_user
        )

        # Log extraction details for monitoring
        print(f"Extracted company: {company_result.name} (confidence: {company_result.confidence.value})")
        logger.info(f"🏢 Extracted company name: {company_name}")
        
        # CRITICAL: Create company folder IMMEDIATELY after company name extraction
        # This ensures folder exists before any analysis files are saved
        from app.utils.user_path_utils import get_user_base_path
        try:
            base_dir = get_user_base_path(user_email)
            company_dir = base_dir / "applied_companies" / company_name
            
            # Create folder with explicit logging
            company_dir.mkdir(parents=True, exist_ok=True)
            
            # Verify folder was created successfully
            if company_dir.exists() and company_dir.is_dir():
                logger.info(f"✅ [FOLDER] Company folder created/verified: {company_dir}")
                logger.info(f"   📁 Full path: {company_dir.absolute()}")
            else:
                logger.error(f"❌ [FOLDER] Failed to create company folder: {company_dir}")
                raise Exception(f"Company folder creation failed: {company_dir}")
        except Exception as e:
            logger.error(f"❌ [FOLDER] Error creating company folder for '{company_name}': {e}")
            logger.error(f"   Base dir: {base_dir if 'base_dir' in locals() else 'unknown'}")
            raise Exception(f"Failed to create company folder: {str(e)}")
        
        # Validate required files exist before proceeding (non-blocking for preliminary flow)
        # In preliminary analysis, we can proceed even if JD hasn't been analyzed yet;
        # the route will save JD content and metadata shortly after.
        try:
            file_validation_error = _validate_required_analysis_files(company_name, user_email)
            if file_validation_error:
                logger.warning(f"⚠️ Proceeding without prior JD analysis: {file_validation_error}")
        except Exception as e:
            logger.warning(f"⚠️ Skipping pre-check due to error: {e}")
        
        # NEW: Always use unified latest-across-all CV (tailored or original by newest timestamp)
        from app.unified_latest_file_selector import get_selector_for_user
        try:
            # Create user-specific selector
            user_selector = get_selector_for_user(user_email)
            # Extract JD URL from latest job_info for this company (for JD usage tracking)
            jd_url_for_tracking = ""
            try:
                from app.utils.user_path_utils import get_user_base_path
                from pathlib import Path as _Path
                base_dir = get_user_base_path(user_email)
                company_dir = base_dir / "applied_companies" / company_name
                job_info_files = list(company_dir.glob("job_info_*.json"))
                if job_info_files:
                    latest_job_info = max(job_info_files, key=lambda f: f.stat().st_mtime)
                    import json as _json
                    with open(latest_job_info, 'r', encoding='utf-8') as _jf:
                        _job = _json.load(_jf)
                    jd_url_for_tracking = _job.get("job_url") or _job.get("url") or ""
                    if jd_url_for_tracking:
                        logger.info(f"🔗 [PRELIM_ANALYSIS] JD URL (latest job_info): {jd_url_for_tracking}")
            except Exception as _e:
                logger.debug(f"(debug) JD URL extraction skipped: {_e}")

            # CRITICAL FIX: Use get_latest_cv_for_company() which respects JD usage tracking
            # This ensures first-time JD usage always gets original CV
            cv_ctx = user_selector.get_latest_cv_for_company(company_name, jd_url_for_tracking, jd_text)
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
        
        # ⭐ CRITICAL: Process JD BEFORE analysis to ensure processed JD is available
        # This ensures the analysis uses the processed JD instead of the original
        if company_name and user_email:
            try:
                logger.info(f"🔄 [PRELIM_ANALYSIS] Processing JD BEFORE analysis for {company_name}")
                print(f"🔄 [PRELIM_ANALYSIS] Processing JD BEFORE analysis for {company_name}")
                from app.services.jd_processing_service import get_jd_processing_service
                
                # Get user object for processing
                try:
                    auth_header = request.headers.get("authorization")
                    if auth_header and auth_header.startswith("Bearer "):
                        token = auth_header.replace("Bearer ", "")
                        token_data = verify_token(token)
                        if token_data:
                            # Get user from database
                            from app.models.user import User
                            from app.database import get_database
                            from app.models.auth import UserData
                            from datetime import timezone
                            
                            user_record = None
                            for db in get_database():
                                user_record = db.query(User).filter(User.email == token_data.email).first()
                                break
                            
                            if user_record:
                                user = UserData(
                                    id=str(user_record.id),
                                    email=user_record.email,
                                    name=user_record.full_name or user_record.username or "User",
                                    created_at=user_record.created_at.replace(tzinfo=timezone.utc) if user_record.created_at.tzinfo is None else user_record.created_at,
                                    is_active=user_record.is_active
                                )
                                
                                # Extract job title from JD if available
                                job_title = None
                                try:
                                    from app.services.job_extractor import extract_job_metadata
                                    job_metadata = await extract_job_metadata(jd_text)
                                    job_title = job_metadata.get('job_title') if job_metadata else None
                                except Exception:
                                    pass
                                
                                # Process JD NOW (before analysis) - REQUIRED, no fallback
                                jd_service = get_jd_processing_service(user.email)
                                logger.info(f"🔄 [PRELIM_ANALYSIS] Triggering JD processing BEFORE analysis for {company_name} | "
                                           f"JD length: {len(jd_text)} chars")
                                print(f"🔄 [PRELIM_ANALYSIS] Triggering JD processing BEFORE analysis for {company_name}")
                                
                                processed_result = await jd_service.process_jd_if_needed(
                                    company_name=company_name,
                                    jd_text=jd_text,
                                    job_title=job_title,
                                    job_url=jd_url,
                                    user=user
                                )
                                
                                # CRITICAL: Verify processed JD was created successfully
                                if not processed_result:
                                    error_msg = (
                                        f"❌ [PRELIM_ANALYSIS] CRITICAL ERROR: JD processing failed for {company_name}. "
                                        f"Processed JD is REQUIRED for skills analysis."
                                    )
                                    logger.error(error_msg)
                                    raise ValueError(
                                        f"JD processing failed for company '{company_name}'. "
                                        f"Processed JD is required for skills analysis."
                                    )
                                
                                # Verify processed JD file exists
                                if not jd_service.has_processed_jd(company_name):
                                    error_msg = (
                                        f"❌ [PRELIM_ANALYSIS] CRITICAL ERROR: Processed JD file not found after processing for {company_name}"
                                    )
                                    logger.error(error_msg)
                                    raise FileNotFoundError(
                                        f"Processed JD file not found for company '{company_name}' after processing. "
                                        f"Please retry the analysis."
                                    )
                                
                                logger.info(f"✅ [PRELIM_ANALYSIS] JD processing completed successfully for {company_name} | "
                                           f"Processed JD verified and ready")
                                print(f"✅ [PRELIM_ANALYSIS] JD processing completed successfully for {company_name}")
                            else:
                                error_msg = f"❌ [PRELIM_ANALYSIS] CRITICAL ERROR: User record not found for {token_data.email}"
                                logger.error(error_msg)
                                raise ValueError(f"User record not found. Cannot process JD for skills analysis.")
                except Exception as proc_err:
                    import traceback
                    error_msg = (
                        f"❌ [PRELIM_ANALYSIS] CRITICAL ERROR: Failed to process JD BEFORE analysis for {company_name}: {proc_err}"
                    )
                    logger.error(error_msg)
                    logger.error(f"❌ [PRELIM_ANALYSIS] Traceback: {traceback.format_exc()}")
                    raise ValueError(
                        f"JD processing failed for company '{company_name}': {str(proc_err)}. "
                        f"Processed JD is required for skills analysis."
                    )
            except Exception as e:
                import traceback
                error_msg = (
                    f"❌ [PRELIM_ANALYSIS] CRITICAL ERROR: JD processing setup failed BEFORE analysis for {company_name}: {e}"
                )
                logger.error(error_msg)
                logger.error(f"❌ [PRELIM_ANALYSIS] Traceback: {traceback.format_exc()}")
                raise ValueError(
                    f"JD processing setup failed for company '{company_name}': {str(e)}. "
                    f"Processed JD is required for skills analysis."
                )
        
        # Perform skills analysis with configuration
        # Now processed JD should be available and will be used automatically
        result = await perform_preliminary_skills_analysis(
            cv_content=cv_content,
            jd_text=jd_text,
            cv_filename=cv_filename,
            current_model="gpt-4o",
            config_name=config_name,
            user_id=user_id,
            user_email=user_email,
            current_user=current_user,
            company_name=company_name  # Pass company name for processed JD lookup
        )
        # Attach resolved company to result so frontend can poll consistently (no extra calls)
        try:
            if company_name:
                result["company"] = company_name
        except Exception:
            pass
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
                company_name = _detect_most_recent_company(user_email)
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
                
                # Ensure folder exists with explicit logging
                try:
                    company_dir.mkdir(parents=True, exist_ok=True)
                    if company_dir.exists() and company_dir.is_dir():
                        logger.info(f"✅ [FOLDER] Pipeline: Company folder verified: {company_dir}")
                    else:
                        logger.error(f"❌ [FOLDER] Pipeline: Company folder verification failed: {company_dir}")
                except Exception as e:
                    logger.error(f"❌ [FOLDER] Pipeline: Error creating company folder: {e}")
                    # Don't silently continue - this is critical for pipeline
                    raise Exception(f"Failed to create company folder for pipeline: {str(e)}")

            # Save JD content and job info to files
            try:
                import json
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
                    job_title = job_metadata.get('job_title') if job_metadata else None
                    if job_metadata:
                        # Save with timestamped, company-specific filename
                        job_info_file = company_dir / f"job_info_{company_name}_{timestamp}.json"
                        with open(job_info_file, 'w', encoding='utf-8') as f:
                            json.dump(job_metadata, f, indent=2, ensure_ascii=False)
                        logger.info(f"💾 [PIPELINE] Job info saved to: {job_info_file}")
                else:
                    logger.info(f"♻️ [PIPELINE] (preliminary-analysis) JD file already exists: {existing_jd}")
                    # Load job_title from existing job_info if available
                    job_title = None
                    try:
                        job_info_files = list(company_dir.glob("job_info_*.json"))
                        if job_info_files:
                            latest_job_info = max(job_info_files, key=lambda f: f.stat().st_mtime)
                            with open(latest_job_info, 'r', encoding='utf-8') as f:
                                job_metadata = json.load(f)
                                job_title = job_metadata.get('job_title')
                    except Exception:
                        pass
                
                # ⭐ ALWAYS try to process JD if not already processed (even if jd_original exists)
                # This ensures processed JD is created for existing JDs too
                try:
                    logger.info(f"🔍 [JD_PROCESSING] Checking if processed JD needed for {company_name}")
                    from app.services.jd_processing_service import get_jd_processing_service
                    
                    # Get user object for processing
                    try:
                        auth_header = request.headers.get("authorization")
                        if auth_header and auth_header.startswith("Bearer "):
                            token = auth_header.replace("Bearer ", "")
                            token_data = verify_token(token)
                            if token_data:
                                # Get user from database
                                from app.models.user import User
                                from app.database import get_database
                                from app.models.auth import UserData
                                from datetime import timezone
                                
                                user_record = None
                                for db in get_database():
                                    user_record = db.query(User).filter(User.email == token_data.email).first()
                                    break
                                
                                if user_record:
                                    user = UserData(
                                        id=str(user_record.id),
                                        email=user_record.email,
                                        name=user_record.full_name or user_record.username or "User",
                                        created_at=user_record.created_at.replace(tzinfo=timezone.utc) if user_record.created_at.tzinfo is None else user_record.created_at,
                                        is_active=user_record.is_active
                                    )
                                    
                                    # Get JD text from file if jd_text is empty
                                    jd_text_for_processing = jd_text or ""
                                    if not jd_text_for_processing and existing_jd:
                                        try:
                                            with open(existing_jd, 'r', encoding='utf-8') as f:
                                                jd_data = json.load(f)
                                                jd_text_for_processing = jd_data.get('text', '')
                                        except Exception:
                                            pass
                                    
                                    if jd_text_for_processing:
                                        jd_service = get_jd_processing_service(user.email)
                                        logger.info(f"🔄 [JD_PROCESSING] Triggering JD processing for {company_name} | "
                                                   f"JD length: {len(jd_text_for_processing)} chars")
                                        await jd_service.process_jd_if_needed(
                                            company_name=company_name,
                                            jd_text=jd_text_for_processing,
                                            job_title=job_title,
                                            job_url=jd_url,
                                            user=user
                                        )
                                        logger.info(f"✅ [JD_PROCESSING] JD processing completed for {company_name}")
                                    else:
                                        logger.warning(f"⚠️ [JD_PROCESSING] No JD text available for processing {company_name}")
                                else:
                                    logger.warning(f"⚠️ [JD_PROCESSING] User record not found for {token_data.email}")
                            else:
                                logger.warning(f"⚠️ [JD_PROCESSING] Invalid token data")
                        else:
                            logger.warning(f"⚠️ [JD_PROCESSING] No authorization header found")
                    except Exception as proc_err:
                        import traceback
                        logger.error(f"❌ [JD_PROCESSING] Failed to process JD for {company_name}: {proc_err}")
                        logger.error(f"❌ [JD_PROCESSING] Traceback: {traceback.format_exc()}")
                        # Don't fail the request - processing is optional
                except Exception as e:
                    import traceback
                    logger.error(f"❌ [JD_PROCESSING] JD processing setup failed for {company_name}: {e}")
                    logger.error(f"❌ [JD_PROCESSING] Traceback: {traceback.format_exc()}")
                    # Continue without processing - fallback to original JD will work
                
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

                # Ensure CV file exists for the matcher - use unified CV selection
                try:
                    import json
                    # Use unified selector instead of missing dynamic_cv_selector
                    from app.unified_latest_file_selector import get_selector_for_user
                    user_selector = get_selector_for_user(user_email)
                    cv_context = user_selector.get_latest_cv_across_all(company_name)
                    cv_file = Path(cv_context.json_path) if cv_context and cv_context.json_path else None
                    
                    logger.info(f"📄 [PIPELINE] Using unified CV: {cv_file} from {cv_context.file_type if cv_context else 'unknown'} folder")
                    
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
            _schedule_post_skill_pipeline(company_name, token_data)
        except Exception as e:
            logger.warning(f"⚠️ [PIPELINE] (preliminary-analysis) failed to schedule: {e}")
        
        # Log successful completion
        logger.info(f"📱 [FRONTEND] POST /api/preliminary-analysis - Analysis completed successfully")
        logger.info(f"   Company: {company_name or 'Unknown'}")
        logger.info(f"   CV Skills: {len(result.get('cv_skills', {}).get('technical_skills', []))}")
        logger.info(f"   JD Skills: {len(result.get('jd_skills', {}).get('technical_skills', []))}")
        
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
async def get_cv_context(
    company: str, 
    is_rerun: bool = False, 
    jd_url: Optional[str] = None,
    current_user: UserData = Depends(get_current_user)
):
    """Get CV selection context for UI feedback"""
    try:
        user_email = current_user.email
        original_company = company  # Save original for logging
        
        # CRITICAL: If company looks like it was extracted from URL, look up the actual company from saved job_info
        if is_url_extracted_company(company):
            if jd_url:
                # Try to find by JD URL first (most accurate)
                logger.info(f"🔍 [CV_CONTEXT] Company '{company}' looks URL-extracted, looking up from saved job_info by JD URL...")
                saved_company = await get_company_from_saved_job_info(jd_url, user_email)
                if saved_company:
                    company = saved_company['company_slug']  # Use the slug for folder name
                    logger.info(f"✅ [CV_CONTEXT] Using saved company: {saved_company['company_name']} (slug: {company})")
                else:
                    logger.warning(f"⚠️ [CV_CONTEXT] Could not find saved company for JD URL, trying fallback...")
                    # Fallback: use most recent company folder
                    recent_company = await _get_most_recent_company_folder(user_email)
                    if recent_company:
                        company = recent_company
                        logger.info(f"✅ [CV_CONTEXT] Using most recent company folder: {company}")
            else:
                # No JD URL provided - use most recent company folder as fallback
                logger.info(f"🔍 [CV_CONTEXT] Company '{company}' looks URL-extracted but no JD URL, using most recent company folder...")
                recent_company = await _get_most_recent_company_folder(user_email)
                if recent_company:
                    company = recent_company
                    logger.info(f"✅ [CV_CONTEXT] Using most recent company folder: {company}")
        
        # Get CV selection context using unified selector
        cv_context = get_cv_context_for_analysis(user_email, company, is_rerun)
        
        # Get available CV versions using unified selector
        available_versions = list_available_cv_versions(user_email, company)
        
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
        
        from app.services.ats.modular_ats_orchestrator import get_modular_ats_orchestrator
        from app.services.dynamic_cv_selector import dynamic_cv_selector
        
        # Use dynamic CV selection for the latest CV file
        latest_cv_paths = dynamic_cv_selector.get_latest_cv_paths_for_services()
        logger.info(f"🔧 [MANUAL] Using dynamic CV: {latest_cv_paths['json_source']} folder")
        
        # Check if required files exist
        from app.utils.user_path_utils import get_user_base_path
        user_email = current_user.email
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
        user_orchestrator = get_modular_ats_orchestrator(user_email=user_email)
        result = await user_orchestrator.run_component_analysis(company)
        
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

            saved_jobs_file = get_user_base_path(current_user.email) / "saved_jobs" / "saved_jobs.json"
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
            job_info_file = get_user_base_path(current_user.email) / "applied_companies" / company / "job_info.json"
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
            base_dir = get_user_base_path(current_user.email)
            await analyze_and_save_company_jd(company, force_refresh=True, base_path=str(base_dir))
            results["steps"].append({"step": "jd_analysis", "status": "success"})
        except Exception as e:
            logger.error(f"❌ [MANUAL] JD Analysis failed: {e}")
            results["steps"].append({"step": "jd_analysis", "status": "failed", "error": str(e)})
            
        # Step 2: CV-JD Matching
        try:
            logger.info(f"🔧 [MANUAL] Step 2: CV-JD Matching for {company}")
            await match_and_save_cv_jd(company, cv_file_path=None, force_refresh=True, user_email=current_user.email)
            results["steps"].append({"step": "cv_jd_matching", "status": "success"})
        except Exception as e:
            logger.error(f"❌ [MANUAL] CV-JD Matching failed: {e}")
            results["steps"].append({"step": "cv_jd_matching", "status": "failed", "error": str(e)})
            
        # Step 3: Component Analysis (includes ATS calculation)
        try:
            logger.info(f"🔧 [MANUAL] Step 3: Component Analysis for {company}")
            from app.services.ats.modular_ats_orchestrator import get_modular_ats_orchestrator
            user_orchestrator = get_modular_ats_orchestrator(user_email=current_user.email)
            component_result = await user_orchestrator.run_component_analysis(company)
            
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
        logger.info(f"📱 [FRONTEND] GET /api/analysis-results/{company} - Frontend polling for ATS data")
        
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
        
        # ⭐ CRITICAL FIX: Resolve URL-extracted company names to actual company names
        # This was the bug that caused 404 errors - company passed as 'www_ethicaljobs_com_au'
        # but files are saved under actual company name like 'Australia_for_UNHCR'
        original_company = company
        if is_url_extracted_company(company):
            logger.info(f"🔍 [ANALYSIS_RESULTS] Company '{company}' looks URL-extracted, searching for actual company name...")
            # Search through all job_info files to find matching URL-extracted slug
            applied_root = base_dir / "applied_companies"
            if applied_root.exists():
                from urllib.parse import urlparse
                for company_folder in applied_root.iterdir():
                    if not company_folder.is_dir():
                        continue
                    # Check job_info files for matching URL that would produce this URL-extracted name
                    job_info_files = list(company_folder.glob("job_info*.json"))
                    for job_info_file in job_info_files:
                        try:
                            with open(job_info_file, 'r', encoding='utf-8') as f:
                                job_info = json.load(f)
                            
                            # Get stored URL
                            extracted_info = job_info.get('extracted_info', {})
                            saved_url = (job_info.get('jd_url') or 
                                        job_info.get('job_url') or 
                                        extracted_info.get('jd_url') or 
                                        extracted_info.get('job_url'))
                            
                            if saved_url:
                                # Convert stored URL to URL-extracted format for comparison
                                try:
                                    parsed = urlparse(saved_url)
                                    domain = parsed.netloc.replace('.', '_').replace('-', '_').lower()
                                    if domain and domain == company.lower():
                                        company = company_folder.name
                                        logger.info(f"✅ [ANALYSIS_RESULTS] Resolved '{original_company}' -> '{company}' (matched JD URL domain)")
                                        break
                                except Exception:
                                    pass
                        except Exception as e:
                            logger.debug(f"Could not read job_info from {job_info_file}: {e}")
                            continue
                    else:
                        continue  # Only continue if inner loop didn't break
                    break  # Break outer loop if inner loop broke
            
            if company == original_company:
                logger.warning(f"⚠️ [ANALYSIS_RESULTS] Could not resolve URL-extracted company '{company}', using as-is")
        
        # Normalize company param to match on-disk slug
        def _normalize_company_dir(base, name: str):
            # Try exact
            candidate = base / "applied_companies" / name
            if candidate.exists():
                return candidate, name
            # Try space ↔ underscore variants
            variants = {
                name.replace(" ", "_"),
                name.replace("_", " "),
            }
            for v in variants:
                cand = base / "applied_companies" / v
                if cand.exists():
                    return cand, v
            # Case-insensitive scan of directories
            applied_root = base / "applied_companies"
            try:
                if applied_root.exists():
                    lower_target_variants = {
                        name.lower(),
                        name.replace(" ", "_").lower(),
                        name.replace("_", " ").lower(),
                    }
                    for d in applied_root.iterdir():
                        if not d.is_dir():
                            continue
                        dn = d.name
                        if dn.lower() in lower_target_variants:
                            return d, dn
            except Exception:
                pass
            # Fallback to original (may not exist; caller will handle 404)
            return base / "applied_companies" / name, name
        
        company_dir, resolved_company = _normalize_company_dir(base_dir, company)
        # Debug: which directories/files are used
        try:
            path_debug.start_operation("get_analysis_results")
            path_debug.log_path(base_dir, "User base dir")
            path_debug.log_path(company_dir, "Company dir")
        except Exception:
            pass
        
        # Use timestamped analysis file with fallback
        from app.utils.timestamp_utils import TimestampUtils
        analysis_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{resolved_company}_skills_analysis", "json")
        if not analysis_file:
            analysis_file = company_dir / f"{resolved_company}_skills_analysis.json"
        
        if not analysis_file.exists():
            try:
                path_debug._log(f"❌ Analysis file not found in {company_dir}")
                path_debug.end_operation()
            except Exception:
                pass
            return JSONResponse(
                status_code=404,
                content={"error": f"No analysis found for company: {company}"}
            )
        
        # Read analysis data
        try:
            path_debug.log_path(analysis_file, "Using analysis file")
        except Exception:
            pass
        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        try:
            path_debug._log(f"✅ Loaded analysis file, size: {analysis_file.stat().st_size} bytes")
            path_debug.end_operation()
        except Exception:
            pass
        
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
            "company": resolved_company,
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
        ai_recommendation_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{resolved_company}_ai_recommendation", "json")
        if not ai_recommendation_file:
            # Try input_recommendation pattern
            ai_recommendation_file = TimestampUtils.find_latest_timestamped_file(company_dir, f"{resolved_company}_input_recommendation", "json")
        if not ai_recommendation_file:
            # Try non-timestamped files
            ai_recommendation_file = company_dir / f"{resolved_company}_ai_recommendation.json"
        if not ai_recommendation_file.exists():
            ai_recommendation_file = company_dir / f"{resolved_company}_input_recommendation.json"
        
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
        tailored_cv_dir = company_dir
        tailored_cv_file = TimestampUtils.find_latest_timestamped_file(tailored_cv_dir, f"{resolved_company}_tailored_cv", "json")
        
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
    user_id: int = 1,
    user_email: str = None,
    current_user: Any = None,
    company_name: Optional[str] = None  # NEW: Optional company name for processed JD lookup
) -> dict:
    """Perform preliminary skills analysis between CV and JD using AI prompts with detailed output"""
    try:
        # ⭐ ENTRY LOGGING
        logger.info(f"🎯 [SKILLS_ANALYSIS] ENTRY - Called for company: {company_name}")
        logger.info(f"🎯 [SKILLS_ANALYSIS] ENTRY - CV filename: {cv_filename}, JD length: {len(jd_text)} chars")
        print(f"🎯 [SKILLS_ANALYSIS] ENTRY - Called for company: {company_name}")
        # ⭐ STRICT: MUST use processed JD - NO FALLBACK, raise error if not available
        import time
        import asyncio
        jd_load_start = time.time()
        original_length = len(jd_text)
        
        # CRITICAL: company_name and user_email are REQUIRED for processed JD
        if not company_name:
            error_msg = f"❌ [SKILLS_ANALYSIS] CRITICAL ERROR: company_name is REQUIRED for processed JD lookup"
            logger.error(error_msg)
            raise ValueError("company_name is required for skills analysis. Processed JD cannot be loaded without company name.")
        
        if not user_email:
            error_msg = f"❌ [SKILLS_ANALYSIS] CRITICAL ERROR: user_email is REQUIRED for processed JD lookup"
            logger.error(error_msg)
            raise ValueError("user_email is required for skills analysis. Processed JD cannot be loaded without user email.")
        
        # Get processed JD service
        from app.services.jd_processing_service import get_jd_processing_service
        jd_service = get_jd_processing_service(user_email)
        
        # Wait up to 3 seconds for processed JD to be created (in case it's still being processed)
        logger.info(f"🔍 [SKILLS_ANALYSIS] Waiting for processed JD for {company_name} | "
                   f"Original JD length: {original_length} chars")
        processed_jd_text = None
        max_wait_seconds = 3
        wait_interval = 0.5
        attempts = int(max_wait_seconds / wait_interval)
        
        for attempt in range(attempts):
            has_processed = jd_service.has_processed_jd(company_name)
            if has_processed:
                processed_jd_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
                if processed_jd_text and len(processed_jd_text.strip()) > 0:
                    break
            if attempt < attempts - 1:
                logger.debug(f"⏳ [SKILLS_ANALYSIS] Processed JD not ready yet, waiting... (attempt {attempt + 1}/{attempts})")
                await asyncio.sleep(wait_interval)
        
        jd_load_time = (time.time() - jd_load_start) * 1000  # Convert to ms
        
        # STRICT: Raise error if processed JD is not available
        if not processed_jd_text or len(processed_jd_text.strip()) == 0:
            error_msg = (
                f"❌ [SKILLS_ANALYSIS] CRITICAL ERROR: Processed JD is REQUIRED but not available for {company_name} | "
                f"Processed JD exists: {jd_service.has_processed_jd(company_name)} | "
                f"Wait time: {max_wait_seconds}s | "
                f"Load time: {jd_load_time:.1f}ms"
            )
            logger.error(error_msg)
            raise FileNotFoundError(
                f"Processed JD is required for skills analysis but not found for company '{company_name}'. "
                f"Please ensure JD processing completed successfully before running skills analysis."
            )
        
        # Use processed JD (guaranteed to exist at this point)
        jd_text = processed_jd_text
        reduction = original_length - len(jd_text)
        reduction_pct = round((reduction / original_length) * 100, 1) if original_length > 0 else 0
        
        # Verify processed JD format (should have sections, not raw text)
        has_sections = any(section in jd_text for section in [
            "ROLE OVERVIEW", "KEY RESPONSIBILITIES", "TECHNICAL REQUIREMENTS"
        ])
        jd_preview = jd_text[:300].replace('\n', ' ')
        
        logger.info(f"✅ [SKILLS_ANALYSIS] ✅✅✅ USING PROCESSED JD for {company_name} | "
                   f"Original: {original_length} chars → Processed: {len(jd_text)} chars | "
                   f"Reduction: {reduction} chars ({reduction_pct}%) | "
                   f"Load time: {jd_load_time:.1f}ms | "
                   f"Has sections format: {has_sections}")
        logger.info(f"📄 [SKILLS_ANALYSIS] Processed JD preview (first 300 chars): {jd_preview}")
        
        # ⭐ PRINT FULL PROCESSED JD TEXT BEING SENT TO AI FOR SKILLS ANALYSIS
        logger.info(f"📋 [SKILLS_ANALYSIS] ========== FULL PROCESSED JD TEXT FOR SKILLS EXTRACTION ==========")
        logger.info(f"📋 [SKILLS_ANALYSIS] Company: {company_name}")
        logger.info(f"📋 [SKILLS_ANALYSIS] Total length: {len(jd_text)} characters")
        logger.info(f"📋 [SKILLS_ANALYSIS] This processed JD text will be sent to AI for skills extraction:")
        logger.info(f"📋 [SKILLS_ANALYSIS] Full processed JD text:\n{jd_text}")
        logger.info(f"📋 [SKILLS_ANALYSIS] ========== END OF PROCESSED JD TEXT FOR SKILLS ANALYSIS ==========")
        print(f"✅ [SKILLS_ANALYSIS] ✅✅✅ USING PROCESSED JD for {company_name} | "
              f"Original: {original_length} chars → Processed: {len(jd_text)} chars | "
              f"Reduction: {reduction} chars ({reduction_pct}%) | "
              f"Has sections: {has_sections}")
        print(f"📋 [SKILLS_ANALYSIS] FULL PROCESSED JD TEXT FOR SKILLS EXTRACTION ({len(jd_text)} chars):\n{jd_text}")
        
        # Get configuration
        config = skills_analysis_config_service.get_config(config_name)
        ai_params = skills_analysis_config_service.get_ai_parameters(config_name)
        logging_params = skills_analysis_config_service.get_logging_parameters(config_name)
        prompt_params = skills_analysis_config_service.get_prompt_parameters(config_name)
        
        # Check if using optimized prompts (cost-efficient mode)
        use_optimized = prompt_params.get("use_optimized_prompts", False)
        prompt_version = prompt_params.get("prompt_version", "verbose")
        
        if logging_params["enable_detailed_logging"]:
            logger.info(f"🔍 [SKILLS_ANALYSIS] Starting AI-powered skills analysis for {cv_filename}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] CV content length: {len(cv_content)} chars")
            logger.info(f"🔍 [SKILLS_ANALYSIS] JD content length: {len(jd_text)} chars | "
                       f"Source: PROCESSED (REQUIRED) | "
                       f"Original was: {original_length} chars")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Using config: {config_name or 'default'}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Prompt version: {prompt_version} (optimized={use_optimized})")
            logger.info(f"✅✅✅ [SKILLS_ANALYSIS] CONFIRMED: Using PROCESSED JD for skills extraction (REQUIRED)")
            # Lightweight CV content preview to aid debugging
            try:
                _cv_preview = (cv_content or "")[:180].replace('\n', ' ')
                logger.info(f"🧪 [SKILLS_ANALYSIS] CV preview: '{_cv_preview}'")
            except Exception:
                pass
        
        # Get AI service instance
        from app.ai.ai_service import ai_service
        
        # Initialize AI service for the current user
        if current_user:
            ai_service.initialize_for_user(current_user)
        
        # Log current AI service status
        current_status = ai_service.get_current_status()
        if logging_params["enable_detailed_logging"]:
            logger.info(f"🔍 [SKILLS_ANALYSIS] Current AI provider: {current_status.get('current_provider')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Current AI model: {current_status.get('current_model')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Provider available: {current_status.get('provider_available')}")
            logger.info(f"🔍 [SKILLS_ANALYSIS] Model from header: {current_model}")
        
        # Extract CV skills using appropriate prompt version
        if logging_params["enable_detailed_logging"]:
            logger.info(f"🔍 [SKILLS_ANALYSIS] Extracting CV skills with {prompt_version} prompt...")
        
        # Use unified prompt getter for both verbose and optimized modes
        if use_optimized:
            cv_prompts = get_skill_prompts("CV", cv_content, use_optimized=True)
            cv_structured_prompt = cv_prompts["user_prompt"]
            cv_system_prompt = cv_prompts["system_prompt"]
            cv_max_tokens = cv_prompts["expected_max_tokens"]
        else:
            cv_structured_prompt = get_skill_prompt('combined_structured', text=cv_content, document_type="CV")
            cv_system_prompt = None  # Use default from ai_service
            cv_max_tokens = ai_params["max_tokens"]
        
        # Use configuration parameters
        cv_structured_response = await ai_service.generate_response(
            prompt=cv_structured_prompt,
            system_prompt=cv_system_prompt if use_optimized else None,
            user=current_user,
            temperature=ai_params["temperature"],
            max_tokens=cv_max_tokens
        )
        cv_raw_response = cv_structured_response.content
        
        # Parse the structured response using appropriate parser
        cv_parser = SkillExtractionParser()
        if use_optimized:
            cv_parsed = cv_parser.parse_optimized_response(cv_raw_response, "CV")
        else:
            cv_parsed = cv_parser.parse_response(cv_raw_response, "CV")
        cv_technical_skills = cv_parsed.get('technical_skills', [])
        cv_soft_skills = cv_parsed.get('soft_skills', [])
        cv_domain_keywords = cv_parsed.get('domain_keywords', [])

        # Do NOT fallback or abort on minimal CVs; proceed and surface warnings + suggestions
        cv_minimal = False
        try:
            total_cv_items = len(cv_technical_skills) + len(cv_soft_skills) + len(cv_domain_keywords)
            # Consider minimal if no items or very few technical skills (< 5)
            if total_cv_items == 0 or len(cv_technical_skills) < 5:
                cv_minimal = True
                logger.warning("⚠️ [SKILLS_ANALYSIS] CV content appears minimal (tech=%d, soft=%d, domain=%d) — continuing without fallback",
                               len(cv_technical_skills), len(cv_soft_skills), len(cv_domain_keywords))
        except Exception:
            pass
        
        # Extract JD skills using enhanced structured prompt
        # ⭐ ADD JD LOGGING: Log JD text before skills extraction
        logger.info(f"📋 [SKILLS_ANALYSIS] ========== JD TEXT FOR SKILLS EXTRACTION ==========")
        logger.info(f"📋 [SKILLS_ANALYSIS] JD Source: PROCESSED")
        logger.info(f"📋 [SKILLS_ANALYSIS] JD Length: {len(jd_text)} chars")
        logger.info(f"📋 [SKILLS_ANALYSIS] JD Preview: {jd_text[:200]}...")
        logger.info(f"📋 [SKILLS_ANALYSIS] ========== END JD TEXT ==========")
        
        if logging_params["enable_detailed_logging"]:
            logger.info(f"🔍 [SKILLS_ANALYSIS] Extracting JD skills with {prompt_version} prompt...")
        
        # Use unified prompt getter for both verbose and optimized modes
        if use_optimized:
            jd_prompts = get_skill_prompts("Job Description", jd_text, use_optimized=True)
            jd_structured_prompt = jd_prompts["user_prompt"]
            jd_system_prompt = jd_prompts["system_prompt"]
            jd_max_tokens = jd_prompts["expected_max_tokens"]
        else:
            jd_structured_prompt = get_skill_prompt('combined_structured', text=jd_text, document_type="Job Description")
            jd_system_prompt = None
            jd_max_tokens = ai_params["max_tokens"]
        
        # Use configuration parameters
        jd_structured_response = await ai_service.generate_response(
            prompt=jd_structured_prompt,
            system_prompt=jd_system_prompt if use_optimized else None,
            user=current_user,
            temperature=ai_params["temperature"],
            max_tokens=jd_max_tokens
        )
        jd_raw_response = jd_structured_response.content
        
        # Parse the structured response using appropriate parser
        jd_parser = SkillExtractionParser()
        if use_optimized:
            jd_parsed = jd_parser.parse_optimized_response(jd_raw_response, "JD")
        else:
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

        # Attach a minimal-CV warning and suggestions without aborting
        if cv_minimal:
            try:
                result.setdefault("warnings", [])
                result["warnings"].append({
                    "type": "cv_minimal",
                    "message": "Your CV appears minimal. We continued the analysis without fallback. Consider enriching the tailored CV with more role-relevant content.",
                })
                # Provide quick actionable suggestions for tailored CV
                improvement_suggestions = {
                    "add_technical": ["SQL", "Power BI", "Python", "Excel", "Data Analysis", "Business Intelligence"],
                    "add_evidence": [
                        "Quantify outcomes for dashboards and analytics (e.g., +30% efficiency)",
                        "Mention data sizes, model counts, and automations",
                        "Reference BI/reporting artifacts delivered"
                    ],
                    "add_domain": ["Fundraising", "Humanitarian Aid", "Donor-Centricity"],
                }
                result.setdefault("suggestions", {})["cv_enrichment"] = improvement_suggestions
            except Exception:
                pass
        
        if logging_params["enable_detailed_logging"]:
            logger.info(f"✅ [SKILLS_ANALYSIS] Analysis completed successfully")
        
        # ⭐ EXIT LOGGING (before return)
        logger.info(f"🎯 [SKILLS_ANALYSIS] EXIT - Completed skills analysis for {company_name}")
        print(f"🎯 [SKILLS_ANALYSIS] EXIT - Completed skills analysis for {company_name}")
        
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
            current_date = datetime.now().strftime('%Y-%m-%d')
            analyze_match_prompt = get_skill_prompt('analyze_match', cv_text=cv_content, job_text=jd_text, current_date=current_date)
            
            # Generate AI response for analyze match
            analyze_match_response = await ai_service.generate_response(
                prompt=analyze_match_prompt,
                user=current_user,
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
                    # Use new version with URL support
                    company_name, company_result = await _extract_company_name_from_jd_v2(
                        jd_text, 
                        jd_url=jd_url or "",  # Use provided URL or empty string
                        user_email=user_email,
                        user=current_user
                    )

                    # Log extraction details for monitoring
                    print(f"Extracted company: {company_result.name} (confidence: {company_result.confidence.value})")
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
                user=current_user,
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
