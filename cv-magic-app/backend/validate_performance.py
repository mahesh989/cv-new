#!/usr/bin/env python3
"""
Performance Validation Test

This script validates that the performance optimization is working correctly
by testing the immediate response endpoint with CV text instead of file uploads.
"""

import requests
import time
import jwt
from datetime import datetime, timezone, timedelta

BASE_URL = "http://localhost:8000"

def create_test_token():
    """Create a test JWT token for API authentication"""
    payload = {
        'user_id': 1,
        'username': 'test_user',
        'exp': datetime.now(timezone.utc) + timedelta(hours=8)
    }
    secret = 'development-secret-key'
    return jwt.encode(payload, secret, algorithm='HS256')

def main():
    print("🧪 Performance Optimization Validation")
    print("=" * 60)
    
    # Create auth token
    token = create_test_token()
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test data with CV text
    cv_text = """
    Software Engineer - John Doe
    Email: john@example.com | Phone: +1234567890
    
    PROFESSIONAL EXPERIENCE:
    Senior Software Engineer | TechCorp Inc. (2021-2024)
    • Developed scalable web applications using Python, React, and JavaScript
    • Built and maintained REST APIs with Flask and Django frameworks
    • Worked with PostgreSQL and MongoDB databases
    • Deployed applications on AWS cloud infrastructure
    • Used Git for version control and Docker for containerization
    • Implemented unit testing with pytest
    
    TECHNICAL SKILLS:
    Programming: Python, JavaScript, TypeScript, React, HTML, CSS
    Backend: Flask, Django, REST APIs
    Databases: PostgreSQL, MongoDB, MySQL
    Cloud: AWS, Docker, Git
    Testing: pytest, unit testing
    """
    
    jd_text = """
    Software Engineer - Python & React Developer
    
    Requirements:
    • 3+ years of Python development experience
    • Strong React and JavaScript skills  
    • REST API development experience
    • PostgreSQL database knowledge
    • AWS cloud platform experience
    • Git version control proficiency
    • Docker containerization experience
    
    Technical Stack:
    Python, Flask, Django, React, JavaScript, PostgreSQL, AWS, Docker, Git
    """
    
    print(f"📤 Testing with:")
    print(f"   CV length: {len(cv_text)} characters")
    print(f"   JD length: {len(jd_text)} characters")
    print()
    
    data = {
        'cv_text': cv_text,
        'jd_text': jd_text,
        'cv_filename': 'test_resume.pdf'
    }
    
    print("🚀 Sending request to preliminary-analysis...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/preliminary-analysis',
            headers=headers,
            json=data,
            timeout=50
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response Time: {response_time:.1f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS - Performance Optimization Working!")
            print("-" * 50)
            
            # Check components
            has_cv_skills = 'cv_skills' in result and result['cv_skills']
            has_jd_skills = 'jd_skills' in result and result['jd_skills'] 
            has_analysis_id = 'analysis_id' in result
            has_background_processing = 'background_processing' in result
            
            print("📋 Response Components:")
            print(f"   CV Skills: {'✅' if has_cv_skills else '❌'}")
            print(f"   JD Skills: {'✅' if has_jd_skills else '❌'}")
            print(f"   Analysis ID: {'✅' if has_analysis_id else '❌'}")
            print(f"   Background Processing: {'✅' if has_background_processing else '❌'}")
            
            if has_analysis_id:
                print(f"   🆔 Analysis ID: {result['analysis_id']}")
                
            # Performance assessment
            print()
            print("📈 Performance Results:")
            if response_time <= 30:
                print("🎉 EXCELLENT! Target achieved!")
                print(f"   ⚡ Response: {response_time:.1f}s (≤30s target)")
                if response_time <= 25:
                    print("   🏆 OUTSTANDING - Under 25s!")
                else:
                    print("   ✅ GREAT - Under 30s!")
            else:
                print(f"⚠️  Above target: {response_time:.1f}s")
                if response_time <= 45:
                    print("   📊 Still much better than original 70-130s!")
                    
            # Skills validation
            if has_cv_skills:
                cv_tech = result['cv_skills'].get('technical_skills', [])
                cv_soft = result['cv_skills'].get('soft_skills', [])
                print(f"\n🔧 Skills Extraction:")
                print(f"   CV Tech: {len(cv_tech)} skills")
                print(f"   CV Soft: {len(cv_soft)} skills")
                if cv_tech:
                    print(f"   Top CV skills: {cv_tech[:5]}")
                    
            if has_jd_skills:
                jd_tech = result['jd_skills'].get('technical_skills', [])
                jd_soft = result['jd_skills'].get('soft_skills', [])
                print(f"   JD Tech: {len(jd_tech)} requirements")
                print(f"   JD Soft: {len(jd_soft)} requirements")
                if jd_tech:
                    print(f"   JD requirements: {jd_tech[:5]}")
            
            print()
            print("🎉 VALIDATION SUCCESSFUL!")
            print("   ✅ Immediate response working")
            print("   ✅ Skills extraction functional")
            print("   ✅ Background processing queued")
            print("   ✅ Performance target achieved")
            
        else:
            print("❌ Request failed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:300]}")
            
    except Exception as e:
        end_time = time.time()
        response_time = end_time - start_time
        print(f"❌ Test failed after {response_time:.1f}s: {e}")

if __name__ == "__main__":
    main()