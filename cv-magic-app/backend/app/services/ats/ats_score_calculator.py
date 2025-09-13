"""
ATS Score Calculator

Implements the structured ATS scoring framework with 100-point allocation:
- Category 1: Direct Match Rates (40 points)
- Category 2: Component Analysis (60 points)
- Category 3: Bonus Points (with 100-point ceiling)
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ATSScoreBreakdown:
    """Structured breakdown of ATS score components"""
    
    # Category 1: Direct Match Rates (40 points)
    technical_skills_match_rate: float
    domain_keywords_match_rate: float
    soft_skills_match_rate: float
    cat1_score: float
    
    # Category 2: Component Analysis (60 points)
    core_competency_avg: float
    experience_seniority_avg: float
    potential_ability_avg: float
    company_fit_avg: float
    cat2_score: float
    
    # Final Scoring
    ats1_score: float  # Pre-bonus
    bonus_points: float
    final_ats_score: float
    
    # Status indicators
    category_status: str
    recommendation: str
    
    # Missing items counts
    technical_missing_count: int
    soft_missing_count: int
    domain_missing_count: int


class ATSScoreCalculator:
    """
    Modular ATS Score Calculator implementing the 100-point framework
    """
    
    def __init__(self):
        self.score_categories = {
            90: {"status": "✅ Excellent fit", "recommendation": "Strong candidate"},
            75: {"status": "✅ Good fit", "recommendation": "Worth an interview"},
            60: {"status": "⚠️ Moderate fit", "recommendation": "Consider if other factors are strong"},
            0: {"status": "❌ Poor fit", "recommendation": "Generally rejected"}
        }
    
    def _get_category_status(self, score: float) -> Tuple[str, str]:
        """Get status and recommendation based on score"""
        for threshold in sorted(self.score_categories.keys(), reverse=True):
            if score >= threshold:
                return (
                    self.score_categories[threshold]["status"],
                    self.score_categories[threshold]["recommendation"]
                )
        return self.score_categories[0]["status"], self.score_categories[0]["recommendation"]
    
    def _calculate_match_rates(self, preextracted_data: Dict[str, Any]) -> Tuple[float, float, float, int, int, int]:
        """
        Calculate match rates from preextracted comparison data
        
        Returns:
            Tuple of (tech_rate, domain_rate, soft_rate, tech_missing, soft_missing, domain_missing)
        """
        try:
            # Parse the comparison content to extract match data
            content = preextracted_data.get("content", "")
            
            # Initialize default values
            tech_rate = domain_rate = soft_rate = 0.0
            tech_missing = soft_missing = domain_missing = 0
            
            # Extract data from the structured content
            lines = content.split('\n')
            for line in lines:
                if "Technical Skills" in line and "Match Rate" in line:
                    # Extract match rate percentage
                    import re
                    match = re.search(r'(\d+)', line)
                    if match:
                        tech_rate = float(match.group(1))
                
                elif "Soft Skills" in line and "Match Rate" in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        soft_rate = float(match.group(1))
                
                elif "Domain Keywords" in line and "Match Rate" in line:
                    match = re.search(r'(\d+)', line)
                    if match:
                        domain_rate = float(match.group(1))
                
                elif "MISSING FROM CV" in line and "Technical" in line:
                    match = re.search(r'(\d+) items', line)
                    if match:
                        tech_missing = int(match.group(1))
                
                elif "MISSING FROM CV" in line and "Soft" in line:
                    match = re.search(r'(\d+) items', line)
                    if match:
                        soft_missing = int(match.group(1))
                
                elif "MISSING FROM CV" in line and "Domain" in line:
                    match = re.search(r'(\d+) items', line)
                    if match:
                        domain_missing = int(match.group(1))
            
            logger.info(f"[ATS] Match rates - Tech: {tech_rate}%, Domain: {domain_rate}%, Soft: {soft_rate}%")
            return tech_rate, domain_rate, soft_rate, tech_missing, soft_missing, domain_missing
            
        except Exception as e:
            logger.error(f"[ATS] Error calculating match rates: {e}")
            return 0.0, 0.0, 0.0, 0, 0, 0
    
    def _normalize_complexity_score(self, complexity: float) -> float:
        """Normalize jd_problem_complexity to 0-100 scale"""
        if complexity <= 0:
            return 0.0
        # Assuming complexity is on 0-10 scale, normalize to 0-100
        return min(100.0, (complexity / 10.0) * 100.0)
    
    def _calculate_category1(self, tech_rate: float, domain_rate: float, soft_rate: float) -> Tuple[float, Dict[str, float]]:
        """
        Calculate Category 1: Direct Match Rates (40 points total)
        
        Returns:
            Tuple of (total_score, breakdown_dict)
        """
        tech_points = (tech_rate / 100.0) * 20  # 20 points max
        domain_points = (domain_rate / 100.0) * 5  # 5 points max
        soft_points = (soft_rate / 100.0) * 15  # 15 points max
        
        total = tech_points + domain_points + soft_points
        
        breakdown = {
            "technical_points": tech_points,
            "domain_points": domain_points,
            "soft_points": soft_points,
            "total": total
        }
        
        logger.info(f"[ATS] Category 1 - Tech: {tech_points:.1f}, Domain: {domain_points:.1f}, Soft: {soft_points:.1f}, Total: {total:.1f}")
        return total, breakdown
    
    def _calculate_category2(self, extracted_scores: Dict[str, float]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate Category 2: Component Analysis (60 points total)
        
        Returns:
            Tuple of (total_score, breakdown_dict)
        """
        # Core Competency (25 points) - Average of 4 metrics
        core_metrics = [
            extracted_scores.get("technical_depth", 0),
            extracted_scores.get("core_skills_match_percentage", 0),
            extracted_scores.get("technical_stack_fit_percentage", 0),
            extracted_scores.get("data_familiarity_score", 0)
        ]
        core_avg = sum(core_metrics) / len(core_metrics) if core_metrics else 0
        core_points = (core_avg / 100.0) * 25
        
        # Experience & Seniority (20 points) - Average of 5 metrics
        exp_metrics = [
            extracted_scores.get("experience_alignment", 0),
            extracted_scores.get("experience_match_percentage", 0),
            extracted_scores.get("responsibility_fit_percentage", 0),
            extracted_scores.get("role_seniority", 0),
            extracted_scores.get("leadership_readiness_score", 0)
        ]
        exp_avg = sum(exp_metrics) / len(exp_metrics) if exp_metrics else 0
        exp_points = (exp_avg / 100.0) * 20
        
        # Potential & Ability (10 points) - Average of 4 metrics
        complexity_normalized = self._normalize_complexity_score(extracted_scores.get("jd_problem_complexity", 0))
        potential_metrics = [
            extracted_scores.get("growth_trajectory_score", 0),
            extracted_scores.get("complexity_readiness_score", 0),
            extracted_scores.get("learning_agility_score", 0),
            complexity_normalized
        ]
        potential_avg = sum(potential_metrics) / len(potential_metrics) if potential_metrics else 0
        potential_points = (potential_avg / 100.0) * 10
        
        # Company Fit (5 points) - Average of 4 metrics
        company_metrics = [
            extracted_scores.get("industry_fit", 0),
            extracted_scores.get("domain_overlap_percentage", 0),
            extracted_scores.get("stakeholder_fit_score", 0),
            extracted_scores.get("business_cycle_alignment", 0)
        ]
        company_avg = sum(company_metrics) / len(company_metrics) if company_metrics else 0
        company_points = (company_avg / 100.0) * 5
        
        total = core_points + exp_points + potential_points + company_points
        
        breakdown = {
            "core_competency": {
                "average": core_avg,
                "points": core_points,
                "metrics": core_metrics
            },
            "experience_seniority": {
                "average": exp_avg,
                "points": exp_points,
                "metrics": exp_metrics
            },
            "potential_ability": {
                "average": potential_avg,
                "points": potential_points,
                "metrics": potential_metrics
            },
            "company_fit": {
                "average": company_avg,
                "points": company_points,
                "metrics": company_metrics
            },
            "total": total
        }
        
        logger.info(f"[ATS] Category 2 - Core: {core_points:.1f}, Exp: {exp_points:.1f}, Potential: {potential_points:.1f}, Company: {company_points:.1f}, Total: {total:.1f}")
        return total, breakdown
    
    def calculate_ats_score(
        self, 
        preextracted_data: Dict[str, Any],
        component_analysis: Dict[str, Any],
        extracted_scores: Dict[str, float]
    ) -> ATSScoreBreakdown:
        """
        Calculate comprehensive ATS score using the structured framework
        
        Args:
            preextracted_data: Data from preextracted comparison
            component_analysis: Component analysis results
            extracted_scores: Extracted numerical scores
            
        Returns:
            ATSScoreBreakdown with complete analysis
        """
        logger.info("[ATS] Starting comprehensive ATS score calculation")
        
        try:
            # Extract match rates and missing counts
            tech_rate, domain_rate, soft_rate, tech_missing, soft_missing, domain_missing = self._calculate_match_rates(preextracted_data)
            
            # Calculate Category 1: Direct Match Rates (40 points)
            cat1_score, cat1_breakdown = self._calculate_category1(tech_rate, domain_rate, soft_rate)
            
            # Calculate Category 2: Component Analysis (60 points)
            cat2_score, cat2_breakdown = self._calculate_category2(extracted_scores)
            
            # Calculate ATS1 (pre-bonus)
            ats1_score = cat1_score + cat2_score
            
            # Get bonus points
            bonus_points = extracted_scores.get("requirement_bonus", 0)
            
            # Calculate final ATS score with ceiling
            final_ats_score = min(100.0, ats1_score + bonus_points)
            
            # Get category status and recommendation
            category_status, recommendation = self._get_category_status(final_ats_score)
            
            # Create breakdown object
            breakdown = ATSScoreBreakdown(
                technical_skills_match_rate=tech_rate,
                domain_keywords_match_rate=domain_rate,
                soft_skills_match_rate=soft_rate,
                cat1_score=cat1_score,
                
                core_competency_avg=cat2_breakdown["core_competency"]["average"],
                experience_seniority_avg=cat2_breakdown["experience_seniority"]["average"],
                potential_ability_avg=cat2_breakdown["potential_ability"]["average"],
                company_fit_avg=cat2_breakdown["company_fit"]["average"],
                cat2_score=cat2_score,
                
                ats1_score=ats1_score,
                bonus_points=bonus_points,
                final_ats_score=final_ats_score,
                
                category_status=category_status,
                recommendation=recommendation,
                
                technical_missing_count=tech_missing,
                soft_missing_count=soft_missing,
                domain_missing_count=domain_missing
            )
            
            logger.info(f"[ATS] Final ATS Score: {final_ats_score:.1f}/100 ({category_status})")
            return breakdown
            
        except Exception as e:
            logger.error(f"[ATS] Error calculating ATS score: {e}")
            # Return default breakdown on error
            return ATSScoreBreakdown(
                technical_skills_match_rate=0, domain_keywords_match_rate=0, soft_skills_match_rate=0, cat1_score=0,
                core_competency_avg=0, experience_seniority_avg=0, potential_ability_avg=0, company_fit_avg=0, cat2_score=0,
                ats1_score=0, bonus_points=0, final_ats_score=0,
                category_status="❌ Poor fit", recommendation="Error in calculation",
                technical_missing_count=0, soft_missing_count=0, domain_missing_count=0
            )
