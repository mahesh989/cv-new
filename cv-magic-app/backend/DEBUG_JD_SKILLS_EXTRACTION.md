# Debug Guide: JD Skills Extraction from jd_analysis.required_skills

## How to Check Logs

### Browser Console (Frontend Logs)

1. **Open Chrome DevTools**: Press `F12` or right-click → Inspect
2. **Go to Console tab**
3. **Filter logs**: Type `INITIAL_ANALYSIS` in the filter box
4. **Look for these log messages**:

```
🔍 [INITIAL_ANALYSIS] ====== PARSING JD SKILLS ======
   JSON keys received: [...]
   jd_analysis present: true/false
   jd_analysis keys: [...]
   required_skills present: true/false
   ...
```

### What to Look For

#### ✅ Success Case:
```
🔍 [INITIAL_ANALYSIS] ====== PARSING JD SKILLS ======
   JSON keys received: [cv_skills, jd_skills, jd_analysis, job_info, cv_jd_matching]
   jd_analysis present: true
   jd_analysis keys: [experience_years, required_skills, preferred_skills, ...]
   required_skills present: true
   required_skills keys: [technical, soft_skills, domain_knowledge, experience]
   technical type: List<dynamic>
   technical value: [SQL, Power BI, Excel, ...]
   ✅ [INITIAL_ANALYSIS] Using jd_analysis.required_skills for side-by-side display
   Technical: X skills
   Soft: Y skills
   Domain: Z skills
```

#### ⚠️ Fallback Case:
```
⚠️ [INITIAL_ANALYSIS] jd_analysis.required_skills is null
   Using jd_skills fallback
   jd_skills keys: [technical_skills, soft_skills, domain_keywords]
```

## Common Issues

### Issue 1: `required_skills present: false`
**Cause**: `jd_analysis.required_skills` is null or missing
**Check**:
- Look at `jd_analysis keys:` - does it include `required_skills`?
- Check API response in Network tab - does `results.jd_analysis.required_skills` exist?

### Issue 2: `required_skills is empty map`
**Cause**: `required_skills` exists but is `{}`
**Check**:
- Backend might not have populated it
- Check backend logs for JD analysis errors

### Issue 3: Lists are empty
**Cause**: `required_skills.technical` etc. are empty arrays
**Check**:
- Look at `technical value:` in logs
- Check if backend JD analysis actually extracted skills

### Issue 4: Type mismatch
**Cause**: Data type is not List
**Check**:
- Look at `technical type:` in logs
- Should be `List<dynamic>` or `JsArray`
- If it's something else, there's a parsing issue

## Next Steps

1. **Share the console logs** - Copy all lines starting with `🔍 [INITIAL_ANALYSIS]`
2. **Check Network tab** - Inspect the `/api/initial-analysis` response
3. **Verify API response** - Check if `results.jd_analysis.required_skills` exists and has data

## Quick Test

Run this in browser console after initial analysis:
```javascript
// Get the last API response
fetch('/api/initial-analysis', {method: 'POST', ...})
  .then(r => r.json())
  .then(data => {
    console.log('jd_analysis:', data.results.jd_analysis);
    console.log('required_skills:', data.results.jd_analysis?.required_skills);
    console.log('jd_skills:', data.results.jd_skills);
  });
```

