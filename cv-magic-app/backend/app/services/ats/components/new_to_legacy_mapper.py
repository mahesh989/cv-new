"""
New to Legacy Structure Mapper

Maps the new 2-analyzer output structure to the old 5-analyzer structure
for backward compatibility with frontend and existing code.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NewToLegacyMapper:
    """Maps new unified analyzer results to legacy 5-analyzer structure"""

    @staticmethod
    def map_to_legacy_structure(
        technical_skills_result: Dict[str, Any],
        experience_fit_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map new 2-analyzer results to legacy 5-analyzer structure.
        
        Args:
            technical_skills_result: Result from TechnicalSkillsAnalyzer
            experience_fit_result: Result from ExperienceFitAnalyzer
            
        Returns:
            Dict with legacy structure matching old 5-analyzer output
        """
        logger.info("[MAPPER] Mapping new analyzer results to legacy structure")
        
        # Extract scores from new structure
        tech_depth = technical_skills_result.get("technical_depth", {}).get("score", 50)
        skills_coverage = technical_skills_result.get("required_skills_coverage", {}).get("score", 50)
        tech_stack = technical_skills_result.get("tech_stack_similarity", {}).get("score", 50)
        business_readiness = technical_skills_result.get("business_readiness", {}).get("score", 50)
        complexity = technical_skills_result.get("complexity_handling", {}).get("score", 50)
        learning = technical_skills_result.get("learning_adaptation", {}).get("score", 50)
        jd_complexity = technical_skills_result.get("complexity_handling", {}).get("jd_complexity_level", 5)
        
        exp_alignment = experience_fit_result.get("experience_alignment", {}).get("score", 50)
        role_similarity = experience_fit_result.get("role_similarity", {}).get("score", 50)
        seniority_match = experience_fit_result.get("seniority_match", {}).get("score", 50)
        leadership = experience_fit_result.get("leadership_readiness", {}).get("score", 50)
        industry_fit = experience_fit_result.get("industry_transition_fit", {}).get("score", 50)
        
        # Map to legacy structure
        legacy_structure = {
            # Skills analyzer structure
            "skills": {
                "skills_analysis": [],
                "overall_skills_score": skills_coverage,  # Use required_skills_coverage as overall
                "corporate_skills_strength": technical_skills_result.get("business_readiness", {}).get("breakdown", "Analysis complete"),
                "academic_skills_discount": "N/A - unified analysis",
                "business_readiness_score": business_readiness,
                "skill_development_timeline": "Based on gaps analysis",
                "strength_areas": technical_skills_result.get("technical_depth", {}).get("evidence", [])[:3],
                "critical_gaps": technical_skills_result.get("required_skills_coverage", {}).get("missing_critical", []),
                "training_investment_needed": technical_skills_result.get("technical_depth", {}).get("gaps", []),
                "immediate_value_skills": technical_skills_result.get("business_readiness", {}).get("breakdown", "").split(",")[:3] if isinstance(technical_skills_result.get("business_readiness", {}).get("breakdown", ""), str) else [],
                "risky_transition_skills": []
            },
            
            # Experience analyzer structure
            "experience": {
                "experience_analysis": {
                    "cv_experience_years": str(experience_fit_result.get("experience_alignment", {}).get("cv_corporate_years", 0) + 
                                               experience_fit_result.get("experience_alignment", {}).get("cv_academic_years", 0)),
                    "cv_corporate_years": str(experience_fit_result.get("experience_alignment", {}).get("cv_corporate_years", 0)),
                    "cv_academic_years": str(experience_fit_result.get("experience_alignment", {}).get("cv_academic_years", 0)),
                    "cv_role_level": experience_fit_result.get("seniority_match", {}).get("cv_level", "Unknown"),
                    "cv_progression": [],
                    "jd_required_years": str(experience_fit_result.get("experience_alignment", {}).get("jd_required_years", 0)),
                    "jd_role_level": experience_fit_result.get("seniority_match", {}).get("jd_level", "Unknown"),
                    "alignment_score": exp_alignment,
                    "experience_gaps": experience_fit_result.get("leadership_readiness", {}).get("gaps", []),
                    "experience_strengths": experience_fit_result.get("seniority_match", {}).get("evidence", []),
                    "quantified_achievements": [],
                    "overqualification_risk": "LOW" if exp_alignment > 70 else "MEDIUM" if exp_alignment > 50 else "HIGH"
                }
            },
            
            # Industry analyzer structure
            "industry": {
                "industry_analysis": {
                    "cv_primary_industry": experience_fit_result.get("industry_transition_fit", {}).get("cv_industry", "Unknown"),
                    "cv_secondary_industries": [],
                    "cv_academic_background": "N/A - unified analysis",
                    "cv_corporate_exposure": str(experience_fit_result.get("experience_alignment", {}).get("cv_corporate_years", 0)),
                    "jd_target_industry": experience_fit_result.get("industry_transition_fit", {}).get("jd_industry", "Unknown"),
                    "jd_industry_specificity": "Medium",
                    "direct_industry_match": "YES" if industry_fit > 80 else "PARTIAL" if industry_fit > 60 else "NO",
                    "industry_alignment_score": industry_fit,
                    "corporate_background_bonus": "N/A",
                    "industry_penalty_factors": [],
                    "transferable_skills_score": industry_fit,
                    "cultural_adaptation_difficulty": experience_fit_result.get("industry_transition_fit", {}).get("risk_level", "MEDIUM RISK"),
                    "regulatory_knowledge_gap": "Unknown",
                    "client_stakeholder_fit": "Good" if leadership > 70 else "Moderate",
                    "business_cycle_understanding": "Good",
                    "success_probability": experience_fit_result.get("industry_transition_fit", {}).get("risk_level", "MEDIUM RISK"),
                    "adaptation_timeline": "3-6 months" if industry_fit > 70 else "6-12 months" if industry_fit > 50 else "12+ months",
                    "investment_level_required": "LOW" if industry_fit > 80 else "MEDIUM" if industry_fit > 60 else "HIGH",
                    "industry_strengths": [],
                    "critical_industry_gaps": [],
                    "hiring_risk_assessment": experience_fit_result.get("industry_transition_fit", {}).get("risk_level", "MEDIUM RISK"),
                    # Additional scores for score calculator
                    "domain_overlap_percentage": industry_fit,  # Use industry_fit as proxy
                    "data_familiarity_score": 70.0,  # Default value, could be enhanced
                    "stakeholder_fit_score": leadership,  # Use leadership as proxy
                    "business_cycle_alignment": 70.0  # Default value
                }
            },
            
            # Seniority analyzer structure
            "seniority": {
                "seniority_analysis": {
                    "cv_corporate_years": str(experience_fit_result.get("experience_alignment", {}).get("cv_corporate_years", 0)),
                    "cv_academic_years": str(experience_fit_result.get("experience_alignment", {}).get("cv_academic_years", 0)),
                    "cv_total_weighted_years": str(experience_fit_result.get("experience_alignment", {}).get("cv_corporate_years", 0) * 0.8 + 
                                                   experience_fit_result.get("experience_alignment", {}).get("cv_academic_years", 0) * 0.2),
                    "cv_responsibility_scope": experience_fit_result.get("seniority_match", {}).get("cv_level", "Unknown"),
                    "cv_leadership_indicators": str(leadership // 10),  # Convert to 1-10 scale
                    "cv_decision_authority": experience_fit_result.get("seniority_match", {}).get("cv_level", "Unknown"),
                    "cv_stakeholder_level": experience_fit_result.get("seniority_match", {}).get("cv_level", "Unknown"),
                    "cv_management_experience": "Yes" if leadership > 60 else "No",
                    "jd_required_seniority": experience_fit_result.get("seniority_match", {}).get("jd_level", "Unknown"),
                    "jd_leadership_requirements": "Yes" if leadership > 60 else "No",
                    "jd_decision_authority_needed": experience_fit_result.get("seniority_match", {}).get("jd_level", "Unknown"),
                    "jd_stakeholder_level": experience_fit_result.get("seniority_match", {}).get("jd_level", "Unknown"),
                    "seniority_score": seniority_match,
                    "corporate_seniority_match": seniority_match,
                    "leadership_readiness_score": leadership,
                    "decision_authority_match": seniority_match,
                    "stakeholder_management_fit": leadership,
                    "overqualification_risk": "LOW" if seniority_match > 70 else "MEDIUM" if seniority_match > 50 else "HIGH",
                    "seniority_strengths": experience_fit_result.get("seniority_match", {}).get("evidence", []),
                    "seniority_gaps": experience_fit_result.get("leadership_readiness", {}).get("gaps", []),
                    "leadership_transition_risk": "LOW" if leadership > 70 else "MEDIUM" if leadership > 50 else "HIGH",
                    "readiness_assessment": "Ready" if seniority_match > 70 else "Needs development",
                    # Additional scores for score calculator
                    "experience_match_percentage": exp_alignment,
                    "responsibility_fit_percentage": seniority_match,
                    "growth_trajectory_score": learning  # Use learning_adaptation as proxy
                }
            },
            
            # Technical analyzer structure
            "technical": {
                "technical_analysis": {
                    "cv_sophistication_level": "Advanced" if tech_depth > 80 else "Strong" if tech_depth > 65 else "Solid" if tech_depth > 50 else "Basic",
                    "cv_primary_domain": "Technology",
                    "cv_core_competencies": technical_skills_result.get("required_skills_coverage", {}).get("missing_critical", []),
                    "cv_problem_complexity": int(complexity // 10),  # Convert to 0-10 scale
                    "cv_innovation_indicators": technical_skills_result.get("learning_adaptation", {}).get("evidence", [])[:2],
                    "jd_required_sophistication": "Advanced" if jd_complexity > 7 else "Intermediate" if jd_complexity > 5 else "Basic",
                    "jd_core_tech_stack": [],
                    "jd_problem_complexity": int(jd_complexity),
                    "jd_innovation_requirements": False,
                    "technical_depth_score": tech_depth,
                    "core_skills_match_percentage": skills_coverage,
                    "technical_stack_fit_percentage": tech_stack,
                    "complexity_readiness_score": complexity,
                    "learning_agility_score": learning,
                    "technical_strengths": technical_skills_result.get("technical_depth", {}).get("evidence", []),
                    "technical_gaps": technical_skills_result.get("technical_depth", {}).get("gaps", []),
                    "overqualification_risk": "LOW" if tech_depth > 80 else "MEDIUM" if tech_depth > 60 else "HIGH"
                }
            }
        }
        
        logger.info("[MAPPER] Legacy structure mapping completed")
        return legacy_structure

    @staticmethod
    def extract_scores_for_calculator(
        technical_skills_result: Dict[str, Any],
        experience_fit_result: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Extract scores in the format expected by ATS score calculator.
        
        Args:
            technical_skills_result: Result from TechnicalSkillsAnalyzer
            experience_fit_result: Result from ExperienceFitAnalyzer
            
        Returns:
            Dict with score keys expected by calculator
        """
        logger.info("[MAPPER] Extracting scores for calculator")
        
        # Extract from technical_skills_result
        tech_depth = float(technical_skills_result.get("technical_depth", {}).get("score", 50))
        skills_coverage = float(technical_skills_result.get("required_skills_coverage", {}).get("score", 50))
        tech_stack = float(technical_skills_result.get("tech_stack_similarity", {}).get("score", 50))
        business_readiness = float(technical_skills_result.get("business_readiness", {}).get("score", 50))
        complexity = float(technical_skills_result.get("complexity_handling", {}).get("score", 50))
        learning = float(technical_skills_result.get("learning_adaptation", {}).get("score", 50))
        jd_complexity = float(technical_skills_result.get("complexity_handling", {}).get("jd_complexity_level", 5))
        
        # Extract from experience_fit_result
        exp_alignment = float(experience_fit_result.get("experience_alignment", {}).get("score", 50))
        role_similarity = float(experience_fit_result.get("role_similarity", {}).get("score", 50))
        seniority_match = float(experience_fit_result.get("seniority_match", {}).get("score", 50))
        leadership = float(experience_fit_result.get("leadership_readiness", {}).get("score", 50))
        industry_fit = float(experience_fit_result.get("industry_transition_fit", {}).get("score", 50))
        
        # Map to calculator expected format
        extracted_scores = {
            # Technical & Skills (for Category 2 - Core Competency)
            "technical_depth": tech_depth,
            "core_skills_match_percentage": skills_coverage,
            "technical_stack_fit_percentage": tech_stack,
            "data_familiarity_score": 70.0,  # Default, could be enhanced
            
            # Experience & Seniority (for Category 2 - Experience & Seniority)
            "experience_alignment": exp_alignment,
            "experience_match_percentage": exp_alignment,  # Use alignment as proxy
            "responsibility_fit_percentage": seniority_match,
            "role_seniority": seniority_match,
            "leadership_readiness_score": leadership,
            
            # Potential & Ability (for Category 2 - Potential & Ability)
            "growth_trajectory_score": learning,  # Use learning_adaptation
            "complexity_readiness_score": complexity,
            "learning_agility_score": learning,
            "jd_problem_complexity": jd_complexity * 10,  # Convert 0-10 to 0-100 scale
            
            # Company Fit (for Category 2 - Company Fit)
            "industry_fit": industry_fit,
            "domain_overlap_percentage": industry_fit,  # Use industry_fit as proxy
            "stakeholder_fit_score": leadership,  # Use leadership as proxy
            "business_cycle_alignment": business_readiness,  # Use business_readiness as proxy
            
            # Bonus (will be added separately)
            "requirement_bonus": 0.0
        }
        
        logger.info("[MAPPER] Score extraction completed")
        return extracted_scores

