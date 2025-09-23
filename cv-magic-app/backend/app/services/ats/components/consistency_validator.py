"""
Consistency Validator for ATS Component Analysis

Validates consistency across different analyzers to ensure they interpret the same CV content consistently.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class ConsistencyValidator:
    """Validates consistency across component analysis results."""
    
    def __init__(self):
        self.tolerance_thresholds = {
            "experience_years": 2,  # Allow 2 years difference
            "seniority_score": 20,  # Allow 20 point difference
            "skills_score": 15,     # Allow 15 point difference
            "industry_score": 20,   # Allow 20 point difference
            "technical_score": 15   # Allow 15 point difference
        }
    
    def validate_cross_analyzer_consistency(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate consistency across different analyzers.
        
        Args:
            results: Dictionary containing all analysis results
            
        Returns:
            Dict containing validation results and recommendations
        """
        validation_results = {
            "is_consistent": True,
            "inconsistencies": [],
            "recommendations": [],
            "confidence_score": 100
        }
        
        try:
            # Extract scores from different analyzers
            experience_data = results.get("experience", {}).get("experience_analysis", {})
            seniority_data = results.get("seniority", {}).get("seniority_analysis", {})
            skills_data = results.get("skills", {})
            industry_data = results.get("industry", {}).get("industry_analysis", {})
            technical_data = results.get("technical", {}).get("technical_analysis", {})
            
            # Check experience years consistency
            exp_years = experience_data.get("cv_experience_years", 0)
            seniority_years = seniority_data.get("cv_experience_years", 0)
            
            if abs(exp_years - seniority_years) > self.tolerance_thresholds["experience_years"]:
                validation_results["is_consistent"] = False
                validation_results["inconsistencies"].append({
                    "type": "experience_years_mismatch",
                    "experience_analyzer": exp_years,
                    "seniority_analyzer": seniority_years,
                    "difference": abs(exp_years - seniority_years),
                    "threshold": self.tolerance_thresholds["experience_years"]
                })
                validation_results["recommendations"].append(
                    f"Experience years mismatch: {exp_years} vs {seniority_years}. "
                    "Review CV interpretation guidelines for academic experience."
                )
            
            # Check role level consistency
            exp_level = experience_data.get("cv_role_level", "")
            seniority_scope = seniority_data.get("cv_responsibility_scope", "")
            
            if self._is_role_level_inconsistent(exp_level, seniority_scope):
                validation_results["is_consistent"] = False
                validation_results["inconsistencies"].append({
                    "type": "role_level_mismatch",
                    "experience_level": exp_level,
                    "seniority_scope": seniority_scope
                })
                validation_results["recommendations"].append(
                    f"Role level mismatch: {exp_level} vs {seniority_scope}. "
                    "Ensure consistent interpretation of academic roles."
                )
            
            # Check score consistency
            scores = {
                "experience": experience_data.get("alignment_score", 0),
                "seniority": seniority_data.get("seniority_score", 0),
                "skills": skills_data.get("overall_skills_score", 0),
                "industry": industry_data.get("industry_alignment_score", 0),
                "technical": technical_data.get("technical_depth_score", 0)
            }
            
            # Calculate overall consistency score
            consistency_score = self._calculate_consistency_score(scores)
            validation_results["confidence_score"] = consistency_score
            
            if consistency_score < 70:
                validation_results["is_consistent"] = False
                validation_results["recommendations"].append(
                    f"Low consistency score: {consistency_score}%. "
                    "Review AI parameters and prompt templates for better alignment."
                )
            
            logger.info(f"[CONSISTENCY] Validation completed. Consistent: {validation_results['is_consistent']}, "
                       f"Confidence: {consistency_score}%")
            
        except Exception as e:
            logger.error(f"[CONSISTENCY] Validation failed: {str(e)}")
            validation_results["is_consistent"] = False
            validation_results["inconsistencies"].append({
                "type": "validation_error",
                "error": str(e)
            })
        
        return validation_results
    
    def _is_role_level_inconsistent(self, exp_level: str, seniority_scope: str) -> bool:
        """Check if role levels are inconsistent."""
        # Define level mappings
        level_mappings = {
            "Entry-Level": ["Entry-Level", "Junior"],
            "Mid-Level": ["Mid-Level", "Mid-Senior", "Senior Individual Contributor"],
            "Senior": ["Senior", "Senior Individual Contributor", "Lead"],
            "Executive": ["Executive", "Director", "VP"]
        }
        
        # Check if levels are compatible
        for level, scopes in level_mappings.items():
            if exp_level in scopes and seniority_scope in scopes:
                return False
        
        return True
    
    def _calculate_consistency_score(self, scores: Dict[str, float]) -> float:
        """Calculate overall consistency score based on score variance."""
        if not scores:
            return 0
        
        # Calculate variance in scores
        score_values = list(scores.values())
        mean_score = sum(score_values) / len(score_values)
        variance = sum((score - mean_score) ** 2 for score in score_values) / len(score_values)
        
        # Convert variance to consistency score (lower variance = higher consistency)
        max_variance = 2500  # Maximum possible variance (100^2)
        consistency = max(0, 100 - (variance / max_variance) * 100)
        
        return round(consistency, 1)
    
    def get_consistency_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable consistency report."""
        report = ["=== ATS Analysis Consistency Report ===\n"]
        
        if validation_results["is_consistent"]:
            report.append("✅ Analysis results are consistent across all components.")
        else:
            report.append("❌ Analysis results show inconsistencies that need attention.")
        
        report.append(f"Confidence Score: {validation_results['confidence_score']}%\n")
        
        if validation_results["inconsistencies"]:
            report.append("🚨 Inconsistencies Found:")
            for i, inconsistency in enumerate(validation_results["inconsistencies"], 1):
                report.append(f"{i}. {inconsistency['type']}: {inconsistency}")
        
        if validation_results["recommendations"]:
            report.append("\n💡 Recommendations:")
            for i, recommendation in enumerate(validation_results["recommendations"], 1):
                report.append(f"{i}. {recommendation}")
        
        return "\n".join(report)
