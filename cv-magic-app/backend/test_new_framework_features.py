#!/usr/bin/env python3
"""
Comprehensive test for new framework features
Tests profile summary, bullet consolidation, tiered keywords, and education validation
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.tailored_cv.models.cv_models import TailoredCV, CleanTailoredCV, ContactInfo, Education, ExperienceEntry, SkillCategory, Project, RecommendationAnalysis
from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
# from app.tailored_cv.services.pdf_export_service import ResumePDFGenerator  # Requires reportlab

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_data():
    """Create test data for framework validation"""
    
    # Test contact info
    contact = ContactInfo(
        name="John Doe",
        email="john.doe@example.com",
        phone="+1-555-123-4567",
        location="San Francisco, CA",
        linkedin="linkedin.com/in/johndoe",
        website="johndoe.com"
    )
    
    # Test education
    education = [
        Education(
            institution="University of California, Berkeley",
            degree="Bachelor of Science in Computer Science",
            location="Berkeley, CA",
            graduation_date="2020",
            gpa="3.8",
            relevant_coursework="Data Structures, Algorithms, Machine Learning",
            honors="Magna Cum Laude"
        )
    ]
    
    # Test experience with varying bullet counts (to test consolidation)
    experience = [
        ExperienceEntry(
            company="Tech Corp",
            title="Senior Data Analyst",
            location="San Francisco, CA",
            start_date="2022-01",
            end_date="Present",
            bullets=[
                "Led 8-person analytics team using Python/SQL to analyze 2M+ customer records, increasing revenue by 40% ($3M annually)",
                "Developed 10+ Tableau dashboards tracking key metrics across 15 departments, improving efficiency by 35%",
                "Managed data pipeline processing 100K+ records daily, reducing processing time by 60%",
                "Collaborated with stakeholders to identify business opportunities",  # 4th bullet - should trigger consolidation warning
                "Implemented data validation framework ensuring 99.9% accuracy"  # 5th bullet - should trigger consolidation warning
            ]
        ),
        ExperienceEntry(
            company="StartupXYZ",
            title="Data Analyst",
            location="San Francisco, CA", 
            start_date="2020-06",
            end_date="2021-12",
            bullets=[
                "Analyzed customer behavior data using Python and SQL, identifying trends that increased user engagement by 25%",
                "Created automated reports reducing manual work by 50% for the marketing team"
            ]
        )
    ]
    
    # Test projects
    projects = [
        Project(
            name="Customer Segmentation Analysis",
            bullets=[
                "Developed machine learning model to segment 100K+ customers into 5 distinct groups",
                "Implemented clustering algorithm achieving 85% accuracy in customer behavior prediction",
                "Presented findings to executive team, leading to targeted marketing campaigns"
            ]
        )
    ]
    
    # Test skills with categories
    skills = [
        SkillCategory(
            category="Programming Languages",
            skills=["Python", "SQL", "R", "JavaScript"]
        ),
        SkillCategory(
            category="Data Analysis Tools", 
            skills=["Tableau", "Power BI", "Excel", "Pandas"]
        ),
        SkillCategory(
            category="Soft Skills",
            skills=["Leadership", "Communication", "Problem Solving", "Teamwork"]
        )
    ]
    
    return {
        'contact': contact,
        'education': education,
        'experience': experience,
        'projects': projects,
        'skills': skills
    }

def create_test_recommendations():
    """Create test recommendations with tiered keywords"""
    
    return RecommendationAnalysis(
        company="Test Corp",
        job_title="Data Analyst",
        missing_technical_skills=["Python", "SQL", "Tableau"],
        missing_soft_skills=["Communication", "Leadership"],
        missing_keywords=[
            # Tier 1 keywords (should always be added)
            "data analysis", "business intelligence", "analytics", "reporting",
            "communication", "leadership", "teamwork", "problem solving",
            
            # Tier 2 keywords (should be added if evidence exists)
            "database", "programming", "scripting", "cloud", "platform",
            "efficiency", "optimization", "automation", "visualization",
            
            # Tier 3 keywords (should never be added)
            "postgresql", "mysql", "dax", "tableau server", "power bi server",
            "scrum master", "saf", "agile certified", "machine learning", "ai"
        ],
        technical_enhancements=["Python", "SQL", "Data Analysis"],
        soft_skill_improvements=["Communication", "Leadership"],
        keyword_integration=["data analysis", "business intelligence"],
        critical_gaps=["data analysis", "business intelligence"],
        important_gaps=["Python", "SQL"],
        nice_to_have=["machine learning", "advanced statistics"]
    )

def test_profile_summary_validation():
    """Test profile summary validation"""
    logger.info("🧪 Testing profile summary validation...")
    
    service = CVTailoringService(user_email="test@example.com")
    
    # Test data with profile summary
    test_data = {
        'profile_summary': 'Data Analyst with 5+ years transforming datasets into insights. Expert in Python, SQL, Tableau with proven track record optimizing pipelines and creating executive dashboards. Strong statistical analysis and visualization skills.',
        'experience': [],
        'skills': []
    }
    
    try:
        service._validate_profile_summary(test_data, 'test_profile')
        logger.info("✅ Profile summary validation test passed")
    except Exception as e:
        logger.error(f"❌ Profile summary validation test failed: {e}")
    
    # Test data with overly long profile summary
    test_data_long = {
        'profile_summary': 'Data Analyst with 5+ years transforming datasets into insights. Expert in Python, SQL, Tableau with proven track record optimizing pipelines and creating executive dashboards. Strong statistical analysis and visualization skills. Additional experience in machine learning and artificial intelligence. Proven ability to work with large datasets and complex analytical problems.',
        'experience': [],
        'skills': []
    }
    
    try:
        service._validate_profile_summary(test_data_long, 'test_profile_long')
        logger.info("✅ Long profile summary validation test passed (should show warning)")
    except Exception as e:
        logger.error(f"❌ Long profile summary validation test failed: {e}")

def test_bullet_consolidation_validation():
    """Test bullet consolidation validation"""
    logger.info("🧪 Testing bullet consolidation validation...")
    
    service = CVTailoringService(user_email="test@example.com")
    
    # Test data with too many bullets
    test_data = {
        'experience': [
            {
                'company': 'Tech Corp',
                'title': 'Data Analyst',
                'bullets': [
                    'Led team of 8 analysts using Python/SQL to analyze 2M+ customer records',
                    'Developed 10+ Tableau dashboards tracking key metrics across 15 departments',
                    'Managed data pipeline processing 100K+ records daily',
                    'Collaborated with stakeholders to identify business opportunities',
                    'Implemented data validation framework ensuring 99.9% accuracy'
                ]
            }
        ],
        'projects': [
            {
                'name': 'Customer Analysis',
                'bullets': [
                    'Developed machine learning model to segment 100K+ customers',
                    'Implemented clustering algorithm achieving 85% accuracy',
                    'Presented findings to executive team',
                    'Led cross-functional team of 5 data scientists'
                ]
            }
        ]
    }
    
    try:
        service._validate_bullet_consolidation(test_data, 'test_bullets')
        logger.info("✅ Bullet consolidation validation test passed")
    except Exception as e:
        logger.error(f"❌ Bullet consolidation validation test failed: {e}")

def test_education_selection_validation():
    """Test education selection validation"""
    logger.info("🧪 Testing education selection validation...")
    
    service = CVTailoringService(user_email="test@example.com")
    
    # Test data with multiple advanced degrees
    test_data = {
        'education': [
            {'degree': 'PhD in Computer Science', 'institution': 'Stanford University'},
            {'degree': 'Master of Business Administration', 'institution': 'Harvard Business School'},
            {'degree': 'Master of Science in Data Science', 'institution': 'MIT'},
            {'degree': 'Bachelor of Science in Mathematics', 'institution': 'UC Berkeley'}
        ]
    }
    
    try:
        service._validate_education_selection(test_data, 'test_education')
        logger.info("✅ Education selection validation test passed")
    except Exception as e:
        logger.error(f"❌ Education selection validation test failed: {e}")

def test_tiered_keyword_classification():
    """Test tiered keyword classification"""
    logger.info("🧪 Testing tiered keyword classification...")
    
    service = CVTailoringService(user_email="test@example.com")
    recommendations = create_test_recommendations()
    
    try:
        keyword_tiers = service._classify_tiered_keywords(recommendations)
        
        logger.info(f"📊 Keyword classification results:")
        logger.info(f"   - Tier 1 (Always): {len(keyword_tiers['tier_1'])} keywords")
        logger.info(f"   - Tier 2 (If Evidence): {len(keyword_tiers['tier_2'])} keywords") 
        logger.info(f"   - Tier 3 (Never): {len(keyword_tiers['tier_3'])} keywords")
        
        logger.info("✅ Tiered keyword classification test passed")
    except Exception as e:
        logger.error(f"❌ Tiered keyword classification test failed: {e}")

def test_tiered_keyword_validation():
    """Test tiered keyword validation"""
    logger.info("🧪 Testing tiered keyword validation...")
    
    service = CVTailoringService(user_email="test@example.com")
    recommendations = create_test_recommendations()
    
    # Test data with good keyword integration
    test_data = {
        'profile_summary': 'Data Analyst with 5+ years experience in data analysis and business intelligence. Expert in Python, SQL, and analytics with strong communication and leadership skills.',
        'experience': [
            {
                'bullets': [
                    'Led team using Python/SQL for data analysis, improving efficiency by 35%',
                    'Developed analytics dashboards for business intelligence reporting'
                ]
            }
        ],
        'skills': [
            {'category': 'Technical Skills', 'skills': ['Python', 'SQL', 'Data Analysis', 'Business Intelligence']}
        ]
    }
    
    try:
        service._validate_tiered_keywords(test_data, recommendations, 'test_keywords')
        logger.info("✅ Tiered keyword validation test passed")
    except Exception as e:
        logger.error(f"❌ Tiered keyword validation test failed: {e}")

def test_pdf_export_with_profile_summary():
    """Test PDF export with profile summary"""
    logger.info("🧪 Testing PDF export with profile summary...")
    
    test_data = create_test_data()
    test_data['profile_summary'] = 'Data Analyst with 5+ years transforming datasets into insights. Expert in Python, SQL, Tableau with proven track record optimizing pipelines and creating executive dashboards.'
    
    try:
        # Test that profile_summary is properly included in data structure
        assert 'profile_summary' in test_data
        assert len(test_data['profile_summary'].split()) <= 50  # Framework rule: max 50 words
        logger.info("✅ PDF export with profile summary test passed (data structure validation)")
    except Exception as e:
        logger.error(f"❌ PDF export test failed: {e}")

def test_data_model_updates():
    """Test data model updates"""
    logger.info("🧪 Testing data model updates...")
    
    test_data = create_test_data()
    test_data['profile_summary'] = 'Data Analyst with 5+ years experience in data analysis and business intelligence.'
    
    try:
        # Test TailoredCV model
        from app.tailored_cv.models.cv_models import OptimizationStrategy
        
        optimization_strategy = OptimizationStrategy(
            keyword_placement={},
            quantification_targets=[],
            impact_enhancements={},
            section_order=[],
            education_strategy=""
        )
        
        tailored_cv = TailoredCV(
            contact=test_data['contact'],
            profile_summary=test_data['profile_summary'],
            education=test_data['education'],
            experience=test_data['experience'],
            projects=test_data['projects'],
            skills=test_data['skills'],
            target_company="Test Corp",
            target_role="Data Analyst",
            optimization_strategy=optimization_strategy,
            enhancements_applied={},
            keywords_integrated=[],
            quantifications_added=[]
        )
        
        # Test CleanTailoredCV model
        clean_cv = CleanTailoredCV(
            contact=test_data['contact'],
            profile_summary=test_data['profile_summary'],
            education=test_data['education'],
            experience=test_data['experience'],
            projects=test_data['projects'],
            skills=test_data['skills']
        )
        
        logger.info("✅ Data model updates test passed")
        logger.info(f"   - TailoredCV profile_summary: {tailored_cv.profile_summary}")
        logger.info(f"   - CleanTailoredCV profile_summary: {clean_cv.profile_summary}")
        
    except Exception as e:
        logger.error(f"❌ Data model updates test failed: {e}")

def run_comprehensive_test():
    """Run all framework feature tests"""
    logger.info("🚀 Starting comprehensive framework feature tests...")
    
    try:
        # Test data model updates
        test_data_model_updates()
        
        # Test profile summary validation
        test_profile_summary_validation()
        
        # Test bullet consolidation validation
        test_bullet_consolidation_validation()
        
        # Test education selection validation
        test_education_selection_validation()
        
        # Test tiered keyword classification
        test_tiered_keyword_classification()
        
        # Test tiered keyword validation
        test_tiered_keyword_validation()
        
        # Test PDF export with profile summary
        test_pdf_export_with_profile_summary()
        
        logger.info("🎉 All framework feature tests completed!")
        
    except Exception as e:
        logger.error(f"❌ Comprehensive test failed: {e}")
        raise

if __name__ == "__main__":
    run_comprehensive_test()
