#!/usr/bin/env python3
"""
Test script for Phase 3: File System Restructuring
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_test_header(test_name):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['access_token']
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_server_connection():
    """Test if server is running"""
    print_test_header("Server Connection")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_result(True, "Server is running")
            return True
        else:
            print_result(False, f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Server connection failed: {e}")
        return False

def test_user_cv_upload(token):
    """Test user CV upload"""
    print_test_header("User CV Upload")
    
    # Create a test CV file
    test_content = b"This is a test CV content for Phase 3"
    
    try:
        files = {
            'file': ('test_cv_phase3.pdf', test_content, 'application/pdf')
        }
        data = {
            'title': 'Test CV Phase 3',
            'description': 'Test CV for Phase 3 testing'
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{API_BASE}/user/cv/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"CV uploaded successfully: {data['cv']['title']}")
            return data['cv']['id']
        else:
            print_result(False, f"CV upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_result(False, f"CV upload error: {e}")
        return None

def test_user_cv_listing(token):
    """Test user CV listing"""
    print_test_header("User CV Listing")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/user/cv/list",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"CV listing successful: {len(data['cvs'])} CVs")
            return True
        else:
            print_result(False, f"CV listing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"CV listing error: {e}")
        return False

def test_user_cv_stats(token):
    """Test user CV statistics"""
    print_test_header("User CV Statistics")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/user/cv/stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print_result(True, f"CV stats: {stats['total_cvs']} CVs, {stats['total_size_mb']} MB")
            return True
        else:
            print_result(False, f"CV stats failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"CV stats error: {e}")
        return False

def test_user_analysis_save(token, cv_id):
    """Test user analysis saving"""
    print_test_header("User Analysis Saving")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test skills analysis
        skills_data = {
            "technical_skills": ["Python", "FastAPI", "PostgreSQL"],
            "soft_skills": ["Communication", "Leadership"],
            "domain_keywords": ["Backend Development", "API Design"],
            "experience_years": 5,
            "education": "Computer Science Degree"
        }
        
        response = requests.post(
            f"{API_BASE}/user/analysis/skills/{cv_id}",
            json=skills_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print_result(True, "Skills analysis saved successfully")
        else:
            print_result(False, f"Skills analysis failed: {response.status_code} - {response.text}")
            return False
        
        # Test recommendations
        recommendations = {
            "recommendations": [
                "Add more technical skills",
                "Include project examples",
                "Highlight leadership experience"
            ],
            "priority": "high"
        }
        
        response = requests.post(
            f"{API_BASE}/user/analysis/recommendations/{cv_id}",
            json=recommendations,
            headers=headers
        )
        
        if response.status_code == 200:
            print_result(True, "Recommendations saved successfully")
        else:
            print_result(False, f"Recommendations failed: {response.status_code} - {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Analysis saving error: {e}")
        return False

def test_user_analysis_listing(token):
    """Test user analysis listing"""
    print_test_header("User Analysis Listing")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/user/analysis/list",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Analysis listing successful: {len(data['analyses'])} analyses")
            return True
        else:
            print_result(False, f"Analysis listing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Analysis listing error: {e}")
        return False

def test_user_job_application(token, cv_id):
    """Test user job application"""
    print_test_header("User Job Application")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test job description save
        job_data = {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "description": "Looking for a senior Python developer with FastAPI experience",
            "requirements": ["Python", "FastAPI", "PostgreSQL", "5+ years experience"]
        }
        
        response = requests.post(
            f"{API_BASE}/user/jobs/description",
            json=job_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print_result(True, "Job description saved successfully")
        else:
            print_result(False, f"Job description failed: {response.status_code} - {response.text}")
            return False
        
        # Test job application
        application_data = {
            "cv_id": cv_id,
            "job_title": "Senior Python Developer",
            "company": "Tech Corp",
            "job_url": "https://example.com/job/123",
            "job_description": "Looking for a senior Python developer",
            "status": "applied",
            "notes": "Applied via company website"
        }
        
        response = requests.post(
            f"{API_BASE}/user/jobs/application",
            json=application_data,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Job application saved: {data['application']['job_title']}")
            return True
        else:
            print_result(False, f"Job application failed: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print_result(False, f"Job application error: {e}")
        return False

def test_user_job_listing(token):
    """Test user job listing"""
    print_test_header("User Job Listing")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/user/jobs/applications",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Job applications listed: {len(data['applications'])} applications")
            return True
        else:
            print_result(False, f"Job listing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Job listing error: {e}")
        return False

def test_user_job_stats(token):
    """Test user job statistics"""
    print_test_header("User Job Statistics")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{API_BASE}/user/jobs/stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data['stats']
            print_result(True, f"Job stats: {stats['total_applications']} applications")
            return True
        else:
            print_result(False, f"Job stats failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Job stats error: {e}")
        return False

def test_file_system_structure():
    """Test file system structure"""
    print_test_header("File System Structure")
    
    import os
    from pathlib import Path
    
    try:
        # Check if user directory structure exists
        user_data_path = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/user_data")
        
        if not user_data_path.exists():
            print_result(False, "User data directory does not exist")
            return False
        
        # Check for user subdirectories
        users_path = user_data_path / "users"
        if not users_path.exists():
            print_result(False, "Users directory does not exist")
            return False
        
        # Check for test user directory
        test_user_path = users_path / "1"  # Assuming user ID 1
        if not test_user_path.exists():
            print_result(False, "Test user directory does not exist")
            return False
        
        # Check for required subdirectories
        required_dirs = [
            "cvs/original",
            "cvs/tailored",
            "cvs/processed",
            "analysis/skills",
            "analysis/recommendations",
            "analysis/results",
            "analysis/comparisons",
            "jobs/saved",
            "jobs/applications",
            "jobs/descriptions",
            "jobs/matches",
            "exports",
            "temp",
            "backups",
            "config",
            "logs"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = test_user_path / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            print_result(False, f"Missing directories: {missing_dirs}")
            return False
        
        print_result(True, "File system structure is correct")
        return True
        
    except Exception as e:
        print_result(False, f"File system structure error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PHASE 3 TESTING: File System Restructuring")
    print(f"Testing at: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    # Test results
    results = []
    
    # 1. Test server connection
    if not test_server_connection():
        print("\n❌ Server is not running. Please start the server first.")
        sys.exit(1)
    
    # 2. Get authentication token
    token = get_auth_token()
    if not token:
        print("\n❌ Authentication failed. Please ensure test user exists.")
        sys.exit(1)
    
    # 3. Test file system structure
    fs_structure_result = test_file_system_structure()
    results.append(("File System Structure", fs_structure_result))
    
    # 4. Test user CV upload
    cv_id = test_user_cv_upload(token)
    cv_upload_result = cv_id is not None
    results.append(("User CV Upload", cv_upload_result))
    
    # 5. Test user CV listing
    cv_listing_result = test_user_cv_listing(token)
    results.append(("User CV Listing", cv_listing_result))
    
    # 6. Test user CV stats
    cv_stats_result = test_user_cv_stats(token)
    results.append(("User CV Statistics", cv_stats_result))
    
    # 7. Test user analysis saving
    if cv_id:
        analysis_save_result = test_user_analysis_save(token, cv_id)
        results.append(("User Analysis Saving", analysis_save_result))
    else:
        results.append(("User Analysis Saving", False))
    
    # 8. Test user analysis listing
    analysis_listing_result = test_user_analysis_listing(token)
    results.append(("User Analysis Listing", analysis_listing_result))
    
    # 9. Test user job application
    if cv_id:
        job_application_result = test_user_job_application(token, cv_id)
        results.append(("User Job Application", job_application_result))
    else:
        results.append(("User Job Application", False))
    
    # 10. Test user job listing
    job_listing_result = test_user_job_listing(token)
    results.append(("User Job Listing", job_listing_result))
    
    # 11. Test user job stats
    job_stats_result = test_user_job_stats(token)
    results.append(("User Job Statistics", job_stats_result))
    
    # Print summary
    print_test_header("TEST SUMMARY")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 3 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
