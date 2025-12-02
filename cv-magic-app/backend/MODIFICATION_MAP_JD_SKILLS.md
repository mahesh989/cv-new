# Modification Map: JD Skills Extraction Improvements

## Overview
This document maps all locations where modifications need to be made to improve JD skill extraction.

---

## 📍 File 1: `jd_skill_sections_prompt.py`
**Location**: `cv-magic-app/backend/app/services/jd_analysis/jd_skill_sections_prompt.py`

### Current State:
- **Lines 7-21**: `THREE_SECTION_SYSTEM_PROMPT` - Basic categorization and extraction rules
- **Lines 24-36**: `get_three_section_prompts()` - User prompt generation

### Changes Needed:
1. **Improve SYSTEM_PROMPT** (lines 7-21):
   - Add explicit anti-hallucination rules
   - Make categorization mutually exclusive
   - Add better examples (multi-industry)
   - Clarify list extraction ("Power BI, Tableau, etc.")
   - Remove vague "Include implied skills" → be more specific

2. **Improve USER_PROMPT** (lines 24-36):
   - Add explicit "DO NOT" examples
   - Emphasize extracting ALL items from lists
   - Add validation reminder

---

## 📍 File 2: `jd_analyzer.py`
**Location**: `cv-magic-app/backend/app/services/jd_analysis/jd_analyzer.py`

### Current State:
- **Lines 469-518**: `_generate_three_section_skills()` method
  - Calls LLM with prompts
  - Parses JSON response
  - Removes markdown fences
  - **Currently has**: Within-category deduplication (lines 494-503)
  - **Returns**: `Dict[str, List[str]]` with technical_skills, soft_skills, domain_knowledge

### Changes Needed:
**In `_generate_three_section_skills()` method (lines 469-518)**:

1. **After JSON parsing** (after line 491):
   - Add JD text validation (fuzzy match against `jd_text` parameter)
   - Add cross-category duplicate detection and removal
   - Add normalization (case, variations)
   - Add blacklist filtering

2. **Before returning** (before line 515):
   - Apply all validation/refinement steps
   - Log validation results

### Option: Create New Validation Module
**Alternative approach**: Create `jd_skills_validator.py` with:
- `validate_against_jd_text(skills: List[str], jd_text: str) -> List[str]`
- `remove_cross_category_duplicates(skills_dict: dict) -> dict`
- `normalize_skill_variations(skills: List[str]) -> List[str]`
- `apply_blacklist_filter(skills: List[str]) -> List[str]`

Then call from `_generate_three_section_skills()` after line 491.

---

## 📍 File 3: `prompt_templates.py` (SkillCategorizer)
**Location**: `cv-magic-app/backend/app/services/skill_extraction/prompt_templates.py`

### Current State:
- **Lines 279-500+**: `SkillCategorizer` class
  - `categorize_term()` (line 388): Rule-based categorization
  - `recategorize_skills()` (line 431): Re-categorizes all skills
  - Already handles: Deduplication, recategorization, generic term exclusion

### Changes Needed:
**In `recategorize_skills()` method (lines 431-500)**:

1. **Add cross-category duplicate handling**:
   - Currently collects all terms and recategorizes
   - **Enhancement**: Detect if same skill in multiple categories, keep in highest priority
   - Priority: Technical > Soft > Domain

2. **Add JD text validation** (if jd_text passed):
   - Optional parameter: `jd_text: Optional[str] = None`
   - If provided, validate each skill appears in JD text

---

## 📍 File 4: `context_aware_analysis_pipeline.py`
**Location**: `cv-magic-app/backend/app/services/context_aware_analysis_pipeline.py`

### Current State:
- **Lines 565-590**: Uses `three_section_skills` from JD analysis
- **Line 582**: Already applies `SkillCategorizer.recategorize_skills()`
- **Lines 1030-1060**: Similar logic for `run_initial_analysis()`

### Changes Needed:
**Minimal changes needed** - already uses `SkillCategorizer`:
- If we enhance `SkillCategorizer.recategorize_skills()` to handle cross-category duplicates, it will automatically apply here
- **Optional**: Pass `jd_text` to `SkillCategorizer` if we add JD validation there

---

## 📍 File 5: (NEW) `jd_skills_validator.py` (Optional)
**Location**: `cv-magic-app/backend/app/services/jd_analysis/jd_skills_validator.py`

### Purpose:
Centralized validation and refinement module for JD skills

### Functions to Create:
1. `validate_skills_against_jd(skills: List[str], jd_text: str) -> List[str]`
   - Fuzzy match each skill against JD text
   - Remove skills not found (prevents hallucinations)

2. `remove_cross_category_duplicates(skills_dict: dict) -> dict`
   - Check for same skill in multiple categories
   - Keep in highest priority: Technical > Soft > Domain

3. `normalize_skill_variations(skills: List[str]) -> List[str]`
   - Normalize case, spacing, variations
   - "SQL" vs "sql" → "SQL"
   - "Power BI" vs "PowerBI" → "Power BI"

4. `apply_blacklist_filter(skills: List[str]) -> List[str]`
   - Remove generic terms: "stakeholders", "insights", etc.

5. `refine_jd_skills(skills_dict: dict, jd_text: str) -> dict`
   - Master function that applies all validations
   - Returns refined skills_dict

---

## 🔄 Data Flow (Current)

```
JD Text
  ↓
jd_skill_sections_prompt.py (get_three_section_prompts)
  ↓
jd_analyzer.py (_generate_three_section_skills)
  ├─ LLM Call
  ├─ JSON Parse
  ├─ Deduplicate (within category) ← CURRENT
  └─ Return Dict
  ↓
JDAnalysisResult.three_section_skills
  ↓
context_aware_analysis_pipeline.py
  ├─ SkillCategorizer.recategorize_skills() ← CURRENT
  └─ results.jd_skills
```

---

## 🔄 Data Flow (Proposed)

```
JD Text
  ↓
jd_skill_sections_prompt.py (IMPROVED prompts)
  ↓
jd_analyzer.py (_generate_three_section_skills)
  ├─ LLM Call
  ├─ JSON Parse
  ├─ validate_skills_against_jd() ← NEW
  ├─ normalize_skill_variations() ← NEW
  ├─ remove_cross_category_duplicates() ← NEW
  ├─ apply_blacklist_filter() ← NEW
  ├─ Deduplicate (within category) ← EXISTING
  └─ Return Dict
  ↓
JDAnalysisResult.three_section_skills
  ↓
context_aware_analysis_pipeline.py
  ├─ SkillCategorizer.recategorize_skills() ← ENHANCED (cross-category)
  └─ results.jd_skills
```

---

## 📋 Implementation Strategy

### Option A: Enhance Existing Files (Recommended)
1. **Improve prompts** in `jd_skill_sections_prompt.py`
2. **Add validation functions** directly in `jd_analyzer.py` (in `_generate_three_section_skills()`)
3. **Enhance `SkillCategorizer.recategorize_skills()`** to handle cross-category duplicates

**Pros**: Minimal file changes, keeps logic together
**Cons**: `jd_analyzer.py` gets longer

### Option B: Create New Validator Module
1. **Improve prompts** in `jd_skill_sections_prompt.py`
2. **Create `jd_skills_validator.py`** with all validation functions
3. **Call validator** from `jd_analyzer.py._generate_three_section_skills()`
4. **Enhance `SkillCategorizer`** for cross-category duplicates

**Pros**: Clean separation, reusable, testable
**Cons**: More files, more imports

---

## 🎯 Recommended Approach

**Hybrid**: 
- **Option A** for simple validations (normalization, blacklist) - add directly to `_generate_three_section_skills()`
- **Option B** for complex validations (JD text matching) - create validator module
- **Enhance `SkillCategorizer`** for cross-category duplicates (already used everywhere)

---

## 📝 Summary of Modification Points

| File | Location | Type | Priority |
|------|----------|------|----------|
| `jd_skill_sections_prompt.py` | Lines 7-21, 24-36 | Prompt improvement | **HIGH** |
| `jd_analyzer.py` | Lines 469-518 | Add validation logic | **HIGH** |
| `prompt_templates.py` | Lines 431-500 | Enhance recategorize_skills() | **MEDIUM** |
| `jd_skills_validator.py` | NEW FILE | Create validator module | **MEDIUM** (if Option B) |
| `context_aware_analysis_pipeline.py` | Lines 582, 1080, 1095 | Minimal (auto-benefits) | **LOW** |

---

## ✅ Validation Checklist

After implementation, verify:
- [ ] No duplicates within categories
- [ ] No duplicates across categories
- [ ] All extracted skills appear in JD text (fuzzy match)
- [ ] No generic terms (blacklist filtered)
- [ ] Skills normalized (case, spacing)
- [ ] Proper categorization (Technical/Soft/Domain)
- [ ] Works for multiple industries (tech, healthcare, finance, nonprofit)

