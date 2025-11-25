"""
Skill Extraction Prompts - Production Optimized
Single unified prompt system for maximum efficiency and accuracy

Key Design:
- Single prompt version (no verbose/optimized split)
- Direct Python list output (no unused evidence generation)
- Clear, non-contradictory rules
- Optimized for cost and accuracy
"""


class SkillExtractionPrompts:
    """Optimized prompt templates for skill extraction"""
    
    @staticmethod
    def get_system_prompt(document_type: str) -> str:
        """
        System prompt - loaded once per conversation (cost-efficient)
        Contains all extraction rules to minimize per-request token usage
        """
        return f"""You are a precision skill extractor for {document_type}s. Follow these rules STRICTLY:

EXTRACTION RULES:
1. VERBATIM ONLY - Copy exact phrases from text, never paraphrase or use synonyms
2. STRIP QUALIFIERS - Remove "Advanced", "Expert", "Strong", "Excellent", "5+ years"
3. STRIP VERSIONS - "Python 3.x" → "Python", "SQL Server 2019" → "SQL Server"
4. STRIP PARENTHETICALS - "SQL (PostgreSQL, MySQL)" → "SQL"
5. NO HALLUCINATION - Only extract what is explicitly written in the text
6. DEDUPLICATE - If same skill appears with slightly different wording, keep the simpler version only
   Examples: "problem-solving" + "proactive problem solving" → keep "problem-solving" only
             "SQL" + "SQL databases" → keep "SQL" only

CATEGORIZATION PRIORITY (Technical > Domain > Soft):

TECHNICAL SKILLS (highest priority):
- Programming/query languages: Python, SQL, R, JavaScript, VBA, Java
- Software tools: Power BI, Tableau, Excel, Salesforce, JIRA
- Databases: PostgreSQL, MySQL, SQL Server, MongoDB, Oracle, MSSQL
- Cloud platforms: AWS, Azure, GCP, Databricks, Snowflake
- Technical processes: Data cleaning, Data preprocessing, ETL, Data transformation, Data mining, Statistical methods, Data modeling
- Technical outputs: Dashboards, Reports, Data visualizations
- Development tools: Docker, Git, APIs

SOFT SKILLS (only if EXPLICITLY stated):
- Must have context like "skills", "ability to", "demonstrated", "excellent"
- Examples: Communication, Collaboration, Problem-solving, Analytical thinking, Leadership
- Stakeholder management, Time management, Project management, Attention to detail
- DO NOT infer from actions (e.g., "led team" ≠ "Leadership" unless stated as skill)

DOMAIN KEYWORDS (lowest priority):
- Industry sectors: Healthcare, Financial Services, E-commerce, Nonprofit, Education
- Business functions: Fundraising, Marketing campaigns, Risk management, Procurement
- Regulatory terms: GDPR, HIPAA, NDIS, SOX compliance
- Sector-specific: Social procurement, Clinical trials, Donor management, Food relief
- EXCLUDE generic terms: "stakeholders", "insights", "best practices", "strategy", "analysis"

OUTPUT: Return ONLY three Python lists, nothing else."""

    @staticmethod
    def get_skill_extraction_template(document_type: str, document_text: str) -> str:
        """
        User prompt - compact extraction request with text and format specification
        """
        return f"""Extract skills from this {document_type}:

═══════════════════════════════════════════════════════════════
{document_text.strip()}
═══════════════════════════════════════════════════════════════

CRITICAL REMINDERS:
- Technical PROCESSES (data cleaning, ETL, statistical methods) → TECHNICAL_SKILLS, not DOMAIN_KEYWORDS
- Cognitive abilities if explicitly stated (numeracy, analytical skills) → SOFT_SKILLS
- Industry/sector context (healthcare, nonprofit, food relief) → DOMAIN_KEYWORDS
- Deduplicate: If "problem-solving" and "proactive problem solving" both appear, keep only "problem-solving"
- Keep different concepts separate: "Data cleaning" and "Data preprocessing" are both kept

OUTPUT FORMAT (exactly this, nothing else):
TECHNICAL_SKILLS = ["skill1", "skill2", "skill3"]
SOFT_SKILLS = ["skill1", "skill2"]
DOMAIN_KEYWORDS = ["keyword1", "keyword2"]

If a category has no skills, use empty list: TECHNICAL_SKILLS = []"""


def get_prompt(key: str, **kwargs) -> str:
    """
    Return prompts by key for different extraction tasks
    
    Supported keys:
    - 'combined_structured': Full extraction (CV/JD)
    - 'technical_skills': Technical skills only
    - 'soft_skills': Soft skills only
    - 'domain_keywords': Domain keywords only
    - 'analyze_match': CV-JD matching analysis
    
    Args:
        key: Prompt type identifier
        **kwargs: Context variables (text, document_type, etc.)
        
    Returns:
        Formatted prompt string
    """
    text = kwargs.get("text", "")
    document_type = kwargs.get("document_type", "document")

    if key == "combined_structured":
        # Main extraction prompt
        extractor = SkillExtractionPrompts()
        return extractor.get_skill_extraction_template(document_type, text)
    
    elif key == "technical_skills":
        return f"""Extract ONLY technical skills from this text. Return a comma-separated list.

RULES:
1. VERBATIM - Use exact words from text
2. NO QUALIFIERS - Remove "Advanced", "Expert", "5+ years"
3. TECHNICAL ONLY - Programming languages, tools, databases, cloud platforms, technical processes

WHAT TO EXTRACT:
✓ Languages: Python, SQL, R, JavaScript
✓ Tools: Power BI, Tableau, Excel, Salesforce
✓ Databases: PostgreSQL, MySQL, SQL Server
✓ Cloud: AWS, Azure, GCP
✓ Processes: Data cleaning, ETL, Data preprocessing

WHAT TO AVOID:
✗ Soft skills (Communication, Leadership)
✗ Domain terms (Healthcare, Marketing)
✗ Generic words (Analysis, Management)

Text:
{text}

Return format: skill1, skill2, skill3 (comma-separated, no brackets)"""

    elif key == "soft_skills":
        return f"""Extract ONLY soft skills from this text. Return a comma-separated list.

RULES:
1. MUST BE EXPLICITLY STATED - Look for "Strong [skill]", "Ability to [action]", "[Skill] skills"
2. VERBATIM - Use exact wording (without qualifiers)
3. NO INFERENCE - Don't assume skills from actions

WHAT TO EXTRACT (if explicitly mentioned):
✓ Communication, Collaboration, Teamwork, Leadership
✓ Problem-solving, Analytical thinking, Critical thinking
✓ Stakeholder management, Time management, Project management
✓ Attention to detail, Adaptability

WHAT TO AVOID:
✗ Technical skills (Python, SQL)
✗ Domain terms (Healthcare, Marketing)
✗ Inferred skills ("led team" ≠ "Leadership" unless stated)
✗ Personality traits ("motivated" unless "self-motivated" stated as skill)

Text:
{text}

Return format: skill1, skill2, skill3 (comma-separated, no brackets)"""

    elif key == "domain_keywords":
        return f"""Extract ONLY domain-specific keywords from this text. Return a comma-separated list.

RULES:
1. VERBATIM - Use exact phrases from text
2. DOMAIN-SPECIFIC - Industry/business/sector terms only
3. NO GENERIC TERMS - Exclude common buzzwords
4. NOT TECHNICAL TOOLS - Those belong in technical skills

WHAT TO EXTRACT:
✓ Industry sectors: Healthcare, Financial Services, E-commerce, Nonprofit
✓ Business functions: Fundraising, Risk management, Procurement
✓ Regulatory: GDPR, HIPAA, NDIS, SOX compliance
✓ Domain processes: Clinical trials, Social procurement, Food relief

WHAT TO AVOID (TOO GENERIC):
✗ "Stakeholders", "Insights", "Trends", "Analysis"
✗ "Best practices", "Strategy", "Innovation"
✗ Technical tools (SQL, Power BI)
✗ Soft skills (Communication, Leadership)

Text:
{text}

Return format: keyword1, keyword2, keyword3 (comma-separated, no brackets)"""

    elif key == "analyze_match":
        from .prompts.analyze_match_prompt import LITMUS_TEST_PROMPT
        cv_text = kwargs.get('cv_text', '')
        job_text = kwargs.get('job_text', '')
        current_date = kwargs.get('current_date', '2025-01-01')
        return LITMUS_TEST_PROMPT.format(cv_text=cv_text, jd_text=job_text, current_date=current_date)
    
    else:
        raise ValueError(
            f"Unknown prompt key: {key}. "
            f"Supported: combined_structured, technical_skills, soft_skills, domain_keywords, analyze_match"
        )


def get_skill_prompts(document_type: str, document_text: str, use_optimized: bool = True) -> dict:
    """
    Get both system and user prompts for skill extraction
    
    Args:
        document_type: "CV" or "Job Description"
        document_text: The text content to analyze
        use_optimized: Deprecated - kept for backward compatibility (always optimized now)
        
    Returns:
        Dict with 'system_prompt' and 'user_prompt' keys
    """
    # Note: use_optimized parameter is kept for backward compatibility but ignored
    # All prompts are now optimized by default
    return {
        "system_prompt": SkillExtractionPrompts.get_system_prompt(document_type),
        "user_prompt": SkillExtractionPrompts.get_skill_extraction_template(document_type, document_text),
        "expected_max_tokens": 500  # Optimized output size
    }


def validate_extraction_quality(skills_dict: dict) -> dict:
    """
    Validate extracted skills meet quality standards
    
    Args:
        skills_dict: Dict with 'technical_skills', 'soft_skills', 'domain_keywords'
        
    Returns:
        Dict with validation results and warnings
    """
    warnings = []
    
    # Check for generic domain terms
    generic_terms = {
        'stakeholders', 'insights', 'trends', 'decision-making', 
        'business processes', 'analysis', 'reporting', 'management',
        'data-driven', 'best practices', 'strategy', 'innovation'
    }
    
    domain_keywords = [k.lower() for k in skills_dict.get('domain_keywords', [])]
    for term in generic_terms:
        if term in domain_keywords:
            warnings.append(f"Generic domain term detected: '{term}' - consider removing")
    
    # Check for qualifiers
    qualifier_words = [
        'advanced', 'expert', 'senior', 'junior', 'strong', 'excellent', 
        'basic', 'intermediate', 'proficient', 'years', 'experience'
    ]
    
    all_skills = (
        skills_dict.get('technical_skills', []) + 
        skills_dict.get('soft_skills', []) + 
        skills_dict.get('domain_keywords', [])
    )
    
    for skill in all_skills:
        skill_lower = skill.lower()
        for qualifier in qualifier_words:
            if qualifier in skill_lower:
                warnings.append(f"Qualifier detected in '{skill}' - should be removed")
                break
    
    # Check for duplicates across categories
    technical_set = {s.lower() for s in skills_dict.get('technical_skills', [])}
    soft_set = {s.lower() for s in skills_dict.get('soft_skills', [])}
    domain_set = {s.lower() for s in skills_dict.get('domain_keywords', [])}
    
    tech_soft_overlap = technical_set & soft_set
    tech_domain_overlap = technical_set & domain_set
    soft_domain_overlap = soft_set & domain_set
    
    if tech_soft_overlap:
        warnings.append(f"Duplicates in Technical & Soft Skills: {list(tech_soft_overlap)[:3]}")
    if tech_domain_overlap:
        warnings.append(f"Duplicates in Technical & Domain: {list(tech_domain_overlap)[:3]}")
    if soft_domain_overlap:
        warnings.append(f"Duplicates in Soft Skills & Domain: {list(soft_domain_overlap)[:3]}")
    
    return {
        'is_valid': len(warnings) == 0,
        'warnings': warnings,
        'quality_score': max(0, 100 - (len(warnings) * 10))
    }
