"""
Skill Normalization Utility

Normalizes extracted skills to improve matching accuracy by:
- Extracting base skills from parenthetical variations
- Removing version numbers
- Handling common variations

Examples:
- "SQL (PostgreSQL, MySQL)" → base: "SQL", full: "SQL (PostgreSQL, MySQL)"
- "Python 3.x" → base: "Python", full: "Python 3.x"
- "Power BI" → base: "Power BI", full: "Power BI"
"""

import re
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


def normalize_skill(skill: str) -> Tuple[str, str]:
    """
    Extract base skill and preserve full skill.
    
    Args:
        skill: Original skill string (e.g., "SQL (PostgreSQL, MySQL)")
        
    Returns:
        Tuple of (base_skill, full_skill)
        
    Examples:
        - "SQL (PostgreSQL, MySQL)" → ("SQL", "SQL (PostgreSQL, MySQL)")
        - "Python 3.x" → ("Python", "Python 3.x")
        - "Power BI" → ("Power BI", "Power BI")
        - "Data Warehousing" → ("Data Warehousing", "Data Warehousing")
    """
    if not skill or not isinstance(skill, str):
        return ("", "")
    
    skill = skill.strip()
    if not skill:
        return ("", "")
    
    # Extract base skill before parentheses
    # Example: "SQL (PostgreSQL, MySQL)" → "SQL"
    if '(' in skill:
        base = skill.split('(')[0].strip()
        # If base is empty after splitting, use full skill
        if base:
            return (base, skill)
    
    # Remove version numbers (e.g., "Python 3.x", "Python 3.9", "Python 3")
    # Pattern matches: space + digits + optional .x or .digit
    version_pattern = r'\s+\d+(?:\.\d+)?(?:\.x)?$'
    base = re.sub(version_pattern, '', skill).strip()
    
    # If normalization removed everything, use original
    if not base:
        base = skill
    
    return (base, skill)


def normalize_skill_list(skills: List[str]) -> List[Dict[str, str]]:
    """
    Normalize a list of skills, preserving both base and full versions.
    
    Args:
        skills: List of skill strings
        
    Returns:
        List of dictionaries with 'base', 'full', and 'normalized' keys
        - 'base': Normalized base skill for matching
        - 'full': Original full skill for display
        - 'normalized': Lowercase base skill for case-insensitive matching
    """
    normalized = []
    seen_bases = set()  # Track unique base skills to avoid duplicates
    
    for skill in skills:
        if not skill or not isinstance(skill, str):
            continue
        
        base, full = normalize_skill(skill)
        normalized_base = base.lower().strip()
        
        # Skip if we've already seen this base skill (deduplication)
        if normalized_base and normalized_base not in seen_bases:
            seen_bases.add(normalized_base)
            normalized.append({
                "base": base,
                "full": full,
                "normalized": normalized_base
            })
        elif normalized_base in seen_bases:
            # Log duplicate base skills
            logger.debug(f"🔍 [NORMALIZER] Skipping duplicate base skill: {full} (base: {base})")
    
    return normalized


def get_base_skills(normalized_skills: List[Dict[str, str]]) -> List[str]:
    """
    Extract just the base skills from normalized skill list.
    
    Args:
        normalized_skills: List of normalized skill dictionaries
        
    Returns:
        List of base skill strings
    """
    return [skill["base"] for skill in normalized_skills if skill.get("base")]


def get_full_skills(normalized_skills: List[Dict[str, str]]) -> List[str]:
    """
    Extract just the full skills from normalized skill list.
    
    Args:
        normalized_skills: List of normalized skill dictionaries
        
    Returns:
        List of full skill strings
    """
    return [skill["full"] for skill in normalized_skills if skill.get("full")]


def normalize_skills_dict(skills_dict: Dict[str, List[str]]) -> Dict[str, Dict[str, List]]:
    """
    Normalize all skills in a skills dictionary.
    
    Args:
        skills_dict: Dictionary with 'technical_skills', 'soft_skills', 'domain_keywords'
        
    Returns:
        Dictionary with normalized skills and original lists:
        {
            'technical_skills': {
                'normalized': [...],  # List of normalized dicts
                'base': [...],        # List of base strings
                'full': [...]         # List of full strings
            },
            ...
        }
    """
    result = {}
    
    for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
        skills = skills_dict.get(category, [])
        normalized = normalize_skill_list(skills)
        
        result[category] = {
            'normalized': normalized,
            'base': get_base_skills(normalized),
            'full': get_full_skills(normalized)
        }
    
    return result


def find_matching_base_skill(skill: str, normalized_skills: List[Dict[str, str]]) -> Optional[str]:
    """
    Find a matching base skill in a normalized list.
    
    Args:
        skill: Skill to match (e.g., "SQL")
        normalized_skills: List of normalized skill dictionaries
        
    Returns:
        Matching base skill if found, None otherwise
    """
    skill_base, _ = normalize_skill(skill)
    skill_normalized = skill_base.lower().strip()
    
    for normalized in normalized_skills:
        if normalized.get("normalized") == skill_normalized:
            return normalized.get("base")
    
    return None

