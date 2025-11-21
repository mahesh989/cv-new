# Match Summary Generation - Complete Analysis

## 📋 File Structure: `ats_recommendation_service.py`

### **Class: `ATSRecommendationService`**

**Location:** `cv-magic-app/backend/app/services/ats_recommendation_service.py`

**Methods:**

1. `__init__(self, user_email: str)`
   - Initializes service with user email
   - Sets base directory path

2. `extract_ats_recommendation_data(self, company: str) -> Optional[Dict[str, Any]]`
   - Main method to extract recommendation data
   - Reads from `{company}_skills_analysis.json`
   - Calls helper methods to extract each component

3. `save_optimized_recommendation(self, company: str, data: Dict[str, Any]) -> Optional[Path]`
   - Saves extracted data to `{company}_input_recommendation_{timestamp}.json`

4. `create_recommendation_file(self, company: str) -> bool`
   - Convenience method that calls extract + save

5. `_extract_preliminary_decision(self, match_entries: List[Dict]) -> Dict[str, Any]`
   - Extracts decision from `analyze_match_entries`
   - Parses text content using regex

6. `_extract_match_summary(self, preextracted_entries: List[Dict]) -> Dict[str, Any]`
   - **KEY METHOD** - Extracts match summary from `preextracted_comparison_entries`
   - Parses text content to extract by_category structure

7. `_extract_component_summary(self, component_entries: List[Dict]) -> Dict[str, Any]`
   - Extracts component scores from `component_analysis_entries`

8. `_extract_ats_scoring(self, ats_entries: List[Dict]) -> Dict[str, Any]`
   - Extracts ATS scores from `ats_calculation_entries`

9. `_classify_keywords(self, missing_keywords: Dict[str, List[str]], cv_skills: Dict[str, List[str]]) -> Dict[str, Any]`
   - Classifies missing keywords into Tier 1/2/3
   - Filters out keywords already in CV

10. `_extract_existing_cv_keywords(self) -> set`
    - Extracts keywords from latest CV (original or tailored)

11. `_extract_keywords_from_cv_file(self, cv_file: Path) -> set`
    - Extracts keywords from CV JSON file

12. `_keyword_exists_in_cv(self, keyword: str, cv_keywords: set) -> bool`
    - Checks if keyword exists in CV (with fuzzy matching)

13. `_is_specific_tool_variant(self, keyword: str, cv_technical_lower: List[str]) -> bool`
    - Checks if keyword is a specific tool variant

---

## 🔍 Match Summary Generation Flow

### **Step 1: Source Data**

**File:** `{company}_skills_analysis.json`

**Structure:**
```json
{
  "cv_skills": {...},
  "jd_skills": {...},
  "preextracted_comparison_entries": [
    {
      "timestamp": "2025-11-21T00:51:58.456679",
      "model_used": "gpt-4o",
      "content": "🎯 OVERALL SUMMARY\n...\n🔹 TECHNICAL SKILLS\n  ✅ MATCHED JD REQUIREMENTS...\n  ❌ MISSING FROM CV...\n🔹 SOFT SKILLS\n..."
    }
  ]
}
```

### **Step 2: Extract Match Summary**

**Method:** `_extract_match_summary(preextracted_entries)`

**Process:**
1. Gets latest entry from `preextracted_comparison_entries`
2. Extracts `content` field (formatted text)
3. Parses text line by line to find:
   - Category markers: "Technical Skills", "Soft Skills", "Domain Keywords"
   - Matched skills: Lines with "CV Has: 'skill'"
   - Missing skills: Lines with "JD Requires: 'skill'" or "JD Required: 'skill'"
   - Match rates: Lines with "Match Rate: X%"

**Code Logic:**
```python
current_category = None
for line in content.split("\n"):
    # Detect category sections
    if "Technical Skills" in line:
        current_category = "technical"
    elif "Soft Skills" in line:
        current_category = "soft"
    elif "Domain Keywords" in line:
        current_category = "domain"
    
    # Extract matched skills
    if ("CV Has:" in line or "CV has:" in line) and current_category:
        skill = line.split("'")[1]  # Extract from quotes
        match_summary["by_category"][current_category]["matched"].append(skill)
    
    # Extract missing skills
    if ("JD Required:" in line or "JD Requires:" in line) and current_category:
        skill = line.split("'")[1]  # Extract from quotes
        match_summary["by_category"][current_category]["missing"].append(skill)
```

### **Step 3: Format Output**

**Output Structure:**
```json
{
  "overall_match_rate": 25.0,
  "by_category": {
    "technical": {
      "matched": [],
      "missing": [],
      "match_rate": 0
    },
    "soft": {
      "matched": [],
      "missing": [],
      "match_rate": 0
    },
    "domain": {
      "matched": [],
      "missing": ["Excel", "Power BI", ...],
      "match_rate": 0.0
    }
  },
  "missing_keywords": {
    "technical": [],
    "soft": [],
    "domain": ["Excel", "Power BI", ...]
  }
}
```

---

## 🚨 ISSUE IDENTIFIED

### **Problem: Preextracted Comparison Format Mismatch**

**ACTUAL FORMAT (from VPS):**
```
🔹 TECHNICAL SKILLS
  ✅ MATCHED JD REQUIREMENTS (3 items):
    1. JD Required: 'Excel'
       → Found in CV: 'Excel'
       💡 brief reasoning: Exact match; both refer to the same software tool.
  ❌ MISSING FROM CV (2 items):
    1. JD Requires: 'SQL'
       💡 brief reason why not found: No direct match; SQL is not listed in the CV.
```

**PARSER EXPECTS:**
- `"CV Has:"` or `"CV has:"` for matched skills
- `"JD Required:"` or `"JD Requires:"` for missing skills

**ACTUAL FORMAT USES:**
- `"→ Found in CV: 'skill'"` for matched skills (NOT "CV Has:")
- `"JD Required: 'skill'"` for matched JD requirements
- `"JD Requires: 'skill'"` for missing JD requirements

**VERIFIED PATTERNS:**
- ✅ Contains "Technical Skills": True
- ✅ Contains "Soft Skills": True
- ✅ Contains "Domain Keywords": True
- ❌ Contains "CV Has:": False (0 occurrences)
- ❌ Contains "CV has:": False (0 occurrences)
- ✅ Contains "→ Found in CV:": True (6 occurrences)
- ✅ Contains "JD Required:": True (6 occurrences - for matched)
- ✅ Contains "JD Requires:": True (9 occurrences - for missing)

**This mismatch causes:**
- ❌ **NO matched skills extracted** (parser looks for "CV Has:" but format uses "→ Found in CV:")
- ✅ Missing skills ARE extracted correctly (parser correctly looks for "JD Requires:")
- ❌ Match rates calculated incorrectly (no matched skills = wrong percentages)

---

## 📊 Services That Generate Skills Analysis

### **1. SkillExtractionResultSaver**

**File:** `cv-magic-app/backend/app/services/skill_extraction/result_saver.py`

**Methods:**
- `save_analysis_results()` - Creates initial `skills_analysis.json`
- `append_analyze_match()` - Appends analyze match entries
- `append_preextracted_comparison()` - Appends preextracted comparison entries

**Called from:**
- `skills_analysis.py` - Main pipeline
- `context_aware_analysis_pipeline.py` - Context-aware pipeline

### **2. PreextractedComparator**

**File:** `cv-magic-app/backend/app/services/skill_extraction/preextracted_comparator.py`

**Methods:**
- `execute_skills_semantic_comparison()` - Main entry point (returns text)
- `execute_skills_comparison_with_json_output()` - Returns JSON dict
- `_format_json_to_text()` - Converts JSON to formatted text

**Format Generated:**
```
🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: 16
Matched: 0
Missing: 16
Match Rate: 0%

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills             5         5         0         0            0
Soft Skills                   4         4         0         0            0
Domain Keywords              0         7         0         7            0

🧠 DETAILED AI ANALYSIS
--------------------------------------------------------------------------------
🔹 TECHNICAL SKILLS
  ✅ MATCHED JD REQUIREMENTS (0 items):

  ❌ MISSING FROM CV (0 items):

🔹 SOFT SKILLS
  ✅ MATCHED JD REQUIREMENTS (0 items):

  ❌ MISSING FROM CV (0 items):

🔹 DOMAIN KEYWORDS
  ✅ MATCHED JD REQUIREMENTS (0 items):

  ❌ MISSING FROM CV (7 items):
    1. JD Requires: 'Excel'
       💡 ...
    2. JD Requires: 'Power BI'
       💡 ...
```

---

## 🔧 Root Cause Analysis

### **Issue 1: Parser Format Mismatch**

**Expected by parser:**
```
CV Has: 'skill'
JD Requires: 'skill'
```

**Actual format:**
```
JD Required: 'skill'
→ Found in CV: 'skill'
JD Requires: 'skill'
```

**Fix needed:** Update `_extract_match_summary()` to handle actual format

### **Issue 2: Category Detection**

The parser looks for:
- `"Technical Skills"` in line → sets category to "technical"
- `"Soft Skills"` in line → sets category to "soft"
- `"Domain Keywords"` in line → sets category to "domain"

But the format uses:
- `"🔹 TECHNICAL SKILLS"` (with emoji)
- `"🔹 SOFT SKILLS"` (with emoji)
- `"🔹 DOMAIN KEYWORDS"` (with emoji)

**This should work** because `"Technical Skills"` is in `"🔹 TECHNICAL SKILLS"`

### **Issue 3: All Keywords in Domain**

Looking at the input file, all 16 missing keywords are in the "domain" category. This suggests:
- Either the preextracted comparison is incorrectly categorizing
- Or the parser is not correctly extracting from technical/soft sections

---

## 📝 Files Involved

1. **`ats_recommendation_service.py`**
   - `_extract_match_summary()` - Parses preextracted comparison text

2. **`preextracted_comparator.py`**
   - `_format_json_to_text()` - Generates the text format
   - `execute_skills_semantic_comparison()` - Main entry point

3. **`result_saver.py`**
   - `append_preextracted_comparison()` - Saves to skills_analysis.json

4. **`skills_analysis.json`**
   - Contains `preextracted_comparison_entries` with formatted text

---

## ✅ Next Steps

1. **Check actual format** of preextracted_comparison content
2. **Fix parser** to match actual format
3. **Add debug prints** to see what's being parsed
4. **Verify category detection** is working correctly

