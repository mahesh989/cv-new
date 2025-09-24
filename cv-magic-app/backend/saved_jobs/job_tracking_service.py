"""
Job Tracking Service

This service monitors the cv-analysis folder for new job_info files
and automatically populates the saved_jobs.json file with job information.
It handles redundancy checking and maintains data integrity.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobTrackingService:
    def __init__(self, cv_analysis_path: str, saved_jobs_path: str):
        """
        Initialize the job tracking service.
        
        Args:
            cv_analysis_path: Path to the cv-analysis directory
            saved_jobs_path: Path to the saved_jobs.json file
        """
        self.cv_analysis_path = Path(cv_analysis_path)
        self.saved_jobs_path = Path(saved_jobs_path)
        self.saved_jobs_file = self.saved_jobs_path / "saved_jobs.json"
        
        # Ensure saved_jobs directory exists
        self.saved_jobs_path.mkdir(exist_ok=True)
        
        # Initialize saved_jobs.json if it doesn't exist
        self._initialize_saved_jobs_file()
        
        # Track processed files to avoid duplicates
        self.processed_files: Set[str] = set()
        
        # Load existing jobs to check for redundancy
        self._load_existing_jobs()

    def _initialize_saved_jobs_file(self):
        """Initialize the saved_jobs.json file if it doesn't exist."""
        if not self.saved_jobs_file.exists():
            initial_data = {
                "jobs": [],
                "last_updated": None,
                "total_jobs": 0
            }
            with open(self.saved_jobs_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Initialized saved_jobs.json at {self.saved_jobs_file}")

    def _load_existing_jobs(self):
        """Load existing jobs from saved_jobs.json to check for redundancy."""
        try:
            with open(self.saved_jobs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.existing_jobs = data.get("jobs", [])
                logger.info(f"Loaded {len(self.existing_jobs)} existing jobs")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load existing jobs: {e}")
            self.existing_jobs = []

    def _extract_job_data(self, job_info_file: Path) -> Optional[Dict]:
        """
        Extract job data from a job_info JSON file.
        
        Args:
            job_info_file: Path to the job_info JSON file
            
        Returns:
            Dictionary containing job data or None if extraction fails
        """
        try:
            with open(job_info_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            
            # Extract required fields
            extracted_job = {
                "company_name": job_data.get("company_name"),
                "job_url": job_data.get("job_url"),
                "job_title": job_data.get("job_title"),
                "location": job_data.get("location"),
                "phone_number": job_data.get("phone_number"),
                "email": job_data.get("email")
            }
            
            # Validate required fields
            if not extracted_job["company_name"] or not extracted_job["job_url"]:
                logger.warning(f"Missing required fields in {job_info_file}")
                return None
                
            return extracted_job
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error extracting job data from {job_info_file}: {e}")
            return None

    def _is_duplicate_job(self, new_job: Dict) -> bool:
        """
        Check if a job already exists in saved_jobs.json to avoid redundancy.
        
        Args:
            new_job: New job data to check
            
        Returns:
            True if job is a duplicate, False otherwise
        """
        for existing_job in self.existing_jobs:
            # Check for duplicates based on company_name and job_url
            if (existing_job.get("company_name") == new_job.get("company_name") and
                existing_job.get("job_url") == new_job.get("job_url")):
                return True
                
            # Also check for same job title at same company
            if (existing_job.get("company_name") == new_job.get("company_name") and
                existing_job.get("job_title") == new_job.get("job_title")):
                return True
                
        return False

    def _update_saved_jobs(self, new_job: Dict):
        """
        Update the saved_jobs.json file with new job data.
        
        Args:
            new_job: New job data to add
        """
        try:
            # Load current data
            with open(self.saved_jobs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add new job
            data["jobs"].append(new_job)
            data["last_updated"] = datetime.now().isoformat()
            data["total_jobs"] = len(data["jobs"])
            
            # Save updated data
            with open(self.saved_jobs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Update in-memory tracking
            self.existing_jobs.append(new_job)
            
            logger.info(f"Added new job: {new_job['company_name']} - {new_job['job_title']}")
            
        except Exception as e:
            logger.error(f"Error updating saved_jobs.json: {e}")

    def process_job_info_file(self, job_info_file: Path):
        """
        Process a single job_info JSON file and add it to saved_jobs.json.
        
        Args:
            job_info_file: Path to the job_info JSON file
        """
        if not job_info_file.exists():
            logger.warning(f"Job info file does not exist: {job_info_file}")
            return
            
        # Check if file has already been processed
        file_key = str(job_info_file)
        if file_key in self.processed_files:
            logger.info(f"File already processed: {job_info_file}")
            return
            
        logger.info(f"Processing job info file: {job_info_file}")
        
        # Extract job data
        job_data = self._extract_job_data(job_info_file)
        if not job_data:
            logger.warning(f"Could not extract job data from {job_info_file}")
            return
            
        # Check for duplicates
        if self._is_duplicate_job(job_data):
            logger.info(f"Duplicate job found, skipping: {job_data['company_name']} - {job_data['job_title']}")
            self.processed_files.add(file_key)
            return
            
        # Add to saved_jobs.json
        self._update_saved_jobs(job_data)
        self.processed_files.add(file_key)

    def scan_existing_jobs(self):
        """
        Scan the cv-analysis directory for existing job_info files and process them.
        This is useful for initial setup or catching up on missed files.
        """
        logger.info("Scanning existing job info files...")
        
        if not self.cv_analysis_path.exists():
            logger.warning(f"CV analysis path does not exist: {self.cv_analysis_path}")
            return
            
        # Find all job_info JSON files
        job_info_files = list(self.cv_analysis_path.rglob("job_info_*.json"))
        logger.info(f"Found {len(job_info_files)} job info files")
        
        for job_file in job_info_files:
            self.process_job_info_file(job_file)
            
        logger.info("Finished scanning existing job info files")

    def get_saved_jobs_summary(self) -> Dict:
        """
        Get a summary of saved jobs.
        
        Returns:
            Dictionary containing summary information
        """
        try:
            with open(self.saved_jobs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return {
                "total_jobs": data.get("total_jobs", 0),
                "last_updated": data.get("last_updated"),
                "companies": list(set(job.get("company_name") for job in data.get("jobs", []) if job.get("company_name"))),
                "file_path": str(self.saved_jobs_file)
            }
        except Exception as e:
            logger.error(f"Error getting saved jobs summary: {e}")
            return {"error": str(e)}


class JobFileHandler(FileSystemEventHandler):
    """File system event handler for monitoring job_info files."""
    
    def __init__(self, job_tracking_service: JobTrackingService):
        self.job_tracking_service = job_tracking_service
        
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and event.src_path.endswith("job_info_") and event.src_path.endswith(".json"):
            logger.info(f"New job info file detected: {event.src_path}")
            # Wait a moment for file to be fully written
            time.sleep(1)
            self.job_tracking_service.process_job_info_file(Path(event.src_path))
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith("job_info_") and event.src_path.endswith(".json"):
            logger.info(f"Job info file modified: {event.src_path}")
            # Wait a moment for file to be fully written
            time.sleep(1)
            self.job_tracking_service.process_job_info_file(Path(event.src_path))


def start_job_tracking_monitor(cv_analysis_path: str, saved_jobs_path: str):
    """
    Start monitoring the cv-analysis directory for new job_info files.
    
    Args:
        cv_analysis_path: Path to the cv-analysis directory
        saved_jobs_path: Path to the saved_jobs directory
    """
    # Initialize job tracking service
    job_service = JobTrackingService(cv_analysis_path, saved_jobs_path)
    
    # Scan existing files first
    job_service.scan_existing_jobs()
    
    # Set up file system monitoring
    event_handler = JobFileHandler(job_service)
    observer = Observer()
    observer.schedule(event_handler, cv_analysis_path, recursive=True)
    
    logger.info(f"Starting job tracking monitor for: {cv_analysis_path}")
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping job tracking monitor...")
        observer.stop()
    finally:
        observer.join()


if __name__ == "__main__":
    # Configuration
    CV_ANALYSIS_PATH = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"
    SAVED_JOBS_PATH = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/saved_jobs"
    
    # Start monitoring
    start_job_tracking_monitor(CV_ANALYSIS_PATH, SAVED_JOBS_PATH)
