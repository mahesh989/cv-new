#!/usr/bin/env python3
"""
Comprehensive test script to show detailed debug output for jd_text and cv_text
"""

import requests
import json
import time

# Server URL
BASE_URL = "http://localhost:8000"

def test_jd_text_debug():
    """Test to see jd_text content in debug output"""
    print("🔍 Testing JD Text Debug Output")
    print("=" * 80)
    
    # Sample JD text with more content
    sample_jd = """
    Senior Data Analyst - No To Violence
    
    About the Role:
    We are seeking a Senior Data Analyst to join our dynamic team. This role is crucial for supporting our mission to end family violence through data-driven insights and strategic reporting.
    
    Key Responsibilities:
    - Lead Business Intelligence (BI) initiatives and systems administration
    - Conduct comprehensive data analytics and create insightful reports
    - Utilize Microsoft Excel (Advanced) for complex data manipulation
    - Manage Management Information Systems and ensure data integrity
    - Develop and maintain KPI reporting frameworks
    - Collect and analyze data from various sources
    - Implement data storage and retrieval systems
    
    Requirements:
    - 5+ years experience in data analytics or related field
    - Proficiency in Business Intelligence tools and systems
    - Advanced Microsoft Excel skills
    - Experience in family violence sector highly preferred
    - Strong communication and leadership skills
    - Change management experience
    - Ability to work with diverse stakeholders
    
    Technical Skills:
    - Business Intelligence (BI) tools
    - Data Analytics and Reporting
    - Microsoft Excel (Advanced)
    - Database Management
    - Systems Administration
    - KPI Development and Monitoring
    
    Soft Skills:
    - Leadership and Team Management
    - Change Management
    - Communication and Presentation
    - Stakeholder Engagement
    - Problem Solving and Critical Thinking
    
    Domain Knowledge:
    - Family Violence Sector
    - Men's Referral Service
    - Brief Intervention Services
    - Perpetrator Accommodation Support Service
    - Peak Body Organizations
    - Regulatory and Governance Requirements
    """
    
    print(f"📄 Sample JD Text Length: {len(sample_jd)} characters")
    print(f"📄 Sample JD Text Preview:")
    print("-" * 40)
    print(sample_jd[:500] + "..." if len(sample_jd) > 500 else sample_jd)
    print("-" * 40)
    
    try:
        print("\n🚀 Sending JD text to /extract-jd-skills/ endpoint...")
        response = requests.post(
            f"{BASE_URL}/extract-jd-skills/",
            json={"jd_text": sample_jd},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ JD skills extraction successful!")
            result = response.json()
            print(f"📊 Extracted Skills:")
            print(f"   Technical: {result.get('technical_skills', [])}")
            print(f"   Soft: {result.get('soft_skills', [])}")
            print(f"   Domain: {result.get('domain_keywords', [])}")
            print(f"   Quality Metrics: {result.get('quality_metrics', {})}")
        else:
            print(f"❌ JD skills extraction failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_cv_text_debug():
    """Test to see cv_text content in debug output"""
    print("\n🔍 Testing CV Text Debug Output")
    print("=" * 80)
    
    # First, get available CVs
    try:
        response = requests.get(f"{BASE_URL}/list-cvs/")
        if response.status_code == 200:
            cvs = response.json()
            print(f"📁 Available CVs: {cvs.get('uploaded_cvs', [])}")
            
            if cvs.get("uploaded_cvs"):
                # Test with a few different CVs
                for cv_filename in cvs["uploaded_cvs"][:3]:  # Test first 3 CVs
                    print(f"\n📄 Testing CV: {cv_filename}")
                    print("-" * 40)
                    
                    # Get CV content
                    content_response = requests.get(f"{BASE_URL}/get-cv-content/{cv_filename}")
                    if content_response.status_code == 200:
                        cv_text = content_response.text
                        print(f"📄 CV Text Length: {len(cv_text)} characters")
                        print(f"📄 CV Text Preview:")
                        print("-" * 20)
                        print(cv_text[:300] + "..." if len(cv_text) > 300 else cv_text)
                        print("-" * 20)
                        
                        # Test CV skills extraction
                        print(f"\n🚀 Sending CV text to /extract-cv-skills/ endpoint...")
                        skills_response = requests.post(
                            f"{BASE_URL}/extract-cv-skills/",
                            json={"cv_filename": cv_filename},
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if skills_response.status_code == 200:
                            print("✅ CV skills extraction successful!")
                            result = skills_response.json()
                            print(f"📊 Extracted Skills:")
                            print(f"   Technical: {result.get('technical_skills', [])}")
                            print(f"   Soft: {result.get('soft_skills', [])}")
                            print(f"   Domain: {result.get('domain_keywords', [])}")
                        else:
                            print(f"❌ CV skills extraction failed: {skills_response.status_code}")
                    else:
                        print(f"❌ Failed to get CV content: {content_response.status_code}")
            else:
                print("❌ No CVs available for testing")
        else:
            print(f"❌ Failed to list CVs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_ats_with_both_texts():
    """Test ATS endpoint to see both jd_text and cv_text in debug output"""
    print("\n🔍 Testing ATS with Both JD and CV Text")
    print("=" * 80)
    
    # Sample JD text
    sample_jd = """
    Data Analyst Position
    
    We are looking for a Data Analyst with:
    - Python programming skills
    - SQL database experience
    - Data visualization expertise
    - Business intelligence tools
    - Stakeholder management
    - Communication skills
    """
    
    # Get a CV to test with
    try:
        response = requests.get(f"{BASE_URL}/list-cvs/")
        if response.status_code == 200:
            cvs = response.json()
            
            if cvs.get("uploaded_cvs"):
                cv_filename = cvs["uploaded_cvs"][0]
                print(f"📄 Using CV: {cv_filename}")
                print(f"📄 Using JD: Sample Data Analyst position")
                
                # Test ATS endpoint
                print(f"\n🚀 Sending both JD and CV to /ats-test/ endpoint...")
                ats_response = requests.post(
                    f"{BASE_URL}/ats-test/",
                    json={
                        "cv_filename": cv_filename,
                        "jd_text": sample_jd
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if ats_response.status_code == 200:
                    print("✅ ATS test successful!")
                    result = ats_response.json()
                    print(f"📊 ATS Score: {result.get('ats_score', 'N/A')}")
                    print(f"📊 Match Percentage: {result.get('match_percentage', 'N/A')}")
                else:
                    print(f"❌ ATS test failed: {ats_response.status_code}")
                    print(f"Error: {ats_response.text}")
            else:
                print("❌ No CVs available for ATS testing")
        else:
            print(f"❌ Failed to list CVs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Comprehensive Debug Print Testing")
    print("=" * 80)
    print("This script will trigger debug prints showing jd_text and cv_text content")
    print("Check the server terminal for detailed debug output!")
    print("=" * 80)
    
    # Wait for server to be ready
    time.sleep(2)
    
    # Run comprehensive tests
    test_jd_text_debug()
    test_cv_text_debug()
    test_ats_with_both_texts()
    
    print("\n✅ All debug tests completed!")
    print("🔍 Check the server terminal for debug output showing:")
    print("   - JD text content and length")
    print("   - CV text content and length") 
    print("   - Both texts when used in ATS testing") 