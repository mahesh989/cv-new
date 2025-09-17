# Frontend Analysis API Integration Guide

## Overview

This guide describes how to integrate the complete analysis results (Skills Analysis, Component Analysis, and ATS Score) into the frontend UI.

## API Endpoints

### 1. List Companies with Analysis Results

**Endpoint:** `GET /api/analysis-results`

**Description:** Get a list of all companies that have analysis results available.

**Response:**
```json
{
  "success": true,
  "companies": [
    {
      "name": "Company_Name",
      "analyses_available": {
        "skills": true,
        "preextracted_comparison": true,
        "component_analysis": true,
        "ats_calculation": true
      },
      "ats_score": 85.5,
      "last_modified": 1699891234.567
    }
  ],
  "total": 5
}
```

### 2. Get Complete Analysis Results for a Company

**Endpoint:** `GET /api/analysis-results/{company}`

**Description:** Get all analysis results for a specific company.

**Response:**
```json
{
  "success": true,
  "data": {
    "company": "Company_Name",
    "skills_analysis": {
      "cv_skills": {
        "technical_skills": ["Python", "React", "AWS"],
        "soft_skills": ["Leadership", "Communication"],
        "domain_keywords": ["Machine Learning", "Data Science"]
      },
      "jd_skills": {
        "technical_skills": ["Python", "JavaScript", "Cloud"],
        "soft_skills": ["Team Leadership", "Communication"],
        "domain_keywords": ["AI", "Analytics"]
      }
    },
    "preextracted_comparison": {
      "timestamp": "2025-09-13T06:00:00.123",
      "model_used": "gpt-4",
      "raw_content": "...",
      "match_rates": {
        "technical_skills": 85,
        "soft_skills": 90,
        "domain_keywords": 75,
        "overall": 83
      }
    },
    "component_analysis": {
      "timestamp": "2025-09-13T06:01:00.123",
      "extracted_scores": {
        "skills_relevance": 85.5,
        "experience_alignment": 90.0,
        "industry_fit": 75.0,
        "role_seniority": 85.0,
        "technical_depth": 88.0
      },
      "component_details": {
        "skills": { /* Detailed skills analysis */ },
        "experience": { /* Detailed experience analysis */ },
        "industry": { /* Detailed industry fit analysis */ },
        "seniority": { /* Detailed seniority analysis */ },
        "technical": { /* Detailed technical analysis */ }
      }
    },
    "ats_score": {
      "timestamp": "2025-09-13T06:02:00.123",
      "final_ats_score": 87.5,
      "category_status": "🌟 Strong Match",
      "recommendation": "Your profile shows strong alignment...",
      "breakdown": {
        "category1": {
          "score": 32.5,
          "technical_skills_match_rate": 85,
          "domain_keywords_match_rate": 75,
          "soft_skills_match_rate": 90,
          "missing_counts": {
            "technical": 2,
            "domain": 3,
            "soft": 1
          }
        },
        "category2": {
          "score": 48.0,
          "core_competency_avg": 82.5,
          "experience_seniority_avg": 87.5,
          "potential_ability_avg": 78.0,
          "company_fit_avg": 75.0
        },
        "ats1_score": 80.5,
        "bonus_points": 7.0
      }
    }
  }
}
```

## Frontend Display Components

### 1. Company List View

Display a list of companies with:
- Company name
- ATS score (if available) with color coding:
  - 🌟 85-100: Green (Strong Match)
  - ✅ 70-84: Blue (Good Match)
  - ⚡ 50-69: Orange (Moderate Match)
  - ❌ 0-49: Red (Poor Match)
- Analysis completion status (checkmarks for each completed analysis)
- Last analysis date

### 2. Detailed Analysis View

When a company is selected, display:

#### A. Skills Match Summary
- Show match rates as progress bars
- Technical Skills: X%
- Soft Skills: Y%
- Domain Keywords: Z%
- Overall Match: Avg%

#### B. Component Analysis Radar Chart
Display the 5 component scores in a radar/spider chart:
- Skills Relevance
- Experience Alignment
- Industry Fit
- Role Seniority
- Technical Depth

#### C. ATS Score Dashboard
- Large circular progress indicator showing final ATS score
- Category status with emoji and color
- Recommendation text
- Breakdown details in expandable sections

#### D. Detailed Breakdowns (Expandable Sections)
1. **Skills Analysis**
   - CV skills vs JD requirements side-by-side
   - Matched items highlighted in green
   - Missing items highlighted in red

2. **Component Details**
   - Each component with its sub-scores
   - Key findings and insights
   - Specific gaps and strengths

3. **ATS Score Breakdown**
   - Category 1: Direct Match (40 points max)
   - Category 2: Component Analysis (60 points max)
   - Bonus Points
   - Visual representation of score composition

## Sample Frontend Code Structure

```javascript
// API Service
class AnalysisService {
  async getCompanies() {
    const response = await fetch('/api/analysis-results');
    return response.json();
  }

  async getCompanyAnalysis(companyName) {
    const response = await fetch(`/api/analysis-results/${companyName}`);
    return response.json();
  }
}

// Component Example
function ATSScoreDisplay({ atsScore }) {
  const getScoreColor = (score) => {
    if (score >= 85) return '#4CAF50'; // Green
    if (score >= 70) return '#2196F3'; // Blue
    if (score >= 50) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  return (
    <div className="ats-score-container">
      <CircularProgress 
        value={atsScore.final_ats_score} 
        color={getScoreColor(atsScore.final_ats_score)}
      />
      <h2>{atsScore.final_ats_score.toFixed(1)}/100</h2>
      <p className="status">{atsScore.category_status}</p>
      <p className="recommendation">{atsScore.recommendation}</p>
    </div>
  );
}
```

## Implementation Steps

1. **Create API Service**: Set up API calls to fetch analysis data
2. **Build Company List**: Display available analyses with ATS scores
3. **Create Detail View**: Show comprehensive analysis results
4. **Add Visualizations**: Implement charts for better data representation
5. **Handle Loading States**: Show appropriate loading indicators
6. **Error Handling**: Display user-friendly error messages

## Best Practices

1. **Cache Results**: Store fetched results to avoid repeated API calls
2. **Progressive Loading**: Load summary first, details on demand
3. **Responsive Design**: Ensure mobile-friendly display
4. **Export Options**: Allow users to download/print analysis reports
5. **Comparison View**: Enable side-by-side comparison of multiple analyses

## Color Scheme Suggestions

- **Excellent (90-100)**: #1B5E20 (Dark Green)
- **Strong (80-89)**: #4CAF50 (Green)
- **Good (70-79)**: #2196F3 (Blue)
- **Moderate (60-69)**: #FF9800 (Orange)
- **Fair (50-59)**: #FF5722 (Deep Orange)
- **Poor (0-49)**: #F44336 (Red)

---

*Last Updated: September 13, 2025*
*API Version: 1.0*
