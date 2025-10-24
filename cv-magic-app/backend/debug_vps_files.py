#!/usr/bin/env python3
"""
VPS File Debug Script

Run this script on the VPS to diagnose file structure and job tracking issues.
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add the app to the path
sys.path.append('/app')

def debug_vps_files():
    """Debug VPS file structure and job tracking issues"""
    print("🔍 VPS File Structure Debug")
    print("=" * 50)
    
    # Check user directory structure
    print("\n📁 User Directory Structure:")
    user_dir = Path("user")
    if user_dir.exists():
        for user_folder in user_dir.iterdir():
            if user_folder.is_dir():
                print(f"  👤 User: {user_folder.name}")
                
                # Check cv-analysis directory
                cv_analysis = user_folder / "cv-analysis"
                if cv_analysis.exists():
                    print(f"    📁 cv-analysis: {cv_analysis}")
                    
                    # Check subdirectories
                    subdirs = ["cvs", "applied_companies", "saved_jobs", "uploads"]
                    for subdir in subdirs:
                        subdir_path = cv_analysis / subdir
                        if subdir_path.exists():
                            files = list(subdir_path.iterdir())
                            print(f"      📂 {subdir}: {len(files)} items")
                            
                            # Show files in each subdirectory
                            for file in files[:5]:  # Show first 5 files
                                if file.is_file():
                                    size = file.stat().st_size
                                    modified = datetime.fromtimestamp(file.stat().st_mtime)
                                    print(f"        📄 {file.name} ({size} bytes, {modified})")
                                elif file.is_dir():
                                    print(f"        📁 {file.name}/")
                        else:
                            print(f"      ❌ {subdir}: Not found")
                else:
                    print(f"    ❌ cv-analysis: Not found")
    else:
        print("  ❌ user directory not found")
    
    # Check for specific job tracking files
    print("\n📋 Job Tracking Files:")
    
    # Look for saved_jobs.json files
    saved_jobs_files = list(Path(".").rglob("saved_jobs.json"))
    print(f"  📄 Found {len(saved_jobs_files)} saved_jobs.json files:")
    for file in saved_jobs_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            jobs_count = len(data.get('jobs', []))
            print(f"    📄 {file}: {jobs_count} jobs")
            if jobs_count > 0:
                print(f"      Latest job: {data['jobs'][0].get('company_name', 'Unknown')} - {data['jobs'][0].get('job_title', 'Unknown')}")
        except Exception as e:
            print(f"    ❌ {file}: Error reading - {e}")
    
    # Look for applied_companies directories
    applied_companies_dirs = list(Path(".").rglob("applied_companies"))
    print(f"\n🏢 Found {len(applied_companies_dirs)} applied_companies directories:")
    for dir_path in applied_companies_dirs:
        if dir_path.is_dir():
            companies = [d for d in dir_path.iterdir() if d.is_dir()]
            print(f"  📁 {dir_path}: {len(companies)} companies")
            for company in companies[:3]:  # Show first 3 companies
                print(f"    🏢 {company.name}")
                
                # Check for analysis files
                analysis_files = list(company.glob("*.json"))
                print(f"      📄 {len(analysis_files)} analysis files")
                for file in analysis_files[:3]:  # Show first 3 files
                    print(f"        📄 {file.name}")
    
    # Look for tailored CV files
    tailored_cv_files = list(Path(".").rglob("*_tailored_cv_*.json"))
    print(f"\n📄 Found {len(tailored_cv_files)} tailored CV files:")
    for file in tailored_cv_files[:5]:  # Show first 5 files
        try:
            size = file.stat().st_size
            modified = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"  📄 {file.name} ({size} bytes, {modified})")
        except Exception as e:
            print(f"  ❌ {file.name}: Error - {e}")
    
    # Check Docker container status
    print("\n🐳 Docker Container Status:")
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Docker containers running:")
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    print(f"    {line}")
        else:
            print("  ❌ Docker not accessible")
    except Exception as e:
        print(f"  ❌ Docker error: {e}")
    
    # Check server logs
    print("\n📋 Server Logs (last 20 lines):")
    try:
        import subprocess
        result = subprocess.run(['docker', 'logs', '--tail', '20', 'cv-magic-app'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  📄 Recent server logs:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"    {line}")
        else:
            print("  ❌ Could not get server logs")
    except Exception as e:
        print(f"  ❌ Log error: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Debug Complete!")
    print("\n💡 If you see:")
    print("  - No saved_jobs.json files → Job tracking will show 404")
    print("  - No applied_companies → No analyzed jobs")
    print("  - No tailored CV files → Preview/download will fail")
    print("  - Docker container not running → Server is down")

if __name__ == "__main__":
    debug_vps_files()
