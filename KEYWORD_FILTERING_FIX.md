# Keyword Filtering Fix - Remove Matched Keywords from Missing List

## Issue Identified

Keywords that are **ALREADY in the CV** (matched) were appearing in the **missing keywords list** due to case-sensitivity issues in the matching process. This caused the AI to categorize keywords that are already in the CV.

### Problem:
- 7 keywords were incorrectly categorized: adaptability, ai engineering, collaboration, computer vision, deep learning, machine learning, python
- These keywords appear in BOTH matched and missing lists (case-sensitivity issue)
- Example: "Computer Vision" (matched) vs "computer vision" (missing) - same keyword, different case

### Root Cause:
The CV-JD matching process has case-sensitivity issues, causing the same keyword to appear in both matched and missing lists with different cases. The prompt was passing both lists to the AI without filtering.

## Solution Implemented

### Code-Level Filtering
**File:** `cv-magic-app/backend/prompt/ai_recommendation_prompt_template.py`

**Added filtering logic BEFORE prompt generation:**
```python
# CRITICAL FIX: Filter out keywords that appear in both matched and missing lists
# This handles case-sensitivity issues where the same keyword appears in both lists
def normalize_keyword(kw):
    """Normalize keyword for comparison (lowercase, strip)"""
    return str(kw).lower().strip()

def filter_missing_keywords(missing_list, matched_list):
    """Remove keywords from missing list that also appear in matched list (case-insensitive)"""
    matched_normalized = {normalize_keyword(kw) for kw in matched_list}
    filtered = []
    for kw in missing_list:
        if normalize_keyword(kw) not in matched_normalized:
            filtered.append(kw)
    return filtered

# Filter missing keywords to exclude those already matched
if technical_match.get('missing') and technical_match.get('matched'):
    technical_match['missing'] = filter_missing_keywords(
        technical_match['missing'], 
        technical_match['matched']
    )
```

### How It Works:
1. **Normalize keywords** (lowercase, strip) for case-insensitive comparison
2. **Filter missing list** to remove any keywords that also appear in matched list
3. **Pass only truly missing keywords** to the AI prompt
4. **AI only sees missing keywords** - no confusion about matched keywords

## Expected Behavior

### Before Fix:
- ❌ Missing list: 30 keywords (including 7 that are already matched)
- ❌ Categorized: 29 keywords (including 7 matched keywords)
- ❌ Error: 7 keywords incorrectly categorized

### After Fix:
- ✅ Missing list: 23 keywords (7 matched keywords filtered out)
- ✅ Categorized: 23 keywords (only truly missing keywords)
- ✅ No matched keywords in categorized list

## Test Results

**Test Case:**
- Matched: ['Adaptability', 'AI engineering', 'Collaboration', 'Computer Vision', 'Python']
- Missing (before): ['adaptability', 'ai engineering', 'collaboration', 'computer vision', 'python', 'data analysis', 'lidar']
- Missing (after filter): ['data analysis', 'lidar'] ✅
- Removed: 5 matched keywords correctly filtered out

## Files Modified

1. ✅ `cv-magic-app/backend/prompt/ai_recommendation_prompt_template.py`
   - Added `normalize_keyword()` function
   - Added `filter_missing_keywords()` function
   - Applied filtering to technical, soft, and domain categories

## Deployment Status

- ✅ File updated locally
- ✅ Deployed to VPS
- ✅ Container restarted
- ⏳ Ready for testing

## Verification Steps

1. **Regenerate AI recommendation** for Climate Friendly Pty Ltd
2. **Check input file** - verify missing keywords list (should have fewer keywords after filtering)
3. **Check output file** - verify:
   - All categorized keywords are from missing list only
   - NO matched keywords are categorized
   - All truly missing keywords are categorized

## Additional Improvements

The prompt also includes:
- Explicit list of matched keywords (for reference)
- Warning not to categorize matched keywords
- Clear instruction that if a keyword appears in both lists, it's already in CV

This provides defense-in-depth: both code-level filtering AND prompt-level instructions.

