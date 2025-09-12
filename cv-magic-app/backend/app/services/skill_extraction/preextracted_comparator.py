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

from typing import Dict, List, Tuple, Any
import json
import re
import logging

logger = logging.getLogger(__name__)


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
- Use semantic matching: "Python programming" → "Python" = ✅ match
- "Leadership" → "Team leadership" = ✅ match  
- "Data analysis" → "Analytical skills" = ✅ match
- Only mark as missing if no semantic equivalent exists
- Provide brief, clear reasoning
- IMPORTANT: Each skill is counted only once (no duplicates across categories)

**OUTPUT FORMAT (TEXT ONLY):**
🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: {jd_tech_count + jd_soft_count + jd_domain_count}
Matched: [Y - must be ≤ {cv_tech_count + cv_soft_count + cv_domain_count}]
Missing: [Z]
Match Rate: [P%]

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills            {cv_tech_count:2d}         {jd_tech_count:2d}         [MT]         [MS]            [RP]
Soft Skills                  {cv_soft_count:2d}         {jd_soft_count:2d}         [MT]         [MS]            [RP]
Domain Keywords             {cv_domain_count:2d}         {jd_domain_count:2d}         [MT]         [MS]            [RP]

🧠 DETAILED AI ANALYSIS
--------------------------------------------------------------------------------

🔹 TECHNICAL SKILLS
  ✅ MATCHED JD REQUIREMENTS (K items):
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning
  ❌ MISSING FROM CV (M items):
    1. JD Requires: '...'
       💡 brief reason why not found

🔹 SOFT SKILLS
  ✅ MATCHED JD REQUIREMENTS (K items):
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning
  ❌ MISSING FROM CV (M items):
    1. JD Requires: '...'
       💡 brief reason why not found

🔹 DOMAIN KEYWORDS
  ✅ MATCHED JD REQUIREMENTS (K items):
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning
  ❌ MISSING FROM CV (M items):
    1. JD Requires: '...'
       💡 brief reason why not found

📚 INPUT SUMMARY (normalized, truncated if long)
CV
- Technical: [comma-separated]
- Soft: [comma-separated]
- Domain: [comma-separated]

JD
- Technical: [comma-separated]
- Soft: [comma-separated]
- Domain: [comma-separated]

Return only this formatted analysis.
"""


async def run_comparison(ai_service, cv_skills: Dict[str, list], jd_skills: Dict[str, list], temperature: float = 0.3, max_tokens: int = 3000) -> str:
    """Execute the comparison prompt using the centralized AI service and return formatted text."""
    try:
        # Use JSON mode for consistent structured output
        json_result = await run_comparison_json(ai_service, cv_skills, jd_skills, temperature, max_tokens)
        
        # Validate the results are mathematically correct
        if not _validate_comparison_results(json_result, cv_skills, jd_skills):
            logger.warning("⚠️ [COMPARISON] JSON results failed validation, falling back to text mode")
            # Fallback to text-based comparison if validation fails
            prompt = build_prompt(cv_skills, jd_skills)
            response = await ai_service.generate_response(
                prompt=prompt,
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
            'terraform', 'ansible', 'chef', 'puppet', 'splunk', 'datadog', 'newrelic'
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
    """Return a strict JSON-only comparison prompt with deterministic guidance."""
    cv, jd = _prepare_inputs(cv_skills, jd_skills)
    
    # Get exact counts for validation
    cv_tech_count = len(cv['technical_skills'])
    cv_soft_count = len(cv['soft_skills'])
    cv_domain_count = len(cv['domain_keywords'])
    jd_tech_count = len(jd['technical_skills'])
    jd_soft_count = len(jd['soft_skills'])
    jd_domain_count = len(jd['domain_keywords'])
    
    return (
        "You are a precise comparator. Compare ONLY the provided pre-extracted lists.\n"
        "Normalize mentally as lowercase and singular where helpful, and use simple semantic equivalence (e.g., 'data analysis' ~ 'analytical skills').\n"
        "DO NOT invent items.\n\n"
        "INPUT LISTS (already normalized and truncated, sorted alphabetically):\n"
        f"CV.technical_skills ({cv_tech_count} items) = {cv['technical_skills']}\n"
        f"CV.soft_skills ({cv_soft_count} items) = {cv['soft_skills']}\n"
        f"CV.domain_keywords ({cv_domain_count} items) = {cv['domain_keywords']}\n\n"
        f"JD.technical_skills ({jd_tech_count} items) = {jd['technical_skills']}\n"
        f"JD.soft_skills ({jd_soft_count} items) = {jd['soft_skills']}\n"
        f"JD.domain_keywords ({jd_domain_count} items) = {jd['domain_keywords']}\n\n"
        "CRITICAL COUNTING CONSTRAINTS:\n"
        f"- CV has {cv_tech_count} technical skills, {cv_soft_count} soft skills, {cv_domain_count} domain keywords\n"
        f"- JD has {jd_tech_count} technical skills, {jd_soft_count} soft skills, {jd_domain_count} domain keywords\n"
        f"- You CANNOT match more than {cv_tech_count} technical skills, {cv_soft_count} soft skills, {cv_domain_count} domain keywords\n"
        f"- Maximum possible matches: {cv_tech_count + cv_soft_count + cv_domain_count} total\n\n"
        "MATCHING RULES:\n"
        "- exact: identical string after normalization\n"
        "- synonym: common phrasing variants (e.g., 'data analysis' vs 'analytical skills')\n"
        "- context: closely related phrasing that clearly implies the JD item\n"
        "- IMPORTANT: Each skill is counted only once (no duplicates across categories)\n"
        "Only mark as missing if no suitable equivalent exists.\n\n"
        "OUTPUT (JSON ONLY, no prose, no markdown):\n"
        "{\n"
        "  \"technical_skills\": {\n"
        "    \"matched\": [\n"
        "      {\n"
        "        \"jd_skill\": \"exact JD requirement\",\n"
        "        \"cv_equivalent\": \"matching CV skill(s)\",\n"
        "        \"reasoning\": \"brief explanation of match\"\n"
        "      }\n"
        "    ],\n"
        "    \"missing\": [\n"
        "      { \"jd_skill\": \"...\", \"reasoning\": \"why not found\" }\n"
        "    ]\n"
        "  },\n"
        "  \"soft_skills\": { \"matched\": [], \"missing\": [] },\n"
        "  \"domain_keywords\": { \"matched\": [], \"missing\": [] }\n"
        "}\n"
        "Ensure arrays are sorted by jd_skill ascending for determinism."
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


async def run_comparison_json(
    ai_service,
    cv_skills: Dict[str, list],
    jd_skills: Dict[str, list],
    temperature: float = 0.2,
    max_tokens: int = 2500,
) -> Dict[str, Any]:
    """Execute JSON-mode comparison and return a dict with strict schema.

    Does not alter the legacy text path used by the frontend.
    """
    prompt = build_json_prompt(cv_skills, jd_skills)
    response = await ai_service.generate_response(
        prompt=prompt,
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
    return result


def _validate_comparison_results(json_result: Dict[str, Any], cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> bool:
    """
    Validate that the comparison results are mathematically correct.
    Returns True if valid, False if invalid.
    """
    try:
        cv_dedup = _deduplicate_skills(cv_skills)
        jd_dedup = _deduplicate_skills(jd_skills)
        
        # Get actual counts
        cv_tech_count = len(cv_dedup.get('technical_skills', []))
        cv_soft_count = len(cv_dedup.get('soft_skills', []))
        cv_domain_count = len(cv_dedup.get('domain_keywords', []))
        
        # Check each category
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            if category not in json_result:
                continue
                
            matched = json_result[category].get('matched', [])
            missing = json_result[category].get('missing', [])
            
            # Get CV count for this category
            cv_count = len(cv_dedup.get(category, []))
            
            # Validate: matched count cannot exceed CV count
            if len(matched) > cv_count:
                logger.warning(f"❌ [VALIDATION] {category}: matched {len(matched)} > CV count {cv_count}")
                return False
                
            # Validate: total (matched + missing) should equal JD count
            jd_count = len(jd_dedup.get(category, []))
            total_processed = len(matched) + len(missing)
            if total_processed != jd_count:
                logger.warning(f"❌ [VALIDATION] {category}: matched {len(matched)} + missing {len(missing)} = {total_processed} ≠ JD count {jd_count}")
                return False
        
        logger.info("✅ [VALIDATION] Comparison results are mathematically correct")
        return True
        
    except Exception as e:
        logger.error(f"❌ [VALIDATION] Error validating results: {e}")
        return False


def _format_json_to_text(json_result: Dict[str, Any], cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> str:
    """Convert JSON comparison result to formatted text output for backward compatibility."""
    
    # Calculate totals
    cv_dedup = _deduplicate_skills(cv_skills)
    jd_dedup = _deduplicate_skills(jd_skills)
    
    cv_total = len(cv_dedup['technical_skills']) + len(cv_dedup['soft_skills']) + len(cv_dedup['domain_keywords'])
    jd_total = len(jd_dedup['technical_skills']) + len(jd_dedup['soft_skills']) + len(jd_dedup['domain_keywords'])
    
    # Calculate match statistics
    total_matched = 0
    total_missing = 0
    
    for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
        if category in json_result:
            total_matched += len(json_result[category].get('matched', []))
            total_missing += len(json_result[category].get('missing', []))
    
    match_rate = round((total_matched / (total_matched + total_missing)) * 100) if (total_matched + total_missing) > 0 else 0
    
    # Build formatted output
    output = f"""🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: {total_matched + total_missing}
Matched: {total_matched}
Missing: {total_missing}
Match Rate: {match_rate}%

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills            {len(cv_dedup['technical_skills']):2d}         {len(jd_dedup['technical_skills']):2d}         {len(json_result.get('technical_skills', {}).get('matched', [])):2d}         {len(json_result.get('technical_skills', {}).get('missing', [])):2d}           {round((len(json_result.get('technical_skills', {}).get('matched', [])) / (len(json_result.get('technical_skills', {}).get('matched', [])) + len(json_result.get('technical_skills', {}).get('missing', []))) * 100) if (len(json_result.get('technical_skills', {}).get('matched', [])) + len(json_result.get('technical_skills', {}).get('missing', []))) > 0 else 0):2d}
Soft Skills                  {len(cv_dedup['soft_skills']):2d}         {len(jd_dedup['soft_skills']):2d}         {len(json_result.get('soft_skills', {}).get('matched', [])):2d}         {len(json_result.get('soft_skills', {}).get('missing', [])):2d}           {round((len(json_result.get('soft_skills', {}).get('matched', [])) / (len(json_result.get('soft_skills', {}).get('matched', [])) + len(json_result.get('soft_skills', {}).get('missing', []))) * 100) if (len(json_result.get('soft_skills', {}).get('matched', [])) + len(json_result.get('soft_skills', {}).get('missing', []))) > 0 else 0):2d}
Domain Keywords             {len(cv_dedup['domain_keywords']):2d}         {len(jd_dedup['domain_keywords']):2d}         {len(json_result.get('domain_keywords', {}).get('matched', [])):2d}         {len(json_result.get('domain_keywords', {}).get('missing', [])):2d}           {round((len(json_result.get('domain_keywords', {}).get('matched', [])) / (len(json_result.get('domain_keywords', {}).get('matched', [])) + len(json_result.get('domain_keywords', {}).get('missing', []))) * 100) if (len(json_result.get('domain_keywords', {}).get('matched', [])) + len(json_result.get('domain_keywords', {}).get('missing', []))) > 0 else 0):2d}

🧠 DETAILED AI ANALYSIS
--------------------------------------------------------------------------------
"""
    
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
    
    # Add input summary
    output += "\n📚 INPUT SUMMARY (normalized, truncated if long)\n"
    output += "CV\n"
    output += f"- Technical: {', '.join(cv_dedup['technical_skills'][:10])}{'...' if len(cv_dedup['technical_skills']) > 10 else ''}\n"
    output += f"- Soft: {', '.join(cv_dedup['soft_skills'][:10])}{'...' if len(cv_dedup['soft_skills']) > 10 else ''}\n"
    output += f"- Domain: {', '.join(cv_dedup['domain_keywords'][:10])}{'...' if len(cv_dedup['domain_keywords']) > 10 else ''}\n\n"
    
    output += "JD\n"
    output += f"- Technical: {', '.join(jd_dedup['technical_skills'][:10])}{'...' if len(jd_dedup['technical_skills']) > 10 else ''}\n"
    output += f"- Soft: {', '.join(jd_dedup['soft_skills'][:10])}{'...' if len(jd_dedup['soft_skills']) > 10 else ''}\n"
    output += f"- Domain: {', '.join(jd_dedup['domain_keywords'][:10])}{'...' if len(jd_dedup['domain_keywords']) > 10 else ''}\n"
    
    return output


