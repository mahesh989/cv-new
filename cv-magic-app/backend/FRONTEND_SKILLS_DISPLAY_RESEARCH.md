# Frontend Side-by-Side Skills Display - Research Report

## Overview

This document explains how CV and JD skills flow from the backend API response to the frontend side-by-side display.

## Data Flow Architecture

```
Backend API Response
    ↓
InitialAnalysisResults.fromJson() (parses API response)
    ↓
SkillsComparisonCard widget (displays side-by-side)
```

## 1. Backend API Response Structure

**Endpoint**: `/api/initial-analysis`

**Response Structure**:
```json
{
  "success": true,
  "results": {
    "cv_skills": {
      "technical_skills": [...],
      "soft_skills": [...],
      "domain_keywords": [...]
    },
    "jd_skills": {
      "technical_skills": [...],
      "soft_skills": [...],
      "domain_keywords": [...]
    },
    "jd_analysis": { ... },
    "job_info": { ... },
    "cv_jd_matching": { ... }
  }
}
```

**Key Fields**:
- `results.cv_skills`: CV skills in 3-section format
- `results.jd_skills`: JD skills in 3-section format
- Both use the same structure: `technical_skills`, `soft_skills`, `domain_keywords`

## 2. Frontend Parsing

### File: `mobile_app/lib/services/context_aware_analysis_service.dart`

**Class**: `InitialAnalysisResults`

```dart
class InitialAnalysisResults {
  final Map<String, dynamic> cvSkills;
  final Map<String, dynamic> jdSkills;
  final Map<String, dynamic> jdAnalysis;
  final Map<String, dynamic> jobInfo;
  final Map<String, dynamic> cvJdMatching;

  factory InitialAnalysisResults.fromJson(Map<String, dynamic> json) {
    return InitialAnalysisResults(
      cvSkills: Map<String, dynamic>.from(json['cv_skills'] ?? {}),
      jdSkills: Map<String, dynamic>.from(json['jd_skills'] ?? {}),
      jdAnalysis: Map<String, dynamic>.from(json['jd_analysis'] ?? {}),
      jobInfo: Map<String, dynamic>.from(json['job_info'] ?? {}),
      cvJdMatching: Map<String, dynamic>.from(json['cv_jd_matching'] ?? {}),
    );
  }
}
```

**Key Points**:
- Directly extracts `cv_skills` and `jd_skills` from `results` object
- No transformation - passes through as `Map<String, dynamic>`
- Both have the same structure: `technical_skills`, `soft_skills`, `domain_keywords`

## 3. Controller Storage

### File: `mobile_app/lib/controllers/context_aware_analysis_controller.dart`

**Storage**:
```dart
InitialAnalysisResult? _initialAnalysisResult;
```

**Access**:
```dart
final results = _initialAnalysisResult!.results!;
// results.cvSkills and results.jdSkills are Map<String, dynamic>
```

## 4. Display Widget

### File: `mobile_app/lib/widgets/skills_comparison_card.dart`

**Widget**: `SkillsComparisonCard`

**Constructor**:
```dart
class SkillsComparisonCard extends StatelessWidget {
  final Map<String, dynamic> cvSkills;
  final Map<String, dynamic> jdSkills;
  
  const SkillsComparisonCard({
    required this.cvSkills,
    required this.jdSkills,
  });
}
```

**Data Extraction** (lines 17-30):
```dart
// Extract skills lists and sort alphabetically
final cvTechnical = List<String>.from(cvSkills['technical_skills'] ?? [])
  ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
final cvSoft = List<String>.from(cvSkills['soft_skills'] ?? [])
  ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
final cvDomain = List<String>.from(cvSkills['domain_keywords'] ?? [])
  ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));

final jdTechnical = List<String>.from(jdSkills['technical_skills'] ?? [])
  ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
final jdSoft = List<String>.from(jdSkills['soft_skills'] ?? [])
  ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
final jdDomain = List<String>.from(jdSkills['domain_keywords'] ?? [])
  ..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));
```

**Display Structure** (lines 68-98):
```dart
Row(
  children: [
    // CV Skills Column (Blue)
    Expanded(
      child: _buildSkillsColumn(
        title: 'Your CV Skills',
        technical: cvTechnical,
        soft: cvSoft,
        domain: cvDomain,
        color: Colors.blue,
      ),
    ),
    
    const SizedBox(width: 16),
    
    // JD Skills Column (Green)
    Expanded(
      child: _buildSkillsColumn(
        title: 'Job Requirements',
        technical: jdTechnical,
        soft: jdSoft,
        domain: jdDomain,
        color: Colors.green,
      ),
    ),
  ],
)
```

## 5. Usage in Screen

### File: `mobile_app/lib/screens/cv_magic_organized_page.dart`

**Location**: Lines 233-264

```dart
AnimatedBuilder(
  animation: _skillsController,
  builder: (context, _) {
    if (_skillsController.hasInitialResults && 
        _skillsController.initialResult?.results != null) {
      final results = _skillsController.initialResult!.results!;
      
      return Column(
        children: [
          SkillsComparisonCard(
            cvSkills: results.cvSkills,  // Map<String, dynamic>
            jdSkills: results.jdSkills,  // Map<String, dynamic>
          ),
        ],
      );
    }
    return const SizedBox.shrink();
  },
)
```

## 6. Expected Data Format

The frontend expects both `cvSkills` and `jdSkills` to have this exact structure:

```dart
{
  "technical_skills": ["SQL", "Power BI", "Excel", ...],
  "soft_skills": ["communication", "problem-solving", ...],
  "domain_keywords": ["fundraising", "nonprofit", ...]
}
```

**Field Names**:
- ✅ `technical_skills` (not `technical`)
- ✅ `soft_skills` (not `soft`)
- ✅ `domain_keywords` (not `domain_knowledge`)

## 7. Current Backend Implementation

### File: `app/services/context_aware_analysis_pipeline.py`

**JD Skills Population** (lines 1030-1054):
```python
# Summarize JD skills for downstream consumers
if not results.jd_skills and results.jd_analysis:
    # Prefer the JD analyzer's own three-section summary if available
    three_section = results.jd_analysis.get("three_section_skills") or {}
    tech_3 = three_section.get("technical_skills") or three_section.get("technical") or []
    soft_3 = three_section.get("soft_skills") or three_section.get("soft") or []
    domain_3 = three_section.get("domain_knowledge") or three_section.get("domain_keywords") or []

    if any([tech_3, soft_3, domain_3]):
        jd_simple = {
            "technical_skills": tech_3,
            "soft_skills": soft_3,
            "domain_keywords": domain_3,  # Note: converts domain_knowledge to domain_keywords
        }
        corrected = SkillCategorizer.recategorize_skills(jd_simple)
        results.jd_skills = {
            "technical_skills": corrected["technical_skills"],
            "soft_skills": corrected["soft_skills"],
            "domain_keywords": corrected["domain_keywords"],
        }
```

**Key Points**:
- `results.jd_skills` is populated from `jd_analysis.three_section_skills` if available
- Field name conversion: `domain_knowledge` → `domain_keywords` for frontend compatibility
- Uses `SkillCategorizer` to recategorize skills

## 8. Summary

### Data Flow Summary

1. **Backend** generates `results.jd_skills` with structure:
   ```json
   {
     "technical_skills": [...],
     "soft_skills": [...],
     "domain_keywords": [...]
   }
   ```

2. **API Response** includes this in `results.jd_skills`

3. **Frontend Parser** (`InitialAnalysisResults.fromJson`) extracts it directly:
   ```dart
   jdSkills: Map<String, dynamic>.from(json['jd_skills'] ?? {})
   ```

4. **Widget** (`SkillsComparisonCard`) receives it and extracts:
   ```dart
   jdSkills['technical_skills']
   jdSkills['soft_skills']
   jdSkills['domain_keywords']
   ```

5. **Display** shows side-by-side with:
   - CV Skills (Blue) on left
   - JD Skills (Green) on right
   - Both sorted alphabetically
   - Grouped by: Technical, Soft Skills, Domain

### Critical Requirements

✅ **Field Names Must Match**:
- `technical_skills` (not `technical`)
- `soft_skills` (not `soft`)
- `domain_keywords` (not `domain_knowledge`)

✅ **Data Structure**:
- Must be arrays of strings: `List<String>`
- Can be empty arrays: `[]`

✅ **Source**:
- Currently uses `results.jd_skills` from API response
- This comes from `jd_analysis.three_section_skills` (if available)
- Or from `_summarize_jd_skills()` fallback

## 9. Current Status

Based on the API response you shared:
- ✅ `results.jd_skills` exists and has correct structure
- ✅ Contains `technical_skills`, `soft_skills`, `domain_keywords`
- ✅ Frontend should be able to display it correctly

The side-by-side display should be working correctly with the current implementation!

