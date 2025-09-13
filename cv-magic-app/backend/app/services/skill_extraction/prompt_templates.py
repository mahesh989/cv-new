"""
Enhanced Prompt Templates for Skill Extraction - Detailed Output Format

This version generates the comprehensive analysis format shown in document 5
Contains all the prompt templates used for AI-based skill extraction
"""

class SkillExtractionPrompts:
    """Centralized prompt templates for skill extraction"""
    
    @staticmethod
    def get_skill_extraction_template(document_type: str, document_text: str) -> str:
        """
        Create standardized prompt for both CV and JD extraction
        
        Args:
            document_type: Type of document ("CV" or "Job Description")
            document_text: The actual text content to analyze
            
        Returns:
            Formatted prompt string
        """
        return f'''
Extract and categorize ALL professional skills and keywords from this {document_type.lower()}:

RULES:
1. Extract ONLY job-relevant skills and keywords
2. Remove ALL qualifiers ("Advanced", "Expert", "5+ years", etc.) - extract PURE skills only
3. NO duplicates across or within categories - each skill appears ONLY ONCE
4. Priority order: Technical Skills > Soft Skills > Domain Keywords
5. Keep exact capitalization for proper nouns and brand names

## {document_type.upper()}:
{document_text}

## SOFT SKILLS (Interpersonal & Behavioral):
EXPLICIT: Extract interpersonal, behavioral, and personal effectiveness skills directly mentioned
STRONGLY IMPLIED: Only include if specific job duties strongly indicate the need

## TECHNICAL SKILLS (Tools & Technologies):
EXPLICIT: Extract ALL technical tools, languages, platforms, frameworks, databases, APIs mentioned
STRONGLY IMPLIED: Only include if job explicitly requires technical implementation

## DOMAIN KEYWORDS (Industry & Business):
EXPLICIT: Extract industry sectors, business functions, methodologies, regulations, domain processes
STRONGLY IMPLIED: Only include if clearly indicated by industry context

AVOID EXTRACTING:
- Company names, locations, dates
- Generic business terms
- Job titles or seniority levels
- Values or mission statements

## CONTEXT EVIDENCE:
Provide brief quotes supporting each extraction

**FINAL OUTPUT - THREE DEDUPLICATED LISTS:**
Ensure NO skill appears in multiple lists. End with EXACTLY:

SOFT_SKILLS = [list of pure soft skills]
TECHNICAL_SKILLS = [list of pure technical skills]  
DOMAIN_KEYWORDS = [list of industry/business keywords]

Text: """
{document_text.strip()}
"""
'''

    @staticmethod
    def get_system_prompt(document_type: str) -> str:
        """
        Get system prompt for the AI model
        
        Args:
            document_type: Type of document being analyzed
            
        Returns:
            System prompt string
        """
        return f"You are a precise extractor of skills from professional {document_type.lower()}s. Analyze the text and provide detailed skill extraction with supporting evidence, then end with clean Python lists."


# Lightweight centralized prompt accessor for preliminary analysis
def get_prompt(key: str, **kwargs) -> str:
    """Return optimized extraction prompts by key.

    Supported keys:
    - 'technical_skills'
    - 'soft_skills'
    - 'domain_keywords'
    """
    text = kwargs.get("text", "")
    document_type = kwargs.get("document_type", "document")  # e.g., "CV" or "Job Description"

    if key == "technical_skills":
        return (
            "Extract technical skills from this text. Return ONLY a comma-separated list of technical skills, "
            "tools, languages, and platforms. No explanations or qualifiers.\n\n"
            "Rules:\n"
            "- Extract PURE skills without qualifiers (SQL not 'Advanced SQL')\n"
            "- Include ALL technical tools mentioned\n"
            "- Keep exact capitalization and brand names\n\n"
            "Focus on: Programming languages, software tools, databases, cloud platforms, frameworks, libraries, APIs, protocols\n"
            "Avoid: Soft skills, business terms, company names, job titles, generic words\n\n"
            "Examples: Python, SQL, Tableau, AWS, Docker, React, REST API, Kubernetes, PostgreSQL, Git\n\n"
            f"Text: {text}"
        )

    if key == "soft_skills":
        return (
            "Extract soft skills from this text. Return ONLY a comma-separated list of interpersonal and behavioral skills. "
            "No explanations.\n\n"
            "Focus on: Communication, leadership, problem-solving, teamwork, adaptability, time management\n"
            "Avoid: Job titles, technical skills, company names, business processes\n\n"
            "Examples: Communication, Leadership, Problem Solving, Teamwork, Adaptability, Time Management, Collaboration\n\n"
            f"Text: {text}"
        )

    if key == "domain_keywords":
        return (
            "Extract domain-specific keywords from this text. Return ONLY a comma-separated list of industry terms, "
            "business functions, and sector concepts. No explanations.\n\n"
            "Focus on: Industry sectors, business functions, domain processes, methodologies, regulations, business concepts\n"
            "Avoid: Technical tools (those go in technical skills), soft skills, company names, job titles\n\n"
            "Examples: Financial Services, Risk Management, Agile, GDPR Compliance, Supply Chain, Market Research, Healthcare\n\n"
            f"Text: {text}"
        )

    # Enhanced combined_structured prompt for comprehensive skill extraction
    if key == "combined_structured":
        return f"""You are a senior CV strategist and hiring consultant. Extract ALL skills and keywords from this {document_type.lower()}.

{document_type.upper()} Content:
{text}

CRITICAL INSTRUCTIONS FOR PURE KEYWORD EXTRACTION:
- Extract ONLY job-relevant skills, tools, technologies, and professional keywords
- DO NOT extract: general words, articles, prepositions, company names, locations, dates, generic business terms
- List each skill INDIVIDUALLY with proper capitalization
- DO NOT include qualifiers like "Advanced", "Basic", "Expert", "Strong", "Senior", "Junior" - extract PURE SKILL only
- If text says "Advanced SQL" → extract "SQL"
- If text says "5+ years Python" → extract "Python" 
- If text says "Expert in Power BI" → extract "Power BI"
- Extract compound skills as separate items ("SQL and Python" → "SQL", "Python")
- Include nice-to-have/desirable skills from all sections
- AVOID DUPLICATES: If a skill can fit in multiple categories, place it ONLY in the most specific category
- PRIORITY ORDER: Technical Skills > Soft Skills > Domain Keywords (more specific wins)
- NO SEMANTIC DUPLICATES: Don't repeat similar concepts (e.g., if "Python" is in Technical, don't add "Python programming" anywhere)

## SOFT SKILLS:

**EXPLICIT (directly stated):**
[Extract ONLY interpersonal, behavioral, and personality skills that are directly mentioned in professional context]

FOCUS ON:
- Interpersonal skills: Communication, Leadership, Teamwork, Collaboration, Negotiation
- Personal effectiveness: Time Management, Organization, Adaptability, Problem-solving
- Professional traits: Analytical Thinking, Critical Thinking, Creativity, Innovation
- Work style: Detail-oriented, Self-motivated, Proactive, Results-driven

AVOID:
- Technical abilities (goes to Technical Skills)
- Industry knowledge (goes to Domain Keywords)
- Generic adjectives not specific to professional skills
- Company values or mission statements

**STRONGLY IMPLIED (very likely based on responsibilities):**
[Only include if there's STRONG evidence from specific job duties - not generic assumptions]

## TECHNICAL SKILLS:

**EXPLICIT (directly stated):**
[Extract EVERY technical skill, tool, technology, platform, or system that requires specific technical knowledge]

CATEGORIES TO SCAN:
- Programming/Scripting Languages (any mentioned)
- Software/Applications (domain-specific tools, not generic like MS Word)
- Databases/Data Storage (all types)
- Cloud/Infrastructure (platforms, containers, orchestration)
- Frameworks/Libraries (technical ones only)
- Development/Analytics Tools
- Technical Certifications (extract the skill, not the cert name)
- Technical Methodologies (CI/CD, DevOps, etc.)
- APIs/Protocols/Standards (REST, GraphQL, TCP/IP, etc.)
- Hardware/Systems (if relevant)

EXTRACTION RULES:
- Include version numbers if meaningful (e.g., "Python 3", "Java 8")
- Keep brand names exact ("Google Cloud Platform" not "GCP" unless text uses "GCP")
- Technical skills take priority - if something could be technical or domain, put in technical
- Include emerging tech mentioned anywhere in the document

**STRONGLY IMPLIED (very likely based on responsibilities):**
[Only include if job explicitly requires technical implementation - not business use]

## DOMAIN KEYWORDS:

**EXPLICIT:**
[Extract industry-specific and role-specific concepts that aren't technical skills or soft skills]

FOCUS ON:
- Industry/Sector terminology (e.g., "Financial Services", "Healthcare", "E-commerce")
- Business functions (e.g., "Risk Management", "Supply Chain", "Revenue Operations")
- Domain-specific processes (e.g., "Clinical Trials", "Regulatory Compliance", "Customer Acquisition")
- Professional methodologies (e.g., "Agile", "Lean Six Sigma", "Design Thinking")
- Industry standards/regulations (e.g., "GDPR", "HIPAA", "SOX Compliance")
- Business concepts (e.g., "ROI Analysis", "Market Research", "Strategic Planning")

AVOID:
- Skills already in Technical Skills (tools, languages, platforms)
- Skills already in Soft Skills (interpersonal abilities)
- Company/organization names
- Generic business terms ("management", "operations", "business")
- Job titles or seniority levels

**STRONGLY IMPLIED:**
[Only include if clearly indicated by industry context or specific responsibilities]

## CONTEXT EVIDENCE:

**Soft Skills:**
[For EACH soft skill identified above, provide the exact quote or context that supports it]

**Technical Skills:**
[For EACH technical skill identified above, provide the exact quote or context that supports it]

**Domain Keywords:**
[For EACH domain keyword identified above, provide the exact quote or context that supports it]

**CRITICAL OUTPUT REQUIREMENT:**
After providing the detailed analysis above, you MUST end your response with EXACTLY these three Python lists:

DEDUPLICATION RULES:
1. NO skill/keyword should appear in more than one list
2. Technical Skills list gets priority for any tool/technology/platform
3. Soft Skills list gets priority for any interpersonal/behavioral skill
4. Domain Keywords gets what remains (industry/business concepts)
5. Remove semantic duplicates (e.g., "Data Analysis" and "Data Analytics" - keep only one)
6. Keep the most specific version (e.g., "Python" over "Programming")

SOFT_SKILLS = ["skill1", "skill2", "skill3"]
TECHNICAL_SKILLS = ["skill1", "skill2", "skill3"]  
DOMAIN_KEYWORDS = ["keyword1", "keyword2", "keyword3"]

**DETAILED EXTRACTION EXAMPLE:**

## TECHNICAL SKILLS:
**EXPLICIT (directly stated):**
- Python - "Specialized in Python programming"
- Pandas - "using libraries such as Pandas"
- NumPy - "using libraries such as Pandas, NumPy"
- scikit-learn - "and scikit-learn"
- SQL - "Proficient in SQL"
- PostgreSQL - "complex relational databases like PostgreSQL"
- MySQL - "PostgreSQL and MySQL"
- Tableau - "creating interactive dashboards and visualizations using Tableau"
- Power BI - "Tableau, Power BI"
- Matplotlib - "Power BI, and Matplotlib"
[Continue for EVERY skill mentioned...]

Text to analyze:
{text.strip()}
"""

    elif key == "analyze_match":
        from .prompts.analyze_match_prompt import ANALYZE_MATCH_PROMPT
        cv_text = kwargs.get('cv_text', '')
        job_text = kwargs.get('job_text', '')
        return ANALYZE_MATCH_PROMPT.format(cv_text=cv_text, job_text=job_text)

    raise ValueError(f"Unknown prompt key: {key}")
