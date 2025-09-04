#!/usr/bin/env python3
"""
Simple test for LLM-based ATS system with strict validation
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm_keyword_matcher import LLMKeywordMatcher

async def test_strict_llm_comparison():
    """Test the strict LLM comparison system"""
    print("🧪 Testing Strict LLM-based ATS Comparison System")
    print("=" * 80)
    
    # Simple test data
    sample_cv = """
    John Doe - Data Analyst
    
    TECHNICAL SKILLS:
    - Python programming
    - SQL database management
    - Excel data analysis
    - Tableau visualization
    - Machine Learning basics
    
    SOFT SKILLS:
    - Communication
    - Problem solving
    - Teamwork
    - Leadership
    
    EXPERIENCE:
    - Data Analyst at Tech Corp (2020-2023)
    - Business Intelligence Analyst at StartupCo (2018-2020)
    - Developed reporting dashboards
    - Performed statistical analysis
    
    EDUCATION:
    - Master of Data Science, University of Melbourne (2018)
    - Bachelor of Computer Science, Monash University (2016)
    """
    
    sample_jd = """
    Data Analyst Position
    
    REQUIRED SKILLS:
    - Python programming
    - SQL expertise
    - Power BI (required)
    - Statistical analysis
    - Data visualization
    
    SOFT SKILLS:
    - Communication skills
    - Problem solving abilities
    - Team collaboration
    - Project management
    
    EXPERIENCE:
    - 3+ years as Data Analyst
    - Experience with reporting tools
    - Business intelligence background
    
    EDUCATION:
    - Bachelor's degree in relevant field
    - Master's degree preferred
    """
    
    try:
        # Initialize matcher
        matcher = LLMKeywordMatcher()
        
        # Test keyword extraction
        print("🔍 Testing keyword extraction...")
        cv_keywords = await matcher.extract_keywords_from_text(sample_cv, "CV")
        jd_keywords = await matcher.extract_keywords_from_text(sample_jd, "JD")
        
        print("\n📄 CV Keywords extracted:")
        for category, keywords in cv_keywords.items():
            print(f"   {category}: {keywords}")
        
        print("\n📋 JD Keywords extracted:")
        for category, keywords in jd_keywords.items():
            print(f"   {category}: {keywords}")
        
        # Test strict comparison
        print("\n🧠 Testing strict comparison...")
        comparisons = await matcher.comprehensive_comparison(sample_cv, sample_jd)
        
        # Validate results
        print("\n✅ STRICT VALIDATION RESULTS:")
        print("=" * 60)
        
        total_hallucinations = 0
        
        for category, comparison in comparisons.items():
            print(f"\n📊 {category.replace('_', ' ').title()}:")
            print(f"   Match percentage: {comparison.match_percentage:.1f}%")
            print(f"   JD keywords: {len(comparison.jd_keywords)}")
            print(f"   CV keywords: {len(comparison.cv_keywords)}")
            
            # Validate each match
            for match in comparison.matches:
                if match.cv_keyword:
                    # Check if cv_keyword actually exists in CV keywords
                    if match.cv_keyword not in comparison.cv_keywords:
                        print(f"   ❌ HALLUCINATION: '{match.cv_keyword}' not in CV keywords")
                        total_hallucinations += 1
                    
                    # Check if cv_keyword exists in CV text
                    if match.cv_keyword.lower() not in sample_cv.lower():
                        print(f"   ❌ HALLUCINATION: '{match.cv_keyword}' not in CV text")
                        total_hallucinations += 1
                    
                    # Valid match
                    print(f"   ✅ {match.jd_keyword} → {match.cv_keyword} ({match.match_type}, {match.confidence:.2f})")
                else:
                    print(f"   ❌ {match.jd_keyword} → Missing")
        
        # Overall results
        overall_score = matcher.calculate_overall_score(comparisons)
        suggestions = matcher.generate_improvement_suggestions(comparisons)
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   Overall Score: {overall_score:.1f}%")
        print(f"   Total Hallucinations: {total_hallucinations}")
        print(f"   Improvement Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"      {i}. {suggestion}")
        
        # Validation summary
        if total_hallucinations == 0:
            print("\n✅ SUCCESS: No hallucinations detected!")
        else:
            print(f"\n❌ FAILURE: {total_hallucinations} hallucinations detected!")
            
        return total_hallucinations == 0
        
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_deduplication():
    """Test keyword deduplication across categories"""
    print("\n🔄 Testing keyword deduplication...")
    
    # Test data with duplicates
    keywords_with_duplicates = {
        "technical_skills": ["Python", "SQL", "Communication", "Data Analysis"],
        "soft_skills": ["Communication", "Leadership", "Python", "Problem Solving"],
        "domain_keywords": ["Data Analysis", "Business Intelligence", "SQL", "Healthcare"],
        "experience_keywords": ["Data Analyst", "Project Management", "Leadership"],
        "education_keywords": ["Master's Degree", "Data Science", "Python"]
    }
    
    matcher = LLMKeywordMatcher()
    deduplicated = matcher._deduplicate_across_categories(keywords_with_duplicates)
    
    print("📊 Deduplication results:")
    for category, keywords in deduplicated.items():
        print(f"   {category}: {keywords}")
    
    # Check for duplicates across categories
    all_keywords = []
    for keywords in deduplicated.values():
        all_keywords.extend([kw.lower() for kw in keywords])
    
    duplicates = len(all_keywords) - len(set(all_keywords))
    print(f"\n📈 Duplicate count: {duplicates}")
    
    if duplicates == 0:
        print("✅ SUCCESS: No duplicates across categories!")
    else:
        print(f"❌ FAILURE: {duplicates} duplicates found!")
    
    return duplicates == 0

async def main():
    """Main test function"""
    print("🚀 Starting Strict LLM ATS System Tests")
    print("=" * 80)
    
    # Run tests
    test1_passed = await test_strict_llm_comparison()
    test2_passed = await test_deduplication()
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 TEST SUMMARY:")
    print(f"   Strict Comparison Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Deduplication Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED - System is working correctly!")
    else:
        print("\n❌ SOME TESTS FAILED - System needs fixes!")

if __name__ == "__main__":
    asyncio.run(main()) 