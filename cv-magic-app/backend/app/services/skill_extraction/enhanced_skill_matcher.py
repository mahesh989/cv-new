"""
Enhanced Skill Matcher

Provides intelligent skill matching capabilities including:
- Semantic similarity matching
- Skill synonym recognition  
- Skill hierarchy understanding
- Fuzzy string matching
- Domain-aware skill relationships
"""

import logging
import re
from typing import Dict, List, Set, Tuple, Optional
from difflib import SequenceMatcher
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SkillMatch:
    """Represents a match between CV and JD skills"""
    jd_skill: str
    cv_skill: str
    match_type: str  # 'exact', 'synonym', 'hierarchical', 'fuzzy', 'semantic'
    confidence: float  # 0.0 to 1.0
    reasoning: str

class EnhancedSkillMatcher:
    """Enhanced skill matching with semantic understanding"""
    
    def __init__(self):
        self.skill_synonyms = self._build_skill_synonyms()
        self.skill_hierarchies = self._build_skill_hierarchies()
        self.domain_mappings = self._build_domain_mappings()
    
    def _build_skill_synonyms(self) -> Dict[str, Set[str]]:
        """Build a comprehensive skill synonym database"""
        return {
            # Data Analysis synonyms
            'data analysis': {'data analysis', 'data analytics', 'analytical skills', 'analytics', 'data science'},
            'data analytics': {'data analysis', 'data analytics', 'analytical skills', 'analytics', 'data science'},
            'analytics': {'data analysis', 'data analytics', 'analytical skills', 'analytics'},
            'analytical thinking': {'analytical skills', 'data analysis', 'problem solving', 'critical thinking'},
            
            # Business Intelligence synonyms
            'business intelligence': {'bi', 'business analytics', 'data warehousing', 'reporting', 'analytics', 'data science'},
            'bi': {'business intelligence', 'business analytics', 'reporting'},
            
            # Programming & Tools
            'sql': {'structured query language', 'database queries', 'database programming'},
            'python': {'python programming', 'python development', 'python scripting'},
            'excel': {'microsoft excel', 'spreadsheet analysis', 'excel modeling'},
            'power bi': {'powerbi', 'microsoft power bi', 'power business intelligence'},
            'tableau': {'tableau desktop', 'tableau server', 'data visualization'},
            'vba': {'visual basic for applications', 'excel vba', 'macro programming'},
            
            # Data Technologies
            'data mining': {'data discovery', 'pattern recognition', 'knowledge discovery'},
            'data warehouse': {'data warehousing', 'dwh', 'data storage', 'etl'},
            'data extraction': {'data ingestion', 'etl', 'data collection', 'data harvesting'},
            'etl': {'extract transform load', 'data pipeline', 'data integration'},
            
            # Machine Learning & AI
            'machine learning': {'ml', 'predictive modeling', 'statistical modeling', 'ai'},
            'deep learning': {'neural networks', 'dl', 'artificial neural networks'},
            'statistical analysis': {'statistics', 'statistical modeling', 'data modeling'},
            'predictive modeling': {'forecasting', 'prediction', 'model building'},
            
            # Soft Skills
            'communication': {'interpersonal skills', 'verbal communication', 'written communication'},
            'problem solving': {'problem-solving', 'analytical thinking', 'critical thinking', 'troubleshooting'},
            'problem-solving': {'problem solving', 'analytical thinking', 'critical thinking', 'troubleshooting'},
            'collaboration': {'teamwork', 'team collaboration', 'interpersonal skills'},
            'time management': {'prioritization', 'organization', 'planning'},
            'stakeholder management': {'client management', 'relationship management', 'stakeholder engagement'},
            
            # Project Management
            'project management': {'pm', 'project coordination', 'program management'},
            'agile': {'scrum', 'agile methodology', 'agile development'},
            
            # Visualization
            'data visualization': {'dashboard creation', 'reporting', 'charts', 'graphs'},
            'dashboard creation': {'dashboard development', 'reporting dashboards', 'data visualization'},
        }
    
    def _build_skill_hierarchies(self) -> Dict[str, Set[str]]:
        """Build skill hierarchies (specific -> general relationships)"""
        return {
            # ML/AI hierarchy - specific skills that imply broader capabilities
            'machine learning': {'data analysis', 'statistical analysis', 'data mining', 'analytics'},
            'deep learning': {'machine learning', 'data analysis', 'statistical analysis', 'analytics'},
            'neural networks': {'machine learning', 'deep learning', 'statistical analysis'},
            'random forests': {'machine learning', 'statistical analysis', 'data mining'},
            'logistic regression': {'machine learning', 'statistical analysis', 'data analysis'},
            
            # Data Science hierarchy
            'data science': {'data analysis', 'analytics', 'statistical analysis', 'data mining', 'business intelligence'},
            'statistical analysis': {'data analysis', 'analytics', 'data mining'},
            'predictive modeling': {'data analysis', 'statistical analysis', 'machine learning'},
            'analytics': {'business intelligence', 'data analysis', 'reporting'},
            
            # Technical Skills hierarchy
            'python': {'programming', 'scripting', 'automation'},
            'sql': {'database management', 'data extraction', 'data analysis'},
            'tableau': {'data visualization', 'business intelligence', 'reporting'},
            'power bi': {'data visualization', 'business intelligence', 'reporting'},
            'excel': {'data analysis', 'spreadsheet analysis', 'reporting'},
            
            # Domain-specific hierarchy
            'object detection': {'computer vision', 'machine learning', 'deep learning'},
            'model optimization': {'machine learning', 'performance tuning', 'algorithm optimization'},
            'fine-tuning': {'machine learning', 'model optimization', 'deep learning'},
        }
    
    def _build_domain_mappings(self) -> Dict[str, Set[str]]:
        """Build domain-specific skill mappings"""
        return {
            'data_analysis': {
                'sql', 'python', 'excel', 'tableau', 'power bi', 'data analysis', 
                'data mining', 'statistical analysis', 'analytics', 'business intelligence'
            },
            'machine_learning': {
                'python', 'machine learning', 'deep learning', 'neural networks',
                'statistical analysis', 'data analysis', 'predictive modeling'
            },
            'business_intelligence': {
                'tableau', 'power bi', 'excel', 'sql', 'data warehouse',
                'business intelligence', 'reporting', 'dashboard creation'
            }
        }
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill for comparison"""
        normalized = skill.lower().strip()
        # Remove common variations
        normalized = re.sub(r'[^\w\s+#.]', ' ', normalized)  # Keep +, #, . for tech skills
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized.strip()
    
    def fuzzy_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate fuzzy string similarity between skills"""
        s1 = self.normalize_skill(skill1)
        s2 = self.normalize_skill(skill2)
        return SequenceMatcher(None, s1, s2).ratio()
    
    def find_synonyms(self, skill: str) -> Set[str]:
        """Find all synonyms for a given skill"""
        normalized_skill = self.normalize_skill(skill)
        
        # Check direct synonym mapping
        if normalized_skill in self.skill_synonyms:
            return self.skill_synonyms[normalized_skill]
        
        # Check if skill appears in any synonym set
        for key, synonyms in self.skill_synonyms.items():
            if normalized_skill in synonyms or any(self.fuzzy_similarity(normalized_skill, syn) > 0.9 for syn in synonyms):
                return synonyms
        
        return {normalized_skill}
    
    def find_hierarchical_matches(self, cv_skill: str, jd_skill: str) -> Optional[Tuple[str, float]]:
        """Check if CV skill implies JD skill through hierarchy"""
        cv_normalized = self.normalize_skill(cv_skill)
        jd_normalized = self.normalize_skill(jd_skill)
        
        # Check if CV skill implies JD skill (CV skill is more specific)
        if cv_normalized in self.skill_hierarchies:
            implied_skills = self.skill_hierarchies[cv_normalized]
            if jd_normalized in implied_skills:
                return ("hierarchical_up", 0.85)  # CV skill is more specific than JD
            
            # Check synonyms of implied skills
            for implied in implied_skills:
                if jd_normalized in self.find_synonyms(implied):
                    return ("hierarchical_synonym", 0.8)
        
        # Check reverse (JD skill implies CV skill - less common but possible)
        if jd_normalized in self.skill_hierarchies:
            implied_skills = self.skill_hierarchies[jd_normalized]
            if cv_normalized in implied_skills:
                return ("hierarchical_down", 0.7)  # JD skill is more specific than CV
        
        return None
    
    def match_skills(self, cv_skills: List[str], jd_skills: List[str]) -> List[SkillMatch]:
        """Find all possible matches between CV and JD skills"""
        matches = []
        
        for jd_skill in jd_skills:
            best_match = None
            best_confidence = 0.0
            
            for cv_skill in cv_skills:
                match_result = self._evaluate_skill_match(cv_skill, jd_skill)
                if match_result and match_result.confidence > best_confidence:
                    best_match = match_result
                    best_confidence = match_result.confidence
            
            if best_match:
                matches.append(best_match)
        
        return matches
    
    def _evaluate_skill_match(self, cv_skill: str, jd_skill: str) -> Optional[SkillMatch]:
        """Evaluate if two skills match and return match details"""
        cv_norm = self.normalize_skill(cv_skill)
        jd_norm = self.normalize_skill(jd_skill)
        
        # 1. Exact match
        if cv_norm == jd_norm:
            return SkillMatch(
                jd_skill=jd_skill,
                cv_skill=cv_skill,
                match_type='exact',
                confidence=1.0,
                reasoning='Exact match'
            )
        
        # 2. Synonym match
        cv_synonyms = self.find_synonyms(cv_skill)
        if jd_norm in cv_synonyms or cv_norm in self.find_synonyms(jd_skill):
            return SkillMatch(
                jd_skill=jd_skill,
                cv_skill=cv_skill,
                match_type='synonym',
                confidence=0.9,
                reasoning='Synonym match - equivalent skills'
            )
        
        # 3. Hierarchical match
        hierarchical_result = self.find_hierarchical_matches(cv_skill, jd_skill)
        if hierarchical_result:
            match_type, confidence = hierarchical_result
            reasoning = {
                'hierarchical_up': f'CV skill "{cv_skill}" demonstrates broader capability including "{jd_skill}"',
                'hierarchical_synonym': f'CV skill "{cv_skill}" relates to "{jd_skill}" through skill hierarchy',
                'hierarchical_down': f'JD requirement "{jd_skill}" is more specific than CV skill "{cv_skill}"'
            }
            return SkillMatch(
                jd_skill=jd_skill,
                cv_skill=cv_skill,
                match_type=match_type,
                confidence=confidence,
                reasoning=reasoning[match_type]
            )
        
        # 4. Fuzzy match (for spelling variations, etc.)
        fuzzy_score = self.fuzzy_similarity(cv_skill, jd_skill)
        if fuzzy_score > 0.85:  # High similarity threshold
            return SkillMatch(
                jd_skill=jd_skill,
                cv_skill=cv_skill,
                match_type='fuzzy',
                confidence=fuzzy_score * 0.8,  # Slightly lower confidence for fuzzy
                reasoning=f'High similarity ({fuzzy_score:.2f}) - likely same skill with minor differences'
            )
        
        # 5. Semantic match (broader context)
        semantic_score = self._calculate_semantic_similarity(cv_skill, jd_skill)
        if semantic_score > 0.7:
            return SkillMatch(
                jd_skill=jd_skill,
                cv_skill=cv_skill,
                match_type='semantic',
                confidence=semantic_score * 0.7,
                reasoning=f'Semantic similarity ({semantic_score:.2f}) - related skills in same domain'
            )
        
        return None
    
    def _calculate_semantic_similarity(self, cv_skill: str, jd_skill: str) -> float:
        """Calculate semantic similarity based on domain context"""
        cv_norm = self.normalize_skill(cv_skill)
        jd_norm = self.normalize_skill(jd_skill)
        
        # Check if skills appear in same domain
        shared_domains = 0
        total_domains = 0
        
        for domain, skills in self.domain_mappings.items():
            total_domains += 1
            cv_in_domain = cv_norm in skills or any(self.fuzzy_similarity(cv_norm, s) > 0.8 for s in skills)
            jd_in_domain = jd_norm in skills or any(self.fuzzy_similarity(jd_norm, s) > 0.8 for s in skills)
            
            if cv_in_domain and jd_in_domain:
                shared_domains += 1
        
        # Base semantic score from domain overlap
        domain_score = shared_domains / max(total_domains, 1) if total_domains > 0 else 0
        
        # Add bonus for word overlap
        cv_words = set(cv_norm.split())
        jd_words = set(jd_norm.split())
        word_overlap = len(cv_words.intersection(jd_words)) / len(cv_words.union(jd_words))
        
        return (domain_score * 0.7) + (word_overlap * 0.3)


# Global instance for easy access
enhanced_skill_matcher = EnhancedSkillMatcher()
