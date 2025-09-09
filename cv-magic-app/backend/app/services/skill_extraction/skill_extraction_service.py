"""
Main Skill Extraction Service

Handles skill extraction from CVs and Job Descriptions with caching and AI integration
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.cv import CV, JobApplication
from app.services.cv_processor import cv_processor
from app.services.job_scraper import scrape_job_description_async
from app.ai.ai_service import ai_service
from .prompt_templates import SkillExtractionPrompts
from .response_parser import SkillExtractionParser
from .result_saver import result_saver

logger = logging.getLogger(__name__)

class SkillExtractionService:
    """Main service for skill extraction with caching and AI integration"""
    
    def __init__(self):
        self.prompts = SkillExtractionPrompts()
        self.parser = SkillExtractionParser()
    
    async def analyze_skills(
        self, 
        cv_filename: str, 
        jd_url: str, 
        user_id: int, 
        force_refresh: bool = False
    ) -> Dict[str, any]:
        """
        Analyze skills from CV and JD with intelligent caching
        
        Args:
            cv_filename: Name of the CV file
            jd_url: URL of the job description
            user_id: ID of the user requesting analysis
            force_refresh: Force fresh analysis bypassing cache
            
        Returns:
            Dictionary containing CV and JD skill analysis results
        """
        logger.info(f"🎯 Starting skill analysis for user {user_id}")
        logger.info(f"📄 CV: {cv_filename}")
        logger.info(f"🔗 JD URL: {jd_url}")
        
        try:
            # Get database session
            with SessionLocal() as db:
                # Step 1: Get or create CV record
                cv_data = await self._get_cv_data(db, cv_filename, user_id)
                if not cv_data:
                    raise ValueError(f"CV file '{cv_filename}' not found. Please upload the CV file first.")
                
                # Step 2: Get or create Job Application record
                jd_data = await self._get_jd_data(db, jd_url, user_id)
                if not jd_data:
                    raise ValueError(f"Failed to get job description from URL: {jd_url}")
                
                # Step 3: Extract CV skills (with caching)
                cv_skills = await self._extract_cv_skills(
                    db, cv_data, force_refresh
                )
                
                # Step 4: Extract JD skills (with caching)  
                jd_skills = await self._extract_jd_skills(
                    db, jd_data, force_refresh
                )
                
                # Step 5: Log results in required format
                self._log_results(cv_skills, jd_skills)
                
                # Step 6: Save results to file
                try:
                    saved_file_path = result_saver.save_analysis_results(
                        cv_skills=cv_skills,
                        jd_skills=jd_skills,
                        jd_url=jd_url,
                        cv_filename=cv_filename,
                        user_id=user_id,
                        cv_data=cv_data,  # Pass CV data for saving original_cv.txt
                        jd_data=jd_data   # Pass JD data for saving jd_original.txt and job_info.json
                    )
                    logger.info(f"📁 Results saved to file: {saved_file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to save results to file: {str(e)}")
                    saved_file_path = None
                
                logger.info(f"✅ Skill analysis completed successfully")
                
                return {
                    "cv_skills": cv_skills,
                    "jd_skills": jd_skills,
                    "cv_filename": cv_filename,
                    "jd_url": jd_url,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "saved_file_path": saved_file_path
                }
                
        except Exception as e:
            logger.error(f"❌ Skill analysis failed: {str(e)}")
            logger.error(f"❌ CV: {cv_filename}, JD URL: {jd_url}, User: {user_id}")
            raise Exception(f"Skill analysis error: {str(e)}")
    
    async def _get_cv_data(self, db: Session, cv_filename: str, user_id: int) -> Optional[Dict]:
        """Get CV data from database and file system"""
        logger.info(f"📄 Getting CV data for {cv_filename}")
        
        try:
            # Check if file exists first
            upload_dir = Path("uploads")
            file_path = upload_dir / cv_filename
            
            if not file_path.exists():
                logger.error(f"❌ CV file not found: {file_path}")
                logger.error(f"❌ Available files in uploads: {list(upload_dir.glob('*')) if upload_dir.exists() else 'Uploads directory does not exist'}")
                return None
            
            # Extract text from file
            extraction_result = cv_processor.extract_text_from_file(file_path)
            
            if not extraction_result['success']:
                logger.error(f"❌ Failed to extract CV text: {extraction_result['error']}")
                logger.error(f"❌ File type: {file_path.suffix}, Size: {file_path.stat().st_size if file_path.exists() else 'N/A'} bytes")
                return None
            
            cv_text = extraction_result['text']
            logger.info(f"📄 CV text extracted: {len(cv_text)} characters")
            
            # Query CV from database
            cv_record = db.query(CV).filter(
                CV.filename == cv_filename,
                CV.user_id == user_id,
                CV.is_active == True
            ).first()
            
            # If no database record exists, create one
            if not cv_record:
                logger.info(f"📝 Creating CV database record for {cv_filename}")
                
                file_stat = file_path.stat()
                cv_record = CV(
                    user_id=user_id,
                    filename=cv_filename,
                    original_filename=cv_filename,
                    title=f"CV - {cv_filename}",
                    file_path=str(file_path),
                    file_size=file_stat.st_size,
                    file_type=extraction_result.get('file_type', 'pdf'),
                    is_active=True
                )
                db.add(cv_record)
                db.commit()
                db.refresh(cv_record)
                logger.info(f"✅ Created CV record with ID: {cv_record.id}")
            
            return {
                "record": cv_record,
                "text": cv_text,
                "filename": cv_filename
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting CV data: {str(e)}")
            logger.error(f"❌ CV filename: {cv_filename}, User ID: {user_id}")
            return None
    
    async def _get_jd_data(self, db: Session, jd_url: str, user_id: int) -> Optional[Dict]:
        """Get JD data by scraping URL"""
        logger.info(f"🔗 Getting JD data from {jd_url}")
        
        try:
            # Scrape job description
            jd_text = await scrape_job_description_async(jd_url)
            
            if jd_text.startswith("Error:") or len(jd_text.strip()) < 10:
                logger.error(f"❌ Failed to scrape JD: {jd_text}")
                return None
            
            logger.info(f"🔗 JD text scraped: {len(jd_text)} characters")
            
            # Create or get job application record
            job_app = db.query(JobApplication).filter(
                JobApplication.job_url == jd_url,
                JobApplication.user_id == user_id
            ).first()
            
            if not job_app:
                # Create new job application record
                job_app = JobApplication(
                    user_id=user_id,
                    job_title="Data Analyst",  # Will be updated by AI later
                    company="Unknown",  # Will be updated by AI later
                    job_url=jd_url,
                    job_description=jd_text,
                    application_date=datetime.now(),
                    status="analyzing"
                )
                db.add(job_app)
                db.commit()
                db.refresh(job_app)
                logger.info(f"📝 Created new job application record: ID {job_app.id}")
            
            return {
                "record": job_app,
                "text": jd_text,
                "url": jd_url
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting JD data: {str(e)}")
            return None
    
    async def _extract_cv_skills(self, db: Session, cv_data: Dict, force_refresh: bool) -> Dict:
        """Extract skills from CV with caching"""
        cv_record = cv_data["record"]
        cv_text = cv_data["text"]
        
        logger.info(f"🔄 Extracting CV skills (force_refresh={force_refresh})")
        
        # Check cache first (unless force_refresh)
        if not force_refresh and cv_record.technical_skills:
            logger.info("📂 Using cached CV skills")
            return {
                "soft_skills": json.loads(cv_record.soft_skills or "[]"),
                "technical_skills": json.loads(cv_record.technical_skills or "[]"),
                "domain_keywords": json.loads(cv_record.domain_keywords or "[]"),
                "from_cache": True
            }
        
        # Extract skills using AI
        logger.info("🤖 Extracting CV skills using AI service")
        
        prompt = self.prompts.get_skill_extraction_template("CV", cv_text)
        system_prompt = self.prompts.get_system_prompt("CV")
        
        # Call AI service
        ai_response = await ai_service.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse response
        parsed_skills = self.parser.parse_response(ai_response.content, "CV")
        
        if not parsed_skills["parsing_success"]:
            raise Exception(f"Failed to parse CV skills: {parsed_skills.get('error', 'Unknown error')}")
        
        # Cache results in database
        cv_record.technical_skills = json.dumps(parsed_skills["technical_skills"])
        cv_record.soft_skills = json.dumps(parsed_skills["soft_skills"])
        cv_record.domain_keywords = json.dumps(parsed_skills["domain_keywords"])
        cv_record.analyzed_at = datetime.now()
        db.commit()
        
        logger.info("💾 CV skills cached in database")
        
        return {
            "soft_skills": parsed_skills["soft_skills"],
            "technical_skills": parsed_skills["technical_skills"],
            "domain_keywords": parsed_skills["domain_keywords"],
            "raw_response": parsed_skills["raw_response"],
            "from_cache": False
        }
    
    async def _extract_jd_skills(self, db: Session, jd_data: Dict, force_refresh: bool) -> Dict:
        """Extract skills from JD with caching"""
        jd_record = jd_data["record"]
        jd_text = jd_data["text"]
        
        logger.info(f"🔄 Extracting JD skills (force_refresh={force_refresh})")
        
        # Check cache first (unless force_refresh)
        if not force_refresh and jd_record.matched_skills:
            logger.info("📂 Using cached JD skills")
            cached_data = json.loads(jd_record.matched_skills or "{}")
            return {
                "soft_skills": cached_data.get("soft_skills", []),
                "technical_skills": cached_data.get("technical_skills", []),
                "domain_keywords": cached_data.get("domain_keywords", []),
                "from_cache": True
            }
        
        # Extract skills using AI
        logger.info("🤖 Extracting JD skills using AI service")
        
        prompt = self.prompts.get_skill_extraction_template("Job Description", jd_text)
        system_prompt = self.prompts.get_system_prompt("Job Description")
        
        # Call AI service
        ai_response = await ai_service.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse response
        parsed_skills = self.parser.parse_response(ai_response.content, "JD")
        
        if not parsed_skills["parsing_success"]:
            raise Exception(f"Failed to parse JD skills: {parsed_skills.get('error', 'Unknown error')}")
        
        # Cache results in database
        skills_cache = {
            "soft_skills": parsed_skills["soft_skills"],
            "technical_skills": parsed_skills["technical_skills"],
            "domain_keywords": parsed_skills["domain_keywords"]
        }
        jd_record.matched_skills = json.dumps(skills_cache)
        jd_record.analyzed_at = datetime.now()
        db.commit()
        
        logger.info("💾 JD skills cached in database")
        
        return {
            "soft_skills": parsed_skills["soft_skills"],
            "technical_skills": parsed_skills["technical_skills"],
            "domain_keywords": parsed_skills["domain_keywords"],
            "raw_response": parsed_skills["raw_response"],
            "from_cache": False
        }
    
    def _log_results(self, cv_skills: Dict, jd_skills: Dict):
        """Log results in the required format"""
        logger.info("📝 Logging results in required format")
        
        # Log CV analysis
        if "raw_response" in cv_skills:
            cv_formatted = self.parser.format_for_logging(cv_skills, "CV")
            print(cv_formatted)
        
        # Log JD analysis
        if "raw_response" in jd_skills:
            jd_formatted = self.parser.format_for_logging(jd_skills, "JD")
            print(jd_formatted)


# Global service instance
skill_extraction_service = SkillExtractionService()
