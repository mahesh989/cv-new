"""
Production-Grade Skill Extraction Prompts - Maximum Precision
Version 2.0 - Designed for 95%+ extraction accuracy with zero hallucination
"""

class SkillExtractionPrompts:
    """Precision-focused prompt templates for skill extraction"""
    
    @staticmethod
    def get_skill_extraction_template(document_type: str, document_text: str) -> str:
        """
        Create precision extraction prompt for CV or JD
        
        Args:
            document_type: "CV" or "Job Description"
            document_text: The actual text content to analyze
            
        Returns:
            Formatted prompt string with strict extraction rules
        """
        return f'''
You are a precision keyword extractor. Extract EVERY skill and keyword from this {document_type.lower()} using VERBATIM text only.

═══════════════════════════════════════════════════════════════
CARDINAL RULES - VIOLATING THESE INVALIDATES THE ENTIRE OUTPUT
═══════════════════════════════════════════════════════════════

1. VERBATIM EXTRACTION ONLY
   ✓ Copy EXACT phrases from the text
   ✗ Do NOT use synonyms, paraphrasing, or your interpretation
   
   Examples:
   Text says: "Power BI"          → Extract: "Power BI" ✓
   Text says: "Power BI"          → Extract: "BI Tools" ✗ WRONG
   Text says: "Data cleaning"     → Extract: "Data cleaning" ✓
   Text says: "Data cleaning"     → Extract: "Data preparation" ✗ WRONG

2. ZERO HALLUCINATION
   ✓ Extract ONLY what is explicitly written
   ✗ Do NOT infer, assume, or add skills based on role/context
   
   Examples:
   Text mentions: "Data Analyst role"      → Do NOT add "Excel" unless stated
   Text mentions: "Python developer"       → Do NOT add "programming" unless stated
   Text mentions: "5+ years experience"    → Do NOT extract "Senior level"

3. PRESERVE GRANULARITY
   ✓ Keep separate mentions as separate extractions
   ✗ Do NOT consolidate related skills
   
   Examples:
   Text: "Data cleaning, data preprocessing, data transformation"
   Extract: ["Data cleaning", "Data preprocessing", "Data transformation"] ✓
   Do NOT: ["Data management"] ✗ WRONG - loses specificity

4. SINGLE CATEGORIZATION
   ✓ Each keyword appears in EXACTLY ONE category
   ✗ Do NOT duplicate across Technical/Soft/Domain
   
   Priority: Technical > Domain > Soft Skills
   If "SQL" appears → Technical only (not also in Domain)

5. NO QUALIFIERS IN OUTPUT
   ✓ Extract the pure skill without level/experience descriptors
   ✗ Remove: "Advanced", "Expert", "5+ years", "Strong", "Excellent"
   
   Examples:
   Text: "Advanced SQL skills"        → Extract: "SQL" ✓
   Text: "Expert in Power BI"         → Extract: "Power BI" ✓
   Text: "5+ years Python"            → Extract: "Python" ✓
   Text: "Strong communication"       → Extract: "Communication" ✓

═══════════════════════════════════════════════════════════════
CATEGORIZATION GUIDELINES
═══════════════════════════════════════════════════════════════

## TECHNICAL SKILLS
Extract if it's a:
- Programming/scripting language (Python, SQL, R, JavaScript, VBA, C#, Java)
- Software tool (Power BI, Tableau, Excel, Salesforce, JIRA, Git)
- Database system (PostgreSQL, MySQL, SQL Server, MongoDB, Oracle)
- Cloud platform (AWS, Azure, GCP, Databricks, Snowflake)
- Framework/library (React, Django, Pandas, NumPy, TensorFlow)
- Technical process (ETL, Data cleaning, Data preprocessing, API integration, CI/CD)
- Development tool (Docker, Kubernetes, Jenkins, VS Code)
- Technical methodology (Agile development, DevOps, Test-driven development)

MUST BE EXPLICITLY MENTIONED - no assumptions based on job title

Examples from text:
"Experience with SQL, Python, and Power BI" → ["SQL", "Python", "Power BI"]
"Data cleaning and preprocessing required" → ["Data cleaning", "Data preprocessing"]
"Tableau or similar tools" → ["Tableau"] only (ignore "similar tools")

## SOFT SKILLS
Extract ONLY if explicitly stated as a skill/ability with phrases like:
- "Strong [skill]" / "Excellent [skill]" / "[Skill] skills"
- "Ability to [action]" / "Capable of [action]"
- "Demonstrated [skill]" / "Proven [skill]"

Common soft skills:
- Communication, Collaboration, Teamwork, Leadership
- Problem-solving, Analytical thinking, Critical thinking
- Stakeholder management, Time management, Project management
- Attention to detail, Adaptability, Creativity

DO NOT extract:
- Personality traits without "skills" context ("detail-oriented" ✗ unless "attention to detail" ✓)
- Generic adjectives ("motivated", "driven" ✗ unless "self-motivated" explicitly stated)
- Inferred skills (don't assume "leadership" from "led team" unless stated as skill)

Examples from text:
"Strong communication and stakeholder management skills" → ["Communication", "Stakeholder management"]
"Excellent problem-solving ability" → ["Problem-solving"]
"Led a team of 5" → Do NOT extract "Leadership" (action, not stated skill)

## DOMAIN KEYWORDS
Extract industry-specific and business-specific terms that aren't technical tools:

Include:
- Industry sectors (Healthcare, Financial Services, Supply Chain, E-commerce, Education)
- Business functions (Fundraising, Marketing campaigns, Risk management, Procurement)
- Domain methodologies (Agile methodology, Lean Six Sigma, Theory of Change, Design thinking)
- Regulatory/compliance (GDPR, HIPAA, NDIS, SOX compliance, Data governance)
- Domain-specific processes (Clinical trials, Social procurement, Impact measurement)
- Sector-specific concepts (Donor management, Food relief, Refugee support)

EXCLUDE these generic terms (too broad, appear everywhere):
✗ "Stakeholders", "Business processes", "Insights", "Trends"
✗ "Best practices", "Innovation", "Strategy"
✗ "Analysis", "Reporting", "Management" (unless part of specific phrase)

Examples from text:
"Experience in healthcare data management" → ["Healthcare"] (Technical="Data management", Domain="Healthcare")
"Social procurement and impact measurement" → ["Social procurement", "Impact measurement"]
"Fundraising campaigns for refugee support" → ["Fundraising", "Refugee support"]
"Working with stakeholders" → Do NOT extract (too generic)

═══════════════════════════════════════════════════════════════
EDGE CASE HANDLING
═══════════════════════════════════════════════════════════════

1. COMPOUND LISTINGS
   Text: "Python, SQL, and R"
   Extract: ["Python", "SQL", "R"] - split into separate items
   
   Text: "Data collection and analysis"
   Extract: ["Data collection", "Data analysis"] - split compound phrases

2. TOOLS WITH VERSIONS
   Text: "Python 3.x"
   Extract: "Python" (remove version unless version is critical, e.g., "Python 2" vs "Python 3")

3. ALTERNATIVE PHRASINGS
   Text: "Power BI or Tableau"
   Extract: ["Power BI", "Tableau"] - both explicitly mentioned
   
   Text: "SQL or equivalent"
   Extract: ["SQL"] only - ignore "equivalent"

4. MULTI-WORD TOOLS/SKILLS
   Keep together as single extraction:
   - "Power BI" (not "Power" and "BI")
   - "SQL Server" (not "SQL" and "Server")
   - "Google Cloud Platform" (not separate words)
   - "Stakeholder management" (not "Stakeholder" and "Management")
   - "Machine learning" (not "Machine" and "Learning")

5. ACRONYMS AND FULL NAMES
   Use what appears in text:
   Text says "GCP" → Extract "GCP"
   Text says "Google Cloud Platform" → Extract "Google Cloud Platform"
   Do NOT convert between them

6. CASE SENSITIVITY
   Maintain exact capitalization for:
   - Proper nouns: "Salesforce", "Databricks", "Excel"
   - Acronyms: "SQL", "API", "ETL", "AWS"
   - Brand names: "Power BI", "Microsoft Azure"

═══════════════════════════════════════════════════════════════
EXTRACTION PROCEDURE
═══════════════════════════════════════════════════════════════

Step 1: Read entire {document_type.lower()} carefully
Step 2: For each skill/keyword found:
   a) Copy EXACT phrase (verbatim)
   b) Remove qualifiers (Advanced, Expert, Strong, etc.)
   c) Determine category: Technical > Domain > Soft
   d) Check if already extracted (prevent duplicates)
   e) Verify it's not a generic term (for Domain category)
Step 3: Do NOT add any skills not explicitly in text
Step 4: Do NOT consolidate separate mentions
Step 5: Do NOT use synonyms or rephrase

═══════════════════════════════════════════════════════════════
{document_type.upper()} TEXT TO ANALYZE
═══════════════════════════════════════════════════════════════

{document_text.strip()}

═══════════════════════════════════════════════════════════════
REQUIRED OUTPUT FORMAT
═══════════════════════════════════════════════════════════════

Provide your analysis in two parts:

PART 1 - DETAILED EXTRACTION WITH EVIDENCE:

## TECHNICAL SKILLS
**EXPLICIT (directly stated in text):**
[List each technical skill with supporting quote]
- [Skill name] - "[exact quote from text where it appears]"

**STRONGLY IMPLIED (clear from technical responsibilities):**
[Only if job explicitly requires technical implementation]
- [Skill name] - "[quote showing technical requirement]"

## SOFT SKILLS
**EXPLICIT (directly stated as a skill/ability):**
[List each soft skill with supporting quote]
- [Skill name] - "[exact quote from text where it appears]"

**STRONGLY IMPLIED (clear from interpersonal responsibilities):**
[Only if clearly indicated by specific duties]
- [Skill name] - "[quote showing requirement]"

## DOMAIN KEYWORDS
**EXPLICIT (directly stated):**
[List each domain keyword with supporting quote]
- [Keyword] - "[exact quote from text where it appears]"

**STRONGLY IMPLIED (clear from industry/business context):**
[Only if clearly indicated]
- [Keyword] - "[quote showing context]"

---

PART 2 - FINAL DEDUPLICATED LISTS (REQUIRED):

After your detailed analysis, you MUST end with these three Python lists:

SOFT_SKILLS = ["skill1", "skill2", "skill3"]
TECHNICAL_SKILLS = ["tool1", "tool2", "tool3"]
DOMAIN_KEYWORDS = ["keyword1", "keyword2", "keyword3"]

DEDUPLICATION CHECKLIST:
□ No skill appears in multiple lists
□ All verbatim from text (no synonyms)
□ No qualifiers included (no "Advanced", "Expert", etc.)
□ Granularity preserved (separate mentions kept separate)
□ No generic domain terms ("Stakeholders", "Insights", etc.)
□ No hallucinated skills (only what's in text)
□ Multi-word skills kept together ("Power BI" not split)

═══════════════════════════════════════════════════════════════
END OF INSTRUCTIONS - BEGIN EXTRACTION
═══════════════════════════════════════════════════════════════
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
        return f"""You are a precision skill extraction specialist with zero tolerance for hallucination.

Your task: Extract VERBATIM keywords from {document_type.lower()}s with 100% accuracy.

Core principles:
1. Extract only what is explicitly written - never infer or assume
2. Use exact wording from the text - never paraphrase or use synonyms
3. Preserve granularity - keep separate mentions separate
4. Single categorization - each skill in exactly one category
5. No qualifiers - extract pure skills without level descriptors

You prioritize accuracy over completeness. Better to miss an ambiguous skill than hallucinate one that isn't there."""


def get_prompt(key: str, **kwargs) -> str:
    """
    Return precision extraction prompts by key
    
    Supported keys:
    - 'technical_skills': Extract technical skills only
    - 'soft_skills': Extract soft skills only  
    - 'domain_keywords': Extract domain keywords only
    - 'combined_structured': Extract all with full analysis
    - 'analyze_match': CV-JD matching analysis
    
    Args:
        key: Prompt type identifier
        **kwargs: Context variables (text, document_type, etc.)
        
    Returns:
        Formatted prompt string
    """
    text = kwargs.get("text", "")
    document_type = kwargs.get("document_type", "document")

    if key == "technical_skills":
        return f"""Extract ONLY technical skills from this text. Return a comma-separated list.

CRITICAL RULES:
1. VERBATIM ONLY - Use exact words from text (no synonyms)
2. NO HALLUCINATION - Only extract what is explicitly mentioned
3. NO QUALIFIERS - Remove "Advanced", "Expert", "5+ years" etc.
4. PRESERVE GRANULARITY - Keep separate mentions separate
5. NO GENERIC TERMS - Must be specific tools/technologies

WHAT TO EXTRACT:
✓ Programming languages: Python, SQL, R, JavaScript, VBA, C++, Java
✓ Software tools: Power BI, Tableau, Excel, Salesforce, JIRA, Git
✓ Databases: PostgreSQL, MySQL, SQL Server, MongoDB, Oracle
✓ Cloud platforms: AWS, Azure, GCP, Databricks, Snowflake
✓ Frameworks/libraries: React, Django, Pandas, NumPy, scikit-learn
✓ Technical processes: Data cleaning, Data preprocessing, ETL, API development
✓ Dev tools: Docker, Kubernetes, Jenkins, Visual Studio

WHAT TO AVOID:
✗ Soft skills (Communication, Leadership, etc.)
✗ Domain/business terms (Healthcare, Marketing, etc.)
✗ Generic words (Analysis, Management, Development - unless part of specific tool)
✗ Company names, job titles, qualifiers

EXAMPLES:
Text: "Advanced SQL and Python experience" → Extract: "SQL, Python"
Text: "Power BI or Tableau" → Extract: "Power BI, Tableau"
Text: "Data cleaning and preprocessing" → Extract: "Data cleaning, Data preprocessing"
Text: "5+ years with AWS" → Extract: "AWS"

Text to analyze:
{text}

Return format: skill1, skill2, skill3 (comma-separated, no brackets)"""

    elif key == "soft_skills":
        return f"""Extract ONLY soft skills from this text. Return a comma-separated list.

CRITICAL RULES:
1. MUST BE EXPLICITLY STATED - Look for phrases like:
   - "Strong [skill]" / "Excellent [skill]" / "[Skill] skills"
   - "Ability to [action]" / "Demonstrated [skill]"
2. VERBATIM EXTRACTION - Use exact wording (without qualifiers)
3. NO HALLUCINATION - Don't infer from job duties
4. NO PERSONALITY TRAITS - Unless explicitly stated as skills

WHAT TO EXTRACT (if explicitly mentioned):
✓ Communication, Collaboration, Teamwork, Leadership
✓ Problem-solving, Analytical thinking, Critical thinking
✓ Stakeholder management, Time management, Project management
✓ Attention to detail, Adaptability, Organizational skills
✓ Creativity, Innovation (if stated as skills)

WHAT TO AVOID:
✗ Technical skills (Python, SQL, etc.)
✗ Domain knowledge (Healthcare, Marketing, etc.)
✗ Personality traits NOT stated as skills ("motivated", "driven")
✗ Inferred skills (don't assume "leadership" from "led team")

EXAMPLES:
Text: "Strong communication and collaboration skills" → Extract: "Communication, Collaboration"
Text: "Excellent stakeholder management" → Extract: "Stakeholder management"
Text: "Ability to solve complex problems" → Extract: "Problem-solving"
Text: "Led a team of 5 developers" → Do NOT extract "Leadership" (action, not stated skill)
Text: "Detail-oriented professional" → Do NOT extract (trait, not stated as skill)

Text to analyze:
{text}

Return format: skill1, skill2, skill3 (comma-separated, no brackets)"""

    elif key == "domain_keywords":
        return f"""Extract ONLY domain-specific keywords from this text. Return a comma-separated list.

CRITICAL RULES:
1. VERBATIM ONLY - Use exact phrases from text
2. DOMAIN-SPECIFIC - Must be industry/business/sector terms
3. NO GENERIC TERMS - Exclude common words that appear in all jobs
4. NOT TECHNICAL TOOLS - Those belong in technical skills

WHAT TO EXTRACT:
✓ Industry sectors: Healthcare, Financial Services, Supply Chain, E-commerce, Education, Nonprofit
✓ Business functions: Fundraising, Marketing campaigns, Risk management, Procurement, Impact measurement
✓ Methodologies: Agile methodology, Lean Six Sigma, Theory of Change, Design thinking
✓ Regulatory/compliance: GDPR, HIPAA, NDIS, SOX compliance, Data governance
✓ Domain processes: Clinical trials, Social procurement, Donor management, Food relief

WHAT TO AVOID (TOO GENERIC):
✗ "Stakeholders" - appears in every job
✗ "Business processes" - too generic
✗ "Insights", "Trends", "Analysis" - too common
✗ "Best practices", "Strategy" - buzzwords
✗ "Innovation", "Excellence", "Quality" - values, not keywords
✗ Technical tools (SQL, Power BI) - belong in technical skills
✗ Soft skills (Communication, Leadership) - belong in soft skills

EXAMPLES:
Text: "Healthcare data analytics" → Extract: "Healthcare" (not "data analytics" - that's technical)
Text: "Social procurement and impact measurement" → Extract: "Social procurement, Impact measurement"
Text: "Fundraising campaigns for refugee support" → Extract: "Fundraising, Refugee support"
Text: "GDPR compliance and data governance" → Extract: "GDPR compliance, Data governance"
Text: "Working with stakeholders to drive insights" → Do NOT extract (both too generic)
Text: "Agile methodology and Lean processes" → Extract: "Agile methodology, Lean"

Text to analyze:
{text}

Return format: keyword1, keyword2, keyword3 (comma-separated, no brackets)"""

    elif key == "combined_structured":
        extractor = SkillExtractionPrompts()
        return extractor.get_skill_extraction_template(document_type, text)

    elif key == "analyze_match":
        from .prompts.analyze_match_prompt import LITMUS_TEST_PROMPT
        cv_text = kwargs.get('cv_text', '')
        job_text = kwargs.get('job_text', '')
        current_date = kwargs.get('current_date', '2025-01-01')
        return LITMUS_TEST_PROMPT.format(cv_text=cv_text, jd_text=job_text, current_date=current_date)

    else:
        raise ValueError(f"Unknown prompt key: {key}. Supported: technical_skills, soft_skills, domain_keywords, combined_structured, analyze_match")


# Validation helpers for extraction quality
def validate_extraction_quality(skills_dict: dict) -> dict:
    """
    Validate extracted skills meet quality standards
    
    Args:
        skills_dict: Dict with 'technical', 'soft_skills', 'domain_keywords'
        
    Returns:
        Dict with validation results and warnings
    """
    warnings = []
    
    # Check for generic domain terms
    generic_terms = {'stakeholders', 'insights', 'trends', 'decision-making', 
                     'business processes', 'analysis', 'reporting', 'management',
                     'data-driven', 'best practices', 'strategy', 'innovation'}
    
    domain_keywords = [k.lower() for k in skills_dict.get('domain_keywords', [])]
    for term in generic_terms:
        if term in domain_keywords:
            warnings.append(f"Generic domain term detected: '{term}' - consider removing")
    
    # Check for qualifiers
    qualifier_words = ['advanced', 'expert', 'senior', 'junior', 'strong', 'excellent', 
                       'basic', 'intermediate', 'proficient', 'years']
    
    all_skills = (skills_dict.get('technical', []) + 
                  skills_dict.get('soft_skills', []) + 
                  skills_dict.get('domain_keywords', []))
    
    for skill in all_skills:
        for qualifier in qualifier_words:
            if qualifier in skill.lower():
                warnings.append(f"Qualifier detected in '{skill}' - should be removed")
    
    # Check for duplicates across categories
    technical_set = set(s.lower() for s in skills_dict.get('technical', []))
    soft_set = set(s.lower() for s in skills_dict.get('soft_skills', []))
    domain_set = set(s.lower() for s in skills_dict.get('domain_keywords', []))
    
    tech_soft_overlap = technical_set & soft_set
    tech_domain_overlap = technical_set & domain_set
    soft_domain_overlap = soft_set & domain_set
    
    if tech_soft_overlap:
        warnings.append(f"Duplicates in Technical & Soft Skills: {tech_soft_overlap}")
    if tech_domain_overlap:
        warnings.append(f"Duplicates in Technical & Domain: {tech_domain_overlap}")
    if soft_domain_overlap:
        warnings.append(f"Duplicates in Soft Skills & Domain: {soft_domain_overlap}")
    
    return {
        'is_valid': len(warnings) == 0,
        'warnings': warnings,
        'quality_score': max(0, 100 - (len(warnings) * 10))
    }