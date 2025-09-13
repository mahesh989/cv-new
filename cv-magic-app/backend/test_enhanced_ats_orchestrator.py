#!/usr/bin/env python3
"""
Test for Enhanced ATS Orchestrator
Tests the complete enhanced ATS analysis workflow
"""

import sys
import os
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.ats.enhanced_ats_orchestrator import EnhancedATSOrchestrator

def test_enhanced_ats_orchestrator():
    """Test the enhanced ATS orchestrator with sample data"""
    
    print("🧪 Testing Enhanced ATS Orchestrator...")
    
    # Initialize orchestrator
    orchestrator = EnhancedATSOrchestrator()
    
    # Sample CV content
    sample_cv_content = """
    John Smith
    Senior Data Scientist
    
    EXPERIENCE:
    - Senior Data Scientist at TechCorp (2020-2024)
      * Led a team of 5 data scientists
      * Developed machine learning models using Python, pandas, scikit-learn
      * Improved system performance by 40%
      * Created Power BI dashboards for business intelligence
      * Worked with SQL databases and data visualization
    
    - Data Analyst at DataCorp (2018-2020)
      * Analyzed large datasets using Python and SQL
      * Created data visualizations and reports
      * Collaborated with cross-functional teams
      * Strong communication and leadership skills
    
    SKILLS:
    Technical: Python, SQL, Machine Learning, Data Analysis, Power BI, Excel, Tableau
    Soft: Leadership, Communication, Teamwork, Problem Solving, Analytical Thinking
    
    EDUCATION:
    Master's in Data Science, University of Technology (2018)
    """
    
    # Sample job description
    sample_jd = """
    Senior Data Analyst - International Aid Organization
    
    We are seeking a Senior Data Analyst to join our team and help drive data-driven decisions 
    in international aid and development.
    
    REQUIREMENTS:
    - 3-5 years of experience in data analysis
    - Strong Python programming skills
    - SQL database experience
    - Experience with data visualization tools (Tableau, Power BI)
    - Excellent communication skills
    - Leadership experience preferred
    - Experience in non-profit or international development preferred
    
    RESPONSIBILITIES:
    - Analyze donor data and fundraising metrics
    - Create data mining strategies for profile analysis
    - Develop segmentation strategies for donor engagement
    - Lead data analysis projects
    - Present findings to executive stakeholders
    - Manage junior analysts
    
    PREFERRED:
    - Experience with fundraising analytics
    - Knowledge of donor management systems
    - International development experience
    """
    
    # Sample company info
    sample_company_info = "International Aid Organization focused on humanitarian assistance and development programs"
    
    try:
        print("📊 Running enhanced ATS analysis...")
        
        # Run the analysis
        results = orchestrator.analyze_cv_job_fit(
            cv_content=sample_cv_content,
            job_description=sample_jd,
            company_info=sample_company_info,
            current_industry="Data Science and Analytics"
        )
        
        print("✅ Enhanced ATS Analysis Successful!")
        print(f"📈 Final ATS Score: {results.final_ats_score:.1f}/100")
        print(f"📊 Overall Assessment: {results.overall_assessment}")
        print(f"⏱️ Processing Time: {results.processing_time_ms}ms")
        print(f"🎯 Confidence Score: {results.confidence_score:.1%}")
        
        print(f"\n🔧 Technical Skills Match Rate: {results.ats_breakdown.technical_skills_match_rate:.1f}%")
        print(f"🎯 Soft Skills Match Rate: {results.ats_breakdown.soft_skills_match_rate:.1f}%")
        print(f"🏷️ Domain Keywords Match Rate: {results.ats_breakdown.domain_keywords_match_rate:.1f}%")
        
        print(f"\n💪 Key Strengths:")
        for strength in results.key_strengths:
            print(f"  • {strength}")
        
        print(f"\n⚠️ Critical Gaps:")
        for gap in results.critical_gaps:
            print(f"  • {gap}")
        
        print(f"\n💡 Recommendations:")
        for rec in results.improvement_recommendations:
            print(f"  • {rec}")
        
        # Test JSON export
        print("\n🔄 Testing JSON export...")
        export_results = orchestrator.export_results_json(results)
        
        # Save test results
        test_output_path = backend_dir / "test_enhanced_ats_results.json"
        with open(test_output_path, 'w') as f:
            json.dump(export_results, f, indent=2, default=str)
        
        print(f"💾 Enhanced ATS results saved to: {test_output_path}")
        print("✅ Enhanced ATS Orchestrator test completed successfully!")
        
        return True, results
        
    except Exception as e:
        print(f"❌ Enhanced ATS Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

if __name__ == "__main__":
    success, results = test_enhanced_ats_orchestrator()
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)
