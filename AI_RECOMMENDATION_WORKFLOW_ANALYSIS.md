# AI Recommendation Generation Workflow - Complete Analysis

## Overview
This document provides a comprehensive analysis of the AI recommendation generation workflow, including code snippets for each component and identified bugs.

---

## 1. CV Skills Extraction Logic

### Location
- **Main Service**: `cv-magic-app/backend/app/services/skill_extraction/skill_extraction_service.py`
- **Parser**: `cv-magic-app/backend/app/services/skill_extraction/response_parser.py`
- **Prompts**: `cv-magic-app/backend/app/services/skill_extraction/prompt_templates.py`

### Code Snippet: CV Skills Extraction

```python
# From skill_extraction_service.py, lines 224-276
async def _extract_cv_skills(self, db: Session, cv_data: Dict, force_refresh: bool) -> Dict:
    """Extract skills from CV with caching"""
    cv_record = cv_data["record"]
    cv_text = cv_data["text"]
    
    # Check cache first (unless force_refresh)
    if not force_refresh and cv_record.technical_skills:
        logger.info("📂 Using cached CV skills")
        return {
            "soft_skills": json.loads(cv_record.soft_skills or "[]"),
            "technical_skills": json.loads(cv_record.technical_skills or "[]"),
            "domain_keywords": json.loads(cv_record.domain_keywords or "[]"),
            "from_cache": True
        }
    
    # Extract skills using AI
    prompt = self.prompts.get_skill_extraction_template("CV", cv_text)
    system_prompt = self.prompts.get_system_prompt("CV")
    
    # Call AI service
    ai_response = await ai_service.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.0,
        max_tokens=2000
    )
    
    # Parse response
    parsed_skills = self.parser.parse_response(ai_response.content, "CV")
    
    return {
        "soft_skills": parsed_skills["soft_skills"],
        "technical_skills": parsed_skills["technical_skills"],
        "domain_keywords": parsed_skills["domain_keywords"],
        "from_cache": False
    }
```

### How It Handles Variations

**From `prompt_templates.py` (lines 143-175):**
- **Compound Listings**: "Python, SQL, and R" → Extracted as separate items: ["Python", "SQL", "R"]
- **Tools with Versions**: "Python 3.x" → Extracted as "Python" (version removed)
- **Alternative Phrasings**: "Power BI or Tableau" → Both extracted: ["Power BI", "Tableau"]
- **Multi-word Tools**: "Power BI" kept as single extraction (not split)

**⚠️ BUG IDENTIFIED**: The prompt says to extract verbatim, but there's NO normalization/stemming applied. 
- "SQL (PostgreSQL, MySQL)" in CV → Extracted as: `["SQL (PostgreSQL, MySQL)"]` (entire string)
- "SQL" in JD → Extracted as: `["SQL"]`
- These won't match because they're different strings!

### Normalization/Stemming

**❌ NO NORMALIZATION APPLIED**: The extraction is verbatim only. The prompt explicitly states:
```
1. VERBATIM EXTRACTION ONLY
   ✓ Copy EXACT phrases from the text
   ✗ Do NOT use synonyms, paraphrasing, or your interpretation
```

**Result**: "SQL (PostgreSQL, MySQL)" and "SQL" are treated as completely different skills.

---

## 2. JD Skills Extraction Logic

### Location
- **Same service as CV**: `skill_extraction_service.py` (lines 278-317)
- **Same parser**: `response_parser.py`

### Code Snippet: JD Skills Extraction

```python
# From skill_extraction_service.py, lines 278-317
async def _extract_jd_skills(self, db: Session, jd_data: Dict, force_refresh: bool) -> Dict:
    """Extract skills from JD with caching"""
    jd_record = jd_data["record"]
    jd_text = jd_data["text"]
    
    # Check cache first
    if not force_refresh and jd_record.matched_skills:
        logger.info("📂 Using cached JD skills")
        cached_data = json.loads(jd_record.matched_skills or "{}")
        return {
            "soft_skills": cached_data.get("soft_skills", []),
            "technical_skills": cached_data.get("technical_skills", []),
            "domain_keywords": cached_data.get("domain_keywords", []),
            "from_cache": True
        }
    
    # Extract skills using AI (same process as CV)
    prompt = self.prompts.get_skill_extraction_template("Job Description", jd_text)
    system_prompt = self.prompts.get_system_prompt("Job Description")
    
    ai_response = await ai_service.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.0,
        max_tokens=2000
    )
    
    parsed_skills = self.parser.parse_response(ai_response.content, "JD")
    
    return {
        "soft_skills": parsed_skills["soft_skills"],
        "technical_skills": parsed_skills["technical_skills"],
        "domain_keywords": parsed_skills["domain_keywords"],
        "from_cache": False
    }
```

### Expected Format

The AI expects **any format** (comma-separated, bullet points, paragraphs). The prompt handles:
- Comma-separated: "Python, SQL, Tableau"
- Bullet points: "- Python\n- SQL\n- Tableau"
- Paragraphs: "Experience with Python, SQL, and Tableau required"

**Same verbatim extraction issue applies to JD** - no normalization.

---

## 3. Keyword Matching Logic

### Location
- **Main Comparator**: `cv-magic-app/backend/app/services/skill_extraction/preextracted_comparator.py`
- **Semantic Mapping**: Lines 28-240 (SEMANTIC_SKILL_MAPPING)

### Code Snippet: Matching Logic

```python
# From preextracted_comparator.py, lines 308-328
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
```

### Semantic Mapping for SQL

```python
# From preextracted_comparator.py, lines 128-135
"sql": [
    "sql",
    "database management",
    "database querying",
    "relational databases",
    "postgresql",
    "mysql"
],
```

### Why "SQL (PostgreSQL, MySQL)" Doesn't Match "SQL"

**The Problem:**
1. CV has: `"SQL (PostgreSQL, MySQL)"` (verbatim extraction)
2. JD has: `"SQL"` (verbatim extraction)
3. Matching logic checks:
   - `jd_normalized = "sql"` (lowercase)
   - `cv_normalized = "sql (postgresql, mysql)"` (lowercase)
   - Checks if `"sql"` in `"sql (postgresql, mysql)"` → ✅ **YES, this should match!**

**But wait...** The matching happens in the AI comparison, not in the exact match logic. Let's check the exact match logic:

```python
# From preextracted_comparator.py, lines 845-872
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
            if jd_normalized in cv_list:  # ❌ EXACT MATCH ONLY
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
```

**❌ BUG**: The exact match logic uses `if jd_normalized in cv_list`, which requires **exact string match**.
- `"sql"` is NOT in `["sql (postgresql, mysql)"]` (exact match fails)
- Falls through to AI matching, which may or may not catch it

### Why "Power BI" and "Tableau" Appear in Both Matched and Missing

**The Problem**: The AI comparison prompt has strict rules, but the parsing logic that extracts matched/missing from the AI response has bugs.

**From `ats_recommendation_service.py`, lines 340-385 (match summary extraction):**

```python
# Extract matched skills - handle BOTH formats
if ("→ Found in CV:" in line or 
    "Found in CV:" in line or 
    "CV Has:" in line or 
    "CV has:" in line):
    try:
        if "'" in line:
            parts = line.split("'")
            if len(parts) >= 2:
                skill = parts[1].strip()
                if skill and skill not in match_summary["by_category"][current_category]["matched"]:
                    match_summary["by_category"][current_category]["matched"].append(skill)
```

**Extract missing skills:**
```python
if ("JD Requires:" in line or "JD Required:" in line):
    try:
        if "'" in line:
            parts = line.split("'")
            if len(parts) >= 2:
                skill = parts[1].strip()
                
                # Only add to missing if it's NOT in the matched section
                in_missing_section = False
                for j in range(max(0, i-5), i):
                    if "MISSING FROM CV" in lines[j].upper() or "❌" in lines[j]:
                        in_missing_section = True
                        break
                
                # If we're in missing section OR skill not in matched, add to missing
                if in_missing_section or skill not in match_summary["by_category"][current_category]["matched"]:
                    if skill and skill not in match_summary["by_category"][current_category]["missing"]:
                        match_summary["by_category"][current_category]["missing"].append(skill)
```

**❌ BUG**: The logic checks `skill not in match_summary["by_category"][current_category]["matched"]`, but:
1. The AI response may list the same skill in BOTH sections (matched AND missing)
2. The parsing happens line-by-line, so if "Power BI" appears in matched section first, then in missing section, it gets added to both
3. The check `skill not in match_summary[...]["matched"]` happens AFTER the skill is already in matched, so it fails to prevent duplicate

**Root Cause**: The AI comparison output format is inconsistent, and the parser doesn't properly deduplicate.

---

## 4. Already-in-CV Filtering

### Location
- **Filtering Logic**: `cv-magic-app/backend/app/services/ats_recommendation_service.py`
- **Methods**: `_extract_existing_cv_keywords()` (lines 655-692), `_keyword_exists_in_cv()` (lines 734-767)

### Code Snippet: Already-in-CV Filtering

```python
# From ats_recommendation_service.py, lines 532-653
def _classify_keywords(self, missing_keywords: Dict[str, List[str]], 
                      cv_skills: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Classify missing keywords into tiers based on CV tailoring framework.
    NOW WITH PRE-FILTERING: Removes keywords already present in the latest CV.
    """
    # STEP 1: Extract existing keywords from latest CV (including tailored CV if it exists)
    existing_keywords_lower = self._extract_existing_cv_keywords()
    
    # STEP 2: Filter missing keywords to exclude those already in CV
    filtered_missing = {}
    already_present = {}
    
    for category, keywords in missing_keywords.items():
        filtered_missing[category] = []
        already_present[category] = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Check if keyword or any variation exists in CV
            if self._keyword_exists_in_cv(keyword_lower, existing_keywords_lower):
                already_present[category].append(keyword)
                logger.info(f"🔍 [KEYWORD_FILTER] Skipping '{keyword}' - already in CV")
            else:
                filtered_missing[category].append(keyword)
    
    # ... classification continues with filtered_missing
```

### Keyword Existence Check

```python
# From ats_recommendation_service.py, lines 734-767
def _keyword_exists_in_cv(self, keyword: str, cv_keywords: set) -> bool:
    """
    Check if a keyword exists in CV keywords (with fuzzy matching).
    Handles variations like "python" vs "python programming", "sql" vs "structured query language".
    """
    keyword_lower = keyword.lower()
    
    # Direct match
    if keyword_lower in cv_keywords:
        return True
    
    # Check if keyword is part of any CV keyword (e.g., "python" in "python programming")
    for cv_kw in cv_keywords:
        if keyword_lower in cv_kw or cv_kw in keyword_lower:
            # Only match if significant overlap (not just "a" in "data")
            if len(keyword_lower) > 3 or len(cv_kw) > 3:
                return True
    
    # Check common variations
    variations = {
        'python': ['python programming', 'python development', 'py'],
        'sql': ['structured query language', 'mysql', 'postgresql', 'sql server'],
        'javascript': ['js', 'javascript programming', 'node', 'nodejs'],
        'data analysis': ['data analytics', 'analyzing data', 'analytical'],
        'machine learning': ['ml', 'ai', 'artificial intelligence'],
        'project management': ['pm', 'project coordination', 'managed projects'],
    }
    
    for base, vars in variations.items():
        if keyword_lower == base or keyword_lower in vars:
            if base in cv_keywords or any(v in cv_keywords for v in vars):
                return True
    
    return False
```

### Why It Detects "Power BI" and "Tableau" But Misses "SQL" and "Data Warehousing"

**For "Power BI" and "Tableau":**
- These are exact brand names, likely extracted verbatim
- The CV probably has exactly "Power BI" and "Tableau"
- Direct match: `"power bi" in cv_keywords` → ✅ Works

**For "SQL":**
- CV might have: `"SQL (PostgreSQL, MySQL)"` → Extracted as entire string
- CV keywords set contains: `{"sql (postgresql, mysql)"}`
- Check: `"sql" in "sql (postgresql, mysql)"` → ✅ Should return True!
- **But wait...** The substring check requires `len(keyword_lower) > 3 or len(cv_kw) > 3`
- `len("sql") = 3` → **NOT > 3**, so the check fails!
- Falls through to variations dict, but "sql" variations don't include "sql (postgresql, mysql)"

**❌ BUG**: The length check `if len(keyword_lower) > 3 or len(cv_kw) > 3` prevents 3-character keywords like "SQL" from matching substrings!

**For "Data Warehousing":**
- CV might have: `"Data Warehouse"` (singular) or `"ETL"` or `"Data storage"`
- JD has: `"Data Warehousing"` (plural)
- Check: `"data warehousing" in "data warehouse"` → ❌ No (different strings)
- Variations dict doesn't include "data warehousing" → ❌ No match

**❌ BUG**: No stemming/pluralization handling. "Data Warehouse" ≠ "Data Warehousing"

### Keyword Extraction from CV

```python
# From ats_recommendation_service.py, lines 694-732
def _extract_keywords_from_cv_file(self, cv_file: Path) -> set:
    """Extract keywords from a CV JSON file"""
    keywords = set()
    
    try:
        with open(cv_file, 'r', encoding='utf-8') as f:
            cv_data = json.load(f)
        
        # Extract from skills
        for skill_cat in cv_data.get('skills', []):
            if isinstance(skill_cat, dict):
                for skill in skill_cat.get('skills', []):
                    if skill:
                        keywords.add(str(skill).lower())
        
        # Extract from experience bullets (2-3 word phrases)
        for exp in cv_data.get('experience', []):
            if isinstance(exp, dict):
                for bullet in exp.get('bullets', []):
                    if bullet:
                        words = str(bullet).lower().split()
                        for i in range(len(words) - 1):
                            keywords.add(f"{words[i]} {words[i+1]}")
                        for i in range(len(words) - 2):
                            keywords.add(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        return keywords
    except Exception as e:
        logger.warning(f"⚠️ [KEYWORD_FILTER] Error extracting keywords from {cv_file}: {e}")
        return set()
```

**Issue**: This extracts 2-3 word phrases from bullets, but doesn't handle:
- Parenthetical variations: "SQL (PostgreSQL, MySQL)" → extracts as-is
- Pluralization: "Data Warehouse" vs "Data Warehousing"
- Abbreviations: "SQL" vs "Structured Query Language"

---

## 5. AI Recommendation Input

### Location
- **Prompt Generation**: `cv-magic-app/backend/prompt/ai_recommendation_prompt_template.py`
- **Service**: `cv-magic-app/backend/app/services/ai_recommendation_generator.py`

### Code Snippet: What Data is Passed to AI

```python
# From ai_recommendation_prompt_template.py, lines 11-427
def generate_ai_recommendation_prompt(company: str, analysis_data: dict) -> str:
    """
    Generate AI recommendation prompt using optimized analysis data
    """
    # Extract optimized data structures
    metadata = analysis_data.get("metadata", {})
    skills_extraction = analysis_data.get("skills_extraction", {})
    preliminary_decision = analysis_data.get("preliminary_decision", {})
    match_summary = analysis_data.get("match_summary", {})
    keyword_guidance = analysis_data.get("keyword_integration_guidance", {})
    component_summary = analysis_data.get("component_summary", {})
    ats_scoring = analysis_data.get("ats_scoring", {})
    
    # Extract CV and JD skills (clean structured data)
    cv_skills = skills_extraction.get("cv", {})
    jd_skills = skills_extraction.get("jd", {})
    
    # Extract match data
    technical_match = match_summary.get("by_category", {}).get("technical", {})
    soft_match = match_summary.get("by_category", {}).get("soft", {})
    domain_match = match_summary.get("by_category", {}).get("domain", {})
    
    # Filter missing keywords (lines 61-105)
    already_in_cv_filtered = keyword_guidance.get("already_in_cv_filtered", [])
    
    if technical_match.get('missing'):
        technical_match['missing'] = filter_missing_keywords(
            technical_match['missing'], 
            technical_match.get('matched', []),
            already_in_cv_filtered
        )
    
    # ... prompt generation continues
```

### Does AI Receive Full Input File or Just Missing Keywords?

**✅ AI receives the FULL input file structure**, but the prompt focuses on:
1. **Missing keywords** (filtered list)
2. **Matched keywords** (for reference - "don't categorize these")
3. **Component scores** (technical, skills, experience, seniority, industry)
4. **ATS scoring** (final score, category breakdowns)
5. **Keyword tiers** (pre-classified, but AI must re-categorize)

### Does AI Have Access to Original CV Bullets/Text?

**❌ NO** - The AI does NOT receive the original CV text or bullets. It only receives:
- Extracted skills lists (technical, soft, domain)
- Match summary (matched vs missing)
- Component analysis scores
- ATS scores

**This is a limitation** - The AI cannot check for "semantic evidence" in CV bullets for Tier 2 keywords because it doesn't have the CV text!

### Prompt Template

The prompt is in `ai_recommendation_prompt_template.py` (lines 150-419). Key sections:
- **Executive Summary**: ATS scores, match rates
- **Missing Keywords Lists**: Filtered lists of missing technical/soft/domain keywords
- **Component Scores**: Technical depth, experience alignment, etc.
- **Output Format**: Structured JSON with tier1/tier2/tier3 categorization

**Critical Requirement** (lines 409-416):
```
**🚨 CRITICAL KEYWORD CATEGORIZATION REQUIREMENT:**
- You MUST categorize EVERY SINGLE missing keyword listed in the "MISSING KEYWORDS" section above
- ⚠️ DO NOT categorize keywords that are ALREADY in the CV (matched keywords)
- Count verification: tier1 + tier2 + tier3 = Total missing keywords
```

---

## 6. File Paths Summary

### Skills Extraction
- **Service**: `cv-magic-app/backend/app/services/skill_extraction/skill_extraction_service.py`
- **Parser**: `cv-magic-app/backend/app/services/skill_extraction/response_parser.py`
- **Prompts**: `cv-magic-app/backend/app/services/skill_extraction/prompt_templates.py`

### Keyword Matching
- **Comparator**: `cv-magic-app/backend/app/services/skill_extraction/preextracted_comparator.py`
- **Semantic Mapping**: Lines 28-240 in `preextracted_comparator.py`

### Already-in-CV Filtering
- **Service**: `cv-magic-app/backend/app/services/ats_recommendation_service.py`
- **Methods**: 
  - `_extract_existing_cv_keywords()` (lines 655-692)
  - `_keyword_exists_in_cv()` (lines 734-767)
  - `_classify_keywords()` (lines 532-653)

### Input File Creation
- **Service**: `cv-magic-app/backend/app/services/ats_recommendation_service.py`
- **Method**: `extract_ats_recommendation_data()` (lines 31-143)
- **Save Method**: `save_optimized_recommendation()` (lines 145-175)

### AI Recommendation Generation
- **Service**: `cv-magic-app/backend/app/services/ai_recommendation_generator.py`
- **Prompt Template**: `cv-magic-app/backend/prompt/ai_recommendation_prompt_template.py`
- **Method**: `generate_ai_recommendation()` (lines 41-128)

---

## Summary of Identified Bugs

### Bug 1: No Normalization in Skills Extraction ✅ FIXED
**Location**: `skill_extraction_service.py` + `prompt_templates.py`
**Issue**: "SQL (PostgreSQL, MySQL)" and "SQL" are treated as different skills
**Fix**: ✅ **IMPLEMENTED** - Added `skill_normalizer.py` with normalization logic:
- Extracts base skills from parentheticals: "SQL (PostgreSQL, MySQL)" → "SQL"
- Removes version numbers: "Python 3.x" → "Python"
- Integrated into `response_parser.py` to normalize all extracted skills
- Backward compatible: Returns normalized base skills in main fields
- Also stores full original skills for display/reference

### Bug 2: Exact Match Logic Too Strict ✅ FIXED
**Location**: `preextracted_comparator.py`, `_identify_exact_matches()` (line 859)
**Issue**: Requires exact string match, fails for "SQL" vs "SQL (PostgreSQL, MySQL)"
**Fix**: ✅ **IMPLEMENTED** - Updated `_identify_exact_matches()` to use:
- Base skill normalization (uses `normalize_skill()` from `skill_normalizer.py`)
- Multiple match strategies:
  1. Exact match: "sql" == "sql"
  2. Base match: "sql" == base of "sql (postgresql, mysql)"
  3. Substring match: "sql" in "sql (postgresql, mysql)" or vice versa
- Enhanced logging with match type (exact/base_match/substring_match)
- Prevents duplicates by breaking after first match

### Bug 3: Length Check Prevents 3-Char Keyword Matching ✅ FIXED
**Location**: `ats_recommendation_service.py`, `_keyword_exists_in_cv()` (line 749)
**Issue**: `if len(keyword_lower) > 3` prevents "SQL" (3 chars) from matching substrings
**Fix**: ✅ **IMPLEMENTED** - Changed `> 3` to `>= 3` to allow 3-character keywords:
- Now handles: "SQL", "ETL", "AWS", "GCP" (all 3 chars)
- Enhanced variations dict with parenthetical patterns: `'sql': [..., 'sql (']`
- Added new check: CV keywords starting with base + space or parenthesis
  - Catches "SQL (PostgreSQL, MySQL)" when looking for "SQL"
- Added debug logging for base pattern matches

### Bug 4: No Pluralization/Stemming ✅ FIXED
**Location**: `ats_recommendation_service.py`, `_keyword_exists_in_cv()`
**Issue**: "Data Warehouse" ≠ "Data Warehousing" (no match)
**Fix**: ✅ **IMPLEMENTED** - Added NLTK PorterStemmer support:
- Added `_stem_keyword()` method using PorterStemmer
- Handles pluralization: "Data Warehousing" → "data warehous" matches "Data Warehouse" → "data warehous"
- Graceful fallback: If NLTK unavailable, skips stemming but continues with other matching methods
- Added NLTK to requirements.txt
- Automatic NLTK data download (punkt tokenizer) on first use
- Enhanced logging for stemming-based matches

### Bug 5: Duplicate Keywords in Matched and Missing ✅ FIXED
**Location**: `ats_recommendation_service.py`, `_extract_match_summary()` (lines 340-385)
**Issue**: Same keyword can appear in both matched and missing arrays
**Fix**: ✅ **IMPLEMENTED** - Two-pronged approach:
1. **Prompt Updates** (prevention):
   - Enhanced `build_prompt()` in `preextracted_comparator.py` with explicit duplicate prevention rules
   - Added verification requirements: "Before listing in MISSING, check if already in MATCHED"
   - Added count verification: "Matched + Missing MUST equal total JD requirements"
   - Updated concise JSON prompt with same rules
2. **Parser Deduplication** (safety net):
   - Added post-processing deduplication in `_extract_match_summary()`
   - Removes keywords from missing list if they're already in matched (case-insensitive)
   - Logs warnings when duplicates are found and removed
   - Ensures each keyword appears in exactly one list

### Bug 6: AI Doesn't Have CV Text for Evidence Checking
**Location**: `ai_recommendation_prompt_template.py`
**Issue**: AI cannot verify "semantic evidence" for Tier 2 keywords without CV text
**Fix**: Include CV text or relevant bullets in prompt for Tier 2 validation

---

## Recommended Fixes Priority

1. **HIGH**: Fix Bug 3 (length check) - blocks "SQL" matching
2. **HIGH**: Fix Bug 2 (exact match) - add substring matching
3. **MEDIUM**: Fix Bug 5 (duplicates) - causes confusion in recommendations
4. **MEDIUM**: Fix Bug 1 (normalization) - extract base skills from parentheticals
5. **LOW**: Fix Bug 4 (pluralization) - nice-to-have improvement
6. **LOW**: Fix Bug 6 (CV text) - would improve Tier 2 accuracy

