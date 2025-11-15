# Understanding Confirmation - Incremental CV Tailoring

## Your Requirements:

### 1. **Unified File Selector for Reruns** ✅
**Question:** Does the analysis use the latest tailored CV via unified file selector for reruns?

**Current Status (from logs):**
- ✅ YES - Logs show: `Using latest CV via unified selector → type=tailored, ts=20251115_083129`
- ✅ Code uses: `get_latest_cv_across_all(company)` which picks the latest tailored CV
- ✅ This is working correctly

---

### 2. **Incremental CV Building (ADD, not REPLACE)** ❌
**Problem:** When generating a tailored CV based on an existing tailored CV, we should only ADD new content, not REPLACE existing content.

**Current Issue:**
- ❌ When a tailored CV exists and we run again with new recommendations:
  1. System loads the existing tailored CV (✅ correct)
  2. But then generates a COMPLETELY NEW tailored CV from scratch (❌ wrong)
  3. This REPLACES the old tailored CV, losing previously integrated keywords/guidance

**Example Scenario:**
- **Run 1:** Recommendations have keywords A, B, C → Tailored CV has A, B, C integrated
- **Run 2:** New recommendations have keywords D, E, F → System generates NEW tailored CV
  - ❌ Old CV is replaced entirely
  - ❌ Keywords A, B, C might be lost if not in new recommendations
  - ❌ ATS score doesn't improve because we're not building upon previous improvements

**Desired Behavior:**
- **Run 1:** Keywords A, B, C → Tailored CV has A, B, C
- **Run 2:** Keywords D, E, F → Tailored CV should have A, B, C, D, E, F (ADDITIVE)
  - ✅ Keep all existing content
  - ✅ Only ADD new keywords/guidance from new recommendations
  - ✅ Don't replace existing content unless explicitly needed
  - ✅ Each run builds upon the previous one, improving incrementally

---

## My Understanding:

### **Current Flow:**
1. ✅ Unified selector picks latest tailored CV for reruns (WORKING)
2. ❌ CV tailoring service loads the tailored CV
3. ❌ But then generates a COMPLETELY NEW tailored CV from scratch
4. ❌ This REPLACES the old tailored CV file
5. ❌ Previously integrated keywords/guidance are lost

### **Required Flow:**
1. ✅ Unified selector picks latest tailored CV for reruns (KEEP)
2. ✅ CV tailoring service loads the tailored CV (KEEP)
3. ✅ **NEW:** Check if loaded CV is a tailored CV (not original)
4. ✅ **NEW:** If tailored CV, use it as BASE and only ADD new keywords/guidance
5. ✅ **NEW:** Merge new recommendations with existing tailored CV content
6. ✅ **NEW:** Preserve all existing keywords, bullets, and improvements
7. ✅ **NEW:** Only add new keywords/guidance that aren't already present
8. ✅ Save as new tailored CV file (with timestamp) but keep all previous improvements

---

## Questions to Confirm:

1. **Should we preserve ALL existing content?**
   - All existing keywords (even if not in new recommendations)?
   - All existing bullets and experience descriptions?
   - All existing skills?

2. **How should we handle conflicts?**
   - If new recommendations say to add keyword X, but it's already in the CV → Skip?
   - If new recommendations have different guidance for same keyword → Use new or keep old?

3. **Should we track which keywords came from which run?**
   - For debugging/auditing purposes?

4. **What about strategic positioning, experience optimization, etc.?**
   - Should we merge these too, or replace them?

---

## Proposed Solution:

### **Option 1: Incremental Addition (Recommended)**
- Load existing tailored CV as BASE
- Extract new keywords from new recommendations that aren't already in CV
- Add only NEW keywords/guidance to existing CV
- Preserve all existing content
- Save as new file with timestamp

### **Option 2: Smart Merge**
- Load existing tailored CV as BASE
- Compare new recommendations with existing CV
- Add missing keywords
- Update/improve existing content if new guidance is better
- Preserve all existing content that's still valid

---

**Please confirm if my understanding is correct, and let me know your preferences for the questions above!**

