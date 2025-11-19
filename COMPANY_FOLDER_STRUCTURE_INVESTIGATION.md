# Company Folder Structure & File Creation Investigation

## 1. Folder Structure

### Path Template

```
user/{user_email}/cv-analysis/applied_companies/{company_slug}/
```

**Example:**
```
user/rashmi@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/
```

### Path Components

1. **Base Path:** `user/{user_email}/cv-analysis`
   - **File:** `backend/app/utils/user_path_utils.py`
   - **Function:** `get_user_base_path(user_email)` (line 13-48)
   - **Email Sanitization:** 
     - Email is normalized: `user_email.strip().lower()`
     - Supports both `user/{email}/cv-analysis` (preferred) and `user/user_{email}/cv-analysis` (legacy)

2. **Company Folder:** `applied_companies/{company_slug}/`
   - Created under base path
   - Each company gets its own folder

3. **Subfolders (not under company):**
   - `cvs/original/` - Original CV files
   - `cvs/tailored/` - Tailored CV files
   - `saved_jobs/` - Shared saved_jobs.json
   - `uploads/` - Uploaded files

---

## 2. Company Slug Generation

### Function Location

**File:** `backend/app/services/job_extraction_service.py`  
**Function:** `_create_company_slug(company_name: str)` (lines 62-77)

**Also exists in:** `backend/app/services/skill_extraction/result_saver.py` (lines 502-525) - **SAME LOGIC**

### Slug Generation Logic

```python
def _create_company_slug(self, company_name: str) -> str:
    """Create a safe company slug for folder names"""
    if not company_name or company_name.lower() in ['unknown', 'null', '']:
        return f"Unknown_Company_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Remove special characters except alphanumeric, spaces, &, ., -
    company_slug = re.sub(r'[^\w\s&.-]', '', company_name)
    # Replace spaces with underscores
    company_slug = re.sub(r'\s+', '_', company_slug)
    # Remove leading/trailing underscores
    company_slug = company_slug.strip('_')
    # Truncate if too long (max 50 characters)
    if len(company_slug) > 50:
        company_slug = company_slug[:50]
    
    return company_slug
```

### Example Transformations

| Input | Output | Status |
|-------|--------|--------|
| `"Australia for UNHCR"` | `"Australia_for_UNHCR"` | ✅ Correct |
| `"Google LLC"` | `"Google_LLC"` | ✅ Correct |
| `"www.ethicaljobs.com.au"` | `"www_ethicaljobs_com_au"` | ❌ Wrong (URL, not company) |
| `"AT&T Corporation"` | `"AT&T_Corporation"` | ✅ Correct (preserves &) |
| `"Company-Name Inc."` | `"Company-Name_Inc."` | ✅ Correct (preserves - and .) |

### Slug Characteristics

- **Case-sensitive:** Yes (preserves original case)
- **Special chars allowed:** `&`, `.`, `-` (preserved)
- **Max length:** 50 characters (truncated)
- **Invalid chars removed:** Everything except `\w`, spaces, `&`, `.`, `-`
- **Spaces:** Replaced with `_`
- **Consistency:** ✅ Same logic in both `JobExtractionService` and `SkillExtractionResultSaver`

---

## 3. File Creation Flow

### A. Job Info Files (`job_info_*.json`)

**When Created:**
- Endpoint: `/api/job-analysis/extract-and-save` (POST)
- Trigger: User clicks "Analyze & Save Job"

**File Naming Pattern:**
```
job_info_{company_slug}_{timestamp}.json
```

**Example:**
```
job_info_Australia_for_UNHCR_20251119_035954.json
```

**Full Path:**
```
user/{email}/cv-analysis/applied_companies/Australia_for_UNHCR/job_info_Australia_for_UNHCR_20251119_035954.json
```

**Code Location:**
- **File:** `backend/app/services/job_extraction_service.py`
- **Function:** `save_job_analysis()` (lines 569-578)
- **Timestamp Format:** `YYYYMMDD_HHMMSS` (e.g., `20251119_035954`)

**Content:**
```json
{
  "company_name": "Australia for UNHCR",
  "company_slug": "Australia_for_UNHCR",
  "job_title": "Data Analyst",
  "location": "Sydney, Australia",
  "job_url": "https://www.ethicaljobs.com.au/...",
  "extracted_at": "2025-11-19T03:59:54.123456",
  ...
}
```

---

### B. JD Original Files (`jd_original_*.json`)

**When Created:**
- Same endpoint: `/api/job-analysis/extract-and-save`
- Created alongside `job_info_*.json`

**File Naming Pattern:**
```
jd_original_{timestamp}.json
```

**Example:**
```
jd_original_20251119_035954.json
```

**Full Path:**
```
user/{email}/cv-analysis/applied_companies/Australia_for_UNHCR/jd_original_20251119_035954.json
```

**Code Location:**
- **File:** `backend/app/services/job_extraction_service.py`
- **Function:** `save_job_analysis()` (lines 580-590)

**Content:**
```json
{
  "company": "Australia for UNHCR",
  "job_title": "Data Analyst",
  "extracted_at": "2025-11-19 03:59:54",
  "length_chars": 6014,
  "job_url": "https://www.ethicaljobs.com.au/...",
  "text": "[full job description text]"
}
```

---

### C. Skills Analysis Files (`{company_slug}_skills_analysis_{timestamp}.json`)

**When Created:**
- Endpoint: `/api/context-aware-analysis` (POST)
- Trigger: User clicks "Analyze skills" (after initial analysis)

**File Naming Pattern:**
```
{company_slug}_skills_analysis_{timestamp}.json
```

**Example:**
```
Australia_for_UNHCR_skills_analysis_20251119_040215.json
```

**Full Path:**
```
user/{email}/cv-analysis/applied_companies/Australia_for_UNHCR/Australia_for_UNHCR_skills_analysis_20251119_040215.json
```

**Code Location:**
- **File:** `backend/app/services/skill_extraction/result_saver.py`
- **Function:** `save_analysis_results()` (lines 148-179)

**Content:**
```json
{
  "generated": "2025-11-19T04:02:15.123",
  "cv_filename": "latest_cv.pdf",
  "jd_url": "https://www.ethicaljobs.com.au/...",
  "user_id": 1,
  "company": "Australia_for_UNHCR",
  "model_used": "gpt-4o",
  "cv_skills": {...},
  "jd_skills": {...},
  "cv_comprehensive_analysis": "...",
  "jd_comprehensive_analysis": "...",
  "analyze_match_entries": [],
  "preextracted_comparison_entries": []
}
```

---

### D. Other Analysis Files

**JD Analysis Files:**
- **Pattern:** `{company_name}_jd_analysis_{timestamp}.json`
- **Created by:** JD Analyzer service
- **Location:** Same company folder

**CV-JD Matching Files:**
- **Pattern:** `{company_name}_cv_jd_matching_{timestamp}.json`
- **Created by:** CV-JD Matcher service
- **Location:** Same company folder

**Component Analysis:**
- **Stored in:** `{company_slug}_skills_analysis_{timestamp}.json` (appended to existing file)
- **Key:** `component_analysis_entries` array

---

## 4. Endpoint Mapping

| Endpoint | Creates Folder? | Creates Files? | File Names |
|----------|----------------|----------------|------------|
| `/api/job-analysis/extract-and-save` | ✅ Yes (if not exists) | ✅ Yes | `job_info_{slug}_{ts}.json`<br>`jd_original_{ts}.json` |
| `/api/initial-analysis` | ❌ No | ❌ No | (Uses existing files) |
| `/api/context-aware-analysis` | ✅ Yes (if not exists) | ✅ Yes | `{slug}_skills_analysis_{ts}.json` |
| `/api/jd-analysis/analyze-jd/{company}` | ❌ No | ✅ Yes | `{company}_jd_analysis_{ts}.json` |
| CV-JD Matching (internal) | ❌ No | ✅ Yes | `{company}_cv_jd_matching_{ts}.json` |

---

## 5. Code Locations

### 1. Folder Creation

**File:** `backend/app/services/job_extraction_service.py`  
**Function:** `save_job_analysis()` (lines 557-567)

```python
# Create company slug for folder name
company_slug = self._create_company_slug(job_info["company_name"])

# Create company-specific directory under applied_companies subfolder
company_dir = self.cv_analysis_dir / "applied_companies" / company_slug
company_dir.mkdir(parents=True, exist_ok=True)
```

**Also in:** `backend/app/services/skill_extraction/result_saver.py` (lines 83-92)

```python
company_folder = self.base_dir / "applied_companies" / company_slug
company_folder.mkdir(parents=True, exist_ok=True)
```

---

### 2. Slug Generation

**File:** `backend/app/services/job_extraction_service.py`  
**Function:** `_create_company_slug()` (lines 62-77)

**Also in:** `backend/app/services/skill_extraction/result_saver.py` (lines 502-525) - **IDENTICAL LOGIC**

---

### 3. File Saving

#### Job Info File

**File:** `backend/app/services/job_extraction_service.py`  
**Function:** `save_job_analysis()` (lines 569-578)

```python
timestamp = TimestampUtils.get_timestamp()  # Format: YYYYMMDD_HHMMSS
job_info_file = company_dir / f"job_info_{company_slug}_{timestamp}.json"
with open(job_info_file, 'w', encoding='utf-8') as f:
    json.dump(job_info_data, f, indent=2, ensure_ascii=False)
```

#### JD Original File

**File:** `backend/app/services/job_extraction_service.py`  
**Function:** `save_job_analysis()` (lines 580-590)

```python
jd_original_file = company_dir / f"jd_original_{timestamp}.json"
with open(jd_original_file, 'w', encoding='utf-8') as f:
    json.dump({...}, f, ensure_ascii=False, indent=2)
```

#### Skills Analysis File

**File:** `backend/app/services/skill_extraction/result_saver.py`  
**Function:** `save_analysis_results()` (lines 148-179)

```python
timestamp = TimestampUtils.get_timestamp()
filename = f"{company_slug}_skills_analysis_{timestamp}.json"
file_path = company_folder / filename
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
```

---

## 6. Real Example Trace

### Scenario: User clicks "Analyze & Save Job" for "Australia for UNHCR"

**Step 1: API Call**
- **Endpoint:** `POST /api/job-analysis/extract-and-save`
- **Input:**
  ```json
  {
    "job_description": "[JD text]",
    "job_url": "https://www.ethicaljobs.com.au/job/12345"
  }
  ```
- **User:** `rashmi@gmail.com`

**Step 2: Extract Job Info**
- **File:** `backend/app/services/job_extraction_service.py`
- **Function:** `extract_job_information()` (line 79)
- **Result:**
  ```json
  {
    "company_name": "Australia for UNHCR",
    "job_title": "Data Analyst",
    "location": "Sydney, Australia",
    ...
  }
  ```

**Step 3: Create Company Slug**
- **File:** `backend/app/services/job_extraction_service.py`
- **Function:** `_create_company_slug()` (line 554)
- **Input:** `"Australia for UNHCR"`
- **Output:** `"Australia_for_UNHCR"`

**Step 4: Create Folder**
- **Path:** `user/rashmi@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/`
- **Code:** `company_dir.mkdir(parents=True, exist_ok=True)` (line 559)
- **Result:** ✅ Folder created

**Step 5: Create Files**
- **Timestamp:** `20251119_035954` (from `TimestampUtils.get_timestamp()`)
- **Files Created:**
  1. `job_info_Australia_for_UNHCR_20251119_035954.json`
  2. `jd_original_20251119_035954.json`

**Step 6: Return Response**
```json
{
  "success": true,
  "company_slug": "Australia_for_UNHCR",
  "company_name": "Australia for UNHCR",
  "job_title": "Data Analyst",
  "job_info_file": "user/rashmi@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/job_info_Australia_for_UNHCR_20251119_035954.json",
  "jd_original_file": "user/rashmi@gmail.com/cv-analysis/applied_companies/Australia_for_UNHCR/jd_original_20251119_035954.json"
}
```

---

## 7. Potential Issues Found

### ✅ Issue 1: Slug Generation Consistency

**Status:** ✅ **FIXED** - Both services use identical logic

- `JobExtractionService._create_company_slug()` (line 62)
- `SkillExtractionResultSaver._create_company_slug()` (line 502)

**Both use same regex and transformation rules.**

---

### ⚠️ Issue 2: URL vs Company Name Confusion

**Problem:** When company name is extracted from URL (e.g., `"www.ethicaljobs.com.au"`), slug becomes `"www_ethicaljobs_com_au"` instead of actual company name.

**Root Cause:** Frontend extracts company from URL hostname, not from job description.

**Solution:** ✅ **FIXED** - Frontend now stores company info from "Analyze & Save Job" response and uses it in "Analyze skills".

---

### ✅ Issue 3: Folder Conflicts

**Status:** ✅ **HANDLED**

- **If folder exists:** `mkdir(parents=True, exist_ok=True)` - No error, reuses folder
- **User-specific:** Each user has their own `user/{email}/` directory
- **No conflicts:** Different users can have same company name in separate folders

---

### ✅ Issue 4: File Naming Collisions

**Status:** ✅ **HANDLED**

- **Timestamp-based:** All files include `YYYYMMDD_HHMMSS` timestamp
- **Collision probability:** Very low (1 second granularity)
- **If collision:** Files are separate (different timestamps in same second would be rare)

**Example:**
- `job_info_Australia_for_UNHCR_20251119_035954.json`
- `job_info_Australia_for_UNHCR_20251119_035955.json` (1 second later)

---

### ⚠️ Issue 5: Inconsistent File Naming Patterns

**Found Inconsistencies:**

1. **Job Info Files:**
   - Pattern: `job_info_{company_slug}_{timestamp}.json` ✅
   - Example: `job_info_Australia_for_UNHCR_20251119_035954.json`

2. **JD Original Files:**
   - Pattern: `jd_original_{timestamp}.json` ⚠️ (missing company_slug)
   - Example: `jd_original_20251119_035954.json`
   - **Issue:** Harder to identify which company it belongs to without folder context

3. **Skills Analysis Files:**
   - Pattern: `{company_slug}_skills_analysis_{timestamp}.json` ✅
   - Example: `Australia_for_UNHCR_skills_analysis_20251119_040215.json`

**Recommendation:** Consider standardizing to include company_slug in all filenames for easier identification.

---

## Summary

### Folder Structure
```
user/{email}/cv-analysis/
  ├── applied_companies/
  │   └── {company_slug}/
  │       ├── job_info_{slug}_{ts}.json
  │       ├── jd_original_{ts}.json
  │       ├── {slug}_skills_analysis_{ts}.json
  │       ├── {company}_jd_analysis_{ts}.json
  │       └── {company}_cv_jd_matching_{ts}.json
  ├── cvs/
  │   ├── original/
  │   └── tailored/
  ├── saved_jobs/
  └── uploads/
```

### Key Findings

1. ✅ **Slug generation is consistent** across all services
2. ✅ **Folders are user-specific** - no cross-user conflicts
3. ✅ **Timestamp-based naming** prevents collisions
4. ⚠️ **JD original files** don't include company_slug in filename (minor issue)
5. ✅ **All files are JSON** (even `jd_original` despite `.txt` in some patterns)

### File Creation Flow

1. **"Analyze & Save Job"** → Creates folder + `job_info_*.json` + `jd_original_*.json`
2. **"Analyze skills"** → Creates `{slug}_skills_analysis_*.json` (folder already exists)
3. **Analysis pipeline** → Creates `{company}_jd_analysis_*.json` and `{company}_cv_jd_matching_*.json`

---

**Investigation Complete** ✅

