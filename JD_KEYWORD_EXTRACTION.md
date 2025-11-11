# Job Description Keyword Extraction - Technical Documentation

## Overview

The system extracts keywords from job descriptions (JD) using AI-powered analysis. Keywords are classified as either **required** or **preferred** based on the language used in the JD, and then categorized into specific skill types.

## Architecture

### Main Components

1. **JD Analyzer Service** (`cv-magic-app/backend/app/services/jd_analysis/jd_analyzer.py`)
   - Main service that orchestrates the analysis
   - Handles caching and file persistence
   - Manages company-specific JD analysis

2. **JD Analysis Prompts** (`cv-magic-app/backend/app/services/jd_analysis/jd_analysis_prompt.py`)
   - Contains the AI prompt templates
   - Defines classification rules and extraction guidelines

3. **AI Service** (`cv-magic-app/backend/app/ai/ai_service.py`)
   - Wrapper around the AI provider (OpenAI/Anthropic)
   - Handles API calls and response parsing

4. **API Routes** (`cv-magic-app/backend/app/routes/jd_analysis.py`)
   - REST endpoints for JD analysis
   - Handles authentication and request/response formatting

## Complete Prompt Templates

The system uses two prompts: a system prompt (instructions) and a user prompt (the actual JD text).

### System Prompt

```python
JD_ANALYSIS_SYSTEM_PROMPT = """You are an expert job description analyzer. Your task is to extract keywords and skills from job descriptions and classify them as either "required" or "preferred" based on the language used, then categorize them into specific skill types.

CLASSIFICATION RULES:

REQUIRED KEYWORDS - Extract from text that uses definitive/mandatory language:
- "Minimum X years"
- "Experience in/with"
- "Strong [skill] skills"
- "Must have"
- "Required"
- "Essential"
- "Necessary"
- From sections like "Requirements", "Must Have", "Essential Criteria"

PREFERRED KEYWORDS - Extract from text that uses softer/optional language:
- "Knowledge of"
- "Appreciation of" 
- "Understanding of"
- "Familiarity with"
- "Nice to have"
- "Preferred"
- "Desirable"
- "Would be an advantage"
- From sections like "Preferred", "Nice to Have", "Desirable"

CATEGORIZATION GUIDELINES:
1. **Technical Skills**: Programming languages, software tools, frameworks, databases, technologies, platforms
   - Examples: SQL, Python, Power BI, Tableau, Excel, VBA, AWS, Azure, Git, Docker
   
2. **Soft Skills**: Communication, leadership, teamwork, problem-solving, analytical thinking, interpersonal skills
   - Examples: Communication, Leadership, Project Management, Teamwork, Problem Solving, Analytical Thinking
   
3. **Experience**: Years of experience, seniority levels, role-specific experience requirements
   - Examples: "2+ years experience", "Senior level", "5+ years preferred", "Entry level"
   
4. **Domain Knowledge**: Industry knowledge, business processes, methodologies, certifications, sector expertise
   - Examples: "Data warehouse", "Marketing campaigns", "Financial modeling", "Agile methodology", "GDPR compliance"

EXTRACTION GUIDELINES:
1. Focus on concrete, actionable keywords (technologies, tools, methodologies, skills)
2. Extract specific software names, programming languages, frameworks
3. Include relevant experience levels (e.g., "2+ years", "senior level")
4. Include both technical and soft skills
5. Keep keywords concise and matchable
6. Remove filler words and focus on the core skill/requirement
7. Categorize each keyword into the appropriate skill type

OUTPUT FORMAT:
Respond with a JSON object only, no additional text:
{
    "experience_years": number_or_null,
    "required_skills": {
        "technical": ["SQL", "Power BI", "VBA"],
        "soft_skills": ["communication", "project management"],
        "domain_knowledge": ["data warehouse", "marketing campaigns"]
    },
    "preferred_skills": {
        "technical": ["Tableau", "Python"],
        "soft_skills": ["leadership"],
        "domain_knowledge": ["machine learning"]
    }
}"""
```

### User Prompt

```python
JD_ANALYSIS_USER_PROMPT = """Analyze the following job description and extract required and preferred keywords/skills with proper categorization:

{job_description}

Remember to:
1. Classify keywords based on the language context they appear in
2. Focus on extracting concrete, matchable skills and technologies
3. Include all types of skills (technical, soft skills, experience, domain knowledge) in the appropriate required/preferred lists"""
```

**Note**: The `{job_description}` placeholder is replaced with the actual JD text when the prompt is used.

## Keyword Extraction Process

### Step 1: Input Processing

The system accepts job descriptions in multiple formats:
- **Text input**: Direct JD text string
- **File input**: JSON or text files containing JD content
- **Company-based**: Loads JD from company-specific directories

```python
# Example: Analyzing JD text
analyzer = JDAnalyzer(user_email="user@example.com")
result = await analyzer.analyze_jd_text(jd_text, temperature=0.0)
```

### Step 2: AI-Powered Extraction

The JD text is sent to an AI model (OpenAI GPT or Anthropic Claude) with a structured prompt that includes:

#### Classification Rules

**REQUIRED KEYWORDS** - Extracted from definitive/mandatory language:
- "Minimum X years"
- "Experience in/with"
- "Strong [skill] skills"
- "Must have"
- "Required"
- "Essential"
- "Necessary"
- Sections like "Requirements", "Must Have", "Essential Criteria"

**PREFERRED KEYWORDS** - Extracted from softer/optional language:
- "Knowledge of"
- "Appreciation of"
- "Understanding of"
- "Familiarity with"
- "Nice to have"
- "Preferred"
- "Desirable"
- "Would be an advantage"
- Sections like "Preferred", "Nice to Have", "Desirable"

#### Categorization

Keywords are categorized into 4 types:

1. **Technical Skills**: Programming languages, software tools, frameworks, databases, technologies, platforms
   - Examples: SQL, Python, Power BI, Tableau, Excel, VBA, AWS, Azure, Git, Docker

2. **Soft Skills**: Communication, leadership, teamwork, problem-solving, analytical thinking
   - Examples: Communication, Leadership, Project Management, Teamwork, Problem Solving

3. **Experience**: Years of experience, seniority levels, role-specific experience requirements
   - Examples: "2+ years experience", "Senior level", "5+ years preferred"

4. **Domain Knowledge**: Industry knowledge, business processes, methodologies, certifications
   - Examples: "Data warehouse", "Marketing campaigns", "Financial modeling", "Agile methodology"

### Step 3: AI Response Parsing

The AI returns a JSON structure:

```json
{
    "experience_years": 3,
    "required_skills": {
        "technical": ["SQL", "Power BI", "VBA"],
        "soft_skills": ["communication", "project management"],
        "domain_knowledge": ["data warehouse", "marketing campaigns"]
    },
    "preferred_skills": {
        "technical": ["Tableau", "Python"],
        "soft_skills": ["leadership"],
        "domain_knowledge": ["machine learning"]
    }
}
```

The system:
1. Parses the JSON response
2. Validates the structure
3. Ensures all category keys exist (with defaults if missing)
4. Creates a `JDAnalysisResult` object

### Step 4: Result Processing

The `JDAnalysisResult` class:
- Merges categorized skills into flat keyword lists (`required_keywords`, `preferred_keywords`)
- Provides helper methods to access skills by category
- Generates summary statistics

```python
# Access methods available:
result.get_technical_skills(required_only=False)
result.get_soft_skills(required_only=False)
result.get_domain_knowledge(required_only=False)
result.get_skill_summary()  # Returns counts by category
```

### Step 5: Caching & Persistence

The system implements intelligent caching:

1. **Hash-based deduplication**: Computes SHA256 hash of JD text to detect duplicates
2. **File-based caching**: Saves analysis results to JSON files in company-specific directories
3. **Cache validation**: Reuses cached results if JD hash matches

```python
# Cache location structure:
{user_base_path}/applied_companies/{company_name}/{company_name}_jd_analysis_{timestamp}.json
```

## API Endpoints

### POST `/api/analyze-jd/{company_name}`

Analyzes job description for a company and saves results.

**Parameters:**
- `company_name`: Company identifier (e.g., "Australia_for_UNHCR")
- `force_refresh`: Force re-analysis even if cached (default: false)
- `temperature`: AI temperature for consistency (default: 0.0)

**Response:**
```json
{
    "success": true,
    "data": {
        "company_name": "Australia_for_UNHCR",
        "required_keywords": ["SQL", "Power BI", ...],
        "preferred_keywords": ["Tableau", "Python", ...],
        "required_skills": {
            "technical": [...],
            "soft_skills": [...],
            "domain_knowledge": [...]
        },
        "preferred_skills": {...},
        "experience_years": 3,
        "analysis_timestamp": "2025-01-09T10:30:00",
        "ai_model_used": "openai/gpt-4",
        "from_cache": false,
        "skill_summary": {...}
    }
}
```

## Alternative Extraction Methods

### Skill Extraction Service

There's also a separate `SkillExtractionService` that extracts skills in a different format:

- **Location**: `cv-magic-app/backend/app/services/skill_extraction/skill_extraction_service.py`
- **Output format**: `technical_skills`, `soft_skills`, `domain_keywords` (no required/preferred distinction)
- **Use case**: Used for skills analysis and matching workflows

### AI Service Direct Method

The `AIService` also has a direct method:

```python
async def analyze_job_description(job_description: str, user: Any) -> AIResponse
```

This returns a simpler format with flat keyword lists (no categorization).

## Key Features

1. **Language-aware classification**: Distinguishes required vs preferred based on linguistic cues
2. **Multi-category extraction**: Categorizes skills into technical, soft, experience, and domain
3. **Intelligent caching**: Prevents redundant analysis of identical JDs
4. **Hash-based deduplication**: Detects duplicate JDs even with minor formatting differences
5. **Flexible input**: Supports text, files, and company-based lookups
6. **Consistent output**: Structured JSON format for easy integration

## Usage Examples

### Analyze JD Text Directly

```python
from app.services.jd_analysis import JDAnalyzer

analyzer = JDAnalyzer(user_email="user@example.com")
result = await analyzer.analyze_jd_text(jd_text)

# Access results
required_tech = result.get_technical_skills(required_only=True)
all_soft_skills = result.get_soft_skills(required_only=False)
summary = result.get_skill_summary()
```

### Analyze Company JD with Caching

```python
result = await analyzer.analyze_and_save_company_jd(
    company_name="Australia_for_UNHCR",
    force_refresh=False,  # Uses cache if available
    temperature=0.0
)
```

### Load Cached Analysis

```python
result = analyzer.load_jd_analysis(company_name="Australia_for_UNHCR")
if result:
    keywords = result.required_keywords
```

## Configuration

- **Temperature**: Default 0.0 for consistent results
- **Max Tokens**: 2000 for response generation
- **AI Model**: Configurable via AI service (supports OpenAI and Anthropic)

## Error Handling

The system handles:
- Invalid JSON responses from AI
- Missing or malformed JD files
- Network errors during AI calls
- File I/O errors during caching

All errors are logged with appropriate context for debugging.

## Integration Points

The extracted keywords are used by:
1. **CV-JD Matching**: `cv_jd_matcher.py` uses keywords to match CV against JD
2. **Skills Analysis**: Combined with CV skills for gap analysis
3. **CV Tailoring**: Guides CV customization to match JD requirements
4. **ATS Scoring**: Used in applicant tracking system scoring algorithms

