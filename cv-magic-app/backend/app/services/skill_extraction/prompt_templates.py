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
Extract SOFT SKILLS, TECHNICAL SKILLS, and DOMAIN KEYWORDS from this {document_type.lower()} and categorize them:

IMPORTANT: Only extract skills/keywords that are explicitly mentioned or have very strong textual evidence. Avoid assumptions or industry-standard inferences. Do not repeat skills/keywords that are already mentioned.

## {document_type.upper()}:
{document_text}

## SOFT SKILLS:
EXPLICIT (directly stated): List soft skills clearly mentioned
STRONGLY IMPLIED (very likely based on responsibilities): List soft skills heavily suggested with strong textual evidence

## TECHNICAL SKILLS:
EXPLICIT (directly stated): List technical skills, tools, software, qualifications clearly mentioned
STRONGLY IMPLIED (very likely based on responsibilities): List technical skills heavily suggested with strong textual evidence

## DOMAIN KEYWORDS:
EXPLICIT:  Your task is to extract **domain-specific keywords** related strictly to the **job role or functional expertise**, NOT the industry, organization, or its values.
  List **industry terms**, **role-specific language**, **tools**, **methodologies**, **compliance concepts**, and **domain knowledge** that are **directly mentioned** in the {document_type.lower()}.

STRONGLY IMPLIED:
  Your task is to extract **domain-specific keywords** related strictly to the **job role or functional expertise**, NOT the industry, organization, or its values.
  List **domain-relevant concepts** that are **heavily suggested** by the context, responsibilities, or required outputs — even if not explicitly named.

### DO NOT include:
- Company or organization names
- Program/service titles
- Sector-level social causes
- Values or mission statements

## CONTEXT EVIDENCE:
For each skill/keyword, provide the relevant quote from the {document_type.lower()} that supports the extraction

**CRITICAL OUTPUT REQUIREMENT:**
You MUST end your response with EXACTLY these three Python lists (no extra text after them):

SOFT_SKILLS = ["skill1", "skill2", "skill3"]
TECHNICAL_SKILLS = ["skill1", "skill2", "skill3"]  
DOMAIN_KEYWORDS = ["keyword1", "keyword2", "keyword3"]

**EXAMPLE OUTPUT FORMAT:**
SOFT_SKILLS = ["Communication", "Leadership", "Problem-solving"]
TECHNICAL_SKILLS = ["Python", "SQL", "Tableau"]
DOMAIN_KEYWORDS = ["Data analysis", "Business intelligence", "Machine learning"]

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
            "tools, languages, and platforms. No explanations.\n\n"
            "Focus on: Programming languages, software tools, databases, cloud platforms, frameworks, libraries, certifications\n"
            "Avoid: Job titles, company names, business processes, marketing terms\n\n"
            "Examples: Python, SQL, Tableau, AWS, Docker, React, Power BI, Excel, Git, Linux, PostgreSQL, Kubernetes\n\n"
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
            "methodologies, and sector concepts. No explanations.\n\n"
            "Focus on: Industry terminology, methodologies, standards, regulations, sector-specific concepts\n"
            "Avoid: Job titles, technical skills, company names, marketing terms, business processes\n\n"
            "Examples: Data Analysis, Machine Learning, Agile, Scrum, Financial Modeling, Clinical Trials, Compliance\n\n"
            f"Text: {text}"
        )

    # Enhanced combined_structured prompt for comprehensive skill extraction
    if key == "combined_structured":
        return f"""You are a senior CV strategist and hiring consultant. Provide a COMPREHENSIVE and THOROUGH analysis of this {document_type.lower()}. Be extremely detailed and extract ALL relevant skills and keywords.

{document_type.upper()} Content:
{text}

CRITICAL INSTRUCTIONS:
- Extract EVERY skill, tool, technology, and keyword mentioned or strongly implied
- List each skill INDIVIDUALLY with proper capitalization (e.g., "Python", "SQL", "Power BI", "Tableau" as separate items)
- Provide specific supporting quotes for each extraction
- Be thorough and comprehensive - don't miss anything
- Look carefully at every sentence for skills and keywords
- Extract skills from job titles, responsibilities, achievements, and requirements
- Preserve original capitalization for proper nouns and brand names

## SOFT SKILLS:

**EXPLICIT (directly stated):**
[Examine EVERY sentence and extract ALL soft skills that are directly mentioned. Include the exact quote that supports each skill.]

Examples of what to look for:
- Communication, leadership, teamwork, collaboration, problem-solving
- Time management, organization, adaptability, creativity, innovation
- Customer service, interpersonal skills, analytical thinking
- Any personality traits or behavioral skills mentioned

**STRONGLY IMPLIED (very likely based on responsibilities):**
[Look at job responsibilities and infer soft skills that would be required. Provide evidence from the text.]

## TECHNICAL SKILLS:

**EXPLICIT (directly stated):**
[Extract EVERY technical skill, tool, software, programming language, database, platform, framework, library mentioned. List each one INDIVIDUALLY with supporting quotes.]

Be comprehensive - look for:
- Programming languages (Python, R, Java, etc.)
- Software tools (Excel, Tableau, Power BI, etc.)
- Databases (SQL, PostgreSQL, MySQL, etc.)
- Cloud platforms (AWS, Azure, GCP, etc.)
- Frameworks and libraries (Pandas, NumPy, React, etc.)
- Operating systems, version control, development tools
- Certifications, methodologies, standards

**STRONGLY IMPLIED (very likely based on responsibilities):**
[Infer technical skills from job duties and responsibilities with supporting evidence.]

## DOMAIN KEYWORDS:

**EXPLICIT:**
Extract ALL domain-specific terms, methodologies, industry concepts, and functional expertise keywords directly mentioned.

Look for:
- Industry terminology and jargon
- Methodologies (Agile, Scrum, Six Sigma, etc.)
- Business processes and functions
- Sector-specific concepts
- Role-specific language

**STRONGLY IMPLIED:**
Infer domain concepts from context and responsibilities.

### DO NOT include:
- Company or organization names
- Program/service titles  
- Sector-level social causes
- Values or mission statements

## CONTEXT EVIDENCE:

**Soft Skills:**
[For EACH soft skill identified above, provide the exact quote or context that supports it]

**Technical Skills:**
[For EACH technical skill identified above, provide the exact quote or context that supports it]

**Domain Keywords:**
[For EACH domain keyword identified above, provide the exact quote or context that supports it]

**CRITICAL OUTPUT REQUIREMENT:**
After providing the detailed analysis above, you MUST end your response with EXACTLY these three Python lists (no extra text after them):

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
