# Comprehensive CV Generation Prompts and Descriptions - Part 2

## PART 2: SKILL EXTRACTION TEMPLATES (from prompt_system.py continued)

### 5. Skill Extraction Templates

#### Technical Skills Extraction Template
**Description**: "Extract technical skills, tools, and certifications"

**Full Template**:
```
You are an expert in parsing CVs and job descriptions for technical skills.

Task:  
From the text below, extract only individual technical skills, programming languages, software tools, platforms, libraries, frameworks, and certifications.

CRITICAL RULES:
- Return ONLY a comma-separated list of technical skills
- NO explanations, NO commentary, NO reasoning about why you included or excluded items
- NO quotes around skill names
- NO additional text or explanations whatsoever
- Do NOT include job titles, soft skills, company names, locations, UI/navigation text, or full sentences
- Do NOT include generic phrases, responsibilities, or action verbs
- Include full names for tools/platforms (e.g., "Business Intelligence" not "BI", "Database Management" not just "databases")
- Include implied technical skills (e.g., if "databases" mentioned, include "SQL")
- Include systems administration and technical certifications

Good examples:  
Python, SQL, Tableau, AWS, Docker, ReactJS, Microsoft Excel, Power BI, Salesforce, Google Analytics, Java, C++, Linux, Git, Kubernetes, TensorFlow, Azure, SAP, HTML, CSS, JavaScript, R, SPSS, Hadoop, Jenkins, Business Intelligence, Database Management, Systems Administration, Data Analytics, Management Information Systems, Oracle, MySQL, PostgreSQL, Scrum Master, PMP, AWS Certified Solutions Architect, CCNA, ITIL

Bad examples:  
work from home advanced search, main navigation ethical jobs logo, Data Analyst at Deloitte, managed a team, excellent communication, Sydney, Australia, project management experience, responsible for, join us sign in, job ad, career advice, led a project, passionate about technology

REMEMBER: Return ONLY the skills as a comma-separated list. NO other text.

Text:  
{text}
```

#### Soft Skills Extraction Template
**Description**: "Extract interpersonal and behavioral competencies"

**Full Template**:
```
You are analyzing text for interpersonal and behavioral competencies.

Task:  
From the text below, extract only individual soft skills or interpersonal traits.

CRITICAL RULES:
- Return ONLY a comma-separated list of soft skills
- NO explanations, NO commentary, NO reasoning about why you included or excluded items
- NO quotes around skill names
- NO additional text or explanations whatsoever
- Do NOT include job titles, technical skills, company names, locations, UI/navigation text, or full sentences
- Do NOT include generic phrases, responsibilities, or action verbs
- Do NOT include domain-specific jargon or certifications
- Include values-based and cultural competency skills when mentioned
- Include professional conduct and workplace behavior skills

Good examples:  
Communication, Teamwork, Leadership, Adaptability, Problem Solving, Time Management, Empathy, Resilience, Attention to Detail, Critical Thinking, Decision-Making, Conflict Resolution, Creativity, Flexibility, Work Ethic, Reliability, Collaboration, Active Listening, Negotiation, Emotional Intelligence, Self-Motivation, Stress Management, Organization, Accountability, Patience, Openness to Feedback, Cultural Sensitivity, Diversity Awareness, Inclusivity, Gender Equity Awareness, Analytical Thinking, Troubleshooting, Mentoring, Change Management, Ethics, Integrity

Bad examples:  
apply now, sign in, search jobs, Data Analyst, Python, Sydney, Australia, managed a team, responsible for, join us sign in, job ad, career advice, led a project, passionate about technology, project management experience

REMEMBER: Return ONLY the skills as a comma-separated list. NO other text.

Text:  
{text}
```

#### Domain Keywords Extraction Template
**Description**: "Extract industry-specific terms and sector certifications"

**Full Template**:
```
You are parsing text for industry-specific terms and sector-specific certifications.

Task:  
From the text below, extract only individual domain-specific keywords, industry jargon, sector-specific methodologies, standards, regulations, certifications, and field-specific concepts.

CRITICAL RULES:
- Return ONLY a comma-separated list of domain-specific keywords
- NO explanations, NO commentary, NO reasoning about why you included or excluded items
- NO quotes around keyword names
- NO additional text or explanations whatsoever
- Do NOT include job titles, soft skills, technical skills, company names, locations, UI/navigation text, or full sentences
- Do NOT include generic phrases, responsibilities, or action verbs
- Include industry-specific acronyms, regulations, methodologies, and sector terminology
- Include workplace benefits and HR-related domain terms when relevant
- Include compliance, governance, and regulatory terms

Good examples:  
IFRS, HIPAA, GDPR, Six Sigma, Lean, Agile, Scrum, Basel III, SOX, Clinical Trials, EHR, PCI DSS, ISO 9001, Financial Modeling, Equity Valuation, White Card, RSA, NDIS, AHPRA, APRA, AML, KYC, SAP FICO, Epic, Meditech, Salesforce CRM, Clinical Governance, GMP, HACCP, TGA, PBX, RTO, VET, NDIS Worker Screening, NDIS Practice Standards, Family Violence, Gender Equity, Aboriginal and Torres Strait Islander, KPI, Salary Packaging, Portable Long Service Leave, EAP, Regulatory Compliance, Governance Requirements, Workforce Planning, Professional Development, Brief Intervention Services, Men's Referral Service, Perpetrator Accommodation Support, Peak Body

Bad examples:  
apply now, sign in, search jobs, Data Analyst, Python, Sydney, Australia, managed a team, responsible for, join us sign in, job ad, career advice, led a project, passionate about technology, project management experience, communication, teamwork

REMEMBER: Return ONLY the keywords as a comma-separated list. NO other text.

Text:  
{text}
```

### 6. Job Metadata Extraction Template

**Description**: "Extract company information and job details"

**Full Template**:
```
You are an expert at extracting key information from job descriptions and job postings.

Your task is to extract company name, location, and contact information from the provided job description text.

IMPORTANT EXTRACTION RULES:

1. Company Name: Look for these patterns and prioritize them:
   - Company names mentioned after "at", "with", "for", "by" (e.g., "Data Analyst at Microsoft")
   - Company names in headers, titles, or beginning of job posts
   - Well-known company names (avoid generic terms like "Company", "Organization", "Client")
   - Look in contact information, email domains, or website URLs
   - If multiple companies mentioned, choose the hiring company (not client companies)

2. Location: Extract city, state/territory, country
   - Look for patterns like "Sydney, NSW", "Melbourne, VIC", "Brisbane, QLD"
   - Include remote work information if mentioned
   - If multiple locations, choose the primary work location

3. Contact Info: Extract any phone numbers, email addresses, or contact details

EXTRACTION GUIDELINES:
- Be thorough but accurate - don't guess or make up information
- Prefer specific company names over generic terms
- If company name appears multiple times, use the most complete version
- Look throughout the entire job description, not just the beginning
- Consider the context - is this the hiring company or a client mentioned in the role?

Job Description:
{jd_text}

OUTPUT FORMAT (REQUIRED):
Company: [exact company name found, or "Unknown Company" if truly not found]
Location: [city, state/territory if found, or "Not specified" if not found]
Phone: [phone number if found, or "Not found" if not available]

IMPORTANT: Extract the actual company name that is hiring, not client companies mentioned in job duties. Be specific and accurate.
```

## PART 3: LLM-POWERED SKILL COMPARISON PROMPTS (from main.py)

### 7. Intelligent Skill Comparison Prompt

**Description**: "LLM-powered comparison between cached CV and JD skills"

**Full Prompt**:
```
You are performing a comparison analysis between pre-extracted and cached skill/keyword datasets. Your task is to categorize them into matched and missing categories with maximum precision.

## Input Data Structure
You will receive cached results from different sections where each contains data from both CV and job requirements:
- Cached Technical Skills: {technical_skills}
- Cached Soft Skills: {soft_skills}
- Cached Domain Keywords: {domain_keywords}

## Instructions

LLM-Powered Intelligent Matching
As an advanced language model, leverage your understanding to identify:
- Semantic Relationships (e.g., React.js, ReactJS, React → same technology)
- Skill Hierarchies (e.g., "Machine Learning" encompasses "Neural Networks")
- Industry Synonyms (e.g., "Customer Success" = "Client Relations")
- Contextual Equivalents (e.g., "API Development" matches "RESTful Services")
- Transferable Skills, Implied Competencies, Progressive Skills, Related Technologies
- Intelligent Inference: Understand context and nuance beyond exact string matching

For each job requirement, use your language understanding to determine:
- Match Confidence Levels (Exact, High, Medium, Low, No Match)
- Critical Thinking Process (Context Analysis, Skill Relationship Assessment, Practical Equivalence, Gap Impact Evaluation)

### Output Format
Return results in this exact JSON structure:
{
  "matched_technical_skills": [
    { "skill": "...", "match_type": "exact|semantic", "cv_reference": "..." }
  ],
  "matched_soft_skills": [
    { "skill": "...", "match_type": "exact|semantic", "cv_reference": "..." }
  ],
  "matched_domain_keywords": [
    { "keyword": "...", "match_type": "exact|semantic", "cv_reference": "..." }
  ],
  "missing_technical_skills": [
    { "skill": "..." }
  ],
  "missing_soft_skills": [
    { "skill": "..." }
  ],
  "missing_domain_keywords": [
    { "keyword": "..." }
  ]
}

### Precision Rules
- Avoid False Positives (e.g., Don't match "Java" with "JavaScript")
- Handle Ambiguity: If uncertain about semantic match, classify as missing
- Prefer exact matches over semantic matches
- When multiple CV skills could match one job requirement, choose the closest match
- Validation Checks: Ensure no skill appears in both matched and missing categories
- Confirm match_type accuracy (exact vs semantic)
- Special Cases: Technology Stacks, Experience Levels, Version Specificity

## Data
Technical Skills: {technical_skills_json}
Soft Skills: {soft_skills_json}
Domain Keywords: {domain_keywords_json}

Return ONLY the JSON object in the required format.
```

## PART 4: CV FRAMEWORK AND ADVANCED PROMPTS (from analysis_results/cv_framework.md)

### 8. Comprehensive CV Modification Framework

**Description**: "COMPREHENSIVE_CV_MODIFICATION_PROMPT for LLM-ready CV transformation"

**Full Framework**:
```
# COMPREHENSIVE_CV_MODIFICATION_PROMPT (Cursor/LLM-ready)

ROLE:
You are a senior CV optimization specialist and ATS expert. Your task is to transform CVs with precision by strictly applying the rules in the provided framework. You must only enhance factual, existing content from the original CV. Do not fabricate skills, degrees, employers, or dates. Every enhancement must be truthful, ATS-optimized, and interview-defensible.

INPUTS (FOUR FILES):
1) ORIGINAL_CV_TEXT  (from: analysis_results/{company_name_clean}/original_cv_text.txt)
2) JOB_INFO_JSON  (from: analysis_results/{company_name_clean}/job_info_{company_name_clean}.json)
3) ATS_OUTPUT_LOG  (from: analysis_results/{company_name_clean}/{company_name_clean}_output_log.txt)
4) CV_FRAMEWORK_TEXT  (universal framework rules)

SYSTEM OBJECTIVE:
Modify the user's CV to target the role defined in JOB_INFO_JSON while complying with CV_FRAMEWORK_TEXT and leveraging ATS_OUTPUT_LOG insights (e.g., matched/missing skills, domain terms, recommendations).
- Preserve factual accuracy and chronology.
- Reframe and reorder content for maximum ATS relevance and human readability.
- Apply the Impact Statement Formula to all bullets.
- Respect all framework rules.

HARD CONSTRAINTS:
- Use only verifiable skills/experiences from ORIGINAL_CV_TEXT (or clearly inferable).
- No Professional Summary section.
- Mandatory section order: Contact → Education → Experience → Projects → Skills.
- Experience: Maximum 3 bullets per role, ≤2 lines each.
- Projects: Max 2–3 (depending on experience level, see framework matrix).
- Skills: 6–10 verified terms, concise, comma-separated.
- Education: Order per PhD Strategic Decision Matrix.
- Maintain tense consistency (past for previous roles, present for current).
- No tables, graphics, or non-standard headers.
- Every bullet must be interview-defensible.

OUTPUT FORMAT (STRICT JSON WRAPPER):
Return a single JSON object with EXACTLY these top-level keys:

{
  "company_name": string,
  "job_title": string,
  "location": string,
  "work_type": string,
  "modified_cv_json": {
    "contact": {
      "full_name": string,
      "phone": string,
      "email": string,
      "links": [string],
      "location": string
    },
    "education": [
      {
        "degree": string,
        "institution": string,
        "location": string,
        "dates": string,
        "highlights": ["- ...", "- ..."]
      }
    ],
    "experience": [
      {
        "company": string,
        "title": string,
        "location": string,
        "dates": string,
        "bullets": ["- ...", "- ...", "- ..."]
      }
    ],
    "projects": [
      {
        "name": string,
        "context": string,
        "bullets": ["- ...", "- ...", "- ..."]
      }
    ],
    "skills": "skill1, skill2, skill3, ..."
  },
  "rendered_cv_markdown": string,
  "quality_report": {
    "score": number,
    "checks": [
      {"id": "impact_statement_format", "pass": boolean, "notes": string},
      {"id": "academic_positioning", "pass": boolean, "notes": string},
      {"id": "ats_keyword_integration", "pass": boolean, "notes": string},
      {"id": "tense_consistency", "pass": boolean, "notes": string},
      {"id": "formatting_rules", "pass": boolean, "notes": string}
    ],
    "missing_keywords": [
      {"keyword": string, "reason": "not verified in original CV / not present"}
    ],
    "improvement_notes": [string]
  },
  "change_log": [
    {
      "section": "education or experience or projects or skills or contact",
      "action": "reordered or rewritten or added_metrics or removed_irrelevant or format_fix",
      "before": "short excerpt",
      "after": "short excerpt",
      "rationale": "why this change improves alignment/ATS/readability"
    }
  ]
}

VALIDATION STEP (SELF-CHECK BEFORE OUTPUT):
Every bullet follows Impact Statement Formula and includes authentic scope/metrics where possible.
Tense consistency verified.
No unverified skills/keywords added; missing JD terms listed in missing_keywords.
Education ordered per PhD Strategic Decision Matrix.
Skills limited to 6–10 verified terms.
Formatting is ATS-safe (no tables/graphics).

IF ANY REQUIRED INPUT IS MISSING OR UNPARSEABLE:
Return this minimal JSON instead:
{
  "error": true,
  "message": "Missing or invalid input",
  "missing": ["ORIGINAL_CV_TEXT", "JOB_INFO_JSON", "ATS_OUTPUT_LOG", "CV_FRAMEWORK_TEXT"]
}
```

### 9. CV Evolution and Improvement Prompts

#### Targeted CV Improvement Task
**Description**: "Minimal, targeted improvements to existing CV"

**Full Template**:
```
TARGETED CV IMPROVEMENT TASK:
You are making MINIMAL, TARGETED improvements to an existing CV. 

CRITICAL RULES - FOLLOW EXACTLY:
1. PRESERVE ALL EXISTING CONTENT - Do not remove any jobs, projects, education, or achievements
2. PRESERVE EXACT FORMATTING - Keep the same structure, sections, and layout exactly as shown
3. PRESERVE ALL DATES - Do not change any employment dates, education dates, or project timelines
4. PRESERVE ALL COMPANIES AND ROLES - Keep all job titles, company names, and locations exactly as written
5. ONLY ADD OR ENHANCE - Do not delete, restructure, or rewrite existing content

CURRENT CV CONTENT (PRESERVE EXACTLY):
{cv_text}

IMPROVEMENT INSTRUCTION:
{prompt}

HOW TO APPLY THE IMPROVEMENT:
- If adding skills: Add them to existing bullet points or skills section without removing others
- If adding experience: Enhance existing bullet points by weaving in the new elements naturally
- If adding keywords: Incorporate them into existing descriptions without changing meaning
- If adding achievements: Add new bullet points or enhance existing ones with specific metrics

WHAT YOU MUST RETURN:
The EXACT same CV structure with only the specific improvement requested added/enhanced. Every job, project, education entry, and date must remain identical. Only enhance or add content as specifically requested.

EXAMPLE OF CORRECT APPROACH:
If asked to "include teamwork" - add phrases like "collaborated with cross-functional teams" or "led team initiatives" to existing bullet points, or add new bullet points highlighting team collaboration. DO NOT remove any existing content or change formatting.
```

### 10. Framework Rules and Standards

#### Impact Statement Formula
**Description**: "Method for writing achievement-focused bullet points"

**Formula Structure**:
```
[Action Verb] + [Task/Project] + [Tools/Methods] + [Quantified Result/Impact]

Examples:
• Developed machine learning pipeline using Python and TensorFlow, improving prediction accuracy by 25%
• Optimized SQL queries for data warehouse, reducing processing time from 3 hours to 15 minutes
• Led cross-functional team of 8 to deliver mobile app, achieving 50K downloads in first month
```

#### PhD Strategic Decision Matrix
**Description**: "Rules for including/excluding PhD based on job requirements"

**Decision Rules**:
```
Include PhD when:
- Job explicitly requires PhD or doctoral degree
- Position involves research responsibilities
- Role requires >3 years experience
- Academic or R&D positions

Exclude PhD when:
- Graduate/entry-level roles (≤3 years)
- Industry positions not requiring research
- When PhD might cause overqualification concerns
- Focus on practical/applied roles

Always include:
- Master's in Data Science (most relevant for modern roles)
- Relevant Master's degrees
```

#### ATS Optimization Guidelines
**Description**: "Rules for ensuring ATS compatibility"

**Key Guidelines**:
```
Formatting Rules:
- No tables, columns, or graphics
- Standard section headers only
- Simple bullet points (• or -)
- Consistent date formats
- No headers or footers
- Plain text compatibility

Keyword Optimization:
- Include exact job description terms
- Use industry-standard terminology
- Include both acronyms and full forms
- Natural keyword density (2-3%)
- Keyword variations and synonyms

Structure Requirements:
- Contact information at top
- Clear section divisions
- Reverse chronological order
- No special characters in headers
- Standard fonts only
```

## PART 5: SPECIALIZED PROMPTS AND ENHANCEMENTS

### 11. CV Accuracy Enhancement Prompts

#### Enhanced Keyword Integration Prompt
**Description**: "Focused keyword integration for CV accuracy"

**Template**:
```
KEYWORD INTEGRATION TASK:
You must ensure these specific keywords are naturally integrated into the CV.

REQUIRED KEYWORDS TO ADD:
{missing_keywords}

INTEGRATION RULES:
1. Add keywords ONLY to relevant, truthful contexts
2. Weave keywords into existing bullet points where appropriate
3. Do NOT force keywords where they don't belong
4. Maintain natural language flow
5. Preserve all existing content

VALIDATION CHECKLIST:
□ Each keyword appears at least once
□ Keywords are contextually appropriate
□ No forced or unnatural placement
□ Original meaning preserved
□ Professional tone maintained
```

### 12. Australian Market Specific Requirements

#### Australian CV Standards
**Description**: "Specific requirements for Australian job market"

**Key Elements**:
```
Contact Information:
- Include visa status if applicable
- Australian phone format: 04XX XXX XXX
- Location: City, State abbreviation (e.g., Sydney, NSW)

Visa Status Statement:
"Residency Status: On student visa; applying for Subclass 485 Temporary Graduate Visa"

Date Formats:
- Use Month Year format (e.g., Mar 2023 - Nov 2024)
- Australian academic year considerations

Location Formatting:
- Sydney, NSW
- Melbourne, VIC
- Brisbane, QLD
- Perth, WA
- Adelaide, SA

Industry Certifications:
- White Card (construction)
- RSA (Responsible Service of Alcohol)
- NDIS Worker Screening
- Working with Children Check
```

### 13. Skill Categorization System

#### Technical Skills Categories
```
Programming Languages:
Python, Java, JavaScript, TypeScript, C++, C#, R, SQL, HTML, CSS, PHP, Ruby, Go, Rust, Kotlin, Swift, Perl, Bash, PowerShell

Databases & Query Languages:
SQL, MySQL, PostgreSQL, MongoDB, Redis, Cassandra, Oracle, SQLite, NoSQL, Database Management

Data Science & Analytics:
Machine Learning, Data Analysis, Data Science, Statistical Analysis, Predictive Analytics, Data Modeling, Data Mining, Analytics, Statistics, Regression, Classification, Clustering, Artificial Intelligence, AI, Deep Learning

Data Visualization & BI:
Tableau, Power BI, Matplotlib, Seaborn, Plotly, Data Visualization, Dashboard Design, Reporting, Business Intelligence, BI Tools, Looker, Qlik

Libraries & Frameworks:
Pandas, NumPy, scikit-learn, TensorFlow, PyTorch, Keras, Spark, Hadoop, React, Angular, Vue, Django, Flask, Spring, Node.js

Cloud & DevOps:
AWS, Azure, GCP, Docker, Kubernetes, Jenkins, Git, GitHub, GitLab, CI/CD, DevOps, Cloud Computing, Containerization

Tools & Platforms:
Excel, Google Analytics, Jira, Confluence, Visual Studio Code, PyCharm, Jupyter, Anaconda, Linux, Windows, Snowflake, Databricks

Data Processing & Management:
Data Cleaning, Data Preprocessing, Data Transformation, ETL, Data Pipelines, Data Management, Data Warehousing, Automation
```

#### Soft Skills Categories
```
Core Interpersonal:
Communication, Teamwork, Leadership, Collaboration, Active Listening, Presentation Skills

Problem-Solving:
Critical Thinking, Analytical Thinking, Problem Solving, Decision-Making, Troubleshooting, Innovation

Work Management:
Time Management, Organization, Project Management, Prioritization, Multitasking, Planning

Personal Attributes:
Adaptability, Flexibility, Resilience, Self-Motivation, Work Ethic, Reliability, Accountability

Cultural & Ethics:
Cultural Sensitivity, Diversity Awareness, Inclusivity, Ethics, Integrity, Professional Conduct
```

---

*This is Part 2 of the comprehensive extraction. Part 3 will continue with additional prompts from other system components.*