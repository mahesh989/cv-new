# AI Recommendation Generation & CV Tailoring Flow Analysis

## 📊 Complete Flow Overview

```
1. Skills Analysis Pipeline
   ↓
2. Input Recommendation File Creation (input_recommendation.json)
   ↓
3. AI Recommendation Generation (ai_recommendation.json)
   ↓
4. CV Tailoring (uses ai_recommendation.json)
```

---

## 🔍 Step-by-Step Analysis

### **Step 1: Input Recommendation File Creation**

**File:** `cv-magic-app/backend/app/services/ats_recommendation_service.py`

**Method:** `extract_ats_recommendation_data(company)`

**Inputs Used:**
- Skills analysis file: `{company}_skills_analysis.json`
  - `cv_skills` (technical, soft, domain)
  - `jd_skills` (technical, soft, domain)
  - `analyze_match_entries` → preliminary decision
  - `preextracted_comparison_entries` → match summary
  - `component_analysis_entries` → component summary
  - `ats_calculation_entries` → ATS scoring

**Output:** `{company}_input_recommendation_{timestamp}.json`

**Structure:**
```json
{
  "metadata": {
    "company": "Australia_for_UNHCR",
    "generated_at": "2025-11-21T04:51:56.724049",
    "ats_score_current": 61.8,
    "match_rate_current": 40.0
  },
  "skills_extraction": {
    "cv": { "technical": [...], "soft": [...], "domain": [...] },
    "jd": { "technical": [...], "soft": [...], "domain": [...] }
  },
  "preliminary_decision": {
    "decision": "DONT_PROCEED",
    "match_score": 50,
    "confidence": 100,
    "critical_missing": [...],
    "implicit_likely": [...]
  },
  "match_summary": {
    "overall_match_rate": 40.0,
    "by_category": {
      "technical": { "matched": [...], "missing": [...], "match_rate": 60.0 },
      "soft": { "matched": [...], "missing": [...], "match_rate": 25.0 },
      "domain": { "matched": [...], "missing": [...], "match_rate": 0.0 }
    }
  },
  "keyword_integration_guidance": {
    "tier1_always_add": { "technical": [...], "soft": [...], "domain": [] },
    "tier2_add_if_evidence": { "technical": [...], "soft": [...], "domain": [] },
    "tier3_never_add": { "technical": [...], "soft": [...], "domain": [...] },
    "already_in_cv_filtered": [...]
  },
  "component_summary": {
    "technical": { "score": 77.5, "core_match": 80, "stack_fit": 75 },
    "skills": { "score": 85, "business_readiness": 85 },
    "experience": { "alignment_score": 63.8, "years": 5, "corporate_years": 5 },
    "seniority": { "score": 70, "cv_level": "Senior", "jd_level": "Mid" },
    "industry": { "alignment_score": 50, "cv_industry": "Tech", "jd_industry": "NFP", "transition_difficulty": "MODERATE" }
  },
  "ats_scoring": {
    "final_score": 61.8,
    "category1_keywords": 35.2,
    "category2_ai_analysis": 25.3,
    "missing_counts": { "technical": 1, "soft": 3, "domain": 6 },
    "scoring_version": "v2_65_35_split"
  },
  "tailoring_strategy": {
    "primary_objective": "Optimize CV for Data Analyst role",
    "emphasis_areas": [...],
    "de_emphasize": [...],
    "critical_additions": {...},
    "tone_guidance": "Professional and results-oriented",
    "industry_bridging": [...]
  }
}
```

**Key Features:**
- ✅ Pre-filters keywords already in CV (from tailored CV if exists)
- ✅ Classifies missing keywords into Tier 1/2/3
- ✅ Extracts component scores and ATS breakdown
- ✅ Provides tailoring strategy guidance

---

### **Step 2: AI Recommendation Generation**

**File:** `cv-magic-app/backend/app/services/ai_recommendation_generator.py`

**Method:** `generate_ai_recommendation(company, force_regenerate)`

**Inputs Used:**
- `{company}_input_recommendation_{timestamp}.json` (from Step 1)
- Prompt template: `cv-magic-app/backend/prompt/ai_recommendation_prompt_template.py`

**Process:**
1. Loads `input_recommendation.json`
2. Generates prompt using `generate_ai_recommendation_prompt(company, analysis_data)`
3. Calls AI service with prompt
4. Parses AI JSON response
5. Converts to markdown for frontend display
6. Extracts actionable guidance for CV generation

**Output:** `{company}_ai_recommendation_{timestamp}.json`

**Structure:**
```json
{
  "company": "Australia_for_UNHCR",
  "generated_at": "2025-11-21T04:51:56.724049",
  "recommendation_content": "# CV Tailoring Strategy Report...",
  "structured_recommendations": {
    "executive_summary": {
      "current_ats_score": 61.8,
      "target_score": 75.0,
      "improvement_needed": 13.2,
      "overall_match_rate": 40.0,
      "primary_objective": "Optimize CV for Data Analyst role",
      "key_challenge": "MODERATE industry transition from Tech to NFP"
    },
    "keyword_integration": {
      "tier1_integrate_immediately": {
        "technical": [
          {
            "keyword": "SQL",
            "basis": "Generic database skill, transferable",
            "integration": "Add to skills section and mention in data analysis bullets",
            "validation": "Can discuss experience with data querying",
            "risk": "low"
          }
        ],
        "soft": [...],
        "domain": []
      },
      "tier2_add_with_evidence": {
        "technical": [...],
        "soft": [...],
        "domain": []
      },
      "tier3_never_add": {
        "technical": [...],
        "domain": [...]
      }
    },
    "experience_reframing": {...},
    "strategic_warnings": {...},
    "implementation_roadmap": {...},
    "tone_and_style": {...}
  },
  "actionable_guidance": {
    "tier1_add_immediately": {
      "technical": [...],
      "soft": [...],
      "domain": []
    },
    "tier2_add_with_evidence": {...},
    "tier3_never_add": [...],
    "strategic_positioning": {...},
    "experience_optimization": {...},
    "achievements": {...},
    "implementation_plan": {...},
    "messaging": {...}
  },
  "ai_model_info": {
    "provider": "openai",
    "model": "gpt-4o",
    "cost": 0.03005,
    "tokens_used": 3757
  },
  "metadata": {
    "content_length": 2884,
    "format_version": "2.0",
    "has_structured_data": true,
    "has_actionable_guidance": true
  }
}
```

**Key Features:**
- ✅ Uses `input_recommendation.json` as input
- ✅ AI categorizes ALL missing keywords into Tier 1/2/3
- ✅ Provides structured JSON + markdown for display
- ✅ Extracts actionable guidance for programmatic CV generation

---

### **Step 3: CV Tailoring**

**File:** `cv-magic-app/backend/app/tailored_cv/services/cv_tailoring_service.py`

**Method:** `load_real_cv_and_recommendation(company)`

**Inputs Used:**
- Latest CV (original or tailored): `{company}_tailored_cv_{timestamp}.json` or `original_cv.json`
- AI Recommendation: `{company}_ai_recommendation_{timestamp}.json`

**Process:**
1. Loads latest CV (prefers tailored if exists)
2. Loads AI recommendation file via `load_recommendation_file()`
3. Parses recommendation using `RecommendationParser.parse_recommendation_file()`
4. Creates `RecommendationAnalysis` object
5. Passes to `tailor_cv()` method

**Recommendation Parser Priority:**
1. **Priority 1:** `actionable_guidance` (v2.0+ - preferred)
2. **Priority 2:** `structured_recommendations` (v2.0)
3. **Priority 3:** `recommendation_content` (v1.0 - markdown fallback)

**Parser File:** `cv-magic-app/backend/app/tailored_cv/services/recommendation_parser.py`

**Key Methods:**
- `parse_actionable_guidance()` - Extracts tier1/tier2/tier3 keywords with full metadata
- `parse_structured_recommendations()` - Extracts from structured JSON
- `parse_markdown_content()` - Fallback markdown parsing

---

## 🐛 Potential Issues & Debug Points

### **Issue 1: AI Recommendations Not Using Correct Input Data**

**Check:**
- ✅ Is `input_recommendation.json` being created correctly?
- ✅ Does it contain all required sections?
- ✅ Are missing keywords properly filtered (not including already-in-CV keywords)?

**Debug Points:**
1. `ats_recommendation_service.py:extract_ats_recommendation_data()` - Check extracted data
2. `ai_recommendation_generator.py:_load_ai_prompt()` - Check prompt generation
3. `ai_recommendation_prompt_template.py:generate_ai_recommendation_prompt()` - Check prompt content

### **Issue 2: AI Not Categorizing Keywords Correctly**

**Check:**
- ✅ Are missing keywords properly listed in prompt?
- ✅ Are matched keywords excluded from missing list?
- ✅ Are already-in-CV keywords filtered out?

**Debug Points:**
1. Prompt generation - check missing keywords list
2. AI response - check if all keywords are categorized
3. Keyword count validation - tier1 + tier2 + tier3 = total missing

### **Issue 3: CV Tailoring Not Using Correct Recommendations**

**Check:**
- ✅ Is correct AI recommendation file being loaded?
- ✅ Is parser using correct priority (actionable_guidance > structured > markdown)?
- ✅ Are tier keywords being extracted correctly?

**Debug Points:**
1. `cv_tailoring_service.py:load_recommendation_file()` - Check file selection
2. `recommendation_parser.py:parse_recommendation_file()` - Check parsing method
3. `recommendation_parser.py:parse_actionable_guidance()` - Check tier extraction

---

## 📝 Debug Prints to Add

### **1. Input Recommendation Creation**

**File:** `ats_recommendation_service.py`

```python
def extract_ats_recommendation_data(self, company: str) -> Optional[Dict[str, Any]]:
    logger.info(f"🔍 [INPUT_RECOMMENDATION] Starting extraction for {company}")
    
    # ... existing code ...
    
    # After extracting match summary
    logger.info(f"📊 [INPUT_RECOMMENDATION] Match Summary:")
    logger.info(f"   - Overall match rate: {match_summary.get('overall_match_rate', 0)}%")
    logger.info(f"   - Technical: {len(technical_match.get('matched', []))} matched, {len(technical_match.get('missing', []))} missing")
    logger.info(f"   - Soft: {len(soft_match.get('matched', []))} matched, {len(soft_match.get('missing', []))} missing")
    logger.info(f"   - Domain: {len(domain_match.get('matched', []))} matched, {len(domain_match.get('missing', []))} missing")
    
    # After keyword classification
    logger.info(f"🔍 [INPUT_RECOMMENDATION] Keyword Classification:")
    logger.info(f"   - Tier 1 (always add): Technical={len(classified['tier1_always_add']['technical'])}, Soft={len(classified['tier1_always_add']['soft'])}")
    logger.info(f"   - Tier 2 (with evidence): Technical={len(classified['tier2_add_if_evidence']['technical'])}, Soft={len(classified['tier2_add_if_evidence']['soft'])}")
    logger.info(f"   - Tier 3 (never add): Technical={len(classified['tier3_never_add']['technical'])}, Domain={len(classified['tier3_never_add']['domain'])}")
    logger.info(f"   - Already in CV (filtered): {len(classified['already_in_cv_filtered'])}")
    
    # After creating recommendation_data
    logger.info(f"✅ [INPUT_RECOMMENDATION] Created recommendation data:")
    logger.info(f"   - ATS Score: {ats_scoring.get('final_score', 0)}")
    logger.info(f"   - Missing counts: Technical={missing_counts.get('technical', 0)}, Soft={missing_counts.get('soft', 0)}, Domain={missing_counts.get('domain', 0)}")
```

### **2. AI Prompt Generation**

**File:** `ai_recommendation_prompt_template.py`

```python
def generate_ai_recommendation_prompt(company: str, analysis_data: dict) -> str:
    logger.info(f"🔍 [AI_PROMPT] Generating prompt for {company}")
    
    # After filtering missing keywords
    logger.info(f"📊 [AI_PROMPT] Missing Keywords (after filtering):")
    logger.info(f"   - Technical: {len(technical_match.get('missing', []))} keywords")
    logger.info(f"   - Soft: {len(soft_match.get('missing', []))} keywords")
    logger.info(f"   - Domain: {len(domain_match.get('missing', []))} keywords")
    logger.info(f"   - Already in CV (excluded): {len(already_in_cv_filtered)} keywords")
    
    # Log first few missing keywords
    if technical_match.get('missing'):
        logger.info(f"   - Technical missing (first 5): {technical_match.get('missing', [])[:5]}")
    if soft_match.get('missing'):
        logger.info(f"   - Soft missing (first 5): {soft_match.get('missing', [])[:5]}")
    
    # After prompt generation
    logger.info(f"✅ [AI_PROMPT] Generated prompt ({len(prompt)} characters)")
    logger.info(f"   - Contains {len(technical_match.get('missing', []))} technical missing keywords")
    logger.info(f"   - Contains {len(soft_match.get('missing', []))} soft missing keywords")
```

### **3. AI Response Parsing**

**File:** `ai_recommendation_generator.py`

```python
def _structure_ai_response(self, ai_response: AIResponse, company: str) -> Dict[str, Any]:
    logger.info(f"🔍 [AI_RESPONSE] Parsing AI response for {company}")
    
    # After parsing JSON
    if json_data:
        logger.info(f"✅ [AI_RESPONSE] Successfully parsed JSON")
        
        # Check keyword categorization
        keyword_integration = json_data.get('keyword_integration', {})
        tier1 = keyword_integration.get('tier1_integrate_immediately', {})
        tier2 = keyword_integration.get('tier2_add_with_evidence', {})
        tier3 = keyword_integration.get('tier3_never_add', {})
        
        tier1_count = len(tier1.get('technical', [])) + len(tier1.get('soft', [])) + len(tier1.get('domain', []))
        tier2_count = len(tier2.get('technical', [])) + len(tier2.get('soft', [])) + len(tier2.get('domain', []))
        tier3_count = len(tier3.get('technical', [])) + len(tier3.get('soft', [])) + len(tier3.get('domain', []))
        
        logger.info(f"📊 [AI_RESPONSE] Keyword Categorization:")
        logger.info(f"   - Tier 1: {tier1_count} keywords")
        logger.info(f"   - Tier 2: {tier2_count} keywords")
        logger.info(f"   - Tier 3: {tier3_count} keywords")
        logger.info(f"   - Total categorized: {tier1_count + tier2_count + tier3_count}")
        
        # Check if actionable_guidance was extracted
        actionable = self._extract_actionable_guidance(json_data)
        if actionable:
            logger.info(f"✅ [AI_RESPONSE] Extracted actionable guidance:")
            logger.info(f"   - Tier 1: {len(actionable.get('tier1_add_immediately', {}).get('technical', []))} technical")
            logger.info(f"   - Tier 2: {len(actionable.get('tier2_add_with_evidence', {}).get('technical', []))} technical")
```

### **4. Recommendation Parsing**

**File:** `recommendation_parser.py`

```python
@staticmethod
def parse_recommendation_file(file_path: str) -> Dict[str, Any]:
    logger.info(f"🔍 [RECOMMENDATION_PARSER] Parsing {file_path}")
    
    # After detecting format
    logger.info(f"📊 [RECOMMENDATION_PARSER] Format detected:")
    logger.info(f"   - Version: {format_version}")
    logger.info(f"   - Has actionable_guidance: {has_actionable}")
    logger.info(f"   - Has structured_recommendations: {has_structured}")
    logger.info(f"   - Has recommendation_content: {has_markdown}")
    logger.info(f"   - Using parser: {parsing_method_used}")
    
    # After parsing actionable_guidance
    if has_actionable:
        logger.info(f"✅ [RECOMMENDATION_PARSER] Parsed actionable_guidance:")
        logger.info(f"   - Tier 1 technical: {len(tier1_technical)} keywords")
        logger.info(f"   - Tier 1 soft: {len(tier1_soft)} keywords")
        logger.info(f"   - Tier 2 technical: {len(tier2_technical)} keywords")
        logger.info(f"   - Tier 3 avoid: {len(tier3_keywords)} keywords")
        logger.info(f"   - Missing technical (combined): {len(missing_technical_skills)}")
        logger.info(f"   - Missing soft (combined): {len(missing_soft_skills)}")
```

### **5. CV Tailoring Loading**

**File:** `cv_tailoring_service.py`

```python
def load_recommendation_file(self, company_folder: str) -> RecommendationAnalysis:
    logger.info(f"🔍 [CV_TAILORING] Loading recommendation for {company_folder}")
    
    # After finding file
    logger.info(f"📄 [CV_TAILORING] Found recommendation file: {latest_file}")
    logger.info(f"   - File size: {latest_file.stat().st_size / 1024:.1f} KB")
    logger.info(f"   - Modified: {datetime.fromtimestamp(latest_file.stat().st_mtime)}")
    
    # After parsing
    logger.info(f"✅ [CV_TAILORING] Parsed recommendation:")
    logger.info(f"   - Company: {parsed_data.get('company')}")
    logger.info(f"   - Missing technical: {len(parsed_data.get('missing_technical_skills', []))}")
    logger.info(f"   - Missing soft: {len(parsed_data.get('missing_soft_skills', []))}")
    logger.info(f"   - Has tier1_keywords: {bool(parsed_data.get('tier1_keywords'))}")
    logger.info(f"   - Has tier2_keywords: {bool(parsed_data.get('tier2_keywords'))}")
    logger.info(f"   - Has tier3_avoid: {bool(parsed_data.get('tier3_avoid'))}")
```

---

## 📋 Files to Copy from VPS

### **Input Recommendation File**
```
Path: /app/user/{user_email}/cv-analysis/applied_companies/{company}/{company}_input_recommendation_{timestamp}.json
Example: /app/user/punam@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/Australia_for_UNHCR_input_recommendation_20251121_045156.json
```

### **AI Recommendation File**
```
Path: /app/user/{user_email}/cv-analysis/applied_companies/{company}/{company}_ai_recommendation_{timestamp}.json
Example: /app/user/punam@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/Australia_for_UNHCR_ai_recommendation_20251121_045156.json
```

### **Copy Command (from VPS to macOS)**
```bash
# From VPS
scp user@vps:/app/user/punam@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/*_input_recommendation*.json ~/Downloads/
scp user@vps:/app/user/punam@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/*_ai_recommendation*.json ~/Downloads/
```

---

## ✅ Next Steps

1. **Add debug prints** to track data flow at each step
2. **Copy latest files** from VPS to analyze actual data
3. **Compare input vs output** to identify where recommendations go wrong
4. **Check keyword categorization** - ensure all missing keywords are categorized
5. **Validate tier assignments** - ensure Tier 1/2/3 assignments are correct

