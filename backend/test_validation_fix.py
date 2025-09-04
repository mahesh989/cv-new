#!/usr/bin/env python3
"""
Test script to validate critical fixes for skill comparison system.
Tests requirement counting, validation, and completeness.
"""

import requests
import json
import time

def test_skill_comparison():
    """Test the updated skill comparison with validation"""
    
    # Test data with known counts
    test_cv_skills = {
        "technical_skills": ["Python", "SQL", "Data Analysis"],
        "soft_skills": ["Communication", "Leadership"],
        "domain_keywords": ["Machine Learning", "Statistics"]
    }
    
    test_jd_skills = {
        "technical_skills": ["Python", "R", "SQL", "Docker", "AWS"],
        "soft_skills": ["Communication", "Teamwork", "Problem Solving"],
        "domain_keywords": ["Data Science", "Machine Learning", "Big Data"]
    }
    
    # Calculate expected totals
    expected_total = len(test_jd_skills["technical_skills"]) + len(test_jd_skills["soft_skills"]) + len(test_jd_skills["domain_keywords"])
    
    print(f"🧪 [TEST] Expected total JD requirements: {expected_total}")
    print(f"🧪 [TEST] Technical: {len(test_jd_skills['technical_skills'])}")
    print(f"🧪 [TEST] Soft Skills: {len(test_jd_skills['soft_skills'])}")
    print(f"🧪 [TEST] Domain: {len(test_jd_skills['domain_keywords'])}")
    
    # Make API request
    url = "http://localhost:8000/api/llm/compare-skills"
    payload = {
        "cv_skills": test_cv_skills,
        "jd_skills": test_jd_skills
    }
    
    try:
        print(f"\n🚀 [TEST] Sending request to {url}")
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if validation data is present
            validation = result.get('validation', {})
            comparison_result = result.get('comparison_result', {})
            
            print(f"\n📊 [VALIDATION] Results:")
            print(f"   Valid: {validation.get('valid', 'N/A')}")
            print(f"   Processed: {validation.get('processed_count', 'N/A')}")
            print(f"   Expected: {expected_total}")
            print(f"   Message: {validation.get('message', 'N/A')}")
            
            # Check match summary
            match_summary = comparison_result.get('match_summary', {})
            print(f"\n📈 [MATCH SUMMARY]:")
            print(f"   Total JD Requirements: {match_summary.get('total_jd_requirements', 'N/A')}")
            print(f"   Total Matches: {match_summary.get('total_matches', 'N/A')}")
            print(f"   Match Percentage: {match_summary.get('match_percentage', 'N/A')}%")
            print(f"   Validation Passed: {match_summary.get('validation_passed', 'N/A')}")
            
            # Count actual processed requirements
            matched = comparison_result.get('matched', {})
            missing = comparison_result.get('missing', {})
            
            matched_count = sum(len(matched.get(cat, [])) for cat in ['technical_skills', 'soft_skills', 'domain_keywords'])
            missing_count = sum(len(missing.get(cat, [])) for cat in ['technical_skills', 'soft_skills', 'domain_keywords'])
            total_processed = matched_count + missing_count
            
            print(f"\n🔍 [ACTUAL COUNTS]:")
            print(f"   Matched: {matched_count}")
            print(f"   Missing: {missing_count}")
            print(f"   Total Processed: {total_processed}")
            
            # Validation checks
            print(f"\n✅ [VALIDATION CHECKS]:")
            print(f"   Count Match: {total_processed == expected_total} ({total_processed}/{expected_total})")
            print(f"   No Missing Requirements: {validation.get('valid', False)}")
            print(f"   Validation Passed: {match_summary.get('validation_passed', False)}")
            
            if total_processed == expected_total and validation.get('valid', False):
                print(f"\n🎉 [SUCCESS] All validation checks PASSED!")
                return True
            else:
                print(f"\n❌ [FAILURE] Validation checks FAILED!")
                return False
                
        else:
            print(f"❌ [ERROR] API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ [ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Skill Comparison Validation Fixes")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    success = test_skill_comparison()
    
    if success:
        print("\n🎉 All tests PASSED! Critical fixes are working correctly.")
    else:
        print("\n❌ Tests FAILED! Issues still exist in the system.") 