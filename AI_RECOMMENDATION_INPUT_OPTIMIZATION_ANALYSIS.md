# AI Recommendation Input Optimization Analysis

---

## 1. EXACT AI PROMPT TEMPLATE ANALYSIS

### File: `ai_recommendation_prompt_template.py` (lines 11-427)

### Fields ACTUALLY USED in Prompt:

#### ✅ **metadata** (PARTIALLY USED)
```python
# Line 27: metadata = analysis_data.get("metadata", {})
# ❌ NOT USED: metadata fields are NOT referenced in prompt
# The prompt uses company parameter directly, not from metadata
```

**Used:** None (company passed as parameter, not from metadata)
**Not Used:** `metadata.company`, `metadata.generated_at`, `metadata.ats_score_current`, `metadata.match_rate_current`

#### ✅ **ats_scoring** (FULLY USED)
```python
# Lines 41-47: All fields used
final_ats_score = ats_scoring.get("final_score", 0)           # ✅ Line 159
category_status = ats_scoring.get("status", "Unknown")         # ✅ Line 160
target_score = ats_scoring.get("target_score", 75.0)            # ✅ Line 161
improvement_needed = ats_scoring.get("improvement_needed", 0)  # ✅ Line 162
category1_score = ats_scoring.get("category1_keywords", 0)     # ✅ Line 212
category2_score = ats_scoring.get("category2_ai_analysis", 0)  # ✅ Line 213
missing_counts = ats_scoring.get("missing_counts", {})          # ✅ Line 212, 270-273
```

**Used:** ALL fields
**Not Used:** None

#### ✅ **preliminary_decision** (FULLY USED)
```python
# Lines 142-148: All fields used
decision = preliminary_decision.get("decision", "UNKNOWN")           # ✅ Line 165
confidence = preliminary_decision.get("confidence", 0)              # ✅ Line 165
match_score = preliminary_decision.get("match_score", 0)            # ✅ Line 165
primary_reason = preliminary_decision.get("primary_reason", "")       # ✅ Line 166
critical_missing = preliminary_decision.get("critical_missing", [])  # ✅ Line 167
implicit_likely = preliminary_decision.get("implicit_likely", [])   # ✅ Line 168
blocker_found = preliminary_decision.get("blocker_found", False)     # ❌ NOT USED in prompt
```

**Used:** decision, confidence, match_score, primary_reason, critical_missing, implicit_likely
**Not Used:** `blocker_found` (extracted but never referenced in prompt)

#### ✅ **match_summary** (FULLY USED)
```python
# Lines 50-53: All fields used
overall_match_rate = match_summary.get("overall_match_rate", 0)  # ✅ Line 170, 250
technical_match = match_summary.get("by_category", {}).get("technical", {})  # ✅ Lines 171, 180, 189, 257, 368
soft_match = match_summary.get("by_category", {}).get("soft", {})  # ✅ Lines 172, 181, 192, 258
domain_match = match_summary.get("by_category", {}).get("domain", {})  # ✅ Lines 173, 182, 195, 259
```

**Used:** ALL fields (overall_match_rate, by_category.technical/soft/domain with matched/missing/match_rate)
**Not Used:** None

#### ✅ **keyword_integration_guidance** (FULLY USED)
```python
# Lines 81, 128-131: All fields used
already_in_cv_filtered = keyword_guidance.get("already_in_cv_filtered", [])  # ✅ Line 183
tier1_keywords = keyword_guidance.get("tier1_always_add", {})  # ✅ Line 220
tier2_keywords = keyword_guidance.get("tier2_add_if_evidence", {})  # ✅ Line 221
tier3_keywords = keyword_guidance.get("tier3_never_add", {})  # ✅ Line 222, 364-365
integration_instructions = keyword_guidance.get("integration_instructions", "")  # ❌ NOT USED
```

**Used:** already_in_cv_filtered, tier1_keywords, tier2_keywords, tier3_keywords
**Not Used:** `integration_instructions` (extracted but never referenced)

#### ✅ **component_summary** (PARTIALLY USED)
```python
# Lines 121-125: Only specific fields used
technical_component = component_summary.get("technical", {})
  # ✅ Used: score (line 205), core_match (line 205), stack_fit (line 205), strengths (line 356), gaps (line 357)
  # ❌ NOT USED: raw_scores.* (35+ fields), all other numeric fields

skills_component = component_summary.get("skills", {})
  # ✅ Used: score (line 206), business_readiness (line 206), strengths (line 370)
  # ❌ NOT USED: raw_scores.*, all other numeric fields

experience_component = component_summary.get("experience", {})
  # ✅ Used: alignment_score (line 207), years (line 207), corporate_years (line 207), strengths (line 369)
  # ❌ NOT USED: raw_scores.*, all other numeric fields

seniority_component = component_summary.get("seniority", {})
  # ✅ Used: score (line 208), cv_level (line 208, 350), jd_level (line 208, 351)
  # ❌ NOT USED: raw_scores.*, all other numeric fields

industry_component = component_summary.get("industry", {})
  # ✅ Used: alignment_score (line 209, 265), cv_industry (line 209, 252), jd_industry (line 209, 252), transition_difficulty (line 209, 252)
  # ❌ NOT USED: raw_scores.*, all other numeric fields
```

**Used:** 
- `technical`: score, core_match, stack_fit, strengths, gaps
- `skills`: score, business_readiness, strengths
- `experience`: alignment_score, years, corporate_years, strengths
- `seniority`: score, cv_level, jd_level
- `industry`: alignment_score, cv_industry, jd_industry, transition_difficulty

**Not Used:** 
- ALL `raw_scores.*` fields (35+ fields per component)
- All other numeric breakdowns not listed above

#### ✅ **tailoring_strategy** (FULLY USED)
```python
# Lines 134-139: All fields used
primary_objective = tailoring_strategy.get("primary_objective", "...")  # ✅ Lines 225, 251, 343
emphasis_areas = tailoring_strategy.get("emphasis_areas", [])  # ✅ Lines 227, 344, 394
de_emphasize_areas = tailoring_strategy.get("de_emphasize", [])  # ✅ Lines 228, 345, 395
critical_additions = tailoring_strategy.get("critical_additions", {})  # ❌ NOT USED
tone_guidance = tailoring_strategy.get("tone_guidance", "...")  # ✅ Lines 226, 386, 393
industry_bridging = tailoring_strategy.get("industry_bridging", [])  # ✅ Lines 229, 346
```

**Used:** primary_objective, emphasis_areas, de_emphasize_areas, tone_guidance, industry_bridging
**Not Used:** `critical_additions` (extracted but never referenced)

#### ❌ **skills_extraction** (NOT USED IN PROMPT)
```python
# Lines 36-38: Extracted but NEVER used in prompt
cv_skills = skills_extraction.get("cv", {})  # ❌ NOT USED
jd_skills = skills_extraction.get("jd", {})  # ❌ NOT USED
```

**Used:** None
**Not Used:** ENTIRE section (cv_skills and jd_skills are extracted but never referenced in prompt)

**Note:** The prompt uses `match_summary` which already contains matched/missing skills, so raw CV/JD skills are redundant.

---

## 2. WHAT GETS PASSED TO AI SERVICE

### File: `ai_recommendation_generator.py`, `_load_ai_prompt()` (lines 176-206)

**Flow:**
1. Reads FULL input recommendation file (JSON)
2. Loads entire `analysis_data` dict
3. Passes to `generate_ai_recommendation_prompt(company, analysis_data)`
4. Template extracts only needed fields and builds prompt string
5. Prompt string sent to AI service (not the JSON)

**Data Structure Passed:**
```python
# Line 185: Full JSON loaded
with open(input_file, 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)  # FULL file structure

# Line 199: Full dict passed to template
prompt_content = template_module.generate_ai_recommendation_prompt(company, analysis_data)
```

**Example Prompt Sent to AI:**
The prompt is a formatted string (not JSON), containing:
- Analysis scores and metrics
- Missing keywords lists
- Matched keywords lists (for exclusion)
- Component summaries (only selected fields)
- Strategic guidance
- Output format instructions

**Token Count:** Estimated 2000-3000 tokens (varies by keyword count)

---

## 3. UNUSED FIELDS IDENTIFICATION

### ❌ **metadata** - NOT USED
- `metadata.company` - Not used (company passed as parameter)
- `metadata.generated_at` - Not used
- `metadata.ats_score_current` - Not used (uses ats_scoring.final_score instead)
- `metadata.match_rate_current` - Not used (uses match_summary.overall_match_rate instead)



### ❌ **skills_extraction** - NOT USED
- `skills_extraction.cv.technical` - Not used (match_summary has matched/missing)
- `skills_extraction.cv.soft` - Not used
- `skills_extraction.cv.domain` - Not used
- `skills_extraction.jd.technical` - Not used
- `skills_extraction.jd.soft` - Not used
- `skills_extraction.jd.domain` - Not used

**Recommendation:** Remove entire `skills_extraction` section (redundant with match_summary)

### ❌ **component_summary.raw_scores** - NOT USED
Each component has 35+ fields in `raw_scores.*` that are never used:
- `component_summary.technical.raw_scores.*` (35+ fields)
- `component_summary.skills.raw_scores.*` (35+ fields)
- `component_summary.experience.raw_scores.*` (35+ fields)
- `component_summary.seniority.raw_scores.*` (35+ fields)
- `component_summary.industry.raw_scores.*` (35+ fields)



### ❌ **preliminary_decision.blocker_found** - NOT USED
- Extracted but never referenced in prompt



### ❌ **keyword_integration_guidance.integration_instructions** - NOT USED
- Extracted but never referenced in prompt


### ❌ **tailoring_strategy.critical_additions** - NOT USED
- Extracted but never referenced in prompt


---

## 4. CV CONTENT INCLUDED? ❌ NO

### Current State:
**The AI does NOT receive:**
- ❌ Original CV bullet points text
- ❌ CV experience descriptions
- ❌ CV skills section text
- ❌ JD description/responsibilities text
- ❌ JD requirements text

**The AI only receives:**
- ✅ Extracted skills lists (technical, soft, domain)
- ✅ Match summary (matched/missing keywords)
- ✅ Component scores and summaries
- ✅ ATS scores

### Impact on Tier 2 Recommendations:

**Problem:** Tier 2 keywords require "semantic evidence from CV" but AI has no access to CV text to verify evidence.

**Example:**
- Missing keyword: "Business process design"
- AI needs to check: "Does CV mention process optimization, workflow improvement, or similar?"
- **Current:** AI cannot check (no CV text)
- **Result:** AI must guess or mark as Tier 3 (high risk)

### Where to Add CV/JD Content:

**Option 1: Add to Input File**
```json
{
  "cv_content": {
    "experience_bullets": ["bullet 1", "bullet 2", ...],
    "skills_section": "Python, SQL, ...",
    "summary": "Professional summary text"
  },
  "jd_content": {
    "description": "Full JD text",
    "requirements": ["req 1", "req 2", ...],
    "responsibilities": ["resp 1", "resp 2", ...]
  }
}
```

**Option 2: Add to Prompt Template**
```python
# In ai_recommendation_prompt_template.py
cv_content = analysis_data.get("cv_content", {})
jd_content = analysis_data.get("jd_content", {})

# Add to prompt:
"""
CV CONTENT (for Tier 2 evidence checking):
Experience Bullets:
{cv_content.get('experience_bullets', [])}

JD CONTENT (for context):
Description:
{jd_content.get('description', '')}
"""
```



---

## 5. EXAMPLE PROMPT WITH REAL DATA

### Estimated Token Breakdown:

**Useful Data (60%):**
- Missing keywords lists: ~800 tokens
- Matched keywords (exclusion): ~200 tokens
- Component summaries (used fields): ~400 tokens
- ATS scores: ~100 tokens
- Strategic guidance: ~200 tokens
- Output format: ~300 tokens
- **Total Useful: ~2000 tokens**

**Bloat (40%):**
- Unused metadata: ~50 tokens
- Unused skills_extraction: ~300 tokens
- Unused raw_scores: ~500 tokens
- Unused fields in components: ~200 tokens
- Redundant instructions: ~200 tokens
- **Total Bloat: ~1250 tokens**

**Total Prompt: ~3250 tokens**
**Useful Percentage: 61.5%**

### Example Prompt Snippet:

```
Strategic CV Optimization Recommendations Generator

ANALYSIS DATA:

Current ATS Performance:
- Final Score: 68/100
- Status: Needs Improvement
- Target: 75/100
- Improvement Needed: 7 points

Match Assessment:
- Decision: MAYBE (Confidence: 75%, Match: 68%)
- Primary Reason: Missing key technical skills
- Critical Missing: Power BI, Tableau, SQL
- Implicit Likely: Data analysis experience

Skills Match (Overall: 65%):
- Technical: 60% (12 matched, 8 missing)
- Soft: 70% (7 matched, 3 missing)
- Domain: 65% (13 matched, 7 missing)

MISSING TECHNICAL KEYWORDS (8 total):
  - Power BI
  - Tableau
  - SQL
  - Data Warehousing
  - ETL
  - Python
  - Excel
  - AWS

[... rest of prompt ...]
```

---

## 6. OPTIMIZATION RECOMMENDATIONS

### Priority 1: Remove Unused Fields (30-40% size reduction)

**Remove:**
1. `metadata` section (or keep minimal tracking fields)
2. `skills_extraction` section (redundant with match_summary)
3. All `component_summary.*.raw_scores.*` (175+ unused fields)
4. `preliminary_decision.blocker_found` (if not used)
5. `keyword_integration_guidance.integration_instructions` (if not used)
6. `tailoring_strategy.critical_additions` (if not used)

**Expected Reduction:** 30-40% file size reduction

### Priority 2: Add CV/JD Content (Improve Tier 2 accuracy)

**Add:**
1. `cv_content.experience_bullets` - Array of bullet point strings
2. `cv_content.skills_section` - Skills section text
3. `cv_content.summary` - Professional summary
4. `jd_content.description` - Full JD description
5. `jd_content.requirements` - Key requirements list

**Expected Impact:** 
- Better Tier 2 evidence checking
- More accurate risk assessment
- Higher quality recommendations

### Priority 3: Optimize Prompt Template

**Changes:**
1. Remove redundant instructions
2. Consolidate keyword tier references
3. Streamline output format instructions

**Expected Reduction:** 10-15% prompt token reduction

---

## 7. OPTIMIZED INPUT FILE STRUCTURE

### Proposed Structure:

```json
{
  "metadata": {
    "company": "Company Name",
    "generated_at": "2024-01-01T00:00:00Z"
    // Remove: ats_score_current, match_rate_current (redundant)
  },
  
  // REMOVE: skills_extraction (redundant with match_summary)
  
  "preliminary_decision": {
    "decision": "MAYBE",
    "confidence": 75,
    "match_score": 68,
    "primary_reason": "...",
    "critical_missing": [...],
    "implicit_likely": [...]
    // Remove: blocker_found (if not used)
  },
  
  "match_summary": {
    // Keep as-is (fully used)
  },
  
  "keyword_integration_guidance": {
    "already_in_cv_filtered": [...],
    "tier1_always_add": {...},
    "tier2_add_if_evidence": {...},
    "tier3_never_add": {...}
    // Remove: integration_instructions (if not used)
  },
  
  "component_summary": {
    "technical": {
      "score": 65,
      "core_match": 70,
      "stack_fit": 60,
      "strengths": [...],
      "gaps": [...]
      // Remove: raw_scores.* (35+ fields)
    },
    // Same for skills, experience, seniority, industry
  },
  
  "tailoring_strategy": {
    "primary_objective": "...",
    "emphasis_areas": [...],
    "de_emphasize_areas": [...],
    "tone_guidance": "...",
    "industry_bridging": [...]
    // Remove: critical_additions (if not used)
  },
  
  "ats_scoring": {
    // Keep as-is (fully used)
  },
  
  // NEW: Add CV/JD content
  "cv_content": {
    "experience_bullets": [
      "Developed Python scripts for data analysis",
      "Led team of 5 analysts",
      ...
    ],
    "skills_section": "Python, SQL, Excel, Power BI",
    "summary": "Data analyst with 5 years experience..."
  },
  
  "jd_content": {
    "description": "Full JD text...",
    "requirements": ["req 1", "req 2", ...],
    "responsibilities": ["resp 1", "resp 2", ...]
  }
}
```

**Expected Size Reduction:** 30-40%
**Expected Quality Improvement:** Better Tier 2 evidence checking

---

## SUMMARY

### Used in Prompt:
- ✅ `ats_scoring` - ALL fields
- ✅ `preliminary_decision` - Most fields (except blocker_found)
- ✅ `match_summary` - ALL fields
- ✅ `keyword_integration_guidance` - Most fields (except integration_instructions)
- ✅ `component_summary` - Selected fields only (score, core_match, stack_fit, strengths, gaps, etc.)
- ✅ `tailoring_strategy` - Most fields (except critical_additions)

### NOT Used in Prompt:
- ❌ `metadata` - Entire section (or minimal use)
- ❌ `skills_extraction` - Entire section (redundant)
- ❌ `component_summary.*.raw_scores.*` - 175+ unused fields
- ❌ `preliminary_decision.blocker_found`
- ❌ `keyword_integration_guidance.integration_instructions`
- ❌ `tailoring_strategy.critical_additions`

### Missing (Should Add):
- ❌ CV content (experience bullets, skills text)
- ❌ JD content (description, requirements)

### Optimization Potential:
- **File Size Reduction:** 30-40%
- **Prompt Token Reduction:** 10-15%
- **Quality Improvement:** Better Tier 2 evidence checking with CV/JD content

