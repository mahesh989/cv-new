# Debug Guide: CV Files Not Created on Selection

## 🔍 Problem

When user selects CV from dropdown, these files should be created immediately:
- `user/{email}/cv-analysis/cvs/original/original_cv.txt`
- `user/{email}/cv-analysis/cvs/original/original_cv.json`

But they're NOT being created.

---

## ✅ Debug Logs Added

I've added comprehensive debug logging to help identify where the flow breaks:

### Frontend Logs

**File:** `mobile_app/lib/screens/cv_magic_organized_page.dart`
- Line 497: `🔍 [DEBUG] _onCVSelected called with: {filename}`
- Line 505: `🔍 [DEBUG] Calling APIService.saveCVForAnalysis...`
- Line 507: `✅ [DEBUG] API call succeeded. Response: {response}`
- Line 510: `❌ [DEBUG] API call failed: {error}`

**File:** `mobile_app/lib/services/api_service.dart`
- Line 298: `🔍 [API] saveCVForAnalysis called with filename: {filename}`
- Line 299: `🔍 [API] Endpoint: /cv/save-for-analysis/{filename}`
- Line 306: `✅ [API] saveCVForAnalysis response: {response}`
- Line 309: `❌ [API] saveCVForAnalysis error: {error}`

### Backend Logs

**File:** `backend/app/routes/cv_organized.py`
- Line 69: `🔍 [SAVE_CV] Received request to save CV: {filename}`
- Line 73: `🔍 [SAVE_CV] Getting CV content for: {filename}`
- Line 78: `🔍 [SAVE_CV] CV content result keys: {keys}`
- Line 87: `🔍 [SAVE_CV] Analysis base path: {path}`
- Line 93: `🔍 [SAVE_CV] Original folder path: {path}`
- Line 100: `🔍 [SAVE_CV] TXT file path: {path}`
- Line 101: `🔍 [SAVE_CV] JSON file path: {path}`
- Line 109: `✅ [SAVE_CV] CV saved as text (overwritten): {path}`
- Line 110: `✅ [SAVE_CV] TXT file exists: {bool}, size: {bytes}`
- Line 132: `✅ [SAVE_CV] CV saved as minimal JSON (overwritten): {path}`
- Line 133: `✅ [SAVE_CV] JSON file exists: {bool}, size: {bytes}`

---

## 🧪 Testing Steps

### Step 1: Select CV from Dropdown

1. Open the app
2. Select a CV from the dropdown
3. **Watch the console/logs**

### Step 2: Check Frontend Console

**Expected logs:**
```
🔍 [DEBUG] _onCVSelected called with: my_cv.pdf
🔍 [DEBUG] Calling APIService.saveCVForAnalysis for: my_cv.pdf
🔍 [API] saveCVForAnalysis called with filename: my_cv.pdf
🔍 [API] Endpoint: /cv/save-for-analysis/my_cv.pdf
🔍 [API_SERVICE] Making authenticated call to: /cv/save-for-analysis/my_cv.pdf
🔍 [API_SERVICE] Token available: true
🔍 [API_SERVICE] Response status: 200
✅ [API] saveCVForAnalysis response: {...}
✅ [DEBUG] API call succeeded. Response: {...}
```

**If you see errors:**
- `❌ [DEBUG] API call failed` → Check error details
- `❌ [API] saveCVForAnalysis error` → Check API service logs
- `401 Unauthorized` → Token issue

### Step 3: Check Backend Logs

**Command:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && tail -f logs/backend_logs.txt | grep -E '\[SAVE_CV\]|save-for-analysis'"
```

**Expected logs:**
```
🔍 [SAVE_CV] Received request to save CV: my_cv.pdf for user: rashmi@gmail.com
🔍 [SAVE_CV] Getting CV content for: my_cv.pdf
🔍 [SAVE_CV] CV content result keys: ['content', 'filename']
🔍 [SAVE_CV] CV content length: 12345
🔍 [SAVE_CV] Analysis base path: /app/user/rashmi@gmail.com/cv-analysis
✅ [SAVE_CV] Analysis base directory created/verified: True
🔍 [SAVE_CV] Original folder path: /app/user/rashmi@gmail.com/cv-analysis/cvs/original
✅ [SAVE_CV] Original folder created/verified: True
🔍 [SAVE_CV] TXT file path: /app/user/rashmi@gmail.com/cv-analysis/cvs/original/original_cv.txt
🔍 [SAVE_CV] JSON file path: /app/user/rashmi@gmail.com/cv-analysis/cvs/original/original_cv.json
💾 [SAVE_CV] Writing TXT file: ...
✅ [SAVE_CV] CV saved as text (overwritten): ...
✅ [SAVE_CV] TXT file exists: True, size: 12345 bytes
💾 [SAVE_CV] Creating minimal JSON file: ...
✅ [SAVE_CV] CV saved as minimal JSON (overwritten): ...
✅ [SAVE_CV] JSON file exists: True, size: 5678 bytes
```

**If you see errors:**
- `❌ [SAVE_CV] CV content not found` → CV file doesn't exist in upload folder
- `❌ [SAVE_CV] Failed to write TXT file` → Permission issue
- `❌ [SAVE_CV] Failed to write JSON file` → Permission issue

### Step 4: Verify Files Exist

**Command:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec -T backend ls -la /app/user/rashmi@gmail.com/cv-analysis/cvs/original/"
```

**Expected output:**
```
total 20
drwxr-xr-x 2 root root 4096 Nov 19 14:50 .
drwxr-xr-x 3 root root 4096 Nov 19 14:50 ..
-rw-r--r-- 1 root root 12345 Nov 19 14:50 original_cv.txt
-rw-r--r-- 1 root root  5678 Nov 19 14:50 original_cv.json
```

---

## 🔍 Common Issues & Solutions

### Issue 1: Frontend Not Calling API

**Symptoms:**
- No `🔍 [DEBUG] _onCVSelected` logs
- No `🔍 [API] saveCVForAnalysis` logs

**Solution:**
- Check if `CVSelectionModule` is calling `onCVSelected` callback
- Verify dropdown `onChanged` is connected

### Issue 2: API Call Failing

**Symptoms:**
- `❌ [DEBUG] API call failed`
- `401 Unauthorized` or `404 Not Found`

**Solution:**
- Check authentication token
- Verify endpoint URL is correct
- Check network connectivity

### Issue 3: Backend Not Receiving Request

**Symptoms:**
- Frontend shows success but no backend logs
- No `🔍 [SAVE_CV] Received request` log

**Solution:**
- Check if endpoint is registered in `main.py`
- Verify route prefix is correct
- Check CORS settings

### Issue 4: CV Content Not Found

**Symptoms:**
- `❌ [SAVE_CV] CV content not found for: {filename}`
- `404` error from `CVPreviewService`

**Solution:**
- Verify CV file exists in upload folder
- Check `CVPreviewService.get_cv_content()` implementation
- Verify user has access to the CV

### Issue 5: File Write Permission Error

**Symptoms:**
- `❌ [SAVE_CV] Failed to write TXT file`
- `Permission denied` error

**Solution:**
- Check Docker volume permissions
- Verify user directory exists
- Check file system permissions

---

## 📊 Debug Checklist

After selecting a CV, check:

- [ ] Frontend console shows `🔍 [DEBUG] _onCVSelected called`
- [ ] Frontend console shows `🔍 [API] saveCVForAnalysis called`
- [ ] Frontend console shows `✅ [API] saveCVForAnalysis response`
- [ ] Backend logs show `🔍 [SAVE_CV] Received request`
- [ ] Backend logs show `✅ [SAVE_CV] CV saved as text`
- [ ] Backend logs show `✅ [SAVE_CV] CV saved as minimal JSON`
- [ ] Files exist: `original_cv.txt` and `original_cv.json`
- [ ] Files have content (size > 0)

---

## 🎯 Next Steps

1. **Deploy the updated code** with debug logs
2. **Select a CV from dropdown**
3. **Check frontend console** for debug messages
4. **Check backend logs** for `[SAVE_CV]` messages
5. **Verify files exist** in Docker container
6. **Report findings** - which step fails?

The debug logs will show exactly where the flow breaks! 🔍

