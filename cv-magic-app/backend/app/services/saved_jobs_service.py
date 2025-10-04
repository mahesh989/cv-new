"""
Saved Jobs Service

This service handles saving and managing job data in a persistent JSON file.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)

class SavedJobsService:
    def __init__(self, user_email: str):
        """Initialize the saved jobs service."""
        from app.utils.user_path_utils import get_user_saved_jobs_path
        self.user_email = user_email
        self.JOBS_FILE = get_user_saved_jobs_path(user_email)
        self._ensure_jobs_file_exists()
    
    def _ensure_jobs_file_exists(self) -> None:
        """Ensure the jobs file exists with valid initial structure."""
        try:
            self.JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
            if not self.JOBS_FILE.exists():
                initial_data = {
                    "jobs": [],
                    "last_updated": datetime.utcnow().isoformat(),
                    "total_jobs": 0
                }
                with open(self.JOBS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, indent=2, ensure_ascii=False)
                logger.info(f"✨ Created new jobs file at {self.JOBS_FILE}")
        except Exception as e:
            logger.error(f"❌ Failed to ensure jobs file exists: {e}")
            raise
    
    def _read_jobs_data(self) -> dict:
        """Read the current jobs data from file."""
        try:
            with open(self.JOBS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            # Auto-heal: create file and return empty structure
            logger.error(f"❌ Failed to read jobs data: {e}")
            try:
                self._ensure_jobs_file_exists()
            except Exception:
                pass
            return {"jobs": [], "last_updated": datetime.utcnow().isoformat(), "total_jobs": 0}
    
    def _write_jobs_data(self, data: dict) -> bool:
        """Write jobs data to file."""
        try:
            # Update metadata
            data["last_updated"] = datetime.utcnow().isoformat()
            data["total_jobs"] = len(data.get("jobs", []))
            
            # Write to file
            with open(self.JOBS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write jobs data: {e}")
            return False
    
    def get_all_jobs(self) -> List[Dict]:
        """Get all saved jobs."""
        data = self._read_jobs_data()
        return data.get("jobs", [])
    
    def get_job_by_url(self, job_url: str) -> Optional[Dict]:
        """Get a job by its URL."""
        jobs = self.get_all_jobs()
        for job in jobs:
            if job.get("job_url") == job_url:
                return job
        return None
    
    def save_new_job(self, job_data: Dict) -> bool:
        """Save a new job."""
        try:
            # Read current data
            data = self._read_jobs_data()
            jobs = data.get("jobs", [])
            
            # Check if job already exists
            job_url = job_data.get("job_url")
            existing_job = next((job for job in jobs if job.get("job_url") == job_url), None)
            
            if existing_job:
                # Update existing job
                existing_job.update(job_data)
                logger.info(f"🔄 Updated existing job: {job_data.get('job_title')} at {job_data.get('company_name')}")
            else:
                # Add new job
                jobs.append(jsonable_encoder(job_data))
                logger.info(f"✨ Added new job: {job_data.get('job_title')} at {job_data.get('company_name')}")
            
            # Update data
            data["jobs"] = jobs
            
            return self._write_jobs_data(data)
            
        except Exception as e:
            logger.error(f"❌ Failed to save job: {e}")
            return False
    
    def delete_job(self, job_url: str) -> bool:
        """Delete a job by its URL."""
        try:
            data = self._read_jobs_data()
            jobs = data.get("jobs", [])
            
            # Remove job with matching URL
            data["jobs"] = [job for job in jobs if job.get("job_url") != job_url]
            
            return self._write_jobs_data(data)
        except Exception as e:
            logger.error(f"❌ Failed to delete job: {e}")
            return False
    
    def clear_all_jobs(self) -> bool:
        """Clear all saved jobs."""
        try:
            data = self._read_jobs_data()
            data["jobs"] = []
            return self._write_jobs_data(data)
        except Exception as e:
            logger.error(f"❌ Failed to clear jobs: {e}")
            return False

# Note: SavedJobsService should be instantiated per user with their email
# Example: service = SavedJobsService(user_email)