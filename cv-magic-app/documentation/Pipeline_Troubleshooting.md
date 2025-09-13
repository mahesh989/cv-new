# Pipeline Troubleshooting Guide

## Issue: Component Analysis and ATS Not Running Automatically

### Problem Description
After running preliminary analysis, the component analysis and ATS calculation were not being saved in the skills analysis file, even though the pipeline was scheduled.

### Root Cause
The asynchronous pipeline runs in the background and may face timing issues or failures that aren't immediately visible. Common causes include:

1. **Missing Required Files**: Component analysis requires:
   - `/cv-analysis/original_cv.json`
   - `/cv-analysis/{company}/jd_original.json`
   - `/cv-analysis/{company}/cv_jd_match_results.json`

2. **Async Task Timing**: The pipeline runs asynchronously and may not complete before checking results

3. **Silent Failures**: Errors in background tasks may not be visible in the main response

### Solutions

#### 1. Manual Pipeline Trigger (Recommended for Testing)

Use the manual trigger endpoint to run the complete pipeline synchronously:

```bash
# Trigger complete pipeline for a company
curl -X POST http://localhost:8000/api/trigger-complete-pipeline/GfK
```

Or use the test script:
```bash
python test_gfk_pipeline.py
```

#### 2. Check Pipeline Status

The pipeline runs these steps in order:
1. JD Analysis
2. CV-JD Matching
3. Component Analysis
4. ATS Calculation (automatically triggered by component analysis)

Check logs for pipeline progress:
```
🚀 [PIPELINE] Scheduling JD analysis and CV-JD matching for 'GfK'...
🔧 [PIPELINE] Starting JD analysis for GfK
✅ [PIPELINE] JD analysis saved for GfK
🔧 [PIPELINE] Starting CV-JD matching for GfK
✅ [PIPELINE] CV-JD match results saved for GfK
🔍 [PIPELINE] Starting component analysis for GfK
✅ [PIPELINE] Component analysis completed for GfK
```

#### 3. Verify Required Files

Before component analysis can run, ensure these files exist:

```python
# Check required files
import os
from pathlib import Path

base_dir = Path("/Users/mahesh/Documents/Github/mahesh/cv-magic-app/backend/cv-analysis")
company = "GfK"

required_files = {
    "CV": base_dir / "original_cv.json",
    "JD": base_dir / company / "jd_original.json",
    "Match Results": base_dir / company / "cv_jd_match_results.json"
}

for name, path in required_files.items():
    exists = "✅" if path.exists() else "❌"
    print(f"{exists} {name}: {path}")
```

#### 4. Manual Component Analysis Trigger

If only component analysis is missing:

```bash
curl -X POST http://localhost:8000/api/trigger-component-analysis/GfK
```

## Monitoring Pipeline Health

### Check Analysis Completeness

Use the API to check what analyses are available:

```bash
# List all companies with analysis status
curl http://localhost:8000/api/analysis-results

# Get detailed results for a company
curl http://localhost:8000/api/analysis-results/GfK
```

### Expected Output Structure

A complete analysis should have all these entries in the JSON file:

```json
{
  "cv_skills": { ... },
  "jd_skills": { ... },
  "analyze_match_entries": [ ... ],
  "preextracted_comparison_entries": [ ... ],
  "component_analysis_entries": [
    {
      "timestamp": "...",
      "component_analyses": {
        "skills": { ... },
        "experience": { ... },
        "industry": { ... },
        "seniority": { ... },
        "technical": { ... }
      },
      "extracted_scores": { ... }
    }
  ],
  "ats_calculation_entries": [
    {
      "timestamp": "...",
      "final_ats_score": 87.5,
      "category_status": "🌟 Strong Match",
      "breakdown": { ... }
    }
  ]
}
```

## Best Practices

1. **Use Manual Triggers for Testing**: During development, use manual pipeline triggers to ensure all steps complete

2. **Monitor Logs**: Watch server logs for pipeline progress and errors

3. **Implement Retries**: For production, consider implementing retry logic for failed pipeline steps

4. **Add Health Checks**: Create monitoring endpoints to check pipeline health

5. **Consider Synchronous Option**: For critical operations, consider offering a synchronous pipeline option that waits for completion

## Common Error Messages

### "Missing required files for component analysis"
**Solution**: Ensure preliminary analysis or skill extraction has been run first to create the required files.

### "No preextracted comparison found for ATS calculation"
**Solution**: The preextracted comparison must complete before ATS calculation. Check if it exists in the analysis file.

### "Component analysis failed"
**Solution**: Check logs for specific error. Common issues include:
- API key not configured
- AI service unavailable
- Invalid file content

---

*Last Updated: September 13, 2025*
