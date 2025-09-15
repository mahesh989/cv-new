#!/usr/bin/env python3
"""
Comprehensive CV-JD Matching Analysis Test

This script tests the CV-JD matching analysis functionality including:
- API endpoint testing (/preliminary-analysis)
- Data extraction and validation
- Matching algorithm accuracy
- Error handling
- Authentication

Run this script to verify that CV-JD matching analysis is working correctly.
"""

import asyncio
import aiohttp
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "api_version": "v1",
    "timeout": 30,
    "debug": True
}

# Sample CV content for testing
SAMPLE_CV_CONTENT = """
John Doe
Senior Software Engineer

EXPERIENCE:
• 5+ years of experience in Python development
• Expertise in Django, Flask, FastAPI frameworks
• Strong knowledge of SQL databases (PostgreSQL, MySQL)
• Experience with cloud platforms (AWS, Azure)
• Proficient in JavaScript, React, Node.js
• Docker and Kubernetes containerization
• Git version control and CI/CD pipelines
• Machine learning with TensorFlow and PyTorch
• Data analysis using pandas and numpy
• RESTful API development and microservices
• Agile methodology and team leadership
• Excellent communication and problem-solving skills

EDUCATION:
• Bachelor of Science in Computer Science
• AWS Certified Solutions Architect

PROJECTS:
• Built scalable web applications serving 100k+ users
• Developed ML models for predictive analytics
• Led team of 5 developers in agile environment
"""

# Sample JD content for testing
SAMPLE_JD_CONTENT = """
Senior Python Developer Position

We are seeking a Senior Python Developer to join our growing team.

Required Skills:
• 3+ years of Python programming experience
• Experience with Django or Flask frameworks
• Knowledge of SQL databases
• RESTful API development
• Git version control
• Strong problem-solving abilities
• Excellent communication skills

Preferred Skills:
• Cloud experience (AWS preferred)
• Docker containerization
• JavaScript and React knowledge
• Machine learning experience
• Leadership experience
• Agile/Scrum methodology
• Data analysis skills

Responsibilities:
• Design and develop scalable Python applications
• Collaborate with cross-functional teams
• Mentor junior developers
• Participate in code reviews
• Implement best practices
"""

class CVJDMatchingTester:
    """Comprehensive tester for CV-JD matching analysis"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TEST_CONFIG["timeout"]))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, status: str, details: str = "", data: Any = None):
        """Log test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if TEST_CONFIG["debug"] and data:
            print(f"   Data: {json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}")
    
    async def authenticate(self) -> bool:
        """Get authentication token"""
        try:
            login_url = f"{self.base_url}/api/quick-login"
            async with self.session.post(login_url) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    self.auth_token = auth_data.get('access_token')
                    self.log_test("Authentication", "PASS", "Successfully obtained auth token")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Authentication", "FAIL", f"Status: {response.status}, Error: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Authentication", "FAIL", f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if not self.auth_token:
            return {"Content-Type": "application/json"}
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    async def setup_test_files(self) -> bool:
        """Setup required test files"""
        try:
            # Ensure CV analysis directory exists
            base_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis")
            base_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test CV file
            cv_file = base_dir / "test_cv.json"
            with open(cv_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "text": SAMPLE_CV_CONTENT,
                    "created_at": datetime.now().isoformat(),
                    "filename": "test_cv.pdf"
                }, f, indent=2, ensure_ascii=False)
            
            # Create original CV file (required by some endpoints)
            original_cv_file = base_dir / "original_cv.json"
            with open(original_cv_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "text": SAMPLE_CV_CONTENT,
                    "created_at": datetime.now().isoformat(),
                    "source": "test"
                }, f, indent=2, ensure_ascii=False)
            
            self.log_test("File Setup", "PASS", f"Created test files: {cv_file}, {original_cv_file}")
            return True
            
        except Exception as e:
            self.log_test("File Setup", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def test_preliminary_analysis_endpoint(self) -> bool:
        """Test the /preliminary-analysis endpoint"""
        try:
            url = f"{self.base_url}/api/preliminary-analysis"
            data = {
                "cv_filename": "test_cv.pdf",
                "jd_text": SAMPLE_JD_CONTENT,
                "config_name": None
            }
            
            headers = self.get_auth_headers()
            
            async with self.session.post(url, json=data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    result = await response.json() if response.content_type == 'application/json' else json.loads(response_text)
                    
                    # Validate response structure
                    required_fields = ["cv_skills", "jd_skills"]
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if missing_fields:
                        self.log_test("Preliminary Analysis API", "FAIL", 
                                    f"Missing required fields: {missing_fields}", result)
                        return False
                    
                    self.log_test("Preliminary Analysis API", "PASS", 
                                "Successfully called preliminary analysis endpoint", {
                                    "cv_skills_count": len(result.get("cv_skills", {})),
                                    "jd_skills_count": len(result.get("jd_skills", {})),
                                    "has_matching_data": "analyze_match" in result
                                })
                    return True
                else:
                    self.log_test("Preliminary Analysis API", "FAIL", 
                                f"HTTP {response.status}: {response_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Preliminary Analysis API", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def test_cv_skill_extraction(self) -> bool:
        """Test CV skill extraction accuracy"""
        try:
            url = f"{self.base_url}/api/preliminary-analysis"
            data = {
                "cv_filename": "test_cv.pdf",
                "jd_text": SAMPLE_JD_CONTENT,
                "config_name": None
            }
            
            headers = self.get_auth_headers()
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    cv_skills = result.get("cv_skills", {})
                    
                    # Expected skills that should be extracted from sample CV
                    expected_technical_skills = ["python", "django", "sql", "javascript", "docker"]
                    expected_soft_skills = ["communication", "leadership", "problem"]
                    
                    technical_skills = cv_skills.get("technical_skills", [])
                    soft_skills = cv_skills.get("soft_skills", [])
                    
                    # Check if at least some expected skills are found
                    found_technical = sum(1 for skill in expected_technical_skills 
                                        if any(skill.lower() in extracted.lower() 
                                               for extracted in technical_skills))
                    
                    found_soft = sum(1 for skill in expected_soft_skills 
                                   if any(skill.lower() in extracted.lower() 
                                          for extracted in soft_skills))
                    
                    if found_technical >= 3 and found_soft >= 1:
                        self.log_test("CV Skill Extraction", "PASS", 
                                    f"Found {found_technical}/5 technical and {found_soft}/3 soft skills", {
                                        "technical_skills": technical_skills,
                                        "soft_skills": soft_skills
                                    })
                        return True
                    else:
                        self.log_test("CV Skill Extraction", "FAIL", 
                                    f"Only found {found_technical}/5 technical and {found_soft}/3 soft skills", {
                                        "technical_skills": technical_skills,
                                        "soft_skills": soft_skills
                                    })
                        return False
                else:
                    self.log_test("CV Skill Extraction", "FAIL", f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("CV Skill Extraction", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def test_jd_skill_extraction(self) -> bool:
        """Test JD skill extraction accuracy"""
        try:
            url = f"{self.base_url}/api/preliminary-analysis"
            data = {
                "cv_filename": "test_cv.pdf",
                "jd_text": SAMPLE_JD_CONTENT,
                "config_name": None
            }
            
            headers = self.get_auth_headers()
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    jd_skills = result.get("jd_skills", {})
                    
                    # Expected skills from the sample JD
                    expected_requirements = ["python", "django", "sql", "api", "git"]
                    expected_soft = ["communication", "problem"]
                    
                    technical_skills = jd_skills.get("technical_skills", [])
                    soft_skills = jd_skills.get("soft_skills", [])
                    
                    found_technical = sum(1 for skill in expected_requirements 
                                        if any(skill.lower() in extracted.lower() 
                                               for extracted in technical_skills))
                    
                    found_soft = sum(1 for skill in expected_soft 
                                   if any(skill.lower() in extracted.lower() 
                                          for extracted in soft_skills))
                    
                    if found_technical >= 3 and found_soft >= 1:
                        self.log_test("JD Skill Extraction", "PASS", 
                                    f"Found {found_technical}/5 technical and {found_soft}/2 soft skills", {
                                        "technical_skills": technical_skills,
                                        "soft_skills": soft_skills
                                    })
                        return True
                    else:
                        self.log_test("JD Skill Extraction", "FAIL", 
                                    f"Only found {found_technical}/5 technical and {found_soft}/2 soft skills", {
                                        "technical_skills": technical_skills,
                                        "soft_skills": soft_skills
                                    })
                        return False
                else:
                    self.log_test("JD Skill Extraction", "FAIL", f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("JD Skill Extraction", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def test_matching_analysis(self) -> bool:
        """Test the CV-JD matching analysis"""
        try:
            url = f"{self.base_url}/api/preliminary-analysis"
            data = {
                "cv_filename": "test_cv.pdf",
                "jd_text": SAMPLE_JD_CONTENT,
                "config_name": None
            }
            
            headers = self.get_auth_headers()
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if matching analysis is present
                    has_analyze_match = "analyze_match" in result
                    has_comprehensive_analysis = "cv_comprehensive_analysis" in result and "jd_comprehensive_analysis" in result
                    
                    if has_analyze_match or has_comprehensive_analysis:
                        analyze_match = result.get("analyze_match", {})
                        
                        self.log_test("CV-JD Matching Analysis", "PASS", 
                                    "Matching analysis data is present", {
                                        "has_analyze_match": has_analyze_match,
                                        "has_comprehensive_analysis": has_comprehensive_analysis,
                                        "match_data_keys": list(analyze_match.keys()) if analyze_match else []
                                    })
                        return True
                    else:
                        self.log_test("CV-JD Matching Analysis", "FAIL", 
                                    "No matching analysis data found in response")
                        return False
                else:
                    self.log_test("CV-JD Matching Analysis", "FAIL", f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("CV-JD Matching Analysis", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling for invalid inputs"""
        test_cases = [
            {
                "name": "Missing CV filename",
                "data": {"jd_text": SAMPLE_JD_CONTENT},
                "expected_status": 400
            },
            {
                "name": "Missing JD text",
                "data": {"cv_filename": "test_cv.pdf"},
                "expected_status": 400
            },
            {
                "name": "Empty JD text",
                "data": {"cv_filename": "test_cv.pdf", "jd_text": ""},
                "expected_status": 400
            },
            {
                "name": "Non-existent CV file",
                "data": {"cv_filename": "nonexistent.pdf", "jd_text": SAMPLE_JD_CONTENT},
                "expected_status": 404
            }
        ]
        
        passed_tests = 0
        
        for test_case in test_cases:
            try:
                url = f"{self.base_url}/api/preliminary-analysis"
                headers = self.get_auth_headers()
                
                async with self.session.post(url, json=test_case["data"], headers=headers) as response:
                    if response.status == test_case["expected_status"]:
                        self.log_test(f"Error Handling - {test_case['name']}", "PASS", 
                                    f"Correctly returned status {response.status}")
                        passed_tests += 1
                    else:
                        error_text = await response.text()
                        self.log_test(f"Error Handling - {test_case['name']}", "FAIL", 
                                    f"Expected {test_case['expected_status']}, got {response.status}: {error_text}")
                        
            except Exception as e:
                self.log_test(f"Error Handling - {test_case['name']}", "FAIL", f"Exception: {str(e)}")
        
        success = passed_tests >= len(test_cases) * 0.75  # 75% success rate
        overall_status = "PASS" if success else "FAIL"
        self.log_test("Error Handling Overall", overall_status, 
                    f"Passed {passed_tests}/{len(test_cases)} error handling tests")
        
        return success
    
    async def test_authentication_required(self) -> bool:
        """Test that authentication is properly required"""
        try:
            url = f"{self.base_url}/api/preliminary-analysis"
            data = {
                "cv_filename": "test_cv.pdf",
                "jd_text": SAMPLE_JD_CONTENT
            }
            
            # Make request without authentication
            headers = {"Content-Type": "application/json"}
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 401:
                    self.log_test("Authentication Required", "PASS", 
                                "Correctly rejected unauthenticated request")
                    return True
                else:
                    self.log_test("Authentication Required", "FAIL", 
                                f"Expected 401, got {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Authentication Required", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results summary"""
        print("🚀 Starting Comprehensive CV-JD Matching Analysis Tests")
        print("=" * 60)
        
        # Setup
        setup_success = await self.setup_test_files()
        if not setup_success:
            return {"success": False, "error": "Failed to setup test files"}
        
        # Authentication
        auth_success = await self.authenticate()
        if not auth_success:
            return {"success": False, "error": "Failed to authenticate"}
        
        # Run tests
        test_functions = [
            self.test_authentication_required,
            self.test_preliminary_analysis_endpoint,
            self.test_cv_skill_extraction,
            self.test_jd_skill_extraction,
            self.test_matching_analysis,
            self.test_error_handling
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                success = await test_func()
                if success:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test function {test_func.__name__} failed with exception: {e}")
        
        # Results summary
        success_rate = (passed_tests / total_tests) * 100
        overall_success = success_rate >= 75  # 75% pass rate required
        
        summary = {
            "success": overall_success,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "timestamp": datetime.now().isoformat(),
            "test_results": self.test_results
        }
        
        print("\n" + "=" * 60)
        print(f"🎯 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Overall Status: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("\n🎉 CV-JD Matching Analysis is working correctly!")
        else:
            print("\n⚠️ CV-JD Matching Analysis has issues that need attention.")
        
        return summary


async def main():
    """Main function to run the CV-JD matching tests"""
    try:
        async with CVJDMatchingTester(TEST_CONFIG["base_url"]) as tester:
            results = await tester.run_all_tests()
            
            # Save results to file
            results_file = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/test_results_cv_jd_matching.json")
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📁 Detailed test results saved to: {results_file}")
            
            # Exit with appropriate code
            sys.exit(0 if results["success"] else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if server is likely running
    print("🔍 CV-JD Matching Analysis Test Suite")
    print(f"Target server: {TEST_CONFIG['base_url']}")
    print("\nEnsure the FastAPI server is running before starting tests...")
    print("Press Ctrl+C to cancel, or wait 3 seconds to continue...")
    
    try:
        import time
        time.sleep(3)
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Tests cancelled by user")
        sys.exit(0)
