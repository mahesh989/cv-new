# ATS Recommendation Service - Complete Method Reference

## 📁 File Location
`cv-magic-app/backend/app/services/ats_recommendation_service.py`

## 🏗️ Class Structure

### **Class: `ATSRecommendationService`**

---

## 📋 Method Signatures

### **1. `__init__(self, user_email: str)`**
- **Purpose:** Initialize service with user email
- **Parameters:**
  - `user_email: str` - User email address
- **Sets:**
  - `self.user_email` - User email
  - `self.base_dir` - Base directory path from `get_user_base_path(user_email)`

---

### **2. `extract_ats_recommendation_data(self, company: str) -> Optional[Dict[str, Any]]`**
- **Purpose:** Extract and optimize recommendation data from skills analysis file
- **Parameters:**
  - `company: str` - Company name
- **Returns:**
  - `Optional[Dict[str, Any]]` - Optimized dictionary for AI consumption or None
- **Process:**
  1. Locates `{company}_skills_analysis.json` file
  2. Reads analysis data
  3. Extracts components:
     - `preliminary_decision` from `analyze_match_entries`
     - `match_summary` from `preextracted_comparison_entries`
     - `component_summary` from `component_analysis_entries`
     - `ats_scoring` from `ats_calculation_entries`
  4. Generates optimized recommendation data structure
  5. Classifies keywords into tiers

---

### **3. `save_optimized_recommendation(self, company: str, data: Dict[str, Any]) -> Optional[Path]`**
- **Purpose:** Save optimized recommendation data to file
- **Parameters:**
  - `company: str` - Company name
  - `data: Dict[str, Any]` - Recommendation data dictionary
- **Returns:**
  - `Optional[Path]` - Path to saved file or None if failed
- **Output File:**
  - `{company}_input_recommendation_{timestamp}.json`

---

### **4. `create_recommendation_file(self, company: str) -> bool`**
- **Purpose:** Create ATS recommendation file (convenience method)
- **Parameters:**
  - `company: str` - Company name
- **Returns:**
  - `bool` - True if successful, False otherwise
- **Process:**
  1. Calls `extract_ats_recommendation_data(company)`
  2. Calls `save_optimized_recommendation(company, data)`

---

### **5. `_extract_preliminary_decision(self, match_entries: List[Dict]) -> Dict[str, Any]`**
- **Purpose:** Extract simplified preliminary decision from analyze match entries
- **Parameters:**
  - `match_entries: List[Dict]` - List of analyze match entries
- **Returns:**
  - `Dict[str, Any]` - Structured decision data
- **Extracts:**
  - `decision` - PROCEED/MAYBE/DONT_PROCEED
  - `match_score` - Numeric score
  - `confidence` - Confidence level
  - `should_proceed` - Boolean
  - `critical_missing` - List of critical missing skills
  - `implicit_likely` - List of implicit likely skills
  - `learnable_gaps` - List of learnable gaps

---

### **6. `_extract_match_summary(self, preextracted_entries: List[Dict]) -> Dict[str, Any]`**
- **Purpose:** Extract clean match summary from preextracted comparison entries
- **Parameters:**
  - `preextracted_entries: List[Dict]` - List of preextracted comparison entries
- **Returns:**
  - `Dict[str, Any]` - Match summary with by_category structure
- **Structure:**
  ```python
  {
    "overall_match_rate": float,
    "by_category": {
      "technical": {"matched": [], "missing": [], "match_rate": float},
      "soft": {"matched": [], "missing": [], "match_rate": float},
      "domain": {"matched": [], "missing": [], "match_rate": float}
    },
    "missing_keywords": {
      "technical": [],
      "soft": [],
      "domain": []
    }
  }
  ```
- **⚠️ ISSUE:** Parser looks for "CV Has:" but actual format uses "→ Found in CV:"

---

### **7. `_extract_component_summary(self, component_entries: List[Dict]) -> Dict[str, Any]`**
- **Purpose:** Extract clean component summary from component analysis entries
- **Parameters:**
  - `component_entries: List[Dict]` - List of component analysis entries
- **Returns:**
  - `Dict[str, Any]` - Component scores
- **Extracts:**
  - `skills_relevance`
  - `experience_alignment`
  - `role_similarity`
  - `seniority_match`
  - `industry_fit`
  - `required_skills_coverage`
  - `tech_stack_similarity`
  - `business_readiness`
  - `industry_transition_fit`

---

### **8. `_extract_ats_scoring(self, ats_entries: List[Dict]) -> Dict[str, Any]`**
- **Purpose:** Extract clean ATS scoring from ATS calculation entries
- **Parameters:**
  - `ats_entries: List[Dict]` - List of ATS calculation entries
- **Returns:**
  - `Dict[str, Any]` - ATS scoring data
- **Extracts:**
  - `final_score`
  - `category1_score`
  - `category2_score`
  - `category3_score`
  - `improvement_needed`
  - `missing_counts`
  - `scoring_version`

---

### **9. `_classify_keywords(self, missing_keywords: Dict[str, List[str]], cv_skills: Dict[str, List[str]]) -> Dict[str, Any]`**
- **Purpose:** Classify missing keywords into tiers (Tier 1/2/3)
- **Parameters:**
  - `missing_keywords: Dict[str, List[str]]` - Missing keywords by category
  - `cv_skills: Dict[str, List[str]]` - CV skills by category
- **Returns:**
  - `Dict[str, Any]` - Classified keywords with tier structure
- **Process:**
  1. Extracts existing keywords from latest CV
  2. Filters missing keywords to exclude those already in CV
  3. Classifies remaining keywords:
     - **Tier 1:** Generic/transferable (always add)
     - **Tier 2:** Add if semantic evidence exists
     - **Tier 3:** Domain-specific/unverifiable (never add)
- **Returns:**
  ```python
  {
    "tier1_always_add": {"technical": [], "soft": [], "domain": []},
    "tier2_add_if_evidence": {"technical": [], "soft": [], "domain": []},
    "tier3_never_add": {"technical": [], "soft": [], "domain": []},
    "already_in_cv_filtered": [],
    "integration_instructions": "..."
  }
  ```

---

### **10. `_extract_existing_cv_keywords(self) -> set`**
- **Purpose:** Extract existing keywords from latest CV (original or tailored)
- **Returns:**
  - `set` - Set of lowercase keywords for case-insensitive matching
- **Process:**
  1. Gets latest tailored CV if exists
  2. Falls back to original CV
  3. Extracts keywords from skills and experience bullets

---

### **11. `_extract_keywords_from_cv_file(self, cv_file: Path) -> set`**
- **Purpose:** Extract keywords from a CV JSON file
- **Parameters:**
  - `cv_file: Path` - Path to CV JSON file
- **Returns:**
  - `set` - Set of lowercase keywords
- **Extracts from:**
  - Skills sections
  - Experience bullets (2-3 word phrases)
  - Role highlights

---

### **12. `_keyword_exists_in_cv(self, keyword: str, cv_keywords: set) -> bool`**
- **Purpose:** Check if keyword exists in CV keywords (with fuzzy matching)
- **Parameters:**
  - `keyword: str` - Keyword to check
  - `cv_keywords: set` - Set of CV keywords
- **Returns:**
  - `bool` - True if keyword exists (with variations)
- **Handles:**
  - Direct matches
  - Substring matches
  - Common variations (python/python programming, sql/mysql, etc.)

---

### **13. `_is_specific_tool_variant(self, keyword: str, cv_technical_lower: List[str]) -> bool`**
- **Purpose:** Check if keyword is a specific tool variant not in CV
- **Parameters:**
  - `keyword: str` - Keyword to check
  - `cv_technical_lower: List[str]` - CV technical skills (lowercase)
- **Returns:**
  - `bool` - True if specific variant without generic version
- **Examples:**
  - "postgresql" without "sql" → True
  - "django" without "python" → True

---

## 🔗 Related Services

### **1. `preextracted_comparator.py`**
- **Location:** `cv-magic-app/backend/app/services/skill_extraction/preextracted_comparator.py`
- **Key Methods:**
  - `execute_skills_semantic_comparison()` - Generates formatted text
  - `_format_json_to_text()` - Converts JSON to text format
- **Output Format:** Text with "→ Found in CV:" pattern

### **2. `result_saver.py`**
- **Location:** `cv-magic-app/backend/app/services/skill_extraction/result_saver.py`
- **Key Methods:**
  - `append_preextracted_comparison()` - Saves to skills_analysis.json
- **Saves to:** `preextracted_comparison_entries` array

### **3. `skills_analysis.json`**
- **Location:** `user/{email}/cv-analysis/applied_companies/{company}/{company}_skills_analysis.json`
- **Structure:**
  ```json
  {
    "preextracted_comparison_entries": [
      {
        "timestamp": "...",
        "model_used": "...",
        "content": "🎯 OVERALL SUMMARY\n..."
      }
    ]
  }
  ```

---

## 🐛 Known Issues

### **Issue 1: Match Summary Parser Format Mismatch**
- **Location:** `_extract_match_summary()` method
- **Problem:** Parser looks for "CV Has:" but format uses "→ Found in CV:"
- **Impact:** No matched skills are extracted
- **Fix:** Update parser to also look for "→ Found in CV:" pattern

### **Issue 2: Category Detection**
- **Status:** ✅ Working (looks for "Technical Skills", "Soft Skills", "Domain Keywords")
- **Note:** Works because these strings are present in the formatted text

---

## 📊 Data Flow

```
skills_analysis.json
  └─ preextracted_comparison_entries
      └─ content (formatted text)
          └─ _extract_match_summary()
              └─ match_summary (structured dict)
                  └─ extract_ats_recommendation_data()
                      └─ recommendation_data
                          └─ save_optimized_recommendation()
                              └─ {company}_input_recommendation_{timestamp}.json
```

