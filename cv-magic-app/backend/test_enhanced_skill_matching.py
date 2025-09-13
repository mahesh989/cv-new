#!/usr/bin/env python3
"""
Test Enhanced Skill Matching

This script demonstrates the improved skill matching capabilities using your specific CV/JD data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.skill_extraction.enhanced_skill_matcher import enhanced_skill_matcher

def test_skill_matching():
    """Test the enhanced skill matcher with your specific data"""
    
    # Your CV skills
    cv_skills = {
        "technical_skills": [
            "SQL", "Tableau", "Python", "Power BI", "Excel", "Data analysis",
            "Data visualization", "Dashboard creation", "Statistical analysis",
            "Machine learning", "Deep learning", "Model optimization", 
            "Pruning techniques", "Fine-tuning strategies", "Object detection",
            "Drones", "Edge devices", "Logistic regression", "Random forests",
            "Undersampling techniques"
        ],
        "soft_skills": [
            "Communication", "Interpersonal skills", "Time management",
            "Prioritization", "Problem-solving"
        ],
        "domain_keywords": [
            "Data Science", "Analytics", "Data-driven projects",
            "Industrial inspection", "Real-time object detection",
            "Corrosion detection", "Heart attack risk prediction"
        ]
    }
    
    # JD requirements
    jd_skills = {
        "technical_skills": [
            "SQL", "Excel", "VBA", "Power BI", "Tableau", "Data Mining",
            "Data Warehouse", "Project Management", "Data Extraction", "Data Analysis"
        ],
        "soft_skills": [
            "Collaboration", "Motivation", "Analytical Thinking", "Communication",
            "Problem-Solving", "Stakeholder Management"
        ],
        "domain_keywords": [
            "Business Intelligence", "Fundraising", "Data Analysis",
            "Data Mining", "Data Warehouse"
        ]
    }
    
    print("🔍 ENHANCED SKILL MATCHING ANALYSIS")
    print("=" * 60)
    
    # Test each category
    categories = [
        ("Technical Skills", "technical_skills"),
        ("Soft Skills", "soft_skills"), 
        ("Domain Keywords", "domain_keywords")
    ]
    
    total_matches = 0
    total_jd_requirements = 0
    
    for category_name, category_key in categories:
        print(f"\n📊 {category_name.upper()}")
        print("-" * 40)
        
        cv_category_skills = cv_skills[category_key]
        jd_category_skills = jd_skills[category_key]
        
        total_jd_requirements += len(jd_category_skills)
        
        print(f"CV Skills ({len(cv_category_skills)}): {', '.join(cv_category_skills)}")
        print(f"JD Requirements ({len(jd_category_skills)}): {', '.join(jd_category_skills)}")
        print()
        
        # Find matches for this category
        matches = enhanced_skill_matcher.match_skills(cv_category_skills, jd_category_skills)
        
        category_matches = 0
        category_missing = 0
        
        # Process matches
        matched_jd_skills = set()
        for match in matches:
            if match.confidence >= 0.7:  # Only count confident matches
                category_matches += 1
                matched_jd_skills.add(match.jd_skill)
                print(f"✅ MATCH: '{match.jd_skill}' → '{match.cv_skill}'")
                print(f"   Type: {match.match_type}, Confidence: {match.confidence:.2f}")
                print(f"   Reasoning: {match.reasoning}")
                print()
        
        # Find missing skills
        missing_skills = [skill for skill in jd_category_skills if skill not in matched_jd_skills]
        category_missing = len(missing_skills)
        
        if missing_skills:
            print(f"❌ MISSING ({category_missing}):")
            for skill in missing_skills:
                print(f"   - {skill}")
            print()
        
        # Category summary
        match_rate = (category_matches / len(jd_category_skills)) * 100 if jd_category_skills else 0
        print(f"📈 {category_name} Summary: {category_matches}/{len(jd_category_skills)} matched ({match_rate:.1f}%)")
        
        total_matches += category_matches
    
    # Overall summary
    overall_match_rate = (total_matches / total_jd_requirements) * 100 if total_jd_requirements > 0 else 0
    print("\n" + "=" * 60)
    print(f"🎯 OVERALL SUMMARY")
    print(f"Total JD Requirements: {total_jd_requirements}")
    print(f"Total Matches Found: {total_matches}")
    print(f"Overall Match Rate: {overall_match_rate:.1f}%")
    print(f"Missing Requirements: {total_jd_requirements - total_matches}")
    
    # Improvement suggestions
    print(f"\n💡 KEY IMPROVEMENTS:")
    print(f"   • Case-insensitive matching: 'Data analysis' now matches 'Data Analysis'")
    print(f"   • Synonym recognition: 'Problem-solving' matches 'Problem-Solving'")  
    print(f"   • Hierarchical matching: 'Machine Learning' demonstrates 'Data Mining' capability")
    print(f"   • Domain awareness: Analytics skills are recognized in BI context")
    print(f"   • Fuzzy matching: Handles minor spelling/formatting differences")

def demonstrate_specific_improvements():
    """Show specific examples of how the enhanced matcher fixes common issues"""
    
    print("\n🚀 SPECIFIC IMPROVEMENT EXAMPLES")
    print("=" * 50)
    
    test_cases = [
        # Case sensitivity fix
        ("Data analysis", "Data Analysis", "Case insensitive matching"),
        
        # Punctuation differences
        ("Problem-solving", "Problem-Solving", "Punctuation normalization"),
        
        # Synonyms
        ("Communication", "Interpersonal skills", "Synonym recognition"),
        ("Analytics", "Data Analysis", "Professional equivalents"),
        ("Collaboration", "Teamwork", "Soft skill synonyms"),
        
        # Hierarchical relationships
        ("Machine learning", "Data Mining", "Hierarchical: ML demonstrates data mining capability"),
        ("Random forests", "Statistical analysis", "Specific technique shows statistical skills"),
        ("Deep learning", "Machine Learning", "Advanced technique demonstrates basic ML"),
        
        # Domain context
        ("Data Science", "Business Intelligence", "Related domains in analytics"),
    ]
    
    for cv_skill, jd_skill, description in test_cases:
        match = enhanced_skill_matcher._evaluate_skill_match(cv_skill, jd_skill)
        if match:
            print(f"✅ {description}")
            print(f"   CV: '{cv_skill}' → JD: '{jd_skill}'")
            print(f"   Match Type: {match.match_type}, Confidence: {match.confidence:.2f}")
            print(f"   Reasoning: {match.reasoning}")
            print()
        else:
            print(f"❌ No match found for: '{cv_skill}' → '{jd_skill}'")
            print()

if __name__ == "__main__":
    test_skill_matching()
    demonstrate_specific_improvements()
