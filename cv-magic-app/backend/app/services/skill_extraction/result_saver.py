"""
Result Saver for Skill Extraction

Handles saving skill extraction results to organized file structure
"""

import os
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from app.core.model_dependency import get_request_model
from app.utils.timestamp_utils import TimestampUtils

logger = logging.getLogger(__name__)


class SkillExtractionResultSaver:
    """Service for saving skill extraction results to organized files"""
    
    def __init__(self, user_email: str):
        from app.utils.user_path_utils import get_user_base_path, get_user_company_analysis_paths
        self.user_email = user_email
        self.base_dir = get_user_base_path(user_email)
        self.paths = lambda company_name: get_user_company_analysis_paths(user_email, company_name)
        # Ensure required directories exist
        for directory in [self.base_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Result saver initialized with base directory: {self.base_dir}")
    
    def save_analysis_results(
        self,
        cv_skills: Dict,
        jd_skills: Dict,
        jd_url: str,
        cv_filename: str,
        user_id: int,
        cv_data: Optional[Dict] = None,
        jd_data: Optional[Dict] = None,
        company_name: Optional[str] = None,
        cv_comprehensive_analysis: Optional[str] = None,
        jd_comprehensive_analysis: Optional[str] = None
    ) -> str:
        """
        Save skill extraction results to organized file structure
        
        Args:
            cv_skills: CV skill extraction results
            jd_skills: JD skill extraction results  
            jd_url: Job description URL
            cv_filename: CV filename
            user_id: User ID
            cv_data: Optional CV data containing text content
            jd_data: Optional JD data containing text content and metadata
            company_name: Optional direct company name to use (if provided, skips extraction)
            
        Returns:
            Path to saved file
        """
        try:
            # Use direct company name if provided, otherwise extract from JD data/URL/skills
            if company_name:
                # Use the provided company name and ensure it's a proper slug
                company_slug = self._create_company_slug(company_name)
                # Check if folder exists and use exact folder name if found
                if self.base_dir.exists():
                    existing_folders = [f.name for f in self.base_dir.iterdir() if f.is_dir()]
                    for folder in existing_folders:
                        if folder.lower() == company_slug.lower():
                            company_slug = folder
                            break
                logger.info(f"🏢 Using provided company name: {company_name} -> {company_slug}")
            else:
            # Use JD data company name or extract from URL/skills
                if jd_data and isinstance(jd_data, dict) and jd_data.get('company_name'):
                    company_slug = self._create_company_slug(jd_data['company_name'])
                    logger.info(f"🏢 Using company name from JD data: {jd_data['company_name']} -> {company_slug}")
                else:
                    company_slug = self._extract_company_name(jd_skills, jd_url, jd_data)
            
            # Create company folder under applied_companies subfolder
            company_folder = self.base_dir / "applied_companies" / company_slug
            company_folder.mkdir(parents=True, exist_ok=True)
            
            # Ensure all required directories exist
            from app.utils.user_path_utils import ensure_user_directories
            ensure_user_directories(self.user_email)
            
            # Save original CV JSON in cvs/original directory if it doesn't exist or doesn't have structured data
            if cv_data and cv_data.get('text'):
                import json
                from app.utils.user_path_utils import get_user_cv_paths
                cv_paths = get_user_cv_paths(self.user_email)
                cv_file_path = cv_paths["original"] / "original_cv.json"
                should_save = True
                
                if cv_file_path.exists():
                    try:
                        with open(cv_file_path, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                        # If file has structured CV data (not just text), don't overwrite it
                        if isinstance(existing_data, dict) and any(key in existing_data for key in ['personal_information', 'career_profile', 'skills', 'education', 'experience']):
                            logger.info(f"💾 Structured CV already exists, preserving it: {cv_file_path}")
                            should_save = False
                        else:
                            logger.info(f"💾 Simple CV exists, will replace with text version: {cv_file_path}")
                    except:
                        # If we can't read the file, we'll save the simple version
                        logger.info(f"💾 Could not read existing CV file, will replace: {cv_file_path}")
                        pass
                
                if should_save:
                    cv_json = {
                        "filename": cv_filename,
                        "user_id": user_id,
                        "extracted_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "length_chars": len(cv_data['text']),
                        "text": cv_data['text']
                    }
                    with open(cv_file_path, 'w', encoding='utf-8') as f:
                        json.dump(cv_json, f, ensure_ascii=False, indent=2)
                    logger.info(f"💾 CV JSON saved to: {cv_file_path}")
                else:
                    logger.info(f"💾 Structured CV preserved, skipping save: {cv_file_path}")
            
            # Skip JD content saving during skills analysis - it's already saved separately
            
            # Generate skill analysis JSON filename with company slug and timestamp
            import json
            timestamp = TimestampUtils.get_timestamp()
            filename = f"{company_slug}_skills_analysis_{timestamp}.json"
            file_path = company_folder / filename
            
            # Clean cv_skills and jd_skills by removing raw_response
            clean_cv_skills = {k: v for k, v in cv_skills.items() if k != "raw_response"}
            clean_jd_skills = {k: v for k, v in jd_skills.items() if k != "raw_response"}
            
            # Get the current model used for this request
            current_model = get_request_model() or "unknown"
            
            # Build structured JSON payload
            payload = {
                "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                "cv_filename": cv_filename,
                "jd_url": jd_url,
                "user_id": user_id,
                "company": company_slug,
                "model_used": current_model,  # Track which model was used
                "cv_skills": clean_cv_skills,
                "jd_skills": clean_jd_skills,
                "cv_comprehensive_analysis": cv_comprehensive_analysis,
                "jd_comprehensive_analysis": jd_comprehensive_analysis,
                "analyze_match_entries": [],
                "preextracted_comparison_entries": []
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Analysis results saved (JSON) to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save analysis results: {str(e)}")
            raise Exception(f"Result saving error: {str(e)}")
    
    def _extract_company_name(self, jd_skills: Dict, jd_url: str, jd_data: Optional[Dict] = None) -> str:
        """
        Extract company name from JD content or URL with improved logic for any company
        
        Args:
            jd_skills: JD skill extraction results
            jd_url: Job description URL
            
        Returns:
            Company slug suitable for folder name (matching existing cv-analysis folders)
        """
        company_name = "Unknown_Company"
        
        try:
            # Prefer company name from JD record if available
            if jd_data and jd_data.get('record') and getattr(jd_data['record'], 'company', None):
                company_from_record = jd_data['record'].company
                if company_from_record and company_from_record.strip().lower() not in ["unknown", "null", "none", ""]:
                    company_slug = self._create_company_slug(company_from_record)
                    logger.info(f"🏢 Using company from JD record: {company_from_record} -> {company_slug}")
                    return company_slug
            
            # Get existing folders for matching
            existing_folders = []
            if self.base_dir.exists():
                existing_folders = [f.name for f in self.base_dir.iterdir() if f.is_dir()]
            
            # STEP 1: Try to extract from URL first (improved for any job site)
            if jd_url and jd_url != "preliminary_analysis" and jd_url.startswith("http"):
                url_company = self._extract_company_from_url(jd_url)
                if url_company and url_company != "Unknown_Company":
                    # Check if this matches any existing folder
                    for folder in existing_folders:
                        if self._names_match(url_company, folder):
                            logger.info(f"🏢 Found matching existing folder: {folder} for URL company: {url_company}")
                            return folder
                    company_name = url_company
                    logger.info(f"🏢 Extracted company from URL: {company_name}")
            
            # STEP 2: Try to extract from JD raw response if URL extraction failed
            raw_response = jd_skills.get('raw_response', '')
            if raw_response and company_name == "Unknown_Company":
                jd_company = self._extract_company_from_jd_text(raw_response)
                if jd_company and jd_company != "Unknown_Company":
                    # Check if this matches any existing folder
                    for folder in existing_folders:
                        if self._names_match(jd_company, folder):
                            logger.info(f"🏢 Found matching existing folder: {folder} for JD company: {jd_company}")
                            return folder
                    company_name = jd_company
                    logger.info(f"🏢 Extracted company from JD content: {company_name}")
            
            # Clean company name for folder use
            company_slug = self._create_company_slug(company_name)
            
            # Check if this slug matches any existing folder
            for folder in existing_folders:
                if folder.lower() == company_slug.lower():
                    logger.info(f"🏢 Using existing folder: {folder}")
                    return folder
            
            return company_slug
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract company name: {e}, using 'Unknown_Company'")
            return "Unknown_Company"
    
    def _extract_company_from_url(self, jd_url: str) -> str:
        """Extract company name from various job site URL patterns"""
        try:
            # EthicalJobs pattern: https://ethicaljobs.com.au/members/company-name/job/12345
            if "ethicaljobs.com.au/members/" in jd_url:
                match = re.search(r'/members/([^/]+)/', jd_url)
                if match:
                    return match.group(1).replace('-', ' ').title()
            
            # Seek pattern: https://www.seek.com.au/company/company-name/jobs
            if "seek.com.au/company/" in jd_url:
                match = re.search(r'/company/([^/]+)/', jd_url)
                if match:
                    return match.group(1).replace('-', ' ').title()
            
            # Indeed pattern: https://au.indeed.com/company/company-name/jobs
            if "indeed.com/company/" in jd_url:
                match = re.search(r'/company/([^/]+)/', jd_url)
                if match:
                    return match.group(1).replace('-', ' ').title()
            
            # LinkedIn pattern: https://www.linkedin.com/company/company-name/
            if "linkedin.com/company/" in jd_url:
                match = re.search(r'/company/([^/]+)/', jd_url)
                if match:
                    return match.group(1).replace('-', ' ').title()
            
            # Glassdoor pattern: https://www.glassdoor.com/Overview/Working-at-Company-Name-EI_IE123456.11,25.htm
            if "glassdoor.com" in jd_url and "Working-at-" in jd_url:
                match = re.search(r'Working-at-([^-]+)', jd_url)
                if match:
                    return match.group(1).replace('-', ' ').title()
            
            # Generic domain-based extraction: extract from subdomain or path
            # Example: https://company-name.com/careers or https://careers.company-name.com
            if jd_url.count('.') >= 2:
                # Try subdomain extraction (e.g., careers.netflix.com -> netflix)
                subdomain_match = re.search(r'https?://([^.]+)\.', jd_url)
                if subdomain_match:
                    subdomain = subdomain_match.group(1)
                    if subdomain not in ['www', 'careers', 'jobs', 'work']:
                        return subdomain.replace('-', ' ').title()
                
                # Try path-based extraction for company sites (e.g., company-name.com/careers -> company-name)
                path_match = re.search(r'https?://[^/]+/([^/]+)/', jd_url)
                if path_match:
                    path_part = path_match.group(1)
                    if path_part not in ['careers', 'jobs', 'work', 'about']:
                        return path_part.replace('-', ' ').title()
                
                # Try domain name extraction (e.g., company-name.com -> company-name)
                domain_match = re.search(r'https?://(?:www\.)?([^.]+)\.', jd_url)
                if domain_match:
                    domain = domain_match.group(1)
                    if domain not in ['www', 'careers', 'jobs', 'work']:
                        return domain.replace('-', ' ').title()
            
            return "Unknown_Company"
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract company from URL: {e}")
            return "Unknown_Company"
    
    def _extract_company_from_jd_text(self, jd_text: str) -> str:
        """Extract company name from JD text content using improved patterns"""
        try:
            # Enhanced patterns for company name extraction
            patterns = [
                # Company heritage/establishment patterns
                r'For\s+over\s+\d+\s+years,\s+([A-Z][a-zA-Z\s&.-]+?)\s+has\s+been',
                r'In\s+\d+,\s+([A-Z][a-zA-Z\s&.-]+?)\s+combined\s+with',
                
                # Brand/division patterns (prioritize parent company)
                r'Drive\s+is\s+([A-Z][a-zA-Z\s&.-]+?)\'s\s+brand',
                r'([A-Z][a-zA-Z\s&.-]+?)\s+Entertainment',
                r'wholly\s+owned\s+by\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s+with|\s+is|\s+offers|$)',
                r'Australia\'s\s+largest\s+media\s+organisation,\s+([A-Z][a-zA-Z\s&.-]+?)(?:\s+with|\s+is|\s+offers|$)',
                
                # About us/company patterns
                r'About\s+us\s+at\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
                r'About\s+us\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
                r'About\s+the\s+company\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
                r'About\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
                
                # Job title patterns
                r'([A-Z][a-zA-Z\s&.-]+?)\s+Job\s+Summary',
                r'([A-Z][a-zA-Z\s&.-]+?)\s+Applications\s+close',
                r'([A-Z][a-zA-Z\s&.-]+?)\s+is\s+hiring',
                r'([A-Z][a-zA-Z\s&.-]+?)\s+is\s+seeking',
                
                # Header patterns
                r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+Job\s+Summary',
                r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+Applications\s+close',
                r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+is\s+hiring',
                
                # Contact/address patterns
                r'([A-Z][a-zA-Z\s&.-]+?)\s+is\s+an\s+equal\s+opportunity',
                r'([A-Z][a-zA-Z\s&.-]+?)\s+is\s+committed\s+to',
                r'([A-Z][a-zA-Z\s&.-]+?)\s+offers\s+competitive',
                
                # Specific company patterns
                r'The Glen Centre',
                r'Glen Centre',
                r'UNHCR',
                r'Australia for UNHCR',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, jd_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    if 'Glen' in pattern:
                        extracted_name = "The Glen Group"
                    elif 'UNHCR' in pattern:
                        extracted_name = "Australia for UNHCR"
                    else:
                        extracted_name = match.group(1).strip()
                    
                    # Clean up the extracted name
                    extracted_name = self._clean_company_name(extracted_name)
                    
                    if extracted_name and len(extracted_name) > 2:
                        logger.debug(f"🏢 Extracted company from JD text: {extracted_name}")
                        return extracted_name
            
            return "Unknown_Company"
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract company from JD text: {e}")
            return "Unknown_Company"
    
    def _clean_company_name(self, name: str) -> str:
        """Clean and validate extracted company name"""
        if not name:
            return "Unknown_Company"
        
        # Remove common prefixes/suffixes
        name = re.sub(r'^(The|A|An)\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(Pty|Ltd|Inc|Corp|LLC|GmbH|AG|SA|S\.A\.|Limited|Corporation)\.?$', '', name, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Validate length and content
        if len(name) < 2 or len(name) > 100:
            return "Unknown_Company"
        
        # Check if it's mostly letters and common punctuation
        if not re.match(r'^[A-Za-z\s&.-]+$', name):
            return "Unknown_Company"
        
        return name
    
    def _names_match(self, name1: str, name2: str) -> bool:
        """Check if two company names are similar enough to be the same company"""
        if not name1 or not name2:
            return False
        
        # Normalize names for comparison
        norm1 = re.sub(r'[^\w\s]', '', name1.lower())
        norm2 = re.sub(r'[^\w\s]', '', name2.lower())
        
        # Check for exact match
        if norm1 == norm2:
            return True
        
        # Check if one name contains the other
        if norm1 in norm2 or norm2 in norm1:
            return True
        
        # Check for significant word overlap (at least 2 words in common)
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        common_words = words1.intersection(words2)
        
        # Remove common words that don't help identify the company
        common_words.discard('the')
        common_words.discard('and')
        common_words.discard('of')
        common_words.discard('for')
        common_words.discard('in')
        common_words.discard('at')
        
        return len(common_words) >= 2
    
    def _create_company_slug(self, company_name: str) -> str:
        """
        Create a safe company slug for folder names (same logic as JobExtractionService)
        
        Args:
            company_name: Raw company name
            
        Returns:
            Cleaned company slug suitable for folder names
        """
        if not company_name or company_name.lower() in ['unknown', 'null', '']:
            return "Unknown_Company"
        
        # Remove special characters except alphanumeric, spaces, &, ., -
        company_slug = re.sub(r'[^\w\s&.-]', '', company_name)
        # Replace spaces with underscores
        company_slug = re.sub(r'\s+', '_', company_slug)
        # Remove leading/trailing underscores
        company_slug = company_slug.strip('_')
        # Truncate if too long (max 50 characters)
        if len(company_slug) > 50:
            company_slug = company_slug[:50]
        
        return company_slug
    
    def _clean_company_name(self, company_name: str) -> str:
        """
        Clean company name to be suitable for folder name
        
        Args:
            company_name: Raw company name
            
        Returns:
            Cleaned company name
        """
        if not company_name or company_name.strip() == "":
            return "Unknown"
        
        # Remove special characters and replace spaces with underscores
        cleaned = re.sub(r'[<>:"/\\|?*]', '', company_name)  # Remove invalid filename chars
        cleaned = re.sub(r'\s+', '_', cleaned.strip())  # Replace spaces with underscores
        cleaned = re.sub(r'_+', '_', cleaned)  # Remove multiple consecutive underscores
        cleaned = cleaned.strip('_')  # Remove leading/trailing underscores
        
        # Limit length
        if len(cleaned) > 50:
            cleaned = cleaned[:50].rstrip('_')
        
        # Ensure not empty after cleaning
        if not cleaned:
            cleaned = "Unknown"
        
        return cleaned
    
    def _generate_analysis_content(
        self,
        cv_skills: Dict,
        jd_skills: Dict,
        cv_filename: str,
        jd_url: str,
        user_id: int
    ) -> str:
        """
        Generate the complete analysis content for saving
        
        Args:
            cv_skills: CV skill extraction results
            jd_skills: JD skill extraction results
            cv_filename: CV filename
            jd_url: Job description URL
            user_id: User ID
            
        Returns:
            Formatted content string
        """
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        
        content = []
        
        # Add header
        content.append("=" * 80)
        content.append("SKILL EXTRACTION ANALYSIS RESULTS")
        content.append("=" * 80)
        content.append(f"Generated: {timestamp}")
        content.append(f"CV File: {cv_filename}")
        content.append(f"JD URL: {jd_url}")
        content.append(f"User ID: {user_id}")
        content.append("=" * 80)
        content.append("")
        
        # Add CV Analysis
        if 'raw_response' in cv_skills:
            content.append("=" * 80)
            content.append(f"[{timestamp}] [CV_CLAUDE_ANALYSIS] OUTPUT:")
            content.append(cv_skills['raw_response'])
            content.append("=" * 80)
            content.append("")
        
        # Add JD Analysis
        if 'raw_response' in jd_skills:
            content.append("=" * 80)
            content.append(f"[{timestamp}] [JD_CLAUDE_ANALYSIS] OUTPUT:")
            content.append(jd_skills['raw_response'])
            content.append("=" * 80)
            content.append("")
        
        # Add Summary
        content.append("=" * 80)
        content.append("EXTRACTION SUMMARY")
        content.append("=" * 80)
        content.append("")
        
        # CV Summary
        content.append("CV SKILLS EXTRACTED:")
        content.append(f"  Soft Skills ({len(cv_skills.get('soft_skills', []))}): {cv_skills.get('soft_skills', [])}")
        content.append(f"  Technical Skills ({len(cv_skills.get('technical_skills', []))}): {cv_skills.get('technical_skills', [])}")
        content.append(f"  Domain Keywords ({len(cv_skills.get('domain_keywords', []))}): {cv_skills.get('domain_keywords', [])}")
        content.append("")
        
        # JD Summary
        content.append("JD REQUIREMENTS EXTRACTED:")
        content.append(f"  Soft Skills ({len(jd_skills.get('soft_skills', []))}): {jd_skills.get('soft_skills', [])}")
        content.append(f"  Technical Skills ({len(jd_skills.get('technical_skills', []))}): {jd_skills.get('technical_skills', [])}")
        content.append(f"  Domain Keywords ({len(jd_skills.get('domain_keywords', []))}): {jd_skills.get('domain_keywords', [])}")
        content.append("")
        
        # Add caching info
        cv_cached = cv_skills.get('from_cache', False)
        jd_cached = jd_skills.get('from_cache', False)
        content.append("CACHING STATUS:")
        content.append(f"  CV Skills: {'Cached' if cv_cached else 'Fresh Analysis'}")
        content.append(f"  JD Skills: {'Cached' if jd_cached else 'Fresh Analysis'}")
        content.append("")
        
        content.append("=" * 80)
        content.append("END OF ANALYSIS")
        content.append("=" * 80)
        
        return "\n".join(content)
    
    def list_saved_analyses(self, company_name: Optional[str] = None) -> Dict:
        """
        List saved analysis files
        
        Args:
            company_name: Optional company name to filter by
            
        Returns:
            Dictionary with analysis files information
        """
        try:
            result = {
                "companies": [],
                "total_files": 0
            }
            
            if company_name:
                # List files for specific company
                company_folder = self.base_dir / "applied_companies" / self._clean_company_name(company_name)
                if company_folder.exists():
                    # Look for timestamped JSON skills analysis files
                    files = TimestampUtils.find_all_timestamped_files(company_folder, f"{company_name}_skills_analysis", "json")
                    result["companies"].append({
                        "name": company_name,
                        "folder": str(company_folder),
                        "files": [str(f) for f in files],
                        "count": len(files)
                    })
                    result["total_files"] = len(files)
            else:
                # List all companies and their files
                if self.base_dir.exists():
                    for company_folder in self.base_dir.iterdir():
                        if company_folder.is_dir():
                            # Look for timestamped JSON skills analysis files
                            files = TimestampUtils.find_all_timestamped_files(company_folder, f"{company_folder.name}_skills_analysis", "json")
                            result["companies"].append({
                                "name": company_folder.name,
                                "folder": str(company_folder),
                                "files": [str(f) for f in files],
                                "count": len(files)
                            })
                            result["total_files"] += len(files)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to list saved analyses: {str(e)}")
            return {"companies": [], "total_files": 0, "error": str(e)}

    def append_analyze_match(self, raw_analysis: str, company_name: str) -> str:
        """
        Append analyze match output to the existing log file
        
        Args:
            raw_analysis: The raw analyze match analysis text
            company_name: Company name for file path
            
        Returns:
            str: Path to the updated file
            
        Raises:
            ValueError: If company name is invalid
        """        
        # Ensure company name is provided and valid
        if not company_name or company_name == "Unknown_Company":
            raise ValueError("Valid company name must be provided for saving analyze match")
            
        # Clean and validate company name 
        from app.utils.user_path_utils import validate_company_name, get_user_company_analysis_paths
        validate_company_name(company_name)
        
        try:
            # Get correct paths using user path utils
            paths = get_user_company_analysis_paths(self.user_email, company_name)
            timestamp = TimestampUtils.get_timestamp()
            skills_file = paths["skills_analysis"](timestamp)
            skills_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create company folder path
            company_folder = self.base_dir / "applied_companies" / company_name
            
            # First try to find an existing analysis file
            import json
            file_path = None
            
            # Look for existing analysis file with exact company name
            exact_name_pattern = f"{company_name}_skills_analysis_*.json"
            matching_files = list(company_folder.glob(exact_name_pattern))
            if matching_files:
                # Sort by modification time to get the latest
                file_path = sorted(matching_files, key=lambda f: f.stat().st_mtime, reverse=True)[0]
                logger.info(f"📂 Found existing analysis file: {file_path}")
            
            # If no file found, try timestamped file search
            if not file_path:
                file_path = TimestampUtils.find_latest_timestamped_file(company_folder, f"{company_name}_skills_analysis", "json")
                if file_path:
                    logger.info(f"📂 Found timestamped analysis file: {file_path}")
            
            # If no timestamped file exists, create a new one
            if not file_path:
                timestamp = TimestampUtils.get_timestamp()
                filename = f"{company_name}_skills_analysis_{timestamp}.json"
                file_path = company_folder / filename
            
            # Ensure directory exists
            company_folder.mkdir(parents=True, exist_ok=True)
            
            # Debug logging
            logger.info(f"🔍 Looking for analysis file in: {company_folder}")
            if file_path:
                logger.info(f"📄 Using existing file: {file_path}")
            else:
                logger.info("❌ No existing file found, will create new")
            
            # Append analyze match output to the JSON file
            try:
                data = {}
                if file_path and file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = {
                        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                        "cv_filename": None,
                        "jd_url": None,
                        "user_id": None,
                        "company": company_name,
                        "cv_skills": {},
                        "jd_skills": {},
                        "analyze_match_entries": [],
                        "preextracted_comparison_entries": []
                    }
                if "analyze_match_entries" not in data:
                    data["analyze_match_entries"] = []
                from datetime import datetime as _dt
                current_model = get_request_model() or "unknown"
                data["analyze_match_entries"].append({
                    "timestamp": _dt.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
                    "model_used": current_model,
                    "content": raw_analysis
                })
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"⚠️ Failed to append analyze match to JSON: {e}")
            
            logger.info(f"📁 [ANALYZE_MATCH] Results appended to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to append analyze match: {str(e)}")
            raise e

    def append_preextracted_comparison(self, raw_analysis: str, company_name: str, saved_file_path: Optional[str] = None) -> str:
        """
        Append pre-extracted skills comparison output to the existing log file.
        Mirrors the analyze-match append behavior to keep a single consolidated log.
        
        Args:
            raw_analysis: The raw formatted comparison text
            company_name: Company name for file path
            saved_file_path: Optional path to an existing file to append to
        
        Returns:
            str: Path to the updated file
        """
        try:
            # Try to infer company from saved_file_path first (most reliable)
            company_slug = None
            if saved_file_path:
                try:
                    p = Path(saved_file_path)
                    # Expect structure: cv-analysis/applied_companies/<Company>/<Company>_skills_analysis.json
                    if p.parent and p.parent.name:
                        company_slug = p.parent.name
                        logger.info(f"🏢 [PREEXTRACTED_COMPARISON] Inferred company from saved_file_path: {company_slug}")
                except Exception:
                    pass

            # Fallback to provided company name
            if not company_slug:
                company_slug = self._create_company_slug(company_name)
            if self.base_dir.exists():
                existing_folders = [f.name for f in self.base_dir.iterdir() if f.is_dir()]
                for folder in existing_folders:
                    if folder.lower() == company_slug.lower():
                        company_slug = folder
                        break
            company_folder = self.base_dir / "applied_companies" / company_slug
            import json
            
            # Find the latest timestamped skills analysis file
            file_path = TimestampUtils.find_latest_timestamped_file(company_folder, f"{company_slug}_skills_analysis", "json")
            
            # If no timestamped file exists, create a new one
            if not file_path:
                timestamp = TimestampUtils.get_timestamp()
                filename = f"{company_slug}_skills_analysis_{timestamp}.json"
                file_path = company_folder / filename
            company_folder.mkdir(parents=True, exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

            try:
                data = {}
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = {
                        "generated": timestamp,
                        "cv_filename": None,
                        "jd_url": None,
                        "user_id": None,
                        "company": company_slug,
                        "cv_skills": {},
                        "jd_skills": {},
                        "analyze_match_entries": [],
                        "preextracted_comparison_entries": []
                    }
                if "preextracted_comparison_entries" not in data:
                    data["preextracted_comparison_entries"] = []
                current_model = get_request_model() or "unknown"
                data["preextracted_comparison_entries"].append({
                    "timestamp": timestamp,
                    "model_used": current_model,
                    "content": raw_analysis
                })
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.warning(f"⚠️ Failed to append preextracted comparison to JSON: {e}")

            logger.info(f"📁 [PREEXTRACTED_COMPARISON] Results appended to: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"❌ Failed to append pre-extracted skills comparison: {str(e)}")
            raise e



# Global instance
# Global instance - will be initialized with proper user email when needed
result_saver = None
