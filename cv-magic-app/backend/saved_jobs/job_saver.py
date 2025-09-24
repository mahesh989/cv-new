"""
Job Saver Integration

Simple integration script that can be called whenever a new job analysis is completed.
This script extracts job information and appends it to saved_jobs.json with redundancy checking.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class JobSaver:
    def __init__(self, saved_jobs_path: str = None):
        """
        Initialize the job saver.
        
        Args:
            saved_jobs_path: Path to the saved_jobs directory (defaults to current directory)
        """
        if saved_jobs_path is None:
            # Default to the saved_jobs directory in the backend
            self.saved_jobs_path = Path(__file__).parent
        else:
            self.saved_jobs_path = Path(saved_jobs_path)
            
        self.saved_jobs_file = self.saved_jobs_path / "saved_jobs.json"
        
        # Ensure saved_jobs directory exists
        self.saved_jobs_path.mkdir(exist_ok=True)
        
        # Initialize saved_jobs.json if it doesn't exist
        self._initialize_saved_jobs_file()

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
            print(f"Initialized saved_jobs.json at {self.saved_jobs_file}")

    def _load_existing_jobs(self) -> List[Dict]:
        """Load existing jobs from saved_jobs.json."""
        try:
            with open(self.saved_jobs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("jobs", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Could not load existing jobs: {e}")
            return []

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
                print(f"Missing required fields in {job_info_file}")
                return None
                
            return extracted_job
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error extracting job data from {job_info_file}: {e}")
            return None

    def _is_duplicate_job(self, new_job: Dict, existing_jobs: List[Dict]) -> bool:
        """
        Check if a job already exists in saved_jobs.json to avoid redundancy.
        
        Args:
            new_job: New job data to check
            existing_jobs: List of existing jobs
            
        Returns:
            True if job is a duplicate, False otherwise
        """
        for existing_job in existing_jobs:
            # Check for duplicates based on company_name and job_url
            if (existing_job.get("company_name") == new_job.get("company_name") and
                existing_job.get("job_url") == new_job.get("job_url")):
                return True
                
            # Also check for same job title at same company
            if (existing_job.get("company_name") == new_job.get("company_name") and
                existing_job.get("job_title") == new_job.get("job_title")):
                return True
                
        return False

    def save_job_from_file(self, job_info_file_path: str) -> bool:
        """
        Save job information from a job_info JSON file to saved_jobs.json.
        
        Args:
            job_info_file_path: Path to the job_info JSON file
            
        Returns:
            True if job was saved successfully, False otherwise
        """
        job_info_file = Path(job_info_file_path)
        
        if not job_info_file.exists():
            print(f"Job info file does not exist: {job_info_file}")
            return False
            
        print(f"Processing job info file: {job_info_file}")
        
        # Extract job data
        job_data = self._extract_job_data(job_info_file)
        if not job_data:
            print(f"Could not extract job data from {job_info_file}")
            return False
            
        # Load existing jobs
        existing_jobs = self._load_existing_jobs()
        
        # Check for duplicates
        if self._is_duplicate_job(job_data, existing_jobs):
            print(f"Duplicate job found, skipping: {job_data['company_name']} - {job_data['job_title']}")
            return False
            
        # Add new job to existing jobs
        existing_jobs.append(job_data)
        
        # Update saved_jobs.json
        try:
            updated_data = {
                "jobs": existing_jobs,
                "last_updated": datetime.now().isoformat(),
                "total_jobs": len(existing_jobs)
            }
            
            with open(self.saved_jobs_file, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, indent=2, ensure_ascii=False)
            
            print(f"Successfully added job: {job_data['company_name']} - {job_data['job_title']}")
            return True
            
        except Exception as e:
            print(f"Error updating saved_jobs.json: {e}")
            return False

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
            print(f"Error getting saved jobs summary: {e}")
            return {"error": str(e)}


def save_job_from_analysis(job_info_file_path: str) -> bool:
    """
    Convenience function to save a job from analysis results.
    
    Args:
        job_info_file_path: Path to the job_info JSON file
        
    Returns:
        True if job was saved successfully, False otherwise
    """
    job_saver = JobSaver()
    return job_saver.save_job_from_file(job_info_file_path)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        job_file_path = sys.argv[1]
        success = save_job_from_analysis(job_file_path)
        if success:
            print("Job saved successfully!")
        else:
            print("Failed to save job.")
    else:
        print("Usage: python job_saver.py <path_to_job_info_file>")
