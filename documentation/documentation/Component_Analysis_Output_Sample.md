# Component Analysis Output Sample

This document shows what the component analysis already saves when triggered after skills analysis.

## Current Implementation

When component analysis runs (via `modular_ats_orchestrator.run_component_analysis()`), it executes all 5 analyzers and saves their complete outputs in the `{company}_skills_analysis.json` file.

## Sample Output Structure

Here's what gets saved in the `component_analysis_entries` array:

```json
{
  "component_analysis_entries": [
    {
      "timestamp": "2025-09-13T06:22:47.123",
      "analysis_type": "modular_component_analysis",
      "component_analyses": {
        
        // 1. SKILLS RELEVANCE ANALYZER OUTPUT
        "skills": {
          "overall_skills_score": 85.5,
          "skills_breakdown": {
            "technical_skills": {
              "cv_skills": ["Python", "React", "AWS", "Docker"],
              "jd_requirements": ["Python", "JavaScript", "Cloud", "DevOps"],
              "matched": ["Python"],
              "related": ["React->JavaScript", "AWS->Cloud", "Docker->DevOps"],
              "score": 87.5
            },
            "soft_skills": {
              "cv_skills": ["Leadership", "Communication", "Problem Solving"],
              "jd_requirements": ["Team Leadership", "Communication"],
              "matched": ["Communication"],
              "related": ["Leadership->Team Leadership"],
              "score": 100.0
            }
          },
          "detailed_analysis": "Strong alignment in programming languages..."
        },
        
        // 2. EXPERIENCE ANALYZER OUTPUT
        "experience": {
          "experience_analysis": {
            "alignment_score": 90.0,
            "cv_experience_years": 5,
            "jd_required_years": "3-5 years",
            "experience_level_match": "Perfect Match",
            "career_progression": {
              "current_level": "Senior",
              "required_level": "Senior",
              "progression_fit": "Well-aligned"
            },
            "relevant_experience": {
              "direct_match_years": 4,
              "related_experience_years": 1,
              "total_relevant": 5
            }
          },
          "detailed_reasoning": "Candidate has 5 years of experience..."
        },
        
        // 3. INDUSTRY FIT ANALYZER OUTPUT
        "industry": {
          "industry_analysis": {
            "industry_alignment_score": 75.0,
            "domain_overlap_percentage": 80.0,
            "data_familiarity_score": 70.0,
            "stakeholder_fit_score": 75.0,
            "business_cycle_alignment": 75.0,
            "cv_industries": ["Technology", "SaaS", "E-commerce"],
            "jd_industry": "FinTech",
            "domain_knowledge": {
              "matched_domains": ["Technology"],
              "transferable_domains": ["SaaS", "E-commerce"],
              "missing_domains": ["Finance", "Banking"]
            }
          },
          "detailed_analysis": "While candidate lacks direct FinTech experience..."
        },
        
        // 4. SENIORITY ANALYZER OUTPUT
        "seniority": {
          "seniority_analysis": {
            "seniority_score": 85.0,
            "experience_match_percentage": 90.0,
            "responsibility_fit_percentage": 85.0,
            "leadership_readiness_score": 80.0,
            "growth_trajectory_score": 85.0,
            "cv_seniority_level": "Senior",
            "jd_seniority_level": "Senior",
            "leadership_indicators": {
              "team_size_managed": 5,
              "project_complexity": "High",
              "strategic_involvement": "Moderate"
            },
            "readiness_assessment": {
              "current_readiness": "Ready",
              "growth_potential": "High",
              "gaps": ["Strategic planning experience"]
            }
          },
          "detailed_reasoning": "Candidate demonstrates senior-level capabilities..."
        },
        
        // 5. TECHNICAL ANALYZER OUTPUT
        "technical": {
          "technical_analysis": {
            "technical_depth_score": 88.0,
            "core_skills_match_percentage": 85.0,
            "technical_stack_fit_percentage": 90.0,
            "complexity_readiness_score": 87.0,
            "learning_agility_score": 85.0,
            "jd_problem_complexity": 8.0,
            "technical_stack": {
              "languages": {
                "cv": ["Python", "JavaScript", "Go"],
                "jd": ["Python", "TypeScript"],
                "match_level": "High"
              },
              "frameworks": {
                "cv": ["Django", "React", "FastAPI"],
                "jd": ["Flask", "React", "Node.js"],
                "match_level": "Good"
              },
              "tools": {
                "cv": ["Docker", "Kubernetes", "Jenkins"],
                "jd": ["Docker", "AWS", "CircleCI"],
                "match_level": "Good"
              }
            },
            "complexity_assessment": {
              "handled_complexity": "High",
              "required_complexity": "High",
              "examples": ["Microservices architecture", "Distributed systems"]
            }
          },
          "detailed_analysis": "Strong technical foundation with excellent depth..."
        },
        
        // BONUS CALCULATION (Not an analyzer, but included)
        "requirement_bonus": {
          "match_counts": {
            "total_required_keywords": 10,
            "total_preferred_keywords": 8,
            "matched_required_count": 8,
            "matched_preferred_count": 5
          },
          "bonus_breakdown": {
            "required_bonus": 8.0,
            "required_penalty": -2.0,
            "preferred_bonus": 2.5,
            "preferred_penalty": -1.5,
            "total_bonus": 7.0
          },
          "coverage_metrics": {
            "required_coverage": 80.0,
            "preferred_coverage": 62.5
          }
        }
      },
      
      // EXTRACTED SCORES (Summary of all scores)
      "extracted_scores": {
        "skills_relevance": 85.5,
        "experience_alignment": 90.0,
        "industry_fit": 75.0,
        "role_seniority": 85.0,
        "technical_depth": 88.0,
        "domain_overlap_percentage": 80.0,
        "data_familiarity_score": 70.0,
        "stakeholder_fit_score": 75.0,
        "business_cycle_alignment": 75.0,
        "experience_match_percentage": 90.0,
        "responsibility_fit_percentage": 85.0,
        "leadership_readiness_score": 80.0,
        "growth_trajectory_score": 85.0,
        "core_skills_match_percentage": 85.0,
        "technical_stack_fit_percentage": 90.0,
        "complexity_readiness_score": 87.0,
        "learning_agility_score": 85.0,
        "jd_problem_complexity": 8.0,
        "requirement_bonus": 7.0,
        "required_coverage": 80.0,
        "preferred_coverage": 62.5
      }
    }
  ]
}
```

## Key Points

1. **All 5 Analyzers Run**: The system already executes all component analyzers
2. **Complete Outputs Saved**: Full analysis results from each analyzer are stored
3. **Structured Format**: Each analyzer's output follows its specific format
4. **Scores Extracted**: Key scores are extracted and stored separately for easy access
5. **Appended to Existing File**: Results are added to the existing skills analysis file

## Accessing the Results

The component analysis results can be found in:
```
/cv-analysis/{company}/{company}_skills_analysis.json
```

Look for the `component_analysis_entries` array, which contains all the analyzer outputs.

## What Each Analyzer Provides

1. **Skills Relevance Analyzer**
   - Overall skills score
   - Breakdown by skill categories
   - Matched vs related skills
   - Detailed analysis text

2. **Experience Analyzer**
   - Years of experience alignment
   - Career progression fit
   - Relevant experience breakdown
   - Experience level matching

3. **Industry Fit Analyzer**
   - Industry alignment score
   - Domain knowledge assessment
   - Multiple sub-scores for different aspects
   - Transferable skills identification

4. **Seniority Analyzer**
   - Seniority level matching
   - Leadership readiness
   - Responsibility alignment
   - Growth trajectory assessment

5. **Technical Analyzer**
   - Technical depth evaluation
   - Technology stack matching
   - Complexity handling assessment
   - Learning agility score

All of this data is already being captured and saved when component analysis runs!
