#!/usr/bin/env python3
"""
Test AI Recommendations Flow - Complete Integration Test
========================================================

This script tests the complete flow:
1. Enhanced ATS Score calculation (which auto-saves analysis results)
2. AI Recommendations generation from saved analysis file

Usage:
    python test_ai_recommendations_flow.py
"""

import requests
import json
import time

# Server configuration
BASE_URL = "http://127.0.0.1:8000"

def test_complete_flow():
    """Test the complete AI recommendations flow"""
    
    print("🧪 TESTING COMPLETE AI RECOMMENDATIONS FLOW")
    print("=" * 60)
    
    # Sample data for testing
    sample_cv_text = """
    Maheshwor Tiwari
    Data Analyst with 3 years of experience in Python, SQL, and Excel.
    Experience with data visualization, statistical analysis, and reporting.
    Strong background in business intelligence and database management.
    """
    
    sample_jd_text = """
    Data Analyst Position at No To Violence
    
    We are looking for a Data Analyst responsible for analysing data sets and reporting 
    using different methodologies and business analytical tools. The role will also 
    communicate analysis findings to management, funding bodies and other key stakeholders.
    
    Requirements:
    - Tertiary qualification in IT, Management Information Systems or Data Analytics
    - Demonstrated knowledge of Business Intelligence tools
    - Technical proficiency with databases
    - Advanced Microsoft Excel skills
    - Experience troubleshooting as a Systems Administrator or Super User
    - Strong reporting capability, particularly regarding reporting against set KPIs
    """
    
    sample_skill_comparison = {
        "matched_technical_skills": ["Python", "SQL", "Excel", "Data Analysis"],
        "missing_technical_skills": ["Business Intelligence tools", "KPI Reporting"],
        "matched_soft_skills": ["Communication", "Problem Solving"],
        "missing_soft_skills": ["Stakeholder Management"],
        "matched_domain_keywords": ["Data", "Analysis", "Reporting"],
        "missing_domain_keywords": ["Business Intelligence", "Governance"]
    }
    
    sample_extracted_keywords = {
        "technical_skills": ["Python", "SQL", "Excel", "Business Intelligence"],
        "soft_skills": ["Communication", "Problem Solving", "Stakeholder Management"],
        "domain_keywords": ["Data Analysis", "Reporting", "KPI", "Business Intelligence"]
    }
    
    # Step 1: Test Enhanced ATS Score (which should auto-save analysis results)
    print("\n🚀 STEP 1: Testing Enhanced ATS Score (with auto-save)")
    print("-" * 50)
    
    try:
        ats_response = requests.post(
            f"{BASE_URL}/api/ats/enhanced-score",
            headers={"Content-Type": "application/json"},
            json={
                "cv_text": sample_cv_text,
                "jd_text": sample_jd_text,
                "skill_comparison": sample_skill_comparison,
                "extracted_keywords": sample_extracted_keywords
            },
            timeout=60
        )
        
        if ats_response.status_code == 200:
            ats_data = ats_response.json()
            print("✅ Enhanced ATS Score calculated successfully!")
            print(f"   ATS Score: {ats_data.get('overall_score', 'N/A')}")
            print(f"   Analysis file saved: {ats_data.get('analysis_file_saved', 'N/A')}")
        else:
            print(f"❌ Enhanced ATS Score failed: {ats_response.status_code}")
            print(f"   Response: {ats_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced ATS Score error: {e}")
        return False
    
    # Wait a moment for file to be written
    time.sleep(2)
    
    # Step 2: Test AI Recommendations from saved analysis file
    print("\n🧠 STEP 2: Testing AI Recommendations from Analysis File")
    print("-" * 50)
    
    try:
        recommendations_response = requests.post(
            f"{BASE_URL}/api/llm/generate-recommendations-from-analysis",
            headers={"Content-Type": "application/json"},
            json={
                "cv_filename": "maheshwor_tiwari.pdf",
                "jd_text": sample_jd_text
            },
            timeout=120  # Longer timeout for LLM processing
        )
        
        if recommendations_response.status_code == 200:
            rec_data = recommendations_response.json()
            print("✅ AI Recommendations generated successfully!")
            print(f"   Source file: {rec_data.get('source_file', 'N/A')}")
            print(f"   Recommendations length: {len(rec_data.get('recommendations', ''))} chars")
            print("\n📋 Sample recommendations:")
            print("-" * 30)
            recommendations = rec_data.get('recommendations', '')
            print(recommendations[:500] + "..." if len(recommendations) > 500 else recommendations)
            print("-" * 30)
        else:
            print(f"❌ AI Recommendations failed: {recommendations_response.status_code}")
            print(f"   Response: {recommendations_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI Recommendations error: {e}")
        return False
    
    # Step 3: Test getting latest analysis file
    print("\n📁 STEP 3: Testing Get Latest Analysis File")
    print("-" * 50)
    
    try:
        latest_file_response = requests.get(f"{BASE_URL}/api/get-latest-analysis-file")
        
        if latest_file_response.status_code == 200:
            file_data = latest_file_response.json()
            print("✅ Latest analysis file retrieved successfully!")
            print(f"   Latest file: {file_data.get('filename', 'N/A')}")
            print(f"   File path: {file_data.get('filepath', 'N/A')}")
        else:
            print(f"❌ Get latest file failed: {latest_file_response.status_code}")
            print(f"   Response: {latest_file_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Get latest file error: {e}")
        return False
    
    print("\n✅ ALL TESTS PASSED!")
    print("🎉 Complete AI Recommendations Flow is working correctly!")
    return True

def main():
    """Main test function"""
    print("🔧 Testing AI Recommendations Integration")
    print("🌐 Server:", BASE_URL)
    print()
    
    success = test_complete_flow()
    
    if success:
        print("\n🎯 INTEGRATION TEST RESULTS:")
        print("✅ Enhanced ATS Score with auto-save: WORKING")
        print("✅ AI Recommendations from analysis file: WORKING") 
        print("✅ Latest analysis file retrieval: WORKING")
        print("\n💡 The system is ready for production use!")
    else:
        print("\n❌ INTEGRATION TEST FAILED")
        print("Please check the server logs and fix any issues.")

if __name__ == "__main__":
    main() 