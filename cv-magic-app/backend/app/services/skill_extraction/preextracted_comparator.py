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


def build_prompt(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> str:
    """Return the exact comparison prompt with lists injected verbatim."""
    return f"""
Compare these pre-extracted CV skills against pre-extracted JD requirements using intelligent semantic matching.

CV SKILLS:
Technical: {cv_skills.get('technical_skills', [])}
Soft: {cv_skills.get('soft_skills', [])}
Domain: {cv_skills.get('domain_keywords', [])}

JD REQUIREMENTS:
Technical: {jd_skills.get('technical_skills', [])}
Soft: {jd_skills.get('soft_skills', [])}
Domain: {jd_skills.get('domain_keywords', [])}

**RULES:**
- Compare only the provided lists (no external knowledge)
- Use semantic matching: "Python programming" → "Python" = ✅ match
- "Leadership" → "Team leadership" = ✅ match  
- "Data analysis" → "Analytical skills" = ✅ match
- Only mark as missing if no semantic equivalent exists
- Provide brief, clear reasoning

**OUTPUT FORMAT (TEXT ONLY):**
🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: X
Matched: Y
Missing: Z
Match Rate: P%

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills            TT         JT         MT         MS            RP
Soft Skills                  TT         JT         MT         MS            RP
Domain Keywords             TT         JT         MT         MS            RP

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
    """Execute the comparison prompt using the centralized AI service and return raw formatted text."""
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
    """Lowercase, strip, dedupe, sort, and truncate to guard tokens deterministically."""
    if not values:
        return []
    seen = set()
    normalized: List[str] = []
    for v in values:
        if not isinstance(v, str):
            continue
        s = re.sub(r"\s+", " ", v.strip().lower())
        if s and s not in seen:
            seen.add(s)
            normalized.append(s)
    normalized.sort()
    if len(normalized) > max_items:
        return normalized[:max_items]
    return normalized


def _prepare_inputs(cv_skills: Dict[str, list], jd_skills: Dict[str, list], max_items: int = 200) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Prepare normalized and truncated inputs for prompt injection."""
    cv = {
        "technical_skills": _normalize_list(cv_skills.get("technical_skills", []), max_items),
        "soft_skills": _normalize_list(cv_skills.get("soft_skills", []), max_items),
        "domain_keywords": _normalize_list(cv_skills.get("domain_keywords", []), max_items),
    }
    jd = {
        "technical_skills": _normalize_list(jd_skills.get("technical_skills", []), max_items),
        "soft_skills": _normalize_list(jd_skills.get("soft_skills", []), max_items),
        "domain_keywords": _normalize_list(jd_skills.get("domain_keywords", []), max_items),
    }
    return cv, jd


def build_json_prompt(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> str:
    """Return a strict JSON-only comparison prompt with deterministic guidance."""
    cv, jd = _prepare_inputs(cv_skills, jd_skills)
    return (
        "You are a precise comparator. Compare ONLY the provided pre-extracted lists.\n"
        "Normalize mentally as lowercase and singular where helpful, and use simple semantic equivalence (e.g., 'data analysis' ~ 'analytical skills').\n"
        "DO NOT invent items.\n\n"
        "INPUT LISTS (already normalized and truncated, sorted alphabetically):\n"
        f"CV.technical_skills = {cv['technical_skills']}\n"
        f"CV.soft_skills = {cv['soft_skills']}\n"
        f"CV.domain_keywords = {cv['domain_keywords']}\n\n"
        f"JD.technical_skills = {jd['technical_skills']}\n"
        f"JD.soft_skills = {jd['soft_skills']}\n"
        f"JD.domain_keywords = {jd['domain_keywords']}\n\n"
        "MATCHING RULES:\n"
        "- exact: identical string after normalization\n"
        "- synonym: common phrasing variants (e.g., 'data analysis' vs 'analytical skills')\n"
        "- context: closely related phrasing that clearly implies the JD item\n"
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


