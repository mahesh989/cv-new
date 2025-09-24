# Job Tracking System

This system automatically populates `saved_jobs.json` with job information whenever a new CV analysis is performed.

## Structure

```
saved_jobs/
├── saved_jobs.json          # Main job database
├── job_saver.py            # Core job saving functionality
├── job_tracking_service.py  # File system monitoring service
├── integrate_with_analysis.py # Integration helper
├── requirements.txt         # Dependencies
└── README.md              # This file
```

## Features

- **Automatic Job Saving**: Monitors cv-analysis folder for new job_info files
- **Redundancy Checking**: Prevents duplicate job entries
- **Data Validation**: Ensures required fields are present
- **Easy Integration**: Simple function calls for existing workflows

## Usage

### Method 1: Direct Integration (Recommended)

Add this to your CV analysis workflow after creating a job_info file:

```python
from saved_jobs.job_saver import save_job_from_analysis

# After creating job_info_company_timestamp.json
job_info_path = "/path/to/job_info_company_timestamp.json"
success = save_job_from_analysis(job_info_path)
```

### Method 2: Command Line Integration

```bash
cd /path/to/saved_jobs
python job_saver.py "/path/to/job_info_company_timestamp.json"
```

### Method 3: File System Monitoring

For automatic monitoring of the cv-analysis folder:

```bash
cd /path/to/saved_jobs
python job_tracking_service.py
```

## Data Structure

The `saved_jobs.json` file contains:

```json
{
  "jobs": [
    {
      "company_name": "Company Name",
      "job_url": "https://example.com/job",
      "job_title": "Job Title",
      "location": "City, Country",
      "phone_number": "phone or null",
      "email": "email or null",
      "extracted_at": "2025-01-01T12:00:00",
      "source_file": "/path/to/source/file.json",
      "added_to_saved_jobs": "2025-01-01T12:00:00"
    }
  ],
  "last_updated": "2025-01-01T12:00:00",
  "total_jobs": 1
}
```

## Redundancy Checking

The system prevents duplicates by checking:
1. Same company name + job URL
2. Same company name + job title

## Integration Examples

### In your CV analysis script:

```python
import json
from pathlib import Path
from saved_jobs.job_saver import save_job_from_analysis

def analyze_cv_and_save_job(cv_file, job_url):
    # Your existing CV analysis code here...
    
    # Create job_info file
    job_info = {
        "company_name": extracted_company,
        "job_url": job_url,
        "job_title": extracted_title,
        "location": extracted_location,
        "phone_number": extracted_phone,
        "email": extracted_email,
        "extracted_at": datetime.now().isoformat()
    }
    
    # Save job_info file
    job_info_path = f"cv-analysis/{company_name}/job_info_{company_name}_{timestamp}.json"
    with open(job_info_path, 'w') as f:
        json.dump(job_info, f, indent=2)
    
    # Automatically save to saved_jobs.json
    save_job_from_analysis(job_info_path)
```

## Monitoring

To monitor the system:

```python
from saved_jobs.job_saver import JobSaver

job_saver = JobSaver()
summary = job_saver.get_saved_jobs_summary()
print(f"Total jobs saved: {summary['total_jobs']}")
```

## Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

## Error Handling

The system handles:
- Missing or invalid JSON files
- Duplicate job entries
- File system errors
- Data validation failures

All errors are logged and the system continues to function.
