#!/usr/bin/env python3
"""
Standalone test for ATS Score Calculator
Tests the ATS calculator independently to ensure it works correctly
"""

import sys
import os
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.ats.ats_score_calculator import ATSScoreCalculator, ATSScoreBreakdown

def test_ats_calculator():
    """Test the ATS score calculator with sample data"""
    
    print("🧪 Testing ATS Score Calculator...")
    
    # Initialize calculator
    calculator = ATSScoreCalculator()
    
    # Sample preextracted data (what would come from previous analysis)
    sample_preextracted_data = {
        "content": """
        Technical Skills Match Rate: 85%
        Soft Skills Match Rate: 70%
        Domain Keywords Match Rate: 60%
        MISSING FROM CV - Technical: 3 items
        MISSING FROM CV - Soft: 2 items
        MISSING FROM CV - Domain: 4 items
        """
    }
    
    # Sample component analysis (what would come from component analyzers)
    sample_component_analysis = {
        "skills": {
            "skills_analysis": [
                {
                    "skill": "Python",
                    "cv_evidence": "3+ years, pandas, scikit-learn, multiple projects",
                    "jd_application": "Data analysis and automation tasks",
                    "relevance_score": 95,
                    "skill_level": "Advanced",
                    "depth_indicators": ["Multiple libraries", "Project leadership", "3+ years"],
                    "synergy_bonus": 10
                }
            ],
            "overall_skills_score": 87,
            "strength_areas": ["Data Analysis", "Programming"],
            "improvement_areas": ["Database Administration", "Cloud Platforms"]
        },
        "experience": {
            "experience_analysis": {
                "cv_experience_years": 4,
                "cv_role_level": "Mid-Senior",
                "cv_progression": ["Junior Developer", "Senior Developer", "Team Lead"],
                "jd_required_years": "3-5 years",
                "jd_role_level": "Senior",
                "alignment_score": 85,
                "experience_gaps": [],
                "experience_strengths": ["Leadership experience", "Technical progression"],
                "quantified_achievements": ["Led team of 5", "Improved performance by 40%"]
            }
        },
        "industry": {
            "industry_analysis": {
                "cv_primary_industry": "Data Science and Analytics",
                "cv_domain_expertise": ["Data Analysis", "Business Intelligence", "Data Visualization"],
                "jd_target_industry": "International Aid and Development",
                "jd_domain_requirements": ["Data Mining", "Profile Analysis", "Segmentation Strategies"],
                "industry_alignment_score": 45,
                "domain_overlap_percentage": 50,
                "data_familiarity_score": 65,
                "stakeholder_fit_score": 40,
                "business_cycle_alignment": 30,
                "transferable_strengths": ["SQL Proficiency", "Power BI Dashboard Creation", "Analytical Problem-Solving"],
                "industry_gaps": ["Fundraising Analytics", "Non-Profit Sector Experience", "Donor-Centric Strategies"],
                "adaptation_timeline": "6-12 months"
            }
        },
        "seniority": {
            "seniority_analysis": {
                "cv_experience_years": 6,
                "cv_responsibility_scope": "Senior Individual Contributor",
                "cv_leadership_indicators": 7,
                "cv_decision_authority": "Project Level",
                "cv_stakeholder_level": "Department",
                "jd_required_seniority": "Senior",
                "jd_leadership_requirements": "Team Leadership Expected",
                "jd_decision_authority_needed": "Program Level",
                "jd_stakeholder_level": "Executive",
                "seniority_score": 75,
                "experience_match_percentage": 85,
                "responsibility_fit_percentage": 70,
                "leadership_readiness_score": 65,
                "growth_trajectory_score": 80,
                "seniority_strengths": ["Strong Technical Leadership", "Cross-functional Collaboration"],
                "seniority_gaps": ["Direct Report Management", "Executive Stakeholder Management"],
                "readiness_assessment": "Stretch Role with Development Support"
            }
        },
        "technical": {
            "technical_analysis": {
                "cv_sophistication_level": "Advanced",
                "cv_primary_domain": "Machine Learning & Data Science",
                "cv_core_competencies": ["Python", "SQL", "Data Visualization"],
                "cv_problem_complexity": 8,
                "cv_innovation_indicators": ["Published Research"],
                "jd_required_sophistication": "Intermediate",
                "jd_core_tech_stack": ["Python", "SQL", "Tableau", "Excel"],
                "jd_problem_complexity": 6,
                "jd_innovation_requirements": False,
                "technical_depth_score": 90,
                "core_skills_match_percentage": 85,
                "technical_stack_fit_percentage": 80,
                "complexity_readiness_score": 95,
                "learning_agility_score": 85,
                "technical_strengths": ["Advanced Analytics", "ML Implementation", "Data Architecture"],
                "technical_gaps": ["Tableau Proficiency", "Business Domain Context"],
                "overqualification_risk": "Moderate"
            }
        },
        "requirement_bonus": {
            "match_counts": {
                "total_required_keywords": 8,
                "total_preferred_keywords": 4,
                "matched_required_count": 5,
                "matched_preferred_count": 1,
                "missing_required": 3,
                "missing_preferred": 3
            },
            "bonus_breakdown": {
                "required_bonus": 2.5,
                "required_penalty": -1.5,
                "preferred_bonus": 0.2,
                "preferred_penalty": -0.45,
                "total_bonus": 0.75
            },
            "coverage_metrics": {
                "required_coverage": 62.5,
                "preferred_coverage": 25.0
            }
        }
    }
    
    # Sample extracted scores (what would come from component analysis)
    sample_extracted_scores = {
        "skills_relevance": 87.0,
        "experience_alignment": 85.0,
        "industry_fit": 45.0,
        "domain_overlap_percentage": 50.0,
        "data_familiarity_score": 65.0,
        "stakeholder_fit_score": 40.0,
        "business_cycle_alignment": 30.0,
        "role_seniority": 75.0,
        "experience_match_percentage": 85.0,
        "responsibility_fit_percentage": 70.0,
        "leadership_readiness_score": 65.0,
        "growth_trajectory_score": 80.0,
        "technical_depth": 90.0,
        "core_skills_match_percentage": 85.0,
        "technical_stack_fit_percentage": 80.0,
        "complexity_readiness_score": 95.0,
        "learning_agility_score": 85.0,
        "jd_problem_complexity": 6.0,
        "requirement_bonus": 0.75,
        "total_bonus": 0.75,
        "required_bonus": 2.5,
        "required_penalty": -1.5,
        "preferred_bonus": 0.2,
        "preferred_penalty": -0.45,
        "required_coverage": 62.5,
        "preferred_coverage": 25.0
    }
    
    try:
        print("📊 Calculating ATS score...")
        
        # Calculate ATS score
        ats_breakdown = calculator.calculate_ats_score(
            preextracted_data=sample_preextracted_data,
            component_analysis=sample_component_analysis,
            extracted_scores=sample_extracted_scores
        )
        
        print("✅ ATS Score Calculation Successful!")
        print(f"📈 Final ATS Score: {ats_breakdown.final_ats_score:.1f}/100")
        print(f"📊 Category Status: {ats_breakdown.category_status}")
        print(f"💡 Recommendation: {ats_breakdown.recommendation}")
        print(f"🔧 Technical Skills Match Rate: {ats_breakdown.technical_skills_match_rate:.1f}%")
        print(f"🎯 Soft Skills Match Rate: {ats_breakdown.soft_skills_match_rate:.1f}%")
        print(f"🏷️ Domain Keywords Match Rate: {ats_breakdown.domain_keywords_match_rate:.1f}%")
        print(f"⭐ Category 1 Score: {ats_breakdown.cat1_score:.1f}")
        print(f"⭐ Category 2 Score: {ats_breakdown.cat2_score:.1f}")
        print(f"🎁 Bonus Points: {ats_breakdown.bonus_points:.1f}")
        
        # Test JSON serialization
        print("\n🔄 Testing JSON serialization...")
        ats_dict = {
            "final_ats_score": ats_breakdown.final_ats_score,
            "category_status": ats_breakdown.category_status,
            "recommendation": ats_breakdown.recommendation,
            "technical_skills_match_rate": ats_breakdown.technical_skills_match_rate,
            "soft_skills_match_rate": ats_breakdown.soft_skills_match_rate,
            "domain_keywords_match_rate": ats_breakdown.domain_keywords_match_rate,
            "cat1_score": ats_breakdown.cat1_score,
            "cat2_score": ats_breakdown.cat2_score,
            "bonus_points": ats_breakdown.bonus_points,
            "technical_missing_count": ats_breakdown.technical_missing_count,
            "soft_missing_count": ats_breakdown.soft_missing_count,
            "domain_missing_count": ats_breakdown.domain_missing_count
        }
        
        # Save test results
        test_output_path = backend_dir / "test_ats_results.json"
        with open(test_output_path, 'w') as f:
            json.dump(ats_dict, f, indent=2)
        
        print(f"💾 Test results saved to: {test_output_path}")
        print("✅ ATS Calculator test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ ATS Calculator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ats_calculator()
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)
