#!/usr/bin/env python3
"""
Test script for job information extraction API
"""
import requests
import json

def test_job_extraction():
    """Test the job information extraction endpoint"""
    
    # Sample job description
    sample_jd = """
    Software Engineer at Google
    
    About the Role:
    We are looking for a talented Software Engineer to join our team at Google.
    This position involves developing scalable web applications and working with
    cutting-edge technologies.
    
    Company: Google Inc.
    Location: Mountain View, CA
    
    Requirements:
    - Bachelor's degree in Computer Science
    - 3+ years of experience in software development
    - Proficiency in Python, Java, or Go
    """
    
    # Test data
    test_data = {
        "job_description": sample_jd
    }
    
    try:
        # Make API call
        response = requests.post(
            "http://127.0.0.1:8000/api/llm/extract-job-info",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Job extraction successful!")
            print(f"🎯 Job Title: {result.get('job_title')}")
            print(f"🏢 Company: {result.get('company')}")
            return True
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing job extraction: {e}")
        return False

def test_fallback_extraction():
    """Test with a more complex job description"""
    
    complex_jd = """
    Senior Frontend Developer Position
    
    We are currently seeking a Senior Frontend Developer to join our 
    innovative team at TechCorp Solutions. This role will focus on 
    building modern web applications using React and TypeScript.
    
    About TechCorp Solutions:
    We are a fast-growing startup in the fintech space...
    
    What you'll do:
    - Develop user interfaces using React
    - Collaborate with backend engineers
    - Optimize application performance
    """
    
    test_data = {
        "job_description": complex_jd
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/llm/extract-job-info",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Complex extraction successful!")
            print(f"🎯 Job Title: {result.get('job_title')}")
            print(f"🏢 Company: {result.get('company')}")
            return True
        else:
            print(f"❌ Complex extraction failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing complex extraction: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Job Information Extraction API")
    print("=" * 50)
    
    # Test basic extraction
    success1 = test_job_extraction()
    
    # Test complex extraction
    success2 = test_fallback_extraction()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All tests passed! Job extraction is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the backend API.") 