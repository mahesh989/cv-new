#!/usr/bin/env python3
"""
Test script for the enhanced CV analysis API

This script tests the key functionality of the enhanced backend:
- CV upload and processing
- JD extraction from URLs and text
- CV-JD analysis and skill matching

Usage:
    python test_enhanced_api.py
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000/api"
TEST_TIMEOUT = 30  # seconds


class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Test basic health check"""
        print("🏥 Testing health check...")
        
        try:
            async with self.session.get(f"{self.base_url.replace('/api', '')}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data['status']}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {str(e)}")
            return False
    
    async def test_cv_upload(self):
        """Test CV upload functionality"""
        print("\n📄 Testing CV upload...")
        
        # Create a sample CV content
        sample_cv_content = """
        John Doe
        Software Engineer
        Email: john.doe@example.com
        Phone: +1-234-567-8900
        
        EXPERIENCE:
        Senior Software Engineer (2020-Present)
        - Developed Python applications using Django and FastAPI
        - Worked with React and JavaScript for frontend development
        - Experience with AWS, Docker, and Kubernetes
        - Led team of 5 developers
        
        SKILLS:
        Technical: Python, JavaScript, React, Django, FastAPI, AWS, Docker, Git
        Soft Skills: Leadership, Communication, Project Management
        
        EDUCATION:
        Bachelor of Science in Computer Science (2018)
        University of Technology
        """
        
        try:
            # Create form data
            data = aiohttp.FormData()
            data.add_field('cv_file', sample_cv_content, filename='test_cv.txt', content_type='text/plain')
            data.add_field('title', 'Test CV - John Doe')
            data.add_field('description', 'Sample CV for testing purposes')
            
            async with self.session.post(f"{self.base_url}/cv-enhanced/upload", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    cv_id = result['id']
                    print(f"✅ CV uploaded successfully: ID={cv_id}")
                    
                    # Wait a bit for processing
                    await asyncio.sleep(2)
                    
                    # Test CV content retrieval
                    await self.test_cv_content(cv_id)
                    return cv_id
                else:
                    text = await response.text()
                    print(f"❌ CV upload failed: {response.status} - {text}")
                    return None
        except Exception as e:
            print(f"❌ CV upload error: {str(e)}")
            return None
    
    async def test_cv_content(self, cv_id: str):
        """Test CV content retrieval"""
        print(f"📖 Testing CV content retrieval for ID: {cv_id}")
        
        try:
            # Try to get CV content (may need to wait for processing)
            for attempt in range(5):
                async with self.session.get(f"{self.base_url}/cv-enhanced/{cv_id}") as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ CV content retrieved: {len(result['text_content'])} characters")
                        return True
                    elif response.status == 202:
                        print(f"⏳ CV still processing, attempt {attempt + 1}/5...")
                        await asyncio.sleep(2)
                    else:
                        text = await response.text()
                        print(f"❌ CV content retrieval failed: {response.status} - {text}")
                        return False
            
            print("❌ CV processing timeout")
            return False
            
        except Exception as e:
            print(f"❌ CV content retrieval error: {str(e)}")
            return False
    
    async def test_jd_extraction_text(self):
        """Test JD extraction from direct text"""
        print("\n💼 Testing JD extraction from text...")
        
        sample_jd_text = """
        Senior Software Engineer - Remote
        Company: Tech Innovations Inc.
        Location: San Francisco, CA (Remote)
        
        REQUIREMENTS:
        - 5+ years of experience in software development
        - Strong experience with Python, Django, FastAPI
        - Frontend development with React, JavaScript, TypeScript
        - Experience with cloud platforms (AWS, Azure)
        - Docker and Kubernetes experience required
        - Strong problem-solving and communication skills
        - Experience with Git, CI/CD pipelines
        
        RESPONSIBILITIES:
        - Lead development of web applications
        - Mentor junior developers
        - Collaborate with cross-functional teams
        - Design and implement scalable solutions
        
        NICE TO HAVE:
        - Machine learning experience
        - DevOps experience
        - Agile/Scrum methodology
        """
        
        try:
            payload = {
                "text": sample_jd_text,
                "title": "Senior Software Engineer",
                "company": "Tech Innovations Inc.",
                "location": "San Francisco, CA (Remote)"
            }
            
            async with self.session.post(
                f"{self.base_url}/jd-enhanced/extract-text", 
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    jd_id = result['id']
                    print(f"✅ JD extracted from text successfully: ID={jd_id}")
                    return jd_id
                else:
                    text = await response.text()
                    print(f"❌ JD extraction failed: {response.status} - {text}")
                    return None
        except Exception as e:
            print(f"❌ JD extraction error: {str(e)}")
            return None
    
    async def test_analysis(self, cv_id: str, jd_id: str):
        """Test CV-JD analysis"""
        print(f"\n🔍 Testing CV-JD analysis (CV: {cv_id}, JD: {jd_id})...")
        
        try:
            payload = {
                "cv_id": cv_id,
                "jd_id": jd_id,
                "analysis_type": "skill_match",
                "include_suggestions": True
            }
            
            async with self.session.post(
                f"{self.base_url}/analysis-enhanced/analyze",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    analysis_id = result['id']
                    print(f"✅ Analysis created successfully: ID={analysis_id}")
                    
                    # Wait a bit for analysis processing
                    await asyncio.sleep(3)
                    
                    # Get analysis result
                    await self.test_analysis_result(analysis_id)
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Analysis creation failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Analysis error: {str(e)}")
            return False
    
    async def test_analysis_result(self, analysis_id: str):
        """Test analysis result retrieval"""
        print(f"📊 Testing analysis result retrieval for ID: {analysis_id}")
        
        try:
            # Try to get analysis result (may need to wait for processing)
            for attempt in range(5):
                async with self.session.get(f"{self.base_url}/analysis-enhanced/{analysis_id}") as response:
                    if response.status == 200:
                        result = await response.json()
                        analysis_result = result.get('result', {})
                        
                        if analysis_result:
                            match_percentage = analysis_result.get('match_percentage', 0)
                            matched_skills = analysis_result.get('matched_skills', [])
                            missing_skills = analysis_result.get('missing_skills', [])
                            
                            print(f"✅ Analysis result retrieved:")
                            print(f"   Match percentage: {match_percentage}%")
                            print(f"   Matched skills: {len(matched_skills)}")
                            print(f"   Missing skills: {len(missing_skills)}")
                            print(f"   Sample matched skills: {matched_skills[:3]}")
                            print(f"   Sample missing skills: {missing_skills[:3]}")
                        else:
                            print("✅ Analysis result retrieved (no detailed results)")
                        
                        return True
                    elif response.status == 202:
                        print(f"⏳ Analysis still processing, attempt {attempt + 1}/5...")
                        await asyncio.sleep(3)
                    else:
                        text = await response.text()
                        print(f"❌ Analysis result retrieval failed: {response.status} - {text}")
                        return False
            
            print("❌ Analysis processing timeout")
            return False
            
        except Exception as e:
            print(f"❌ Analysis result retrieval error: {str(e)}")
            return False
    
    async def test_skill_extraction(self):
        """Test skill extraction functionality"""
        print("\n🎯 Testing skill extraction...")
        
        sample_text = """
        I am a software engineer with 5 years of experience in Python, JavaScript, and React.
        I have strong communication and leadership skills. I've worked with AWS, Docker, and 
        have experience in project management and teamwork.
        """
        
        try:
            payload = {
                "text": sample_text,
                "text_type": "cv",
                "extract_technical": True,
                "extract_soft": True
            }
            
            async with self.session.post(
                f"{self.base_url}/analysis-enhanced/extract-skills",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    technical_skills = result.get('technical_skills', [])
                    soft_skills = result.get('soft_skills', [])
                    
                    print(f"✅ Skill extraction successful:")
                    print(f"   Technical skills: {technical_skills}")
                    print(f"   Soft skills: {soft_skills}")
                    print(f"   Total skills found: {result.get('total_skills_found', 0)}")
                    return True
                else:
                    text = await response.text()
                    print(f"❌ Skill extraction failed: {response.status} - {text}")
                    return False
        except Exception as e:
            print(f"❌ Skill extraction error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Enhanced CV Analysis API Tests")
        print("=" * 50)
        
        results = {
            'health_check': False,
            'cv_upload': False,
            'jd_extraction': False,
            'analysis': False,
            'skill_extraction': False
        }
        
        # Test 1: Health check
        results['health_check'] = await self.test_health_check()
        if not results['health_check']:
            print("❌ Health check failed. Is the server running?")
            return results
        
        # Test 2: CV upload and processing
        cv_id = await self.test_cv_upload()
        results['cv_upload'] = cv_id is not None
        
        # Test 3: JD extraction
        jd_id = await self.test_jd_extraction_text()
        results['jd_extraction'] = jd_id is not None
        
        # Test 4: Analysis (if we have both CV and JD)
        if cv_id and jd_id:
            results['analysis'] = await self.test_analysis(cv_id, jd_id)
        
        # Test 5: Skill extraction
        results['skill_extraction'] = await self.test_skill_extraction()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY:")
        print("=" * 50)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title():<20} {status}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Enhanced API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the server logs for more details.")
        
        return results


async def main():
    """Main test function"""
    print("Enhanced CV Analysis API Test Suite")
    print(f"Testing against: {BASE_URL}")
    print()
    
    async with APITester(BASE_URL) as tester:
        results = await tester.run_all_tests()
        
        # Exit with appropriate code
        if all(results.values()):
            exit(0)  # Success
        else:
            exit(1)  # Some tests failed


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n💥 Test suite error: {str(e)}")
        exit(1)
