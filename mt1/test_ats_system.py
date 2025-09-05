#!/usr/bin/env python3
"""
Test script for ATS Rules Engine
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ats_rules_engine import evaluate_ats_compatibility, extract_skills_unified

# Sample CV text
SAMPLE_CV = """
Maheshwor Tiwari
0414 032 507 | maheshtwari99@gmail.com | LinkedIn | GitHub
Melbourne, Australia

EDUCATION
Master of Data Science, University of Melbourne, 2023
Bachelor of Computer Science, Tribhuvan University, 2020

EXPERIENCE
Data Analyst Intern | TechCorp Australia | Jan 2023 - Jun 2023
• Developed Python scripts for data analysis and visualization using Pandas and Matplotlib
• Created interactive dashboards using Tableau, improving reporting efficiency by 30%
• Collaborated with cross-functional teams to analyze customer behavior patterns
• Implemented SQL queries to extract insights from large datasets (500K+ records)

Research Assistant | University of Melbourne | Jul 2022 - Dec 2022
• Conducted machine learning research using Python and scikit-learn
• Published findings in peer-reviewed journal, increasing citation impact by 25%
• Mentored 3 undergraduate students in data science methodologies
• Managed research project budget of $15,000 AUD

PROJECTS
Customer Churn Prediction | Machine Learning Project | 2023
• Built predictive model using Python, pandas, and scikit-learn to identify at-risk customers
• Achieved 85% accuracy in predicting customer churn, potentially saving $200K annually
• Implemented feature engineering techniques to improve model performance
• Deployed model using Flask API for real-time predictions

Sales Dashboard | Business Intelligence Project | 2022
• Developed comprehensive sales dashboard using Tableau and SQL
• Integrated data from multiple sources including CRM and ERP systems
• Reduced reporting time from 2 hours to 15 minutes through automation
• Presented insights to senior management, influencing strategic decisions

SKILLS
Python, SQL, Tableau, Power BI, Machine Learning, Data Analysis, Statistical Modeling, Pandas, NumPy, scikit-learn, Matplotlib, Seaborn, Git, Excel, R, AWS, Docker, Agile, Problem Solving, Communication, Leadership, Teamwork
"""

# Sample Job Description
SAMPLE_JD = """
Senior Data Analyst - TechCorp Australia
Location: Melbourne, Australia

We are seeking a skilled Senior Data Analyst to join our growing analytics team. The ideal candidate will have strong technical skills and experience in data analysis, visualization, and machine learning.

Key Responsibilities:
• Analyze large datasets to identify trends and insights
• Create compelling data visualizations and dashboards
• Collaborate with stakeholders to understand business requirements
• Develop predictive models to support business decisions
• Present findings to senior management and cross-functional teams

Required Skills:
• 3+ years of experience in data analysis
• Proficiency in Python programming and data libraries (Pandas, NumPy)
• Strong SQL skills for database querying
• Experience with data visualization tools (Tableau, Power BI)
• Knowledge of machine learning algorithms and techniques
• Statistical analysis and modeling experience
• Excellent communication and presentation skills

Preferred Skills:
• Experience with cloud platforms (AWS, Azure)
• Knowledge of R programming language
• Familiarity with big data technologies
• Experience with version control (Git)
• Agile/Scrum methodology experience
• Leadership and mentoring experience

What We Offer:
• Competitive salary package
• Flexible working arrangements
• Professional development opportunities
• Collaborative team environment
"""

async def test_ats_system():
    """Test the ATS evaluation system"""
    print("🎯 Testing ATS Rules Engine")
    print("=" * 80)
    
    # Test 1: Skill extraction
    print("\n📊 TEST 1: Skill Extraction")
    print("-" * 40)
    
    print("📄 CV TEXT (first 200 chars):")
    print(SAMPLE_CV[:200] + "...")
    
    print("\n🧾 JD TEXT (first 200 chars):")
    print(SAMPLE_JD[:200] + "...")
    
    try:
        skills = await extract_skills_unified(SAMPLE_CV)
        print(f"\n✅ Extracted Skills:")
        print(f"   Technical: {len(skills.get('technical_skills', []))} skills")
        print(f"   Soft: {len(skills.get('soft_skills', []))} skills") 
        print(f"   Domain: {len(skills.get('domain_skills', []))} skills")
        print(f"   Certifications: {len(skills.get('certifications', []))} skills")
        
        print(f"\n🔧 Technical Skills: {skills.get('technical_skills', [])[:10]}...")
        print(f"🤝 Soft Skills: {skills.get('soft_skills', [])[:5]}...")
        print(f"🏢 Domain Skills: {skills.get('domain_skills', [])[:5]}...")
        
    except Exception as e:
        print(f"❌ Skill extraction failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: ATS Evaluation
    print("\n📊 TEST 2: ATS Evaluation")
    print("-" * 40)
    
    try:
        result = await evaluate_ats_compatibility(SAMPLE_CV, SAMPLE_JD, "data_analyst")
        
        print(f"\n🎯 ATS EVALUATION RESULTS:")
        print(f"   Overall Score: {result.overall_score:.1f}/100")
        print(f"   Compatibility: {result.compatibility_level.value}")
        print(f"   Status: {result.status.value}")
        
        print(f"\n📈 Category Scores:")
        for category, score in result.category_scores.items():
            print(f"   {category}: {score:.1f}/100")
        
        print(f"\n💡 Feedback ({len(result.feedback)} items):")
        for i, feedback in enumerate(result.feedback[:3], 1):
            print(f"   {i}. {feedback}")
        
        print(f"\n🔧 Format Suggestions ({len(result.format_suggestions)} items):")
        for i, suggestion in enumerate(result.format_suggestions[:3], 1):
            print(f"   {i}. {suggestion}")
        
        print(f"\n🎯 Improvement Recommendations ({len(result.improvement_recommendations)} items):")
        for i, rec in enumerate(result.improvement_recommendations[:3], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n📊 Skill Matches ({len(result.skill_matches)} total):")
        matched_skills = [s for s in result.skill_matches if s.match_type != "missing"]
        missing_skills = [s for s in result.skill_matches if s.match_type == "missing"]
        
        print(f"   ✅ Matched: {len(matched_skills)} skills")
        print(f"   ❌ Missing: {len(missing_skills)} skills")
        
        if matched_skills:
            print(f"   Top matches: {[s.skill for s in matched_skills[:5]]}")
        
        if missing_skills:
            print(f"   Missing skills: {[s.skill for s in missing_skills[:5]]}")
        
        print(f"\n📏 Metrics Analysis ({len(result.metrics_analysis)} metrics found):")
        for metric in result.metrics_analysis[:3]:
            print(f"   {metric.type}: {metric.value} (impact: {metric.impact_score:.2f})")
        
    except Exception as e:
        print(f"❌ ATS evaluation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_ats_system()) 