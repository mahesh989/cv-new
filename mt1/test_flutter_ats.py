#!/usr/bin/env python3

import requests
import json
import time

def test_flutter_ats_endpoint():
    """Test the exact same endpoint that Flutter calls"""
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    # Test data matching Flutter's request format
    test_payload = {
        "cv_filename": "maheshwor_tiwari.pdf",
        "cv_type": "uploaded",  # This is what Flutter sends
        "jd_text": """
        Senior Data Analyst Position
        
        We are seeking a skilled Data Analyst to join our team. The ideal candidate will have:
        
        Required Skills:
        - Python programming (3+ years)
        - SQL and database management (PostgreSQL, MySQL)
        - Data visualization tools (Tableau, Power BI)
        - Statistical analysis and machine learning
        - Experience with pandas, numpy, scikit-learn
        - Data pipeline development
        
        Qualifications:
        - Master's degree in Data Science, Statistics, or related field
        - 3+ years of professional data analysis experience
        - Strong communication and presentation skills
        """,
        "prompt": "Analyze this CV against the job description and provide ATS compatibility score"
    }
    
    print("🚀 Testing Flutter ATS Endpoint...")
    print(f"📄 CV File: {test_payload['cv_filename']}")
    print(f"📋 CV Type: {test_payload['cv_type']}")
    print(f"📝 JD Length: {len(test_payload['jd_text'])} characters")
    print(f"💬 Prompt Length: {len(test_payload['prompt'])} characters")
    print("=" * 60)
    
    try:
        print("🔍 Sending request to /ats-test/ endpoint...")
        response = requests.post(
            f"{base_url}/ats-test/",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ ATS Test Successful!")
            print("=" * 60)
            
            # Show key results
            print(f"📊 Overall Score: {result.get('overall_score', 'N/A')}/100")
            print(f"🎯 Status: {result.get('status', 'N/A')}")
            print(f"📈 Compatibility: {result.get('compatibility_level', 'N/A')}")
            
            # Show skill matches
            matched_hard = result.get('matched_hard_skills', [])
            missed_hard = result.get('missed_hard_skills', [])
            
            print(f"\n✅ Matched Hard Skills ({len(matched_hard)}):")
            for skill in matched_hard[:10]:  # Show first 10
                print(f"  • {skill}")
            
            if missed_hard:
                print(f"\n⚠️  Missing Hard Skills ({len(missed_hard)}):")
                for skill in missed_hard[:5]:  # Show first 5
                    print(f"  • {skill}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_flutter_ats_endpoint() 