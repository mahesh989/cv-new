# CV-JD Skills Comparison - Technical Documentation

## Overview

The system uses **two main approaches** to compare CV skills against JD requirements:

1. **Full CV Text Matching** (`cv_jd_matcher.py`) - Matches CV content against JD keywords extracted from job description
2. **Pre-Extracted Skills Comparison** (`preextracted_comparator.py`) - Compares pre-extracted CV skills against pre-extracted JD skills

## Approach 1: Full CV Text Matching

### Location
- **Service**: `cv-magic-app/backend/app/services/cv_jd_matching/cv_jd_matcher.py`
- **Prompts**: `cv-magic-app/backend/app/services/cv_jd_matching/cv_jd_matching_prompt.py`

### How It Works

1. **Input**: 
   - Full CV text content
   - JD keywords (required + preferred) extracted from JD analysis

2. **Process**:
   - Uses AI to analyze CV text against JD keywords
   - Performs intelligent semantic matching
   - Identifies which keywords are present/absent in CV

3. **Output**: JSON with matched/missed keywords and match counts

### Complete Prompt Templates

#### System Prompt

```python
CV_JD_MATCHING_SYSTEM_PROMPT = """You are an expert CV-JD matching analyst. Your task is to analyze a CV against job description keywords and determine which keywords are present in the CV content using intelligent matching.

MATCHING RULES:

SMART MATCHING LOGIC:
1. **Exact Matches**: Direct keyword matches (case-insensitive)
2. **Synonym Matches**: Related terms and synonyms
3. **Context Matches**: Keywords found in relevant context
4. **Skill Variations**: Different forms of the same skill
5. **Abbreviation Matches**: Full forms and abbreviations

EXAMPLES OF SMART MATCHING:
- "SQL" matches: "SQL", "sql", "Structured Query Language", "database queries"
- "Project Management" matches: "project management", "PM", "project coordination", "managed projects"
- "Communication" matches: "communication", "communicate", "verbal skills", "written communication"
- "Python" matches: "Python", "python", "Python programming", "Python development"
- "Data Analysis" matches: "data analysis", "analyzing data", "data analytics", "statistical analysis"

MATCHING GUIDELINES:
1. **Be Intelligent**: Look for semantic meaning, not just exact text
2. **Consider Context**: Keywords in relevant sections (experience, skills, education)
3. **Handle Variations**: Different tenses, forms, and expressions
4. **Be Thorough**: Check all sections of the CV for keyword presence
5. **Be Accurate**: Only mark as matched if the skill is genuinely present

OUTPUT FORMAT - CRITICAL: RETURN ONLY VALID JSON:

⚠️  IMPORTANT: ALL STRING VALUES MUST BE ENCLOSED IN DOUBLE QUOTES
⚠️  CRITICAL: NO UNQUOTED TEXT IN VALUES - EVERYTHING MUST BE QUOTED
⚠️  REQUIRED: Use this EXACT schema with properly quoted string values:

{
  "matched_required_keywords": ["keyword1", "keyword2"],
  "matched_preferred_keywords": ["keyword1", "keyword2"],
  "missed_required_keywords": ["keyword1", "keyword2"],
  "missed_preferred_keywords": ["keyword1", "keyword2"],
  "match_counts": {
    "total_required_keywords": 10,
    "total_preferred_keywords": 3,
    "matched_required_count": 6,
    "matched_preferred_count": 2
  },
  "matching_notes": {
    "Excel": "Found in technical skills section",
    "SQL": "Mentioned multiple times in experience",
    "Python": "Explicitly listed and used in projects"
  }
}

🚨 ABSOLUTELY CRITICAL: All values in matching_notes MUST be surrounded by double quotes.
🚨 DO NOT write: "Excel": Found in skills (WRONG - will break JSON parsing)
🚨 ALWAYS write: "Excel": "Found in skills" (CORRECT - proper JSON format)

**INSTRUCTIONS**:
- Be intelligent about semantic matching
- Only mark as MISSING if truly no equivalent skill exists
- Provide clear, helpful reasoning for each decision
- Focus on helping candidate understand gaps
"""
```

#### User Prompt

```python
CV_JD_MATCHING_USER_PROMPT = """Analyze the following CV content against the job description keywords and determine which keywords are present using intelligent matching.

JOB DESCRIPTION KEYWORDS TO MATCH:
Required Keywords: {required_keywords}
Preferred Keywords: {preferred_keywords}

CV CONTENT:
{cv_content}

INSTRUCTIONS:
1. Go through each required keyword and check if it exists in the CV (using smart matching)
2. Go through each preferred keyword and check if it exists in the CV (using smart matching)
3. Separate matched keywords from missed keywords
4. Provide accurate counts for all categories
5. Include notes about any smart matches or context analysis

Remember to use intelligent matching - look for semantic meaning, synonyms, variations, and context, not just exact text matches.

🚨 CRITICAL JSON FORMATTING REQUIREMENTS:
1. Return ONLY valid JSON - no markdown, no code blocks, no additional text
2. ALL string values MUST be enclosed in double quotes
3. In matching_notes section, values MUST be quoted strings like: "Excel": "Found in skills"
4. DO NOT use unquoted text in values - this will break JSON parsing
5. Test your JSON mentally before responding - it must be parseable

Return ONLY the JSON response."""
```

### Usage Example

```python
from app.services.cv_jd_matching import CVJDMatcher

matcher = CVJDMatcher(user_email="user@example.com")
result = await matcher.match_cv_against_jd(
    company_name="Australia_for_UNHCR",
    cv_file_path="path/to/cv.txt",
    temperature=0.0
)

# Access results
matched_required = result.matched_required_keywords
missed_required = result.missed_required_keywords
match_percentage = result.get_match_percentage()
```

---

## Approach 2: Pre-Extracted Skills Comparison

### Location
- **Service**: `cv-magic-app/backend/app/services/skill_extraction/preextracted_comparator.py`

### How It Works

1. **Input**: 
   - Pre-extracted CV skills (technical, soft_skills, domain_keywords)
   - Pre-extracted JD skills (technical, soft_skills, domain_keywords)

2. **Process**:
   - Normalizes and deduplicates skills
   - Uses AI with semantic matching rules
   - Compares skills category by category
   - Identifies exact matches, synonym matches, hierarchical matches

3. **Output**: JSON with matched/missing skills per category + formatted text report

### Key Features

#### 1. Semantic Skill Mapping

The system includes a comprehensive semantic mapping for intelligent matching:

```python
SEMANTIC_SKILL_MAPPING = {
    # Soft Skills Equivalents
    "communication": [
        "communication", "communication skills", "interpersonal skills",
        "verbal communication", "written communication", "presentation skills"
    ],
    "leadership": [
        "leadership", "team leadership", "mentoring",
        "course facilitation", "student engagement", "team management"
    ],
    "teamwork": [
        "teamwork", "collaboration", "collaborative",
        "team collaboration", "cross-functional collaboration"
    ],
    "problem-solving": [
        "problem-solving", "problem solving", "analytical thinking",
        "critical thinking", "troubleshooting", "solution-oriented"
    ],
    
    # Technical Skills Equivalents
    "sql": [
        "sql", "database management", "database querying",
        "relational databases", "postgresql", "mysql"
    ],
    "excel": [
        "excel", "spreadsheets", "microsoft excel"
    ],
    "power bi": [
        "power bi", "business intelligence", "data visualization",
        "dashboard creation", "reporting"
    ],
    "data analysis": [
        "data analysis", "data analytics", "analytics",
        "statistical analysis"
    ],
    # ... many more mappings
}
```

#### 2. Domain Clusters

Groups related domain terms for matching:

```python
DOMAIN_CLUSTERS = {
    "data_analytics_cluster": [
        "business intelligence", "data science", "analytics",
        "data analysis", "data visualization", "dashboard creation"
    ],
    "database_cluster": [
        "data warehouse", "relational databases", "database management",
        "sql databases", "sql", "data storage"
    ],
    "marketing_cluster": [
        "direct marketing", "campaign outcomes", "marketing analytics",
        "customer segmentation", "segmentation strategies"
    ]
}
```

#### 3. Matching Rules

The system uses a hierarchical matching approach:

1. **Exact Match**: Case-insensitive identical skills
2. **Synonym Match**: Professional equivalents (e.g., "Data Analysis" = "Data Analytics")
3. **Hierarchical Match**: Specific skills demonstrate broader capabilities (e.g., "SQL" demonstrates "Database Management")
4. **Domain Context**: Skills in same professional domain
5. **Partial Match**: Similar core concepts (used sparingly)

### Complete Prompt Template

#### JSON Mode Prompt (Primary)

```python
def build_json_prompt(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> str:
    """Return a strict JSON-only comparison prompt with enhanced matching guidance."""
    
    return (
        "You are an expert skill matching system. Compare the pre-extracted skills using INTELLIGENT SEMANTIC MATCHING.\n"
        "DO NOT require exact word matches - use professional skill equivalencies and relationships.\n\n"
        "INPUT LISTS (already normalized, sorted alphabetically):\n"
        f"CV.technical_skills ({cv_tech_count} items) = {cv['technical_skills']}\n"
        f"CV.soft_skills ({cv_soft_count} items) = {cv['soft_skills']}\n"
        f"CV.domain_keywords ({cv_domain_count} items) = {cv['domain_keywords']}\n\n"
        f"JD.technical_skills ({jd_tech_count} items) = {jd['technical_skills']}\n"
        f"JD.soft_skills ({jd_soft_count} items) = {jd['soft_skills']}\n"
        f"JD.domain_keywords ({jd_domain_count} items) = {jd['domain_keywords']}\n\n"
        "INTELLIGENT MATCHING RULES (apply in order):\n"
        "1. EXACT MATCH: Case-insensitive identical skills\n"
        "   ⚠️ CRITICAL: If CV has 'Communication' and JD requires 'Communication' → EXACT MATCH\n"
        "2. SYNONYM MATCH: Professional equivalents:\n"
        "   • 'Data Analysis' = 'Data Analytics' = 'Analytics' = 'Statistical Analysis'\n"
        "   • 'Problem Solving' = 'Problem-Solving' = 'Analytical Thinking' = 'Critical Thinking'\n"
        "   • 'Collaboration' = 'Teamwork' = 'Collaborative' = 'Team Collaboration'\n"
        "   • 'SQL' = 'Database Management' = 'Relational Databases' = 'PostgreSQL' = 'MySQL'\n"
        "   • 'Power BI' = 'Business Intelligence' = 'Data Visualization' = 'Dashboard Creation'\n"
        "3. HIERARCHICAL MATCH: Specific skills demonstrate broader capabilities:\n"
        "   • 'SQL' demonstrates 'Database Management', 'Data Extraction', 'Querying'\n"
        "   • 'Data Science' demonstrates 'Data Analysis', 'Statistical Analysis', 'Machine Learning'\n"
        "   ⚠️ CRITICAL: Do NOT match 'Machine Learning' with 'Data Mining' (different skills)\n"
        "4. DOMAIN CONTEXT: Skills in same professional domain\n"
        "5. PARTIAL MATCH: Similar core concepts (use sparingly)\n\n"
        "CRITICAL CONSTRAINTS:\n"
        f"- CV has {cv_tech_count} technical, {cv_soft_count} soft, {cv_domain_count} domain skills\n"
        f"- JD has {jd_tech_count} technical, {jd_soft_count} soft, {jd_domain_count} domain requirements\n"
        f"- CANNOT match more CV skills than exist: max {cv_tech_count} technical, {cv_soft_count} soft, {cv_domain_count} domain\n"
        "- Each CV skill can only be used once across all categories\n"
        "- Prioritize stronger matches (exact > synonym > hierarchical > domain)\n"
        "- IMPORTANT: Total matched + missing must equal JD requirements count for each category\n\n"
        "OUTPUT (JSON ONLY, no prose, no markdown):\n"
        "{\n"
        "  \"technical_skills\": {\n"
        "    \"matched\": [\n"
        "      {\n"
        "        \"jd_skill\": \"exact JD requirement\",\n"
        "        \"cv_equivalent\": \"matching CV skill\",\n"
        "        \"reasoning\": \"match type and brief explanation\"\n"
        "      }\n"
        "    ],\n"
        "    \"missing\": [\n"
        "      { \"jd_skill\": \"...\", \"reasoning\": \"why no CV equivalent found\" }\n"
        "    ]\n"
        "  },\n"
        "  \"soft_skills\": { \"matched\": [], \"missing\": [] },\n"
        "  \"domain_keywords\": { \"matched\": [], \"missing\": [] }\n"
        "}\n"
    )
```

#### Text Mode Prompt (Legacy)

```python
def build_prompt(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> str:
    """Return the exact comparison prompt with lists injected verbatim."""
    
    return f"""
Compare these pre-extracted CV skills against pre-extracted JD requirements using intelligent semantic matching.

CV SKILLS:
Technical ({cv_tech_count} items): {cv_deduplicated.get('technical_skills', [])}
Soft ({cv_soft_count} items): {cv_deduplicated.get('soft_skills', [])}
Domain ({cv_domain_count} items): {cv_deduplicated.get('domain_keywords', [])}

JD REQUIREMENTS:
Technical ({jd_tech_count} items): {jd_deduplicated.get('technical_skills', [])}
Soft ({jd_soft_count} items): {jd_deduplicated.get('soft_skills', [])}
Domain ({jd_domain_count} items): {jd_deduplicated.get('domain_keywords', [])}

**CRITICAL COUNTING RULES:**
- CV Technical Skills: {cv_tech_count} items
- CV Soft Skills: {cv_soft_count} items  
- CV Domain Keywords: {cv_domain_count} items
- JD Technical Skills: {jd_tech_count} items
- JD Soft Skills: {jd_soft_count} items
- JD Domain Keywords: {jd_domain_count} items
- You CANNOT match more items than exist in the CV
- If CV has {cv_soft_count} soft skills, you can match AT MOST {cv_soft_count} JD soft skills
- If CV has {cv_tech_count} technical skills, you can match AT MOST {cv_tech_count} JD technical skills
- If CV has {cv_domain_count} domain keywords, you can match AT MOST {cv_domain_count} JD domain keywords

**MATCHING RULES:**
- Compare only the provided lists (no external knowledge)
- Use STRICT semantic matching: "Python programming" → "Python" = ✅ match
- "Leadership" → "Team leadership" = ✅ match  
- "Data analysis" → "Analytical skills" = ✅ match
- **CRITICAL**: Only match skills that are DIRECTLY relevant to the job requirements
- **CRITICAL**: Domain keywords must be relevant to the job domain
- **AVOID**: Overly broad matches like "Data Mining" → "Data Analysis" (different skills)
- Only mark as missing if no DIRECT semantic equivalent exists
- Provide brief, clear reasoning
- IMPORTANT: Each skill is counted only once (no duplicates across categories)

**CRITICAL CATEGORIZATION RULES:**
- ✅ MATCHED section: ONLY list JD requirements that have a corresponding skill in the CV
- ❌ MISSING section: ONLY list JD requirements that have NO corresponding skill in the CV
- NEVER list the same JD requirement in both sections

**OUTPUT FORMAT (TEXT ONLY):**
🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: {jd_total}
Matched: [Calculate total matches across all categories]
Missing: [Calculate total missing across all categories]
Match Rate: [Calculate percentage: (Matched / Total Requirements) * 100]

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills            {cv_tech_count:2d}         {jd_tech_count:2d}         [Calculate]         [Calculate]            [Calculate]
Soft Skills                  {cv_soft_count:2d}         {jd_soft_count:2d}         [Calculate]         [Calculate]            [Calculate]
Domain Keywords             {cv_domain_count:2d}         {jd_domain_count:2d}         [Calculate]         [Calculate]            [Calculate]

🧠 DETAILED AI ANALYSIS
--------------------------------------------------------------------------------

🔹 TECHNICAL SKILLS
  ✅ MATCHED JD REQUIREMENTS (K items):
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning: [Be specific - why is this a DIRECT match?]
  ❌ MISSING FROM CV (M items):
    1. JD Requires: '...'
       💡 brief reason why not found: [Be specific - why no DIRECT match exists]

🔹 SOFT SKILLS
  ✅ MATCHED JD REQUIREMENTS (K items):
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning
  ❌ MISSING FROM CV (M items):
    1. JD Requires: '...'
       💡 brief reason why not found

🔹 DOMAIN KEYWORDS
  ✅ MATCHED JD REQUIREMENTS (K items):
    1. JD Required: '...'
       → Found in CV: '...'
       💡 brief reasoning: [Be specific - why is this a DIRECT match?]
  ❌ MISSING FROM CV (M items):
    1. JD Requires: '...'
       💡 brief reason why not found: [Be specific - why no DIRECT match exists]
"""
```

### Usage Example

```python
from app.services.skill_extraction.preextracted_comparator import (
    execute_skills_comparison_with_json_output,
    execute_skills_semantic_comparison
)

# JSON mode (recommended)
json_result = await execute_skills_comparison_with_json_output(
    ai_service=ai_service,
    cv_skills={
        'technical_skills': ['SQL', 'Python', 'Power BI'],
        'soft_skills': ['Communication', 'Leadership'],
        'domain_keywords': ['Data Science', 'Analytics']
    },
    jd_skills={
        'technical_skills': ['SQL', 'Excel', 'Tableau'],
        'soft_skills': ['Communication', 'Teamwork'],
        'domain_keywords': ['Business Intelligence', 'Data Analysis']
    },
    user=current_user,
    temperature=0.0
)

# Text mode (legacy)
text_result = await execute_skills_semantic_comparison(
    ai_service=ai_service,
    cv_skills=cv_skills,
    jd_skills=jd_skills,
    user=current_user,
    temperature=0.0
)
```

### Output Format

#### JSON Output Structure

```json
{
  "technical_skills": {
    "matched": [
      {
        "jd_skill": "SQL",
        "cv_equivalent": "SQL",
        "reasoning": "Exact match - identical skills"
      },
      {
        "jd_skill": "Business Intelligence Tools",
        "cv_equivalent": "Power BI",
        "reasoning": "Hierarchical match - Power BI is a BI tool"
      }
    ],
    "missing": [
      {
        "jd_skill": "Tableau",
        "reasoning": "No equivalent BI tool found in CV"
      }
    ]
  },
  "soft_skills": {
    "matched": [...],
    "missing": [...]
  },
  "domain_keywords": {
    "matched": [...],
    "missing": [...]
  }
}
```

#### Text Output Format

```
🎯 OVERALL SUMMARY
----------------------------------------
Total Requirements: 15
Matched: 10
Missing: 5
Match Rate: 67%

📊 SUMMARY TABLE
--------------------------------------------------------------------------------
Category              CV Total  JD Total   Matched   Missing  Match Rate (%)
Technical Skills              8         5         4         1            80
Soft Skills                   5         6         4         2            67
Domain Keywords               7         4         2         2            50

🧠 DETAILED AI ANALYSIS
--------------------------------------------------------------------------------
...
```

---

## Key Differences Between Approaches

| Feature | Full CV Text Matching | Pre-Extracted Skills Comparison |
|---------|----------------------|--------------------------------|
| **Input** | Full CV text + JD keywords | Pre-extracted CV skills + JD skills |
| **Matching** | Semantic search in CV text | Direct skill-to-skill comparison |
| **Accuracy** | Can find skills in context | More precise, category-based |
| **Performance** | Slower (analyzes full text) | Faster (compares lists) |
| **Use Case** | Initial matching, keyword presence | Detailed gap analysis |
| **Output** | Matched/missed keywords | Matched/missing skills per category |

---

## Validation & Quality Assurance

### Exact Match Detection

The system pre-processes to identify exact matches before AI analysis:

```python
def _identify_exact_matches(cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> Dict[str, List[Dict[str, str]]]:
    """Identify exact matches between CV and JD skills before AI processing."""
    # Case-insensitive matching
    # Ensures exact matches are always included
```

### Result Validation

The system validates comparison results:

```python
def _validate_comparison_results(json_result: Dict[str, Any], cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> bool:
    """
    Validate that the comparison results are mathematically correct.
    - Matched count cannot exceed CV skills count
    - Total matched + missing should equal JD requirements count
    """
```

### Automatic Fixing

If validation fails, the system attempts to fix inconsistencies:

```python
def _fix_inconsistent_json_result(json_result: Dict[str, Any], cv_skills: Dict[str, list], jd_skills: Dict[str, list]) -> Dict[str, Any]:
    """Fix inconsistencies in AI JSON response using rule-based logic."""
    # Trims excess matches
    # Adds missing JD skills
    # Ensures mathematical correctness
```

---

## Integration Points

Both comparison methods are used by:

1. **Skills Analysis Pipeline** (`skills_analysis.py`)
   - Uses pre-extracted skills comparison for detailed gap analysis
   
2. **CV-JD Matching Service** (`cv_jd_matcher.py`)
   - Uses full CV text matching for keyword presence detection
   
3. **ATS Scoring** (`ats_score_calculator.py`)
   - Uses comparison results to calculate match scores
   
4. **CV Tailoring** (`cv_tailoring_service.py`)
   - Uses missing skills to generate recommendations

---

## Configuration

- **Temperature**: Default 0.0 for consistent results
- **Max Tokens**: 2000-3000 depending on mode
- **AI Model**: Configurable via AI service (supports OpenAI and Anthropic)

---

## Best Practices

1. **Use Pre-Extracted Comparison** for detailed skill gap analysis
2. **Use Full CV Text Matching** for initial keyword presence check
3. **Always validate results** to ensure mathematical correctness
4. **Leverage semantic mappings** for intelligent matching
5. **Handle edge cases** like duplicates, normalization, and truncation

