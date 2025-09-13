"""
Industry Alignment Scorer

Addresses the industry fit overestimation issue by implementing:
1. Realistic industry transition difficulty matrices
2. Domain expertise overlap calculation  
3. Contextual skill transferability assessment
4. Experience relevance weighting
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class IndustryAlignment:
    """Industry alignment assessment results"""
    source_industry: str
    target_industry: str
    transition_difficulty: float  # 0.0 (impossible) to 1.0 (seamless)
    domain_overlap_score: float  # 0-100
    skill_transferability_score: float  # 0-100
    experience_relevance_score: float  # 0-100
    overall_fit_score: float  # 0-100
    transition_category: str  # "Natural", "Moderate", "Difficult", "High-risk"
    key_gaps: List[str]
    transferable_advantages: List[str]


class IndustryAlignmentScorer:
    """
    Realistic industry alignment scoring system
    """
    
    def __init__(self):
        self._initialize_industry_clusters()
        self._initialize_transition_matrices()
        self._initialize_skill_transferability_maps()
    
    def _initialize_industry_clusters(self):
        """Define industry clusters and their characteristics"""
        
        self.industry_clusters = {
            "technology": {
                "domains": ["software", "tech", "saas", "cloud", "ai", "data", "cybersecurity", "fintech"],
                "core_skills": ["programming", "system design", "agile", "problem solving", "innovation"],
                "culture": ["fast-paced", "innovation-focused", "data-driven", "collaborative"]
            },
            "finance": {
                "domains": ["banking", "investment", "insurance", "accounting", "financial services"],
                "core_skills": ["financial analysis", "risk management", "compliance", "attention to detail"],
                "culture": ["regulated", "conservative", "precision-focused", "hierarchy"]
            },
            "consulting": {
                "domains": ["management consulting", "strategy", "advisory", "professional services"],
                "core_skills": ["analytical thinking", "communication", "problem solving", "client management"],
                "culture": ["client-focused", "results-driven", "travel-heavy", "deadline-oriented"]
            },
            "healthcare": {
                "domains": ["medical", "pharmaceutical", "biotech", "health services"],
                "core_skills": ["scientific knowledge", "compliance", "patient care", "precision"],
                "culture": ["regulated", "mission-driven", "evidence-based", "collaborative"]
            },
            "nonprofit": {
                "domains": ["charity", "ngo", "social impact", "fundraising", "humanitarian"],
                "core_skills": ["mission alignment", "stakeholder management", "resource optimization"],
                "culture": ["mission-driven", "resource-conscious", "impact-focused", "collaborative"]
            },
            "government": {
                "domains": ["public sector", "policy", "defense", "civil service"],
                "core_skills": ["policy knowledge", "compliance", "stakeholder management", "process adherence"],
                "culture": ["regulated", "hierarchical", "process-focused", "stability-oriented"]
            },
            "education": {
                "domains": ["academic", "university", "k-12", "training", "research"],
                "core_skills": ["knowledge transfer", "research", "communication", "curriculum design"],
                "culture": ["knowledge-focused", "collaborative", "long-term thinking", "mission-driven"]
            },
            "retail_consumer": {
                "domains": ["retail", "consumer goods", "e-commerce", "marketing", "brand management"],
                "core_skills": ["customer focus", "marketing", "operations", "brand management"],
                "culture": ["customer-centric", "fast-paced", "competitive", "results-driven"]
            }
        }
    
    def _initialize_transition_matrices(self):
        """Define realistic transition difficulty between industries"""
        
        # Transition difficulty matrix (0.0 = impossible, 1.0 = seamless)
        # Based on common career transition patterns and success rates
        self.transition_matrix = {
            "technology": {
                "technology": 1.0,
                "consulting": 0.8,  # Tech → Consulting (common, valued background)
                "finance": 0.7,     # Tech → Finance (fintech growth, quant roles)
                "healthcare": 0.6,  # Tech → Healthcare (health tech, but domain gap)
                "nonprofit": 0.5,   # Tech → Nonprofit (skill mismatch, culture gap)
                "government": 0.4,  # Tech → Government (bureaucracy, pace mismatch)
                "education": 0.6,   # Tech → Education (training roles, but pace difference)
                "retail_consumer": 0.7  # Tech → Retail (e-commerce, digital transformation)
            },
            "finance": {
                "technology": 0.6,  # Finance → Tech (analytical skills transfer, but culture gap)
                "consulting": 0.9,  # Finance → Consulting (very common transition)
                "finance": 1.0,
                "healthcare": 0.4,  # Finance → Healthcare (limited transferability)
                "nonprofit": 0.3,   # Finance → Nonprofit (major culture/mission shift)
                "government": 0.7,  # Finance → Government (regulatory knowledge valuable)
                "education": 0.3,   # Finance → Education (culture and skill mismatch)
                "retail_consumer": 0.6  # Finance → Retail (business skills transfer)
            },
            "consulting": {
                "technology": 0.7,  # Consulting → Tech (problem-solving skills valued)
                "consulting": 1.0,
                "finance": 0.8,     # Consulting → Finance (analytical skills transfer well)
                "healthcare": 0.6,  # Consulting → Healthcare (process skills transfer)
                "nonprofit": 0.6,   # Consulting → Nonprofit (strategy skills valuable)
                "government": 0.7,  # Consulting → Government (policy consulting background)
                "education": 0.5,   # Consulting → Education (different pace and culture)
                "retail_consumer": 0.8  # Consulting → Retail (business strategy skills)
            },
            "healthcare": {
                "technology": 0.4,  # Healthcare → Tech (domain shift, but analytical skills)
                "consulting": 0.5,  # Healthcare → Consulting (process knowledge, limited business)
                "finance": 0.3,     # Healthcare → Finance (limited financial background)
                "healthcare": 1.0,
                "nonprofit": 0.7,   # Healthcare → Nonprofit (mission alignment, service focus)
                "government": 0.6,  # Healthcare → Government (regulatory knowledge)
                "education": 0.8,   # Healthcare → Education (knowledge transfer, research)
                "retail_consumer": 0.3  # Healthcare → Retail (significant domain gap)
            },
            "nonprofit": {
                "technology": 0.3,  # Nonprofit → Tech (mission/culture gap, limited tech skills)
                "consulting": 0.5,  # Nonprofit → Consulting (limited business background)
                "finance": 0.2,     # Nonprofit → Finance (major skill and culture gap)
                "healthcare": 0.6,  # Nonprofit → Healthcare (mission alignment)
                "nonprofit": 1.0,
                "government": 0.8,  # Nonprofit → Government (policy focus, public service)
                "education": 0.7,   # Nonprofit → Education (mission alignment, service focus)
                "retail_consumer": 0.3  # Nonprofit → Retail (limited commercial experience)
            },
            "government": {
                "technology": 0.3,  # Government → Tech (pace and culture mismatch)
                "consulting": 0.6,  # Government → Consulting (policy expertise valuable)
                "finance": 0.5,     # Government → Finance (regulatory knowledge)
                "healthcare": 0.5,  # Government → Healthcare (regulatory overlap)
                "nonprofit": 0.8,   # Government → Nonprofit (public service alignment)
                "government": 1.0,
                "education": 0.7,   # Government → Education (public service, knowledge focus)
                "retail_consumer": 0.3  # Government → Retail (limited commercial experience)
            },
            "education": {
                "technology": 0.4,  # Education → Tech (analytical skills, but pace gap)
                "consulting": 0.5,  # Education → Consulting (research skills, limited business)
                "finance": 0.3,     # Education → Finance (limited financial experience)
                "healthcare": 0.6,  # Education → Healthcare (research, knowledge focus)
                "nonprofit": 0.8,   # Education → Nonprofit (mission alignment)
                "government": 0.6,  # Education → Government (public service, research)
                "education": 1.0,
                "retail_consumer": 0.4  # Education → Retail (limited commercial experience)
            },
            "retail_consumer": {
                "technology": 0.5,  # Retail → Tech (customer focus, but tech skill gap)
                "consulting": 0.6,  # Retail → Consulting (business operations knowledge)
                "finance": 0.5,     # Retail → Finance (business acumen, limited finance depth)
                "healthcare": 0.3,  # Retail → Healthcare (domain gap)
                "nonprofit": 0.4,   # Retail → Nonprofit (service experience, but profit focus)
                "government": 0.3,  # Retail → Government (culture and pace mismatch)
                "education": 0.4,   # Retail → Education (customer service, but domain gap)
                "retail_consumer": 1.0
            }
        }
    
    def _initialize_skill_transferability_maps(self):
        """Define which skills transfer well between industries"""
        
        self.skill_transferability = {
            # High transferability skills (work in most industries)
            "high_transfer": [
                "leadership", "management", "communication", "problem solving",
                "analytical thinking", "project management", "teamwork", "adaptability",
                "strategic thinking", "decision making", "negotiation", "presentation"
            ],
            
            # Medium transferability skills (work in related industries)
            "medium_transfer": [
                "data analysis", "research", "process improvement", "quality assurance",
                "stakeholder management", "budget management", "compliance", "training"
            ],
            
            # Low transferability skills (industry-specific)
            "low_transfer": [
                "programming", "software development", "clinical knowledge", "regulatory expertise",
                "financial modeling", "accounting", "medical procedures", "legal knowledge"
            ]
        }
    
    def _classify_industry(self, job_description: str, company_info: str = "") -> str:
        """Classify industry based on job description and company info"""
        
        text = (job_description + " " + company_info).lower()
        
        # Score each industry cluster based on keyword matches
        industry_scores = {}
        for industry, cluster_info in self.industry_clusters.items():
            score = 0
            for domain in cluster_info["domains"]:
                if domain in text:
                    score += 2
            for skill in cluster_info["core_skills"]:
                if skill in text:
                    score += 1
            industry_scores[industry] = score
        
        # Return industry with highest score, default to 'technology' if unclear
        if not industry_scores or max(industry_scores.values()) == 0:
            return "technology"
        
        return max(industry_scores, key=industry_scores.get)
    
    def _calculate_domain_overlap(self, cv_experience: List[str], target_industry: str) -> float:
        """Calculate domain expertise overlap with target industry"""
        
        if target_industry not in self.industry_clusters:
            return 50.0  # Default moderate score
        
        target_domains = self.industry_clusters[target_industry]["domains"]
        target_skills = self.industry_clusters[target_industry]["core_skills"]
        
        cv_text = " ".join(cv_experience).lower()
        
        # Calculate domain overlap
        domain_matches = sum(1 for domain in target_domains if domain in cv_text)
        domain_score = (domain_matches / len(target_domains)) * 100
        
        # Calculate skill overlap
        skill_matches = sum(1 for skill in target_skills if skill in cv_text)
        skill_score = (skill_matches / len(target_skills)) * 100
        
        # Weighted average (domains more important)
        overlap_score = (domain_score * 0.6 + skill_score * 0.4)
        
        logger.info(f"[Industry] Domain overlap for {target_industry}: {overlap_score:.1f}% "
                   f"(domains: {domain_matches}/{len(target_domains)}, skills: {skill_matches}/{len(target_skills)})")
        
        return overlap_score
    
    def _calculate_skill_transferability(self, cv_skills: List[str], target_industry: str) -> float:
        """Calculate how well CV skills transfer to target industry"""
        
        if not cv_skills:
            return 0.0
        
        transferability_scores = []
        
        for skill in cv_skills:
            skill_lower = skill.lower()
            
            # Determine transferability level
            if any(skill_lower in ht_skill or ht_skill in skill_lower 
                  for ht_skill in self.skill_transferability["high_transfer"]):
                transferability_scores.append(100)
            elif any(skill_lower in mt_skill or mt_skill in skill_lower 
                    for mt_skill in self.skill_transferability["medium_transfer"]):
                transferability_scores.append(70)
            elif any(skill_lower in lt_skill or lt_skill in skill_lower 
                    for lt_skill in self.skill_transferability["low_transfer"]):
                transferability_scores.append(30)
            else:
                transferability_scores.append(50)  # Unknown skill, moderate score
        
        average_transferability = sum(transferability_scores) / len(transferability_scores)
        
        logger.info(f"[Industry] Skill transferability to {target_industry}: {average_transferability:.1f}%")
        return average_transferability
    
    def _calculate_experience_relevance(self, cv_experience: List[str], target_industry: str, years_experience: int) -> float:
        """Calculate relevance of experience to target industry"""
        
        if not cv_experience:
            return 0.0
        
        target_cluster = self.industry_clusters.get(target_industry, {})
        target_domains = target_cluster.get("domains", [])
        
        cv_text = " ".join(cv_experience).lower()
        
        # Calculate direct experience relevance
        relevant_experience_count = 0
        for domain in target_domains:
            if domain in cv_text:
                relevant_experience_count += 1
        
        direct_relevance = (relevant_experience_count / len(target_domains)) * 100 if target_domains else 0
        
        # Experience depth bonus (more years = higher confidence in assessment)
        experience_multiplier = min(1.2, 1.0 + (years_experience / 20))  # Max 20% bonus for 20+ years
        
        relevance_score = direct_relevance * experience_multiplier
        
        logger.info(f"[Industry] Experience relevance to {target_industry}: {relevance_score:.1f}% "
                   f"(direct: {direct_relevance:.1f}%, years: {years_experience})")
        
        return min(100.0, relevance_score)
    
    def _identify_transition_gaps(self, source_industry: str, target_industry: str) -> List[str]:
        """Identify key gaps in transitioning between industries"""
        
        gaps = []
        
        if source_industry not in self.industry_clusters or target_industry not in self.industry_clusters:
            return ["Industry classification unclear"]
        
        source_cluster = self.industry_clusters[source_industry]
        target_cluster = self.industry_clusters[target_industry]
        
        # Culture gaps
        source_culture = set(source_cluster["culture"])
        target_culture = set(target_cluster["culture"])
        culture_gaps = target_culture - source_culture
        
        if culture_gaps:
            gaps.append(f"Culture adaptation: {', '.join(culture_gaps)}")
        
        # Skill gaps
        source_skills = set(source_cluster["core_skills"])
        target_skills = set(target_cluster["core_skills"])
        skill_gaps = target_skills - source_skills
        
        if skill_gaps:
            gaps.append(f"Core skills: {', '.join(skill_gaps)}")
        
        # Domain gaps
        source_domains = set(source_cluster["domains"])
        target_domains = set(target_cluster["domains"])
        domain_gaps = target_domains - source_domains
        
        if len(domain_gaps) > len(target_domains) * 0.7:  # If >70% of domains are new
            gaps.append("Significant domain knowledge gap")
        
        return gaps[:3]  # Return top 3 gaps
    
    def _identify_transferable_advantages(self, source_industry: str, target_industry: str) -> List[str]:
        """Identify transferable advantages from source to target industry"""
        
        advantages = []
        
        if source_industry not in self.industry_clusters or target_industry not in self.industry_clusters:
            return []
        
        source_cluster = self.industry_clusters[source_industry]
        target_cluster = self.industry_clusters[target_industry]
        
        # Skill advantages
        source_skills = set(source_cluster["core_skills"])
        target_skills = set(target_cluster["core_skills"])
        skill_overlap = source_skills & target_skills
        
        if skill_overlap:
            advantages.append(f"Transferable skills: {', '.join(skill_overlap)}")
        
        # Culture advantages
        source_culture = set(source_cluster["culture"])
        target_culture = set(target_cluster["culture"])
        culture_overlap = source_culture & target_culture
        
        if culture_overlap:
            advantages.append(f"Cultural fit: {', '.join(culture_overlap)}")
        
        # Industry-specific advantages
        transition_advantages = {
            ("technology", "consulting"): "Technical expertise brings unique value to clients",
            ("finance", "consulting"): "Financial analysis and modeling expertise",
            ("consulting", "technology"): "Strategic thinking and client management skills",
            ("healthcare", "nonprofit"): "Mission-driven approach and service orientation",
            ("government", "nonprofit"): "Public service experience and stakeholder management"
        }
        
        if (source_industry, target_industry) in transition_advantages:
            advantages.append(transition_advantages[(source_industry, target_industry)])
        
        return advantages[:3]  # Return top 3 advantages
    
    def assess_industry_alignment(
        self,
        cv_experience: List[str],
        cv_skills: List[str], 
        jd_text: str,
        company_info: str = "",
        years_experience: int = 0,
        current_industry: str = ""
    ) -> IndustryAlignment:
        """
        Assess realistic industry alignment between CV and job
        
        Args:
            cv_experience: List of experience descriptions from CV
            cv_skills: List of skills from CV
            jd_text: Job description text
            company_info: Company information
            years_experience: Years of experience
            current_industry: Current/source industry (if known)
            
        Returns:
            IndustryAlignment assessment
        """
        logger.info("[Industry] Starting industry alignment assessment")
        
        try:
            # Classify target industry
            target_industry = self._classify_industry(jd_text, company_info)
            
            # Classify source industry if not provided
            if not current_industry:
                cv_text = " ".join(cv_experience + cv_skills)
                source_industry = self._classify_industry(cv_text)
            else:
                source_industry = current_industry
            
            # Get transition difficulty
            transition_difficulty = self.transition_matrix.get(source_industry, {}).get(target_industry, 0.3)
            
            # Calculate component scores
            domain_overlap = self._calculate_domain_overlap(cv_experience, target_industry)
            skill_transferability = self._calculate_skill_transferability(cv_skills, target_industry)
            experience_relevance = self._calculate_experience_relevance(cv_experience, target_industry, years_experience)
            
            # Calculate overall fit score (weighted combination)
            overall_fit = (
                transition_difficulty * 40 +  # Transition feasibility (40%)
                domain_overlap * 0.25 +       # Domain overlap (25%)
                skill_transferability * 0.20 + # Skill transferability (20%) 
                experience_relevance * 0.15    # Experience relevance (15%)
            )
            
            # Categorize transition
            if transition_difficulty >= 0.8:
                transition_category = "Natural"
            elif transition_difficulty >= 0.6:
                transition_category = "Moderate"
            elif transition_difficulty >= 0.4:
                transition_category = "Difficult"
            else:
                transition_category = "High-risk"
            
            # Identify gaps and advantages
            key_gaps = self._identify_transition_gaps(source_industry, target_industry)
            transferable_advantages = self._identify_transferable_advantages(source_industry, target_industry)
            
            alignment = IndustryAlignment(
                source_industry=source_industry,
                target_industry=target_industry,
                transition_difficulty=transition_difficulty,
                domain_overlap_score=domain_overlap,
                skill_transferability_score=skill_transferability,
                experience_relevance_score=experience_relevance,
                overall_fit_score=overall_fit,
                transition_category=transition_category,
                key_gaps=key_gaps,
                transferable_advantages=transferable_advantages
            )
            
            logger.info(f"[Industry] Assessment complete - {source_industry} → {target_industry}: "
                       f"{overall_fit:.1f}% fit ({transition_category})")
            
            return alignment
            
        except Exception as e:
            logger.error(f"[Industry] Error in alignment assessment: {e}")
            # Return default assessment
            return IndustryAlignment(
                source_industry="unknown",
                target_industry="unknown", 
                transition_difficulty=0.5,
                domain_overlap_score=50.0,
                skill_transferability_score=50.0,
                experience_relevance_score=50.0,
                overall_fit_score=50.0,
                transition_category="Moderate",
                key_gaps=["Assessment error"],
                transferable_advantages=[]
            )
