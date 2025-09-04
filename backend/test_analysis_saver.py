#!/usr/bin/env python3
"""
Test script for Analysis Results Saver
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis_results_saver import AnalysisResultsSaver

def test_analysis_saver():
    """Test the analysis results saver with sample data"""
    
    # Sample data
    cv_text = """
    John Doe
    Software Engineer
    
    EXPERIENCE:
    - Senior Developer at TechCorp (2020-2023)
    - Python, JavaScript, React, Node.js
    - Led team of 5 developers
    - Improved performance by 40%
    
    EDUCATION:
    - Master of Data Science, University of Technology
    """
    
    jd_text = """
    Senior Software Engineer at Google
    
    REQUIREMENTS:
    - Python programming experience (required)
    - JavaScript and React (required)
    - AWS cloud experience (preferred)
    - Leadership experience (preferred)
    - Master's degree in Computer Science or related field (required)
    
    RESPONSIBILITIES:
    - Lead development team
    - Design and implement scalable solutions
    - Mentor junior developers
    """
    
    skill_comparison = {
        'matched': {
            'technical_skills': [
                {'jd_requirement': 'Python', 'cv_equivalent': 'Python'},
                {'jd_requirement': 'JavaScript', 'cv_equivalent': 'JavaScript'},
                {'jd_requirement': 'React', 'cv_equivalent': 'React'}
            ],
            'soft_skills': [
                {'jd_requirement': 'Leadership', 'cv_equivalent': 'Team leadership'}
            ]
        },
        'missing': {
            'technical_skills': ['AWS'],
            'soft_skills': []
        },
        'match_summary': {
            'total_matches': 4,
            'total_jd_requirements': 5,
            'match_percentage': 80
        }
    }
    
    ats_results = {
        'overall_ats_score': 85.5,
        'score_category': 'Strong',
        'detailed_breakdown': {
            'technical_skills_match': {
                'score': 75.0,
                'weight': 25.0,
                'contribution': 18.75
            },
            'soft_skills_match': {
                'score': 90.0,
                'weight': 10.0,
                'contribution': 9.0
            },
            'domain_keywords_match': {
                'score': 80.0,
                'weight': 8.0,
                'contribution': 6.4
            },
            'skills_relevance': {
                'score': 85.0,
                'weight': 12.0,
                'contribution': 10.2
            },
            'experience_alignment': {
                'score': 90.0,
                'weight': 15.0,
                'contribution': 13.5
            },
            'industry_fit': {
                'score': 85.0,
                'weight': 10.0,
                'contribution': 8.5
            },
            'role_seniority': {
                'score': 88.0,
                'weight': 8.0,
                'contribution': 7.04
            },
            'technical_depth': {
                'score': 82.0,
                'weight': 3.0,
                'contribution': 2.46
            },
            'requirement_bonus': {
                'essential_requirements': {
                    'matches': [
                        {'requirement': 'Python', 'jd_proof_text': 'Python programming experience (required)'},
                        {'requirement': 'JavaScript', 'jd_proof_text': 'JavaScript and React (required)'},
                        {'requirement': 'React', 'jd_proof_text': 'JavaScript and React (required)'}
                    ],
                    'missing': [
                        {'requirement': 'AWS', 'jd_proof_text': 'AWS cloud experience (preferred)'}
                    ]
                },
                'preferred_requirements': {
                    'matches': [
                        {'requirement': 'Leadership', 'jd_proof_text': 'Leadership experience (preferred)'}
                    ],
                    'missing': []
                },
                'essential_bonus': 2.0,
                'preferred_bonus': 1.0,
                'total_bonus': 3.0
            }
        },
        'detailed_analysis': {
            'skills_relevance': {
                'overall_skills_score': 85,
                'skills_analysis': [
                    {
                        'skill': 'Python',
                        'relevance_score': 95,
                        'skill_level': 'Advanced'
                    }
                ]
            },
            'experience_alignment': {
                'experience_analysis': {
                    'alignment_score': 90,
                    'cv_experience_years': 3,
                    'cv_role_level': 'Senior',
                    'jd_required_years': '3-5 years',
                    'jd_role_level': 'Senior'
                }
            },
            'missing_skills_impact': {
                'overall_impact_score': 75,
                'critical_gaps': ['AWS']
            }
        },
        'recommendations': [
            "Add AWS cloud experience to technical skills section",
            "Highlight leadership achievements more prominently",
            "Consider adding cloud platform certifications"
        ]
    }
    
    # Test the saver with debug enabled
    try:
        saver = AnalysisResultsSaver(debug=True)
        filepath = saver.save_analysis_results(
            cv_text=cv_text,
            jd_text=jd_text,
            skill_comparison=skill_comparison,
            ats_results=ats_results,
            company_name="Google"
        )
        
        print(f"✅ Analysis results saved successfully!")
        print(f"📁 File: {filepath}")
        
        # Read and display the first few lines
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            print("\n📄 First 500 characters of saved file:")
            print("-" * 50)
            print(content[:500])
            print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing analysis saver: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Analysis Results Saver...")
    success = test_analysis_saver()
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!") 