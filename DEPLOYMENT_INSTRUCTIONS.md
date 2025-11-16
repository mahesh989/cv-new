# Deployment Instructions - Tier Classification Fix

**Status:** Code committed and pushed ✅  
**Branch:** `enhanced-vps-ghs`  
**Commit:** `209a0d6` - "Fix: Implement aggressive Tier 1 classification and validation loop"

---

## 🚀 DEPLOYMENT TO VPS

### Step 1: SSH to VPS
```bash
ssh root@165.22.181.20
```

### Step 2: Navigate to Project
```bash
cd /root/cv-magic
```

### Step 3: Pull Latest Changes
```bash
git fetch origin
git checkout enhanced-vps-ghs
git pull origin enhanced-vps-ghs
```

**Expected Output:**
```
From github.com:mahesh989/cv-new
 * branch            enhanced-vps-ghs -> FETCH_HEAD
Updating 4b588ed..209a0d6
Fast-forward
 8 files changed, 2088 insertions(+), 133 deletions(-)
 create mode 100644 PHASE_CODE_COMPLETE.md
 create mode 100644 TIER_CLASSIFICATION_FIX_COMPLETE.md
 create mode 100644 TIER_CLASSIFICATION_FIX_STATUS.md
```

### Step 4: Stop Current Containers
```bash
docker compose down
```

### Step 5: Rebuild Backend (No Cache)
```bash
docker compose build --pull --no-cache backend
```

**Why no cache?**
- Ensures latest code is used
- Previous issue: Docker was using old code despite git pull
- This forces a complete rebuild

### Step 6: Start All Services
```bash
docker compose up -d
```

### Step 7: Verify Deployment
```bash
# Check if containers are running
docker compose ps

# Check backend logs for startup
docker compose logs backend | tail -50
```

**Look for:**
```
✅ Loaded CV optimization framework
✅ Backend API started successfully
```

---

## 🔍 VERIFICATION TESTS

### Test 1: Check Phase 6 Logging
```bash
docker compose logs backend | grep "PHASE6" | tail -20
```

**Expected Output (on next analysis run):**
```
🔍 [PHASE6] Starting recommendation data extraction for: Company
✅ [PHASE6] Loaded CV-JD matching from: Company_cv_jd_matching_*.json
📊 [PHASE6] Total missing keywords: X
   - Required: X → [list]
   - Preferred: X → [list]
📊 [PHASE6] Categorized missing keywords:
   - Technical: X → [list]
   - Soft: X → [list]
   - Domain: X → [list]
✅ [PHASE6-CLASSIFY] VALIDATION PASSED - All keywords classified
```

### Test 2: Check Phase 7 Logging
```bash
docker compose logs backend | grep "PHASE7" | tail -20
```

**Expected Output:**
```
📊 [PHASE7-VALIDATE] AI Classification results:
   - Tier 1: X
   - Tier 2: X
   - Tier 3: X
   - Total: X
   - Expected: X
✅ [PHASE7-VALIDATE] All keywords classified
```

### Test 3: Check Phase 8 Logging
```bash
docker compose logs backend | grep "PHASE8" | tail -30
```

**Expected Output:**
```
🎯 [PHASE8] Starting CV tailoring with validation (max 3 attempts)
📊 [PHASE8] Tier 1 keywords to integrate: X
   - technical: [list]
   - soft: [list]
🔄 [PHASE8] Attempt 1/3
📊 [PHASE8] Attempt 1 results:
   - Integration rate: X%
   - Integrated: X/X
   - Missing: X
✅ [PHASE8] 100% Tier 1 integration achieved!
```

### Test 4: Perform Live Analysis
**On your mobile app or web interface:**

1. **Select a user** (e.g., `chunem@gmail.com`)
2. **Upload/Select CV** (e.g., `latest_cv.pdf`)
3. **Enter JD URL** for "The Smith Family"
4. **Run Analysis**

**Watch for:**
```bash
# On VPS terminal:
docker compose logs -f backend | grep -E "PHASE6|PHASE7|PHASE8|KEYWORD"
```

**Success Indicators:**
- ✅ All missing keywords from cv_jd_matching.json are loaded
- ✅ "business processes" appears in categorized list (if in JD)
- ✅ "Communication" classified as Tier 1 (not Tier 2)
- ✅ ALL soft skills → Tier 1
- ✅ Validation passes in Phase 6, 7, 8
- ✅ High Tier 1 integration rate (80%+)

---

## 📊 TESTING CHECKLIST

### ✅ Deployment Verification:
- [ ] Git pull successful on VPS
- [ ] Docker rebuild completed (no cache)
- [ ] Containers running (docker compose ps)
- [ ] Backend logs show successful startup
- [ ] No errors in logs

### ✅ Functional Testing:
- [ ] **New Company (First Run):**
  - Upload CV
  - Enter JD URL
  - Run analysis
  - Check Phase 6 logs: All keywords loaded from cv_jd_matching.json
  - Check Phase 7 logs: Validation passed
  - Check Phase 8 logs: High Tier 1 integration rate
  - Check output: Recommendations show Tier 1 with soft skills
  
- [ ] **Rerun (Same Company):**
  - Run analysis again
  - Check Phase 6 logs: Keywords filtered as "already in CV"
  - Check Phase 8 logs: Fewer Tier 1 keywords (already integrated)
  - Verify: ATS score improved from first run

- [ ] **Multi-word Keyword Test:**
  - Find a JD with "business processes" keyword
  - Run analysis
  - Check Phase 6 logs: "business processes" in categorized list
  - Check Phase 7 logs: "business processes" classified
  - Verify: "business processes" appears in recommendations

- [ ] **Soft Skills Test:**
  - Find a JD with soft skills (Communication, Teamwork, Problem-solving)
  - Run analysis
  - Check Phase 6 logs: All soft skills → Tier 1
  - Check recommendations: All soft skills in Tier 1 section
  - Verify: NOT in Tier 2

---

## 🐛 TROUBLESHOOTING

### Issue 1: Old Code Still Running
**Symptoms:**
- No PHASE6/PHASE7/PHASE8 logs
- Same issues as before (keywords disappearing)

**Solution:**
```bash
# Force rebuild with no cache
docker compose down
docker compose build --pull --no-cache backend
docker compose up -d

# Verify images
docker images | grep cv-magic
# Should show recent timestamp
```

### Issue 2: Import Errors
**Symptoms:**
- Backend fails to start
- Logs show "ModuleNotFoundError"

**Solution:**
```bash
# Check requirements.txt is up to date
docker compose logs backend | grep "Error"

# Rebuild
docker compose down
docker compose build --pull --no-cache backend
docker compose up -d
```

### Issue 3: No Logs Appearing
**Symptoms:**
- Analysis runs but no PHASE logs

**Solution:**
```bash
# Check if new code path is being used
docker compose logs backend | grep "extract_ats_recommendation_data"

# Should see:
# "🔍 [PHASE6] Starting recommendation data extraction"

# If not, backend might not be using new code - force rebuild
```

### Issue 4: Validation Failing
**Symptoms:**
- Logs show "❌ [PHASE6-CLASSIFY] VALIDATION FAILED"

**Solution:**
- Check logs for details:
  ```bash
  docker compose logs backend | grep -A 5 "VALIDATION FAILED"
  ```
- This indicates keywords are being lost during classification
- File a bug report with the logs

---

## 📝 POST-DEPLOYMENT TASKS

### 1. Monitor First Few Analyses
```bash
# Keep this running during first test
docker compose logs -f backend | grep -E "PHASE6|PHASE7|PHASE8|❌|✅"
```

### 2. Check File Outputs
```bash
# Find latest analysis for a company
find /root/cv-magic/storage/cv-analysis -name "*input_recommendation*.json" -type f -mtime -1

# Check validation in AI recommendation
cat /path/to/*ai_recommendation*.json | jq '.validation'
```

### 3. Compare Before/After
**Before Fix:**
- "business processes" disappeared
- "Communication" in Tier 2
- Tier 1 empty for soft skills

**After Fix:**
- "business processes" in recommendations
- "Communication" in Tier 1
- ALL soft skills in Tier 1
- Validation logs confirm no loss

---

## 🎯 SUCCESS CRITERIA

Deployment is successful if:

1. ✅ **No keywords lost:**
   - Every keyword from cv_jd_matching.json appears in logs
   - Validation passes in Phase 6, 7, 8

2. ✅ **Aggressive Tier 1:**
   - "Communication" → Tier 1
   - "Teamwork" → Tier 1
   - "Problem-solving" → Tier 1
   - "business processes" → Tier 1

3. ✅ **High Integration Rate:**
   - Phase 8 logs show 80%+ integration rate
   - Retry attempts if < 100%
   - Final CV contains most Tier 1 keywords

4. ✅ **Consistent Reruns:**
   - Second run shows fewer missing keywords
   - Keywords from first run filtered as "already in CV"
   - ATS score improves with each run

---

## 📞 NEXT STEPS

1. **Deploy to VPS** (Steps above)
2. **Run verification tests** (Testing Checklist)
3. **Monitor first 3-5 analyses** (Watch logs)
4. **Compare results** (Before/After)
5. **Report success or issues**

---

**Deployment Ready!** 🚀

All code changes are committed, pushed, and documented.
Follow steps above to deploy and verify on VPS.

