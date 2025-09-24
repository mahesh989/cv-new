"""
Integration Script for CV Analysis Workflow

This script can be integrated into the existing CV analysis workflow
to automatically save job information whenever a new analysis is completed.
"""

import sys
import os
from pathlib import Path

# Add the saved_jobs directory to the Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from job_saver import save_job_from_analysis

def integrate_job_saving(job_info_file_path: str) -> bool:
    """
    Integrate job saving into the CV analysis workflow.
    
    Args:
        job_info_file_path: Path to the job_info JSON file created during analysis
        
    Returns:
        True if job was saved successfully, False otherwise
    """
    try:
        print(f"Integrating job saving for: {job_info_file_path}")
        success = save_job_from_analysis(job_info_file_path)
        
        if success:
            print("✅ Job successfully saved to saved_jobs.json")
            return True
        else:
            print("⚠️ Job was not saved (likely duplicate or invalid data)")
            return False
            
    except Exception as e:
        print(f"❌ Error integrating job saving: {e}")
        return False

def get_saved_jobs_summary():
    """Get a summary of all saved jobs."""
    try:
        from job_saver import JobSaver
        job_saver = JobSaver()
        summary = job_saver.get_saved_jobs_summary()
        
        print("\n📊 Saved Jobs Summary:")
        print(f"Total Jobs: {summary.get('total_jobs', 0)}")
        print(f"Last Updated: {summary.get('last_updated', 'Never')}")
        print(f"Companies: {', '.join(summary.get('companies', []))}")
        print(f"File Location: {summary.get('file_path', 'Unknown')}")
        
        return summary
        
    except Exception as e:
        print(f"❌ Error getting summary: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        job_file_path = sys.argv[1]
        integrate_job_saving(job_file_path)
    else:
        print("Usage: python integrate_with_analysis.py <path_to_job_info_file>")
        print("\nOr run without arguments to see saved jobs summary:")
        get_saved_jobs_summary()
