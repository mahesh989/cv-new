"""
Data Formatting Utilities - Pure Functions Only
===============================================

This module contains pure utility functions extracted from main.py
for data formatting and processing. These functions:
- Do not modify global state
- Have no side effects (except logging)
- Are deterministic for the same inputs
- Can be safely tested in isolation
"""

from typing import Dict, List, Any, Set
import json
import re


def convert_to_frontend_format(ai_result: dict) -> dict:
    """
    Convert the enhanced AI matcher result to frontend-expected format
    Maps from Python-style result to Flutter app format
    """
    try:
        # Frontend expects this structure with matched/missing per category
        formatted = {
            "matched": {},
            "missing": {},
            "match_summary": ai_result.get('match_summary', {})
        }
        
        # Map each category from AI result to frontend format
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            if category in ai_result:
                category_data = ai_result[category]
                
                # Convert matched skills with reasoning
                formatted["matched"][category] = []
                for match in category_data.get('matched', []):
                    formatted["matched"][category].append({
                        "cv_skill": match.get('cv_equivalent', ''),
                        "jd_requirement": match.get('jd_skill', ''),
                        "match_reason": match.get('reasoning', 'AI semantic match'),
                        "match_type": "semantic",  # All enhanced matches are semantic
                        "reasoning": match.get('reasoning', '')  # Extra reasoning field
                    })
                
                # Convert missing skills with reasoning
                formatted["missing"][category] = []
                for missing in category_data.get('missing', []):
                    formatted["missing"][category].append({
                        "jd_skill": missing.get('jd_skill', ''),
                        "reasoning": missing.get('reasoning', 'Not found in CV')
                    })
        
        print(f"🔄 [FORMAT] Converted AI result to frontend format")
        print(f"📊 [FORMAT] Categories: {list(formatted['matched'].keys())}")
        
        return formatted
        
    except Exception as e:
        print(f"❌ [FORMAT] Error converting format: {e}")
        # Return basic structure if conversion fails
        return {
            "matched": {"technical_skills": [], "soft_skills": [], "domain_keywords": []},
            "missing": {"technical_skills": [], "soft_skills": [], "domain_keywords": []},
            "match_summary": {"match_percentage": 0, "total_matched": 0, "total_missing": 0}
        }


def consolidate_matched_skills(result: dict) -> dict:
    """
    Remove duplicate CV skills from matched results and consolidate JD requirements.
    Each CV skill should appear only once, even if it matches multiple JD requirements.
    """
    try:
        matched = result.get('matched', {})
        consolidated_matched = {}
        
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            category_matches = matched.get(category, [])
            
            # Group by CV skill to remove duplicates
            cv_skill_groups = {}
            for match in category_matches:
                cv_skill = match.get('cv_skill', '')
                jd_requirement = match.get('jd_requirement', '')
                match_reason = match.get('match_reason', '')
                
                if cv_skill not in cv_skill_groups:
                    cv_skill_groups[cv_skill] = {
                        'cv_skill': cv_skill,
                        'jd_requirements': [],
                        'match_reasons': []
                    }
                
                cv_skill_groups[cv_skill]['jd_requirements'].append(jd_requirement)
                cv_skill_groups[cv_skill]['match_reasons'].append(match_reason)
            
            # Create consolidated matches with unique CV skills
            consolidated_category = []
            for cv_skill, group in cv_skill_groups.items():
                # Use the first JD requirement and combine match reasons if multiple
                primary_jd = group['jd_requirements'][0] if group['jd_requirements'] else ''
                
                if len(group['jd_requirements']) > 1:
                    # Multiple JD requirements matched to this CV skill
                    combined_reason = f"Matches {len(group['jd_requirements'])} requirements: {', '.join(group['jd_requirements'])}"
                else:
                    combined_reason = group['match_reasons'][0] if group['match_reasons'] else ''
                
                consolidated_category.append({
                    'cv_skill': cv_skill,
                    'jd_requirement': primary_jd,
                    'match_reason': combined_reason
                })
            
            consolidated_matched[category] = consolidated_category
        
        # Update the result with consolidated matches
        result['matched'] = consolidated_matched
        
        # Recalculate match summary with unique CV skills
        total_unique_matches = sum(len(consolidated_matched[cat]) for cat in consolidated_matched)
        total_jd_requirements = result.get('match_summary', {}).get('total_jd_requirements', 0)
        
        if total_jd_requirements > 0:
            match_percentage = round((total_unique_matches / total_jd_requirements) * 100)
        else:
            match_percentage = 0
        
        result['match_summary']['total_matches'] = total_unique_matches
        result['match_summary']['match_percentage'] = match_percentage
        
        print(f"✨ [Consolidation] Removed duplicates: {total_unique_matches} unique CV skills match {total_jd_requirements} JD requirements")
        
        return result
        
    except Exception as e:
        print(f"❌ [Consolidation] Error consolidating skills: {e}")
        return result  # Return original result if consolidation fails


def validate_comparison_completeness(result: dict, jd_skills: dict, total_jd_requirements: int) -> dict:
    """
    Validates if all JD requirements are accounted for in the comparison result.
    Returns detailed information about what's missing.
    """
    # Collect all JD requirements that should be processed
    all_jd_requirements = []
    for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
        all_jd_requirements.extend(jd_skills.get(category, []))
    
    print(f"🔍 [VALIDATION] All JD requirements to check: {all_jd_requirements}")
    
    # Collect matched requirements
    matched_jd_requirements = set()
    matched_section = result.get('matched', {})
    for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
        for match in matched_section.get(category, []):
            if isinstance(match, dict):
                matched_jd_requirements.add(match.get('jd_requirement'))
            else:
                print(f"⚠️ [VALIDATION] Unexpected match format: {match}")
    
    # Collect missing requirements  
    missing_from_result = []
    missing_section = result.get('missing', {})
    for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
        missing_from_result.extend(missing_section.get(category, []))
    
    # Find requirements that are completely unaccounted for
    accounted_requirements = matched_jd_requirements.union(set(missing_from_result))
    missing_jd_requirements = [req for req in all_jd_requirements if req not in accounted_requirements]
    
    processed_count = len(matched_jd_requirements) + len(missing_from_result)
    
    print(f"🔍 [VALIDATION] Matched: {len(matched_jd_requirements)}, Missing in result: {len(missing_from_result)}, Unaccounted: {len(missing_jd_requirements)}")
    print(f"🔍 [VALIDATION] Unaccounted requirements: {missing_jd_requirements}")

    if missing_jd_requirements:
        return {
            'valid': False,
            'message': f"Missing JD requirements: {', '.join(missing_jd_requirements)}",
            'missing_count': len(missing_jd_requirements),
            'missing_requirements': missing_jd_requirements,
            'processed_count': processed_count
        }
    else:
        return {
            'valid': True,
            'message': "All JD requirements accounted for.",
            'processed_count': processed_count,
            'missing_requirements': []
        }


def parse_json_from_response(response_text: str) -> dict:
    """
    Extract JSON from an AI response that may contain extra text
    Returns parsed JSON or raises ValueError if no valid JSON found
    """
    import re
    import json
    
    # Try to find JSON in the response
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        return json.loads(json_str)
    else:
        # Try to parse the whole response
        return json.loads(response_text)


def create_empty_skill_structure() -> dict:
    """
    Create an empty skill comparison structure for fallback cases
    """
    return {
        "matched": {"technical_skills": [], "soft_skills": [], "domain_keywords": []},
        "missing": {"technical_skills": [], "soft_skills": [], "domain_keywords": []},
        "match_summary": {"match_percentage": 0, "total_matched": 0, "total_missing": 0}
    }


def calculate_match_percentage(total_matched: int, total_missing: int) -> float:
    """
    Calculate match percentage from totals
    Returns 0 if total is 0 to avoid division by zero
    """
    total = total_matched + total_missing
    if total > 0:
        return round((total_matched / total) * 100, 1)
    return 0.0


def extract_skill_list_from_text(label: str, text: str) -> List[str]:
    """
    Extract a skill list from formatted AI response text
    Returns cleaned list of skills or ["N/A"] if not found
    """
    pattern = rf"{label}:\s*(.*?)(?=\n[A-Z][^:]*:|$)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        items = [w.strip() for w in match.group(1).split(",") if w.strip()]
        # Filter out obvious artifacts
        valid_items = []
        for item in items:
            item = item.strip().strip('"').strip("'")
            if (item and 
                len(item) > 1 and 
                item.lower() not in ['n/a', 'none', 'not applicable', 'not found']):
                valid_items.append(item)
        return valid_items if valid_items else ["N/A"]
    return ["N/A"]
