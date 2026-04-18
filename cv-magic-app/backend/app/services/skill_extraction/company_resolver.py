"""
Company name resolution helpers for skills analysis.

Responsible for extracting, cleaning and matching company names from JD text
against existing user folder structures.
"""
import logging
import re
from typing import Optional
from pathlib import Path

from app.utils.user_path_utils import get_user_base_path
from app.utils.timestamp_utils import TimestampUtils

logger = logging.getLogger(__name__)


async def extract_company_name_from_jd(jd_text: str, user_email: str) -> str:
    """Extract company name from job description text using AI with fallback to existing folders."""
    try:
        from app.services.job_extractor import extract_job_metadata
        metadata = await extract_job_metadata(jd_text)

        if metadata and metadata.get("company"):
            ai_company_name = metadata["company"].strip()
            ai_company_name = re.sub(r'^(?i)(organisation_|organization_|company_|org_)', '', ai_company_name)
            ai_company_name = re.sub(r'[^\w\s-]', '', ai_company_name)
            ai_company_name = re.sub(r'\s+', '_', ai_company_name)
            if len(ai_company_name) > 50:
                ai_company_name = ai_company_name[:50]

            existing = find_matching_company_folder(ai_company_name, user_email)
            if existing:
                logger.info(f"Found matching company folder: {existing}")
                return existing
            return ai_company_name

        # Regex fallback patterns
        patterns = [
            r'Australia\s+for\s+UNHCR',
            r'([A-Z][a-zA-Z\s&.-]+?)\s+logo',
            r'About\s+([A-Z][a-zA-Z\s&.-]{3,20}?)\s+is',
            r'([A-Z][a-zA-Z\s&.-]{3,20}?)\s+is\s+(?:Australia\'s|the)',
            r'Working\s+at\s+([A-Z][a-zA-Z\s&.-]{3,20}?),',
        ]
        for pattern in patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                company_name = match.group(1).strip() if match.lastindex else match.group(0).strip()
                company_name = re.sub(r'[^\w\s-]', '', company_name)
                company_name = re.sub(r'\s+', '_', company_name)
                existing = find_matching_company_folder(company_name, user_email)
                if existing:
                    logger.info(f"Found matching company folder: {existing}")
                    return existing
                return company_name

        existing = find_company_in_existing_folders(jd_text, user_email)
        if existing:
            logger.info(f"Found company in existing folders: {existing}")
            return existing

        return "Unknown_Company"

    except Exception as e:
        logger.warning(f"Failed to extract company name: {e}")
        return "Unknown_Company"


def find_matching_company_folder(extracted_name: str, user_email: str) -> Optional[str]:
    """Return the folder name that best matches *extracted_name*, or None."""
    try:
        base = get_user_base_path(user_email)
        if not base.exists():
            return None
        extracted_lower = extracted_name.lower()
        for folder in base.iterdir():
            if folder.is_dir() and folder.name != "cvs":
                folder_lower = folder.name.lower()
                if folder_lower == extracted_lower or extracted_lower in folder_lower or folder_lower in extracted_lower:
                    return folder.name
        return None
    except Exception as e:
        logger.warning(f"Error finding matching company folder: {e}")
        return None


def find_company_in_existing_folders(jd_text: str, user_email: str) -> Optional[str]:
    """Find a company by checking if any existing folder name appears in the JD text."""
    try:
        base = get_user_base_path(user_email)
        if not base.exists():
            return None
        jd_lower = jd_text.lower()
        for folder in base.iterdir():
            if folder.is_dir() and folder.name != "cvs":
                folder_readable = folder.name.replace('_', ' ').lower()
                if folder_readable in jd_lower:
                    return folder.name
                words = folder_readable.split()
                if len(words) >= 2:
                    matches = sum(1 for w in words if w in jd_lower and len(w) > 3)
                    if matches >= 2:
                        return folder.name
        return None
    except Exception as e:
        logger.warning(f"Error finding company in existing folders: {e}")
        return None


def validate_required_analysis_files(company_name: str, user_email: Optional[str] = None) -> Optional[str]:
    """Return an error message if required analysis files are missing, else None."""
    try:
        if not user_email:
            raise ValueError("User authentication required for file operations")
        base_path = get_user_base_path(user_email) / "applied_companies" / company_name

        jd_file = TimestampUtils.find_latest_timestamped_file(base_path, "jd_original", "json") \
                  or base_path / "jd_original.json"
        job_info_file = TimestampUtils.find_latest_timestamped_file(base_path, f"job_info_{company_name}", "json") \
                        or base_path / f"job_info_{company_name}.json"

        missing = []
        if not jd_file.exists():
            missing.append("jd_original.json")
        if not job_info_file.exists():
            missing.append(f"job_info_{company_name}.json")

        if missing:
            return "Please analyze the job description first before running skills analysis."
        return None
    except Exception as e:
        logger.error(f"Error validating required files: {e}")
        return f"Error validating required files: {e}"


def detect_most_recent_company(user_email: str) -> Optional[str]:
    """Return the most recently modified company folder that has job/JD files, or None."""
    try:
        base = get_user_base_path(user_email)
        if not base.exists():
            return None
        candidates = []
        for d in base.iterdir():
            if d.is_dir() and d.name != "Unknown_Company":
                has_job_info = TimestampUtils.find_latest_timestamped_file(d, "job_info", "json") \
                               or list(d.glob("job_info_*.json"))
                has_jd = TimestampUtils.find_latest_timestamped_file(d, "jd_original", "json") \
                         or (d / "jd_original.json").exists()
                if has_job_info or has_jd:
                    candidates.append(d)
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime).name
    except Exception:
        return None


def extract_match_rates_from_content(content: str) -> dict:
    """Parse category match rates out of a preextracted comparison text block."""
    rates = {"technical_skills": 0, "soft_skills": 0, "domain_keywords": 0, "overall": 0}
    try:
        overall_match = re.search(r"Match Rate:\s*(\d+(?:\.\d+)?)%", content)
        if overall_match:
            rates["overall"] = int(float(overall_match.group(1)))

        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "Category" in line and "Match Rate" in line:
                for j in range(i + 1, min(i + 10, len(lines))):
                    parts = [p.strip() for p in lines[j].strip().split()]
                    if len(parts) >= 6:
                        try:
                            category = parts[0].lower()
                            rate = float(parts[-1]) if parts[-1].replace('.', '').isdigit() else 0
                            if "technical" in category:
                                rates["technical_skills"] = int(rate)
                            elif "soft" in category:
                                rates["soft_skills"] = int(rate)
                            elif "domain" in category:
                                rates["domain_keywords"] = int(rate)
                        except Exception:
                            pass

        # Legacy format fallbacks
        for key, pattern in [
            ("technical_skills", r"Technical Skills Match Rate:\s*(\d+)%"),
            ("soft_skills", r"Soft Skills Match Rate:\s*(\d+)%"),
            ("domain_keywords", r"Domain Keywords Match Rate:\s*(\d+)%"),
        ]:
            if rates[key] == 0:
                m = re.search(pattern, content)
                if m:
                    rates[key] = int(m.group(1))

        if rates["overall"] == 0 and any(rates[k] for k in ["technical_skills", "soft_skills", "domain_keywords"]):
            rates["overall"] = int((rates["technical_skills"] + rates["soft_skills"] + rates["domain_keywords"]) / 3)
    except Exception as e:
        logger.warning(f"Failed to extract match rates: {e}")
    return rates
