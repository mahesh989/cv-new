"""
Dynamic CV Content Service

Handles dynamic CV content retrieval and management, replacing hardcoded content
"""
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.cv import CV
from app.services.cv_processor import cv_processor

logger = logging.getLogger(__name__)


class CVContentService:
    """Service for dynamic CV content management"""
    
    def __init__(self, user_email: str):
        from app.utils.user_path_utils import get_user_uploads_path
        self.user_email = user_email
        self.upload_dir = get_user_uploads_path(self.user_email)  # Use user context
        self.fallback_cv_content = self._get_fallback_cv_content()
    
    def get_cv_content(self, cv_filename: str, user_id: int = 1, use_fallback: bool = False) -> Dict[str, Any]:
        """
        Get CV content dynamically from file system or database
        
        Args:
            cv_filename: Name of the CV file
            user_id: User ID (default: 1)
            use_fallback: Whether to use fallback content if file not found (default: False)
            
        Returns:
            Dictionary containing CV content and metadata
        """
        try:
            logger.info(f"🔍 [CV_CONTENT] Retrieving content for: {cv_filename}")
            
            # Try to get from file system first
            file_content = self._get_from_file_system(cv_filename)
            if file_content:
                logger.info(f"✅ [CV_CONTENT] Retrieved from file system: {cv_filename}")
                return file_content
            
            # Try to get from database
            db_content = self._get_from_database(cv_filename, user_id)
            if db_content:
                logger.info(f"✅ [CV_CONTENT] Retrieved from database: {cv_filename}")
                return db_content
            
            # Use fallback only if explicitly enabled
            if use_fallback:
                logger.warning(f"⚠️ [CV_CONTENT] Using fallback content for: {cv_filename}")
                return self._get_fallback_content(cv_filename)
            
            # No content found - return error
            logger.error(f"❌ [CV_CONTENT] No content found for: {cv_filename}")
            return {
                "success": False,
                "error": f"CV file '{cv_filename}' not found. Please upload the CV file first.",
                "content": "",
                "source": "none",
                "suggestions": [
                    "Check if the CV file exists in the uploads folder",
                    "Verify the filename is correct",
                    "Upload the CV file using the CV upload feature",
                    "Check if the file was uploaded successfully"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ [CV_CONTENT] Error retrieving CV content: {str(e)}")
            if use_fallback:
                return self._get_fallback_content(cv_filename)
            return {
                "success": False,
                "error": f"Error retrieving CV content: {str(e)}",
                "content": "",
                "source": "error",
                "suggestions": [
                    "Check if the CV file exists and is accessible",
                    "Verify file permissions",
                    "Try uploading the CV file again"
                ]
            }
    
    def _get_from_file_system(self, cv_filename: str) -> Optional[Dict[str, Any]]:
        """Get CV content from file system"""
        try:
            file_path = self.upload_dir / cv_filename
            
            if not file_path.exists():
                return None
            
            # Extract text using CV processor
            result = cv_processor.extract_text_from_file(file_path)
            
            if not result['success']:
                logger.warning(f"⚠️ [CV_CONTENT] Failed to extract from file: {result['error']}")
                return None
            
            return {
                "success": True,
                "content": result['text'],
                "source": "file_system",
                "filename": cv_filename,
                "file_path": str(file_path),
                "metadata": {
                    "file_type": result.get('file_type', 'unknown'),
                    "word_count": result.get('word_count', 0),
                    "character_count": len(result['text'])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ [CV_CONTENT] Error reading from file system: {str(e)}")
            return None
    
    def _get_from_database(self, cv_filename: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Get CV content from database"""
        try:
            with SessionLocal() as db:
                cv_record = db.query(CV).filter(
                    CV.filename == cv_filename,
                    CV.user_id == user_id,
                    CV.is_active == True
                ).first()
                
                if not cv_record:
                    return None
                
                # If we have the file path, try to read from file
                if cv_record.file_path and Path(cv_record.file_path).exists():
                    file_result = self._get_from_file_system(cv_filename)
                    if file_result:
                        file_result["source"] = "database_file"
                        file_result["cv_id"] = cv_record.id
                        return file_result
                
                # Return database record info even if file is missing
                return {
                    "success": True,
                    "content": "",  # No content available
                    "source": "database_record",
                    "filename": cv_filename,
                    "cv_id": cv_record.id,
                    "metadata": {
                        "file_size": cv_record.file_size,
                        "file_type": cv_record.file_type,
                        "created_at": cv_record.created_at.isoformat() if cv_record.created_at else None
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ [CV_CONTENT] Error reading from database: {str(e)}")
            return None
    
    def _get_fallback_content(self, cv_filename: str) -> Dict[str, Any]:
        """Get fallback CV content"""
        return {
            "success": True,
            "content": self.fallback_cv_content,
            "source": "fallback",
            "filename": cv_filename,
            "metadata": {
                "file_type": "fallback",
                "word_count": len(self.fallback_cv_content.split()),
                "character_count": len(self.fallback_cv_content),
                "note": "Using fallback content - actual CV file not found"
            }
        }
    
    def _get_fallback_cv_content(self) -> str:
        """Get the fallback CV content (moved from main.py)"""
        return """Maheshwor Tiwari  
0414 032 507 | maheshtwari99@gmail.com | LinkedIn  | Hurstville, NSW, 2220  
Blogs on Medium  | GitHub  | Dashboard  Portfolio  
CAREER PROFILE 
I hold a PhD in Physics and completed a Master's in Data Science, bringing over three years of experience in Python 
coding, AI, and machine learning. My expertise encompasses modeling and training AI models, writing efficient Python 
scripts, designing and deploying robust data pipelines, conducting innovative research, and creating advanced 
visualizations that convert complex data into actionable insights. I am also proficient in SQL, Tableau, and Power BI, building 
comprehensive dashboards that support data-driven decision-making.  
TECHNICAL SKILLS  
• Specialized in Python programming, including data analysis, automation, and machine learning using libraries such 
as Pandas, NumPy, and scikit-learn.  
• Proficient in SQL for querying, modeling, and managing complex relational databases like PostgreSQL and MySQL.  
• Skilled in creating interactive dashboards and visualizations using Tableau, Power BI, and Matplotlib.  
• Experienced with GitHub for version control, Docker for containerization, and Snowflake for cloud data warehousing.  
• Adept at leveraging tools like Visual Studio Code, Google Analytics, and Excel for data-driven solutions and reporting.

EXPERIENCE  
Data Analyst         Jul 2024 – Present  
The Bitrates, Sydney, New South Wales, Australia  
• Designed and implemented Python scripts for data cleaning, preprocessing, and analysis, improving data pipeline 
efficiency by 30%.  
• Developed machine learning models in Python for predictive analytics, enabling data-driven business decisions.  
• Leveraged AI techniques to automate repetitive tasks, reducing manual effort and improving productivity.  
• Built dynamic dashboards and visualizations using Python libraries like Matplotlib and Seaborn to communicate 
insights effectively.  
• Integrated Google Analytics data with Python for advanced analysis, enhancing customer behavior insights.
"""
    
    def list_available_cvs(self, user_id: int = 1) -> Dict[str, Any]:
        """List all available CVs for a user"""
        try:
            cvs = []
            
            # Get from file system
            if self.upload_dir.exists():
                for file_path in self.upload_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in {'.pdf', '.docx', '.txt'}:
                        cvs.append({
                            "filename": file_path.name,
                            "source": "file_system",
                            "path": str(file_path),
                            "size": file_path.stat().st_size
                        })
            
            # Get from database
            with SessionLocal() as db:
                db_cvs = db.query(CV).filter(
                    CV.user_id == user_id,
                    CV.is_active == True
                ).all()
                
                for cv_record in db_cvs:
                    # Avoid duplicates
                    if not any(cv["filename"] == cv_record.filename for cv in cvs):
                        cvs.append({
                            "filename": cv_record.filename,
                            "source": "database",
                            "cv_id": cv_record.id,
                            "size": cv_record.file_size
                        })
            
            return {
                "success": True,
                "cvs": cvs,
                "total_count": len(cvs),
                "sources": list(set(cv["source"] for cv in cvs))
            }
            
        except Exception as e:
            logger.error(f"❌ [CV_CONTENT] Error listing CVs: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "cvs": [],
                "total_count": 0
            }


# Global instance removed - service now requires user_email parameter
# Create instances per request with proper user context
