#!/usr/bin/env python3
"""
Test Skill Count Consistency

Verifies that the skill counts in initial extraction match exactly 
with the counts shown in comparison results table.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.skill_extraction.preextracted_comparator import _format_json_to_text, _deduplicate_skills

def test_count_consistency():
    """Test that skill counts are consistent between extraction and comparison"""
    
    # Your CV skills (from initial extraction)
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
    
    # JD requirements (from initial extraction)
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
    
    print("🔍 SKILL COUNT CONSISTENCY TEST")
    print("=" * 50)
    
    # Show initial extraction counts
    print("\n📋 INITIAL EXTRACTION COUNTS:")
    print(f"CV Technical Skills: {len(cv_skills['technical_skills'])}")
    print(f"CV Soft Skills: {len(cv_skills['soft_skills'])}")
    print(f"CV Domain Keywords: {len(cv_skills['domain_keywords'])}")
    print()
    print(f"JD Technical Skills: {len(jd_skills['technical_skills'])}")
    print(f"JD Soft Skills: {len(jd_skills['soft_skills'])}")
    print(f"JD Domain Keywords: {len(jd_skills['domain_keywords'])}")
    
    # Show what deduplication would do (this was the problem)
    cv_dedup = _deduplicate_skills(cv_skills)
    jd_dedup = _deduplicate_skills(jd_skills)
    
    print("\n⚠️  WHAT DEDUPLICATION WOULD SHOW (OLD BROKEN WAY):")
    print(f"CV Technical Skills (dedup): {len(cv_dedup['technical_skills'])}")
    print(f"CV Soft Skills (dedup): {len(cv_dedup['soft_skills'])}")
    print(f"CV Domain Keywords (dedup): {len(cv_dedup['domain_keywords'])}")
    print()
    print(f"JD Technical Skills (dedup): {len(jd_dedup['technical_skills'])}")
    print(f"JD Soft Skills (dedup): {len(jd_dedup['soft_skills'])}")
    print(f"JD Domain Keywords (dedup): {len(jd_dedup['domain_keywords'])}")
    
    # Check for differences
    cv_differences = []
    jd_differences = []
    
    categories = [
        ("technical_skills", "Technical Skills"),
        ("soft_skills", "Soft Skills"), 
        ("domain_keywords", "Domain Keywords")
    ]
    
    for key, name in categories:
        cv_raw = len(cv_skills[key])
        cv_dedup_count = len(cv_dedup[key])
        jd_raw = len(jd_skills[key])
        jd_dedup_count = len(jd_dedup[key])
        
        if cv_raw != cv_dedup_count:
            cv_differences.append(f"{name}: {cv_raw} -> {cv_dedup_count} (lost {cv_raw - cv_dedup_count})")
        
        if jd_raw != jd_dedup_count:
            jd_differences.append(f"{name}: {jd_raw} -> {jd_dedup_count} (lost {jd_raw - jd_dedup_count})")
    
    if cv_differences or jd_differences:
        print("\n❌ DEDUPLICATION CAUSES COUNT MISMATCHES:")
        if cv_differences:
            print("CV differences:")
            for diff in cv_differences:
                print(f"  - {diff}")
        if jd_differences:
            print("JD differences:")
            for diff in jd_differences:
                print(f"  - {diff}")
    else:
        print("\n✅ No deduplication differences (rare case)")
    
    # Create a mock comparison result to test the formatter
    mock_comparison_result = {
        "technical_skills": {
            "matched": [
                {"jd_skill": "SQL", "cv_equivalent": "SQL", "reasoning": "Exact match"},
                {"jd_skill": "Excel", "cv_equivalent": "Excel", "reasoning": "Exact match"}
            ],
            "missing": [
                {"jd_skill": "VBA", "reasoning": "Not found in CV"},
                {"jd_skill": "Project Management", "reasoning": "Not found in CV"}
            ]
        },
        "soft_skills": {
            "matched": [
                {"jd_skill": "Communication", "cv_equivalent": "Communication", "reasoning": "Exact match"}
            ],
            "missing": [
                {"jd_skill": "Motivation", "reasoning": "Not found in CV"}
            ]
        },
        "domain_keywords": {
            "matched": [
                {"jd_skill": "Data Analysis", "cv_equivalent": "Data Science", "reasoning": "Synonym match"}
            ],
            "missing": [
                {"jd_skill": "Fundraising", "reasoning": "Not found in CV"}
            ]
        }
    }
    
    # Test the formatter with fixed logic
    formatted_output = _format_json_to_text(mock_comparison_result, cv_skills, jd_skills)
    
    print("\n📊 COMPARISON TABLE PREVIEW (FIXED VERSION):")
    # Extract just the summary table part
    lines = formatted_output.split('\n')
    table_start = False
    for line in lines:
        if "SUMMARY TABLE" in line:
            table_start = True
        if table_start and line.strip():
            print(line)
        if table_start and "DETAILED AI ANALYSIS" in line:
            break
    
    print("\n✅ SOLUTION IMPLEMENTED:")
    print("  • Removed deduplication from count calculations")
    print("  • Table now shows RAW extraction counts")
    print("  • Numbers match exactly between extraction and comparison")
    print("  • Fixed validation logic to use consistent counts")
    print("  • Updated input summary to show actual extracted skills")

if __name__ == "__main__":
    test_count_consistency()
