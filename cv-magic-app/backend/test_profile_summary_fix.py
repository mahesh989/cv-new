#!/usr/bin/env python3
"""
Test to verify profile_summary mapping fix in tailored_cv_adapter.py
"""

import sys
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

def test_profile_summary_mapping():
    """Test that profile_summary is properly mapped from tailored CV to PDF format"""
    
    print("=" * 80)
    print("Testing Profile Summary Mapping Fix")
    print("=" * 80)
    
    from app.tailored_cv.services.tailored_cv_adapter import adapt_tailored_cv_to_pdf_format
    
    # Mock tailored CV data with profile_summary
    tailored_cv_data = {
        "contact": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890",
            "location": "Sydney, Australia",
            "linkedin": "linkedin.com/in/johndoe",
            "website": "johndoe.com"
        },
        "profile_summary": "Experienced Data Scientist with 5 years of expertise in machine learning and AI.",
        "education": [
            {
                "institution": "University of Sydney",
                "degree": "Master of Data Science",
                "location": "Sydney, Australia",
                "graduation_date": "2020"
            }
        ],
        "experience": [
            {
                "title": "Data Scientist",
                "company": "Tech Corp",
                "location": "Sydney",
                "start_date": "2020",
                "end_date": "Present",
                "bullets": ["Led ML projects", "Improved model accuracy by 25%"]
            }
        ],
        "skills": [
            {
                "category": "Programming Languages",
                "skills": ["Python", "R", "SQL"]
            },
            {
                "category": "Machine Learning",
                "skills": ["TensorFlow", "PyTorch", "scikit-learn"]
            }
        ],
        "projects": [],
        "certifications": []
    }
    
    print("\n📥 Input: Tailored CV Data")
    print(f"   profile_summary: '{tailored_cv_data['profile_summary'][:50]}...'")
    
    # Run the adapter
    pdf_data = adapt_tailored_cv_to_pdf_format(tailored_cv_data)
    
    print("\n📤 Output: PDF Data")
    print(f"   Has 'profile_summary' key: {('profile_summary' in pdf_data)}")
    print(f"   Has 'career_profile' key: {('career_profile' in pdf_data)}")
    
    # Verify profile_summary is mapped
    success = True
    if 'profile_summary' not in pdf_data:
        print("   ❌ FAIL: 'profile_summary' not found in PDF data")
        success = False
    else:
        if pdf_data['profile_summary'] == tailored_cv_data['profile_summary']:
            print(f"   ✅ PASS: profile_summary correctly mapped")
            print(f"            Value: '{pdf_data['profile_summary'][:50]}...'")
        else:
            print(f"   ❌ FAIL: profile_summary value mismatch")
            print(f"            Expected: '{tailored_cv_data['profile_summary']}'")
            print(f"            Got: '{pdf_data['profile_summary']}'")
            success = False
    
    # Verify career_profile is also set (backward compatibility)
    if 'career_profile' in pdf_data:
        if isinstance(pdf_data['career_profile'], dict) and 'summary' in pdf_data['career_profile']:
            if pdf_data['career_profile']['summary'] == tailored_cv_data['profile_summary']:
                print(f"   ✅ PASS: career_profile.summary set for backward compatibility")
            else:
                print(f"   ⚠️  WARN: career_profile.summary value mismatch")
        else:
            print(f"   ⚠️  WARN: career_profile exists but doesn't have 'summary' key")
    else:
        print(f"   ⚠️  WARN: career_profile not set (optional for backward compatibility)")
    
    # Verify validation ran
    print("\n🔍 Validation Layer:")
    print("   Check logs above for validation messages")
    
    # Test case 2: Missing profile_summary
    print("\n" + "=" * 80)
    print("Test 2: Missing Profile Summary (Should Log Warning)")
    print("=" * 80)
    
    tailored_cv_no_summary = {
        "contact": {"name": "Jane Doe", "email": "jane@example.com"},
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "certifications": []
    }
    
    pdf_data_no_summary = adapt_tailored_cv_to_pdf_format(tailored_cv_no_summary)
    
    if 'profile_summary' not in pdf_data_no_summary:
        print("   ✅ PASS: No profile_summary in output (as expected)")
        print("   ✅ Check logs above for warning message")
    else:
        print("   ❌ FAIL: profile_summary should not be in output when missing from source")
    
    # Final result
    print("\n" + "=" * 80)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("Profile summary mapping fix is working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Profile summary mapping needs attention.")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = test_profile_summary_mapping()
    sys.exit(0 if success else 1)

