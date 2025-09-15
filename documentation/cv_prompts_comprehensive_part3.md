# Comprehensive CV Generation Prompts and Descriptions - Part 3 (Final)

## PART 6: AI RECOMMENDATIONS PROMPTS

### 14. Expert CV Tailoring Consultant Prompt

**Description**: "Generate actionable CV tailoring recommendations based on analysis data"

**Full Template**:
```
You are an expert CV tailoring consultant. Analyze the provided comprehensive analysis data and generate actionable CV tailoring recommendations.

COMPREHENSIVE ANALYSIS DATA:
{analysis_content}

Based on this detailed analysis, provide specific, actionable recommendations for improving the CV to better match the job requirements. Focus on:

1. **Technical Skills Enhancement**: Based on the skills comparison and gaps identified
2. **Soft Skills Positioning**: Leverage identified strengths and address weaknesses  
3. **ATS Score Optimization**: Address specific ATS scoring factors and requirements
4. **Strategic Positioning**: Based on the match analysis and market insights
5. **Keyword Integration**: Use the domain keywords analysis for strategic placement

Provide concrete, implementable advice that will maximize the candidate's chances of success.
```

## PART 7: PRELIMINARY ANALYSIS PROMPTS

### 15. Skill Extraction Prompt for Preliminary Analysis

**Description**: "Unified skill extraction for both CV and JD documents"

**Template Structure**:
```
def create_skill_extraction_prompt(document_type: str, document_text: str) -> str:
    """Create unified skill extraction prompt for CV or JD"""
    
    return f"""
You are a skill extraction specialist analyzing a {document_type}.

Extract EXACTLY three comma-separated lists from the text below. Only include terms that ACTUALLY APPEAR in the document.

CRITICAL RULES:
1. Extract ONLY keywords that ACTUALLY APPEAR in the text
2. Use exact terminology from the text (preserve original casing/naming)
3. Do NOT add skills that are not explicitly mentioned
4. Return results in the exact format specified

Technical Skills: (programming languages, tools, software, platforms, databases, frameworks)
Soft Skills: (interpersonal skills, work habits, communication abilities)
Domain Keywords: (industry-specific terms, certifications, methodologies)

Return exactly in this format (no extra commentary):

Technical Skills: term1, term2, ...
Soft Skills: term1, term2, ...
Domain Keywords: term1, term2, ...

{document_type} TEXT:
{document_text}
"""
```

## PART 8: INTELLIGENT SKILL COMPARISON PROMPTS

### 16. HR Analyst and ATS Skill Matcher Prompt

**Description**: "Expert skill comparison with semantic matching and reasoning"

**Full Template**:
```
You are an expert HR analyst and ATS skill matcher. Compare CV skills against JD requirements with intelligent reasoning.

**OBJECTIVE**: Determine which JD requirements are satisfied by CV skills, and which are missing.

**CRITICAL RULES**:
- Direction: JD → CV (match JD requirements against CV skills)
- MATCHED: JD requirement has corresponding CV skill (including semantic matches)
- MISSING: JD requirement has NO corresponding CV skill
- Provide clear reasoning for each decision
- Use intelligent semantic matching, not just exact text

**CV SKILLS** (What candidate has):
Technical: {cv_technical_skills}
Soft: {cv_soft_skills}
Domain: {cv_domain_keywords}

**JD REQUIREMENTS** (What job needs):
Technical: {jd_technical_skills}
Soft: {jd_soft_skills}
Domain: {jd_domain_keywords}

**INTELLIGENT MATCHING EXAMPLES**:
- "Database proficiency" (JD) matches "SQL, PostgreSQL, MySQL" (CV) → MATCHED
- "BI tools" (JD) matches "Power BI, Tableau" (CV) → MATCHED
- "Management skills" (JD) matches "Leadership, Mentoring" (CV) → MATCHED
- "Data analysis methodologies" (JD) matches "Data analysis, Predictive analytics" (CV) → MATCHED
- "Communication skills" (JD) matches "Communication skills" (CV) → MATCHED

**RETURN STRUCTURED JSON**:
{
    "technical_skills": {
        "matched": [
            {
                "jd_skill": "exact JD requirement",
                "cv_equivalent": "matching CV skill(s)",
                "reasoning": "brief explanation of match"
            }
        ],
        "missing": [
            {
                "jd_skill": "exact JD requirement",
                "reasoning": "why not found in CV"
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

**INSTRUCTIONS**:
- Be intelligent about semantic matching
- Only mark as MISSING if truly no equivalent skill exists
- Provide clear, helpful reasoning for each decision
- Focus on helping candidate understand gaps
```

## PART 9: NEW CV GENERATION PROMPTS (from main.py)

### 17. Complete Professional CV Generation Prompt

**Description**: "Generate complete CV from scratch based on job description"

**Full Template**:
```
Generate a complete professional CV with these essential sections in this exact order:

START WITH CONTACT DETAILS (no header):
Maheshwor Tiwari
0414 032 507 | maheshtwari99@gmail.com | Blogs on Medium | GitHub | Dashboard Portfolio
Residency Status: On student visa; applying for Subclass 485 Temporary Graduate Visa

1. EDUCATION
2. EXPERIENCE
3. PROJECTS
4. SKILLS

MANDATORY FIRST SECTION - CONTACT INFORMATION:
You MUST start the CV with a CONTACT INFORMATION section. Extract these details from the original CV:
- Full name: "Maheshwor Tiwari" 
- Phone number: "0414 032 507"
- Email: "maheshtwari99@gmail.com" 
- Links: "Blogs on Medium | GitHub | Dashboard Portfolio"
- Status: "Residency Status: On student visa; applying for Subclass 485 Temporary Graduate Visa"

Format it exactly like this:
CONTACT INFORMATION
[Name from original CV]
[Phone] | [Email] | [Links from original CV]
[Any additional status/location info from original CV]

Requirements:
- CRITICAL: Start with CONTACT INFORMATION section using ACTUAL details from the original CV
- Do NOT use generic placeholders like [Full Name] - find and use the actual contact information
- For EXPERIENCE: Each company must have 3-5 bullet points using STAR format
- For PROJECTS: Each project must have 3-4 bullet points using STAR format
- Use specific technologies, tools, and methodologies from the job description
- Include quantifiable achievements (percentages, dollar amounts, team sizes)
- SKILLS section: Single paragraph with skills separated by commas (no categories)
- Use action verbs and measurable outcomes in all bullet points
- Follow STAR format: describe situation, task, action taken, and quantifiable result
- Return ONLY the complete CV content with professional formatting
- NO professional summary section

**CRITICAL BULLET POINT FORMATTING REQUIREMENTS:**
- Use • (bullet symbol) or - (dash) at the start of each bullet point
- Each bullet point must start with • or - followed by a space
- Examples:
  • Developed machine learning pipeline using Python and TensorFlow to predict customer churn
  - Improved data processing efficiency by 30% through optimization of SQL queries
  • Led a team of 5 developers to deliver a web application using React and Node.js
- DO NOT use other symbols like *, →, ▪, or any other bullet variations

STAR Format Example: "• Developed machine learning pipeline using Python and TensorFlow to predict customer churn, improving retention forecasting accuracy by 25% and saving $200K annually"

CRITICAL: Do NOT include any commentary, analysis, or explanatory text about the CV. Do NOT write things like "This tailored CV aligns with..." or "This CV emphasizes...". Return ONLY the actual CV content that would appear on the document.

**CRITICAL FORMATTING REQUIREMENTS:**
- Add TWO line breaks (\n\n) between each major section
- Add ONE line break (\n) after each section heading
- Add ONE line break (\n) after each bullet point
- Add ONE line break (\n) between different companies/experiences
- Add ONE line break (\n) between different projects
- Ensure each bullet point is on its own line
- Use proper spacing to make the CV readable as plain text

Format the output as a complete, professional CV ready for job applications with CONTACT INFORMATION as the very first section.
```

## PART 10: SYSTEM MESSAGES AND VALIDATION

### 18. System Validation Messages

#### Missing Input Error Response
```json
{
  "error": true,
  "message": "Missing or invalid input",
  "missing": ["ORIGINAL_CV_TEXT", "JOB_INFO_JSON", "ATS_OUTPUT_LOG", "CV_FRAMEWORK_TEXT"]
}
```

#### Successful Processing Response Structure
```json
{
  "company_name": "string",
  "job_title": "string", 
  "location": "string",
  "work_type": "string",
  "modified_cv_json": {...},
  "rendered_cv_markdown": "string",
  "quality_report": {...},
  "change_log": [...]
}
```

## PART 11: PROMPT ENGINEERING PRINCIPLES

### Key Principles Applied Throughout System

1. **Specificity and Clarity**
   - Every prompt includes explicit instructions
   - Clear delineation of input and output formats
   - Precise language to avoid ambiguity

2. **Context Setting**
   - Role definition at start of each prompt
   - Background information about candidate profile
   - Market-specific requirements (Australian focus)

3. **Output Structuring**
   - JSON format requirements where applicable
   - Specific field definitions
   - Example outputs provided

4. **Validation and Constraints**
   - Hard constraints clearly stated
   - Validation checklists included
   - Error handling instructions

5. **Progressive Enhancement**
   - Prompts build on each other
   - Iterative improvement capabilities
   - Version control through templates

## PART 12: PROMPT CATEGORIES SUMMARY

### Complete Prompt Category Overview

1. **Analysis Prompts** (2 types)
   - Primary CV-JD compatibility analysis
   - User-facing compatibility analysis

2. **Generation Prompts** (3 types)
   - Initial CV tailoring
   - Iterative CV refinement
   - General CV generation

3. **Extraction Prompts** (4 types)
   - Technical skills extraction
   - Soft skills extraction
   - Domain keywords extraction
   - Job metadata extraction

4. **Comparison Prompts** (2 types)
   - LLM-powered skill comparison
   - Intelligent HR analyst comparison

5. **Framework Prompts** (3 types)
   - Comprehensive CV modification
   - Targeted CV improvement
   - Keyword integration

6. **Specialized Prompts** (4 types)
   - Australian market requirements
   - ATS optimization
   - Impact statement formula
   - PhD decision matrix

## PART 13: PROMPT PARAMETERS AND VARIABLES

### Common Template Variables Used

```
{cv_text} - Original CV content
{jd_text} - Job description text
{job_text} - Alternative name for job description
{tailored_cv} - Previously tailored CV content
{user_instruction} - User's specific modification request
{additional_instructions} - Extra generation instructions
{text} - Generic text input for extraction
{company_name} - Company name from job posting
{company_name_clean} - Sanitized company name for filenames
{education_level} - Candidate's education background
{target_roles} - Types of roles being targeted
{experience_years} - Years of experience
{missing_keywords} - Keywords to be integrated
{technical_skills} - Technical skills list
{soft_skills} - Soft skills list
{domain_keywords} - Domain-specific keywords list
{analysis_content} - Previous analysis results
{prompt} - Custom prompt override
```

## PART 14: SPECIAL FORMATTING REQUIREMENTS

### Universal Formatting Rules

1. **Bullet Points**
   - Must use • (bullet) or - (dash) only
   - No *, →, ▪, or other symbols
   - Space required after bullet symbol

2. **Section Structure**
   - Contact → Education → Experience → Projects → Skills
   - No deviation from this order
   - Clear section headers required

3. **Line Spacing**
   - Two line breaks between major sections
   - One line break after section headings
   - One line break between items

4. **Date Formats**
   - Month Year format (e.g., Mar 2023 - Nov 2024)
   - Consistent formatting throughout
   - Australian standard preferred

5. **Skills Section**
   - Single paragraph format
   - Comma-separated values
   - No categorization or subsections
   - 6-10 skills maximum

## PART 15: QUALITY ASSURANCE PROMPTS

### Self-Check Validation Points

Before any CV generation output:
1. ✓ All bullets follow Impact Statement Formula
2. ✓ Tense consistency maintained
3. ✓ No unverified skills added
4. ✓ Education ordered correctly
5. ✓ Skills within limit (6-10)
6. ✓ ATS-safe formatting
7. ✓ Interview-defensible content
8. ✓ Truthfulness preserved
9. ✓ Keyword optimization applied
10. ✓ Professional tone maintained

---

## COMPREHENSIVE EXTRACTION SUMMARY

### Total Prompt Categories Extracted: 18
### Total Unique Prompt Templates: 25+
### Total Description Elements: 150+
### Total Formatting Rules: 50+
### Total Validation Points: 30+

### Key System Characteristics:
- **Philosophy**: Truthfulness and authenticity above all
- **Market Focus**: Australian job market optimization
- **Technology**: ATS compatibility and keyword optimization
- **Methodology**: STAR format and impact statements
- **Personalization**: PhD decision matrix and academic rules
- **Quality**: Multiple validation and self-check mechanisms
- **Evolution**: Iterative improvement capabilities
- **Intelligence**: Semantic matching and AI reasoning

---

*This concludes the comprehensive extraction of CV generation prompts and descriptions from the CV Magic App system. All prompts, templates, descriptions, rules, and guidelines have been extracted and documented across these three parts.*

## END OF COMPREHENSIVE EXTRACTION

**Total Documentation Created:**
- Part 1: Core prompt system and CV generation templates
- Part 2: Skill extraction and framework prompts
- Part 3: AI recommendations and specialized prompts

**Files Created:**
1. `/documentation/cv_generation_prompts_extracted.md` - Initial extraction
2. `/documentation/cv_prompts_comprehensive_part1.md` - Detailed Part 1
3. `/documentation/cv_prompts_comprehensive_part2.md` - Detailed Part 2
4. `/documentation/cv_prompts_comprehensive_part3.md` - Detailed Part 3 (this file)

All CV generation-related prompts, descriptions, and instructional content have been successfully extracted from the system.