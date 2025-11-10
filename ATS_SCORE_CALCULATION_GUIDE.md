# ATS Score Calculation Guide

## Overview

The ATS (Applicant Tracking System) score is calculated using a **structured 100-point framework** that evaluates CV-Job Description alignment across multiple dimensions. The system uses AI-powered component analysis combined with mathematical scoring algorithms.

---

## Score Structure (100 Points Total)

### **Category 1: Direct Match Rates (40 points)**
- **Technical Skills Match**: 20 points max
- **Domain Keywords Match**: 5 points max  
- **Soft Skills Match**: 15 points max

### **Category 2: Component Analysis (60 points)**
- **Core Competency**: 25 points max
- **Experience & Seniority**: 20 points max
- **Potential & Ability**: 10 points max
- **Company Fit**: 5 points max

### **Category 3: Bonus Points**
- **Requirement Bonus**: Up to additional points (capped at 100 total)

---

## Calculation Formula

### Step 1: Category 1 - Direct Match Rates (40 points)

```python
# Technical Skills (20 points)
tech_points = (tech_match_rate / 100) * 20

# Domain Keywords (5 points)
domain_points = (domain_match_rate / 100) * 5

# Soft Skills (15 points)
soft_points = (soft_match_rate / 100) * 15

cat1_score = tech_points + domain_points + soft_points
```

**Match rates are extracted from preextracted comparison data** that compares CV skills against JD requirements.

### Step 2: Category 2 - Component Analysis (60 points)

#### 2.1 Core Competency (25 points)
Averages 4 metrics:
- `technical_depth` (0-100)
- `core_skills_match_percentage` (0-100)
- `technical_stack_fit_percentage` (0-100)
- `data_familiarity_score` (0-100)

```python
core_avg = (technical_depth + core_skills_match + technical_stack_fit + data_familiarity) / 4
core_points = (core_avg / 100) * 25
```

#### 2.2 Experience & Seniority (20 points)
Averages 5 metrics:
- `experience_alignment` (0-100)
- `experience_match_percentage` (0-100)
- `responsibility_fit_percentage` (0-100)
- `role_seniority` (0-100)
- `leadership_readiness_score` (0-100)

```python
exp_avg = (experience_alignment + experience_match + responsibility_fit + role_seniority + leadership_readiness) / 5
exp_points = (exp_avg / 100) * 20
```

#### 2.3 Potential & Ability (10 points)
Averages 4 metrics:
- `growth_trajectory_score` (0-100)
- `complexity_readiness_score` (0-100)
- `learning_agility_score` (0-100)
- `jd_problem_complexity` (normalized 0-100)

```python
complexity_normalized = (jd_problem_complexity / 10) * 100  # Normalize from 0-10 scale
potential_avg = (growth_trajectory + complexity_readiness + learning_agility + complexity_normalized) / 4
potential_points = (potential_avg / 100) * 10
```

#### 2.4 Company Fit (5 points)
Averages 4 metrics:
- `industry_fit` (0-100)
- `domain_overlap_percentage` (0-100)
- `stakeholder_fit_score` (0-100)
- `business_cycle_alignment` (0-100)

```python
company_avg = (industry_fit + domain_overlap + stakeholder_fit + business_cycle_alignment) / 4
company_points = (company_avg / 100) * 5
```

```python
cat2_score = core_points + exp_points + potential_points + company_points
```

### Step 3: Final Score Calculation

```python
# Pre-bonus score
ats1_score = cat1_score + cat2_score

# Add bonus points (if any)
bonus_points = extracted_scores.get("requirement_bonus", 0)

# Final score (capped at 100)
final_ats_score = min(100.0, ats1_score + bonus_points)
```

---

## Score Interpretation

| Score Range | Status | Recommendation |
|------------|--------|----------------|
| **90-100** | ✅ Excellent fit | Strong candidate |
| **75-89** | ✅ Good fit | Worth an interview |
| **60-74** | ⚠️ Moderate fit | Consider if other factors are strong |
| **0-59** | ❌ Poor fit | Generally rejected |

---

## Component Analysis Prompts

The system uses **5 specialized AI prompts** to analyze different aspects of the CV-JD match. Each prompt is designed to evaluate specific dimensions with **corporate/business context prioritization**.

### 1. Technical Depth Analysis Prompt
**File**: `prompt/ats_technical_prompt.py`

**Purpose**: Analyzes technical sophistication and depth

**Key Metrics Extracted**:
- `technical_depth_score` (0-100)
- `core_skills_match_percentage` (0-100)
- `technical_stack_fit_percentage` (0-100)
- `complexity_readiness_score` (0-100)
- `learning_agility_score` (0-100)
- `jd_problem_complexity` (0-10 scale)

**Scoring Guidelines**:
- 90-100: Excellent match, minimal gaps
- 75-89: Strong fit, minor development needed
- 60-74: Good fit, moderate gaps manageable
- 40-59: Some alignment, significant development required
- 25-39: Limited fit, major gaps present
- 0-24: Poor match, substantial mismatch

**Prompt Template**:
```python
TECHNICAL_DEPTH_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze technical sophistication and depth.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## TECHNICAL DEPTH ANALYSIS
Analyze technical sophistication and depth. Extract and analyze:
1. Sophistication level
2. Core competency depth
3. Problem complexity handled
4. Innovation contributions
5. Technical leadership activities

Return JSON only:
{
 "technical_analysis": {
   "technical_depth_score": 90,
   "core_skills_match_percentage": 85,
   "technical_stack_fit_percentage": 80,
   ...
 }
}
"""
```

---

### 2. Skills Relevance Analysis Prompt
**File**: `prompt/ats_skills_relevance_prompt.py`

**Purpose**: Analyzes skills relevance with **corporate application priority**

**Key Features**:
- **Corporate vs Academic Weighting**:
  - Corporate/Industry Application = 1.0x (full credit)
  - Commercial Project Usage = 0.9x
  - Consulting/Client Work = 0.8x
  - Academic Research Usage = 0.4x (limited business relevance)
  - Course/Certification Only = 0.2x (theoretical knowledge)
  - Personal Projects = 0.3x (no business pressure)

**Business Context Bonuses**:
- Revenue generation applications: +20 points
- Cost reduction implementations: +20 points
- Client delivery usage: +20 points
- Cross-functional collaboration: +20 points
- Regulatory compliance applications: +20 points

**Penalty Factors**:
- Only academic usage: -10 to -20 points
- No measurable outcomes: -10 to -20 points
- Theoretical knowledge only: -10 to -20 points

**Key Metrics Extracted**:
- `overall_skills_score` (0-100, weighted toward corporate application)
- `business_readiness_score` (0-100)
- Individual skill relevance scores

**Prompt Template**:
```python
SKILLS_RELEVANCE_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze skills relevance with REALISTIC assessment that heavily prioritizes corporate application over academic usage.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}
MATCHED SKILLS: {matched_skills}

## CRITICAL SKILLS INTERPRETATION RULES:

### Corporate vs Academic Skill Application (Weight Multipliers):
- **Corporate/Industry Application** = 1.0x skill value (full credit)
- **Academic Research Usage** = 0.4x skill value (limited business relevance)
- **Course/Certification Only** = 0.2x skill value (theoretical knowledge)

## SKILLS RELEVANCE ANALYSIS
Analyze skills relevance with CORPORATE APPLICATION PRIORITY.

Return JSON only:
{
 "skills_analysis": [...],
 "overall_skills_score": "[0-100 weighted toward corporate application]",
 "business_readiness_score": "[0-100 for immediate corporate application]",
 ...
}
"""
```

---

### 3. Experience Alignment Analysis Prompt
**File**: `prompt/ats_experience_prompt.py`

**Purpose**: Analyzes experience alignment with **corporate experience priority**

**Key Features**:
- **Corporate Experience Weighting (90% weight)**:
  - Full-time corporate roles = 1.0x (full value)
  - Internships at companies = 0.5x
  - Consulting projects = 0.6x
  - Freelance/contract work = 0.5x

- **Academic Experience Weighting (10% weight)**:
  - PhD research = 0.5-1 year equivalent maximum
  - Master's thesis = 0.25 year equivalent maximum
  - Academic leadership = Soft skills evidence only (no experience value)
  - Publications = Technical competency evidence only (no experience value)

**Key Metrics Extracted**:
- `alignment_score` (0-100, heavily weighted toward corporate experience)
- `cv_corporate_years` (pure corporate/industry experience)
- `cv_academic_years` (academic experience - treated as background only)
- `overqualification_risk` (LOW/MEDIUM/HIGH)

**Prompt Template**:
```python
EXPERIENCE_ALIGNMENT_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze experience alignment between CV and JD requirements with REALISTIC market interpretation that heavily favors corporate experience.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## CRITICAL CV INTERPRETATION RULES:

### Corporate/Industrial Experience (Primary Value - 90% weight):
- Full-time corporate roles = Full professional experience value (1.0x)
- Internships at companies = 0.5x experience value
- Academic experience = Technical knowledge background (not professional years)

## EXPERIENCE ALIGNMENT ANALYSIS
Analyze experience alignment between CV and JD requirements.

Return JSON only:
{
 "experience_analysis": {
   "cv_corporate_years": "[Pure corporate/industry experience only]",
   "cv_academic_years": "[Academic experience - treated as background only]",
   "alignment_score": "[0-100 overall score heavily weighted toward corporate experience]",
   "overqualification_risk": "[LOW/MEDIUM/HIGH assessment]"
 }
}
"""
```

---

### 4. Role Seniority Analysis Prompt
**File**: `prompt/ats_seniority_prompt.py`

**Purpose**: Analyzes role seniority fit with **strict data-driven interpretation**

**Key Features**:
- **STRICT DATA-ONLY RULES**:
  - ONLY analyze information EXPLICITLY stated in the CV
  - DO NOT make assumptions about experience not mentioned
  - DO NOT infer skills from job titles alone
  - DO NOT assume leadership experience unless explicitly stated

- **Corporate Seniority Assessment (80% weight)**:
  - Full-time corporate roles = Actual seniority level
  - Management experience in business = True leadership seniority
  - P&L responsibility = Senior executive capability
  - Client/stakeholder management = Business relationship seniority

- **Academic Experience Seniority (20% weight)**:
  - PhD research = Individual contributor level (NOT management level)
  - Research publications = Technical competency (NOT leadership seniority)
  - Academic supervision = Teaching capability (NOT business management)

**Corporate Seniority Levels**:
- **Entry Level**: 0-2 years corporate experience
- **Mid Level**: 3-5 years corporate experience with some leadership
- **Senior Level**: 6-10 years corporate experience with management responsibility
- **Executive Level**: 10+ years with P&L, strategic decision-making

**Key Metrics Extracted**:
- `seniority_score` (0-100)
- `corporate_seniority_match` (0-100 based on corporate experience)
- `leadership_readiness_score` (0-100 based on business management experience)
- `overqualification_risk` (LOW/MEDIUM/HIGH)

**Prompt Template**:
```python
ROLE_SENIORITY_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze role seniority fit with STRICT DATA-DRIVEN interpretation based ONLY on what is explicitly stated in the CV.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## CRITICAL CV INTERPRETATION RULES - STRICT DATA ONLY:

### MANDATORY ANALYSIS CONSTRAINTS:
- ONLY analyze information EXPLICITLY stated in the CV
- DO NOT make assumptions about experience not mentioned
- DO NOT infer skills from job titles alone

### Corporate Seniority Assessment (Primary - 80% weight):
- Full-time corporate roles = Actual seniority level
- Management experience in business = True leadership seniority

## ROLE SENIORITY ANALYSIS
Analyze role seniority fit focusing on corporate seniority indicators.

Return JSON only:
{
 "seniority_analysis": {
   "seniority_score": "[0-100 overall seniority alignment]",
   "corporate_seniority_match": "[0-100 based on corporate experience]",
   "leadership_readiness_score": "[0-100 based on business management experience]",
   ...
 }
}
"""
```

---

### 5. Industry Fit Analysis Prompt
**File**: `prompt/ats_industry_prompt.py`

**Purpose**: Analyzes industry background alignment with **realistic market expectations**

**Key Features**:
- **Industry Experience Priority**:
  - Same industry experience = GOLD STANDARD (90-100 score range)
  - Related industry with corporate experience = Strong (70-85 score range)
  - Different industry but corporate background = Moderate (50-70 score range)
  - Academic/Research to any industry = High risk (25-50 score range MAX)

**Industry Transition Realism Matrix**:
- Same Industry, Same Role: 85-100 (hiring manager's dream)
- Same Industry, Different Role: 75-90 (internal mobility preferred)
- Related Industry, Similar Role: 65-80 (manageable transition)
- Academic/Research → Corporate: 25-50 MAX (high failure risk)

**Penalty Factors**:
- Regulated Industries (Finance, Healthcare, Pharma): -20 points if no regulatory experience
- Client-Facing Industries (Consulting, Sales): -15 points if no client management
- Fast-Paced Industries (Tech, Startups): -15 points if only academic pace
- Revenue-Driven Industries: -20 points if no commercial experience

**Key Metrics Extracted**:
- `industry_alignment_score` (0-100 based on realistic transition matrix)
- `corporate_background_bonus` (0-20 points for corporate vs academic experience)
- `success_probability` (HIGH/MEDIUM/LOW based on transition factors)
- `hiring_risk_assessment` (LOW RISK/MEDIUM RISK/HIGH RISK/VERY HIGH RISK)

**Prompt Template**:
```python
INDUSTRY_FIT_PROMPT = """
You are an expert hiring manager with 15+ years of experience. Analyze industry background alignment with REALISTIC market expectations that heavily favor industry-specific experience.

CV TEXT: {cv_text}
JD REQUIREMENTS: {jd_text}

## CRITICAL INDUSTRY INTERPRETATION RULES:

### Industry Experience Priority (Corporate Reality):
- **Same industry experience = GOLD STANDARD** (90-100 score range)
- **Academic/Research to any industry** = High risk (25-50 score range MAX)

## INDUSTRY FIT ANALYSIS
Analyze industry background alignment with REALISTIC hiring manager expectations.

Return JSON only:
{
 "industry_analysis": {
   "industry_alignment_score": "[0-100 based on realistic transition matrix]",
   "corporate_background_bonus": "[0-20 points for corporate vs academic experience]",
   "success_probability": "[HIGH/MEDIUM/LOW based on transition factors]",
   ...
 }
}
"""
```

---

## Data Flow

### 1. Requirements Extraction
- **Component**: `CentralizedRequirementsExtractor`
- Extracts technical skills, soft skills, domain keywords, tools, platforms from JD

### 2. Skills Matching
- **Component**: `EnhancedSkillsMatcher`
- Matches CV skills against JD requirements
- Calculates match rates for technical, soft, and domain skills
- Generates preextracted comparison data with match rates

### 3. Component Analysis (Parallel Execution)
All 5 analyzers run in parallel:
- `TechnicalAnalyzer` → Uses `TECHNICAL_DEPTH_PROMPT`
- `SkillsRelevanceAnalyzer` → Uses `SKILLS_RELEVANCE_PROMPT`
- `ExperienceAnalyzer` → Uses `EXPERIENCE_ALIGNMENT_PROMPT`
- `SeniorityAnalyzer` → Uses `ROLE_SENIORITY_PROMPT`
- `IndustryAnalyzer` → Uses `INDUSTRY_FIT_PROMPT`

### 4. Score Extraction
- Extracts numerical scores from each component's JSON response
- Maps to standardized score dictionary

### 5. ATS Score Calculation
- **Component**: `ATSScoreCalculator`
- Calculates Category 1 (40 points) from match rates
- Calculates Category 2 (60 points) from extracted scores
- Adds bonus points (if any)
- Final score capped at 100

### 6. Results Assembly
- Combines all component analyses
- Generates insights (key strengths, critical gaps, recommendations)
- Saves to analysis file

---

## Key Design Principles

### 1. **Corporate/Business Context Priority**
- Corporate experience valued significantly higher than academic experience
- Business application of skills prioritized over theoretical knowledge
- Real-world business impact metrics preferred

### 2. **Strict Data-Driven Analysis**
- Only uses explicitly stated information from CV
- No assumptions or inferences
- Missing information scored accordingly (not assumed)

### 3. **Realistic Market Expectations**
- Reflects actual hiring manager preferences
- Industry-specific penalties and bonuses
- Transition risk assessment

### 4. **Comprehensive Multi-Dimensional Analysis**
- 5 specialized analyzers for different aspects
- Parallel execution for efficiency
- Structured scoring framework

---

## Example Calculation

### Input Data:
- Technical Skills Match Rate: 85%
- Domain Keywords Match Rate: 70%
- Soft Skills Match Rate: 90%
- Technical Depth: 80
- Core Skills Match: 85
- Technical Stack Fit: 75
- Data Familiarity: 70
- Experience Alignment: 75
- Experience Match: 80
- Responsibility Fit: 70
- Role Seniority: 85
- Leadership Readiness: 75
- Growth Trajectory: 80
- Complexity Readiness: 75
- Learning Agility: 85
- JD Problem Complexity: 7 (normalized to 70)
- Industry Fit: 80
- Domain Overlap: 75
- Stakeholder Fit: 70
- Business Cycle Alignment: 75
- Requirement Bonus: 0

### Calculation:

**Category 1 (40 points)**:
- Technical: (85/100) * 20 = 17.0
- Domain: (70/100) * 5 = 3.5
- Soft: (90/100) * 15 = 13.5
- **Cat1 Total: 34.0**

**Category 2 (60 points)**:
- Core Competency: ((80+85+75+70)/4)/100 * 25 = 19.375
- Experience & Seniority: ((75+80+70+85+75)/5)/100 * 20 = 15.0
- Potential & Ability: ((80+75+85+70)/4)/100 * 10 = 7.75
- Company Fit: ((80+75+70+75)/4)/100 * 5 = 3.75
- **Cat2 Total: 45.875**

**Final Score**:
- ATS1 (pre-bonus): 34.0 + 45.875 = 79.875
- Bonus: 0
- **Final ATS Score: 79.875/100** → **"✅ Good fit - Worth an interview"**

---

## Files Reference

### Core Calculation:
- `app/services/ats/ats_score_calculator.py` - Main scoring algorithm
- `app/services/ats/enhanced_ats_orchestrator.py` - Orchestration logic

### Component Analyzers:
- `app/services/ats/components/technical_analyzer.py`
- `app/services/ats/components/skills_relevance_analyzer.py`
- `app/services/ats/components/experience_analyzer.py`
- `app/services/ats/components/seniority_analyzer.py`
- `app/services/ats/components/industry_analyzer.py`

### Prompts:
- `prompt/ats_technical_prompt.py`
- `prompt/ats_skills_relevance_prompt.py`
- `prompt/ats_experience_prompt.py`
- `prompt/ats_seniority_prompt.py`
- `prompt/ats_industry_prompt.py`

### Assembly:
- `app/services/ats/component_assembler.py` - Assembles all components

---

## Summary

The ATS scoring system is a **sophisticated, multi-dimensional evaluation framework** that:

1. **Uses AI-powered component analysis** to evaluate 5 key dimensions
2. **Prioritizes corporate/business experience** over academic background
3. **Applies strict data-driven rules** to avoid over-inference
4. **Reflects realistic market expectations** for hiring decisions
5. **Provides comprehensive scoring** across 100 points with detailed breakdowns

The system is designed to give candidates and hiring managers a realistic, actionable assessment of CV-JD alignment.

