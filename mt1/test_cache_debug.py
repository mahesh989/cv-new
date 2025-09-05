#!/usr/bin/env python3
"""
Debug script to check what's stored in the keyword cache and comparison results.
"""

import requests
import json

def test_cache_contents():
    """Check what's in the cache"""
    
    # Test with a known CV file
    test_data = {
        "cv_skills": {
            "technical_skills": ["Python", "SQL"],
            "soft_skills": ["Communication"],
            "domain_keywords": ["Data Analysis"]
        },
        "jd_skills": {
            "technical_skills": ["Python", "R", "SQL"],
            "soft_skills": ["Communication", "Teamwork"],
            "domain_keywords": ["Data Science", "Analytics"]
        }
    }
    
    print("🧪 [DEBUG] Testing with sample data:")
    print(f"  CV Skills: {test_data['cv_skills']}")
    print(f"  JD Skills: {test_data['jd_skills']}")
    
    try:
        url = "http://localhost:8000/api/llm/compare-skills"
        print(f"\n🚀 [DEBUG] Sending request to {url}")
        
        response = requests.post(url, json=test_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            comparison_result = result.get('comparison_result', {})
            validation = result.get('validation', {})
            
            print(f"\n📊 [DEBUG] Comparison Result:")
            print(f"  Match Summary: {comparison_result.get('match_summary', {})}")
            print(f"  Matched Count: {sum(len(comparison_result.get('matched', {}).get(cat, [])) for cat in ['technical_skills', 'soft_skills', 'domain_keywords'])}")
            print(f"  Missing Count: {sum(len(comparison_result.get('missing', {}).get(cat, [])) for cat in ['technical_skills', 'soft_skills', 'domain_keywords'])}")
            
            print(f"\n✅ [DEBUG] Validation:")
            print(f"  Valid: {validation.get('valid', 'N/A')}")
            print(f"  Processed: {validation.get('processed_count', 'N/A')}")
            print(f"  Message: {validation.get('message', 'N/A')}")
            
            return True
            
        else:
            print(f"❌ [ERROR] API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ [ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Debug Cache Contents")
    print("=" * 40)
    
    success = test_cache_contents()
    
    if success:
        print("\n✅ Debug test completed successfully")
    else:
        print("\n❌ Debug test failed") 