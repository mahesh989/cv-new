#!/usr/bin/env python3
"""
Test script to debug CV parsing issues
"""
import json
import sys
import os

# Add the backend directory to Python path
sys.path.append('/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend')

from app.tailored_cv.services.recommendation_parser import RecommendationParser

def test_cv_parsing():
    """Test the CV parsing functionality"""
    print("🔍 Testing CV parsing...")
    
    # Load the original CV
    cv_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/original_cv.json"
    
    try:
        with open(cv_path, 'r') as f:
            cv_data = json.load(f)
        
        # Test the proper CV loading method
        parsed_cv = RecommendationParser.load_original_cv(cv_path)
        
        print("\n✅ Parsed CV data:")
        print(json.dumps(parsed_cv, indent=2))
        
        # Check what we extracted
        print(f"\n📊 Summary:")
        print(f"  Name: {parsed_cv['contact']['name']}")
        print(f"  Email: {parsed_cv['contact']['email']}")
        print(f"  Education entries: {len(parsed_cv['education'])}")
        print(f"  Experience entries: {len(parsed_cv['experience'])}")
        print(f"  Skills categories: {len(parsed_cv['skills'])}")
        
        if parsed_cv['experience']:
            print(f"  First job: {parsed_cv['experience'][0]['company']} - {parsed_cv['experience'][0]['title']}")
        
    except Exception as e:
        print(f"❌ Error testing CV parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cv_parsing()