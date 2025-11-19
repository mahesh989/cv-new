# CV Save Debug Guide

## Current Implementation Status

### ✅ Code is Already in Place

1. **Frontend (`cv_magic_organized_page.dart`):**
   - ✅ `_onCVSelected()` has debug logs (lines 497-518)
   - ✅ Calls `APIService.saveCVForAnalysis(filename)`
   - ✅ Error handling with detailed logs

2. **API Service (`api_service.dart`):**
   - ✅ `saveCVForAnalysis()` has debug logs (lines 297-311)
   - ✅ Endpoint: `/cv/save-for-analysis/$filename`
   - ✅ Full URL: `https://cvagent.duckdns.org/api/cv/save-for-analysis/{filename}`

3. **Backend (`cv_organized.py`):**
   - ✅ Endpoint exists: `POST /api/cv/save-for-analysis/{filename}` (line 66)
   - ✅ Router registered in `main.py` (line 290)
   - ✅ Extensive logging throughout (lines 69-213)
   - ✅ Creates both `original_cv.txt` and `original_cv.json` (lines 97-136)

## Path Verification

**Frontend Call:**
```
Endpoint: /cv/save-for-analysis/{filename}
Full URL: https://cvagent.duckdns.org/api/cv/save-for-analysis/{filename}
```

**Backend Route:**
```
Router prefix: /api/cv
Route: /save-for-analysis/{filename}
Full path: /api/cv/save-for-analysis/{filename}
```

✅ **Paths match correctly!**

## Debug Checklist

### Step 1: Check Frontend Console

When you select a CV from dropdown, you should see:

```
🔍 [DEBUG] _onCVSelected called with: {filename}
🔍 [DEBUG] Calling APIService.saveCVForAnalysis for: {filename}
🔍 [API] saveCVForAnalysis called with filename: {filename}
🔍 [API] Endpoint: /cv/save-for-analysis/{filename}
🔍 [API_SERVICE] Making authenticated call to: /cv/save-for-analysis/{filename}
🔍 [API_SERVICE] Token available: true/false
🔍 [API_SERVICE] Response status: 200/404/500
```

**What to check:**
- [ ] Is `_onCVSelected` being called?
- [ ] Is the filename correct?
- [ ] Is the token available?
- [ ] What's the response status code?
- [ ] What's the response body?

### Step 2: Check Backend Logs

**Command:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose logs --tail=50 backend | grep -i 'SAVE_CV'"
```

**Expected logs:**
```
🔍 [SAVE_CV] Received request to save CV: {filename} for user: {email}
🔍 [SAVE_CV] Getting CV content for: {filename}
🔍 [SAVE_CV] CV content result keys: [...]
🔍 [SAVE_CV] CV content length: {number}
🔍 [SAVE_CV] Analysis base path: {path}
✅ [SAVE_CV] Analysis base directory created/verified: True
🔍 [SAVE_CV] Original folder path: {path}
✅ [SAVE_CV] Original folder created/verified: True
💾 [SAVE_CV] Writing TXT file: {path}
✅ [SAVE_CV] CV saved as text (overwritten): {path}
✅ [SAVE_CV] TXT file exists: True, size: {bytes} bytes
💾 [SAVE_CV] Creating minimal JSON file: {path}
✅ [SAVE_CV] CV saved as minimal JSON (overwritten): {path}
✅ [SAVE_CV] JSON file exists: True, size: {bytes} bytes
```

**What to check:**
- [ ] Is the request reaching the backend?
- [ ] Is CV content found?
- [ ] Are folders being created?
- [ ] Are files being written?
- [ ] Any errors in the logs?

### Step 3: Check File System

**Command:**
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec backend ls -la /app/user/{email}/cv-analysis/cvs/original/"
```

**Expected output:**
```
-rw-r--r-- 1 root root {size} original_cv.txt
-rw-r--r-- 1 root root {size} original_cv.json
```

**What to check:**
- [ ] Do the files exist?
- [ ] Are file sizes > 0?
- [ ] Are permissions correct?

### Step 4: Test Endpoint Directly

**Command:**
```bash
# Get your auth token first
TOKEN="your_token_here"
FILENAME="test_cv.pdf"

curl -X POST "https://cvagent.duckdns.org/api/cv/save-for-analysis/$FILENAME" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -v
```

**What to check:**
- [ ] What's the HTTP status code?
- [ ] What's the response body?
- [ ] Any error messages?

## Common Issues & Solutions

### Issue 1: 401 Unauthorized

**Symptoms:**
- Frontend: `Response status: 401`
- Backend: No logs appear

**Solution:**
- Check if token is valid
- Check if token is being sent in headers
- Verify authentication middleware

### Issue 2: 404 Not Found

**Symptoms:**
- Frontend: `Response status: 404`
- Backend: `CV content not found for: {filename}`

**Solution:**
- Verify CV file exists in user's upload folder
- Check `CVPreviewService.get_cv_content()` can find the file
- Verify filename matches exactly

### Issue 3: 500 Internal Server Error

**Symptoms:**
- Frontend: `Response status: 500`
- Backend: Error in logs with traceback

**Solution:**
- Check backend logs for full error
- Verify file system permissions
- Check if directories can be created

### Issue 4: Files Not Created

**Symptoms:**
- Backend logs show success
- But files don't exist on disk

**Solution:**
- Check file system permissions
- Verify Docker volume mounts
- Check if path is correct (relative vs absolute)

## Next Steps

1. **Run the debug checklist above**
2. **Report findings:**
   - Frontend console logs
   - Backend logs
   - File system check
   - curl test results

3. **Based on findings, we'll:**
   - Fix authentication if needed
   - Fix file path issues
   - Fix permissions
   - Add more error handling

## Quick Test Script

```bash
#!/bin/bash
# Quick test script

EMAIL="your_email@example.com"
FILENAME="test_cv.pdf"

echo "1. Checking backend logs..."
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose logs --tail=100 backend | grep -i 'SAVE_CV' | tail -20"

echo ""
echo "2. Checking if files exist..."
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec backend ls -la /app/user/$EMAIL/cv-analysis/cvs/original/ 2>&1"

echo ""
echo "3. Checking file contents..."
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose exec backend head -5 /app/user/$EMAIL/cv-analysis/cvs/original/original_cv.txt 2>&1"
```

## Expected Behavior

When user selects CV from dropdown:

1. ✅ Frontend calls API
2. ✅ Backend receives request
3. ✅ Backend gets CV content
4. ✅ Backend creates folders
5. ✅ Backend writes `original_cv.txt`
6. ✅ Backend writes `original_cv.json`
7. ✅ Backend returns success response
8. ✅ Frontend shows success message

**All steps should complete in < 1 second.**

