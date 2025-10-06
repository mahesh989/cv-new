"""
Helper script to verify the file paths are being created correctly.
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

from .user_path_utils import (
    get_user_base_path,
    get_user_company_analysis_paths,
    get_user_cv_paths,
    ensure_user_directories
)

def verify_company_paths(company: str, user_email: Optional[str] = None) -> Dict[str, bool]:
    """Verify that all required paths exist for a company."""
    # Ensure base directories exist
    ensure_user_directories(user_email)
    
    # Get the paths
    paths = get_user_company_analysis_paths(user_email, company)
    cv_paths = get_user_cv_paths(user_email)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create test files
    test_data = {"test": True, "timestamp": timestamp}
    
    required_files = {
        "jd_original": paths["jd_original"](timestamp),
        "job_info": paths["job_info"](timestamp),
        "jd_analysis": paths["jd_analysis"](timestamp),
        "cv_jd_matching": paths["cv_jd_matching"](timestamp),
        "component_analysis": paths["component_analysis"](timestamp),
        "skills_analysis": paths["skills_analysis"](timestamp),
        "input_recommendation": paths["input_recommendation"](timestamp),
        "ai_recommendation": paths["ai_recommendation"](timestamp),
        "tailored_cv": paths["tailored_cv"](timestamp)
    }
    
    results = {}
    
    # Create parent directories
    for path in required_files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        
    # Try to write test files
    for name, path in required_files.items():
        try:
            with open(path, 'w') as f:
                json.dump(test_data, f)
            results[name] = True
        except Exception as e:
            results[name] = False
            print(f"Failed to create {name}: {e}")
    
    # Verify CV directories
    for name, path in cv_paths.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
            test_file = path / "test.json"
            with open(test_file, 'w') as f:
                json.dump(test_data, f)
            results[f"cv_{name}"] = True
            test_file.unlink()  # Clean up test file
        except Exception as e:
            results[f"cv_{name}"] = False
            print(f"Failed to verify CV directory {name}: {e}")
    
    # Clean up test files
    for path in required_files.values():
        try:
            path.unlink()
        except:
            pass
            
    return results

def print_company_structure(company: str, user_email: Optional[str] = None) -> None:
    """Print the expected directory structure for a company."""
    base_path = get_user_base_path(user_email)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = get_user_company_analysis_paths(user_email, company)
    
    print(f"Directory structure for {company}:")
    print("user/")
    print(f"└── user_{user_email}/")
    print("    └── cv-analysis/")
    print("        ├── applied_companies/")
    print(f"        │   └── {company}/")
    
    # List all files that should be in the company directory
    for name, path_func in paths.items():
        path = path_func(timestamp)
        print(f"        │       ├── {path.name}")
    
    print("        ├── cvs/")
    print("        │   ├── original/")
    print("        │   │   ├── original_cv.txt")
    print("        │   │   └── original_cv.json")
    print("        │   └── tailored/")
    print(f"        │       └── {company}_tailored_cv_{timestamp}.json")
    print("        ├── saved_jobs/")
    print("        │   └── saved_jobs.json")
    print("        └── uploads/")

if __name__ == "__main__":
    # Test for a company
    company = "Australia_for_UNHCR"
    print("\nVerifying paths...")
    results = verify_company_paths(company)
    
    print("\nResults:")
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print("\nExpected structure:")
    print_company_structure(company)