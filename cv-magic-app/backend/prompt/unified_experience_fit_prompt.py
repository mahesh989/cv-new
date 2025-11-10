"""
Unified Experience, Seniority & Industry Fit Analysis Prompt
Consolidates ExperienceAnalyzer + SeniorityAnalyzer + IndustryAnalyzer into one comprehensive prompt
"""

UNIFIED_EXPERIENCE_FIT_PROMPT = """You are an expert hiring manager with 15+ years of experience evaluating candidate fit.

## CANDIDATE CV
{cv_text}

## JOB DESCRIPTION
{jd_text}

---

## YOUR TASK: Evaluate Experience Level, Seniority Match, and Industry Fit
You must score 5 specific metrics with supporting evidence. Use the scoring rubrics provided.

### METRIC 1: EXPERIENCE ALIGNMENT (0-100)
**What to evaluate:** Do they have the right TYPE and AMOUNT of experience?
**STEP 1: Count Years of Experience**
Use these conversion rates for different experience types:
- Corporate full-time roles = Full years counted (1.0x)
- Corporate internships = Half credit (0.5x)
- Consulting/contract work = 70% credit (0.7x)
- PhD/academic research = 30% credit (0.3x) - technical background, not professional experience
- Teaching/academic administration = 0% credit (not relevant to industry roles)
- Personal projects = 0% credit (not professional experience)
Calculate: Total weighted years = (corp_years × 1.0) + (intern_years × 0.5) + (consulting_years × 0.7) + (academic_years × 0.3)
**STEP 2: Compare to JD Requirements**
Extract years required from JD (e.g., "5+ years experience", "3-5 years", etc.)
Score based on match:
- CV years = JD years ±1 → Score: 90-100 (perfect match)
- CV years = JD years ±2 → Score: 75-89 (good match)
- CV years = JD years -3 or more → Score: 50-74 (underqualified)
- CV years = JD years +5 or more → Score: 40-60 (overqualification risk)
**Required Fields:**
- cv_corporate_years: Float (pure corporate/industry years)
- cv_academic_years: Float (academic/research years)
- jd_required_years: Float (extracted from JD)
- calculation: String explaining your math
---

### METRIC 2: ROLE SIMILARITY (0-100)
**What to evaluate:** Have they done THIS TYPE of work before?
**Scoring Rubric:**
- 85-100: Same role + same industry (Senior Backend Engineer → Senior Backend Engineer in SaaS)
- 70-84: Same role + different industry (Backend Engineer retail → Backend Engineer fintech)
- 55-69: Similar role + similar industry (Backend Engineer → Full Stack Engineer)
- 40-54: Related role (Backend Engineer → DevOps Engineer, adjacent skills)
- 0-39: Different role (Backend Engineer → Product Manager, fundamentally different)
**Reasoning Required:** Explain role comparison in 2-3 sentences
---

### METRIC 3: SENIORITY MATCH (0-100)
**What to evaluate:** Are they at the RIGHT LEVEL for this job?
**STEP 1: Determine CV Seniority Level (based on CORPORATE experience only)**
Seniority Levels:
- Entry (0-2 corp years): Individual contributor, learning phase, executes tasks
- Mid (3-5 corp years + some leadership): Owns features/projects, mentors juniors
- Senior (6-10 corp years + team management): Leads teams, makes architectural decisions, manages stakeholders
- Executive (10+ corp years + P&L/strategic): Owns business units, strategic decisions, executive stakeholder management
**STEP 2: Extract JD Seniority Requirements**
Look for indicators:
- Years required
- Team size to manage
- Scope of responsibility
- Decision-making authority
- Stakeholder level
**STEP 3: Score the Match**
- CV level exactly matches JD level → 90-100 (ideal fit)
- CV one level below JD → 60-75 (growth opportunity, manageable with training)
- CV one level above JD → 50-65 (overqualification risk - might leave)
- CV two+ levels different → 0-49 (significant mismatch)
**Required Fields:**
- cv_level: String ("Entry", "Mid", "Senior", or "Executive")
- jd_level: String ("Entry", "Mid", "Senior", or "Executive")
- evidence: List of 2-3 quotes from CV showing seniority level
---

### METRIC 4: LEADERSHIP READINESS (0-100)
**What to evaluate:** If the role requires leadership, can they deliver?
**Look for (CORPORATE experience only, academic supervision doesn't count):**
- Managed teams (how many direct reports?)
- Mentored engineers
- Made hiring decisions
- Owned technical roadmaps
- Led cross-functional initiatives
- Managed stakeholders (clients, executives, etc.)
**Scoring Based on JD Needs:**
- JD requires leadership + CV has strong evidence → 85-100
- JD requires leadership + CV has some evidence → 60-84
- JD requires leadership + CV has minimal/no evidence → 0-40
- JD doesn't require leadership → 70 (baseline - not critical)
**Required Fields:**
- evidence: List of 2-3 leadership examples from CV
- gaps: List of 1-2 leadership gaps compared to JD
---

### METRIC 5: INDUSTRY & TRANSITION FIT (0-100)
**What to evaluate:** Can they successfully transition into THIS industry?
**STEP 1: Identify Industries**
- CV Primary Industry: Extract from work experience (e.g., E-commerce, Fintech, Healthcare)
- JD Target Industry: Extract from job description
**STEP 2: Apply Transition Matrix**
Industry transition scoring:
- Same industry, same role → 90-100 (perfect fit, hiring manager's dream)
- Same industry, adjacent role → 75-89 (internal mobility, low risk)
- Related industry, same role → 65-80 (manageable transition, similar problems)
- Different industry, corporate background → 50-69 (moderate risk, needs adaptation)
- Academic background → any corporate industry → 30-50 (high risk, major adaptation needed)
**STEP 3: Apply Industry-Specific Penalties**
Subtract points for:
- Regulated industry (Finance, Healthcare, Pharma) without compliance experience: -15 points
- Client-facing role without client management experience: -15 points
- Fast-paced environment (Startup, high-growth) from slow-paced (academia, big corp): -10 points
- B2B complex sales without enterprise experience: -10 points
**STEP 4: Determine Risk Level**
- Score 80-100: LOW RISK - High success probability
- Score 60-79: MEDIUM RISK - Needs onboarding support
- Score 40-59: HIGH RISK - Significant adaptation required
- Score 0-39: VERY HIGH RISK - Major transition challenges
**Required Fields:**
- cv_industry: String (primary industry from CV)
- jd_industry: String (target industry from JD)
- transition_type: String (e.g., "Same industry, same role")
- risk_level: String ("LOW RISK", "MEDIUM RISK", "HIGH RISK", or "VERY HIGH RISK")
- reasoning: String (2-3 sentences explaining industry fit assessment)
---

## OUTPUT FORMAT
Return ONLY valid JSON (no markdown, no preamble, no explanation):
{
  "experience_alignment": {
    "score": 85,
    "cv_corporate_years": 5.0,
    "cv_academic_years": 3.0,
    "jd_required_years": 5.0,
    "calculation": "Corporate: 5 years full-time at TechCorp + 1 year at Startup = 6 years. Academic: 3 years PhD research × 0.3 = 0.9 years equivalent. Total weighted: 6.9 years. JD requires 5+ years. Score: 85 (exceeds requirement slightly)"
  },
  "role_similarity": {
    "score": 90,
    "reasoning": "CV shows Senior Backend Engineer role for 5 years building payment systems and APIs. JD seeks Senior Backend Engineer for payment platform. Exact role match with highly relevant domain experience (payment systems). Both roles involve microservices, APIs, and high-transaction systems."
  },
  "seniority_match": {
    "score": 90,
    "cv_level": "Senior",
    "jd_level": "Senior",
    "evidence": [
      "Led team of 4 backend engineers at TechCorp",
      "Owned technical roadmap for payment processing system",
      "Managed stakeholder relationships with product and finance teams"
    ]
  },
  "leadership_readiness": {
    "score": 80,
    "evidence": [
      "Managed team of 4 engineers with hiring and performance review responsibilities",
      "Mentored 5 junior developers, 2 promoted to mid-level",
      "Led cross-functional project involving engineering, product, and design teams"
    ],
    "gaps": [
      "No mention of managing multiple teams or senior leadership responsibilities",
      "Limited evidence of executive stakeholder management (mostly product/engineering level)"
    ]
  },
  "industry_transition_fit": {
    "score": 75,
    "cv_industry": "E-commerce",
    "jd_industry": "Fintech",
    "transition_type": "Related industry, same role",
    "risk_level": "MEDIUM RISK",
    "reasoning": "Both e-commerce and fintech are transaction-heavy domains requiring high reliability, security, and scale. Payment processing experience from e-commerce directly transfers to fintech. However, fintech has stricter regulatory requirements (PCI-DSS, financial regulations) which aren't evident in CV. Needs compliance training but technical skills are highly transferable."
  }
}

## CRITICAL RULES:
1. ALL scores must be integers 0-100
2. Count ONLY corporate experience as professional experience (academic = background knowledge)
3. PhD/research time counts as 0.3x professional years MAX (technical depth, not business experience)
4. Academic supervision ≠ business management (don't credit as leadership)
5. Be realistic about industry transitions (academic→corporate is HIGH RISK)
6. Use evidence from CV only (don't invent experience)
7. List gaps honestly (makes analysis valuable)

## SCORING CALIBRATION GUIDE:
- If candidate has exact corporate years + same role + same industry → Experience should be 85+
- If candidate transitions from academia → Corporate → Cap experience at 70 MAX (even with perfect technical fit)
- Only use scores above 90 for perfect matches (same industry, same role, exact years)
- Use scores 30-50 for academic→corporate transitions (be realistic about risk)
"""


