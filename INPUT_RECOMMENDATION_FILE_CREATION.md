# AI Recommendation Input File Creation - Complete Investigation

## 📋 Overview

The **Input Recommendation File** (`{company}_input_recommendation_{timestamp}.json`) is a structured JSON file that serves as input data for AI recommendation generation. This document explains how it's created, what data it contains, and the complete flow.

---

## 🔄 Creation Flow

```
1. Skills Analysis Pipeline Triggered
   ↓
2. JD Analysis (Step 1)
   ↓
3. CV-JD Matching (Step 2)
   ↓
4. Component Analysis (Step 3)
   ↓
5. ATS Calculation (Step 3)
   ↓
6. Input Recommendation File Creation (Step 4)
   ├── extract_ats_recommendation_data()
   │   ├── Read skills_analysis.json
   │   ├── Extract metadata
   │   ├── Extract skills (CV & JD)
   │   ├── Extract preliminary decision
   │   ├── Extract match summary
   │   ├── Extract component summary
   │   ├── Extract ATS scoring
   │   └── Classify keywords into tiers
   └── save_optimized_recommendation()
       └── Save to: {company}_input_recommendation_{timestamp}.json
```

---

## 📍 Entry Points

### **1. Automatic Pipeline (Primary Method)**

**Location:** `cv-magic-app/backend/app/routes/skills_analysis.py`

**Function:** `_run_pipeline(cname: str, token_data=None)`

**Step 4 (Lines 841-862):**
```python
# Step 4: Create Input Recommendation File
try:
    logger.info(f"📋 [PIPELINE] Creating input recommendation file for {cname}")
    from app.services.ats_recommendation_service import ATSRecommendationService
    recommendation_service = ATSRecommendationService(user_email=user_email)
    
    # Extract and save optimized recommendation
    recommendation_data = recommendation_service.extract_ats_recommendation_data(cname)
    if recommendation_data:
        saved_file = recommendation_service.save_optimized_recommendation(cname, recommendation_data)
        if saved_file:
            logger.info(f"✅ [PIPELINE] Input recommendation file created for {cname}: {saved_file}")
            pipeline_results["input_recommendation"] = True
```

**Triggered by:**
- Skills analysis API endpoint
- Context-aware analysis pipeline
- Complete pipeline trigger

---

### **2. Manual Creation Endpoint**

**Location:** `cv-magic-app/backend/app/routes/skills_analysis.py`

**Endpoint:** `POST /create-recommendation-file/{company}`

**Function:** `create_recommendation_file(company: str, force_update: bool = False)`

**Lines 2165-2209:**
```python
@router.post("/create-recommendation-file/{company}")
async def create_recommendation_file(company: str, force_update: bool = False):
    """Manually create or update a recommendation file for a company"""
    ats_service = ATSRecommendationService(user_email=current_user.email)
    success = ats_service.update_existing_recommendation(company, force_update)
```

---

## 🏗️ Service Implementation

### **Service Class:** `ATSRecommendationService`

**Location:** `cv-magic-app/backend/app/services/ats_recommendation_service.py`

**Purpose:** Creates optimized recommendation files with structured data, keyword tier classification, and pre-filtering.

---

## 🔧 Core Methods

### **1. `extract_ats_recommendation_data(company: str)`**

**Lines 31-143**

**What it does:**
1. Locates the skills analysis file (`{company}_skills_analysis.json`)
2. Reads and parses the JSON data
3. Extracts data from multiple sections:
   - CV skills & JD skills
   - Analyze match entries (preliminary decision)
   - Preextracted comparison entries (match summary)
   - Component analysis entries (component scores)
   - ATS calculation entries (ATS scores)
4. Calls helper methods to parse each section
5. Assembles the final recommendation data structure

**Key Helper Methods:**
- `_extract_preliminary_decision()` - Parses match decision
- `_extract_match_summary()` - Parses match rates and keywords
- `_extract_component_summary()` - Parses component scores
- `_extract_ats_scoring()` - Parses ATS scores
- `_classify_keywords()` - Classifies missing keywords into tiers

**Returns:** `Dict[str, Any]` with complete recommendation data structure

---

### **2. `save_optimized_recommendation(company: str, data: Dict[str, Any])`**

**Lines 145-175**

**What it does:**
1. Creates company directory if it doesn't exist
2. Generates timestamped filename: `{company}_input_recommendation_{timestamp}.json`
3. Saves JSON with clean formatting (indent=2)
4. Logs file size and success

**File Location:**
```
{user_base_path}/applied_companies/{company}/{company}_input_recommendation_{timestamp}.json
```

**Example:**
```
cv-magic-app/user/punam@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/Australia_for_UNHCR_input_recommendation_20251121_005158.json
```

**Returns:** `Path` to saved file or `None` if failed

---

### **3. `create_recommendation_file(company: str)`**

**Lines 177-209**

**Convenience method** that combines extraction and saving:
```python
def create_recommendation_file(self, company: str) -> bool:
    recommendation_data = self.extract_ats_recommendation_data(company)
    if not recommendation_data:
        return False
    output_file = self.save_optimized_recommendation(company, recommendation_data)
    return output_file is not None
```

---

## 📊 Data Extraction Details

### **1. Metadata Extraction**

**Source:** Created fresh (not from skills_analysis.json)

**Lines 85-90:**
```python
"metadata": {
    "company": company,
    "generated_at": datetime.utcnow().isoformat(),
    "ats_score_current": ats_scoring.get("final_score", 0),
    "match_rate_current": match_summary.get("overall_match_rate", 0)
}
```

---

### **2. Skills Extraction**

**Source:** `skills_analysis.json` → `cv_skills` and `jd_skills`

**Lines 93-104:**
```python
"skills_extraction": {
    "cv": {
        "technical": cv_skills.get("technical_skills", []),
        "soft": cv_skills.get("soft_skills", []),
        "domain": cv_skills.get("domain_keywords", [])
    },
    "jd": {
        "technical": jd_skills.get("technical_skills", []),
        "soft": jd_skills.get("soft_skills", []),
        "domain": jd_skills.get("domain_keywords", [])
    }
}
```

---

### **3. Preliminary Decision Extraction**

**Source:** `skills_analysis.json` → `analyze_match_entries` (latest entry)

**Method:** `_extract_preliminary_decision()` (Lines 211-265)

**Parsing Logic:**
- Uses regex to extract: `DECISION:`, `MATCH_SCORE:`, `CONFIDENCE:`
- Extracts skill lists: `CRITICAL_MISSING:`, `IMPLICIT_LIKELY:`, `LEARNABLE_GAPS:`
- Parses from text content of the latest match entry

**Output:**
```python
{
    "decision": "PROCEED" | "MAYBE" | "DONT_PROCEED" | "UNKNOWN",
    "match_score": int,
    "confidence": int,
    "should_proceed": bool,
    "critical_missing": List[str],
    "implicit_likely": List[str],
    "learnable_gaps": List[str]
}
```

---

### **4. Match Summary Extraction**

**Source:** `skills_analysis.json` → `preextracted_comparison_entries` (latest entry)

**Method:** `_extract_match_summary()` (Lines 267-337)

**Parsing Logic:**
- Extracts overall match rate from text: `Match Rate: XX%`
- Parses per-category data by detecting section headers:
  - "Technical Skills" → `technical` category
  - "Soft Skills" → `soft` category
  - "Domain Keywords" → `domain` category
- Extracts matched skills: Lines containing `CV Has: 'skill'`
- Extracts missing skills: Lines containing `JD Required: 'skill'` or `JD Requires: 'skill'`
- Calculates match rates per category

**Output:**
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

---

### **5. Component Summary Extraction**

**Source:** `skills_analysis.json` → `component_analysis_entries` (latest entry)

**Method:** `_extract_component_summary()` (Lines 339-363)

**Extracts from:** `latest_entry.get("extracted_scores", {})`

**Output:**
```python
{
    "skills_relevance": float,
    "experience_alignment": float,
    "role_similarity": float,
    "seniority_match": float,
    "industry_fit": float,
    "required_skills_coverage": float,
    "tech_stack_similarity": float,
    "business_readiness": float,
    "industry_transition_fit": float
}
```

---

### **6. ATS Scoring Extraction**

**Source:** `skills_analysis.json` → `ats_calculation_entries` (latest entry)

**Method:** `_extract_ats_scoring()` (Lines 365-390)

**Extracts from:**
- `latest_entry.get("final_ats_score", 0)`
- `latest_entry.get("breakdown", {})`
- `latest_entry.get("scoring_version", "unknown")`

**Output:**
```python
{
    "final_score": float,
    "category1_score": float,
    "category2_score": float,
    "category3_score": float,
    "improvement_needed": float,  # max(0, 75.0 - final_score)
    "category1_keywords": float,
    "category2_ai_analysis": float,
    "missing_counts": {
        "technical": int,
        "soft": int,
        "domain": int
    },
    "scoring_version": str
}
```

---

### **7. Keyword Classification**

**Source:** Missing keywords from match summary + CV skills

**Method:** `_classify_keywords()` (Lines 392-513)

**Process:**
1. **Pre-filtering:** Removes keywords already in CV (Lines 403-429)
   - Extracts existing keywords from latest CV (tailored or original)
   - Filters missing keywords to exclude those already present
   - Logs filtering results

2. **Tier Classification:** Classifies filtered keywords into 3 tiers
   - **Tier 1 (Always Add):** Generic soft skills, transferable competencies
   - **Tier 2 (Add if Evidence):** Default for most keywords
   - **Tier 3 (Never Add):** Domain-specific, certifications, unverifiable

**Tier 1 Patterns:**
```python
"soft": ["leadership", "communication", "teamwork", "problem solving", ...]
"technical": ["data analysis", "project management", "stakeholder management", ...]
```

**Tier 3 Patterns:**
```python
"domain": ["refugee", "humanitarian", "fundraising", "donor", ...]
"certifications": ["pmp", "scrum master", "aws certified", ...]
```

**Output:**
```python
{
    "tier1_always_add": {"technical": [], "soft": [], "domain": []},
    "tier2_add_if_evidence": {"technical": [], "soft": [], "domain": []},
    "tier3_never_add": {"technical": [], "soft": [], "domain": []},
    "already_in_cv_filtered": List[str],
    "integration_instructions": str
}
```

---

## 🔍 Keyword Pre-Filtering Details

### **Existing Keyword Extraction**

**Method:** `_extract_existing_cv_keywords()` (Lines 515-552)

**Process:**
1. Checks for latest tailored CV first: `cvs/tailored/*_tailored_cv_*.json`
2. Falls back to original CV: `cvs/original/original_cv.json`
3. Extracts keywords from:
   - Skills sections
   - Experience bullets (2-3 word phrases)
   - Role highlights

**Method:** `_extract_keywords_from_cv_file()` (Lines 554-592)

---

### **Keyword Matching**

**Method:** `_keyword_exists_in_cv()` (Lines 594-627)

**Matching Logic:**
1. Direct match (case-insensitive)
2. Substring match (e.g., "python" in "python programming")
3. Common variations dictionary:
   - `python` → `['python programming', 'python development', 'py']`
   - `sql` → `['structured query language', 'mysql', 'postgresql']`
   - `data analysis` → `['data analytics', 'analyzing data']`

---

## 📁 File Structure

### **Input File (Source):**
```
{user_base_path}/applied_companies/{company}/{company}_skills_analysis.json
```

**Required Sections:**
- `cv_skills` - CV skills breakdown
- `jd_skills` - JD skills breakdown
- `analyze_match_entries` - Preliminary decision entries
- `preextracted_comparison_entries` - Match summary entries
- `component_analysis_entries` - Component score entries
- `ats_calculation_entries` - ATS score entries

---

### **Output File (Created):**
```
{user_base_path}/applied_companies/{company}/{company}_input_recommendation_{timestamp}.json
```

**Structure:**
```json
{
  "metadata": {...},
  "skills_extraction": {...},
  "preliminary_decision": {...},
  "match_summary": {...},
  "keyword_integration_guidance": {...},
  "component_summary": {...},
  "ats_scoring": {...}
}
```

---

## 🚨 Dependencies

### **Prerequisites:**
1. ✅ Skills analysis file must exist (`{company}_skills_analysis.json`)
2. ✅ Skills analysis must have completed successfully
3. ✅ At minimum, `analyze_match_entries` must exist (for preliminary decision)

### **Optional (but recommended):**
- `preextracted_comparison_entries` - For match summary
- `component_analysis_entries` - For component scores
- `ats_calculation_entries` - For ATS scores

---

## 🔄 Usage After Creation

The input recommendation file is used by:

1. **AI Recommendation Generator** (`ai_recommendation_generator.py`)
   - Loads the file via `_get_input_recommendation_file_path()`
   - Passes to `AIRecommendationPromptTemplate`
   - Generates AI prompt for recommendation generation

2. **API Endpoint:** `POST /generate-ai-recommendation/{company}`
   - Checks if input file exists before generating AI recommendations
   - Returns 404 if file not found

---

## 📝 Key Design Decisions

1. **Timestamped Filenames:** Each creation generates a new file with timestamp
   - Allows tracking of multiple runs
   - Preserves history

2. **Pre-filtering:** Keywords already in CV are filtered out before classification
   - Reduces noise in AI recommendations
   - Focuses on genuinely missing keywords

3. **Tier Classification:** Keywords are pre-classified into tiers
   - Provides guidance to AI
   - Helps with integration strategy

4. **Structured Data Only:** No verbose text, only structured data
   - Optimized for AI consumption
   - Reduces token usage

5. **User-Specific Paths:** Files are stored per user
   - Multi-user support
   - Isolation between users

---

## 🐛 Known Issues

1. **Missing Tailoring Strategy:** The input file doesn't include `tailoring_strategy` section
   - Impact: AI recommendations may lack strategic guidance
   - Fix: Add tailoring strategy extraction in `extract_ats_recommendation_data()`

2. **Match Summary Structure:** Sometimes all keywords end up in "domain" category
   - Impact: Incorrect categorization in AI prompt
   - Fix: Improve `_extract_match_summary()` parsing logic

3. **Empty Matched Lists:** Sometimes matched lists are empty
   - Impact: AI doesn't know what's already in CV
   - Fix: Improve match extraction from preextracted entries

---

## ✅ Summary

**Service:** `ATSRecommendationService`
**Main Method:** `extract_ats_recommendation_data()` + `save_optimized_recommendation()`
**Source:** `{company}_skills_analysis.json`
**Output:** `{company}_input_recommendation_{timestamp}.json`
**Location:** `{user_base_path}/applied_companies/{company}/`
**Triggered:** Automatically in skills analysis pipeline (Step 4)

The file serves as a bridge between skills analysis results and AI recommendation generation, providing structured, optimized data for the AI to process.

