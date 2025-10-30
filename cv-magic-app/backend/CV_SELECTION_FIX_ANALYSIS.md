# CV Selection Logic Fix - Complete Analysis

## Investigation Summary

### User Report
User (chunem@gmail.com) performed two analyses:
1. **UNHCR analysis** - Looked OK
2. **Cause Food (Foodbank) analysis** - Issue detected

**Problem:** When using `maheshwor_tiwari.pdf` for Foodbank JD analysis, the system used an OLD tailored CV instead of the newly uploaded original CV.

**Expected Behavior:** When a new JD link/company analysis is being done after uploading a fresh CV, it should ALWAYS choose the `original_cv` for the first analysis.

---

## Complete Analysis of What Happened

### Timeline (Oct 30, 2025):

1. **10:24-10:27**: UNHCR analysis
   - Used: `Australia_for_UNHCR_tailored_cv_20251027_090720` (OLD from Oct 27)
   - ✅ **This was OK** - happened BEFORE the new CV upload

2. **10:31-10:32**: User uploaded `maheshwor_tiwari.pdf`
   - `original_cv.json` was updated with Maheshwor Tiwari's CV
   - File modification time: 1761820338 (Oct 30 10:31-10:32)

3. **10:36-10:40**: Foodbank analysis
   - Used: `Foodbank_tailored_cv_20251026_103852` (OLD from Oct 26) ❌ **WRONG!**
   - Should have used: `original_cv.json` (NEW from Oct 30 10:31) ✅
   - File modification times:
     - Old Foodbank tailored CV: 1761475132 (Oct 26)
     - New original CV: 1761820338 (Oct 30) - **345,206 seconds newer!**

---

## Root Cause Analysis

### The Bug
Located in: `app/unified_latest_file_selector.py` - `get_latest_cv_across_all()` method

**Original Sorting Logic:**
```python
def _candidate_key(c):
    json_path, _txt_path, ts, _ftype = c
    mtime = json_path.stat().st_mtime if json_path and json_path.exists() else 0
    return (ts, mtime)  # Sorted by timestamp FIRST, then mtime
candidates.sort(key=_candidate_key, reverse=True)
```

**Why it Failed:**
- Tailored CV: `ts="20251026_103852"` (from filename), `mtime=1761475132`
- Original CV: `ts="00000000_000000"` (dummy timestamp), `mtime=1761820338` (NEWER!)

When sorting by `(timestamp, mtime)` in descending order:
- `"20251026_103852"` > `"00000000_000000"` - tailored CV ALWAYS wins
- Even though original CV has a MUCH newer modification time!

The timestamp comparison happened FIRST, so the mtime (which should have indicated the CV was recently updated) was ignored.

---

## The Fix

### Implementation
Modified `get_latest_cv_across_all()` to:

1. **Detect when original_cv is significantly newer** (>60 seconds) than ALL tailored CVs
2. **When detected:** Prioritize `original` type in sorting
3. **Otherwise:** Use original timestamp-based sorting

### Key Code Changes:
```python
# Check if original_cv is significantly newer than any tailored CV
original_candidates = [c for c in candidates if c[3] == "original"]
tailored_candidates = [c for c in candidates if c[3] == "tailored"]

should_prefer_original = False
if original_candidates and tailored_candidates:
    original_mtime = original_json.stat().st_mtime
    max_tailored_mtime = max(t_json.stat().st_mtime for t_json, _, _, _ in tailored_candidates)
    
    # If original_cv is newer by >60 seconds, prefer it
    if original_mtime > 0 and (original_mtime - max_tailored_mtime) > 60:
        should_prefer_original = True
        print(f"🆕 [UNIFIED] Original CV is significantly newer (mtime diff: {original_mtime - max_tailored_mtime:.0f}s)")

# Modified sorting key
def _candidate_key(c):
    json_path, _txt_path, ts, ftype = c
    mtime = json_path.stat().st_mtime if json_path and json_path.exists() else 0
    
    if should_prefer_original:
        type_priority = 1 if ftype == "original" else 0
        return (type_priority, mtime, ts)  # Sort by type FIRST, then mtime, then timestamp
    else:
        return (ts, mtime)  # Original behavior
```

---

## Testing

### Test Results
Created `test_cv_selection_fix.py` to verify the fix:

**Scenario:**
- Old tailored CV from Oct 26 (4 days ago)
- New original CV just uploaded (current time)
- Time difference: 345,600 seconds

**Result:**
```
🆕 [UNIFIED] Original CV is significantly newer (mtime diff: 345600s), preferring it for first analysis
🔍 [UNIFIED_DEBUG] CV Selection Details for TestCompany:
  🏆 Selected candidate: type=original ✅
```

✅ **Test PASSED** - Original CV correctly selected when significantly newer

---

## Deployment

### Steps Completed:
1. ✅ Fixed `app/unified_latest_file_selector.py`
2. ✅ Created and verified test case
3. ✅ Committed changes to git
4. ✅ Pushed to `enhanced-vps-ghs` branch
5. ✅ Deployed to VPS (13.210.217.204)
6. ✅ Restarted backend container

### Verification:
```bash
ssh ubuntu@13.210.217.204 "cd ~/cv-new/cv-magic-app && docker compose restart backend"
# Container cv_backend  Restarted ✅
```

---

## What This Fixes

### Before the Fix:
When you uploaded a new CV (`maheshwor_tiwari.pdf`):
- System would ALWAYS choose old tailored CVs for companies that already had them
- Even though you just uploaded a completely different CV!
- Result: Analysis based on WRONG CV content

### After the Fix:
When you upload a new CV:
- System detects that `original_cv.json` is significantly newer (>60s) than any tailored CV
- For the FIRST analysis after upload, uses the NEW original CV ✅
- Subsequent analyses (without CV changes) can still use tailored CVs if appropriate

---

## Rule Implemented

**"Always use original_cv for the first analysis after uploading a new CV"**

The 60-second threshold ensures:
- Fresh CV uploads always trigger original_cv selection
- Minor file system fluctuations don't cause issues
- Re-analyses of same CV continue to work as expected

---

## Next Steps for Testing

To verify the fix works for your scenario:
1. Upload a NEW CV (or select a different existing CV)
2. Wait 2-3 minutes to ensure file modification times settle
3. Run analysis for ANY company (new or existing)
4. Check logs - you should see:
   ```
   🆕 [UNIFIED] Original CV is significantly newer (mtime diff: XXXXs), preferring it for first analysis
   📄 [UNIFIED] Latest CV resolved → type=original
   ```
5. The analysis should use content from your newly uploaded CV

---

## Files Changed

1. **cv-magic-app/backend/app/unified_latest_file_selector.py**
   - Modified `get_latest_cv_across_all()` method
   - Added logic to detect and prefer recently updated original_cv
   - ~47 lines added/modified

2. **cv-magic-app/backend/test_cv_selection_fix.py** (NEW)
   - Test script to verify the fix
   - Creates test scenario with old tailored CV and new original CV
   - Validates that original CV is correctly selected

---

## Commit Information

**Commit:** debec5d  
**Branch:** enhanced-vps-ghs  
**Message:** "Fix CV selection logic: prioritize original_cv when newly updated"

---

## Contact

For any questions or issues:
- Check backend logs: `docker logs cv_backend`
- Look for the `🆕 [UNIFIED]` log entries
- The detailed debug logs show all candidates and selection reasoning

---

**Status:** ✅ DEPLOYED AND ACTIVE
**Date:** October 30, 2025
**Server:** 13.210.217.204 (VPS)

