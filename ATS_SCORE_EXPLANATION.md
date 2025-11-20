# ATS Score Calculation & Display Explanation

## 📊 How ATS Score is Calculated

The ATS (Applicant Tracking System) score is calculated using a **100-point framework** with a **65/35 split** (v2 scoring method):

### Formula Overview

```
Final ATS Score = Base Score + Boost + Bonus Points
                 = (Category 1 + Category 2) + Boost + Bonus
                 = (65 points max) + (35 points max) + (up to 10 points) + (up to 5 points)
                 = Maximum 100 points (capped at 100)
```

### Category 1: Keyword Matching (65 points maximum)

This category measures direct keyword matches between CV and Job Description:

1. **Technical Skills** (40 points max)
   - Formula: `(Technical Skills Match Rate / 100) × 40`
   - Example: If 75% of technical skills match → `0.75 × 40 = 30 points`

2. **Domain Keywords** (10 points max)
   - Formula: `(Domain Keywords Match Rate / 100) × 10`
   - Example: If 80% of domain keywords match → `0.80 × 10 = 8 points`

3. **Soft Skills** (15 points max)
   - Formula: `(Soft Skills Match Rate / 100) × 15`
   - Example: If 60% of soft skills match → `0.60 × 15 = 9 points`

**Category 1 Total**: 30 + 8 + 9 = **47 points**

### Category 2: AI Component Analysis (35 points maximum)

This category uses AI analysis to evaluate deeper aspects:

1. **Technical & Skills Component** (22 points max)
   - Averages 4 metrics: `technical_depth`, `required_skills_coverage`, `tech_stack_similarity`, `business_readiness`
   - Formula: `(Average of 4 metrics / 100) × 22`
   - Example: If average is 70% → `0.70 × 22 = 15.4 points`

2. **Experience & Fit Component** (13 points max)
   - Averages 4 metrics: `experience_alignment`, `role_similarity`, `seniority_match`, `industry_transition_fit`
   - Formula: `(Average of 4 metrics / 100) × 13`
   - Example: If average is 65% → `0.65 × 13 = 8.45 points`

**Category 2 Total**: 15.4 + 8.45 = **23.85 points**

### Boost Points (Automatic)

Boost is automatically applied based on technical skills match rate:
- **+5 points** if technical skills match rate ≥ 85%
- **+3 points** if technical skills match rate ≥ 75%
- **+0 points** otherwise

### Bonus Points (Up to 10 points)

Additional points awarded for exceptional matches or deducted for critical gaps.

### Final Calculation Example

Let's calculate a complete example:

**Input Data:**
- Technical Skills Match Rate: 75%
- Domain Keywords Match Rate: 80%
- Soft Skills Match Rate: 60%
- Technical & Skills Component Average: 70%
- Experience & Fit Component Average: 65%
- Bonus Points: 2.0

**Step-by-Step Calculation:**

1. **Category 1 (Keyword Matching):**
   - Technical: `(75/100) × 40 = 30.0 points`
   - Domain: `(80/100) × 10 = 8.0 points`
   - Soft: `(60/100) × 15 = 9.0 points`
   - **Category 1 Total: 47.0 points**

2. **Category 2 (AI Analysis):**
   - Technical & Skills: `(70/100) × 22 = 15.4 points`
   - Experience & Fit: `(65/100) × 13 = 8.45 points`
   - **Category 2 Total: 23.85 points**

3. **Base Score:** 47.0 + 23.85 = **70.85 points**

4. **Boost:** Since technical match rate is 75% (≥75%), apply **+3.0 points**

5. **Bonus Points:** **+2.0 points**

6. **Final ATS Score:** 70.85 + 3.0 + 2.0 = **75.85/100**

**Status:** ✅ Good fit (score ≥ 75)
**Recommendation:** "Worth an interview - Good potential match"

---

## 🎨 How It's Displayed in the Frontend

The ATS score is displayed using the `ATSScoreWidgetWithProgressBars` widget. Here's what users see:

### 1. Main Score Display
```
┌─────────────────────────────────┐
│   ATS Score Analysis            │
│                                 │
│   ┌───────────────────────┐   │
│   │   75.8/100            │   │  ← Large, color-coded score
│   └───────────────────────┘   │
│                                 │
│   [✅ Good fit]                 │  ← Status badge
│   Worth an interview - Good     │  ← Recommendation text
│   potential match               │
└─────────────────────────────────┘
```

### 2. Category 1 Breakdown (Keyword Matching)
```
┌─────────────────────────────────┐
│ 📊 Category 1: Keyword Matching │
│                                 │
│ Technical Skills                │
│ ████████████████░░░░  30.0/40  │  ← Progress bar
│ 75.0%                           │
│                                 │
│ Domain Keywords                 │
│ ████████████░░░░░░░░  8.0/10   │
│ 80.0%                           │
│                                 │
│ Soft Skills                      │
│ █████████░░░░░░░░░░  9.0/15   │
│ 60.0%                           │
│                                 │
│ Total: 47.0/65                 │
└─────────────────────────────────┘
```

### 3. Category 2 Breakdown (AI Analysis)
```
┌─────────────────────────────────┐
│ 📊 Category 2: AI Component     │
│    Analysis                      │
│                                 │
│ Technical & Skills Component     │
│ ████████████████░░░░  15.4/22  │
│ 70.0%                           │
│                                 │
│ Experience & Fit Component       │
│ ████████████░░░░░░░░  8.45/13  │
│ 65.0%                           │
│                                 │
│ Total: 23.85/35                │
└─────────────────────────────────┘
```

### 4. Bonus & Boost Section
```
┌─────────────────────────────────┐
│ ⚡ Boost Applied                │
│ +3.0                            │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 📈 Bonus Points                 │
│ +2.0                            │
│ Bonus points awarded for        │
│ exceptional keyword matches     │
└─────────────────────────────────┘
```

### 5. Final Score Summary
```
┌─────────────────────────────────┐
│ 📊 Final ATS Score              │
│ Base (70.9) + Boost (+3.0) +    │
│ Bonus (+2.0)                    │
│                      [75.8]     │  ← Final score in badge
└─────────────────────────────────┘
```

### Color Coding

The score is color-coded based on value:
- **Green** (≥80): Excellent fit
- **Orange** (60-79): Good to moderate fit
- **Red** (<60): Poor fit

### Visual Features

1. **Progress Bars**: Visual representation of each component's contribution
2. **Percentage Display**: Shows match rates for each category
3. **Color-Coded Badges**: Quick visual feedback on score quality
4. **Detailed Breakdown**: Users can see exactly how the score was calculated
5. **Status & Recommendation**: Clear guidance on what the score means

---

## 📝 Code Location

- **Backend Calculation**: `backend/app/services/ats/ats_score_calculator.py`
  - Method: `calculate_ats_score_v2()` (lines 334-436)
  
- **Frontend Display**: `mobile_app/lib/widgets/ats_score_widget_with_progress_bars.dart`
  - Widget: `ATSScoreWidgetWithProgressBars`

---

## 🔍 Key Metrics Explained

| Metric | Description | Impact |
|--------|-------------|--------|
| **Technical Skills Match Rate** | % of required technical skills found in CV | High (40 points) |
| **Domain Keywords Match Rate** | % of industry/domain keywords matched | Medium (10 points) |
| **Soft Skills Match Rate** | % of required soft skills found | Medium (15 points) |
| **Technical Depth** | AI assessment of technical expertise depth | Medium (part of 22 points) |
| **Experience Alignment** | How well CV experience matches JD requirements | Medium (part of 13 points) |
| **Boost** | Automatic bonus for high technical match | Bonus (up to 5 points) |
| **Bonus Points** | Manual/additional adjustments | Variable (up to 10 points) |

---

## 💡 Example Scenario

**Job Description Requirements:**
- Technical: Python, React, AWS, Docker (4 skills)
- Domain: FinTech, Banking, Payments (3 keywords)
- Soft: Leadership, Communication, Problem-solving (3 skills)

**Candidate's CV:**
- Technical: Python, React, AWS (3/4 = 75% match)
- Domain: FinTech, Banking (2/3 = 67% match)
- Soft: Leadership, Communication (2/3 = 67% match)

**Calculation:**
- Category 1: (75%×40) + (67%×10) + (67%×15) = 30 + 6.7 + 10 = **46.7 points**
- Category 2: (assume 70% avg) = 15.4 + 8.45 = **23.85 points**
- Base: 46.7 + 23.85 = **70.55 points**
- Boost: +3 (75% technical match) = **73.55 points**
- Final: **73.6/100** → ✅ Good fit

This gives the candidate a clear understanding of their match quality and areas for improvement!

