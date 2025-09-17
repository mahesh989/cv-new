# CV-JD Analysis Inconsistencies Report

## Major Conflicts Identified

### 1. **Experience Years Conflict**
- **CV Skills Section**: States "over 2 years of hands-on experience in analytics"
- **Component Analysis**: Shows `cv_experience_years: 2` vs `jd_required_years: "3-5 years"`
- **But JD Analysis**: No explicit 3-5 years requirement found in the job description text
- **Issue**: The system is inferring experience requirements that aren't explicitly stated

### 2. **Role Level Inconsistency**
- **Component Analysis**: 
  - CV: "Entry-Level" 
  - JD: "Mid-Senior"
- **Reality Check**: Job description asks for "A highly motivated, organised and detail-oriented Data Analyst" - doesn't specify seniority level
- **Issue**: System is making assumptions about role level without clear evidence

### 3. **Technical Skills Matching Conflicts**

#### Skills Count Discrepancy:
- **Preextracted Comparison**: 
  - Technical Skills: CV=13, JD=13, Matched=7, Missing=6 (54% match)
- **Component Analysis**: 
  - `technical_stack_fit_percentage: 80%`
  - `core_skills_match_percentage: 85%`
- **Issue**: Different components giving different match percentages

#### VBA Experience Gap:
- **Missing in CV**: VBA (identified correctly)
- **But**: CV shows "Excel" experience and the analysis doesn't consider that many Excel users can learn VBA
- **Gap**: Not assessing transferable/learnable skills properly

### 4. **Soft Skills Assessment Issues**

#### Match Count Problems:
- **Summary Table**: Shows 6 matched soft skills out of 14 JD requirements (43%)
- **Component Analysis**: Shows higher alignment scores (70-88%)
- **Conflict**: Numbers don't align with percentages

#### Missing Context:
- **CV Evidence**: "Strong ability to manage and prioritise multiple tasks" 
- **JD Requirement**: "Organised" and "Project Management"
- **Issue**: System not recognizing semantic equivalence

### 5. **Domain Keywords Misalignment**

#### Business Intelligence Gap:
- **Missing**: "Business Intelligence" from CV
- **But CV Has**: "Data Science", "Analytics", "Data Visualization" 
- **Reality**: These are closely related domains
- **Issue**: Too narrow domain matching

#### Industry Context Missing:
- **CV Focus**: Technical/Academic projects (Heart Attack Prediction, Corrosion Detection)
- **JD Focus**: Fundraising, Direct Marketing, Non-profit
- **Analysis**: Shows 70% industry fit, but doesn't address the significant domain shift
- **Issue**: Overestimating industry transferability

### 6. **Scoring Inconsistencies**

#### Overall Scores Conflict:
- **Analyze Match**: 60-70% interview chance
- **Component Scores**: Range from 60-95% across different areas
- **Preextracted**: 43% overall match rate
- **Issue**: Different modules producing conflicting assessments

## Recommended Fixes

### 1. **Standardize Experience Assessment**
```python
# Fix experience requirements extraction
if "years" not in jd_text.lower():
    inferred_years = "Not specified"
else:
    # Extract actual years mentioned
    inferred_years = extract_years_from_text(jd_text)
```

### 2. **Improve Skills Matching Logic**
```python
# Add semantic similarity for related skills
SKILL_EQUIVALENTS = {
    "organised": ["time management", "task prioritization"],
    "business intelligence": ["data science", "analytics", "data visualization"],
    "project management": ["task management", "multiple projects"]
}
```

### 3. **Consistent Scoring Framework**
```python
# Weighted scoring system
final_score = (
    technical_match * 0.4 +
    soft_skills_match * 0.3 +
    experience_fit * 0.2 +
    industry_alignment * 0.1
)
```

### 4. **Context-Aware Gap Analysis**
- Distinguish between "hard gaps" (missing critical skills) vs "soft gaps" (learnable skills)
- Consider industry transferability more realistically
- Account for role flexibility in non-profit sector

### 5. **Unified Output Structure**
All analysis components should use the same:
- Skill categorization
- Scoring scale (0-100)
- Match criteria
- Evidence weighting

## Impact Assessment

**Current Issues:**
- Candidate might receive conflicting feedback
- Different parts of the system give different recommendations
- Scoring inconsistencies could affect ranking
- Missing nuanced assessment of transferable skills

**Proposed Solutions:**
- Implement unified scoring framework
- Add semantic skill matching
- Improve context awareness
- Standardize experience requirement extraction
- Add confidence levels to assessments
