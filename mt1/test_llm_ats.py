#!/usr/bin/env python3
"""
Test script for LLM-based ATS keyword extraction and comparison
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.llm_keyword_matcher import LLMKeywordMatcher

# Sample CV text
sample_cv = """
Maheshwor Tiwari
0414 032 507 | maheshtwari99@gmail.com | GitHub | LinkedIn
Residency Status: On student visa; applying for Subclass 485 Temporary Graduate Visa

EDUCATION
Master of Data Science, University of Melbourne, 2022-2024
Bachelor of Computer Science, Tribhuvan University, 2018-2021

EXPERIENCE
Data Analyst Intern, Tech Solutions Pty Ltd, Melbourne, 2023-2024
• Developed Python scripts for data preprocessing and analysis using pandas and numpy
• Created interactive dashboards using Tableau and Power BI for business intelligence
• Implemented machine learning models for customer segmentation using scikit-learn
• Collaborated with cross-functional teams to deliver data-driven insights

Research Assistant, University of Melbourne, 2022-2023
• Conducted statistical analysis using R and SPSS for research projects
• Managed large datasets and performed data cleaning and validation
• Presented findings to academic committees and stakeholders

PROJECTS
Customer Churn Prediction System
• Built predictive model using Python, TensorFlow, and SQL databases
• Achieved 85% accuracy in predicting customer churn patterns
• Deployed model using Docker containers on AWS cloud platform

SKILLS
Programming: Python, R, SQL, JavaScript, HTML, CSS
Data Analysis: pandas, numpy, scikit-learn, TensorFlow, matplotlib, seaborn
Database: MySQL, PostgreSQL, MongoDB
Cloud: AWS, Azure, Google Cloud Platform
Visualization: Tableau, Power BI, D3.js
Soft Skills: Communication, Leadership, Problem Solving, Team Collaboration, Time Management
"""

# Sample Job Description
sample_jd = """
Data Analyst Position at No To Violence
Melbourne, Victoria

About the Role:
We are seeking a skilled Data Analyst to join our team at No To Violence, a leading organization dedicated to ending family violence. The successful candidate will play a crucial role in analyzing data to support our mission and improve service delivery.

Key Responsibilities:
• Analyze large datasets to identify trends and patterns in family violence data
• Develop and maintain dashboards using Tableau or Power BI for stakeholder reporting
• Conduct statistical analysis using Python, R, or similar tools
• Collaborate with program managers and researchers to support evidence-based decision making
• Prepare comprehensive reports and presentations for executive leadership
• Ensure data quality and integrity across all systems
• Support grant applications with data analysis and visualization

Required Skills:
• Bachelor's degree in Data Science, Statistics, Computer Science, or related field
• 2+ years of experience in data analysis and visualization
• Proficiency in Python and SQL for data manipulation and analysis
• Experience with statistical software (R, SPSS, SAS)
• Strong knowledge of data visualization tools (Tableau, Power BI)
• Experience with database management systems (MySQL, PostgreSQL)
• Knowledge of machine learning techniques and predictive modeling
• Excellent communication and presentation skills
• Strong analytical and problem-solving abilities
• Experience working with sensitive data and understanding of privacy requirements

Preferred Qualifications:
• Experience in social services or non-profit sector
• Knowledge of family violence prevention and intervention strategies
• Experience with cloud platforms (AWS, Azure)
• Familiarity with grant reporting requirements
• Understanding of NDIS and government funding frameworks

What We Offer:
• Competitive salary package with salary packaging benefits
• Professional development opportunities
• Flexible working arrangements
• Opportunity to make a meaningful impact in ending family violence
• Collaborative and supportive work environment
"""

async def test_llm_extraction():
    """Test LLM-based keyword extraction"""
    print("=" * 80)
    print("🧪 TESTING LLM-BASED KEYWORD EXTRACTION")
    print("=" * 80)
    
    # Create matcher instance
    llm_matcher = LLMKeywordMatcher()
    
    # Test CV extraction
    print("\n📄 EXTRACTING KEYWORDS FROM CV:")
    cv_keywords = await llm_matcher.extract_keywords_from_text(sample_cv, "CV")
    
    for category, keywords in cv_keywords.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for i, keyword in enumerate(keywords[:10], 1):
            print(f"  {i}. {keyword}")
        if len(keywords) > 10:
            print(f"  ... and {len(keywords) - 10} more")
    
    # Test JD extraction
    print("\n\n🧾 EXTRACTING KEYWORDS FROM JOB DESCRIPTION:")
    jd_keywords = await llm_matcher.extract_keywords_from_text(sample_jd, "JD")
    
    for category, keywords in jd_keywords.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for i, keyword in enumerate(keywords[:10], 1):
            print(f"  {i}. {keyword}")
        if len(keywords) > 10:
            print(f"  ... and {len(keywords) - 10} more")

async def test_llm_comparison():
    """Test LLM-based keyword comparison"""
    print("\n\n" + "=" * 80)
    print("🧪 TESTING LLM-BASED KEYWORD COMPARISON")
    print("=" * 80)
    
    # Create matcher instance
    llm_matcher = LLMKeywordMatcher()
    
    # Perform comprehensive comparison
    comparisons = await llm_matcher.comprehensive_comparison(sample_cv, sample_jd)
    
    # Display results for each category
    for category, comparison in comparisons.items():
        print(f"\n📊 {category.replace('_', ' ').title().upper()}:")
        print(f"   Match Percentage: {comparison.match_percentage:.1f}%")
        print(f"   JD Keywords: {len(comparison.jd_keywords)}")
        print(f"   CV Keywords: {len(comparison.cv_keywords)}")
        
        if comparison.matches:
            print(f"\n   🔍 DETAILED MATCHES:")
            for match in comparison.matches[:5]:  # Show first 5 matches
                status = "✅" if match.match_type != "missing" else "❌"
                print(f"   {status} {match.jd_keyword}")
                if match.cv_keyword:
                    print(f"      → Matched with: {match.cv_keyword}")
                    print(f"      → Type: {match.match_type} (confidence: {match.confidence:.2f})")
                    print(f"      → Explanation: {match.explanation}")
                else:
                    print(f"      → Status: Missing from CV")
                print()
        
        if comparison.missing_keywords:
            print(f"   ❌ MISSING KEYWORDS ({len(comparison.missing_keywords)}):")
            for keyword in comparison.missing_keywords[:5]:
                print(f"      • {keyword}")
            if len(comparison.missing_keywords) > 5:
                print(f"      ... and {len(comparison.missing_keywords) - 5} more")
        
        if comparison.additional_keywords:
            print(f"   ➕ ADDITIONAL CV KEYWORDS ({len(comparison.additional_keywords)}):")
            for keyword in comparison.additional_keywords[:5]:
                print(f"      • {keyword}")
            if len(comparison.additional_keywords) > 5:
                print(f"      ... and {len(comparison.additional_keywords) - 5} more")

async def test_overall_scoring():
    """Test overall scoring and suggestions"""
    print("\n\n" + "=" * 80)
    print("🧪 TESTING OVERALL SCORING AND SUGGESTIONS")
    print("=" * 80)
    
    # Create matcher instance
    llm_matcher = LLMKeywordMatcher()
    
    # Perform comprehensive comparison
    comparisons = await llm_matcher.comprehensive_comparison(sample_cv, sample_jd)
    
    # Calculate overall score
    overall_score = llm_matcher.calculate_overall_score(comparisons)
    print(f"\n📊 OVERALL ATS SCORE: {overall_score:.1f}%")
    
    # Generate improvement suggestions
    suggestions = llm_matcher.generate_improvement_suggestions(comparisons)
    
    if suggestions:
        print(f"\n💡 IMPROVEMENT SUGGESTIONS:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
    
    # Category breakdown
    print(f"\n📈 CATEGORY BREAKDOWN:")
    weights = {
        "technical_skills": 0.35,
        "soft_skills": 0.20,
        "domain_keywords": 0.20,
        "experience_keywords": 0.15,
        "education_keywords": 0.10
    }
    
    for category, comparison in comparisons.items():
        weight = weights.get(category, 0.1)
        contribution = comparison.match_percentage * weight
        print(f"   {category.replace('_', ' ').title()}: {comparison.match_percentage:.1f}% (weight: {weight:.0%}, contribution: {contribution:.1f})")

async def main():
    """Run all tests"""
    print("🚀 STARTING LLM-BASED ATS TESTING")
    
    await test_llm_extraction()
    await test_llm_comparison()
    await test_overall_scoring()
    
    print("\n\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 