"""
Result Saver for Skill Extraction

Handles saving skill extraction results to organized file structure
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SkillExtractionResultSaver:
    """Service for saving skill extraction results to organized files"""
    
    def __init__(self, base_dir: str = "cv-analysis"):
        self.base_dir = Path(base_dir)
        # Ensure base directory exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Result saver initialized with base directory: {self.base_dir}")
    
    def save_analysis_results(
        self,
        cv_skills: Dict,
        jd_skills: Dict,
        jd_url: str,
        cv_filename: str,
        user_id: int,
        cv_data: Optional[Dict] = None,
        jd_data: Optional[Dict] = None
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
            
        Returns:
            Path to saved file
        """
        try:
            # Extract company name from JD data when available (preferred), otherwise from URL/skills
            company_name = self._extract_company_name(jd_skills, jd_url, jd_data)
            
            # Create company folder
            company_folder = self.base_dir / company_name
            company_folder.mkdir(parents=True, exist_ok=True)
            
            # Save original CV text file in root cv-analysis directory (not in company folder)
            if cv_data and cv_data.get('text'):
                cv_file_path = self.base_dir / "original_cv.txt"
                with open(cv_file_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write("ORIGINAL CV TEXT\n")
                    f.write(f"Filename: {cv_filename}\n")
                    f.write(f"User ID: {user_id}\n")
                    f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(cv_data['text'])} characters\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(cv_data['text'])
                logger.info(f"💾 CV text saved to: {cv_file_path}")
            
            # Save JD original text file if provided and not already existing
            jd_original_path = company_folder / "jd_original.txt"
            if jd_data and jd_data.get('text') and not jd_original_path.exists():
                with open(jd_original_path, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write("ORIGINAL JOB DESCRIPTION\n")
                    f.write(f"URL: {jd_url}\n")
                    f.write(f"User ID: {user_id}\n")
                    f.write(f"Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Length: {len(jd_data['text'])} characters\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(jd_data['text'])
                logger.info(f"💾 JD text saved to: {jd_original_path}")
            
            # Save JD metadata JSON file if provided and not already existing
            jd_json_path = company_folder / f"job_info_{company_name}.json"
            if jd_data and jd_data.get('record') and not jd_json_path.exists():
                jd_record = jd_data['record']
                job_info = {
                    "company_name": jd_record.company or "Unknown",
                    "job_title": jd_record.job_title or "Unknown",
                    "job_url": jd_url,
                    "user_id": user_id,
                    "application_date": jd_record.application_date.isoformat() if jd_record.application_date else None,
                    "status": jd_record.status or "analyzing",
                    "extracted_at": datetime.now().isoformat(),
                    "notes": jd_record.notes
                }
                
                with open(jd_json_path, 'w', encoding='utf-8') as f:
                    json.dump(job_info, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 JD metadata saved to: {jd_json_path}")
            
            # Generate skill analysis log filename (no numbers as requested)
            filename = "log_output.txt"
            file_path = company_folder / filename
            
            # Generate skill analysis content
            content = self._generate_analysis_content(cv_skills, jd_skills, cv_filename, jd_url, user_id)
            
            # Save skill analysis to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"💾 Analysis results saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save analysis results: {str(e)}")
            raise Exception(f"Result saving error: {str(e)}")
    
    def _extract_company_name(self, jd_skills: Dict, jd_url: str, jd_data: Optional[Dict] = None) -> str:
        """
        Extract company name from JD content or URL using same logic as JobExtractionService
        
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
                    return company_slug
            
            # First, try to find existing company folder by checking if JD was already processed
            existing_folders = []
            if self.base_dir.exists():
                existing_folders = [f.name for f in self.base_dir.iterdir() if f.is_dir()]
            
            # Try to extract from URL first
            if "ethicaljobs.com.au/members/" in jd_url:
                # Extract from ethicaljobs URL pattern
                match = re.search(r'/members/([^/]+)/', jd_url)
                if match:
                    url_company = match.group(1)
                    # Check if this matches any existing folder
                    for folder in existing_folders:
                        if url_company.lower() in folder.lower() or folder.lower() in url_company.lower():
                            logger.debug(f"🏢 Found matching existing folder: {folder}")
                            return folder
                    company_name = url_company
                    logger.debug(f"🏢 Extracted company from URL: {company_name}")
            
            # Try to extract from JD raw response
            raw_response = jd_skills.get('raw_response', '')
            if raw_response and company_name == "Unknown_Company":
                # Look for common company name patterns (same as JobExtractionService)
                patterns = [
                    r'About\s+us\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
                    r'About\s+the\s+company\s+([A-Z][a-zA-Z\s&.-]+?)\s+is',
                    r'([A-Z][a-zA-Z\s&.-]+?)\s+Job\s+Summary\s+\\1',
                    r'([A-Z][a-zA-Z\s&.-]+?)\s+Applications\s+close.*?\\1',
                    r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+Job\s+Summary',
                    r'(?:^|\n)\s*([A-Z][a-zA-Z\s&.-]+?)\s+Applications\s+close',
                    r'The Glen Centre',
                    r'Glen Centre',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, raw_response, re.IGNORECASE)
                    if match:
                        if 'Glen' in pattern:
                            extracted_name = "The Glen Group"
                        else:
                            extracted_name = match.group(1).strip()
                        
                        # Check if this matches any existing folder
                        for folder in existing_folders:
                            if any(word in folder.lower() for word in extracted_name.lower().split()):
                                logger.debug(f"🏢 Found matching existing folder: {folder} for extracted name: {extracted_name}")
                                return folder
                        
                        company_name = extracted_name
                        logger.debug(f"🏢 Extracted company from JD content: {company_name}")
                        break
            
            # Clean company name for folder use (same logic as JobExtractionService._create_company_slug)
            company_slug = self._create_company_slug(company_name)
            
            # Check if this slug matches any existing folder
            for folder in existing_folders:
                if folder.lower() == company_slug.lower():
                    logger.debug(f"🏢 Using existing folder: {folder}")
                    return folder
            
            return company_slug
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract company name: {e}, using 'Unknown_Company'")
            return "Unknown_Company"
    
    def _create_company_slug(self, company_name: str) -> str:
        """
        Create a safe company slug for folder names (same logic as JobExtractionService)
        
        Args:
            company_name: Raw company name
            
        Returns:
            Cleaned company slug suitable for folder names
        """
        if not company_name or company_name.lower() in ['unknown', 'null', '']:
            return f"Unknown_Company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
                company_folder = self.base_dir / self._clean_company_name(company_name)
                if company_folder.exists():
                    files = list(company_folder.glob("log_output.txt"))
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
                            files = list(company_folder.glob("log_output.txt"))
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


# Global instance
result_saver = SkillExtractionResultSaver("cv-analysis")
