#!/usr/bin/env python3
"""
Test script to verify the rerun analysis fix
"""

import json
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append('/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend')

def test_skills_transformation():
    """Test the skills transformation logic"""
    print("🧪 Testing skills transformation logic...")
    
    # Simulate the skills data from tailored CV
    cv_data = {
        "contact": {"name": "Test User"},
        "education": [],
        "experience": [],
        "projects": [],
        "skills": ["SQL", "Excel", "Python", "Power BI", "VBA", "Data Analysis", "Data Warehouse"],
        "created_at": "2025-09-24T09:44:52"
    }
    
    print(f"📋 Original skills format: {cv_data['skills']}")
    print(f"📋 Skills type: {type(cv_data['skills'][0])}")
    
    # Apply the transformation logic
    if 'skills' in cv_data and isinstance(cv_data['skills'], list):
        if cv_data['skills'] and isinstance(cv_data['skills'][0], str):
            print("🔄 Transforming skills from string array to SkillCategory format")
            cv_data['skills'] = [{"skills": cv_data['skills']}]
            print(f"✅ Transformed skills: {cv_data['skills']}")
    
    # Test if it would work with OriginalCV model
    try:
        from app.tailored_cv.models.cv_models import OriginalCV
        original_cv = OriginalCV(**cv_data)
        print("✅ OriginalCV model creation successful!")
        print(f"✅ Skills field: {original_cv.skills}")
        return True
    except Exception as e:
        print(f"❌ OriginalCV model creation failed: {e}")
        return False

def test_file_selection():
    """Test the file selection logic"""
    print("\n🧪 Testing file selection logic...")
    
    try:
        from app.unified_latest_file_selector import unified_selector
        
        # Test getting latest CV for Australia_for_UNHCR
        cv_context = unified_selector.get_latest_cv_across_all("Australia_for_UNHCR")
        
        print(f"✅ Found CV: {cv_context.file_type}")
        print(f"✅ JSON path: {cv_context.json_path}")
        print(f"✅ TXT path: {cv_context.txt_path}")
        print(f"✅ Timestamp: {cv_context.timestamp}")
        
        return True
    except Exception as e:
        print(f"❌ File selection failed: {e}")
        return False

def test_ai_recommendation_files():
    """Test if AI recommendation files exist"""
    print("\n🧪 Testing AI recommendation files...")
    
    company_dir = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/Australia_for_UNHCR")
    
    if not company_dir.exists():
        print(f"❌ Company directory not found: {company_dir}")
        return False
    
    # Find all AI recommendation files
    ai_files = list(company_dir.glob("*ai_recommendation*.json"))
    
    if not ai_files:
        print("❌ No AI recommendation files found")
        return False
    
    # Sort by modification time
    ai_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    latest_file = ai_files[0]
    
    print(f"✅ Found {len(ai_files)} AI recommendation files")
    print(f"✅ Latest file: {latest_file.name}")
    print(f"✅ Last modified: {latest_file.stat().st_mtime}")
    
    # Try to read the file
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ File readable, has keys: {list(data.keys())}")
        return True
    except Exception as e:
        print(f"❌ Failed to read AI recommendation file: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running rerun analysis fix tests...\n")
    
    tests = [
        ("Skills Transformation", test_skills_transformation),
        ("File Selection", test_file_selection),
        ("AI Recommendation Files", test_ai_recommendation_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The fix should work.")
    else:
        print("⚠️ Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()
