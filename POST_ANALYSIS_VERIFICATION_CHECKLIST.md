# Post-Analysis Verification Checklist

**Use this checklist after running ANY analysis to verify the tier classification fix is working correctly.**

---

## 📋 **QUICK START**

After running an analysis for a company (e.g., "The Smith Family"):

1. Check VPS logs for Phase 6, 7, 8
2. Examine output files (input_recommendation.json, ai_recommendation.json, tailored_cv.json)
3. Verify keyword classification and integration
4. Compare with expected results

---

## 🔍 **STEP 1: CHECK LOGS (VPS)**

### **A. Phase 6 Logs - Keyword Loading & Classification**

```bash
ssh root@165.22.181.20
cd /root/cv-magic
docker compose logs backend | grep "PHASE6" | tail -50
```

#### ✅ **What to Look For:**

**1. Keyword Loading from cv_jd_matching.json**
```
✅ Expected:
🔍 [PHASE6] Starting recommendation data extraction for: The Smith Family
✅ [PHASE6] Loaded CV-JD matching from: The_Smith_Family_cv_jd_matching_*.json
📊 [PHASE6] Total missing keywords: 15
   - Required: 10 → ["Communication", "Microsoft Excel", "business processes", ...]
   - Preferred: 5 → ["curiosity", "continuous improvement mindset", ...]

❌ If Missing:
- No PHASE6 logs at all → OLD CODE STILL RUNNING
- "Skills analysis file not found" → Phase 6 not loading cv_jd_matching.json
```

**2. Keyword Categorization**
```
✅ Expected:
📊 [PHASE6] Categorized missing keywords:
   - Technical: 5 → ["Microsoft Excel", "Power BI", "SQL", ...]
   - Soft: 8 → ["Communication", "Teamwork", "Problem-solving", ...]
   - Domain: 2 → ["Dashboard creation", "Data cleansing", ...]

❌ Red Flags:
- Keywords listed as "Required" in cv_jd_matching.json but NOT in categorized list
- "business processes" missing from any category
- All keywords in one category (indicates categorization failure)
```

**3. Tier 1 Classification (AGGRESSIVE)**
```
✅ Expected:
✅ [PHASE6-CLASSIFY] Filtering complete:
   - Still missing: 15
   - Already in CV: 0  (first run)

📊 [PHASE6-CLASSIFY] Classification complete:
   - Tier 1: 8
      technical: []
      soft: ["Communication", "Teamwork", "Problem-solving", "Analytical skills", ...]
      domain: ["business processes", ...]
   - Tier 2: 5
   - Tier 3: 2
   - Already in CV: 0

✅ [PHASE6-CLASSIFY] VALIDATION PASSED - All keywords classified

❌ Red Flags:
- Tier 1 soft is EMPTY → OLD CODE or classification failed
- "Communication" NOT in Tier 1 → Should be Tier 1 (soft skill)
- "business processes" NOT in any tier → Keyword disappeared
- VALIDATION FAILED → Some keywords were lost
- Total classified ≠ Total missing → Keywords lost during classification
```

---

### **B. Phase 7 Logs - AI Validation**

```bash
docker compose logs backend | grep "PHASE7" | tail -30
```

#### ✅ **What to Look For:**

**1. AI Classification Results**
```
✅ Expected:
📊 [PHASE7-VALIDATE] AI Classification results:
   - Tier 1: 8
   - Tier 2: 5
   - Tier 3: 2
   - Total: 15
   - Expected: 15
✅ [PHASE7-VALIDATE] All keywords classified

❌ Red Flags:
- Total < Expected → AI lost some keywords
- No PHASE7 logs → Validation not running
- "Could not load input recommendation" → Phase 6 output not saved
- validation_passed: false → AI classification incomplete
```

---

### **C. Phase 8 Logs - CV Tailoring with Validation**

```bash
docker compose logs backend | grep "PHASE8" | tail -50
```

#### ✅ **What to Look For:**

**1. Tier 1 Keyword Extraction**
```
✅ Expected:
🎯 [PHASE8] Starting CV tailoring with validation (max 3 attempts)
📊 [PHASE8] Tier 1 keywords to integrate: 8
   - technical: []
   - soft: ["Communication", "Teamwork", "Problem-solving", "Analytical skills"]
   - domain: ["business processes"]

❌ Red Flags:
- No PHASE8 logs → Validation wrapper not being used
- Tier 1 keywords: 0 → No keywords to integrate (check Phase 6/7)
```

**2. Integration Attempts**
```
✅ Expected:
🔄 [PHASE8] Attempt 1/3
📊 [PHASE8] Attempt 1 results:
   - Integration rate: 87.5%
   - Integrated: 7/8
   - Missing: 1
⚠️ Missing Tier 1 keyword: 'Communication' (soft)

🔄 [PHASE8] Retrying with focus on missing keywords...
🔄 [PHASE8] Attempt 2/3
📊 [PHASE8] Attempt 2 results:
   - Integration rate: 100.0%
   - Integrated: 8/8
   - Missing: 0

✅ [PHASE8] 100% Tier 1 integration achieved!

❌ Red Flags:
- Integration rate < 50% after all attempts → CV generation issue
- No retry attempts → Validation not triggering retries
- Same missing keywords in every attempt → Prompt not being updated
```

**3. Final Summary**
```
✅ Expected:
================================================================================
✅ [PHASE8] COMPLETE - Summary:
   Company: The Smith Family
   Total attempts: 2
   Final integration rate: 100.0%
   Tier 1 keywords integrated: 8/8
================================================================================

❌ Red Flags:
- Integration rate < 80% → Low integration success
- Missing count > 0 after max attempts → Some Tier 1 keywords never integrated
```

---

## 📂 **STEP 2: CHECK OUTPUT FILES**

### **A. Phase 6 Output: input_recommendation.json**

**Location:**
```bash
find /root/cv-magic/storage/cv-analysis -name "*The_Smith_Family*input_recommendation*.json" -type f -mtime -1
```

**What to Check:**
```bash
# On VPS
cat /path/to/The_Smith_Family_input_recommendation_*.json | jq '.keyword_integration_guidance'
```

#### ✅ **Expected Structure:**

```json
{
  "keyword_integration_guidance": {
    "tier1_always_add": {
      "technical": [],
      "soft": ["Communication", "Teamwork", "Problem-solving", "Analytical skills"],
      "domain": ["business processes"]
    },
    "tier2_add_if_evidence": {
      "technical": ["Microsoft Excel", "Power BI", "SQL"],
      "soft": [],
      "domain": ["Dashboard creation", "Data cleansing"]
    },
    "tier3_never_add": {
      "technical": [],
      "soft": [],
      "domain": ["Annual Impact Report", "food relief"]
    },
    "already_in_cv_filtered": []
  }
}
```

#### ❌ **Red Flags:**

| Issue | What It Means | Action |
|-------|---------------|--------|
| All tiers are EMPTY `[]` | Phase 6 classification failed | Check Phase 6 logs for errors |
| "Communication" in Tier 2 | Not using aggressive classification | OLD CODE - redeploy |
| "business processes" NOT in any tier | Keyword disappeared | Check cv_jd_matching.json has it |
| Tier 1 soft is `[]` | Soft skills not classified to Tier 1 | OLD CODE - redeploy |

---

### **B. Phase 7 Output: ai_recommendation.json**

**Location:**
```bash
find /root/cv-magic/storage/cv-analysis -name "*The_Smith_Family*ai_recommendation*.json" -type f -mtime -1
```

**What to Check:**
```bash
# On VPS
cat /path/to/The_Smith_Family_ai_recommendation_*.json | jq '.validation'
```

#### ✅ **Expected Validation:**

```json
{
  "validation": {
    "total_classified": 15,
    "expected_total": 15,
    "tier1_count": 8,
    "tier2_count": 5,
    "tier3_count": 2,
    "all_keywords_classified": true,
    "validation_passed": true
  }
}
```

#### ✅ **Expected Keyword Integration:**

```bash
cat /path/to/The_Smith_Family_ai_recommendation_*.json | jq '.structured_recommendations.keyword_integration'
```

```json
{
  "keyword_integration": {
    "tier1_integrate_immediately": {
      "technical": [],
      "soft": [
        {
          "keyword": "Communication",
          "rationale": "Generic soft skill, universally transferable"
        },
        {
          "keyword": "Teamwork",
          "rationale": "Essential collaboration skill"
        }
      ],
      "domain": [
        {
          "keyword": "business processes",
          "rationale": "Generic business skill, transferable"
        }
      ]
    }
  }
}
```

#### ❌ **Red Flags:**

| Issue | What It Means | Action |
|-------|---------------|--------|
| `validation_passed: false` | AI didn't classify all keywords | Check Phase 7 logs |
| `total_classified < expected_total` | Keywords lost during AI classification | Check input vs output |
| "Communication" in tier2 (not tier1) | AI overriding Phase 6 classification | Check AI prompt |
| No `validation` field | OLD CODE - Phase 7 validation not running | Redeploy |

---

### **C. Phase 8 Output: tailored_cv.json**

**Location:**
```bash
find /root/cv-magic/storage/cv-analysis -name "*tailored_cv*.json" -type f -mtime -1
```

**What to Check:**
```bash
# Search for Tier 1 keywords in tailored CV
cat /path/to/latest_tailored_cv_*.json | grep -i "communication\|teamwork\|problem-solving\|business processes"
```

#### ✅ **Expected:**

- Tier 1 keywords appear in:
  - `skills` section
  - `experience` bullets
  - `projects` bullets (if applicable)
  - `summary` or `role_highlights`

**Example:**
```json
{
  "skills": [
    {
      "category": "Soft Skills",
      "skills": ["Communication", "Teamwork", "Problem-solving", ...]
    }
  ],
  "experience": [
    {
      "bullets": [
        "Led cross-functional team collaboration to deliver...",
        "Improved business processes through data-driven analysis..."
      ]
    }
  ]
}
```

#### ❌ **Red Flags:**

| Issue | What It Means | Action |
|-------|---------------|--------|
| Tier 1 keyword NOT in CV | Integration failed | Check Phase 8 logs |
| Only in skills, not in bullets | Weak integration | Check AI prompt |
| All Tier 1 keywords missing | Phase 8 not running | Check logs, redeploy |

---

## 🔄 **STEP 3: RERUN VERIFICATION (Same Company)**

### **Purpose:** Verify keyword filtering works on rerun

**Action:** Run analysis again for same company

#### ✅ **Expected on Second Run:**

**Phase 6 Logs:**
```
📊 [PHASE6] Total missing keywords: 15
✅ [PHASE6-CLASSIFY] Filtering complete:
   - Still missing: 7
   - Already in CV: 8  ← Keywords from first run filtered!

📊 [PHASE6-CLASSIFY] Classification complete:
   - Tier 1: 0  ← All soft skills already integrated!
   - Tier 2: 5
   - Tier 3: 2
   - Already in CV: 8  ← ["Communication", "Teamwork", "Problem-solving", ...]
```

**input_recommendation.json:**
```json
{
  "tier1_always_add": {
    "technical": [],
    "soft": [],  ← EMPTY because already integrated
    "domain": []
  },
  "already_in_cv_filtered": [
    "Communication",
    "Teamwork",
    "Problem-solving",
    "business processes",
    ...
  ]
}
```

#### ❌ **Red Flags:**

| Issue | What It Means | Action |
|-------|---------------|--------|
| Already in CV: 0 (should be > 0) | Filtering not working | Check keyword extraction |
| Same Tier 1 keywords as first run | Previous CV not being used | Check CV selector |
| Tier 1 still has "Communication" | Keyword matching failed | Check fuzzy matching logic |

---

## 📊 **STEP 4: COMPARISON TABLE**

### **Expected vs Actual - Use This Table**

| Metric | First Run Expected | Second Run Expected | Check File/Log |
|--------|-------------------|---------------------|----------------|
| **Total Missing Keywords** | 15 | 15 (same JD) | Phase 6 logs |
| **Keywords Filtered** | 0 | 8 | Phase 6 logs |
| **Still Missing** | 15 | 7 | Phase 6 logs |
| **Tier 1 Count** | 8 | 0 | input_recommendation.json |
| **Tier 1 Soft Skills** | ["Communication", "Teamwork", ...] | [] (empty) | input_recommendation.json |
| **"business processes"** | In Tier 1 or Tier 2 | In already_in_cv_filtered | input_recommendation.json |
| **Validation Passed** | true | true | ai_recommendation.json |
| **Integration Rate** | 80-100% | 80-100% | Phase 8 logs |
| **Tier 1 in CV** | Yes | N/A (already there) | tailored_cv.json |

---

## 🎯 **STEP 5: KEY SUCCESS INDICATORS**

### **✅ ALL GOOD - Your Implementation is Working!**

If you see:
1. ✅ Phase 6/7/8 logs present
2. ✅ All missing keywords from cv_jd_matching.json appear in logs
3. ✅ "business processes" NOT disappeared
4. ✅ "Communication" in Tier 1 (not Tier 2)
5. ✅ ALL soft skills → Tier 1
6. ✅ Validation passes in Phase 6, 7, 8
7. ✅ Integration rate > 80%
8. ✅ Tier 1 keywords appear in tailored CV
9. ✅ Second run filters keywords as "already in CV"
10. ✅ Tier 1 count decreases with each rerun

---

### **❌ ISSUES DETECTED - Troubleshooting**

| Symptom | Root Cause | Fix |
|---------|------------|-----|
| No PHASE6/7/8 logs | Docker using OLD CODE | Rebuild: `docker compose build --pull --no-cache backend` |
| "business processes" disappeared | Not loading from cv_jd_matching.json | Check Phase 6 code, redeploy |
| "Communication" in Tier 2 | Not using aggressive classification | OLD CODE, redeploy |
| Tier 1 soft empty | Classification failed | Check Phase 6 logs for errors |
| Validation failed | Keywords lost during classification | Check Phase 6 classification logic |
| Integration rate < 50% | CV generation issue | Check Phase 8 logs, AI prompt |
| Same keywords in rerun | Filtering not working | Check keyword extraction/matching |

---

## 📋 **QUICK COMMAND REFERENCE**

### **One-Liner to Check Everything:**

```bash
ssh root@165.22.181.20 'cd /root/cv-magic && \
echo "=== PHASE 6 ===" && docker compose logs backend | grep "PHASE6" | tail -20 && \
echo "" && echo "=== PHASE 7 ===" && docker compose logs backend | grep "PHASE7" | tail -10 && \
echo "" && echo "=== PHASE 8 ===" && docker compose logs backend | grep "PHASE8" | tail -15 && \
echo "" && echo "=== FILES ===" && \
find storage/cv-analysis -name "*input_recommendation*.json" -type f -mtime -1 -exec echo "Found: {}" \; | head -3'
```

---

## 📝 **CHECKLIST TEMPLATE**

**Copy and fill out after each analysis:**

```
Company: _____________
Date: _____________
Run Number: _____ (1st, 2nd, 3rd)

□ Phase 6 logs present
□ Keywords loaded from cv_jd_matching.json
□ "business processes" in categorized list (if in JD)
□ "Communication" in Tier 1 soft
□ Tier 1 has soft skills (not empty)
□ Validation passed in Phase 6

□ Phase 7 logs present
□ validation_passed: true
□ total_classified = expected_total

□ Phase 8 logs present
□ Integration rate: _____% (target: >80%)
□ Attempts: _____ (max 3)
□ Missing keywords: _____ (target: 0)

□ Tier 1 keywords in tailored CV
□ Second run filters keywords
□ Tier 1 count decreased (on rerun)

Overall: ✅ PASS / ❌ FAIL
Notes: ___________________________
```

---

## 🎯 **WHAT SUCCESS LOOKS LIKE**

### **Perfect First Run:**
```
Phase 6: 15 missing → 8 Tier 1 (all soft) → 0 filtered
Phase 7: 15 classified → validation passed
Phase 8: 100% integration (2 attempts)
Output: All Tier 1 in CV
```

### **Perfect Second Run:**
```
Phase 6: 15 missing → 0 Tier 1 (already in CV) → 8 filtered
Phase 7: 7 classified → validation passed
Phase 8: Tier 2 integration only
Output: Converging to optimal CV
```

---

**Use this checklist after EVERY analysis to ensure the fix is working!** ✅

