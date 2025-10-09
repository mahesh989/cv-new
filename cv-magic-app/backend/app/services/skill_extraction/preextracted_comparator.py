"""
Pre-Extracted Skills Comparator

Builds and runs prompts to compare pre-extracted CV skills against
pre-extracted JD requirements using the centralized AI service.

This module exposes both text and JSON comparison modes:
- build_prompt(cv_skills, jd_skills) -> str (legacy human-readable)
- run_comparison(ai_service, cv_skills, jd_skills, ...) -> str (legacy)
- build_json_prompt(cv_skills, jd_skills) -> str (strict JSON schema)
- run_comparison_json(ai_service, cv_skills, jd_skills, ...) -> Dict (strict JSON)

JSON mode adds normalization, truncation guards, and a deterministic output
schema suitable for programmatic reuse while preserving the legacy output
for the frontend.
"""

import logging
from typing import Dict, List, Tuple, Any
import json
import re

logger = logging.getLogger(__name__)

# SEMANTIC SKILL MAPPING for improved matching accuracy
SEMANTIC_SKILL_MAPPING = {
    # Soft Skills Equivalents - FIXED MATCHING
    "communication": [
        "communication",
        "communication skills",
        "interpersonal skills",
        "verbal communication",
        "written communication",
        "presentation skills"
    ],
    "leadership": [
        "leadership",
        "team leadership",
        "mentoring",
        "course facilitation",
        "student engagement",
        "team management"
    ],
    "teamwork": [
        "teamwork",
        "collaboration",
        "collaborative",
        "team collaboration",
        "cross-functional collaboration"
    ],
    "collaboration": [
        "collaboration",
        "teamwork",
        "collaborative",
        "team collaboration",
        "cross-functional collaboration"
    ],
    "problem-solving": [
        "problem-solving",
        "problem solving",
        "analytical thinking",
        "critical thinking",
        "troubleshooting",
        "solution-oriented"
    ],
    "organised": [
        "organised",
        "organized",
        "manage and prioritise multiple tasks",
        "task management", 
        "time management",
        "prioritization",
        "manage multiple tasks",
        "priority management"
    ],
    "project management": [
        "project management",
        "manage multiple projects", 
        "task prioritization",
        "deliver multiple projects",
        "project coordination",
        "task management",
        "manage and prioritise multiple tasks",
        "time management",
        "manage multiple tasks"
    ],
    "detail-oriented": [
        "detail-oriented",
        "detail oriented",
        "attention to detail",
        "accuracy",
        "precision",
        "99% accuracy",
        "data integrity",
        "quality assurance"
    ],
    "motivated": [
        "motivated",
        "self-motivated",
        "proactive",
        "self-driven",
        "initiative",
        "enthusiastic",
        "dynamic"
    ],
    "stakeholder management": [
        "stakeholder management",
        "stakeholder engagement",
        "work with stakeholders",
        "stakeholder interaction",
        "business stakeholder collaboration",
        "collaboration",
        "interpersonal skills"
    ],
    "adaptability": [
        "adaptability",
        "adaptable",
        "flexible",
        "dynamic environments",
        "diverse industries",
        "cross-functional"
    ],
    
    # Technical Skills Equivalents - IMPROVED MATCHING
    "sql": [
        "sql",
        "database management",
        "database querying",
        "relational databases",
        "postgresql",
        "mysql"
    ],
    "excel": [
        "excel",
        "spreadsheets",
        "microsoft excel"
    ],
    "power bi": [
        "power bi",
        "business intelligence",
        "data visualization",
        "dashboard creation",
        "reporting"
    ],
    "tableau": [
        "tableau",
        "data visualization",
        "dashboard creation",
        "business intelligence"
    ],
    "vba": [
        "vba",
        "visual basic for applications",
        "excel vba",
        "macro programming"
    ],
    "data analysis": [
        "data analysis",
        "data analytics",
        "analytics",
        "statistical analysis"
    ],
    "data mining": [
        "data mining",
        "machine learning",
        "predictive analytics",
        "data science"
    ],
    "data modeling": [
        "data modeling",
        "data science",
        "machine learning",
        "statistical modeling"
    ],
    "data segmentation": [
        "data segmentation",
        "statistical analysis",
        "data analysis",
        "customer segmentation"
    ],
    "data warehousing": [
        "data warehousing",
        "data warehouse",
        "sql",
        "database management",
        "relational databases"
    ],
    "database management": [
        "database management",
        "sql",
        "relational databases",
        "postgresql",
        "mysql"
    ],
    "extracting data": [
        "extracting data",
        "data extraction",
        "sql",
        "database querying",
        "data retrieval"
    ],
    "querying": [
        "querying",
        "sql",
        "database querying",
        "data retrieval"
    ],
    "relational databases": [
        "relational databases",
        "sql",
        "database management",
        "postgresql",
        "mysql"
    ],
    "report creation": [
        "report creation",
        "reporting",
        "data visualization",
        "dashboard creation",
        "power bi",
        "tableau"
    ],
    "spreadsheets": [
        "spreadsheets",
        "excel",
        "microsoft excel"
    ],
    
    # Domain Keywords Equivalents
    "evidence-based decision making": [
        "data-driven decision making",
        "data-driven projects",
        "analytical decision making"
    ],
    "multi-channel communication": [
        "communication strategies",
        "stakeholder communication",
        "integrated communication"
    ]
}

# DOMAIN CLUSTERS for related field matching
DOMAIN_CLUSTERS = {
    "data_analytics_cluster": [
        "business intelligence",
        "data science", 
        "analytics",
        "data analysis",
        "data visualization",
        "dashboard creation",
        "data analytics",
        "statistical analysis"
    ],
    "database_cluster": [
        "data warehouse",
        "relational databases", 
        "database management",
        "sql databases",
        "sql",
        "data storage"
    ],
    "marketing_cluster": [
        "direct marketing",
        "campaign outcomes",
        "marketing analytics",
        "customer segmentation",
        "segmentation strategies"
    ],
    "reporting_cluster": [
        "reporting",
        "dashboard creation",
        "data visualization",
        "power bi",
        "tableau",
        "insights delivery"
    ]
}

# TRANSFERABLE SKILLS assessment
TRANSFERABLE_SKILLS = {
    "vba": {
        "base_skills": ["excel", "spreadsheets", "formulas"],
        "difficulty": "easy",
        "time_to_learn": "2-4 weeks",
        "note": "VBA is commonly learned by Excel users"
    },
    "tableau": {
        "base_skills": ["power bi", "data visualization", "dashboard creation"],
        "difficulty": "medium", 
        "time_to_learn": "1-2 months",
        "note": "Similar BI tools, transferable skills"
    },
    "data warehouse": {
        "base_skills": ["sql", "database", "relational databases"],
        "difficulty": "medium",
        "time_to_learn": "2-3 months", 
        "note": "SQL experience provides foundation"
    },
    "segmentation strategies": {
        "base_skills": ["data analysis", "statistical analysis", "analytics"],
        "difficulty": "easy",
        "time_to_learn": "3-6 weeks",
        "note": "Data analysis skills transfer to segmentation"
    }
}


def find_semantic_matches(cv_skills: List[str], jd_requirement: str) -> Tuple[bool, str, str]:
    """Find semantic matches between CV skills and JD requirements"""
    jd_normalized = jd_requirement.lower().strip()
    
    # Check direct equivalents in semantic mapping
    if jd_normalized in SEMANTIC_SKILL_MAPPING:
        for cv_skill in cv_skills:
            cv_normalized = cv_skill.lower().strip()
            for equivalent in SEMANTIC_SKILL_MAPPING[jd_normalized]:
                if equivalent in cv_normalized or cv_normalized in equivalent:
                    return True, cv_skill, "semantic match"
    
    # Check reverse mapping - CV skill mapped to JD requirement
    for cv_skill in cv_skills:
        cv_normalized = cv_skill.lower().strip()
        for key, equivalents in SEMANTIC_SKILL_MAPPING.items():
            if any(equiv in cv_normalized or cv_normalized in equiv for equiv in equivalents):
                if key in jd_normalized or jd_normalized in key:
                    return True, cv_skill, "reverse semantic match"
    
    return False, "", ""


def find_domain_matches(cv_domains: List[str], jd_requirement: str) -> Tuple[bool, str, str]:
    """Find matches within domain clusters"""
    jd_normalized = jd_requirement.lower().strip()
    
    for cluster_name, cluster_terms in DOMAIN_CLUSTERS.items():
        if any(term in jd_normalized or jd_normalized in term for term in cluster_terms):
            # Check if CV has any other terms from the same cluster
            for cv_domain in cv_domains:
                cv_normalized = cv_domain.lower().strip()
                if any(term in cv_normalized or cv_normalized in term for term in cluster_terms):
                    if cv_normalized != jd_normalized:  # Don't match identical
                        return True, cv_domain, f"domain cluster match ({cluster_name})"
    
    return False, "", ""


def assess_transferable_skill(missing_skill: str, cv_skills: List[str]) -> Tuple[bool, Dict[str, str]]:
    """Assess if a missing skill is transferable from existing CV skills"""
    missing_normalized = missing_skill.lower().strip()
    
    if missing_normalized in TRANSFERABLE_SKILLS:
        transfer_info = TRANSFERABLE_SKILLS[missing_normalized]
        
        # Check if CV has base skills
        for cv_skill in cv_skills:
            cv_normalized = cv_skill.lower().strip()
            for base_skill in transfer_info["base_skills"]:
                if base_skill in cv_normalized or cv_normalized in base_skill:
                    return True, {
                        "base_skill": cv_skill,
                        "missing_skill": missing_skill,
                        "difficulty": transfer_info["difficulty"],
                        "time_to_learn": transfer_info["time_to_learn"],
                        "note": transfer_info["note"]
                    }
    
    return False, {}


def _deduplicate_skills(skills_dict: Dict[str, list]) -> Dict[str, list]:
    """
    Remove duplicate skills across categories using semantic-aware matching.
    Priority: Technical > Soft > Domain (technical skills take precedence)
    """
    all_skills = set()
    deduplicated = {
        'technical_skills': [],
        'soft_skills': [],
        'domain_keywords': []
    }
    
    def _normalize_for_dedup(skill: str) -> str:
        """Normalize skill for deduplication while preserving important distinctions"""
        # Remove extra whitespace and convert to lowercase for comparison
        normalized = re.sub(r'\s+', ' ', skill.strip().lower())
        # Remove common variations that don't change meaning
        normalized = re.sub(r'\b(and|&|,)\b', ' ', normalized)
        return normalized
    
    # Process in priority order: Technical > Soft > Domain
    for skill in skills_dict.get('technical_skills', []):
        skill_normalized = _normalize_for_dedup(skill)
        if skill_normalized not in all_skills:
            deduplicated['technical_skills'].append(skill)
            all_skills.add(skill_normalized)
    
    for skill in skills_dict.get('soft_skills', []):
        skill_normalized = _normalize_for_dedup(skill)
        if skill_normalized not in all_skills:
            deduplicated['soft_skills'].append(skill)
            all_skills.add(skill_normalized)
    
    for skill in skills_dict.get('domain_keywords', []):
        skill_normalized = _normalize_for_dedup(skill)
        if skill_normalized not in all_skills:
            deduplicated['domain_keywords'].append(skill)
            all_skills.add(skill_normalized)
    
    return deduplicated


def _calculate_accurate_totals(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> Dict[str, int]:
    """
    Calculate accurate totals without duplication across categories.
    """
    cv_dedup = _deduplicate_skills(cv_skills)
    jd_dedup = _deduplicate_skills(jd_skills)
    
    cv_total = (
        len(cv_dedup['technical_skills']) + 
        len(cv_dedup['soft_skills']) + 
        len(cv_dedup['domain_keywords'])
    )
    
    jd_total = (
        len(jd_dedup['technical_skills']) + 
        len(jd_dedup['soft_skills']) + 
        len(jd_dedup['domain_keywords'])
    )
    
    return {
        'cv_total': cv_total,
        'jd_total': jd_total
    }


def build_prompt(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> str:
    """Return the exact comparison prompt with lists injected verbatim."""
    
    # Deduplicate skills to avoid double counting
    cv_deduplicated = _deduplicate_skills(cv_skills)
    jd_deduplicated = _deduplicate_skills(jd_skills)
    
    # Calculate accurate totals
    totals = _calculate_accurate_totals(cv_skills, jd_skills)
    
    # Get exact counts for each category
    cv_tech_count = len(cv_deduplicated.get('technical_skills', []))
    cv_soft_count = len(cv_deduplicated.get('soft_skills', []))
    cv_domain_count = len(cv_deduplicated.get('domain_keywords', []))
    jd_tech_count = len(jd_deduplicated.get('technical_skills', []))
    jd_soft_count = len(jd_deduplicated.get('soft_skills', []))
    jd_domain_count = len(jd_deduplicated.get('domain_keywords', []))
    
    return f"""
Compare these pre-extracted CV skills against pre-extracted JD requirements using intelligent semantic matching.

CV SKILLS:
Technical ({cv_tech_count} items): {cv_deduplicated.get('technical_skills', [])}
Soft ({cv_soft_count} items): {cv_deduplicated.get('soft_skills', [])}
Domain ({cv_domain_count} items): {cv_deduplicated.get('domain_keywords', [])}

JD REQUIREMENTS:
Technical ({jd_tech_count} items): {jd_deduplicated.get('technical_skills', [])}
Soft ({jd_soft_count} items): {jd_deduplicated.get('soft_skills', [])}
Domain ({jd_domain_count} items): {jd_deduplicated.get('domain_keywords', [])}

**CRITICAL COUNTING RULES:**
- CV Technical Skills: {cv_tech_count} items
- CV Soft Skills: {cv_soft_count} items  
- CV Domain Keywords: {cv_domain_count} items
- JD Technical Skills: {jd_tech_count} items
- JD Soft Skills: {jd_soft_count} items
- JD Domain Keywords: {jd_domain_count} items
- You CANNOT match more items than exist in the CV
- If CV has {cv_soft_count} soft skills, you can match AT MOST {cv_soft_count} JD soft skills
- If CV has {cv_tech_count} technical skills, you can match AT MOST {cv_tech_count} JD technical skills
- If CV has {cv_domain_count} domain keywords, you can match AT MOST {cv_domain_count} JD domain keywords

**MATCHING RULES:**
- Compare only the provided lists (no external knowledge)
- Use STRICT semantic matching: "Python programming" → "Python" = ✅ match
- "Leadership" → "Team leadership" = ✅ match  
- "Data analysis" → "Analytical skills" = ✅ match
- **CRITICAL**: Only match skills that are DIRECTLY relevant to the job requirements
- **CRITICAL**: Domain keywords must be relevant to the job domain (e.g., humanitarian work, not academic subjects)
- **CRITICAL**: Technical skills must be directly applicable to the job role
- **AVOID**: Overly broad matches like "Data Mining" → "Data Analysis" (these are different skills)
- **AVOID**: Matching academic subjects (Physics, Theoretical Physics) to non-academic jobs
- **EXAMPLE**: For UNHCR job, "Physics" and "Theoretical Physics" are NOT relevant domain keywords
- **EXAMPLE**: "Data Mining" and "Data Analysis" are different technical skills - don't match them
- **EXAMPLE**: "Business Intelligence Tools" → "Power BI" is acceptable (Power BI is a BI tool)
- **EXAMPLE**: "Data Science" → "Data Science" is acceptable (exact match)
- Only mark as missing if no DIRECT semantic equivalent exists
- Provide brief, clear reasoning
- IMPORTANT: Each skill is counted only once (no duplicates across categories)

**CRITICAL CATEGORIZATION RULES:**
- ✅ MATCHED section: ONLY list JD requirements that have a corresponding skill in the CV
- ❌ MISSING section: ONLY list JD requirements that have NO corresponding skill in the CV
- NEVER list the same JD requirement in both sections
- If a JD requirement has a match in CV → goes in MATCHED section
- If a JD requirement has no match in CV → goes in MISSING section

**OUTPUT FORMAT (TEXT ONLY):**
🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: {jd_tech_count + jd_soft_count + jd_domain_count}
Matched: [Calculate total matches across all categories]
Missing: [Calculate total missing across all categories]
Match Rate: [Calculate percentage: (Matched / Total Requirements) * 100]

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills            {cv_tech_count:2d}         {jd_tech_count:2d}         [Calculate matches]         [Calculate missing]            [Calculate percentage]
Soft Skills                  {cv_soft_count:2d}         {jd_soft_count:2d}         [Calculate matches]         [Calculate missing]            [Calculate percentage]
Domain Keywords             {cv_domain_count:2d}         {jd_domain_count:2d}         [Calculate matches]         [Calculate missing]            [Calculate percentage]

🧠 DETAILED AI ANALYSIS
--------------------------------------------------------------------------------

🔹 TECHNICAL SKILLS
  ✅ MATCHED JD REQUIREMENTS (K items):
    [ONLY list JD requirements that have a DIRECT corresponding skill in the CV]
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning: [Be specific - why is this a DIRECT match?]
  ❌ MISSING FROM CV (M items):
    [ONLY list JD requirements that have NO DIRECT corresponding skill in the CV]
    1. JD Requires: '...'
       💡 brief reason why not found: [Be specific - why no DIRECT match exists]

🔹 SOFT SKILLS
  ✅ MATCHED JD REQUIREMENTS (K items):
    [ONLY list JD requirements that have a corresponding skill in the CV]
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning
  ❌ MISSING FROM CV (M items):
    [ONLY list JD requirements that have NO corresponding skill in the CV]
    1. JD Requires: '...'
       💡 brief reason why not found

🔹 DOMAIN KEYWORDS
  ✅ MATCHED JD REQUIREMENTS (K items):
    [ONLY list JD requirements that have a DIRECT corresponding skill in the CV]
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning: [Be specific - why is this a DIRECT match?]
  ❌ MISSING FROM CV (M items):
    [ONLY list JD requirements that have NO DIRECT corresponding skill in the CV]
    1. JD Requires: '...'
       💡 brief reason why not found: [Be specific - why no DIRECT match exists]

📚 INPUT SUMMARY (normalized, truncated if long)
CV
- Technical: [List CV technical skills]
- Soft: [List CV soft skills]
- Domain: [List CV domain keywords]

JD
- Technical: [List JD technical skills]
- Soft: [List JD soft skills]
- Domain: [List JD domain keywords]

Return only this formatted analysis.
"""


async def execute_skills_semantic_comparison(ai_service, cv_skills: Dict[str, list], jd_skills: Dict[str, list], user: Any, temperature: float = 0.0, max_tokens: int = 3000) -> str:
    """Execute the comparison prompt using the centralized AI service and return formatted text."""
    try:
        # Use JSON mode for consistent structured output
        json_result = await execute_skills_comparison_with_json_output(ai_service, cv_skills, jd_skills, user, temperature, max_tokens)
        
        # Validate the results are mathematically correct
        if not _validate_comparison_results(json_result, cv_skills, jd_skills):
            logger.warning("⚠️ [COMPARISON] JSON results failed validation, attempting to fix inconsistencies")
            
            # Try to fix the JSON result using rule-based logic
            fixed_result = _fix_inconsistent_json_result(json_result, cv_skills, jd_skills)
            
            # If we successfully fixed it, use the fixed version
            if fixed_result and _validate_comparison_results(fixed_result, cv_skills, jd_skills):
                logger.info("✅ [COMPARISON] Successfully fixed AI response inconsistencies")
                json_result = fixed_result
            else:
                logger.warning("⚠️ [COMPARISON] Could not fix inconsistencies, falling back to text mode")
                # Fallback to text-based comparison if validation fails
                prompt = build_prompt(cv_skills, jd_skills)
                response = await ai_service.generate_response(
                    prompt=prompt,
                    user=user,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.content
        
        # Convert JSON result to formatted text for backward compatibility
        return _format_json_to_text(json_result, cv_skills, jd_skills)
        
    except Exception as e:
        # Fallback to original text-based comparison if JSON fails
        logger.warning(f"⚠️ [COMPARISON] JSON mode failed: {e}, falling back to text mode")
        prompt = build_prompt(cv_skills, jd_skills)
        response = await ai_service.generate_response(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.content


# -------------------------
# JSON-FIRST COMPARATOR
# -------------------------

def _normalize_list(values: List[str], max_items: int = 200) -> List[str]:
    """Normalize list while preserving important formatting for proper nouns and brand names."""
    if not values:
        return []
    seen = set()
    normalized: List[str] = []
    
    def _preserve_capitalization(skill: str) -> str:
        """Preserve capitalization for known proper nouns and brand names"""
        # Common brand names and proper nouns that should maintain capitalization
        brand_names = {
            'power bi', 'tableau', 'aws', 'azure', 'gcp', 'kubernetes', 'docker',
            'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'kafka',
            'react', 'angular', 'vue', 'node.js', 'express.js', 'django', 'flask',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
            'seaborn', 'plotly', 'jupyter', 'git', 'github', 'gitlab', 'jenkins',
            'terraform', 'ansible', 'chef', 'puppet', 'splunk', 'datadog', 'newrelic',
            'sql', 'vba', 'excel', 'python', 'java', 'javascript', 'html', 'css'
        }
        
        # Clean up whitespace but preserve original case for known brands
        cleaned = re.sub(r"\s+", " ", skill.strip())
        if cleaned.lower() in brand_names:
            return cleaned
        # For other skills, use title case for consistency
        return cleaned.title()
    
    for v in values:
        if not isinstance(v, str):
            continue
        normalized_skill = _preserve_capitalization(v)
        # Use lowercase for deduplication comparison
        s = normalized_skill.lower()
        if s and s not in seen:
            seen.add(s)
            normalized.append(normalized_skill)
    
    normalized.sort()
    if len(normalized) > max_items:
        return normalized[:max_items]
    return normalized


def _prepare_inputs(cv_skills: Dict[str, list], jd_skills: Dict[str, list], max_items: int = 200) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Prepare normalized and truncated inputs for prompt injection with deduplication."""
    
    # First deduplicate skills across categories
    cv_deduplicated = _deduplicate_skills(cv_skills)
    jd_deduplicated = _deduplicate_skills(jd_skills)
    
    # Then normalize and truncate
    cv = {
        "technical_skills": _normalize_list(cv_deduplicated.get("technical_skills", []), max_items),
        "soft_skills": _normalize_list(cv_deduplicated.get("soft_skills", []), max_items),
        "domain_keywords": _normalize_list(cv_deduplicated.get("domain_keywords", []), max_items),
    }
    jd = {
        "technical_skills": _normalize_list(jd_deduplicated.get("technical_skills", []), max_items),
        "soft_skills": _normalize_list(jd_deduplicated.get("soft_skills", []), max_items),
        "domain_keywords": _normalize_list(jd_deduplicated.get("domain_keywords", []), max_items),
    }
    return cv, jd


def build_json_prompt(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> str:
    """Return a strict JSON-only comparison prompt with enhanced matching guidance."""
    cv, jd = _prepare_inputs(cv_skills, jd_skills)
    
    # Get RAW counts for validation to match initial extraction display
    cv_tech_count = len(cv_skills.get('technical_skills', []))
    cv_soft_count = len(cv_skills.get('soft_skills', []))
    cv_domain_count = len(cv_skills.get('domain_keywords', []))
    jd_tech_count = len(jd_skills.get('technical_skills', []))
    jd_soft_count = len(jd_skills.get('soft_skills', []))
    jd_domain_count = len(jd_skills.get('domain_keywords', []))
    
    return (
        "You are an expert skill matching system. Compare the pre-extracted skills using INTELLIGENT SEMANTIC MATCHING.\n"
        "DO NOT require exact word matches - use professional skill equivalencies and relationships.\n\n"
        "INPUT LISTS (already normalized, sorted alphabetically):\n"
        f"CV.technical_skills ({cv_tech_count} items) = {cv['technical_skills']}\n"
        f"CV.soft_skills ({cv_soft_count} items) = {cv['soft_skills']}\n"
        f"CV.domain_keywords ({cv_domain_count} items) = {cv['domain_keywords']}\n\n"
        f"JD.technical_skills ({jd_tech_count} items) = {jd['technical_skills']}\n"
        f"JD.soft_skills ({jd_soft_count} items) = {jd['soft_skills']}\n"
        f"JD.domain_keywords ({jd_domain_count} items) = {jd['domain_keywords']}\n\n"
        "INTELLIGENT MATCHING RULES (apply in order):\n"
        "1. EXACT MATCH: Case-insensitive identical skills (e.g., 'SQL' = 'sql', 'Communication' = 'communication')\n"
        "   ⚠️ CRITICAL: If CV has 'Communication' and JD requires 'Communication' → EXACT MATCH\n"
        "   ⚠️ CRITICAL: If CV has 'Leadership' and JD requires 'Leadership' → EXACT MATCH\n"
        "   ⚠️ CRITICAL: If CV has 'Teamwork' and JD requires 'Teamwork' → EXACT MATCH\n"
        "   ⚠️ CRITICAL: If CV has 'Collaboration' and JD requires 'Collaboration' → EXACT MATCH\n"
        "   ⚠️ CRITICAL: If CV has 'Problem-solving' and JD requires 'Problem-solving' → EXACT MATCH\n"
        "2. SYNONYM MATCH: Professional equivalents:\n"
        "   • 'Data Analysis' = 'Data Analytics' = 'Analytics' = 'Statistical Analysis'\n"
        "   • 'Problem Solving' = 'Problem-Solving' = 'Analytical Thinking' = 'Critical Thinking'\n"
        "   • 'Machine Learning' = 'ML' = 'Predictive Analytics' = 'Data Science'\n"
        "   • 'Communication' = 'Communication Skills' = 'Interpersonal Skills'\n"
        "   • 'Collaboration' = 'Teamwork' = 'Collaborative' = 'Team Collaboration'\n"
        "   • 'Leadership' = 'Team Leadership' = 'Mentoring' = 'Course Facilitation'\n"
        "   • 'SQL' = 'Database Management' = 'Relational Databases' = 'PostgreSQL' = 'MySQL'\n"
        "   • 'Power BI' = 'Business Intelligence' = 'Data Visualization' = 'Dashboard Creation'\n"
        "   • 'Tableau' = 'Data Visualization' = 'Dashboard Creation' = 'Business Intelligence'\n"
        "   • 'Excel' = 'Spreadsheets' = 'Microsoft Excel'\n"
        "   • 'VBA' = 'Visual Basic for Applications' = 'Excel VBA' = 'Macro Programming'\n"
        "3. HIERARCHICAL MATCH: Specific skills demonstrate broader capabilities:\n"
        "   • 'Machine Learning' demonstrates 'Data Mining', 'Data Analysis', and 'Statistical Analysis'\n"
        "   • 'SQL' demonstrates 'Database Management', 'Data Extraction', 'Querying', and 'Relational Databases'\n"
        "   • 'Data Science' demonstrates 'Data Analysis', 'Statistical Analysis', and 'Machine Learning'\n"
        "   • 'Python' demonstrates 'Programming', 'Scripting', and 'Data Analysis' skills\n"
        "   • 'Tableau/Power BI' demonstrates 'Data Visualization', 'Business Intelligence', and 'Reporting'\n"
        "4. DOMAIN CONTEXT: Skills in same professional domain:\n"
        "   • Data Science: SQL, Python, Tableau, Power BI, Statistical Analysis, Machine Learning\n"
        "   • Business Intelligence: Data Science, Analytics, Data Visualization, Dashboard creation, Reporting\n"
        "   • Analytics: Data Analysis, Statistical Analysis, Data Mining, Business Intelligence, Data Science\n"
        "   • Database: SQL, Data Warehouse, Relational Databases, Data Storage, Data Extraction\n"
        "   • Reporting: Dashboard Creation, Data Visualization, Power BI, Tableau, Insights Delivery\n"
        "5. PARTIAL MATCH: Similar core concepts (use sparingly)\n\n"
        "CRITICAL CONSTRAINTS:\n"
        f"- CV has {cv_tech_count} technical, {cv_soft_count} soft, {cv_domain_count} domain skills\n"
        f"- JD has {jd_tech_count} technical, {jd_soft_count} soft, {jd_domain_count} domain requirements\n"
        f"- CANNOT match more CV skills than exist: max {cv_tech_count} technical, {cv_soft_count} soft, {cv_domain_count} domain\n"
        "- Each CV skill can only be used once across all categories\n"
        "- Prioritize stronger matches (exact > synonym > hierarchical > domain)\n"
        "- IMPORTANT: Total matched + missing must equal JD requirements count for each category\n"
        f"- Technical: matched + missing must = {jd_tech_count}\n"
        f"- Soft: matched + missing must = {jd_soft_count}\n"
        f"- Domain: matched + missing must = {jd_domain_count}\n\n"
        "EXAMPLES OF GOOD MATCHES:\n"
        "✅ JD: 'Communication' → CV: 'Communication' (exact match)\n"
        "✅ JD: 'Leadership' → CV: 'Leadership' (exact match)\n"
        "✅ JD: 'Teamwork' → CV: 'Collaboration' (synonym)\n"
        "✅ JD: 'Problem-Solving' → CV: 'Problem Solving' (exact, ignore punctuation)\n"
        "✅ JD: 'SQL' → CV: 'SQL' (exact match)\n"
        "✅ JD: 'Power BI' → CV: 'Power BI' (exact match)\n"
        "✅ JD: 'Excel' → CV: 'Excel' (exact match)\n"
        "✅ JD: 'Data Analysis' → CV: 'Data Analytics' (synonym)\n"
        "✅ JD: 'Data Mining' → CV: 'Machine Learning' (hierarchical - ML includes data mining)\n"
        "✅ JD: 'Database Management' → CV: 'SQL' (hierarchical - SQL demonstrates DB management)\n"
        "✅ JD: 'Report Creation' → CV: 'Data Visualization' (synonym - both involve creating reports)\n"
        "✅ JD: 'Tableau' → CV: 'Power BI' (domain context - both are BI tools)\n"
        "✅ JD: 'Relational Databases' → CV: 'SQL' (hierarchical - SQL works with relational databases)\n"
        "✅ JD: 'Extracting Data' → CV: 'SQL' (hierarchical - SQL enables data extraction)\n"
        "✅ JD: 'Querying' → CV: 'SQL' (hierarchical - SQL is used for querying)\n"
        "❌ DON'T match: JD: 'VBA' → CV: 'Python' (different programming languages)\n"
        "❌ DON'T match: JD: 'Fundraising' → CV: 'Data Science' (unrelated domains)\n"
        "❌ DON'T match: JD: 'Direct Marketing' → CV: 'Machine Learning' (different domains)\n\n"
        "OUTPUT (JSON ONLY, no prose, no markdown):\n"
        "{\n"
        "  \"technical_skills\": {\n"
        "    \"matched\": [\n"
        "      {\n"
        "        \"jd_skill\": \"exact JD requirement\",\n"
        "        \"cv_equivalent\": \"matching CV skill\",\n"
        "        \"reasoning\": \"match type and brief explanation\"\n"
        "      }\n"
        "    ],\n"
        "    \"missing\": [\n"
        "      { \"jd_skill\": \"...\", \"reasoning\": \"why no CV equivalent found\" }\n"
        "    ]\n"
        "  },\n"
        "  \"soft_skills\": { \"matched\": [], \"missing\": [] },\n"
        "  \"domain_keywords\": { \"matched\": [], \"missing\": [] }\n"
        "}\n"
        "Sort arrays by jd_skill alphabetically."
    )


def _extract_json_from_text(text: str) -> Any:
    """Best-effort extraction if the model wraps JSON with extra text."""
    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass
    # Fallback: find the largest JSON object in the text
    match = re.search(r"\{[\s\S]*\}$", text.strip())
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    # Try a more permissive bracket match
    brace_spans = [m.span() for m in re.finditer(r"\{", text)]
    for start, _ in reversed(brace_spans):
        candidate = text[start:]
        try:
            return json.loads(candidate)
        except Exception:
            continue
    raise ValueError("Failed to parse JSON from model output")


def _fix_inconsistent_json_result(json_result: Dict[str, Any], cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> Dict[str, Any]:
    """Fix inconsistencies in AI JSON response using rule-based logic."""
    try:
        logger.info("🔧 [FIX] Attempting to fix inconsistent AI response")
        fixed_result = json.loads(json.dumps(json_result))  # Deep copy
        
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            if category not in fixed_result:
                fixed_result[category] = {"matched": [], "missing": []}
                continue
                
            cv_skills_list = cv_skills.get(category, [])
            jd_skills_list = jd_skills.get(category, [])
            
            matched = fixed_result[category].get('matched', [])
            missing = fixed_result[category].get('missing', [])
            
            # If we have more matches than CV skills, trim the excess
            if len(matched) > len(cv_skills_list):
                logger.warning(f"🔧 [FIX] {category}: Trimming {len(matched)} matches to {len(cv_skills_list)} (CV limit)")
                # Keep the first N matches (likely more accurate)
                fixed_result[category]['matched'] = matched[:len(cv_skills_list)]
                
                # Move excess matches to missing
                excess_matches = matched[len(cv_skills_list):]
                for excess in excess_matches:
                    missing.append({
                        "jd_skill": excess.get('jd_skill', 'Unknown'),
                        "reasoning": "Moved from matched due to CV skills limit"
                    })
                fixed_result[category]['missing'] = missing
            
            # Ensure we account for all JD skills in this category
            total_accounted = len(fixed_result[category]['matched']) + len(fixed_result[category]['missing'])
            jd_count = len(jd_skills_list)
            
            if total_accounted < jd_count:
                # We're missing some JD skills - add them as missing
                logger.info(f"🔧 [FIX] {category}: Adding {jd_count - total_accounted} missing JD skills")
                
                # Find JD skills not accounted for
                accounted_jd_skills = set()
                for match in fixed_result[category]['matched']:
                    accounted_jd_skills.add(match.get('jd_skill', ''))
                for miss in fixed_result[category]['missing']:
                    accounted_jd_skills.add(miss.get('jd_skill', ''))
                
                for jd_skill in jd_skills_list:
                    if jd_skill not in accounted_jd_skills:
                        fixed_result[category]['missing'].append({
                            "jd_skill": jd_skill,
                            "reasoning": "Not accounted for in AI response"
                        })
            
            elif total_accounted > jd_count:
                # We have too many items - this shouldn't happen but let's handle it
                logger.warning(f"🔧 [FIX] {category}: Too many items ({total_accounted} > {jd_count}), trimming missing items")
                excess = total_accounted - jd_count
                if excess <= len(fixed_result[category]['missing']):
                    fixed_result[category]['missing'] = fixed_result[category]['missing'][:-excess]
        
        logger.info("✅ [FIX] Finished fixing AI response inconsistencies")
        return fixed_result
        
    except Exception as e:
        logger.error(f"❌ [FIX] Error fixing AI response: {e}")
        return None


def _sort_section(section: Dict[str, Any]) -> Dict[str, Any]:
    """Sort matched/missing arrays by jd_skill for determinism."""
    def sort_by_key(items: List[Dict[str, Any]], key: str = "jd_skill") -> List[Dict[str, Any]]:
        try:
            return sorted(items, key=lambda x: (x.get(key) or "").lower())
        except Exception:
            return items
    return {
        "matched": sort_by_key(section.get("matched", [])),
        "missing": sort_by_key(section.get("missing", [])),
    }


def _identify_exact_matches(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> Dict[str, List[Dict[str, str]]]:
    """Identify exact matches between CV and JD skills before AI processing."""
    exact_matches = {
        "technical_skills": [],
        "soft_skills": [],
        "domain_keywords": []
    }
    
    for category in ["technical_skills", "soft_skills", "domain_keywords"]:
        cv_list = [skill.lower().strip() for skill in cv_skills.get(category, [])]
        jd_list = jd_skills.get(category, [])
        
        for jd_skill in jd_list:
            jd_normalized = jd_skill.lower().strip()
            if jd_normalized in cv_list:
                # Find the original CV skill (preserve case)
                cv_skill = next((skill for skill in cv_skills.get(category, []) 
                               if skill.lower().strip() == jd_normalized), jd_skill)
                
                exact_matches[category].append({
                    "jd_skill": jd_skill,
                    "cv_skill": cv_skill,
                    "match_type": "exact",
                    "confidence": 1.0,
                    "reasoning": "Exact match - identical skills"
                })
    
    return exact_matches


def _ensure_exact_matches_included(
    result: Dict[str, Any], 
    exact_matches: Dict[str, List[Dict[str, str]]], 
    cv_skills: Dict[str, list], 
    jd_skills: Dict[str, list]
) -> Dict[str, Any]:
    """Ensure that exact matches are included in the final result."""
    
    for category in ["technical_skills", "soft_skills", "domain_keywords"]:
        if category not in result:
            result[category] = {"matched": [], "missing": []}
        
        # Get current matched JD skills
        current_matched = {match.get("jd_skill", "").lower() for match in result[category].get("matched", [])}
        
        # Add exact matches that aren't already included
        for exact_match in exact_matches.get(category, []):
            jd_skill = exact_match["jd_skill"]
            if jd_skill.lower() not in current_matched:
                result[category]["matched"].append(exact_match)
                logger.info(f"✅ [EXACT_MATCH] Added exact match: {jd_skill} → {exact_match['cv_skill']}")
        
        # Remove exact matches from missing list
        exact_jd_skills = {match["jd_skill"].lower() for match in exact_matches.get(category, [])}
        result[category]["missing"] = [
            miss for miss in result[category].get("missing", [])
            if miss.get("jd_skill", "").lower() not in exact_jd_skills
        ]
    
    return result


async def execute_skills_comparison_with_json_output(
    ai_service,
    cv_skills: Dict[str, list],
    jd_skills: Dict[str, list],
    user: Any,
    temperature: float = 0.0,
    max_tokens: int = 2500,
) -> Dict[str, Any]:
    """Execute JSON-mode comparison and return a dict with strict schema.

    Does not alter the legacy text path used by the frontend.
    """
    # Pre-process to identify obvious exact matches
    exact_matches = _identify_exact_matches(cv_skills, jd_skills)
    logger.info(f"🔍 [EXACT_MATCHES] Found {len(exact_matches)} exact matches: {exact_matches}")
    
    prompt = build_json_prompt(cv_skills, jd_skills)
    response = await ai_service.generate_response(
        prompt=prompt,
        user=user,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    raw = response.content or ""
    parsed = _extract_json_from_text(raw)

    # Enforce schema keys and sort deterministically
    result: Dict[str, Any] = {
        "technical_skills": _sort_section(parsed.get("technical_skills", {})),
        "soft_skills": _sort_section(parsed.get("soft_skills", {})),
        "domain_keywords": _sort_section(parsed.get("domain_keywords", {})),
    }
    
    # Post-process to ensure exact matches are included
    result = _ensure_exact_matches_included(result, exact_matches, cv_skills, jd_skills)
    
    return result


def _validate_comparison_results(json_result: Dict[str, Any], cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> bool:
    """
    Validate that the comparison results are mathematically correct.
    Returns True if valid, False if invalid.
    """
    try:
        # CRITICAL: Use RAW counts for validation to match display numbers
        # Get actual counts from raw skills (not deduplicated)
        cv_tech_count = len(cv_skills.get('technical_skills', []))
        cv_soft_count = len(cv_skills.get('soft_skills', []))
        cv_domain_count = len(cv_skills.get('domain_keywords', []))
        
        validation_errors = 0
        
        # Check each category
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            if category not in json_result:
                continue
                
            matched = json_result[category].get('matched', [])
            missing = json_result[category].get('missing', [])
            
            # Get raw CV count for this category (matches display)
            cv_count = len(cv_skills.get(category, []))
            
            # Critical validation: matched count cannot exceed CV count
            if len(matched) > cv_count:
                logger.warning(f"❌ [VALIDATION] {category}: matched {len(matched)} > CV count {cv_count}")
                validation_errors += 1
                
            # Flexible validation: warn but don't fail if total doesn't exactly match JD count
            # This can happen due to AI interpretation, deduplication, or similar skills being grouped
            jd_count = len(jd_skills.get(category, []))
            total_processed = len(matched) + len(missing)
            if total_processed != jd_count:
                # Only log as info, not as a hard failure
                logger.info(f"ℹ️ [VALIDATION] {category}: matched {len(matched)} + missing {len(missing)} = {total_processed} vs JD count {jd_count} (acceptable variance)")
                
                # Only fail if the variance is extreme (more than 50% off)
                if abs(total_processed - jd_count) > max(jd_count * 0.5, 3):
                    logger.warning(f"❌ [VALIDATION] {category}: extreme variance - processed {total_processed} vs expected {jd_count}")
                    validation_errors += 1
        
        # Add detailed logging to understand the mismatch
        logger.info(f"📊 [VALIDATION_DETAIL] CV Skills: Tech={cv_tech_count}, Soft={cv_soft_count}, Domain={cv_domain_count}")
        logger.info(f"📊 [VALIDATION_DETAIL] JD Skills: Tech={len(jd_skills.get('technical_skills', []))}, Soft={len(jd_skills.get('soft_skills', []))}, Domain={len(jd_skills.get('domain_keywords', []))}")
        
        if validation_errors == 0:
            logger.info("✅ [VALIDATION] Comparison results passed validation")
            return True
        else:
            logger.warning(f"❌ [VALIDATION] {validation_errors} validation error(s) found")
            return False
        
    except Exception as e:
        logger.error(f"❌ [VALIDATION] Error validating results: {e}")
        return False


def _format_json_to_text(json_result: Dict[str, Any], cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> str:
    """Convert JSON comparison result to formatted text output for backward compatibility."""
    
    # CRITICAL FIX: Use RAW skills for counts to match initial extraction numbers
    # Do NOT deduplicate here as it causes count mismatches with initial extraction
    cv_raw_counts = {
        'technical_skills': len(cv_skills.get('technical_skills', [])),
        'soft_skills': len(cv_skills.get('soft_skills', [])),
        'domain_keywords': len(cv_skills.get('domain_keywords', []))
    }
    
    jd_raw_counts = {
        'technical_skills': len(jd_skills.get('technical_skills', [])),
        'soft_skills': len(jd_skills.get('soft_skills', [])),
        'domain_keywords': len(jd_skills.get('domain_keywords', []))
    }
    
    cv_total = cv_raw_counts['technical_skills'] + cv_raw_counts['soft_skills'] + cv_raw_counts['domain_keywords']
    jd_total = jd_raw_counts['technical_skills'] + jd_raw_counts['soft_skills'] + jd_raw_counts['domain_keywords']
    
    # Calculate match statistics
    total_matched = 0
    total_missing = 0
    
    for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
        if category in json_result:
            total_matched += len(json_result[category].get('matched', []))
            total_missing += len(json_result[category].get('missing', []))
    
    # Calculate match rate as matched / total_requirements
    match_rate = round((total_matched / max(jd_total, 1)) * 100)
    
    # Calculate match rates for each category correctly
    tech_matched = len(json_result.get('technical_skills', {}).get('matched', []))
    tech_missing = len(json_result.get('technical_skills', {}).get('missing', []))
    tech_total = tech_matched + tech_missing
    tech_rate = round((tech_matched / max(tech_total, 1)) * 100) if tech_total > 0 else 0
    
    soft_matched = len(json_result.get('soft_skills', {}).get('matched', []))
    soft_missing = len(json_result.get('soft_skills', {}).get('missing', []))
    soft_total = soft_matched + soft_missing
    soft_rate = round((soft_matched / max(soft_total, 1)) * 100) if soft_total > 0 else 0
    
    domain_matched = len(json_result.get('domain_keywords', {}).get('matched', []))
    domain_missing = len(json_result.get('domain_keywords', {}).get('missing', []))
    domain_total = domain_matched + domain_missing
    domain_rate = round((domain_matched / max(domain_total, 1)) * 100) if domain_total > 0 else 0

    # Build formatted output using RAW counts to match initial extraction
    output = f"""🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: {jd_total}
Matched: {total_matched}
Missing: {total_missing}
Match Rate: {match_rate}%

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills            {cv_raw_counts['technical_skills']:2d}         {jd_raw_counts['technical_skills']:2d}         {tech_matched:2d}         {tech_missing:2d}           {tech_rate:2d}
Soft Skills                  {cv_raw_counts['soft_skills']:2d}         {jd_raw_counts['soft_skills']:2d}         {soft_matched:2d}         {soft_missing:2d}           {soft_rate:2d}
Domain Keywords             {cv_raw_counts['domain_keywords']:2d}         {jd_raw_counts['domain_keywords']:2d}         {domain_matched:2d}         {domain_missing:2d}           {domain_rate:2d}

🧠 DETAILED AI ANALYSIS
--------------------------------------------------------------------------------"""
    
    # Add detailed analysis for each category
    for category_name, category_key in [("TECHNICAL SKILLS", "technical_skills"), ("SOFT SKILLS", "soft_skills"), ("DOMAIN KEYWORDS", "domain_keywords")]:
        if category_key in json_result:
            matched = json_result[category_key].get('matched', [])
            missing = json_result[category_key].get('missing', [])
            
            output += f"\n🔹 {category_name}\n"
            
            if matched:
                output += f"  ✅ MATCHED JD REQUIREMENTS ({len(matched)} items):\n"
                for i, match in enumerate(matched, 1):
                    output += f"    {i}. JD Required: '{match.get('jd_skill', '')}'\n"
                    output += f"       → Found in CV: '{match.get('cv_equivalent', '')}'\n"
                    output += f"       💡 {match.get('reasoning', '')}\n"
            
            if missing:
                output += f"  ❌ MISSING FROM CV ({len(missing)} items):\n"
                for i, miss in enumerate(missing, 1):
                    output += f"    {i}. JD Requires: '{miss.get('jd_skill', '')}'\n"
                    output += f"       💡 {miss.get('reasoning', '')}\n"
    
    # Add input summary using RAW skills to match initial extraction display
    output += "\n📚 INPUT SUMMARY (as extracted, showing first 10 if many)\n"
    output += "CV\n"
    cv_tech_list = cv_skills.get('technical_skills', [])
    cv_soft_list = cv_skills.get('soft_skills', [])
    cv_domain_list = cv_skills.get('domain_keywords', [])
    output += f"- Technical: {', '.join(cv_tech_list[:10])}{'...' if len(cv_tech_list) > 10 else ''}\n"
    output += f"- Soft: {', '.join(cv_soft_list[:10])}{'...' if len(cv_soft_list) > 10 else ''}\n"
    output += f"- Domain: {', '.join(cv_domain_list[:10])}{'...' if len(cv_domain_list) > 10 else ''}\n\n"
    
    output += "JD\n"
    jd_tech_list = jd_skills.get('technical_skills', [])
    jd_soft_list = jd_skills.get('soft_skills', [])
    jd_domain_list = jd_skills.get('domain_keywords', [])
    output += f"- Technical: {', '.join(jd_tech_list[:10])}{'...' if len(jd_tech_list) > 10 else ''}\n"
    output += f"- Soft: {', '.join(jd_soft_list[:10])}{'...' if len(jd_soft_list) > 10 else ''}\n"
    output += f"- Domain: {', '.join(jd_domain_list[:10])}{'...' if len(jd_domain_list) > 10 else ''}\n"
    
    return output


# ====================================
# BACKWARD COMPATIBILITY WRAPPERS
# ====================================

async def run_comparison(ai_service, cv_skills: Dict[str, list], jd_skills: Dict[str, list], user: Any, temperature: float = 0.0, max_tokens: int = 3000) -> str:
    """Legacy wrapper for execute_skills_semantic_comparison - DEPRECATED"""
    logger.warning("⚠️ [DEPRECATED] run_comparison is deprecated, use execute_skills_semantic_comparison instead")
    return await execute_skills_semantic_comparison(ai_service, cv_skills, jd_skills, user, temperature, max_tokens)

async def run_comparison_json(ai_service, cv_skills: Dict[str, list], jd_skills: Dict[str, list], user: Any, temperature: float = 0.0, max_tokens: int = 2500) -> Dict[str, Any]:
    """Legacy wrapper for execute_skills_comparison_with_json_output - DEPRECATED"""
    logger.warning("⚠️ [DEPRECATED] run_comparison_json is deprecated, use execute_skills_comparison_with_json_output instead")
    return await execute_skills_comparison_with_json_output(ai_service, cv_skills, jd_skills, user, temperature, max_tokens)

