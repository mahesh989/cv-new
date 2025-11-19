# Manual Test Guide: Australia for UNHCR Data Analyst

## 🎯 Test Objective

Test the company folder creation and analysis flow for:
- **Job URL:** https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst
- **Company:** Australia for UNHCR
- **Position:** Data Analyst

---

## 📋 Pre-Test Checklist

1. ✅ **Deploy latest code** (with folder creation fixes)
   ```bash
   cd ~/cv-new/cv-magic-app
   ./deploy.sh
   # Select option 1: Full Deployment
   ```

2. ✅ **Clear logs** (optional, for clean test)
   ```bash
   ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && > logs/backend_logs.txt"
   ```

3. ✅ **Get authentication token**
   - Use the mobile app to get a valid token
   - Or use the API login endpoint

---

## 🧪 Test Steps

### Step 1: Trigger Analysis via API

**Option A: Using the test script**
```bash
cd /Users/mahesh/Documents/Github/cv-new
# Edit test_manual_analysis.py and set AUTH_TOKEN
python3 test_manual_analysis.py
```

**Option B: Using curl**
```bash
curl -X POST https://cvagent.duckdns.org/api/preliminary-analysis \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_filename": "original_cv.json",
    "jd_text": "PASTE_JD_TEXT_HERE",
    "jd_url": "https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst",
    "config_name": "default"
  }'
```

**Option C: Using the mobile app**
1. Open the CV Magic app
2. Select a CV
3. Paste the JD URL: `https://www.ethicaljobs.com.au/members/australiaforunhcr/data-analyst`
4. Click "Analyze Match"

---

### Step 2: Monitor Logs in Real-Time

**In a separate terminal, watch logs:**
```bash
ssh ubuntu@cvagent.duckdns.org "tail -f ~/cv-new/cv-magic-app/logs/backend_logs.txt | grep -E '\[FOLDER\]|\[JD_ANALYSIS\]|Extracted company|Australia|UNHCR'"
```

**Expected log sequence:**
```
🏢 Extracted company name: Australia_for_UNHCR
✅ [FOLDER] Company folder created/verified: /app/user/.../applied_companies/Australia_for_UNHCR
   📁 Full path: /app/user/.../applied_companies/Australia_for_UNHCR
🏢 [JD_ANALYSIS] Creating folder for company: Australia for UNHCR -> Australia_for_UNHCR
✅ [JD_ANALYSIS] Company folder created successfully: /app/user/.../applied_companies/Australia_for_UNHCR
   📁 Full path: /app/user/.../applied_companies/Australia_for_UNHCR
```

---

### Step 3: Verify Folder Creation

**Check folder exists:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec -T backend ls -la /app/user/chunem@gmail.com/cv-analysis/applied_companies/ | grep -i 'australia\|unhcr'"
```

**Expected output:**
```
drwxr-xr-x 2 root root 4096 Nov 18 08:39 Australia_for_UNHCR
```

**List files in folder:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec -T backend ls -la /app/user/chunem@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/"
```

**Expected files:**
```
-rw-r--r-- 1 root root 1234 Nov 18 08:40 jd_original_20251118_084000.json
-rw-r--r-- 1 root root 5678 Nov 18 08:40 job_info_Australia_for_UNHCR_20251118_084000.json
-rw-r--r-- 1 root root 9012 Nov 18 08:41 Australia_for_UNHCR_skills_analysis_20251118_084100.json
```

---

### Step 4: Verify Analysis Files

**Check for key analysis files:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec -T backend find /app/user/chunem@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/ -type f -name '*.json' | head -10"
```

**Expected files:**
- `jd_original_*.json` - Original JD text
- `job_info_*.json` - Extracted job metadata
- `*_skills_analysis_*.json` - Skills analysis results
- `*_cv_jd_matching_*.json` - CV-JD matching results
- `*_input_recommendation_*.json` - Input for AI recommendations
- `*_ai_recommendation_*.json` - AI recommendations

---

## ✅ Success Criteria

1. **✅ Folder Creation**
   - Company folder is created immediately after company name extraction
   - Logs show `✅ [FOLDER] Company folder created/verified`
   - Folder exists in Docker: `/app/user/{email}/cv-analysis/applied_companies/Australia_for_UNHCR/`

2. **✅ Company Name Extraction**
   - Logs show: `🏢 Extracted company name: Australia_for_UNHCR`
   - Company name is correctly normalized (spaces → underscores)

3. **✅ JD Analysis**
   - `jd_original_*.json` file is created
   - `job_info_*.json` file is created with correct metadata
   - Logs show: `✅ [JD_ANALYSIS] Company folder created successfully`

4. **✅ Analysis Files**
   - Skills analysis file is created
   - CV-JD matching file is created
   - All files are saved in the correct company folder

---

## 🔍 Troubleshooting

### Issue: Folder not created

**Check logs:**
```bash
ssh ubuntu@cvagent.duckdns.org "grep -E 'FOLDER|Error creating company folder' ~/cv-new/cv-magic-app/logs/backend_logs.txt | tail -20"
```

**Check permissions:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec -T backend ls -la /app/user/chunem@gmail.com/cv-analysis/applied_companies/"
```

### Issue: Wrong company name

**Check extraction:**
```bash
ssh ubuntu@cvagent.duckdns.org "grep 'Extracted company name' ~/cv-new/cv-magic-app/logs/backend_logs.txt | tail -5"
```

**Check existing folders:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec -T backend ls /app/user/chunem@gmail.com/cv-analysis/applied_companies/"
```

### Issue: Analysis fails

**Check full error logs:**
```bash
ssh ubuntu@cvagent.duckdns.org "tail -100 ~/cv-new/cv-magic-app/logs/backend_logs.txt | grep -A 10 -B 10 ERROR"
```

---

## 📊 Expected Results

### Folder Structure
```
/app/user/chunem@gmail.com/cv-analysis/
└── applied_companies/
    └── Australia_for_UNHCR/
        ├── jd_original_20251118_084000.json
        ├── job_info_Australia_for_UNHCR_20251118_084000.json
        ├── Australia_for_UNHCR_skills_analysis_20251118_084100.json
        ├── Australia_for_UNHCR_cv_jd_matching_20251118_084200.json
        ├── Australia_for_UNHCR_input_recommendation_20251118_084300.json
        └── Australia_for_UNHCR_ai_recommendation_20251118_084400.json
```

### Log Sequence
1. `🏢 Extracted company name: Australia_for_UNHCR`
2. `✅ [FOLDER] Company folder created/verified: .../Australia_for_UNHCR`
3. `🏢 [JD_ANALYSIS] Creating folder for company: Australia for UNHCR -> Australia_for_UNHCR`
4. `✅ [JD_ANALYSIS] Company folder created successfully: .../Australia_for_UNHCR`
5. `💾 [PIPELINE] JD JSON saved to: .../jd_original_*.json`
6. `💾 [PIPELINE] Job info saved to: .../job_info_*.json`

---

## 📝 Notes

- Company name should be normalized: `Australia for UNHCR` → `Australia_for_UNHCR`
- Folder creation happens **immediately** after company name extraction
- All subsequent files are saved to this folder
- If folder already exists, `mkdir(parents=True, exist_ok=True)` won't fail
- Logs are saved in real-time to `logs/backend_logs.txt`

---

## 🎯 Next Steps After Test

1. **Verify folder creation worked** ✅
2. **Check all analysis files were created** ✅
3. **Review logs for any errors** ✅
4. **Test with another company** (optional)
5. **Deploy to production** (if test successful)

