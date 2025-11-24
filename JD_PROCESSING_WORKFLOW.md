# JD Processing Workflow

## Overview

This document explains **when** processed JD is created and **how** it's used throughout the analysis pipeline.

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER SUBMITS JD (via API endpoint)                          │
│    - /preliminary-analysis                                      │
│    - /initial-analysis                                          │
│    - /context-aware-analysis                                    │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. JD SAVED TO FILE                                             │
│    Location: user/applied_companies/{company}/jd_original.json │
│    Content: {"text": "raw JD text", "job_url": "...", ...}     │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. PROCESSED JD TRIGGERED (Automatic)                           │
│    ✅ Check if jd_processed.json exists                         │
│    ✅ If NOT exists → Process JD using AI                       │
│    ✅ Save to: jd_processed_{timestamp}.json                    │
│    ⚠️  If processing fails → Fallback to original JD            │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. PROCESSED JD USED IN ALL ANALYSIS STEPS                      │
│    ✅ JD Analysis (keyword extraction)                          │
│    ✅ CV-JD Matching                                            │
│    ✅ Skills Analysis                                            │
│    ✅ Tailored CV Generation                                     │
│    ✅ ATS Analysis                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📍 Trigger Points (When Processed JD is Created)

### **Trigger 1: Preliminary Analysis Endpoint**
**File**: `app/routes/skills_analysis.py` (line ~1705)

```python
# When JD is saved
jd_file = company_dir / f"jd_original_{timestamp}.json"
with open(jd_file, 'w', encoding='utf-8') as f:
    json.dump({"text": jd_text, ...}, f, ...)

# ⭐ ADD HERE: Process JD after saving
from app.services.jd_processing_service import get_jd_processing_service
jd_service = get_jd_processing_service(user_email)
await jd_service.process_jd_if_needed(
    company_name=company_name,
    jd_text=jd_text,
    job_title=job_title,
    job_url=jd_url,
    user=user
)
```

### **Trigger 2: Job Extraction Service**
**File**: `app/services/job_extraction_service.py` (line ~580)

```python
# When JD is saved
jd_original_file = company_dir / f"jd_original_{timestamp}.json"
with open(jd_original_file, 'w', encoding='utf-8') as f:
    json.dump({...}, f, ...)

# ⭐ ADD HERE: Process JD after saving
from app.services.jd_processing_service import get_jd_processing_service
jd_service = get_jd_processing_service(user.email)
await jd_service.process_jd_if_needed(
    company_name=company_slug,
    jd_text=job_description,
    job_title=job_info.get('job_title'),
    job_url=job_url,
    user=user
)
```

### **Trigger 3: Context-Aware Analysis Pipeline**
**File**: `app/services/context_aware_analysis_pipeline.py`

When JD is first encountered in the pipeline, process it automatically.

---

## 🔍 Usage Points (How Processed JD Text is Used)

### **Usage 1: JD Analysis (Keyword Extraction)**
**File**: `app/services/jd_analysis/jd_analyzer.py`

**Current Flow**:
```python
def _read_jd_file(self, file_path):
    # Reads jd_original.json
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get('text', '')
```

**With Processed JD**:
```python
def _read_jd_file(self, file_path):
    # ⭐ Try processed JD first
    from app.services.jd_processing_service import get_jd_processing_service
    company_name = self._extract_company_name_from_path(file_path)
    if company_name:
        jd_service = get_jd_processing_service(self.user_email)
        processed_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
        if processed_text:
            return processed_text  # ✅ Use processed JD
    
    # Fallback to original
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get('text', '')
```

**Why**: Processed JD removes noise (salary, benefits, contact info) so keyword extraction focuses on actual requirements.

---

### **Usage 2: CV-JD Matching**
**File**: `app/services/cv_jd_matching/cv_jd_matcher.py`

**Current Flow**:
```python
async def match_cv_against_jd(self, company_name, ...):
    # Uses JD analysis keywords
    jd_analysis = self._read_jd_analysis(company_name)
    required_keywords = jd_analysis['required_keywords']
    # Match CV against keywords
```

**With Processed JD**:
```python
async def match_cv_against_jd(self, company_name, ...):
    # ⭐ Get processed JD text for better context
    from app.services.jd_processing_service import get_jd_processing_service
    jd_service = get_jd_processing_service(self.user_email)
    jd_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
    
    if jd_text:
        # Use processed JD for smarter matching
        # Processed JD has organized sections making matching more accurate
    else:
        # Fallback to JD analysis keywords
        jd_analysis = self._read_jd_analysis(company_name)
```

**Why**: Processed JD's organized structure (TECHNICAL REQUIREMENTS, KEY RESPONSIBILITIES) helps match CV content more accurately.

---

### **Usage 3: Skills Analysis**
**File**: `app/routes/skills_analysis.py` (line ~3073)

**Current Flow**:
```python
async def _run_pipeline(cname, token_data):
    # Load JD text from jd_original.json
    jd_text_for_recording = jd_data.get('jd_text', '')
    # Use JD text for skills extraction
    jd_structured_prompt = get_skill_prompt('combined_structured', text=jd_text_for_recording, ...)
```

**With Processed JD**:
```python
async def _run_pipeline(cname, token_data):
    # ⭐ Get processed JD text
    from app.services.jd_processing_service import get_jd_processing_service
    jd_service = get_jd_processing_service(user_email)
    jd_text = jd_service.get_jd_text_for_ai(cname, prefer_processed=True)
    
    if not jd_text:
        # Fallback to original
        jd_text = jd_data.get('jd_text', '')
    
    # Use processed JD for skills extraction
    jd_structured_prompt = get_skill_prompt('combined_structured', text=jd_text, ...)
```

**Why**: Processed JD's structured sections (TECHNICAL REQUIREMENTS, SOFT SKILLS) make skill extraction more precise.

---

### **Usage 4: Tailored CV Generation**
**File**: `app/tailored_cv/services/cv_tailoring_service.py`

**Current Flow**:
```python
async def _generate_tailored_cv(self, original_cv, recommendations, ...):
    # Uses JD from recommendations object
    jd_text = recommendations.job_description  # Raw JD text
    # Generate tailored CV
```

**With Processed JD**:
```python
async def _generate_tailored_cv(self, original_cv, recommendations, ...):
    # ⭐ Get processed JD text
    from app.services.jd_processing_service import get_jd_processing_service
    jd_service = get_jd_processing_service(self.user_email)
    company_name = recommendations.company
    jd_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
    
    if not jd_text:
        # Fallback to recommendations JD
        jd_text = recommendations.job_description
    
    # Use processed JD in prompt for better tailoring
    prompt = f"... JD: {jd_text} ..."
```

**Why**: Processed JD's organized structure helps AI focus on relevant requirements when tailoring CV.

---

### **Usage 5: ATS Analysis**
**File**: `app/services/ats_recommendation_service.py`

**Current Flow**:
```python
def analyze_cv_job_fit(self, cv_content, job_description, ...):
    # Uses raw job_description text
    # Analyzes fit
```

**With Processed JD**:
```python
def analyze_cv_job_fit(self, cv_content, job_description, company_name, ...):
    # ⭐ Get processed JD text
    from app.services.jd_processing_service import get_jd_processing_service
    jd_service = get_jd_processing_service(self.user_email)
    processed_jd_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
    
    if processed_jd_text:
        job_description = processed_jd_text  # ✅ Use processed JD
    
    # Analyze fit with processed JD
```

**Why**: Processed JD removes irrelevant content, making ATS scoring more accurate.

---

## 🔄 Complete Flow Example

### **Scenario: User submits JD for analysis**

1. **User calls `/preliminary-analysis`** with JD text
   ```json
   {
     "jd_url": "https://...",
     "jd_text": "Data Analyst... [raw JD with salary, benefits, etc.]",
     "company": "Australia_for_UNHCR"
   }
   ```

2. **JD Saved** (line ~1705 in `skills_analysis.py`)
   ```python
   # Save to: user/applied_companies/Australia_for_UNHCR/jd_original_{timestamp}.json
   jd_file = company_dir / f"jd_original_{timestamp}.json"
   with open(jd_file, 'w') as f:
       json.dump({"text": jd_text, ...}, f)
   ```

3. **Processed JD Triggered** (NEW - to be added)
   ```python
   # After saving jd_original
   jd_service = get_jd_processing_service(user_email)
   await jd_service.process_jd_if_needed(
       company_name="Australia_for_UNHCR",
       jd_text=jd_text,
       job_title="Data Analyst",
       job_url=jd_url,
       user=user
   )
   # Creates: jd_processed_{timestamp}.json with structured sections
   ```

4. **JD Analysis Uses Processed JD** (when `analyze_jd_text()` is called)
   ```python
   # In jd_analyzer.py
   jd_text = jd_service.get_jd_text_for_ai("Australia_for_UNHCR", prefer_processed=True)
   # Returns processed JD text (noise removed, organized)
   result = await analyzer.analyze_jd_text(jd_text)  # ✅ Better keyword extraction
   ```

5. **CV-JD Matching Uses Processed JD**
   ```python
   # In cv_jd_matcher.py
   jd_text = jd_service.get_jd_text_for_ai("Australia_for_UNHCR", prefer_processed=True)
   # Match CV against processed JD (more accurate)
   ```

6. **Skills Analysis Uses Processed JD**
   ```python
   # In skills_analysis.py
   jd_text = jd_service.get_jd_text_for_ai("Australia_for_UNHCR", prefer_processed=True)
   # Extract skills from processed JD (better precision)
   ```

7. **Tailored CV Uses Processed JD**
   ```python
   # In cv_tailoring_service.py
   jd_text = jd_service.get_jd_text_for_ai("Australia_for_UNHCR", prefer_processed=True)
   # Generate tailored CV using processed JD (better alignment)
   ```

---

## 🎯 Key Benefits

1. **Automatic Processing**: Processed JD is created automatically when JD is saved
2. **Transparent Usage**: All analysis steps automatically use processed JD if available
3. **Fallback Safety**: If processed JD doesn't exist or processing fails, falls back to original JD
4. **Better AI Performance**: Processed JD removes noise and organizes content, improving all AI operations
5. **No Breaking Changes**: Existing code continues to work (backward compatible)

---

## 📝 Implementation Checklist

- [ ] Add `process_jd_if_needed()` call after JD is saved in `preliminary-analysis` endpoint
- [ ] Add `process_jd_if_needed()` call after JD is saved in `job_extraction_service.py`
- [ ] Update `jd_analyzer.py` to use `get_jd_text_for_ai()`
- [ ] Update `cv_jd_matcher.py` to use `get_jd_text_for_ai()`
- [ ] Update `skills_analysis.py` to use `get_jd_text_for_ai()`
- [ ] Update `cv_tailoring_service.py` to use `get_jd_text_for_ai()`
- [ ] Update ATS analysis services to use `get_jd_text_for_ai()`
- [ ] Test with existing JDs (should fallback to original)
- [ ] Test with new JDs (should use processed JD)

---

## 🔍 Debugging

**Check if processed JD exists**:
```python
from app.services.jd_processing_service import get_jd_processing_service
jd_service = get_jd_processing_service(user_email)
has_processed = jd_service.has_processed_jd("Australia_for_UNHCR")
print(f"Processed JD exists: {has_processed}")
```

**View processed JD structure**:
```python
processed_jd = jd_service.get_processed_jd("Australia_for_UNHCR")
print(json.dumps(processed_jd, indent=2))
```

**Get processed JD as text**:
```python
jd_text = jd_service.get_jd_text_for_ai("Australia_for_UNHCR", prefer_processed=True)
print(jd_text)  # Organized, noise-free JD text
```

