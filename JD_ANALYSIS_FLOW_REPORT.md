# JD Analysis Flow - Information Gathering Report

## Current JD Analysis Flow

### Entry Point
- **File**: `app/services/context_aware_analysis_pipeline.py`
- **Function**: `_analyze_jd()` 
- **Line**: ~540-652
- **Flow**: 
  1. Checks for cached JD analysis
  2. If not found/force_refresh, calls `jd_analyzer.analyze_and_save_company_jd()` or `jd_analyzer.analyze_company_jd()`
  3. Converts result to dict via `jd_analysis_result.to_dict()`
  4. Stores in `results.jd_analysis`

### LLM Call Location
- **File**: `app/services/jd_analysis/jd_analyzer.py`
- **Function**: `analyze_jd_text()` 
- **Line**: 680-784
- **Key Code**:
  ```python
  system_prompt, user_prompt = get_jd_analysis_prompts(jd_text)  # Line 710
  response = await self.ai_service.generate_response(
      prompt=user_prompt,
      user=current_user,
      system_prompt=system_prompt,
      temperature=temperature,
      max_tokens=3000
  )  # Line 756-762
  ```

### Response Parsing
- **File**: `app/services/jd_analysis/jd_analyzer.py`
- **Function**: `_parse_ai_response()`
- **Line**: 377-467
- **Process**:
  1. Strips markdown code fences if present
  2. Parses JSON with `json.loads()`
  3. Validates structure and ensures all category keys exist
  4. Creates `JDAnalysisResult` object
  5. Returns `JDAnalysisResult` instance

---

## Expected JSON Structure

The LLM must return JSON in this exact format:

```json
{
  "experience_years": <number_or_null>,
  "required_skills": {
    "technical": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "experience": ["requirement1", ...],
    "domain_knowledge": ["domain1", "domain2", ...]
  },
  "preferred_skills": {
    "technical": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "experience": ["requirement1", ...],
    "domain_knowledge": ["domain1", "domain2", ...]
  }
}
```

### Required Fields
- `required_skills` (dict) - MUST exist, parser creates defaults if missing
- `preferred_skills` (dict) - MUST exist, parser creates defaults if missing
- Each skill dict MUST have these 4 categories: `technical`, `soft_skills`, `experience`, `domain_knowledge`
- `experience_years` (optional) - can be null or number

### Parser Behavior
- **Location**: `jd_analyzer.py:_parse_ai_response()` lines 429-451
- Creates default empty structure if keys missing
- Ensures all 4 categories exist in both required/preferred
- Merges categories into flat `required_keywords` and `preferred_keywords` lists in `JDAnalysisResult.to_dict()`

---

## Current Prompt Functions

### Function Signature
```python
def get_jd_analysis_prompts(job_description: str) -> tuple[str, str]:
    """
    Get system and user prompts for job description analysis
    
    Args:
        job_description: The job description text to analyze
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    return (
        JD_ANALYSIS_SYSTEM_PROMPT,
        JD_ANALYSIS_USER_PROMPT.format(job_description=job_description)
    )
```

### Current System Prompt (First 50 lines)
```
You are an expert job description analyzer. Your task is to extract keywords and skills using PATTERN RECOGNITION.

🔴 CRITICAL INSTRUCTIONS:

1. **EXTRACT FIRST, PATTERN SECOND**: Always extract direct mentions first, then apply patterns.
2. **DON'T OVERTHINK**: If you see "SQL", extract "SQL". If you see "Tableau", extract "Tableau".
3. **PATTERNS ARE FOR NOVEL PHRASES**: Use patterns when you see action verbs (develop, build, administer) + nouns.

Extraction priority:
1️⃣ Direct mentions → Extract as-is ("SQL" → "SQL", "Tableau" → "Tableau")
2️⃣ Action phrases → Apply Pattern 1 ("develop dashboards" → "dashboard development")
3️⃣ Behavioral phrases → Apply Pattern 3 ("work independently" → "independence")

Example thinking:
✅ See "SQL" → Extract "SQL" (direct mention)
✅ See "administer warehouses" → Apply Pattern 1 → Extract "warehouse administration"
✅ See "data cleaning" → Extract "data cleaning" (direct mention)
❌ See "SQL" → Skip because no action verb (WRONG! Always extract direct mentions!)

═══════════════════════════════════════════════════════════════
CLASSIFICATION RULES
═══════════════════════════════════════════════════════════════

REQUIRED KEYWORDS - Extract from definitive/mandatory language:
- "Minimum X years", "Experience in/with", "Strong [skill] skills"
- "Must have", "Required", "Essential", "Necessary"
- From sections: "Requirements", "Must Have", "Essential Criteria"

PREFERRED KEYWORDS - Extract from optional language:
- "Knowledge of", "Appreciation of", "Understanding of", "Familiarity with"
- "Nice to have", "Preferred", "Desirable", "Would be an advantage"
- From sections: "Preferred", "Nice to Have", "Desirable"

═══════════════════════════════════════════════════════════════
CATEGORIZATION: 3-QUESTION TEST (Applied in Priority Order)
═══════════════════════════════════════════════════════════════

For EACH extracted term, ask:

**QUESTION 1:** "Can a computer execute this? OR Is it a tool/software?"
→ YES = **TECHNICAL SKILL**
Includes:
- Languages/Tools: SQL, Python, Power BI, Tableau, Excel, VBA, AWS, Docker, Git
- Data processes: Data cleaning, Data transformation, ETL, Data modeling, Data mining, Statistical methods
- Technical artifacts: Dashboards, Models, APIs, Pipelines, Reports
→ NO = Go to Question 2

**QUESTION 2:** "Does it require human interaction + behavioral trait?"
→ YES = **SOFT SKILL**
Includes: Communication, Leadership, Teamwork, Problem-solving, Analytical thinking, Collaboration, Attention to detail, Time management
→ NO = Go to Question 3

**QUESTION 3:** "Is it industry/sector/regulatory term?"
→ YES = **DOMAIN KNOWLEDGE**
Includes:
- Industry sectors: Healthcare, Finance, E-commerce, Nonprofit, Retail, Manufacturing
- Educational backgrounds: Accounting, Commerce, Business, Economics, Marketing (when "background in X" or "degree in X")
- Regulatory: GDPR, HIPAA, SOX, ISO standards, NDIS
- Sector-specific: Clinical trials, Underwriting, Food relief, Fundraising, Charity
→ NO = EXCLUDE (too generic: "stakeholders", "insights", "best practices")

**CRITICAL:** Data processes (data cleaning, ETL, data transformation) are TECHNICAL, NOT domain!
```

### Current User Prompt (First 30 lines)
```
Analyze this job description using PATTERN RECOGNITION:

{job_description}

═══════════════════════════════════════════════════════════════
EXTRACTION PROCESS
═══════════════════════════════════════════════════════════════

1. **Read ENTIRE job description first** (understand role context)

2. **Apply 6 PATTERNS** to extract skills:
   - Pattern 1: [Action Verb] + [Technical Object] (ANY verb, not just examples)
   - Pattern 2: Preserve specific technology names
   - Pattern 3: [Behavioral Action] → Soft skill
   - Pattern 4: Keep compound technical terms together
   - Pattern 5: Infer domain from context (explicit or implicit)
   - Pattern 6: Deduplicate semantically similar terms

3. **Categorize using 3-QUESTION TEST**:
   Q1: Computer executable/tool? → Technical
   Q2: Human interaction + behavioral? → Soft
   Q3: Industry/sector/regulatory? → Domain
   None → Exclude

4. **Classify Required vs Preferred**:
   Based on language strength (mandatory vs optional)

5. **Quality check**:
   - Technical includes: tools, languages, AND data processes (data cleaning, ETL, etc.)
   - Domain includes: industries, educational backgrounds, regulatory terms
   - Removed: Generic terms (stakeholders, insights, best practices)
   - Deduplicated: Similar terms (keep shortest form)

CRITICAL REMINDERS:
- Apply patterns to ANY verb-noun combination (not just listed examples)
- "administer warehouses" → Recognize Pattern 1 → Extract "warehouse administration"
- "orchestrate deployments" → Recognize Pattern 1 → Extract "deployment orchestration"
- Infer domain from organizational context (nonprofit, UN, startup, etc.)

Return JSON only, no additional text.
```

---

## Integration Points

### Where Extracted Data Goes

1. **Immediate Processing**:
   - `JDAnalysisResult` object created from parsed JSON
   - Stored in `jd_analysis_result` variable

2. **Pipeline Integration**:
   - **File**: `context_aware_analysis_pipeline.py:563`
   - **Code**: `results.jd_analysis = jd_analysis_result.to_dict()`
   - Converts to dict format for pipeline consumption

3. **Data Structure After to_dict()**:
   ```python
   {
       'experience_years': <int or None>,
       'required_skills': {
           'technical': [...],
           'soft_skills': [...],
           'experience': [...],
           'domain_knowledge': [...]
       },
       'preferred_skills': {
           'technical': [...],
           'soft_skills': [...],
           'experience': [...],
           'domain_knowledge': [...]
       },
       'three_section_skills': {...},  # Optional lightweight summary
       'required_keywords': [...],  # Merged flat list from all required categories
       'preferred_keywords': [...],  # Merged flat list from all preferred categories
       'analysis_timestamp': <ISO string>,
       'ai_model_used': <string>,
       'processing_status': "completed",
       'company_name': <string>,
       'metadata': {...}
   }
   ```

4. **File Persistence**:
   - **File**: `jd_analyzer.py:_save_analysis_result()` line 507-558
   - **Path**: `{base_path}/applied_companies/{company_name}/{company_name}_jd_analysis_{timestamp}.json`
   - Saves full `to_dict()` output as JSON

5. **Database/Model Dependencies**:
   - No direct database writes from JD analyzer
   - Results stored in file system only
   - Used by CV-JD matching, ATS scoring, component assembler

---

## Files That Import This

### Direct Imports of `get_jd_analysis_prompts()`
- `app/services/jd_analysis/jd_analyzer.py` (line 19)
- `app/services/jd_analysis/__init__.py` (line 17) - re-exported

### Imports of `JDAnalyzer` Class
- `app/services/context_aware_analysis_pipeline.py` (line 23)
  - Used at lines: 542, 547, 646
- `app/routes/skills_analysis.py` (line 664)
  - Used for standalone JD analysis endpoint

### Imports of Related Classes
- `app/services/ats/component_assembler.py` (line 18)
  - Imports `RequirementsExtractor` from `jd_analyzer.py`
  - Uses `JDAnalysisResult` for requirement counting

### Usage in Context-Aware Pipeline
- **Primary usage**: `context_aware_analysis_pipeline.py:_analyze_jd()` 
- **Methods called**:
  - `analyze_and_save_company_jd()` - with force_refresh option
  - `analyze_company_jd()` - without saving
  - `analyze_jd_file()` - direct file analysis

---

## Safe Change Checklist

### ✅ Can Change (Safe to Modify)
- [x] **System prompt content** - Can simplify categorization rules
- [x] **User prompt content** - Can simplify extraction instructions
- [x] **Prompt length** - Can reduce verbosity
- [x] **Pattern examples** - Can remove or simplify pattern descriptions
- [x] **Categorization logic in prompt** - Can use simpler 3-question test only

### ⚠️ Must Preserve (Critical - Do Not Change)
- [ ] **JSON output structure** - MUST return exact format:
  ```json
  {
    "experience_years": <number_or_null>,
    "required_skills": {
      "technical": [],
      "soft_skills": [],
      "experience": [],
      "domain_knowledge": []
    },
    "preferred_skills": {
      "technical": [],
      "soft_skills": [],
      "experience": [],
      "domain_knowledge": []
    }
  }
  ```
- [ ] **Function signature** - `get_jd_analysis_prompts(job_description: str) -> tuple[str, str]`
- [ ] **Return type** - Must return tuple of (system_prompt, user_prompt)
- [ ] **Category names** - Must use exact keys: `technical`, `soft_skills`, `experience`, `domain_knowledge`
- [ ] **Required vs Preferred distinction** - Must maintain this classification

### ❌ Will Break If (Danger Zones)
- [ ] **Change JSON structure** - Parser expects exact nested dict format
- [ ] **Remove required_skills/preferred_skills** - Parser creates defaults but downstream code expects them
- [ ] **Change category names** - `JDAnalysisResult` class expects these exact keys
- [ ] **Remove experience_years** - Optional but used by ATS scoring
- [ ] **Change function signature** - All callers expect `(job_description: str) -> tuple[str, str]`
- [ ] **Return different format** - Parser expects JSON, not Python assignment format

---

## Additional Notes

### Three-Section Skills (Optional)
- There's a separate lightweight extraction: `_generate_three_section_skills()` (line 469)
- Uses `get_three_section_prompts()` from `jd_skill_sections_prompt.py`
- Returns: `{technical_skills: [], soft_skills: [], domain_knowledge: []}`
- This is NON-BLOCKING and doesn't affect main analysis
- Can be ignored for prompt replacement

### Caching Logic
- JD analyzer has complex caching with processed JD support
- Cache invalidation checks if processed JD exists
- Metadata tracks `used_processed_jd` flag
- Prompt changes won't affect caching logic

### Error Handling
- Parser has fallback defaults if JSON structure incomplete
- Creates empty lists for missing categories
- Raises `ValueError` if JSON parsing fails completely
- Logs detailed debug info for troubleshooting

---

## Summary

**Safe to Replace**: The prompt content (system + user prompts) can be simplified while keeping the same JSON output format.

**Critical Constraint**: The LLM must return JSON matching the exact structure shown above, with all 4 categories in both required_skills and preferred_skills.

**Integration Points**: Results flow through `JDAnalysisResult.to_dict()` → `results.jd_analysis` → saved to JSON files → used by CV-JD matching and ATS scoring.

