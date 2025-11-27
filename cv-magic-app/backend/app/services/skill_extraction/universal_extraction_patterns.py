"""
Universal Extraction Patterns - Shared between CV and JD extraction

This module contains pattern-based extraction rules that work across ALL industries.
Import these patterns into any skill extraction prompt for consistent behavior.

Usage:
    from app.services.skill_extraction.universal_extraction_patterns import (
        UNIVERSAL_PATTERNS_SYSTEM,
        UNIVERSAL_PATTERNS_USER
    )
"""

# System prompt addition - detailed patterns for the AI to learn
UNIVERSAL_PATTERNS_SYSTEM = """
═══════════════════════════════════════════════════════════════
UNIVERSAL EXTRACTION ENHANCEMENT RULES
═══════════════════════════════════════════════════════════════

Apply these pattern-based rules to ANY document in ANY industry:

**PATTERN 1: Action-to-Deliverable Conversion**
When you see: [Action Verb] + [Technical Noun/Tool]
Extract as: [Technical Noun] OR "[Technical Noun] development/creation"

Action Verbs: develop, built, create, design, implement, deploy, configure, 
              maintain, optimize, automate, analyze, model, visualize, process

Examples (Universal):
- "develop/developed dashboards" → "dashboard development" or "dashboards"
- "build/built pipelines" → "pipeline development" or "pipelines"
- "create/created reports" → "reporting"
- "design/designed systems" → "system design"
- "deploy/deployed infrastructure" → "infrastructure"

**PATTERN 2: Preserve Specific Technology Names**
ALWAYS keep specific technology/tool names. Do NOT generalize.

Rules:
- Specific brand/tool name → Keep exact name
- Both specific and generic mentioned → Extract BOTH

Examples:
- "MSSQL" → Extract "MSSQL" (not just "SQL")
- "PostgreSQL" → Extract "PostgreSQL" (not just "database")
- "React" → Extract "React" (not just "JavaScript framework")
- "Terraform" → Extract "Terraform" (not just "IaC")
- "SQL databases like PostgreSQL" → Extract ["SQL", "PostgreSQL"]
- "CI/CD using Jenkins" → Extract ["CI/CD", "Jenkins"]

**PATTERN 3: Soft Skills from Action Phrases**
When you see action phrases describing HOW someone works:
Extract the base soft skill noun.

Patterns:
- "[verb] effectively/collaboratively/independently" → Extract base skill
  - "work independently" → "independence"
  - "collaborate effectively" → "collaboration"
  - "communicate clearly" → "communication"
- "ability to [verb]" → Extract "[verb-noun]"
  - "ability to solve problems" → "problem-solving"
  - "ability to think critically" → "critical thinking"
- "[adjective] [skill noun]" → Extract just the skill noun
  - "strong analytical thinking" → "analytical thinking"
  - "excellent communication" → "communication"

**PATTERN 4: Keep Compound Terms Together**
When 2-3 words form a single concept → Keep them TOGETHER.

Test: "Does splitting lose meaning?"
- "cloud computing" → ❌ Don't split → Keep as "cloud computing"
- "machine learning" → ❌ Don't split → Keep as "machine learning"
- "clinical trials" → ❌ Don't split → Keep as "clinical trials"
- "data warehousing" → ❌ Don't split → Keep as "data warehousing"
- "large datasets" → ✅ "datasets" works alone → Extract "datasets"

**PATTERN 5: Educational Background as Domain**
When you see: "background in/from [X]" OR "degree in [Y]" OR "experience in [Z]"
Extract: X, Y, Z as domain_knowledge

Universal Pattern:
- "background from Accounting, Business, Finance" → ["Accounting", "Business", "Finance"]
- "degree in Computer Science or Engineering" → ["Computer Science", "Engineering"]
- "experience in Healthcare or Pharmaceutical" → ["Healthcare", "Pharmaceutical"]
- "Master in Data Science" → ["Data Science"]
"""

# User prompt addition - concise reminders for the AI
UNIVERSAL_PATTERNS_USER = """
═══════════════════════════════════════════════════════════════
UNIVERSAL EXTRACTION INSTRUCTIONS:
═══════════════════════════════════════════════════════════════

1. **Action-to-Deliverable**: 
   "develop/built/created [X]" → Extract "[X]" or "[X] development"

2. **Preserve Specificity**: 
   Keep specific tool names. "MSSQL" → "MSSQL" (not generic "SQL")

3. **Soft Skills from Actions**: 
   "work independently" → "independence"
   "collaborate effectively" → "collaboration"

4. **Keep Compound Terms Together**: 
   "cloud computing", "machine learning" → Don't split

5. **Educational Backgrounds → Domain**: 
   "degree in X" OR "background from X" → domain_knowledge

6. **Technical Processes → Technical** (NOT domain):
   data cleaning, ETL, data transformation → TECHNICAL skills

7. **Deduplicate**: 
   Keep shorter/simpler form only
"""

# Cross-industry examples for reference
UNIVERSAL_EXAMPLES = """
═══════════════════════════════════════════════════════════════
UNIVERSAL EXAMPLES (Cross-Industry)
═══════════════════════════════════════════════════════════════

Data Role:
Text: "Developed dashboards using Power BI. Strong analytical skills."
→ Technical: ["Power BI", "dashboard development"], Soft: ["analytical skills"]

Software Engineering:
Text: "Built microservices with Python and Docker. Cloud computing experience."
→ Technical: ["Python", "Docker", "microservices", "cloud computing"]

DevOps Role:
Text: "Designed CI/CD pipelines using Jenkins and Terraform."
→ Technical: ["CI/CD", "Jenkins", "Terraform", "pipeline design"]

Business Analyst:
Text: "Created reports and presentations. Background in Finance or Business."
→ Technical: ["reporting", "presentations"], Domain: ["Finance", "Business"]

CV Example:
Text: "Master of Data Science. 2+ years building ETL pipelines with Python."
→ Technical: ["Python", "ETL pipelines"], Domain: ["Data Science"]
"""


def get_universal_patterns_for_prompt(include_examples: bool = False) -> dict:
    """
    Get universal patterns ready to append to any prompt.
    
    Args:
        include_examples: Whether to include cross-industry examples
        
    Returns:
        Dict with 'system' and 'user' pattern strings
    """
    system_patterns = UNIVERSAL_PATTERNS_SYSTEM
    if include_examples:
        system_patterns += "\n" + UNIVERSAL_EXAMPLES
    
    return {
        "system": system_patterns,
        "user": UNIVERSAL_PATTERNS_USER
    }

