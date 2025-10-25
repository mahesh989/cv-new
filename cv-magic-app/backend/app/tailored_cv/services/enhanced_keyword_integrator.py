"""
Enhanced Keyword Integration System
Implements tiered keyword validation and semantic skills categorization
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class KeywordTier:
    """Classification of keyword types"""
    tier: int  # 1, 2, or 3
    keyword: str
    category: str
    reason: str

class EnhancedKeywordIntegrator:
    """Improved keyword integration with tier-based validation"""
    
    # Tier 1: Generic, transferable keywords (always safe to add)
    TIER1_PATTERNS = {
        'role_keywords': [
            'data analysis', 'business intelligence', 'analytics',
            'project management', 'team collaboration', 'stakeholder management'
        ],
        'soft_skills': [
            'leadership', 'communication', 'problem solving', 'critical thinking',
            'teamwork', 'adaptability', 'time management', 'attention to detail'
        ],
        'generic_technical': [
            'programming', 'scripting', 'database querying', 'data visualization',
            'data pipeline', 'data integration', 'reporting', 'automation'
        ]
    }
    
    # Tier 2: Requires semantic evidence from CV
    TIER2_PATTERNS = {
        'tool_families': {
            'sql': ['database querying', 'relational databases', 'query optimization'],
            'python': ['programming', 'scripting', 'automation'],
            'excel': ['spreadsheet analysis', 'data analysis', 'pivot tables'],
            'tableau': ['data visualization', 'dashboard creation', 'BI tools'],
            'cloud': ['cloud computing', 'cloud platforms', 'cloud services'],
            'git': ['version control', 'source control', 'collaboration tools']
        },
        'platform_agnostic': [
            'cloud computing', 'containerization', 'API development',
            'data warehousing', 'ETL processes', 'business intelligence'
        ]
    }
    
    # Tier 3: Specific tools/certifications (NEVER add without explicit mention)
    TIER3_PATTERNS = [
        # Specific database variants
        'postgresql', 'mysql', 'oracle', 'mongodb', 'cassandra',
        # Specific cloud platforms
        'aws certified', 'azure certified', 'gcp certified',
        # Advanced features
        'dax', 'power query', 'tableau server', 'databricks',
        # Certifications
        'scrum master', 'pmp', 'safe', 'cissp', 'cpa',
        # Advanced technologies
        'machine learning', 'deep learning', 'neural networks', 'ai/ml',
        'kubernetes', 'terraform', 'ansible'
    ]
    
    def __init__(self, cv_content: str, request_id: str = 'debug'):
        """Initialize with original CV content for semantic validation"""
        self.cv_content = cv_content.lower()
        self.cv_keywords = set(re.findall(r'\b\w+\b', self.cv_content))
        self.request_id = request_id
        
        logger.info(f"🔍 [{request_id}] [ENHANCED_KEYWORDS] Initialized with CV content ({len(self.cv_content)} chars, {len(self.cv_keywords)} keywords)")
        logger.debug(f"📊 [{request_id}] [ENHANCED_KEYWORDS] CV keywords sample: {list(self.cv_keywords)[:10]}")
        
    def classify_keyword(self, keyword: str) -> KeywordTier:
        """Classify a keyword into Tier 1, 2, or 3"""
        keyword_lower = keyword.lower()
        
        logger.debug(f"🔍 [{self.request_id}] [ENHANCED_KEYWORDS] Classifying keyword: '{keyword}'")
        
        # Check Tier 3 first (blocklist)
        for tier3_keyword in self.TIER3_PATTERNS:
            if tier3_keyword in keyword_lower:
                logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_KEYWORDS] Tier 3 keyword detected: '{keyword}' (contains '{tier3_keyword}')")
                return KeywordTier(
                    tier=3,
                    keyword=keyword,
                    category='specific_tool',
                    reason=f"Specific tool/certification: {tier3_keyword}"
                )
        
        # Check Tier 1 (always safe)
        for category, keywords in self.TIER1_PATTERNS.items():
            if any(k in keyword_lower for k in keywords):
                logger.info(f"✅ [{self.request_id}] [ENHANCED_KEYWORDS] Tier 1 keyword: '{keyword}' (category: {category})")
                return KeywordTier(
                    tier=1,
                    keyword=keyword,
                    category=category,
                    reason="Generic/transferable keyword"
                )
        
        # Check Tier 2 (needs semantic evidence)
        for tool, related_terms in self.TIER2_PATTERNS['tool_families'].items():
            if tool in self.cv_content:
                if any(term in keyword_lower for term in related_terms):
                    logger.info(f"🔍 [{self.request_id}] [ENHANCED_KEYWORDS] Tier 2 keyword: '{keyword}' (CV mentions '{tool}')")
                    return KeywordTier(
                        tier=2,
                        keyword=keyword,
                        category='tool_family',
                        reason=f"CV mentions {tool}, keyword is related"
                    )
        
        # Default to Tier 2 (needs validation)
        logger.info(f"🔍 [{self.request_id}] [ENHANCED_KEYWORDS] Default Tier 2 keyword: '{keyword}' (needs validation)")
        return KeywordTier(
            tier=2,
            keyword=keyword,
            category='unknown',
            reason="Needs semantic validation"
        )
    
    def has_semantic_evidence(self, keyword: str) -> Tuple[bool, str]:
        """Check if CV has semantic evidence for a keyword"""
        keyword_lower = keyword.lower()
        
        logger.debug(f"🔍 [{self.request_id}] [ENHANCED_KEYWORDS] Checking semantic evidence for: '{keyword}'")
        
        # Direct mention
        if keyword_lower in self.cv_content:
            logger.info(f"✅ [{self.request_id}] [ENHANCED_KEYWORDS] Direct mention found for: '{keyword}'")
            return True, "Direct mention in CV"
        
        # Synonym/variation check
        synonyms = self._get_synonyms(keyword_lower)
        for syn in synonyms:
            if syn in self.cv_content:
                logger.info(f"✅ [{self.request_id}] [ENHANCED_KEYWORDS] Synonym '{syn}' found for: '{keyword}'")
                return True, f"Synonym '{syn}' found in CV"
        
        # Related work check
        related_activities = self._get_related_activities(keyword_lower)
        for activity in related_activities:
            if activity in self.cv_content:
                logger.info(f"✅ [{self.request_id}] [ENHANCED_KEYWORDS] Related activity '{activity}' found for: '{keyword}'")
                return True, f"Related activity '{activity}' found"
        
        logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_KEYWORDS] No semantic evidence found for: '{keyword}'")
        return False, "No semantic evidence found"
    
    def _get_synonyms(self, keyword: str) -> List[str]:
        """Get common synonyms for a keyword"""
        synonym_map = {
            'leadership': ['led', 'managed', 'directed', 'supervised'],
            'collaboration': ['collaborated', 'worked with', 'partnered', 'team'],
            'communication': ['presented', 'communicated', 'reported', 'briefed'],
            'analysis': ['analyzed', 'examined', 'evaluated', 'assessed'],
            'optimization': ['optimized', 'improved', 'enhanced', 'streamlined'],
            'automation': ['automated', 'scripted', 'programmed'],
            'visualization': ['visualized', 'charted', 'graphed', 'dashboard']
        }
        return synonym_map.get(keyword, [])
    
    def _get_related_activities(self, keyword: str) -> List[str]:
        """Get activities that imply the keyword"""
        activity_map = {
            'database querying': ['sql', 'queries', 'database', 'data retrieval'],
            'data visualization': ['dashboard', 'chart', 'graph', 'tableau', 'power bi'],
            'programming': ['python', 'code', 'script', 'software'],
            'cloud computing': ['aws', 'azure', 'gcp', 'cloud'],
            'project management': ['managed project', 'led initiative', 'coordinated'],
            'stakeholder management': ['stakeholder', 'client', 'customer', 'executive']
        }
        return activity_map.get(keyword, [])
    
    def validate_keyword_integration(
        self, 
        missing_keywords: List[str]
    ) -> Dict[str, List[str]]:
        """Validate and categorize missing keywords for integration"""
        
        logger.info(f"🔍 [{self.request_id}] [ENHANCED_KEYWORDS] Starting keyword integration validation for {len(missing_keywords)} keywords")
        
        results = {
            'tier1_integrate': [],  # Always add (generic/transferable)
            'tier1_adapt': [],      # Tier 1 with small modifications
            'tier2_integrate': [],  # Add if evidence exists
            'tier3_reject': [],     # Never add
            'tier2_no_evidence': [] # Don't add (no evidence)
        }
        
        for keyword in missing_keywords:
            logger.debug(f"🔍 [{self.request_id}] [ENHANCED_KEYWORDS] Processing keyword: '{keyword}'")
            
            classification = self.classify_keyword(keyword)
            
            if classification.tier == 1:
                # Check if we can find semantic evidence first
                has_evidence, reason = self.has_semantic_evidence(keyword)
                if has_evidence:
                    results['tier1_integrate'].append(keyword)
                    logger.info(f"✅ [{self.request_id}] [ENHANCED_KEYWORDS] Tier 1 - Integrate (has evidence): '{keyword}' - {reason}")
                else:
                    # Even without evidence, integrate with small modifications for generic skills
                    results['tier1_adapt'].append(keyword)
                    logger.info(f"✅ [{self.request_id}] [ENHANCED_KEYWORDS] Tier 1 - Adapt (generic skill): '{keyword}' - Will integrate with modifications")
            
            elif classification.tier == 2:
                has_evidence, reason = self.has_semantic_evidence(keyword)
                if has_evidence:
                    results['tier2_integrate'].append(keyword)
                    logger.info(f"✅ [{self.request_id}] [ENHANCED_KEYWORDS] Tier 2 - Integrate (has evidence): '{keyword}' - {reason}")
                else:
                    results['tier2_no_evidence'].append(keyword)
                    logger.warning(f"⚠️ [{self.request_id}] [ENHANCED_KEYWORDS] Tier 2 - Skip (no evidence): '{keyword}' - {reason}")
            
            elif classification.tier == 3:
                results['tier3_reject'].append(keyword)
                logger.warning(f"❌ [{self.request_id}] [ENHANCED_KEYWORDS] Tier 3 - Reject (unverifiable): '{keyword}' - {classification.reason}")
        
        # Summary logging
        logger.info(f"📊 [{self.request_id}] [ENHANCED_KEYWORDS] Keyword integration summary:")
        logger.info(f"   - Tier 1 (With Evidence): {len(results['tier1_integrate'])} keywords")
        logger.info(f"   - Tier 1 (Adapt/Modify): {len(results['tier1_adapt'])} keywords")
        logger.info(f"   - Tier 2 (With Evidence): {len(results['tier2_integrate'])} keywords")
        logger.info(f"   - Tier 2 (No Evidence): {len(results['tier2_no_evidence'])} keywords")
        logger.info(f"   - Tier 3 (Rejected): {len(results['tier3_reject'])} keywords")
        
        return results
    
    def generate_tier1_modifications(self, keywords: List[str]) -> Dict[str, str]:
        """Generate modified versions of Tier 1 keywords for integration without evidence"""
        
        logger.info(f"🔧 [{self.request_id}] [ENHANCED_KEYWORDS] Generating Tier 1 modifications for {len(keywords)} keywords")
        
        modifications = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Generate context-appropriate modifications
            if keyword_lower in ['leadership', 'team leadership']:
                modifications[keyword] = "Demonstrated leadership through project coordination and team collaboration"
            elif keyword_lower in ['communication', 'verbal communication', 'written communication']:
                modifications[keyword] = "Strong communication skills developed through stakeholder interaction and technical documentation"
            elif keyword_lower in ['teamwork', 'collaboration']:
                modifications[keyword] = "Proven teamwork abilities through cross-functional collaboration and project delivery"
            elif keyword_lower in ['problem solving', 'analytical thinking']:
                modifications[keyword] = "Strong problem-solving skills applied to technical challenges and process optimization"
            elif keyword_lower in ['time management', 'project management']:
                modifications[keyword] = "Effective time management demonstrated through project delivery and deadline adherence"
            elif keyword_lower in ['adaptability', 'flexibility']:
                modifications[keyword] = "Adaptable professional with experience across diverse technical environments"
            else:
                # Generic modification for other Tier 1 keywords
                modifications[keyword] = f"Developed {keyword} skills through professional experience and continuous learning"
            
            logger.info(f"🔧 [{self.request_id}] [ENHANCED_KEYWORDS] Modified '{keyword}' → '{modifications[keyword]}'")
        
        return modifications


class SemanticSkillsCategorizer:
    """Semantic-based skills categorization (no hard-coded lists)"""
    
    CATEGORY_PATTERNS = {
        'Programming/Scripting': [
            'python', 'java', 'javascript', 'r', 'c++', 'sql',
            'programming', 'coding', 'scripting', 'development'
        ],
        'Data Analysis/BI': [
            'excel', 'tableau', 'power bi', 'looker', 'qlik',
            'analysis', 'analytics', 'visualization', 'reporting'
        ],
        'Cloud/Infrastructure': [
            'aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes',
            'devops', 'infrastructure', 'deployment'
        ],
        'Databases': [
            'sql', 'postgresql', 'mysql', 'mongodb', 'snowflake',
            'database', 'data warehouse', 'etl'
        ],
        'Professional Skills': [
            'leadership', 'communication', 'stakeholder', 'management',
            'collaboration', 'problem solving', 'critical thinking'
        ],
        'Domain Expertise': []  # Populated dynamically based on JD
    }
    
    def __init__(self, request_id: str = 'debug'):
        self.request_id = request_id
        logger.info(f"🔍 [{request_id}] [SEMANTIC_SKILLS] Initialized semantic skills categorizer")
    
    def categorize_skill(self, skill: str, domain_keywords: List[str] = None) -> str:
        """Categorize a skill semantically"""
        skill_lower = skill.lower()
        
        logger.debug(f"🔍 [{self.request_id}] [SEMANTIC_SKILLS] Categorizing skill: '{skill}'")
        
        # Check domain expertise first
        if domain_keywords:
            if any(dk.lower() in skill_lower for dk in domain_keywords):
                logger.info(f"✅ [{self.request_id}] [SEMANTIC_SKILLS] Domain expertise: '{skill}'")
                return 'Domain Expertise'
        
        # Check other categories
        for category, patterns in self.CATEGORY_PATTERNS.items():
            if any(pattern in skill_lower for pattern in patterns):
                logger.info(f"✅ [{self.request_id}] [SEMANTIC_SKILLS] {category}: '{skill}'")
                return category
        
        # Default to Professional Skills for soft skills
        soft_skill_indicators = ['management', 'leadership', 'communication', 'analysis']
        if any(ind in skill_lower for ind in soft_skill_indicators):
            logger.info(f"✅ [{self.request_id}] [SEMANTIC_SKILLS] Professional Skills: '{skill}'")
            return 'Professional Skills'
        
        logger.info(f"✅ [{self.request_id}] [SEMANTIC_SKILLS] Other: '{skill}'")
        return 'Other'
    
    def group_skills(
        self, 
        skills: List[str], 
        domain_keywords: List[str] = None
    ) -> Dict[str, List[str]]:
        """Group skills into semantic categories"""
        
        logger.info(f"🔍 [{self.request_id}] [SEMANTIC_SKILLS] Grouping {len(skills)} skills into categories")
        
        categorized = {}
        
        for skill in skills:
            category = self.categorize_skill(skill, domain_keywords)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(skill)
        
        # Sort categories by importance
        priority_order = [
            'Programming/Scripting',
            'Data Analysis/BI',
            'Databases',
            'Cloud/Infrastructure',
            'Domain Expertise',
            'Professional Skills',
            'Other'
        ]
        
        sorted_categories = {}
        for cat in priority_order:
            if cat in categorized and categorized[cat]:
                sorted_categories[cat] = sorted(categorized[cat])
                logger.info(f"📊 [{self.request_id}] [SEMANTIC_SKILLS] {cat}: {len(categorized[cat])} skills")
        
        logger.info(f"📊 [{self.request_id}] [SEMANTIC_SKILLS] Skills categorization complete: {len(sorted_categories)} categories")
        return sorted_categories
