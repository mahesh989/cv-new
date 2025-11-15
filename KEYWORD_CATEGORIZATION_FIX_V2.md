# Keyword Categorization Fix V2 - Only Missing Keywords

## Issue Identified

The AI recommendation was categorizing keywords that are **ALREADY in the CV** (matched keywords), not just missing keywords.

### Problem:
- "Collaboration" was categorized but it's already in the CV (matched)
- The prompt was showing both matched and missing keywords, causing confusion
- AI was categorizing keywords from both lists instead of ONLY missing keywords

### Root Cause:
The prompt didn't explicitly state that ONLY missing keywords should be categorized. The AI saw both matched and missing keywords and categorized some from both lists.

## Fix Applied

### Updated Prompt Template
**File:** `cv-magic-app/backend/prompt/ai_recommendation_prompt_template.py`

### Changes:

1. **Added Explicit Warning:**
   ```
   ⚠️ IMPORTANT: DO NOT categorize keywords that are ALREADY in the CV. 
   Only categorize keywords from the MISSING lists below.
   ```

2. **Clarified Missing Keywords Definition:**
   ```
   MISSING TECHNICAL KEYWORDS (X total) - NOT in CV, but in JD:
   ```

3. **Added Validation Rule:**
   ```
   - ⚠️ DO NOT categorize keywords that are ALREADY in the CV (matched keywords). 
     ONLY categorize keywords from the MISSING lists.
   - If a keyword is ALREADY in the CV (matched), it MUST NOT appear in any tier 
     (tier1, tier2, or tier3)
   ```

4. **Clarified Keyword Tiers Section:**
   ```
   ⚠️ NOTE: The "Keyword Tiers" section above shows PRE-CLASSIFIED keywords 
   from previous analysis. You MUST re-categorize ALL missing keywords listed 
   in the "MISSING KEYWORDS" section below, regardless of any pre-classification. 
   ONLY use the missing keywords lists for categorization.
   ```

## Expected Behavior

### Before Fix:
- ❌ Categorizing keywords already in CV (e.g., "Collaboration")
- ❌ Only categorizing 5 out of 21 missing keywords
- ❌ Mixing matched and missing keywords

### After Fix:
- ✅ ONLY categorizing missing keywords (NOT in CV, but in JD)
- ✅ All missing keywords categorized (tier1 + tier2 + tier3 = total missing)
- ✅ Matched keywords explicitly excluded from categorization

## Verification Steps

1. **Regenerate AI recommendation** for Climate Friendly Pty Ltd
2. **Check input file** - verify missing keywords list
3. **Check output file** - verify:
   - All categorized keywords are from missing list
   - No matched keywords are categorized
   - All missing keywords are categorized

## Files Modified

1. ✅ `cv-magic-app/backend/prompt/ai_recommendation_prompt_template.py`
   - Added explicit warnings about matched keywords
   - Clarified missing keywords definition
   - Added validation rules

## Deployment Status

- ✅ File updated locally
- ✅ Deployed to VPS
- ✅ Container restarted
- ⏳ Ready for testing

