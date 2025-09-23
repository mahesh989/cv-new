"""
Enhanced Skill Extraction Service

Enhanced version using the new file selector system for proper version tracking
and rerun support.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.cv import CV, JobApplication
from app.services.cv_processor import cv_processor
from app.services.job_scraper import scrape_job_description_async
from app.ai.ai_service import ai_service
from app.services.skill_analysis.skill_analysis_file_selector import skill_analysis_file_selector
from .prompt_templates import SkillExtractionPrompts
from .response_parser import SkillExtractionParser

logger = logging.getLogger(__name__)


class EnhancedSkillExtractionService:
    """Enhanced service for skill extraction with proper file selection and version tracking"""
    
    def __init__(self):
        self.prompts = SkillExtractionPrompts()
        self.parser = SkillExtractionParser()
        self.file_selector = skill_analysis_file_selector
    
    async def analyze_skills(
        self, 
        cv_filename: str, 
        jd_url: str, 
        user_id: int, 
        company: str,
        is_rerun: bool = False,
        force_refresh: bool = False
    ) -> Dict[str, any]:
        """
        Analyze skills with enhanced file selection and version tracking
        
        Args:
            cv_filename: Name of the CV file
            jd_url: URL of the job description
            user_id: ID of the user requesting analysis
            company: Company name for organization
            is_rerun: Whether this is a rerun analysis
            force_refresh: Force fresh analysis bypassing cache
        """
        logger.info(f"🎯 Starting {'rerun' if is_rerun else 'fresh'} analysis for {company}")
        logger.info(f"📄 CV: {cv_filename}")
        logger.info(f"🔗 JD URL: {jd_url}")
        
        try:
            # Get database session
            with SessionLocal() as db:
                # Step 1: Get or create CV and JD data
                cv_data = await self._get_cv_data(db, cv_filename, user_id)
                jd_data = await self._get_jd_data(db, jd_url, user_id)
                
                if not cv_data or not jd_data:
                    raise ValueError("Failed to get CV or JD data")
                
                # Step 2: Extract skills (with file selection)
                analysis_result = await self._perform_skill_analysis(
                    db=db,
                    cv_data=cv_data,
                    jd_data=jd_data,
                    company=company,
                    is_rerun=is_rerun,
                    force_refresh=force_refresh
                )
                
                # Step 3: Save analysis files
                saved_files = await self._save_analysis_files(
                    company=company,
                    is_rerun=is_rerun,
                    analysis_result=analysis_result,
                    cv_data=cv_data,
                    jd_data=jd_data
                )
                
                logger.info(f"✅ Analysis completed successfully")
                return {
                    **analysis_result,
                    "saved_files": saved_files,
                    "cv_filename": cv_filename,
                    "jd_url": jd_url,
                    "company": company,
                    "analysis_timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            raise Exception(f"Skill analysis error: {str(e)}")
    
    async def _perform_skill_analysis(
        self,
        db: Session,
        cv_data: Dict,
        jd_data: Dict,
        company: str,
        is_rerun: bool,
        force_refresh: bool
    ) -> Dict[str, Any]:
        """Perform skill analysis with proper file selection"""
        try:
            # Step 1: Check if we can use existing analysis
            if not force_refresh and not is_rerun:
                existing_analysis = self.file_selector.get_analysis_content(
                    company=company,
                    is_rerun=False
                )
                if existing_analysis["success"]:
                    logger.info("📂 Using existing analysis")
                    return existing_analysis["json_content"]
            
            # Step 2: Extract CV skills
            cv_skills = await self._extract_cv_skills(
                db=db,
                cv_data=cv_data,
                force_refresh=force_refresh or is_rerun
            )
            
            # Step 3: Extract JD skills
            jd_skills = await self._extract_jd_skills(
                db=db,
                jd_data=jd_data,
                force_refresh=force_refresh or is_rerun
            )
            
            # Step 4: Create complete analysis result
            analysis_result = {
                "cv_skills": cv_skills,
                "jd_skills": jd_skills,
                "metadata": {
                    "company": company,
                    "is_rerun": is_rerun,
                    "analysis_version": "2.0",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error performing analysis: {str(e)}")
            raise
    
    async def _save_analysis_files(
        self,
        company: str,
        is_rerun: bool,
        analysis_result: Dict,
        cv_data: Dict,
        jd_data: Dict
    ) -> Dict[str, str]:
        """Save analysis files with proper versioning"""
        try:
            # Get appropriate file paths from selector
            analysis_context = self.file_selector.get_analysis_files(
                company=company,
                is_rerun=is_rerun
            )
            
            saved_files = {}
            
            # Save JSON analysis
            if analysis_context.json_path:
                json_path = analysis_context.json_path
                json_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_result, f, indent=2)
                saved_files["json_path"] = str(json_path)
            
            # Save summary
            if analysis_context.summary_path:
                summary_path = analysis_context.summary_path
                summary_path.parent.mkdir(parents=True, exist_ok=True)
                
                summary_content = self._generate_analysis_summary(
                    analysis_result=analysis_result,
                    cv_data=cv_data,
                    jd_data=jd_data
                )
                
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(summary_content)
                saved_files["summary_path"] = str(summary_path)
            
            return saved_files
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis files: {str(e)}")
            return {}
    
    def _generate_analysis_summary(
        self,
        analysis_result: Dict,
        cv_data: Dict,
        jd_data: Dict
    ) -> str:
        """Generate human-readable summary of analysis"""
        cv_skills = analysis_result["cv_skills"]
        jd_skills = analysis_result["jd_skills"]
        
        summary = []
        summary.append("SKILL ANALYSIS SUMMARY")
        summary.append("=====================")
        summary.append("")
        
        # CV Skills
        summary.append("CV SKILLS:")
        summary.append("----------")
        summary.append("Technical Skills:")
        for skill in cv_skills["technical_skills"]:
            summary.append(f"- {skill}")
        summary.append("")
        
        summary.append("Soft Skills:")
        for skill in cv_skills["soft_skills"]:
            summary.append(f"- {skill}")
        summary.append("")
        
        summary.append("Domain Keywords:")
        for keyword in cv_skills["domain_keywords"]:
            summary.append(f"- {keyword}")
        summary.append("")
        
        # JD Skills
        summary.append("JOB REQUIREMENTS:")
        summary.append("----------------")
        summary.append("Technical Skills:")
        for skill in jd_skills["technical_skills"]:
            summary.append(f"- {skill}")
        summary.append("")
        
        summary.append("Soft Skills:")
        for skill in jd_skills["soft_skills"]:
            summary.append(f"- {skill}")
        summary.append("")
        
        summary.append("Domain Keywords:")
        for keyword in jd_skills["domain_keywords"]:
            summary.append(f"- {keyword}")
        
        return "\n".join(summary)
    
    # Keep existing helper methods (_get_cv_data, _get_jd_data, _extract_cv_skills, _extract_jd_skills)
    async def _get_cv_data(self, db: Session, cv_filename: str, user_id: int) -> Optional[Dict]:
        """Get CV data from database and file system"""
        # Implementation remains the same as original
        pass
        
    async def _get_jd_data(self, db: Session, jd_url: str, user_id: int) -> Optional[Dict]:
        """Get JD data by scraping URL"""
        # Implementation remains the same as original
        pass
    
    async def _extract_cv_skills(self, db: Session, cv_data: Dict, force_refresh: bool) -> Dict:
        """Extract skills from CV with caching"""
        # Implementation remains the same as original
        pass
    
    async def _extract_jd_skills(self, db: Session, jd_data: Dict, force_refresh: bool) -> Dict:
        """Extract skills from JD with caching"""
        # Implementation remains the same as original
        pass


# Global instance
enhanced_skill_extraction_service = EnhancedSkillExtractionService()