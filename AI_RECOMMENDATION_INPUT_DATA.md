# AI Recommendation Generation - Input Data Analysis

## 📋 Source File

**File:** `{company}_input_recommendation_{timestamp}.json`

**Example:** `Australia_for_UNHCR_input_recommendation_20251121_005158.json`

**Location:**
- VPS: `/app/user/{user_email}/cv-analysis/applied_companies/{company}/`
- Local: `cv-magic-app/user/{user_email}/cv-analysis/applied_companies/{company}/`

---

## 🔍 Data Flow

```
1. Input Recommendation File (JSON)
   ↓
2. AI Recommendation Generator loads file
   ↓
3. Prompt Template extracts data
   ↓
4. Prompt Template generates prompt string
   ↓
5. AI Service receives prompt
   ↓
6. AI generates JSON response
   ↓
7. Response saved as AI Recommendation File
```

---

## 📊 Data Extracted from Input Recommendation File

### **1. Metadata**
```json
{
  "company": "Australia_for_UNHCR",
  "generated_at": "2025-11-21T00:51:58.456679",
  "ats_score_current": 63.5,
  "match_rate_current": 25.0
}
```
**Used for:** Company name, timestamps, current scores

---

### **2. Skills Extraction**

#### **CV Skills:**
```json
{
  "technical": ["Python", "Power BI", "Tableau", "Excel", "Data Modelling"],
  "soft": ["Analytical Thinking", "Communication", "Problem Solving", "Teamwork"],
  "domain": []
}
```

#### **JD Skills:**
```json
{
  "technical": ["Excel", "Power BI", "SQL", "Tableau", "VBA"],
  "soft": ["communication", "customer service", "project management", "stakeholder management"],
  "domain": ["clean data", "data issues", "data mining", "data models", "data warehouse", "de-duplication", "marketing campaigns"]
}
```

**Used for:**
- Showing what CV has vs what JD requires
- Identifying matched vs missing keywords
- Keyword categorization

---

### **3. Preliminary Decision**
```json
{
  "decision": "PROCEED",
  "match_score": 90,
  "confidence": 85,
  "should_proceed": true,
  "critical_missing": [],
  "implicit_likely": ["Excel", "SQL", "Power BI", "Tableau"],
  "learnable_gaps": []
}
```

**Used for:**
- Match assessment in prompt
- Decision confidence
- Critical missing skills
- Implicit likely skills

---

### **4. Match Summary**

#### **Overall Match Rate:**
```json
{
  "overall_match_rate": 25.0
}
```

#### **By Category:**
```json
{
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
    "missing": [
      "Excel", "Power BI", "Tableau", "SQL", "VBA",
      "communication", "customer service", "project management", "stakeholder management",
      "clean data", "data issues", "data mining", "data models", "data warehouse",
      "de-duplication", "marketing campaigns"
    ],
    "match_rate": 0.0
  }
}
```

**⚠️ ISSUE FOUND:** The match summary shows ALL keywords in "domain" category, but they should be split into technical/soft/domain. This is incorrect data structure.

**Used for:**
- Showing match rates per category
- Listing matched keywords (already in CV)
- Listing missing keywords (need to be categorized by AI)

---

### **5. Keyword Integration Guidance**

```json
{
  "tier1_always_add": {
    "technical": [],
    "soft": [],
    "domain": []
  },
  "tier2_add_if_evidence": {
    "technical": [],
    "soft": [],
    "domain": ["VBA", "customer service", "data mining", "data models", "data warehouse", "marketing campaigns"]
  },
  "tier3_never_add": {
    "technical": [],
    "soft": [],
    "domain": []
  },
  "already_in_cv_filtered": [
    "Excel", "Power BI", "project management", "SQL", "clean data",
    "Tableau", "stakeholder management", "de-duplication", "communication", "data issues"
  ]
}
```

**Used for:**
- Pre-classified keyword tiers (reference only)
- Already-in-CV keywords (to exclude from missing list)
- Integration instructions

---

### **6. Component Summary**

```json
{
  "skills_relevance": 80.0,
  "experience_alignment": 85.0,
  "role_similarity": 70.0,
  "seniority_match": 90.0,
  "industry_fit": 65.0,
  "required_skills_coverage": 75.0,
  "tech_stack_similarity": 70.0,
  "business_readiness": 80.0,
  "industry_transition_fit": 65.0
}
```

**⚠️ ISSUE FOUND:** The prompt template expects nested structure like:
```json
{
  "technical": { "score": 77.5, "core_match": 80, "stack_fit": 75 },
  "skills": { "score": 85, "business_readiness": 85 },
  "experience": { "alignment_score": 63.8, "years": 5 },
  "seniority": { "score": 70, "cv_level": "Senior", "jd_level": "Mid" },
  "industry": { "alignment_score": 50, "cv_industry": "Tech", "jd_industry": "NFP" }
}
```

But the actual file has flat structure. This mismatch could cause issues.

**Used for:**
- Component scores in prompt
- Technical depth analysis
- Experience alignment
- Seniority matching
- Industry fit assessment

---

### **7. ATS Scoring**

```json
{
  "final_score": 63.5,
  "category1_score": 32.0,
  "category2_score": 27.1,
  "category3_score": 0,
  "improvement_needed": 11.5,
  "category1_keywords": 32.0,
  "category2_ai_analysis": 27.1,
  "missing_counts": {
    "technical": 1,
    "soft": 4,
    "domain": 7
  },
  "scoring_version": "v2_65_35_split"
}
```

**Used for:**
- Current ATS score display
- Target score calculation
- Improvement needed calculation
- Missing keyword counts
- Category breakdown

---

### **8. Tailoring Strategy**

**⚠️ MISSING:** The input file does NOT contain `tailoring_strategy` section, but the prompt template expects it:

```python
tailoring_strategy = analysis_data.get("tailoring_strategy", {})
primary_objective = tailoring_strategy.get("primary_objective", "Optimize CV for target role")
emphasis_areas = tailoring_strategy.get("emphasis_areas", [])
de_emphasize_areas = tailoring_strategy.get("de_emphasize", [])
tone_guidance = tailoring_strategy.get("tone_guidance", "Professional and results-oriented")
industry_bridging = tailoring_strategy.get("industry_bridging", [])
```

**Impact:** These will all be empty/default values, which may affect recommendation quality.

---

## 🔧 How Data is Used in Prompt Generation

### **Step 1: Load Input File**
```python
# File: ai_recommendation_generator.py
input_file = self._get_input_recommendation_file_path(company)
with open(input_file, 'r', encoding='utf-8') as f:
    analysis_data = json.load(f)
```

### **Step 2: Extract Data Sections**
```python
# File: ai_recommendation_prompt_template.py
metadata = analysis_data.get("metadata", {})
skills_extraction = analysis_data.get("skills_extraction", {})
preliminary_decision = analysis_data.get("preliminary_decision", {})
match_summary = analysis_data.get("match_summary", {})
keyword_guidance = analysis_data.get("keyword_integration_guidance", {})
component_summary = analysis_data.get("component_summary", {})
tailoring_strategy = analysis_data.get("tailoring_strategy", {})  # ⚠️ MISSING
ats_scoring = analysis_data.get("ats_scoring", {})
```

### **Step 3: Filter Missing Keywords**
```python
# Filter out keywords already in CV
already_in_cv_filtered = keyword_guidance.get("already_in_cv_filtered", [])

# Filter missing keywords
technical_match['missing'] = filter_missing_keywords(
    technical_match['missing'], 
    technical_match.get('matched', []),
    already_in_cv_filtered
)
```

### **Step 4: Generate Prompt String**
The prompt template uses f-string formatting to insert all extracted data into a structured prompt that includes:

1. **Current ATS Performance** - from `ats_scoring`
2. **Match Assessment** - from `preliminary_decision`
3. **Skills Match** - from `match_summary`
4. **Missing Keywords Lists** - from filtered `match_summary.by_category`
5. **Component Scores** - from `component_summary`
6. **Keyword Tiers (Reference)** - from `keyword_integration_guidance`
7. **Strategic Guidance** - from `tailoring_strategy` (⚠️ MISSING)

---

## 🚨 Issues Found

### **Issue 1: Missing Tailoring Strategy**
- **Problem:** `tailoring_strategy` section is missing from input file
- **Impact:** Strategic guidance (emphasis areas, tone, bridging) will be empty
- **Fix:** Need to add tailoring_strategy generation in `ats_recommendation_service.py`

### **Issue 2: Incorrect Match Summary Structure**
- **Problem:** All keywords are in "domain" category instead of technical/soft/domain
- **Impact:** AI will receive incorrect missing keyword lists
- **Fix:** Need to fix `_extract_match_summary()` in `ats_recommendation_service.py`

### **Issue 3: Component Summary Structure Mismatch**
- **Problem:** Flat structure vs expected nested structure
- **Impact:** Component scores may not display correctly in prompt
- **Fix:** Need to align structure or update prompt template to handle flat structure

### **Issue 4: Empty Matched Lists**
- **Problem:** `matched` lists are empty for all categories
- **Impact:** AI doesn't know what's already in CV
- **Fix:** Need to fix match extraction logic

---

## 📝 What Gets Sent to AI

The final prompt sent to AI contains:

1. **Role & Objective** - Instructions for AI
2. **Current ATS Performance** - Score, status, target, improvement needed
3. **Match Assessment** - Decision, confidence, match score, critical missing
4. **Skills Match Breakdown** - Technical/Soft/Domain match rates and counts
5. **Missing Keywords Lists** - Filtered lists of keywords NOT in CV
6. **Already in CV Keywords** - List of keywords to exclude from categorization
7. **Component Scores** - Technical, skills, experience, seniority, industry scores
8. **ATS Breakdown** - Category 1 and Category 2 scores
9. **Keyword Tiers (Reference)** - Pre-classified tiers (for reference only)
10. **Strategic Guidance** - Primary objective, tone, emphasis areas (⚠️ MISSING)
11. **Output Format Requirements** - JSON structure specification
12. **Validation Rules** - Requirements for keyword categorization

---

## ✅ Summary

**Input File:** `{company}_input_recommendation_{timestamp}.json`

**Data Sections Used:**
1. ✅ `metadata` - Company, timestamps, scores
2. ✅ `skills_extraction` - CV and JD skills
3. ✅ `preliminary_decision` - Match decision and confidence
4. ✅ `match_summary` - Match rates and missing keywords (⚠️ STRUCTURE ISSUE)
5. ✅ `keyword_integration_guidance` - Pre-classified tiers and already-in-CV list
6. ✅ `component_summary` - Component scores (⚠️ STRUCTURE MISMATCH)
7. ❌ `tailoring_strategy` - **MISSING** (will use defaults)
8. ✅ `ats_scoring` - ATS scores and missing counts

**Prompt Template:** `cv-magic-app/backend/prompt/ai_recommendation_prompt_template.py`

**Output:** Generated prompt string sent to AI service

