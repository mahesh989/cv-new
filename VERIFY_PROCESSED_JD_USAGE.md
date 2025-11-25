# Quick Verification Guide: Processed JD Usage

## 🎯 **Goal**: Verify processed JD is actually being used during JD analysis

---

## ✅ **Step 1: Confirm Processed JD Files Exist**

```bash
# Check processed JD files
docker exec cv_backend find /app/user -name 'jd_processed_*.json' -type f | head -5
```

**Expected**: Should see files like `jd_processed_20251125_111457.json`

---

## 🚀 **Step 2: Trigger JD Analysis**

### **Method A: Via Frontend**
1. Go to company page: "Australia for UNHCR"
2. Click **"Analyze"** or **"JD Analysis"** button
3. Wait for analysis to complete

### **Method B: Via API** (if you have auth token)
```bash
curl -X POST http://localhost:8000/api/jd-analysis/analyze-jd/Australia_for_UNHCR \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Method C: Via Pipeline** (automatic)
- The pipeline should trigger JD analysis automatically
- Check logs after running preliminary analysis

---

## 🔍 **Step 3: Check Logs for Verification**

```bash
# Check for processed JD usage logs
docker logs cv_backend --tail 200 | grep -E "JD_ANALYZER.*PROCESSED|JD_ANALYZER.*LEGACY|JD_ANALYZER.*Analyzing"
```

### **✅ Success Indicators:**

```
🔍 [JD_ANALYZER] Attempting to use processed JD for Australia_for_UNHCR
✅ [JD_ANALYZER] ✅ Using PROCESSED JD for Australia_for_UNHCR | Length: 3153 chars
🔄 [JD_ANALYZER] Analyzing JD for Australia_for_UNHCR (force_refresh=False)
```

### **⚠️ Fallback Indicators:**

```
📄 [JD_ANALYZER] Processed JD not available for Australia_for_UNHCR, falling back to LEGACY file
📄 [JD_ANALYZER] Using LEGACY (original) JD file | Path: jd_original_*.json
```

---

## 📊 **Step 4: Compare Results**

### **If Processed JD is Used:**
- JD text length: ~3153 chars (processed)
- Faster analysis (fewer tokens)
- Better keyword extraction (cleaner input)

### **If Legacy JD is Used:**
- JD text length: ~6014 chars (original)
- Slower analysis (more tokens)
- May include noise (salary, benefits, etc.)

---

## 🎯 **Quick Test Script**

Save this as `test_jd_analysis.sh`:

```bash
#!/bin/bash

echo "🔍 Checking processed JD files..."
docker exec cv_backend find /app/user -name 'jd_processed_*.json' -type f | head -3

echo ""
echo "📊 Checking recent JD analysis logs..."
docker logs cv_backend --tail 500 | grep -E "JD_ANALYZER.*PROCESSED|JD_ANALYZER.*LEGACY" | tail -5

echo ""
echo "✅ If you see 'Using PROCESSED JD', it's working!"
echo "⚠️ If you see 'Using LEGACY', processed JD may not be available or there's an issue"
```

---

## 🔧 **Troubleshooting**

### **If processed JD is not being used:**

1. **Check if processed JD file exists:**
   ```bash
   docker exec cv_backend ls -la /app/user/*/cv-analysis/applied_companies/Australia_for_UNHCR/jd_processed_*.json
   ```

2. **Check if company name matches:**
   - Processed JD file: `Australia_for_UNHCR`
   - Analysis request: Must use exact same company name

3. **Check user email:**
   - Ensure `user_email` is passed correctly to `JDAnalyzer`

4. **Check logs for errors:**
   ```bash
   docker logs cv_backend --tail 200 | grep -i "error\|warning" | grep -i "jd"
   ```

---

## ✅ **Expected Outcome**

After triggering JD analysis, you should see:

1. ✅ Log message: `✅ [JD_ANALYZER] ✅ Using PROCESSED JD`
2. ✅ Analysis completes successfully
3. ✅ Better keyword extraction (from cleaner JD)
4. ✅ Faster processing (47% fewer tokens)

---

**Status**: Ready to test! 🚀

