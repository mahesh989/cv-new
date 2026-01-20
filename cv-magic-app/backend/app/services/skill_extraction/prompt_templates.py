"""
Skill Extraction Prompts - Production Optimized with Rule-Based Validation
Single unified prompt system with automatic categorization correction

Key Design:
- Rule-based prompt (no hardcoded examples)
- Direct Python list output
- Automatic post-processing validation
- Works for ANY IT job description
- Uses shared universal patterns (same as JD extraction)
"""

# Import shared universal patterns (same patterns used in jd_analysis_prompt.py)
import os

from app.services.skill_extraction.universal_extraction_patterns import (
    get_universal_patterns_for_prompt
)

# Toggle simplified skill prompts here (True = test.py style, False = legacy)
USE_SIMPLE_SKILL_PROMPTS = True


class SkillExtractionPrompts:
    """Optimized prompt templates for skill extraction"""
    
    @staticmethod
    def get_system_prompt(document_type: str) -> str:
        """
        System prompt - Universal rules that work for ANY job description
        Uses shared universal patterns (same as JD extraction)
        """
        # Get shared universal patterns (same patterns used by jd_analysis_prompt.py)
        universal_patterns = get_universal_patterns_for_prompt()
        
        return f"""You are a precision skill extractor for {document_type}s. Follow these rules STRICTLY:

EXTRACTION RULES:
1. VERBATIM ONLY - Copy exact phrases from text, never paraphrase
2. STRIP QUALIFIERS - Remove "Advanced", "Expert", "Strong", "Excellent", "5+ years"
3. STRIP VERSIONS - "Python 3.x" → "Python"
4. NO HALLUCINATION - Only extract what is explicitly written
5. SCAN ALL TEXT - Extract from every section equally (Skills, Experience, Projects, Summary)
6. NO SECTION BIAS - Don't favor explicit "Skills:" sections over narrative text

TOOL + DELIVERABLE RULE (CRITICAL):
When a tool and deliverable appear together, extract BOTH separately:
- "Power BI dashboards" → Extract: ["Power BI", "dashboards"]
- "SQL reports" → Extract: ["SQL", "reports"]
- "Python pipelines" → Extract: ["Python", "pipelines"]
- "Tableau visualizations" → Extract: ["Tableau", "visualizations"]

DEDUPLICATION (CRITICAL):
- Keep ONLY the shorter/simpler form when similar phrases exist
- "problem-solving" + "proactive problem solving" → KEEP ONLY "problem-solving"
- "analytical thinking" + "analytical skills" → KEEP ONLY "analytical thinking"
- NEVER include both variations

═══════════════════════════════════════════════════════════════
UNIVERSAL CATEGORIZATION RULES (Work for ANY job type)
═══════════════════════════════════════════════════════════════

RULE 1: TECHNICAL SKILLS
A term is TECHNICAL if it meets ANY of these tests:

TEST 1 - SOFTWARE/TOOL: "Can you install/download/purchase this?"
  ✓ YES → TECHNICAL
  Examples: Excel, Python, JIRA, Docker, Kubernetes, Salesforce

TEST 2 - EXECUTABLE PROCESS: "Can a computer execute/automate this?"
  ✓ YES → TECHNICAL
  Examples: data cleaning, ETL, data transformation, data warehousing,
           statistical methods, API integration, unit testing, CI/CD

TEST 3 - TECHNICAL ARTIFACT: "Is this created using software tools?"
  ✓ YES → TECHNICAL
  Examples: dashboards, data pipelines, APIs, reports, data models

TEST 4 - PROGRAMMING LANGUAGE: "Used to write code or query data?"
  ✓ YES → TECHNICAL
  Examples: Python, SQL, JavaScript, R, VBA, DAX

═══════════════════════════════════════════════════════════════

RULE 2: SOFT SKILLS
A term is SOFT if it meets BOTH:

TEST 1 - HUMAN INTERACTION: "Requires human-to-human interaction?"
TEST 2 - BEHAVIORAL: "Is it a behavioral trait or interpersonal skill?"
  ✓ BOTH YES → SOFT SKILL
  Examples: communication, leadership, collaboration, teamwork,
           problem-solving, attention to detail, analytical thinking

═══════════════════════════════════════════════════════════════

RULE 3: DOMAIN KEYWORDS
A term is DOMAIN if it meets ANY:

TEST 1 - INDUSTRY/SECTOR: "Specific industry or business vertical?"
  ✓ YES → DOMAIN
  Examples: Healthcare, Finance, E-commerce, Nonprofit, Manufacturing

TEST 2 - REGULATORY: "Regulation, standard, or compliance requirement?"
  ✓ YES → DOMAIN
  Examples: GDPR, HIPAA, SOX, ISO 27001, NDIS

TEST 3 - BUSINESS DOMAIN: "Industry-specific business function?"
  ✓ YES → DOMAIN
  Examples: Clinical trials, Underwriting, Food relief, Accounting

CRITICAL EXCLUSIONS - DO NOT PUT IN DOMAIN:
✗ Generic terms: "stakeholders", "insights", "best practices", "data-driven"
✗ Data processes: data cleaning, ETL (these are TECHNICAL)
✗ Generic analytics: "data analytics" (too broad, not industry-specific)

═══════════════════════════════════════════════════════════════

PRIORITY ORDER (if term could fit multiple):
TECHNICAL > SOFT > DOMAIN
{universal_patterns['system']}

OUTPUT: Return ONLY three Python lists, nothing else."""

    @staticmethod
    def get_skill_extraction_template(document_type: str, document_text: str) -> str:
        """
        User prompt - Decision framework for categorization
        """
        return f"""Extract skills from this {document_type}:

{document_text.strip()}

═══════════════════════════════════════════════════════════════
CRITICAL: SCAN ALL TEXT EQUALLY (NO SECTION BIAS)
═══════════════════════════════════════════════════════════════

⚠️ Extract from EVERY section, not just "Skills:" heading
- Scan: Skills sections, Experience bullets, Project descriptions, Summaries
- NO BIAS: Treat all text equally regardless of structure or formatting

⚠️ TOOL + DELIVERABLE PATTERN (Extract BOTH separately):
When you see patterns like:
  "Built Power BI dashboards..." → Extract: "Power BI" AND "dashboards"
  "Created SQL reports..." → Extract: "SQL" AND "reports"
  "Developed Python pipelines..." → Extract: "Python" AND "pipelines"

NEVER extract ONLY the tool and ignore the deliverable!

═══════════════════════════════════════════════════════════════
APPLY THESE TESTS TO EACH TERM:
═══════════════════════════════════════════════════════════════

FOR EACH EXTRACTED TERM, ASK:

QUESTION 1: "Can I install this? OR Can a computer execute this?"
├─ YES → TECHNICAL_SKILLS
└─ NO  → Go to QUESTION 2

QUESTION 2: "Human interaction + Behavioral trait?"
├─ YES → SOFT_SKILLS
└─ NO  → Go to QUESTION 3

QUESTION 3: "Industry/Sector OR Regulatory term?"
├─ YES → DOMAIN_KEYWORDS
└─ NO  → EXCLUDE (too generic)

═══════════════════════════════════════════════════════════════
EXTRACTION ENHANCEMENTS:
═══════════════════════════════════════════════════════════════

1. **Action-to-Deliverable**: "developed dashboards" → "dashboards"
2. **Preserve Specificity**: "PostgreSQL" stays as "PostgreSQL"
3. **Keep Compounds Together**: "machine learning" → don't split
4. **Educational Background → Domain**: "degree in Finance" → Finance

═══════════════════════════════════════════════════════════════
SELF-CHECK BEFORE OUTPUT:
═══════════════════════════════════════════════════════════════

TECHNICAL_SKILLS:
[ ] All software/tools? (Excel, Python, Power BI, SQL, Tableau)
[ ] All data processes? (data cleaning, ETL, data transformation, data warehousing)
[ ] All technical artifacts? (dashboards, reports, APIs, pipelines, visualizations, data models)
[ ] Specific tech names preserved? (MSSQL, PostgreSQL, not just "SQL")
[ ] Extracted from ALL sections? (not just "Skills:" heading)
[ ] BOTH tool AND deliverable when together? ("Power BI dashboards" → "Power BI" + "dashboards")

SOFT_SKILLS:
[ ] All human interaction + behavioral? (communication, leadership, collaboration)
[ ] NO duplicates? (keep shortest form only)
[ ] Extracted from ALL sections? (experience bullets, summaries, etc.)

DOMAIN_KEYWORDS:
[ ] All industry-specific? (Healthcare, Nonprofit, Finance)
[ ] All regulatory? (GDPR, HIPAA, SOX)
[ ] Educational backgrounds included? (Computer Science, Business)
[ ] NO data processes? (those are TECHNICAL)

OUTPUT (exactly this format, nothing else):
TECHNICAL_SKILLS = []
SOFT_SKILLS = []
DOMAIN_KEYWORDS = []"""


def get_simple_skill_prompts(document_type: str, document_text: str) -> dict:
    """
    Minimal three-section prompt inspired by backend/test.py.
    Produces the same Python list assignments expected by existing parsers.
    """
    doc_label = document_type.lower()
    system_prompt = f"""You are a skilled {doc_label} analyzer. Extract skills and categorize them into
technical skills, soft skills, and domain keywords. Return ONLY valid Python list assignments.

CATEGORIZATION RULES:
- TECHNICAL: Tools (SQL, Excel), technical processes (data cleaning, ETL), and artifacts (dashboards, APIs)
- SOFT SKILLS: Human interaction + behavioral traits (communication, leadership, stakeholder management)
- DOMAIN KEYWORDS: Industry or regulatory terms (Healthcare, Finance, Nonprofit, GDPR, fundraising)

EXTRACTION RULES:
- Extract direct mentions AS-IS and keep compounds intact (machine learning, cloud computing)
- Remove qualifiers: "strong SQL" → "SQL"
- Preserve specific tools: "Power BI" stays "Power BI"
- Include implied skills only when clearly supported by the text

OUTPUT (STRICT):
TECHNICAL_SKILLS = [...]
SOFT_SKILLS = [...]
DOMAIN_KEYWORDS = [...]

No commentary, explanations, or markdown."""

    user_prompt = f"""Extract ALL skills from this {document_type} and categorize them:
{document_text.strip()}

Return EXACTLY this format with three Python lists (use double quotes, comma-separated values):
TECHNICAL_SKILLS = ["SQL", "Power BI"]
SOFT_SKILLS = ["communication", "problem-solving"]
DOMAIN_KEYWORDS = ["Healthcare", "Nonprofit"]
"""

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "expected_max_tokens": 1500,
        "prompt_version": "simple",
    }


def get_simple_structured_skill_prompts(document_type: str, document_text: str) -> dict:
    """
    Simplified instructions that still return the full structured JSON payload
    required by the context-aware pipeline (skills + metadata fields).
    """
    doc_label = document_type.lower()
    system_prompt = f"""You are a precise {doc_label} skill extractor. Use short, direct
rules to classify each term into technical, soft, or domain categories.

SIMPLE CLASSIFICATION:
- Technical: tools/technologies (SQL, Power BI), executable processes (ETL, dashboards),
  or technical artifacts (APIs, data pipelines).
- Soft: people-facing or behavioral skills (communication, collaboration, stakeholder management,
  problem-solving, attention to detail).
- Domain: industries, sectors, regulatory or mission-specific terms (Healthcare, Nonprofit, GDPR,
  fundraising).

RULES:
- Copy exact phrases from the document; remove qualifiers ("strong SQL" → "SQL").
- Keep compound terms intact ("machine learning", "cloud computing").
- If a term fits multiple categories, use priority Technical > Soft > Domain.
- Never invent skills that are not clearly implied.

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "technical_skills": [],
  "soft_skills": [],
  "domain_keywords": [],
  "experience_years": number_or_null,
  "education": [],
  "certifications": [],
  "languages": [],
  "summary": "2-3 sentence professional summary"
}}

No narration, no Markdown—just JSON."""

    user_prompt = f"""Analyze this {document_type} and return the JSON exactly in the format above.
Document:

{document_text.strip()}

CHECKLIST BEFORE OUTPUT:
1. Technical skills include all tools, software, data processes, and artifacts found in the text.
2. Soft skills include interpersonal/behavioral phrases (communication, stakeholder management, etc.).
3. Domain keywords cover industries, missions, regulatory terms (Nonprofit, Fundraising, GDPR, etc.).
4. experience_years is a number if explicitly stated, otherwise null.
5. education / certifications / languages arrays list any entries mentioned (empty array if none).
6. summary is a concise 2-3 sentence description covering role scope and strengths."""

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "expected_max_tokens": 2000,
        "prompt_version": "simple_structured",
    }


class SkillCategorizer:
    """
    Rule-based categorizer - Automatically fixes LLM categorization mistakes
    This runs AFTER LLM extraction as a validation layer
    """
    
    # Technical indicators (substring matching - lowercase)
    # ⚠️ IMPORTANT: Single-character indicators (like 'r') are handled separately
    # to avoid false positives (e.g., 'r' matching 'charity')
    TECHNICAL_INDICATORS = {
        # Programming languages (excluding single-char 'r' - handled in EXACT_MATCH_ONLY)
        'python', 'sql', 'javascript', 'java', 'c++', 'scala',  # 'go' in EXACT_MATCH
        'ruby', 'php', 'swift', 'kotlin', 'typescript', 'vba', 'matlab',
        'r programming', 'r language', 'r studio', 'rstudio',  # R with context
        
        # Tools & Software
        'excel', 'power bi', 'tableau', 'looker', 'qlik', 'jira', 'confluence',
        'salesforce', 'sap', 'oracle', 'git', 'github', 'gitlab', 'bitbucket',
        
        # Databases
        'sql server', 'mssql', 'postgresql', 'mysql', 'mongodb', 'redis',
        'cassandra', 'dynamodb', 'snowflake', 'bigquery', 'redshift',
        
        # Cloud platforms
        'aws', 'azure', 'gcp', 'cloud', 'databricks', 'kubernetes', 'docker',
        
        # Data processes (ALWAYS TECHNICAL)
        'data cleaning', 'data transformation', 'data preprocessing',
        'data warehousing', 'data mining', 'data modeling', 'data pipeline',
        'etl', 'elt', 'data integration', 'data migration', 'data collection',
        
        # Technical processes
        'ci/cd', 'api', 'rest api', 'microservices', 'automation',
        'testing', 'unit testing', 'integration testing', 'deployment',
        'version control', 'containerization',
        
        # Analytics & ML
        'machine learning', 'deep learning', 'nlp', 'natural language processing',
        'computer vision', 'neural network', 'algorithm', 'statistical methods',
        'regression', 'classification', 'clustering', 'time series',
        
        # Technical artifacts/outputs
        'dashboard', 'data visualization', 'report', 'data model',
        'architecture', 'framework', 'library', 'pipeline',
        
        # Methodologies (technical practices)
        'agile', 'scrum', 'kanban', 'devops', 'lean', 'waterfall'
    }
    
    # Soft skill indicators
    SOFT_INDICATORS = {
        'communication', 'collaboration', 'teamwork', 'leadership',
        'interpersonal', 'presentation', 'negotiation', 'mentoring',
        'coaching', 'facilitation', 'influencing',
        'attention to detail', 'time management', 'organization',
        'adaptability', 'flexibility', 'resilience', 'creativity',
        'critical thinking', 'problem-solving', 'analytical thinking',
        'decision-making', 'strategic thinking', 'innovation',
        'stakeholder management', 'client relationship', 'customer service'
    }
    
    # Domain indicators (industry/sector/regulatory only)
    DOMAIN_INDICATORS = {
        # Industries
        'healthcare', 'health', 'medical', 'clinical', 'pharmaceutical',
        'finance', 'financial', 'banking', 'insurance', 'investment',
        'retail', 'e-commerce', 'ecommerce', 'consumer goods',
        'manufacturing', 'automotive', 'aerospace', 'defense',
        'telecom', 'telecommunications', 'media', 'entertainment',
        'nonprofit', 'charity', 'ngo', 'social services',
        'education', 'academic', 'university', 'school',
        'government', 'public sector', 'municipal',
        'energy', 'utilities', 'oil and gas', 'renewable',
        'real estate', 'property', 'construction',
        'logistics', 'transportation', 'supply chain',
        'hospitality', 'tourism', 'food service',
        
        # Regulations & Compliance
        'gdpr', 'hipaa', 'sox', 'sarbanes-oxley', 'pci-dss', 'pci dss',
        'iso', 'iso 27001', 'iso 9001', 'ndis', 'finra', 'sec',
        'fda', 'compliance', 'audit', 'regulatory',
        
        # Business domains (field-specific)
        'business', 'accounting', 'commerce', 'economics', 'procurement',
        'fundraising', 'underwriting', 'actuarial', 'treasury',
        'food relief', 'hunger relief', 'disaster relief',
        'clinical trials', 'drug development', 'patient care',
        'risk management', 'fraud detection', 'credit scoring'
    }
    
    # Generic terms to ALWAYS EXCLUDE from domain
    GENERIC_EXCLUSIONS = {
        'stakeholders', 'insights', 'best practices', 'data-driven',
        'decision-making', 'business processes', 'strategy', 'strategic',
        'innovation', 'trends', 'patterns', 'analysis', 'reporting',
        'data analytics', 'analytics', 'business intelligence',
        'performance', 'optimization', 'improvement', 'efficiency',
        'quality', 'accuracy', 'integrity', 'management'
    }
    
    # Single-character or short indicators that must match EXACTLY (no substring matching)
    # These would cause false positives with substring matching (e.g., 'r' in 'charity')
    EXACT_MATCH_INDICATORS = {
        'r': 'technical',      # R programming language
        'c': 'technical',      # C programming language
        'go': 'technical',     # Go programming language (also matches 'algorithm' with substring)
    }
    
    @staticmethod
    def categorize_term(term: str) -> str:
        """
        Rule-based categorization for a single term
        Returns: 'technical', 'soft', 'domain', or 'exclude'
        
        ⚠️ CRITICAL FIX: 
        1. Check EXACT_MATCH_INDICATORS first for single-char terms (e.g., 'r', 'c')
        2. Check SOFT_INDICATORS before TECHNICAL_INDICATORS to prevent false matches
        3. Use substring matching only for multi-character indicators
        """
        term_lower = term.lower().strip()
        
        # Priority 0: Check exact-match-only indicators (single chars like 'r', 'c')
        # These are checked FIRST because they require exact match to avoid false positives
        # e.g., "R" should be technical, but "charity" should NOT match 'r'
        if term_lower in SkillCategorizer.EXACT_MATCH_INDICATORS:
            return SkillCategorizer.EXACT_MATCH_INDICATORS[term_lower]
        
        # Priority 1: Check if should be excluded (generic terms)
        # Only exclude if the exclusion is an exact match or the term contains the exclusion
        for exclusion in SkillCategorizer.GENERIC_EXCLUSIONS:
            if exclusion == term_lower or (len(exclusion) <= len(term_lower) and exclusion in term_lower):
                return 'exclude'
        
        # Priority 2: Check SOFT_INDICATORS BEFORE TECHNICAL_INDICATORS
        for indicator in SkillCategorizer.SOFT_INDICATORS:
            if indicator == term_lower or indicator in term_lower:
                return 'soft'
        
        # Priority 3: Check technical (after soft to avoid false matches)
        for indicator in SkillCategorizer.TECHNICAL_INDICATORS:
            if indicator == term_lower or indicator in term_lower:
                return 'technical'
        
        # Priority 4: Check domain
        for indicator in SkillCategorizer.DOMAIN_INDICATORS:
            if indicator == term_lower or indicator in term_lower:
                return 'domain'
        
        # Default: exclude if uncertain (better safe than wrong category)
        return 'exclude'
    
    @staticmethod
    def recategorize_skills(skills_dict: dict) -> dict:
        """
        Re-categorize ALL skills using rule-based logic
        This fixes any LLM categorization mistakes automatically
        
        Args:
            skills_dict: Dict with 'technical_skills', 'soft_skills', 'domain_keywords'
        
        Returns:
            Dict with corrected categorization
        """
        # Collect all unique terms from all categories
        all_terms = []
        for category in ['technical_skills', 'soft_skills', 'domain_keywords']:
            all_terms.extend(skills_dict.get(category, []))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in all_terms:
            term_lower = term.lower()
            if term_lower not in seen:
                seen.add(term_lower)
                unique_terms.append(term)
        
        # Recategorize each term using rules
        technical = []
        soft = []
        domain = []
        
        for term in unique_terms:
            category = SkillCategorizer.categorize_term(term)
            if category == 'technical':
                technical.append(term)
            elif category == 'soft':
                soft.append(term)
            elif category == 'domain':
                domain.append(term)
            # 'exclude' terms are dropped
        
        # Deduplicate soft skills (keep shortest variant)
        soft_deduped = {}
        for skill in soft:
            # Remove common qualifiers to find base skill
            base = skill.lower()
            for qualifier in ['strong ', 'excellent ', 'proactive ', 'effective ', 'good ']:
                base = base.replace(qualifier, '')
            
            if base not in soft_deduped or len(skill) < len(soft_deduped[base]):
                soft_deduped[base] = skill
        
        return {
            'technical_skills': sorted(technical),
            'soft_skills': sorted(soft_deduped.values()),
            'domain_keywords': sorted(domain)
        }


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
        # Main extraction prompt with universal rules
        extractor = SkillExtractionPrompts()
        return extractor.get_skill_extraction_template(document_type, text)
    
    elif key == "technical_skills":
        return f"""Extract ONLY technical skills from this text. Return a comma-separated list.

UNIVERSAL RULE: A skill is TECHNICAL if you can answer YES to:
"Can I install/download this?" OR "Can a computer execute this?"

WHAT TO EXTRACT:
✓ Software/Tools (Excel, Python, JIRA, Docker)
✓ Programming Languages (SQL, JavaScript, R)
✓ Data Processes (data cleaning, ETL, data transformation)
✓ Technical Artifacts (dashboards, APIs, pipelines)

WHAT TO AVOID:
✗ Soft skills (Communication, Leadership)
✗ Domain terms (Healthcare, Finance)
✗ Generic words (Analysis, Management)

Text:
{text}

Return format: skill1, skill2, skill3 (comma-separated, no brackets)"""

    elif key == "soft_skills":
        return f"""Extract ONLY soft skills from this text. Return a comma-separated list.

UNIVERSAL RULE: A skill is SOFT if it requires:
Human interaction + Behavioral trait

WHAT TO EXTRACT (if explicitly mentioned):
✓ Communication, Collaboration, Teamwork, Leadership
✓ Problem-solving, Analytical thinking, Critical thinking
✓ Attention to detail, Time management, Adaptability

WHAT TO AVOID:
✗ Technical skills (Python, SQL, Excel)
✗ Domain terms (Healthcare, Finance)
✗ Generic terms (Analysis, Management)

Text:
{text}

Return format: skill1, skill2, skill3 (comma-separated, no brackets)"""

    elif key == "domain_keywords":
        return f"""Extract ONLY domain-specific keywords from this text. Return a comma-separated list.

UNIVERSAL RULE: A term is DOMAIN if it's:
Industry/Sector OR Regulatory/Compliance term

WHAT TO EXTRACT:
✓ Industries: Healthcare, Finance, E-commerce, Nonprofit
✓ Regulations: GDPR, HIPAA, SOX, ISO 27001
✓ Domain Functions: Clinical trials, Underwriting, Food relief

WHAT TO AVOID (TOO GENERIC):
✗ "Stakeholders", "Insights", "Best practices", "Data analytics"
✗ Technical tools (SQL, Power BI)
✗ Data processes (data cleaning, ETL)

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


def get_skill_prompts(
    document_type: str,
    document_text: str,
    use_optimized: bool = True,
    allow_simple: bool = False,
    simple_mode: str = "assignments"
) -> dict:
    """
    Get both system and user prompts for skill extraction
    
    Args:
        document_type: "CV" or "Job Description"
        document_text: The text content to analyze
        use_optimized: Deprecated - kept for backward compatibility (always optimized now)
        
    Returns:
        Dict with 'system_prompt' and 'user_prompt' keys
    """
    if allow_simple and USE_SIMPLE_SKILL_PROMPTS:
        if simple_mode == "structured":
            return get_simple_structured_skill_prompts(document_type, document_text)
        return get_simple_skill_prompts(document_type, document_text)
    
    return {
        "system_prompt": SkillExtractionPrompts.get_system_prompt(document_type),
        "user_prompt": SkillExtractionPrompts.get_skill_extraction_template(document_type, document_text),
        "expected_max_tokens": 3000,
        "prompt_version": "optimized"  # Always optimized with rule-based validation
    }


def validate_extraction_quality(skills_dict: dict) -> dict:
    """
    Validate extracted skills meet quality standards
    NOW WITH AUTOMATIC CORRECTION
    
    Args:
        skills_dict: Dict with 'technical_skills', 'soft_skills', 'domain_keywords'
        
    Returns:
        Dict with validation results, warnings, and CORRECTED skills
    """
    warnings = []
    
    # Check for generic domain terms
    generic_terms = {
        'stakeholders', 'insights', 'trends', 'decision-making', 
        'business processes', 'analysis', 'reporting', 'management',
        'data-driven', 'best practices', 'strategy', 'innovation',
        'data analytics'
    }
    
    domain_keywords = [k.lower() for k in skills_dict.get('domain_keywords', [])]
    for term in generic_terms:
        if term in domain_keywords:
            warnings.append(f"Generic domain term detected: '{term}' - will be removed")
    
    # Check for data processes in wrong category
    data_processes = {
        'data cleaning', 'data transformation', 'data warehousing',
        'etl', 'data mining', 'data preprocessing', 'data modeling'
    }
    
    for term in domain_keywords:
        if term.lower() in data_processes:
            warnings.append(f"Data process in Domain: '{term}' - should be Technical")
    
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
        warnings.append(f"Duplicates in Technical & Soft: {list(tech_soft_overlap)[:3]}")
    if tech_domain_overlap:
        warnings.append(f"Duplicates in Technical & Domain: {list(tech_domain_overlap)[:3]}")
    if soft_domain_overlap:
        warnings.append(f"Duplicates in Soft & Domain: {list(soft_domain_overlap)[:3]}")
    
    # AUTOMATIC CORRECTION using rule-based categorizer
    corrected_skills = SkillCategorizer.recategorize_skills(skills_dict)
    
    return {
        'is_valid': len(warnings) == 0,
        'warnings': warnings,
        'quality_score': max(0, 100 - (len(warnings) * 10)),
        'corrected_skills': corrected_skills,  # NEW: Auto-corrected version
        'corrections_applied': len(warnings) > 0
    }