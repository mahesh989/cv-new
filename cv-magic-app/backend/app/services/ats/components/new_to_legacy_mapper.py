"""
Mapper to convert new 2-analyzer output to legacy 5-analyzer structure
This ensures frontend compatibility without any changes
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NewToLegacyMapper:
    """Maps new 2-analyzer results to legacy 5-analyzer structure for backward compatibility"""

    @staticmethod
    def map_to_legacy_structure(
        tech_skills_result: Dict[str, Any],
        exp_fit_result: Dict[str, Any],
        bonus_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Map new 2-analyzer results to legacy 5-analyzer structure.
        """
        logger.info("[MAPPER] Converting new analyzer results to legacy structure")

        tech_depth = tech_skills_result.get("technical_depth", {})
        skills_coverage = tech_skills_result.get("required_skills_coverage", {})
        stack_similarity = tech_skills_result.get("tech_stack_similarity", {})
        business_readiness = tech_skills_result.get("business_readiness", {})
        complexity = tech_skills_result.get("complexity_handling", {})
        learning = tech_skills_result.get("learning_adaptation", {})

        exp_alignment = exp_fit_result.get("experience_alignment", {})
        role_sim = exp_fit_result.get("role_similarity", {})
        seniority = exp_fit_result.get("seniority_match", {})
        leadership = exp_fit_result.get("leadership_readiness", {})
        industry = exp_fit_result.get("industry_transition_fit", {})

        legacy_structure = {
            "technical": {
                "technical_analysis": {
                    "technical_depth_score": tech_depth.get("score", 50),
                    "core_skills_match_percentage": skills_coverage.get("score", 50),
                    "technical_stack_fit_percentage": stack_similarity.get("score", 50),
                    "complexity_readiness_score": complexity.get("score", 50),
                    "learning_agility_score": learning.get("score", 50),
                    "jd_problem_complexity": complexity.get("jd_complexity_level", 5),
                    "technical_strengths": tech_depth.get("evidence", []),
                    "technical_gaps": tech_depth.get("gaps", []),
                    "cv_sophistication_level": "Derived from analysis",
                    "cv_primary_domain": "Extracted from CV",
                    "jd_required_sophistication": "Extracted from JD",
                    "overqualification_risk": "LOW",
                }
            },
            "skills": {
                "overall_skills_score": business_readiness.get("score", 50),
                "business_readiness_score": business_readiness.get("score", 50),
                "skills_analysis": [
                    {
                        "skill": "Consolidated skills analysis",
                        "relevance_score": business_readiness.get("score", 50),
                        "context": business_readiness.get("breakdown", ""),
                        "business_application": business_readiness.get("breakdown", ""),
                    }
                ],
                "corporate_skills_strength": business_readiness.get("breakdown", ""),
                "academic_skills_discount": "Applied in scoring",
                "strength_areas": tech_depth.get("evidence", []),
                "critical_gaps": skills_coverage.get("missing_critical", []),
                "immediate_value_skills": tech_depth.get("evidence", []),
                "training_investment_needed": skills_coverage.get("missing_critical", []),
            },
            "experience": {
                "experience_analysis": {
                    "cv_experience_years": str(
                        exp_alignment.get("cv_corporate_years", 0) + exp_alignment.get("cv_academic_years", 0)
                    ),
                    "cv_corporate_years": str(exp_alignment.get("cv_corporate_years", 0)),
                    "cv_academic_years": str(exp_alignment.get("cv_academic_years", 0)),
                    "cv_role_level": seniority.get("cv_level", "Unknown"),
                    "jd_required_years": str(exp_alignment.get("jd_required_years", 0)),
                    "jd_role_level": seniority.get("jd_level", "Unknown"),
                    "alignment_score": exp_alignment.get("score", 50),
                    "experience_gaps": leadership.get("gaps", []),
                    "experience_strengths": seniority.get("evidence", []),
                    "overqualification_risk": "LOW" if exp_alignment.get("score", 50) > 70 else "MEDIUM",
                    "cv_progression": ["Derived from analysis"],
                    "quantified_achievements": seniority.get("evidence", []),
                }
            },
            "seniority": {
                "seniority_analysis": {
                    "cv_corporate_years": str(exp_alignment.get("cv_corporate_years", 0)),
                    "cv_academic_years": str(exp_alignment.get("cv_academic_years", 0)),
                    "seniority_score": seniority.get("score", 50),
                    "corporate_seniority_match": seniority.get("score", 50),
                    "leadership_readiness_score": leadership.get("score", 50),
                    "experience_match_percentage": role_sim.get("score", 50),
                    "responsibility_fit_percentage": seniority.get("score", 50),
                    "growth_trajectory_score": learning.get("score", 50),
                    "cv_responsibility_scope": seniority.get("cv_level", "Unknown"),
                    "cv_leadership_indicators": "8" if leadership.get("score", 50) > 70 else "5",
                    "jd_required_seniority": seniority.get("jd_level", "Unknown"),
                    "overqualification_risk": "LOW" if seniority.get("score", 50) > 70 else "MEDIUM",
                    "seniority_strengths": seniority.get("evidence", []),
                    "seniority_gaps": leadership.get("gaps", []),
                    "readiness_assessment": f"Score: {seniority.get('score', 50)}",
                }
            },
            "industry": {
                "industry_analysis": {
                    "cv_primary_industry": industry.get("cv_industry", "Unknown"),
                    "jd_target_industry": industry.get("jd_industry", "Unknown"),
                    "industry_alignment_score": industry.get("score", 50),
                    "transition_type": industry.get("transition_type", "Unknown"),
                    "success_probability": "HIGH" if industry.get("score", 50) > 70 else "MEDIUM",
                    "hiring_risk_assessment": industry.get("risk_level", "MEDIUM RISK"),
                    "industry_strengths": [industry.get("reasoning", "")],
                    "critical_industry_gaps": [],
                    "corporate_background_bonus": "15" if industry.get("score", 50) > 60 else "5",
                    "domain_overlap_percentage": industry.get("score", 50),
                    "data_familiarity_score": complexity.get("score", 50),
                    "stakeholder_fit_score": leadership.get("score", 50),
                    "business_cycle_alignment": industry.get("score", 50),
                    "direct_industry_match": "YES" if industry.get("score", 50) > 80 else "PARTIAL",
                    "cultural_adaptation_difficulty": "LOW" if industry.get("score", 50) > 70 else "MEDIUM",
                    "adaptation_timeline": "3-6 months" if industry.get("score", 50) > 60 else "6-12 months",
                }
            },
            "requirement_bonus": bonus_result,
        }

        logger.info("[MAPPER] Legacy structure mapping completed")
        return legacy_structure

    @staticmethod
    def extract_scores_from_new_results(
        tech_skills_result: Dict[str, Any],
        exp_fit_result: Dict[str, Any],
        bonus_result: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Extract numerical scores from new analyzer results for score calculation.
        """
        logger.info("[MAPPER] Extracting scores from new analyzer results")

        scores = {
            "technical_depth": float(tech_skills_result.get("technical_depth", {}).get("score", 50)),
            "required_skills_coverage": float(tech_skills_result.get("required_skills_coverage", {}).get("score", 50)),
            "tech_stack_similarity": float(tech_skills_result.get("tech_stack_similarity", {}).get("score", 50)),
            "business_readiness": float(tech_skills_result.get("business_readiness", {}).get("score", 50)),
            "experience_alignment": float(exp_fit_result.get("experience_alignment", {}).get("score", 50)),
            "role_similarity": float(exp_fit_result.get("role_similarity", {}).get("score", 50)),
            "seniority_match": float(exp_fit_result.get("seniority_match", {}).get("score", 50)),
            "industry_transition_fit": float(exp_fit_result.get("industry_transition_fit", {}).get("score", 50)),
            "core_skills_match_percentage": float(
                tech_skills_result.get("required_skills_coverage", {}).get("score", 50)
            ),
            "technical_stack_fit_percentage": float(
                tech_skills_result.get("tech_stack_similarity", {}).get("score", 50)
            ),
            "data_familiarity_score": float(tech_skills_result.get("complexity_handling", {}).get("score", 50)),
            "complexity_readiness_score": float(tech_skills_result.get("complexity_handling", {}).get("score", 50)),
            "learning_agility_score": float(tech_skills_result.get("learning_adaptation", {}).get("score", 50)),
            "jd_problem_complexity": float(
                tech_skills_result.get("complexity_handling", {}).get("jd_complexity_level", 5)
            ),
            "experience_match_percentage": float(exp_fit_result.get("role_similarity", {}).get("score", 50)),
            "responsibility_fit_percentage": float(exp_fit_result.get("seniority_match", {}).get("score", 50)),
            "role_seniority": float(exp_fit_result.get("seniority_match", {}).get("score", 50)),
            "leadership_readiness_score": float(exp_fit_result.get("leadership_readiness", {}).get("score", 50)),
            "growth_trajectory_score": float(tech_skills_result.get("learning_adaptation", {}).get("score", 50)),
            "industry_fit": float(exp_fit_result.get("industry_transition_fit", {}).get("score", 50)),
            "domain_overlap_percentage": float(exp_fit_result.get("industry_transition_fit", {}).get("score", 50)),
            "stakeholder_fit_score": float(exp_fit_result.get("leadership_readiness", {}).get("score", 50)),
            "business_cycle_alignment": float(exp_fit_result.get("industry_transition_fit", {}).get("score", 50)),
            "requirement_bonus": float((bonus_result or {}).get("total_bonus", (bonus_result or {}).get("bonus", 0))),
        }

        logger.info("[MAPPER] Score extraction completed")
        return scores


