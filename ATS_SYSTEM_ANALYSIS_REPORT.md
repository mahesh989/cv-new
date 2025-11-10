# ATS System Analysis Report - Information Gathering

## Executive Summary

This document provides complete information about the current ATS system implementation to support refactoring from 5 analyzers to 2 consolidated analyzers while maintaining backward compatibility.

---

## 1. CURRENT COMPONENT ANALYZER FILES

### Location
`cv-magic-app/backend/app/services/ats/components/`

### All 5 Analyzer Files:

1. **`skills_relevance_analyzer.py`** → `SkillsAnalyzer` class
2. **`experience_analyzer.py`** → `ExperienceAnalyzer` class
3. **`industry_analyzer.py`** → `IndustryAnalyzer` class
4. **`seniority_analyzer.py`** → `SeniorityAnalyzer` class
5. **`technical_analyzer.py`** → `TechnicalAnalyzer` class

### Base Class/Interface
- **No shared base class** - Each analyzer is a standalone class
- All analyzers follow the same pattern:
  - `__init__()` - Initializes with prompt template
  - `async def analyze(...)` - Main analysis method
  - `_clean_llm_response()` - Response cleaning
  - `_parse_response()` - JSON parsing with fallbacks

### Method Signatures

All analyzers have the same pattern:

```python
async def analyze(self, cv_text: str, jd_text: str, user_email: str = None) -> Dict[str, Any]:
    """
    Analyze [component] using LLM.
    
    Args:
        cv_text: CV content (limited to 5000 chars)
        jd_text: Job description content (limited to 3000 chars)
        user_email: User email for API key context
        
    Returns:
        Dict containing [component] analysis results
    """
```

**Exception:** `SkillsAnalyzer` has an additional parameter:
```python
async def analyze(self, cv_text: str, jd_text: str, matched_skills: str, user_email: str = None) -> Dict[str, Any:
```

### Execution Model
- **All analyzers run asynchronously** (`async def`)
- Called in parallel using `asyncio.gather()` in `component_assembler.py`
- No shared utility functions - each has its own parsing logic

### Shared Configuration
- **`standardized_config.py`** contains:
  - `STANDARD_AI_PARAMS` - Temperature (0.0), max_tokens (3000), system_prompt
  - `validate_analysis_result()` - Validation function (not consistently used)

---

## 2. CURRENT PROMPT FILES

### Location
`cv-magic-app/backend/prompt/`

### All 5 Prompt Files:

1. **`ats_skills_relevance_prompt.py`** → `SKILLS_RELEVANCE_PROMPT` constant
2. **`ats_experience_prompt.py`** → `EXPERIENCE_ALIGNMENT_PROMPT` constant
3. **`ats_industry_prompt.py`** → `INDUSTRY_FIT_PROMPT` constant
4. **`ats_seniority_prompt.py`** → `ROLE_SENIORITY_PROMPT` constant
5. **`ats_technical_prompt.py`** → `TECHNICAL_DEPTH_PROMPT` constant

### Structure
- **Python files with string constants** (not functions)
- All prompts use `.format()` method with template variables:
  - `{cv_text}` - CV content (limited to 5000 chars)
  - `{jd_text}` - Job description (limited to 3000 chars)
  - `{matched_skills}` - Only used in skills_relevance_prompt

### Prompt Utility Functions
- **None** - Prompts are simple string templates
- No token counting or formatting utilities

---

## 3. ORCHESTRATOR LOGIC

### Location
`cv-magic-app/backend/app/services/ats/component_assembler.py`

### Main Orchestration Method

```python
async def assemble_analysis(self, company: str, cv_text: Optional[str] = None, jd_url: str = "") -> Dict[str, Any]:
```

### How Analyzers Are Called

**Current Implementation (5 analyzers in parallel):**

```python
async def _run_component_analyses(self, cv_text: str, jd_text: str, matched_skills: str, company: str) -> Dict[str, Any]:
    """Run all component analyses in parallel."""
    
    # Run all analyses in parallel
    skills_task = self.skills_analyzer.analyze(cv_text, jd_text, matched_skills, self.user_email)
    experience_task = self.experience_analyzer.analyze(cv_text, jd_text, self.user_email)
    industry_task = self.industry_analyzer.analyze(cv_text, jd_text, self.user_email)
    seniority_task = self.seniority_analyzer.analyze(cv_text, jd_text, self.user_email)
    technical_task = self.technical_analyzer.analyze(cv_text, jd_text, self.user_email)
    
    # Run bonus calculation in parallel (synchronous but wrapped in asyncio)
    bonus_task = asyncio.get_event_loop().run_in_executor(
        None, self._calculate_requirement_bonus, company
    )
    
    # Wait for all to complete
    skills_result, experience_result, industry_result, seniority_result, technical_result, bonus_result = await asyncio.gather(
        skills_task,
        experience_task,
        industry_task,
        seniority_task,
        technical_task,
        bonus_task,
        return_exceptions=True
    )
```

### Data Structure Passed to Analyzers

- **Input:** `cv_text` (str), `jd_text` (str), `matched_skills` (str, only for skills analyzer)
- **No complex data structures** - just strings

### Data Structure Returned by Each Analyzer

Each analyzer returns a dict with a nested structure:

```python
# SkillsAnalyzer
{
    "skills_analysis": [...],
    "overall_skills_score": float,
    "corporate_skills_strength": str,
    "academic_skills_discount": str,
    "business_readiness_score": float,
    ...
}

# ExperienceAnalyzer
{
    "experience_analysis": {
        "cv_experience_years": str,
        "cv_corporate_years": str,
        "cv_academic_years": str,
        "alignment_score": float,
        ...
    }
}

# IndustryAnalyzer
{
    "industry_analysis": {
        "cv_primary_industry": str,
        "jd_target_industry": str,
        "industry_alignment_score": float,
        ...
    }
}

# SeniorityAnalyzer
{
    "seniority_analysis": {
        "cv_corporate_years": str,
        "seniority_score": float,
        "leadership_readiness_score": float,
        ...
    }
}

# TechnicalAnalyzer
{
    "technical_analysis": {
        "technical_depth_score": float,
        "core_skills_match_percentage": float,
        "technical_stack_fit_percentage": float,
        ...
    }
}
```

### Error Handling

- **`return_exceptions=True`** in `asyncio.gather()` - exceptions are returned as results
- **Post-gather validation:**
```python
for component, result in results.items():
    if isinstance(result, Exception):
        logger.error("[ASSEMBLER] %s analysis failed: %s", component.title(), str(result))
        raise result
```

### Retry/Fallback Logic

- **No retry logic** - If an analyzer fails, the entire process fails
- **Batched analyzer fallback:** There's a `BatchedAnalyzer` class that can fallback to individual analyzers if batched approach fails

### Results Combination

Results are stored in a dict:
```python
results = {
    "skills": skills_result,
    "experience": experience_result,
    "industry": industry_result,
    "seniority": seniority_result,
    "technical": technical_result,
    "requirement_bonus": bonus_result
}
```

---

## 4. SCORE CALCULATOR

### Location
`cv-magic-app/backend/app/services/ats/ats_score_calculator.py`

### Method Signature

```python
def calculate_ats_score(
    self, 
    preextracted_data: Dict[str, Any],
    component_analysis: Dict[str, Any],
    extracted_scores: Dict[str, float]
) -> ATSScoreBreakdown:
```

### Input Parameters

1. **`preextracted_data`**: Dict with `{"content": str}` - Contains match rate information parsed from text
2. **`component_analysis`**: Dict - **Currently not used** (empty dict passed)
3. **`extracted_scores`**: Dict[str, float] - Numerical scores extracted from component analyzers

### Extracted Scores Structure (Current)

```python
extracted_scores = {
    # Technical & Skills
    "technical_depth": float,
    "core_skills_match_percentage": float,
    "technical_stack_fit_percentage": float,
    "data_familiarity_score": float,
    
    # Experience
    "experience_alignment": float,
    "experience_match_percentage": float,
    "responsibility_fit_percentage": float,
    "role_seniority": float,
    "leadership_readiness_score": float,
    
    # Potential & Ability
    "growth_trajectory_score": float,
    "complexity_readiness_score": float,
    "learning_agility_score": float,
    "jd_problem_complexity": float,  # 0-10 scale, normalized to 0-100
    
    # Company Fit
    "industry_fit": float,
    "domain_overlap_percentage": float,
    "stakeholder_fit_score": float,
    "business_cycle_alignment": float,
    
    # Bonus
    "requirement_bonus": float
}
```

### Current Score Calculation Logic

**Category 1: Direct Match Rates (40 points)**
- Technical Skills: 20 points (from match rate)
- Domain Keywords: 5 points (from match rate)
- Soft Skills: 15 points (from match rate)

**Category 2: Component Analysis (60 points)**
- Core Competency (25 points): Average of 4 metrics
  - technical_depth
  - core_skills_match_percentage
  - technical_stack_fit_percentage
  - data_familiarity_score
- Experience & Seniority (20 points): Average of 5 metrics
  - experience_alignment
  - experience_match_percentage
  - responsibility_fit_percentage
  - role_seniority
  - leadership_readiness_score
- Potential & Ability (10 points): Average of 4 metrics
  - growth_trajectory_score
  - complexity_readiness_score
  - learning_agility_score
  - jd_problem_complexity (normalized)
- Company Fit (5 points): Average of 4 metrics
  - industry_fit
  - domain_overlap_percentage
  - stakeholder_fit_score
  - business_cycle_alignment

**Category 3: Bonus Points**
- requirement_bonus (up to +10 points)

**Final Score:** `min(100.0, cat1_score + cat2_score + bonus_points)`

### Score Capping

- **Line 290:** `final_ats_score = min(100.0, ats1_score + bonus_points)`
- Capped at 100.0

### Validation Checks

- **Match rate parsing:** Validates regex patterns in preextracted_data
- **Score range validation:** Each analyzer validates scores are 0-100
- **No validation in calculator itself** - assumes valid inputs

---

## 5. SCORE EXTRACTION LOGIC

### Location
`cv-magic-app/backend/app/services/ats/component_assembler.py`

### Method

```python
def _extract_scores(self, component_results: Dict[str, Any]) -> Dict[str, float]:
    """Extract scores from component results."""
```

### Keys Extracted from Each Analyzer

**From SkillsAnalyzer:**
- `skills_relevance` ← `overall_skills_score`

**From ExperienceAnalyzer:**
- `experience_alignment` ← `experience_analysis.alignment_score`

**From IndustryAnalyzer:**
- `industry_fit` ← `industry_analysis.industry_alignment_score`
- `domain_overlap_percentage` ← `industry_analysis.domain_overlap_percentage`
- `data_familiarity_score` ← `industry_analysis.data_familiarity_score`
- `stakeholder_fit_score` ← `industry_analysis.stakeholder_fit_score`
- `business_cycle_alignment` ← `industry_analysis.business_cycle_alignment`

**From SeniorityAnalyzer:**
- `role_seniority` ← `seniority_analysis.seniority_score`
- `experience_match_percentage` ← `seniority_analysis.experience_match_percentage`
- `responsibility_fit_percentage` ← `seniority_analysis.responsibility_fit_percentage`
- `leadership_readiness_score` ← `seniority_analysis.leadership_readiness_score`
- `growth_trajectory_score` ← `seniority_analysis.growth_trajectory_score`

**From TechnicalAnalyzer:**
- `technical_depth` ← `technical_analysis.technical_depth_score`
- `core_skills_match_percentage` ← `technical_analysis.core_skills_match_percentage`
- `technical_stack_fit_percentage` ← `technical_analysis.technical_stack_fit_percentage`
- `complexity_readiness_score` ← `technical_analysis.complexity_readiness_score`
- `learning_agility_score` ← `technical_analysis.learning_agility_score`
- `jd_problem_complexity` ← `technical_analysis.jd_problem_complexity`

**From RequirementBonus:**
- `requirement_bonus` ← `bonus_breakdown.total_bonus`
- Various bonus breakdown fields

### Missing Scores Handling

- **Uses `.get()` with defaults** - Missing keys return `None` or default values
- **No explicit error handling** - Missing scores would cause KeyError if accessed directly
- **Float conversion:** All scores converted to `float()` - may raise ValueError if invalid

### JSON Validation

- **Each analyzer validates its own response** before returning
- **No centralized JSON validation** - each analyzer has its own parsing logic
- **Fallback strategies:** Each analyzer has multiple parsing strategies (direct parse, extract objects, wrap, etc.)

---

## 6. COMPONENT ASSEMBLER

### Location
`cv-magic-app/backend/app/services/ats/component_assembler.py`

### Purpose

The `ComponentAssembler` class:
1. **Orchestrates** all 5 component analyzers
2. **Extracts scores** from analyzer results
3. **Saves results** to JSON files
4. **Triggers ATS calculation** after component analysis
5. **Handles minimal CV detection** and uses appropriate analyzer

### How It Combines Results

1. **Runs analyzers in parallel** (see section 3)
2. **Extracts scores** using `_extract_scores()` method
3. **Saves to file:**
```python
assembled_entry = {
    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3],
    "component_analyses": component_results,  # Full results from all 5 analyzers
    "extracted_scores": scores,  # Extracted numerical scores
    "analysis_type": "modular_component_analysis"
}
```

### Final Output Structure

```python
{
    "company": str,
    "timestamp": str,
    "component_results": {
        "skills": {...},
        "experience": {...},
        "industry": {...},
        "seniority": {...},
        "technical": {...},
        "requirement_bonus": {...}
    },
    "extracted_scores": {
        "technical_depth": float,
        "experience_alignment": float,
        ...
    },
    "ats_results": {...},
    "consistency_validation": {...},
    "status": "success"
}
```

### Insights/Recommendations Generation

- **Not generated in assembler** - Generated in `enhanced_ats_orchestrator.py`
- Assembler focuses on running analyses and extracting scores

---

## 7. API RESPONSE STRUCTURE

### API Endpoint

**Location:** `cv-magic-app/backend/app/routes/skills_analysis.py`

**Endpoint:** `GET /analysis-results/{company}`

### Complete API Response Structure

```python
{
    "company": str,
    "skills_analysis": {
        "cv_skills": {
            "technical_skills": [str],
            "soft_skills": [str],
            "domain_keywords": [str]
        },
        "jd_skills": {
            "technical_skills": [str],
            "soft_skills": [str],
            "domain_keywords": [str]
        }
    },
    "preextracted_comparison": {
        "timestamp": str,
        "model_used": str,
        "raw_content": str,
        "match_rates": {
            "technical_skills_match_rate": float,
            "domain_keywords_match_rate": float,
            "soft_skills_match_rate": float
        }
    },
    "component_analysis": {
        "timestamp": str,
        "extracted_scores": {
            "technical_depth": float,
            "experience_alignment": float,
            "industry_fit": float,
            "role_seniority": float,
            "skills_relevance": float,
            ...
        },
        "component_details": {
            "skills": {...},
            "experience": {...},
            "industry": {...},
            "seniority": {...},
            "technical": {...}
        }
    },
    "ats_score": {
        "timestamp": str,
        "final_ats_score": float,
        "category_status": str,
        "recommendation": str,
        "breakdown": {
            "category1": {
                "score": float,
                "technical_skills_match_rate": float,
                "domain_keywords_match_rate": float,
                "soft_skills_match_rate": float,
                "missing_counts": {
                    "technical": int,
                    "domain": int,
                    "soft": int
                }
            },
            "category2": {
                "score": float,
                "core_competency_avg": float,
                "experience_seniority_avg": float,
                "potential_ability_avg": float,
                "company_fit_avg": float
            },
            "ats1_score": float,
            "bonus_points": float
        }
    }
}
```

### Fields from 5 Analyzers Exposed in API

**From component_analysis.component_details:**
- `skills` - Full skills analyzer result
- `experience` - Full experience analyzer result
- `industry` - Full industry analyzer result
- `seniority` - Full seniority analyzer result
- `technical` - Full technical analyzer result

**From component_analysis.extracted_scores:**
- All numerical scores extracted from the 5 analyzers (see section 5)

### Transformations Before Sending to Frontend

- **Skills sorting:** Skills are alphabetically sorted
- **Latest entry selection:** Only the latest entry from each analysis type is returned
- **Match rate extraction:** Parsed from preextracted_comparison content using regex

### Pydantic Models

- **No Pydantic models found** - API returns plain dicts
- **No request/response validation** using Pydantic schemas

---

## 8. FRONTEND COMPONENT SCORE DISPLAY

### Frontend Location
- **Mobile App:** `cv-magic-app/mobile_app/` (Flutter/Dart)
- **No web frontend found** in the codebase

### Frontend Files Using Component Scores

**Main Service:**
- `cv-magic-app/mobile_app/lib/services/skills_analysis_service.dart`

**Main Controller:**
- `cv-magic-app/mobile_app/lib/controllers/skills_analysis_controller.dart`

### Fields from 5 Analyzers Used in Frontend

Based on API response structure, frontend accesses:

**From `component_analysis.extracted_scores`:**
- `technical_depth`
- `experience_alignment`
- `industry_fit`
- `role_seniority`
- `skills_relevance`
- All other extracted scores

**From `component_analysis.component_details`:**
- Full nested structures from each analyzer (skills, experience, industry, seniority, technical)

**From `ats_score.breakdown`:**
- Category 1 and Category 2 breakdowns
- Final ATS score
- Bonus points

### Charts/Visualizations

- **No chart code found** in the codebase search
- Frontend likely displays scores in cards/lists, not charts

### Frontend Calculations

- **No calculations found** - Frontend appears to display backend-provided scores directly
- **Progressive loading:** Frontend polls for results and displays as they become available

---

## 9. SCORE VISUALIZATION COMPONENTS

### Charts Found
- **None** - No chart configurations found in codebase

### Data Points Mapped
- **N/A** - No visualization code found

### Hardcoded Component Names
- **None found** - Component names likely come from API response

---

## 10. TYPE DEFINITIONS

### TypeScript Interfaces
- **No TypeScript found** - Frontend is Flutter/Dart

### Dart Type Definitions

**Location:** `cv-magic-app/mobile_app/lib/models/` (likely, not confirmed)

**Expected Structure:**
- `ComponentAnalysisResult` class
- `ATSResult` class
- `AIRecommendationResult` class

### Exact Types Expected

Based on controller code:
```dart
ComponentAnalysisResult? componentAnalysis;
if (completeResults['component_analysis'] != null) {
    componentAnalysis = ComponentAnalysisResult.fromJson(
        completeResults['component_analysis'],
    );
}

ATSResult? atsResult;
if (completeResults['ats_score'] != null) {
    atsResult = ATSResult.fromJson(completeResults['ats_score']);
}
```

---

## 11. FEATURE FLAG SYSTEM

### Current Feature Flag Usage

**Found in:**
- `cv-magic-app/backend/app/routes/skills_analysis.py`
- `cv-magic-app/backend/app/services/skills_analysis_config.py`

### Feature Flag Implementation

- **No centralized feature flag system found**
- **Environment variables:** Could be used but not currently implemented for analyzer switching
- **Batched analyzer:** There's a `BatchedAnalyzer` class that attempts to use 2 LLM calls instead of 5, but it's not feature-flag controlled

### Recommendation

- **Implement environment variable:** `USE_NEW_ANALYZERS=true/false`
- **Add to config:** Create a feature flag config file or add to existing config

---

## 12. ERROR HANDLING

### Current Error Handling

**In Analyzers:**
- Each analyzer catches exceptions and logs errors
- Some analyzers return fallback responses (e.g., SkillsAnalyzer)
- Others raise exceptions (e.g., TechnicalAnalyzer)

**In Orchestrator:**
- `asyncio.gather(..., return_exceptions=True)` - Exceptions returned as results
- Post-gather check raises exceptions if any analyzer failed
- **No automatic retry** - If one fails, entire process fails

### Caching

- **No caching found** - Each analysis runs fresh
- Results are saved to JSON files but not cached in memory

---

## 13. KEY FINDINGS FOR REFACTORING

### Critical Dependencies

1. **Frontend expects `component_analysis.component_details`** with keys:
   - `skills`, `experience`, `industry`, `seniority`, `technical`

2. **Score calculator expects specific keys** in `extracted_scores`:
   - Technical: `technical_depth`, `core_skills_match_percentage`, `technical_stack_fit_percentage`, `data_familiarity_score`
   - Experience: `experience_alignment`, `experience_match_percentage`, `responsibility_fit_percentage`, `role_seniority`, `leadership_readiness_score`
   - Potential: `growth_trajectory_score`, `complexity_readiness_score`, `learning_agility_score`, `jd_problem_complexity`
   - Company: `industry_fit`, `domain_overlap_percentage`, `stakeholder_fit_score`, `business_cycle_alignment`

3. **API response structure must remain unchanged** - Frontend depends on exact structure

### Mapping Requirements

**New 2-analyzer output must map to:**
- Old 5-analyzer structure for `component_details`
- All required keys in `extracted_scores`
- All fields in `ats_score.breakdown`

### Implementation Strategy

1. **Create 2 new analyzers** that return combined results
2. **Add mapping layer** to convert new structure → old structure
3. **Update score calculator** to accept both old and new structures (feature flag)
4. **Update orchestrator** to call new analyzers when flag enabled
5. **Maintain backward compatibility** - Old system must continue working

---

## 14. ADDITIONAL NOTES

### Batched Analyzer

There's already a `BatchedAnalyzer` class that attempts to reduce LLM calls:
- **Batch 1:** Skills + Experience (1 call)
- **Batch 2:** Industry + Seniority + Technical (1 call)
- **Total:** 2 calls instead of 5

**However:**
- It's not currently used as the default
- It has different output structure
- It's used as a fallback in `_run_batched_component_analyses()`

### Minimal CV Handling

- `ComponentAssembler` detects minimal CVs and uses a different analyzer
- This should be preserved in the refactoring

### Consistency Validator

- `ConsistencyValidator` validates cross-analyzer consistency
- This should work with new analyzers if output structure is maintained

---

## 15. SUMMARY CHECKLIST

### Backend Analysis ✅
- [x] All 5 analyzer files identified
- [x] Method signatures documented
- [x] Prompt files identified
- [x] Orchestrator logic understood
- [x] Score calculator logic documented
- [x] Score extraction logic documented
- [x] Component assembler understood
- [x] API response structure documented

### Frontend Analysis ✅
- [x] Frontend location identified (Flutter/Dart)
- [x] Component score usage identified
- [x] API endpoint identified
- [x] Data structure dependencies documented

### Implementation Readiness ✅
- [x] All required information gathered
- [x] Backward compatibility requirements understood
- [x] Mapping requirements identified
- [x] Feature flag strategy recommended

---

**END OF ANALYSIS REPORT**

