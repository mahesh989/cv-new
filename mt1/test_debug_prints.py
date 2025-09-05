#!/usr/bin/env python3
"""
Test script to trigger debug prints for jd_text and cv_text
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8000"

def test_jd_scraping():
    """Test JD scraping to see jd_text debug output"""
    print("🔍 Testing JD scraping debug prints...")
    print("=" * 60)
    
    # Test URL (you can change this to any job posting URL)
    test_url = "https://www.seek.com.au/job/12345678"
    
    try:
        response = requests.post(
            f"{BASE_URL}/scrape-job-description/",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ JD scraping successful")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ JD scraping failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing JD scraping: {e}")

def test_jd_skills_extraction():
    """Test JD skills extraction to see jd_text debug output"""
    print("\n🔍 Testing JD skills extraction debug prints...")
    print("=" * 60)
    
    # Sample JD text
    sample_jd = """
    Data Analyst - No To Violence
    
    We are seeking a Data Analyst to join our team. The role involves:
    - Business Intelligence (BI) tools and systems administration
    - Data analytics and reporting
    - Microsoft Excel (Advanced)
    - Management Information Systems
    - KPI reporting and data collection
    
    Requirements:
    - Experience in family violence sector preferred
    - Strong communication and leadership skills
    - Change management experience
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/extract-jd-skills/",
            json={"jd_text": sample_jd},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ JD skills extraction successful")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ JD skills extraction failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing JD skills extraction: {e}")

def test_cv_skills_extraction():
    """Test CV skills extraction to see cv_text debug output"""
    print("\n🔍 Testing CV skills extraction debug prints...")
    print("=" * 60)
    
    # First, check what CVs are available
    try:
        response = requests.get(f"{BASE_URL}/list-cvs/")
        if response.status_code == 200:
            cvs = response.json()
            print(f"Available CVs: {cvs}")
            
            if cvs.get("uploaded_cvs"):
                cv_filename = cvs["uploaded_cvs"][0]  # Use first available CV
                print(f"Testing with CV: {cv_filename}")
                
                # Test CV skills extraction
                response = requests.post(
                    f"{BASE_URL}/extract-cv-skills/",
                    json={"cv_filename": cv_filename},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print("✅ CV skills extraction successful")
                    print(f"Response: {json.dumps(response.json(), indent=2)}")
                else:
                    print(f"❌ CV skills extraction failed: {response.status_code}")
                    print(f"Error: {response.text}")
            else:
                print("❌ No CVs available for testing")
        else:
            print(f"❌ Failed to list CVs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing CV skills extraction: {e}")

def test_cv_content():
    """Test CV content retrieval to see cv_text debug output"""
    print("\n🔍 Testing CV content retrieval debug prints...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/list-cvs/")
        if response.status_code == 200:
            cvs = response.json()
            
            if cvs.get("uploaded_cvs"):
                cv_filename = cvs["uploaded_cvs"][0]  # Use first available CV
                print(f"Testing CV content for: {cv_filename}")
                
                # Test CV content retrieval
                response = requests.get(f"{BASE_URL}/get-cv-content/{cv_filename}")
                
                if response.status_code == 200:
                    print("✅ CV content retrieval successful")
                    print(f"CV Text Length: {len(response.text)} characters")
                    print(f"First 500 chars: {response.text[:500]}...")
                else:
                    print(f"❌ CV content retrieval failed: {response.status_code}")
                    print(f"Error: {response.text}")
            else:
                print("❌ No CVs available for testing")
        else:
            print(f"❌ Failed to list CVs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing CV content retrieval: {e}")

if __name__ == "__main__":
    print("🧪 Testing Debug Prints for JD and CV Text")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    # Run tests
    test_jd_skills_extraction()
    test_cv_skills_extraction()
    test_cv_content()
    
    print("\n✅ Debug print tests completed!")
    print("Check the server terminal for debug output showing jd_text and cv_text content.") 