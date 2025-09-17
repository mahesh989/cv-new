#!/usr/bin/env python3
"""
Test script to validate the fix for keyword extraction from recommendations
"""

import json
import sys
from pathlib import Path

# Add the backend directory to path
sys.path.insert(0, '/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend')

from app.tailored_cv.services.recommendation_parser import RecommendationParser

def test_keyword_extraction():
    """Test that keywords are properly extracted from recommendation file"""
    
    # Load the AI recommendation file
    rec_file = Path("/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/Australia_for_UNHCR/Australia_for_UNHCR_ai_recommendation.json")
    
    print("=" * 60)
    print("Testing Keyword Extraction Fix")
    print("=" * 60)
    
    # Parse the recommendation file
    parsed_data = RecommendationParser.parse_recommendation_file(str(rec_file))
    
    print("\n📋 Extracted Data:")
    print(f"  Company: {parsed_data.get('company')}")
    print(f"  Job Title: {parsed_data.get('job_title')}")
    
    print("\n🔑 Critical Gaps (should be actual keywords):")
    critical_gaps = parsed_data.get('critical_gaps', [])
    for i, gap in enumerate(critical_gaps[:10], 1):
        print(f"  {i}. {gap}")
    
    print("\n📝 Missing Keywords:")
    missing_keywords = parsed_data.get('missing_keywords', [])
    for i, keyword in enumerate(missing_keywords[:10], 1):
        print(f"  {i}. {keyword}")
    
    print("\n💼 Missing Technical Skills:")
    missing_tech = parsed_data.get('missing_technical_skills', [])
    for i, skill in enumerate(missing_tech[:10], 1):
        print(f"  {i}. {skill}")
    
    print("\n👥 Missing Soft Skills:")
    missing_soft = parsed_data.get('missing_soft_skills', [])
    for i, skill in enumerate(missing_soft[:10], 1):
        print(f"  {i}. {skill}")
    
    # Validate that critical_gaps doesn't contain category labels
    print("\n✅ Validation Results:")
    
    invalid_entries = []
    for gap in critical_gaps:
        # Check for category labels with percentages
        if '(' in gap and '%' in gap:
            invalid_entries.append(f"Category label: {gap}")
        elif ':' in gap or '=' in gap:
            invalid_entries.append(f"Non-keyword: {gap}")
        elif len(gap) > 50:
            invalid_entries.append(f"Too long: {gap[:30]}...")
    
    if invalid_entries:
        print("  ❌ Found invalid entries in critical_gaps:")
        for entry in invalid_entries:
            print(f"    - {entry}")
    else:
        print("  ✅ All critical_gaps entries are valid keywords")
    
    # Check if we have actual keywords
    all_keywords = list(set(critical_gaps + missing_keywords + missing_tech[:3] + missing_soft[:3]))
    print(f"\n📊 Total unique keywords extracted: {len(all_keywords)}")
    
    # Show sample of final keyword list
    print("\n🎯 Sample of final keywords for integration:")
    for i, keyword in enumerate(all_keywords[:15], 1):
        print(f"  {i}. {keyword}")
    
    return len(invalid_entries) == 0

if __name__ == "__main__":
    success = test_keyword_extraction()
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: Keywords are properly extracted")
    else:
        print("❌ TEST FAILED: Invalid entries found in keywords")
    print("=" * 60)
    sys.exit(0 if success else 1)