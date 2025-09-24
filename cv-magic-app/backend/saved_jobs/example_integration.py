"""
Example Integration

This shows how to integrate the job saving system into your existing CV analysis workflow.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Add the saved_jobs directory to the Python path
saved_jobs_dir = Path(__file__).parent
sys.path.append(str(saved_jobs_dir))

from job_saver import save_job_from_analysis

def example_cv_analysis_workflow():
    """
    Example of how to integrate job saving into your CV analysis workflow.
    This simulates what happens when a new job analysis is completed.
    """
    
    # Simulate extracting job information (replace with your actual extraction logic)
    job_info = {
        "company_name": "Example Company",
        "job_url": "https://example.com/job-posting",
        "job_title": "Software Engineer",
        "location": "San Francisco, CA",
        "phone_number": "+1-555-123-4567",
        "email": "hr@example.com",
        "extracted_at": datetime.now().isoformat()
    }
    
    # Create the job_info file path (following your naming convention)
    company_name = job_info["company_name"].replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_info_filename = f"job_info_{company_name}_{timestamp}.json"
    
    # Create the directory structure
    analysis_dir = Path("cv-analysis") / company_name
    analysis_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the job_info file
    job_info_path = analysis_dir / job_info_filename
    
    with open(job_info_path, 'w', encoding='utf-8') as f:
        json.dump(job_info, f, indent=2, ensure_ascii=False)
    
    print(f"Created job_info file: {job_info_path}")
    
    # Automatically save to saved_jobs.json
    print("Saving job to saved_jobs.json...")
    success = save_job_from_analysis(str(job_info_path))
    
    if success:
        print("✅ Job successfully saved to saved_jobs.json")
    else:
        print("⚠️ Job was not saved (likely duplicate or invalid data)")
    
    return success

def example_batch_processing():
    """
    Example of processing multiple existing job_info files.
    """
    print("Processing existing job_info files...")
    
    # Find all job_info files in the cv-analysis directory
    cv_analysis_dir = Path("cv-analysis")
    if not cv_analysis_dir.exists():
        print("cv-analysis directory not found")
        return
    
    job_info_files = list(cv_analysis_dir.rglob("job_info_*.json"))
    print(f"Found {len(job_info_files)} job_info files")
    
    for job_file in job_info_files:
        print(f"\nProcessing: {job_file}")
        success = save_job_from_analysis(str(job_file))
        
        if success:
            print("✅ Successfully saved")
        else:
            print("⚠️ Skipped (duplicate or invalid)")

if __name__ == "__main__":
    print("=== Job Saving Integration Example ===\n")
    
    # Example 1: Single job analysis
    print("1. Single Job Analysis Example:")
    example_cv_analysis_workflow()
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Batch processing
    print("2. Batch Processing Example:")
    example_batch_processing()
    
    print("\n" + "="*50 + "\n")
    
    # Show summary
    from job_saver import JobSaver
    job_saver = JobSaver()
    summary = job_saver.get_saved_jobs_summary()
    
    print("📊 Final Summary:")
    print(f"Total Jobs: {summary.get('total_jobs', 0)}")
    print(f"Companies: {', '.join(summary.get('companies', []))}")
    print(f"Last Updated: {summary.get('last_updated', 'Never')}")
