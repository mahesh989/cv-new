#!/usr/bin/env python3
"""
Comprehensive test suite for enhanced keyword integration and CV validation systems
Tests semantic validation, quality-focused validation, and end-to-end pipeline
"""

import sys
import os
import json
import logging
from typing import Dict, Any, List

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.tailored_cv.services.enhanced_keyword_integrator import EnhancedKeywordIntegrator, SemanticSkillsCategorizer
from app.tailored_cv.services.enhanced_cv_validator import EnhancedCVValidator, ValidationResult
from app.tailored_cv.models.cv_models import TailoredCV, CleanTailoredCV, ContactInfo, Education, ExperienceEntry, SkillCategory, Project, RecommendationAnalysis

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_cv_content():
    """Create realistic CV content for testing"""
    return """
    John Smith
    Data Analyst with 5+ years experience
    Email: john.smith@email.com
    Phone: +1-555-123-4567
    Location: San Francisco, CA
    
    EXPERIENCE:
    Senior Data Analyst at Tech Corp (2022-Present)
    - Led team of 8 analysts using Python and SQL to analyze 2M+ customer records
    - Developed 10+ Tableau dashboards for executives, improving decision-making by 35%
    - Optimized database queries reducing runtime by 60%
    - Collaborated with stakeholders to identify business opportunities
    
    Data Analyst at StartupXYZ (2020-2022)
    - Analyzed customer behavior data using Python and SQL
    - Created automated reports reducing manual work by 50%
    - Worked with AWS cloud infrastructure
    
    EDUCATION:
    Bachelor of Science in Computer Science, UC Berkeley (2020)
    
    SKILLS:
    Python, SQL, Tableau, Excel, AWS, Leadership, Communication
    """

def create_test_recommendations():
    """Create test recommendations with various keyword types"""
    return RecommendationAnalysis(
        company="Test Corp",
        job_title="Senior Data Analyst",
        missing_technical_skills=["Python", "SQL", "Tableau"],
        missing_soft_skills=["Leadership", "Communication"],
        missing_keywords=[
            # Tier 1 keywords (should always be added)
            "data analysis", "business intelligence", "analytics", "reporting",
            "communication", "leadership", "teamwork", "problem solving",
            
            # Tier 2 keywords (should be added if evidence exists)
            "database querying", "programming", "cloud computing", "data visualization",
            "efficiency", "optimization", "automation",
            
            # Tier 3 keywords (should never be added)
            "postgresql", "mysql", "dax", "tableau server", "power bi server",
            "scrum master", "pmp", "machine learning", "kubernetes"
        ],
        technical_enhancements=["Python", "SQL", "Data Analysis"],
        soft_skill_improvements=["Communication", "Leadership"],
        keyword_integration=["data analysis", "business intelligence"],
        critical_gaps=["data analysis", "business intelligence"],
        important_gaps=["Python", "SQL"],
        nice_to_have=["machine learning", "advanced statistics"]
    )

def create_test_cv_data():
    """Create test CV data for validation"""
    return {
        'contact': {
            'name': 'John Smith',
            'email': 'john.smith@email.com',
            'phone': '+1-555-123-4567',
            'location': 'San Francisco, CA'
        },
        'profile_summary': 'Data Analyst with 5+ years experience in data analysis and business intelligence. Expert in Python, SQL, Tableau with proven track record optimizing pipelines and creating executive dashboards.',
        'education': [
            {
                'institution': 'UC Berkeley',
                'degree': 'Bachelor of Science in Computer Science',
                'location': 'Berkeley, CA',
                'graduation_date': '2020',
                'gpa': '3.8'
            }
        ],
        'experience': [
            {
                'company': 'Tech Corp',
                'title': 'Senior Data Analyst',
                'location': 'San Francisco, CA',
                'start_date': '2022',
                'end_date': 'Present',
                'bullets': [
                    'Led team of 8 analysts using Python and SQL to analyze 2M+ customer records, increasing revenue by 40%',
                    'Developed 10+ Tableau dashboards for executives, improving decision-making by 35%',
                    'Optimized database queries reducing runtime by 60%'
                ]
            },
            {
                'company': 'StartupXYZ',
                'title': 'Data Analyst',
                'location': 'San Francisco, CA',
                'start_date': '2020',
                'end_date': '2022',
                'bullets': [
                    'Analyzed customer behavior data using Python and SQL, identifying trends that increased engagement by 25%',
                    'Created automated reports reducing manual work by 50% for the marketing team'
                ]
            }
        ],
        'projects': [
            {
                'name': 'Customer Segmentation Analysis',
                'bullets': [
                    'Developed machine learning model to segment 100K+ customers into 5 distinct groups',
                    'Implemented clustering algorithm achieving 85% accuracy in customer behavior prediction'
                ]
            }
        ],
        'skills': [
            {
                'category': 'Programming/Scripting',
                'skills': ['Python', 'SQL', 'R']
            },
            {
                'category': 'Data Analysis/BI',
                'skills': ['Tableau', 'Excel', 'Power BI']
            },
            {
                'category': 'Professional Skills',
                'skills': ['Leadership', 'Communication', 'Problem Solving']
            }
        ]
    }

def test_enhanced_keyword_integration():
    """Test enhanced keyword integration system"""
    logger.info("🧪 Testing Enhanced Keyword Integration System...")
    
    cv_content = create_test_cv_content()
    missing_keywords = [
        'data analysis', 'business intelligence', 'leadership', 'communication',
        'database querying', 'programming', 'cloud computing',
        'postgresql', 'mysql', 'machine learning', 'kubernetes'
    ]
    
    integrator = EnhancedKeywordIntegrator(cv_content, 'test_keywords')
    
    # Test keyword classification
    logger.info("🔍 Testing keyword classification...")
    for keyword in missing_keywords:
        classification = integrator.classify_keyword(keyword)
        logger.info(f"   {keyword} -> Tier {classification.tier} ({classification.category}): {classification.reason}")
    
    # Test semantic evidence checking
    logger.info("🔍 Testing semantic evidence validation...")
    test_keywords = ['leadership', 'database querying', 'postgresql', 'cloud computing']
    for keyword in test_keywords:
        has_evidence, reason = integrator.has_semantic_evidence(keyword)
        logger.info(f"   {keyword}: {has_evidence} - {reason}")
    
    # Test full integration validation
    logger.info("🔍 Testing full keyword integration validation...")
    results = integrator.validate_keyword_integration(missing_keywords)
    
    logger.info("📊 Keyword Integration Results:")
    logger.info(f"   - Tier 1 (Always): {len(results['tier1_integrate'])} keywords")
    logger.info(f"   - Tier 2 (With Evidence): {len(results['tier2_integrate'])} keywords")
    logger.info(f"   - Tier 2 (No Evidence): {len(results['tier2_no_evidence'])} keywords")
    logger.info(f"   - Tier 3 (Rejected): {len(results['tier3_reject'])} keywords")
    
    for category, keywords in results.items():
        if keywords:
            logger.info(f"   {category}: {keywords}")
    
    logger.info("✅ Enhanced keyword integration test completed")

def test_semantic_skills_categorization():
    """Test semantic skills categorization"""
    logger.info("🧪 Testing Semantic Skills Categorization...")
    
    skills = [
        'Python', 'SQL', 'Excel', 'Tableau', 'AWS', 
        'Leadership', 'Communication', 'Data Analysis',
        'Machine Learning', 'Kubernetes', 'PostgreSQL'
    ]
    
    categorizer = SemanticSkillsCategorizer('test_skills')
    grouped = categorizer.group_skills(skills)
    
    logger.info("📊 Skills Categorization Results:")
    for category, skill_list in grouped.items():
        logger.info(f"   {category}: {', '.join(skill_list)}")
    
    logger.info("✅ Semantic skills categorization test completed")

def test_enhanced_cv_validation():
    """Test enhanced CV validation system"""
    logger.info("🧪 Testing Enhanced CV Validation System...")
    
    cv_data = create_test_cv_data()
    original_cv = create_test_cv_content()
    recommendations = create_test_recommendations()
    
    # Convert recommendations to dict format
    recommendations_dict = {
        'critical_gaps': recommendations.critical_gaps or [],
        'missing_keywords': recommendations.missing_keywords or [],
        'technical_enhancements': recommendations.technical_enhancements or [],
        'soft_skill_improvements': recommendations.soft_skill_improvements or []
    }
    
    validator = EnhancedCVValidator('test_validation')
    result = validator.validate_tailored_cv(
        cv_data=cv_data,
        original_cv=original_cv,
        recommendations=recommendations_dict
    )
    
    logger.info("📊 Enhanced CV Validation Results:")
    logger.info(f"   - Passed: {result.passed}")
    logger.info(f"   - Score: {result.score:.1f}/100")
    logger.info(f"   - Issues: {len(result.issues)}")
    logger.info(f"   - Warnings: {len(result.warnings)}")
    
    if result.issues:
        logger.warning("   Issues found:")
        for issue in result.issues:
            logger.warning(f"     - {issue}")
    
    if result.warnings:
        logger.warning("   Warnings:")
        for warning in result.warnings:
            logger.warning(f"     - {warning}")
    
    logger.info("📊 Quality Metrics:")
    for metric, score in result.quality_metrics.items():
        logger.info(f"   - {metric}: {score:.1f}/100")
    
    logger.info("✅ Enhanced CV validation test completed")

def test_edge_cases():
    """Test edge cases and error handling"""
    logger.info("🧪 Testing Edge Cases and Error Handling...")
    
    # Test with empty CV content
    logger.info("🔍 Testing with empty CV content...")
    integrator = EnhancedKeywordIntegrator("", 'test_edge')
    results = integrator.validate_keyword_integration(['data analysis', 'leadership'])
    logger.info(f"   Empty CV results: {len(results['tier1_integrate'])} tier1, {len(results['tier2_integrate'])} tier2")
    
    # Test with minimal CV data
    logger.info("🔍 Testing with minimal CV data...")
    minimal_cv_data = {
        'contact': {'name': 'Test User'},
        'experience': [],
        'skills': []
    }
    
    validator = EnhancedCVValidator('test_edge')
    result = validator.validate_tailored_cv(
        cv_data=minimal_cv_data,
        original_cv="Minimal CV content",
        recommendations={}
    )
    
    logger.info(f"   Minimal CV validation: Passed={result.passed}, Score={result.score:.1f}")
    
    # Test with problematic data
    logger.info("🔍 Testing with problematic data...")
    problematic_cv_data = {
        'contact': {'name': 'Test User'},
        'profile_summary': 'A' * 200,  # Too long
        'experience': [
            {'bullets': ['Bullet 1', 'Bullet 2', 'Bullet 3', 'Bullet 4', 'Bullet 5']}  # Too many bullets
        ],
        'education': [
            {'degree': 'PhD in Computer Science'},
            {'degree': 'Master of Business Administration'},
            {'degree': 'Master of Science in Data Science'},
            {'degree': 'Bachelor of Science in Mathematics'}
        ],
        'skills': []
    }
    
    result = validator.validate_tailored_cv(
        cv_data=problematic_cv_data,
        original_cv="Original CV content",
        recommendations={'critical_gaps': ['data analysis']}
    )
    
    logger.info(f"   Problematic CV validation: Passed={result.passed}, Score={result.score:.1f}")
    logger.info(f"   Issues: {len(result.issues)}, Warnings: {len(result.warnings)}")
    
    logger.info("✅ Edge cases and error handling test completed")

def test_performance():
    """Test performance with large datasets"""
    logger.info("🧪 Testing Performance with Large Datasets...")
    
    # Create large CV content
    large_cv_content = "Data Analyst with experience in " + "Python, SQL, Tableau, " * 100
    large_keywords = [f"keyword_{i}" for i in range(100)]
    
    logger.info("🔍 Testing with large keyword set...")
    integrator = EnhancedKeywordIntegrator(large_cv_content, 'test_perf')
    
    import time
    start_time = time.time()
    results = integrator.validate_keyword_integration(large_keywords)
    end_time = time.time()
    
    logger.info(f"   Processed {len(large_keywords)} keywords in {end_time - start_time:.2f} seconds")
    logger.info(f"   Results: {len(results['tier1_integrate'])} tier1, {len(results['tier2_integrate'])} tier2")
    
    # Test with large CV data
    logger.info("🔍 Testing with large CV data...")
    large_cv_data = {
        'contact': {'name': 'Test User'},
        'profile_summary': 'Data Analyst with extensive experience',
        'experience': [
            {
                'bullets': [f'Bullet {i} with some content' for i in range(50)]
            }
        ],
        'skills': [
            {'category': f'Category {i}', 'skills': [f'skill_{j}' for j in range(10)]}
            for i in range(20)
        ]
    }
    
    start_time = time.time()
    validator = EnhancedCVValidator('test_perf')
    result = validator.validate_tailored_cv(
        cv_data=large_cv_data,
        original_cv=large_cv_content,
        recommendations={'critical_gaps': ['data analysis']}
    )
    end_time = time.time()
    
    logger.info(f"   Validated large CV in {end_time - start_time:.2f} seconds")
    logger.info(f"   Score: {result.score:.1f}, Passed: {result.passed}")
    
    logger.info("✅ Performance test completed")

def run_comprehensive_test():
    """Run all enhanced system tests"""
    logger.info("🚀 Starting Comprehensive Enhanced Systems Test Suite...")
    
    try:
        # Test enhanced keyword integration
        test_enhanced_keyword_integration()
        
        # Test semantic skills categorization
        test_semantic_skills_categorization()
        
        # Test enhanced CV validation
        test_enhanced_cv_validation()
        
        # Test edge cases
        test_edge_cases()
        
        # Test performance
        test_performance()
        
        logger.info("🎉 All Enhanced Systems Tests Completed Successfully!")
        
    except Exception as e:
        logger.error(f"❌ Comprehensive test failed: {e}")
        raise

if __name__ == "__main__":
    run_comprehensive_test()
