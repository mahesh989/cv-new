# Analysis Report: Last 3 Runs for Climate_Friendly_Pty_Ltd

## Executive Summary

**Analysis Date:** 2025-11-15  
**Company:** Climate_Friendly_Pty_Ltd  
**Runs Analyzed:** 3 (Nov 14 06:52, Nov 14 10:38, Nov 15 03:52)

---

## Run Comparison

### Run 1: 2025-11-14 06:52:57
- **ATS Score:** 41.5/100
- **Match Rate:** 30.0%
- **Missing Keywords:** 14 technical, 1 soft, 6 domain

**Tier 1 Keywords:**
- Technical: "Data analysis", "Data visualizations"
- Soft: "Collaboration", "Adaptability"

**Tier 2 Keywords:**
- Technical: "Computer vision", "Data engineering"
- Soft: "Relationship development"

**Tier 3 Keywords:**
- Technical: "IAM"
- Domain: "Christian identity"

---

### Run 2: 2025-11-14 10:38:30
- **ATS Score:** 43.8/100 (+2.3 improvement)
- **Match Rate:** 27.59% (-2.41% decrease)
- **Missing Keywords:** 14 technical, 1 soft, 6 domain (same as Run 1)

**Tier 1 Keywords:**
- Technical: "Data visualisations" (singular, different spelling)
- Soft: "Collaboration", "Adaptability" (same as Run 1)

**Tier 2 Keywords:**
- Technical: "Computer vision", "Data engineering" (same as Run 1)
- Soft: [] (empty - lost "Relationship development")

**Tier 3 Keywords:**
- Technical: [] (empty - lost "IAM")
- Domain: [] (empty - lost "Christian identity")

**Issues Identified:**
1. ❌ Lost Tier 2 soft keyword "Relationship development"
2. ❌ Lost Tier 3 keywords (IAM, Christian identity)
3. ⚠️ Keyword spelling inconsistency ("visualizations" vs "visualisations")
4. ⚠️ Match rate decreased despite ATS score improvement

---

### Run 3: 2025-11-15 03:52:16
- **ATS Score:** 43.9/100 (+0.1 from Run 2, +2.4 from Run 1)
- **Match Rate:** 29.63% (+2.04% from Run 2, -0.37% from Run 1)
- **Missing Keywords:** 17 technical, 1 soft, 5 domain (worse than previous runs)

**Tier 1 Keywords:**
- Technical: "Visualisations", "Scripting languages" (NEW keywords, different from previous)
- Soft: "Adaptability" (lost "Collaboration")

**Tier 2 Keywords:**
- Technical: "Version control", "Statistical models", "Data engineering", "Deep learning", "Remote sensing" (5 keywords - expanded)
- Soft: [] (empty)

**Tier 3 Keywords:**
- Technical: 8 keywords (expanded list)
- Domain: 5 keywords (expanded list)

**Issues Identified:**
1. ❌ Lost Tier 1 soft keyword "Collaboration" from previous runs
2. ❌ Missing keywords INCREASED (17 vs 14 technical)
3. ⚠️ Completely different Tier 1 keywords than previous runs
4. ⚠️ No continuity - keywords from Run 1 and Run 2 are not preserved

---

## Critical Issues Found

### 1. **Keywords Not Preserved Across Runs** ❌
- **Problem:** Each run generates completely new keyword recommendations
- **Impact:** Keywords from previous runs are lost, even if they were successfully integrated
- **Example:** "Collaboration" was in Run 1 and Run 2, but missing in Run 3

### 2. **Incremental Merge Not Working** ❌
- **Problem:** The system claims to preserve content but keywords are being lost
- **Evidence:** 
  - Run 2 lost "Relationship development" from Tier 2
  - Run 3 lost "Collaboration" from Tier 1
  - Missing keywords increased from 14 to 17 technical keywords

### 3. **ATS Score Stagnation** ⚠️
- **Problem:** ATS score improved only 2.4 points over 3 runs (41.5 → 43.9)
- **Expected:** Should improve more if keywords are being preserved and added incrementally
- **Root Cause:** New tailored CVs are replacing old ones instead of building upon them

### 4. **Match Rate Inconsistency** ⚠️
- **Problem:** Match rate fluctuates (30.0% → 27.59% → 29.63%)
- **Expected:** Should improve or at least remain stable if content is preserved
- **Root Cause:** CV content is being regenerated from scratch each time

### 5. **Keyword Inconsistency** ⚠️
- **Problem:** Same keywords appear with different spellings/forms
  - "Data visualizations" vs "Data visualisations" vs "Visualisations"
- **Impact:** Confusion and potential duplicate keywords

---

## Root Cause Analysis

### Issue 1: Prompt Not Enforcing Preservation
**Location:** `cv_tailoring_service.py` - `_build_user_prompt()`

**Current Behavior:**
- Prompt includes incremental mode instructions
- BUT: AI is still generating completely new CVs
- Instructions may not be strong enough

**Evidence:**
```python
if is_tailored_cv_base:
    incremental_mode_instructions = """
    🚨 CRITICAL: INCREMENTAL MERGE MODE - PRESERVE EXISTING CONTENT
    ...
    """
```

**Problem:** Instructions exist but AI is not following them strictly enough.

---

### Issue 2: No Keyword Tracking
**Location:** Missing feature

**Problem:**
- No system to track which keywords were added in previous runs
- No way to ensure keywords from previous recommendations are preserved
- Each recommendation generation is independent

**Impact:**
- Keywords from Run 1 are not considered in Run 2
- Keywords from Run 2 are not considered in Run 3

---

### Issue 3: Validation Not Enforcing Preservation
**Location:** `_validate_incremental_merge()`

**Current Behavior:**
- Validation checks if bullets/skills decreased
- BUT: Only warns, doesn't fail or regenerate
- Allows CVs with lost content to be saved

**Evidence:**
```python
if preservation_rate < 80:
    logger.warning(f"⚠️ Issues found: {issues}")
    # Still continues - doesn't fail!
```

---

## Recommended Fixes

### Fix 1: Strengthen Incremental Merge Prompt
**Priority:** HIGH  
**File:** `cv_tailoring_service.py` - `_build_user_prompt()`

**Changes:**
1. Add explicit list of existing keywords that MUST be preserved
2. Add instruction to ONLY ADD new keywords, never remove existing ones
3. Add validation that all existing keywords are present in output

---

### Fix 2: Track Keywords Across Runs
**Priority:** HIGH  
**File:** New feature in `cv_tailoring_service.py`

**Changes:**
1. Extract keywords from existing tailored CV before generation
2. Pass list of existing keywords to prompt
3. Validate that all existing keywords are preserved in new CV

---

### Fix 3: Fail Validation on Content Loss
**Priority:** MEDIUM  
**File:** `cv_tailoring_service.py` - `_validate_incremental_merge()`

**Changes:**
1. Make validation stricter - fail if preservation rate < 90%
2. Regenerate if content is lost
3. Log specific missing keywords/bullets

---

### Fix 4: Merge Recommendations
**Priority:** MEDIUM  
**File:** `ai_recommendation_generator.py`

**Changes:**
1. When generating new recommendations, include keywords from previous recommendations
2. Mark keywords as "already integrated" if they exist in tailored CV
3. Only recommend NEW keywords that aren't already present

---

### Fix 5: Improve Keyword Consistency
**Priority:** LOW  
**File:** `ats_recommendation_service.py`

**Changes:**
1. Normalize keyword spelling/formatting
2. Deduplicate similar keywords
3. Use consistent keyword format across runs

---

## Implementation Plan

### Phase 1: Immediate Fixes (Critical)
1. ✅ Strengthen incremental merge prompt with explicit keyword list
2. ✅ Extract and track existing keywords from tailored CV
3. ✅ Fail validation if keywords are lost

### Phase 2: Enhancement (Important)
4. ✅ Merge recommendations across runs
5. ✅ Track keyword integration history
6. ✅ Improve keyword normalization

### Phase 3: Optimization (Nice to Have)
7. ✅ Add keyword deduplication
8. ✅ Improve ATS score tracking across runs
9. ✅ Add analytics dashboard for keyword preservation

---

## Testing Plan

### Test Case 1: Incremental Keyword Addition
1. Run 1: Generate tailored CV with keywords A, B, C
2. Run 2: Generate tailored CV with keywords D, E, F
3. **Expected:** Final CV should have A, B, C, D, E, F
4. **Actual:** Need to verify

### Test Case 2: Keyword Preservation
1. Run 1: Add "Collaboration" to Tier 1
2. Run 2: Generate new recommendations
3. **Expected:** "Collaboration" should still be in CV
4. **Actual:** Currently lost

### Test Case 3: ATS Score Improvement
1. Run 1: ATS = 41.5
2. Run 2: Add keywords → ATS should improve
3. Run 3: Add more keywords → ATS should improve further
4. **Expected:** Incremental improvement
5. **Actual:** Stagnation (41.5 → 43.8 → 43.9)

---

## Conclusion

The main issue is that **incremental merge is not working correctly**. The system:
- ✅ Detects that a tailored CV exists
- ✅ Loads the tailored CV
- ❌ But generates a completely new CV instead of preserving existing content
- ❌ Keywords from previous runs are lost

**Critical fixes needed:**
1. Strengthen prompt to explicitly preserve existing keywords
2. Track and validate keyword preservation
3. Fail validation if content is lost

