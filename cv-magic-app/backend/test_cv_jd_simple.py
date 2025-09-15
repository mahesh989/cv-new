#!/usr/bin/env python3
"""
Simple CV-JD Matching Test

This script tests the CV-JD matching functionality using the existing GfK analysis
that we know works.
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path
from datetime import datetime

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "debug": True
}

class SimpleCVJDTester:
    """Simple tester for CV-JD matching using existing data"""
    
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
    
    def log_test(self, test_name: str, status: str, details: str = "", data: any = None):
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
            login_url = f"{self.base_url}/api/auth/login"
            login_data = {
                "email": "demo@cvagent.com",
                "password": "demo123"
            }
            
            async with self.session.post(login_url, json=login_data) as response:
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
    
    def get_auth_headers(self) -> dict:
        """Get authentication headers"""
        if not self.auth_token:
            return {"Content-Type": "application/json"}
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    async def test_cv_jd_matching_status(self) -> bool:
        """Test CV-JD matching status endpoint"""
        try:
            url = f"{self.base_url}/api/cv-jd-matching/status/GfK"
            headers = self.get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if the response has the expected structure
                    if result.get("success") and "data" in result:
                        data = result["data"]
                        required_fields = ["company_name", "cv_file_exists", "jd_analysis_exists", "match_results_exists"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            self.log_test("CV-JD Matching Status", "FAIL", 
                                        f"Missing required fields: {missing_fields}", result)
                            return False
                        
                        self.log_test("CV-JD Matching Status", "PASS", 
                                    "Successfully retrieved CV-JD matching status", {
                                        "company": data.get("company_name"),
                                        "cv_exists": data.get("cv_file_exists"),
                                        "jd_exists": data.get("jd_analysis_exists"),
                                        "match_exists": data.get("match_results_exists")
                                    })
                        return True
                    else:
                        self.log_test("CV-JD Matching Status", "FAIL", 
                                    "Invalid response structure", result)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("CV-JD Matching Status", "FAIL", 
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("CV-JD Matching Status", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def test_cv_jd_match_results(self) -> bool:
        """Test CV-JD match results endpoint"""
        try:
            url = f"{self.base_url}/api/cv-jd-matching/results/GfK"
            headers = self.get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if the response has the expected structure
                    if result.get("success") and "data" in result:
                        data = result["data"]
                        required_fields = ["matched_required_keywords", "matched_preferred_keywords", "match_counts"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            self.log_test("CV-JD Match Results", "FAIL", 
                                        f"Missing required fields: {missing_fields}", result)
                            return False
                        
                        match_counts = data.get("match_counts", {})
                        self.log_test("CV-JD Match Results", "PASS", 
                                    "Successfully retrieved CV-JD match results", {
                                        "matched_required": len(data.get("matched_required_keywords", [])),
                                        "matched_preferred": len(data.get("matched_preferred_keywords", [])),
                                        "total_required": match_counts.get("total_required_keywords", 0),
                                        "total_preferred": match_counts.get("total_preferred_keywords", 0)
                                    })
                        return True
                    else:
                        self.log_test("CV-JD Match Results", "FAIL", 
                                    "Invalid response structure", result)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("CV-JD Match Results", "FAIL", 
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("CV-JD Match Results", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def test_match_percentage(self) -> bool:
        """Test match percentage endpoint"""
        try:
            url = f"{self.base_url}/api/cv-jd-matching/match-percentage/GfK"
            headers = self.get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check if the response has the expected structure
                    if result.get("success") and "data" in result:
                        data = result["data"]
                        required_fields = ["match_percentages", "match_counts"]
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if missing_fields:
                            self.log_test("Match Percentage", "FAIL", 
                                        f"Missing required fields: {missing_fields}", result)
                            return False
                        
                        percentages = data.get("match_percentages", {})
                        self.log_test("Match Percentage", "PASS", 
                                    "Successfully retrieved match percentages", {
                                        "overall_match": percentages.get("overall_match_percentage", 0),
                                        "required_match": percentages.get("required_match_percentage", 0),
                                        "preferred_match": percentages.get("preferred_match_percentage", 0)
                                    })
                        return True
                    else:
                        self.log_test("Match Percentage", "FAIL", 
                                    "Invalid response structure", result)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Match Percentage", "FAIL", 
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Match Percentage", "FAIL", f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self) -> dict:
        """Run all tests and return results summary"""
        print("🚀 Starting Simple CV-JD Matching Tests")
        print("=" * 50)
        
        # Authentication
        auth_success = await self.authenticate()
        if not auth_success:
            return {"success": False, "error": "Failed to authenticate"}
        
        # Run tests
        test_functions = [
            self.test_cv_jd_matching_status,
            self.test_cv_jd_match_results,
            self.test_match_percentage
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
        
        print("\n" + "=" * 50)
        print(f"🎯 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Overall Status: {'✅ PASS' if overall_success else '❌ FAIL'}")
        
        if overall_success:
            print("\n🎉 CV-JD Matching is working correctly!")
        else:
            print("\n⚠️ CV-JD Matching has issues that need attention.")
        
        return summary


async def main():
    """Main function to run the simple CV-JD matching tests"""
    try:
        async with SimpleCVJDTester(TEST_CONFIG["base_url"]) as tester:
            results = await tester.run_all_tests()
            
            # Save results to file
            results_file = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/test_results_simple_cv_jd.json")
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
    print("🔍 Simple CV-JD Matching Test Suite")
    print(f"Target server: {TEST_CONFIG['base_url']}")
    print("\nTesting CV-JD matching using existing GfK analysis...")
    
    asyncio.run(main())
