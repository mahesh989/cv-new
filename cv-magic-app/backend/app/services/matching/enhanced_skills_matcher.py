"""
Enhanced Skills Matcher

Addresses the semantic skill matching inconsistencies by implementing:
1. Semantic skill equivalence mapping
2. Domain clustering for related fields  
3. Transferable/learnable skills assessment
4. Industry alignment scoring with realistic transitions
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)


class SkillType(Enum):
    TECHNICAL = "technical"
    SOFT = "soft"
    DOMAIN = "domain"
    TRANSFERABLE = "transferable"


@dataclass
class SkillMatch:
    """Represents a skill match with confidence and type"""
    cv_skill: str
    jd_skill: str
    match_type: str  # "exact", "semantic", "transferable", "learnable"
    confidence: float  # 0.0 to 1.0
    skill_type: SkillType


@dataclass 
class SkillAnalysis:
    """Complete skill analysis results"""
    matched_skills: List[SkillMatch]
    missing_skills: List[str]
    transferable_skills: List[SkillMatch]
    match_rate: float
    confidence_weighted_rate: float


class EnhancedSkillsMatcher:
    """
    Enhanced skills matcher that addresses semantic matching issues
    """
    
    def __init__(self):
        self._initialize_skill_mappings()
        self._initialize_domain_clusters()
        self._initialize_transferable_mappings()
    
    def _initialize_skill_mappings(self):
        """Initialize semantic skill equivalence mappings"""
        
        # Soft Skills Semantic Equivalence
        self.soft_skills_map = {
            # Organization & Planning
            "organized": ["organised", "task management", "time management", "planning", "project planning", "workflow management"],
            "task management": ["organized", "organised", "multitasking", "prioritization", "time management"],
            "time management": ["organized", "organised", "task management", "scheduling", "planning"],
            "multitasking": ["task management", "organized", "juggling priorities", "parallel processing"],
            "prioritization": ["task management", "organized", "decision making", "strategic thinking"],
            
            # Communication
            "communication": ["written communication", "verbal communication", "presentation", "public speaking", "interpersonal skills"],
            "presentation": ["public speaking", "communication", "stakeholder engagement", "reporting"],
            "stakeholder engagement": ["communication", "relationship building", "client management", "presentation"],
            "collaboration": ["teamwork", "cross-functional collaboration", "partnership", "cooperation"],
            "teamwork": ["collaboration", "team player", "cross-functional collaboration"],
            
            # Leadership & Management
            "leadership": ["team leadership", "people management", "mentoring", "coaching", "strategic leadership"],
            "management": ["people management", "team management", "leadership", "supervision"],
            "mentoring": ["coaching", "leadership", "training", "knowledge transfer"],
            "coaching": ["mentoring", "leadership", "training", "development"],
            
            # Problem Solving & Analysis
            "problem solving": ["analytical thinking", "troubleshooting", "critical thinking", "solution design"],
            "analytical thinking": ["problem solving", "data analysis", "critical thinking", "research"],
            "critical thinking": ["analytical thinking", "problem solving", "decision making", "evaluation"],
            "research": ["analytical thinking", "investigation", "data gathering", "analysis"],
            
            # Adaptability & Learning
            "adaptability": ["flexibility", "change management", "learning agility", "resilience"],
            "flexibility": ["adaptability", "change management", "agility", "versatility"],
            "learning agility": ["adaptability", "continuous learning", "quick learner", "upskilling"],
            "continuous learning": ["learning agility", "professional development", "upskilling", "growth mindset"]
        }
        
        # Technical Skills Semantic Equivalence
        self.technical_skills_map = {
            # Programming Languages
            "javascript": ["js", "node.js", "nodejs", "ecmascript"],
            "typescript": ["ts", "javascript", "js"],
            "python": ["py", "python3", "django", "flask", "fastapi"],
            
            # Data & Analytics
            "excel": ["microsoft excel", "spreadsheets", "vba", "pivot tables", "vlookup"],
            "vba": ["excel", "microsoft excel", "excel automation", "macros"],
            "sql": ["mysql", "postgresql", "database", "queries", "data analysis"],
            "data analysis": ["analytics", "data analytics", "statistical analysis", "sql", "excel"],
            "tableau": ["data visualization", "dashboard", "reporting", "analytics"],
            "power bi": ["powerbi", "data visualization", "dashboard", "microsoft bi"],
            
            # Cloud & Infrastructure
            "aws": ["amazon web services", "cloud computing", "ec2", "s3"],
            "azure": ["microsoft azure", "cloud computing", "cloud services"],
            "docker": ["containerization", "containers", "devops"],
            "kubernetes": ["k8s", "container orchestration", "devops"],
            
            # Frameworks & Libraries
            "react": ["reactjs", "javascript", "frontend", "ui development"],
            "angular": ["angularjs", "typescript", "frontend", "spa"],
            "django": ["python", "web framework", "backend"],
            "flask": ["python", "web framework", "microservices"],
            
            # Tools & Platforms
            "git": ["version control", "source control", "github", "gitlab"],
            "github": ["git", "version control", "collaboration", "code repository"],
            "jira": ["project management", "issue tracking", "agile", "scrum"],
            "confluence": ["documentation", "wiki", "knowledge management"],
        }
    
    def _initialize_domain_clusters(self):
        """Initialize domain clusters for related field matching"""
        
        self.domain_clusters = {
            "data_and_analytics": [
                "data science", "data analysis", "data analytics", "business intelligence", 
                "machine learning", "ai", "artificial intelligence", "statistics", 
                "quantitative analysis", "data engineering", "big data", "data visualization"
            ],
            "software_development": [
                "software engineering", "web development", "full stack development", 
                "frontend development", "backend development", "mobile development",
                "application development", "programming", "coding", "software design"
            ],
            "cloud_and_devops": [
                "cloud computing", "devops", "infrastructure", "system administration",
                "site reliability engineering", "platform engineering", "automation",
                "containerization", "microservices", "cicd"
            ],
            "project_management": [
                "project management", "program management", "agile", "scrum", "kanban",
                "product management", "delivery management", "pmo", "portfolio management"
            ],
            "finance_and_accounting": [
                "finance", "accounting", "financial analysis", "investment", "banking",
                "financial planning", "budgeting", "treasury", "risk management", "audit"
            ],
            "marketing_and_sales": [
                "marketing", "digital marketing", "sales", "business development",
                "customer acquisition", "lead generation", "brand management", "advertising"
            ],
            "nonprofit_and_social": [
                "nonprofit", "non-profit", "ngo", "fundraising", "social impact",
                "community development", "humanitarian", "charity", "philanthropy"
            ],
            "consulting_and_strategy": [
                "consulting", "strategy", "business strategy", "management consulting",
                "strategic planning", "transformation", "change management"
            ]
        }
    
    def _initialize_transferable_mappings(self):
        """Initialize transferable and learnable skill mappings"""
        
        self.transferable_skills = {
            # Excel experience suggests VBA capability
            "vba": {
                "source_skills": ["excel", "microsoft excel", "spreadsheet automation", "macros"],
                "learnability": 0.8,  # High - if you know Excel well, VBA is learnable
                "description": "VBA is learnable with strong Excel background"
            },
            
            # SQL knowledge suggests database skills
            "database administration": {
                "source_skills": ["sql", "mysql", "postgresql", "database design"],
                "learnability": 0.7,
                "description": "Database administration builds on SQL knowledge"
            },
            
            # Programming language transferability
            "typescript": {
                "source_skills": ["javascript", "java", "c#", "programming"],
                "learnability": 0.9,  # Very high for JS developers
                "description": "TypeScript is highly learnable for JavaScript developers"
            },
            
            "python": {
                "source_skills": ["java", "c++", "c#", "javascript", "programming"],
                "learnability": 0.8,
                "description": "Python is learnable for experienced programmers"
            },
            
            # Cloud platform transferability
            "azure": {
                "source_skills": ["aws", "google cloud", "cloud computing"],
                "learnability": 0.7,
                "description": "Cloud platforms share similar concepts"
            },
            
            "aws": {
                "source_skills": ["azure", "google cloud", "cloud computing"],
                "learnability": 0.7,
                "description": "Cloud platforms share similar concepts"
            },
            
            # Project management tools
            "jira": {
                "source_skills": ["asana", "trello", "monday.com", "project management"],
                "learnability": 0.9,
                "description": "Project management tools have similar workflows"
            }
        }
    
    def _find_semantic_matches(self, cv_skill: str, jd_skills: List[str], skill_type: SkillType) -> List[SkillMatch]:
        """Find semantic matches for a CV skill against JD skills"""
        matches = []
        cv_skill_lower = cv_skill.lower().strip()
        
        # Choose appropriate mapping
        skill_map = {}
        if skill_type == SkillType.SOFT:
            skill_map = self.soft_skills_map
        elif skill_type == SkillType.TECHNICAL:
            skill_map = self.technical_skills_map
        
        # Check for exact matches first
        for jd_skill in jd_skills:
            jd_skill_lower = jd_skill.lower().strip()
            if cv_skill_lower == jd_skill_lower:
                matches.append(SkillMatch(
                    cv_skill=cv_skill,
                    jd_skill=jd_skill,
                    match_type="exact",
                    confidence=1.0,
                    skill_type=skill_type
                ))
        
        # Check for semantic matches
        for jd_skill in jd_skills:
            jd_skill_lower = jd_skill.lower().strip()
            
            # Check if CV skill maps to JD skill
            if cv_skill_lower in skill_map:
                equivalent_skills = [s.lower() for s in skill_map[cv_skill_lower]]
                if jd_skill_lower in equivalent_skills:
                    matches.append(SkillMatch(
                        cv_skill=cv_skill,
                        jd_skill=jd_skill,
                        match_type="semantic",
                        confidence=0.85,
                        skill_type=skill_type
                    ))
            
            # Check if JD skill maps to CV skill
            if jd_skill_lower in skill_map:
                equivalent_skills = [s.lower() for s in skill_map[jd_skill_lower]]
                if cv_skill_lower in equivalent_skills:
                    matches.append(SkillMatch(
                        cv_skill=cv_skill,
                        jd_skill=jd_skill,
                        match_type="semantic",
                        confidence=0.85,
                        skill_type=skill_type
                    ))
        
        return matches
    
    def _find_domain_matches(self, cv_domains: List[str], jd_domains: List[str]) -> List[SkillMatch]:
        """Find matches between domain keywords using clustering"""
        matches = []
        
        for cv_domain in cv_domains:
            cv_domain_lower = cv_domain.lower().strip()
            
            # Find which cluster the CV domain belongs to
            cv_cluster = None
            for cluster_name, domains in self.domain_clusters.items():
                if any(cv_domain_lower in domain.lower() or domain.lower() in cv_domain_lower for domain in domains):
                    cv_cluster = cluster_name
                    break
            
            if cv_cluster:
                # Check if any JD domains are in the same cluster
                for jd_domain in jd_domains:
                    jd_domain_lower = jd_domain.lower().strip()
                    
                    # Exact match first
                    if cv_domain_lower == jd_domain_lower:
                        matches.append(SkillMatch(
                            cv_skill=cv_domain,
                            jd_skill=jd_domain,
                            match_type="exact",
                            confidence=1.0,
                            skill_type=SkillType.DOMAIN
                        ))
                        continue
                    
                    # Cluster match
                    if any(jd_domain_lower in domain.lower() or domain.lower() in jd_domain_lower 
                          for domain in self.domain_clusters[cv_cluster]):
                        matches.append(SkillMatch(
                            cv_skill=cv_domain,
                            jd_skill=jd_domain,
                            match_type="semantic",
                            confidence=0.75,
                            skill_type=SkillType.DOMAIN
                        ))
        
        return matches
    
    def _find_transferable_matches(self, cv_skills: List[str], missing_jd_skills: List[str]) -> List[SkillMatch]:
        """Find transferable/learnable skills"""
        matches = []
        cv_skills_lower = [skill.lower().strip() for skill in cv_skills]
        
        for missing_skill in missing_jd_skills:
            missing_skill_lower = missing_skill.lower().strip()
            
            if missing_skill_lower in self.transferable_skills:
                transfer_info = self.transferable_skills[missing_skill_lower]
                
                # Check if candidate has any source skills
                source_matches = []
                for source_skill in transfer_info["source_skills"]:
                    for cv_skill in cv_skills:
                        if source_skill.lower() in cv_skill.lower() or cv_skill.lower() in source_skill.lower():
                            source_matches.append(cv_skill)
                
                if source_matches:
                    # Create transferable match
                    matches.append(SkillMatch(
                        cv_skill=", ".join(source_matches),
                        jd_skill=missing_skill,
                        match_type="transferable",
                        confidence=transfer_info["learnability"],
                        skill_type=SkillType.TRANSFERABLE
                    ))
        
        return matches
    
    def analyze_skills(
        self, 
        cv_skills: Dict[str, List[str]], 
        jd_skills: Dict[str, List[str]]
    ) -> Dict[str, SkillAnalysis]:
        """
        Comprehensive skill analysis with enhanced matching
        
        Args:
            cv_skills: {"technical": [...], "soft": [...], "domain": [...]}
            jd_skills: {"technical": [...], "soft": [...], "domain": [...]}
        
        Returns:
            Dictionary of skill analyses by type
        """
        results = {}
        
        # Analyze technical skills
        if "technical" in cv_skills and "technical" in jd_skills:
            tech_matches = self._find_semantic_matches(
                cv_skills["technical"][0] if cv_skills["technical"] else "", 
                jd_skills["technical"], 
                SkillType.TECHNICAL
            ) if cv_skills["technical"] else []
            
            # Find all technical matches
            all_tech_matches = []
            for cv_skill in cv_skills["technical"]:
                matches = self._find_semantic_matches(cv_skill, jd_skills["technical"], SkillType.TECHNICAL)
                all_tech_matches.extend(matches)
            
            # Find missing skills
            matched_jd_skills = {match.jd_skill.lower() for match in all_tech_matches}
            missing_tech = [skill for skill in jd_skills["technical"] 
                           if skill.lower() not in matched_jd_skills]
            
            # Find transferable matches
            transferable_tech = self._find_transferable_matches(cv_skills["technical"], missing_tech)
            
            # Calculate rates
            total_jd_tech = len(jd_skills["technical"])
            match_rate = len(set(match.jd_skill for match in all_tech_matches)) / total_jd_tech if total_jd_tech > 0 else 0
            confidence_weighted_rate = sum(match.confidence for match in all_tech_matches) / total_jd_tech if total_jd_tech > 0 else 0
            
            results["technical"] = SkillAnalysis(
                matched_skills=all_tech_matches,
                missing_skills=missing_tech,
                transferable_skills=transferable_tech,
                match_rate=match_rate,
                confidence_weighted_rate=confidence_weighted_rate
            )
        
        # Analyze soft skills
        if "soft" in cv_skills and "soft" in jd_skills:
            all_soft_matches = []
            for cv_skill in cv_skills["soft"]:
                matches = self._find_semantic_matches(cv_skill, jd_skills["soft"], SkillType.SOFT)
                all_soft_matches.extend(matches)
            
            matched_jd_skills = {match.jd_skill.lower() for match in all_soft_matches}
            missing_soft = [skill for skill in jd_skills["soft"] 
                           if skill.lower() not in matched_jd_skills]
            
            total_jd_soft = len(jd_skills["soft"])
            match_rate = len(set(match.jd_skill for match in all_soft_matches)) / total_jd_soft if total_jd_soft > 0 else 0
            confidence_weighted_rate = sum(match.confidence for match in all_soft_matches) / total_jd_soft if total_jd_soft > 0 else 0
            
            results["soft"] = SkillAnalysis(
                matched_skills=all_soft_matches,
                missing_skills=missing_soft,
                transferable_skills=[],  # Soft skills typically not transferable in same way
                match_rate=match_rate,
                confidence_weighted_rate=confidence_weighted_rate
            )
        
        # Analyze domain keywords
        if "domain" in cv_skills and "domain" in jd_skills:
            domain_matches = self._find_domain_matches(cv_skills["domain"], jd_skills["domain"])
            
            matched_jd_domains = {match.jd_skill.lower() for match in domain_matches}
            missing_domains = [skill for skill in jd_skills["domain"] 
                              if skill.lower() not in matched_jd_domains]
            
            total_jd_domains = len(jd_skills["domain"])
            match_rate = len(set(match.jd_skill for match in domain_matches)) / total_jd_domains if total_jd_domains > 0 else 0
            confidence_weighted_rate = sum(match.confidence for match in domain_matches) / total_jd_domains if total_jd_domains > 0 else 0
            
            results["domain"] = SkillAnalysis(
                matched_skills=domain_matches,
                missing_skills=missing_domains,
                transferable_skills=[],
                match_rate=match_rate,
                confidence_weighted_rate=confidence_weighted_rate
            )
        
        logger.info(f"[Enhanced Matcher] Analysis complete - Technical: {results.get('technical', {}).match_rate if 'technical' in results else 0:.1%}, "
                   f"Soft: {results.get('soft', {}).match_rate if 'soft' in results else 0:.1%}, "
                   f"Domain: {results.get('domain', {}).match_rate if 'domain' in results else 0:.1%}")
        
        return results
