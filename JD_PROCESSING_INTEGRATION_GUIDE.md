# JD Processing Integration Guide

This guide shows where and how to integrate the processed JD (structured JSON format) into your application without losing existing functionality.

## Overview

The `JDProcessingService` processes job descriptions into structured JSON format with organized sections. This processed JD is optimized for AI operations (skill analysis, CV matching, tailored CV generation) while maintaining backward compatibility with original JD text.

## Key Integration Points

### 1. **JD Analysis** (`app/services/jd_analysis/jd_analyzer.py`)

**Current**: Reads JD from `jd_original.json` file  
**Change**: Use processed JD if available, fallback to original

**Location**: `_read_jd_file()` method (line ~244)

```python
def _read_jd_file(self, file_path: Union[str, Path]) -> str:
    """Read job description from file"""
    # ADD: Try processed JD first
    from app.services.jd_processing_service import get_jd_processing_service
    
    # Extract company name from file path if possible
    company_name = self._extract_company_name_from_path(file_path)
    if company_name:
        jd_service = get_jd_processing_service(self.user_email)
        processed_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
        if processed_text:
            return processed_text
    
    # Fallback to original file reading logic
    path = Path(file_path)
    # ... existing code ...
```

### 2. **CV-JD Matching** (`app/services/cv_jd_matching/cv_jd_matcher.py`)

**Current**: Uses JD analysis results (keywords)  
**Change**: Use processed JD text for better matching context

**Location**: `match_cv_against_jd()` method

```python
async def match_cv_against_jd(self, company_name: str, ...):
    """Match CV against JD"""
    # ADD: Get processed JD text for better matching
    from app.services.jd_processing_service import get_jd_processing_service
    
    jd_service = get_jd_processing_service(self.user_email)
    jd_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
    
    if not jd_text:
        # Fallback to original JD analysis
        jd_analysis = self._read_jd_analysis(company_name)
        # ... existing code ...
```

### 3. **Skills Analysis** (`app/routes/skills_analysis.py`)

**Current**: Uses `jd_text` parameter directly  
**Change**: Process JD when saved, use processed JD for analysis

**Location**: `_run_pipeline()` function (line ~643)

```python
async def _run_pipeline(cname: str, token_data=None):
    """Main pipeline for skills analysis"""
    # ... existing code to load JD ...
    
    # ADD: Process JD if not already processed
    from app.services.jd_processing_service import get_jd_processing_service
    from app.core.dependencies import get_current_user
    
    if jd_text_for_recording:
        jd_service = get_jd_processing_service(user_email)
        user = await get_current_user(token_data)  # Get user object
        
        # Process JD asynchronously (non-blocking)
        await jd_service.process_jd_if_needed(
            company_name=cname,
            jd_text=jd_text_for_recording,
            job_title=job_title_for_recording,
            job_url=jd_url_for_recording,
            user=user
        )
        
        # Use processed JD for analysis
        jd_text_for_analysis = jd_service.get_jd_text_for_ai(cname, prefer_processed=True)
        if jd_text_for_analysis:
            jd_text_for_recording = jd_text_for_analysis
    
    # Continue with existing analysis using processed JD text
    # ... rest of pipeline ...
```

### 4. **Tailored CV Generation** (`app/tailored_cv/services/cv_tailoring_service.py`)

**Current**: Uses JD text from recommendations  
**Change**: Use processed JD for better CV tailoring

**Location**: `_generate_tailored_cv()` method (line ~85)

```python
async def _generate_tailored_cv(
    self,
    original_cv: OriginalCV,
    recommendations: RecommendationAnalysis,
    optimization_strategy: OptimizationStrategy,
    custom_instructions: Optional[str] = None
) -> TailoredCV:
    """Generate tailored CV"""
    # ADD: Get processed JD text
    from app.services.jd_processing_service import get_jd_processing_service
    
    jd_service = get_jd_processing_service(self.user_email)
    company_name = recommendations.company
    
    # Get processed JD text for better tailoring
    jd_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
    
    if jd_text:
        # Use processed JD in prompt
        # ... modify prompt to use jd_text ...
    else:
        # Fallback to original JD from recommendations
        # ... existing code ...
```

### 5. **JD Analysis Route** (`app/routes/jd_analysis.py`)

**Current**: Analyzes JD from `jd_original.json`  
**Change**: Use processed JD for analysis

**Location**: `analyze_jd_endpoint()` function (line ~42)

```python
@router.post("/analyze-jd/{company_name}")
async def analyze_jd_endpoint(...):
    """Analyze job description"""
    # ADD: Use processed JD if available
    from app.services.jd_processing_service import get_jd_processing_service
    
    jd_service = get_jd_processing_service(current_user.email)
    jd_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
    
    if jd_text:
        # Analyze processed JD
        result = await analyzer.analyze_jd_text(jd_text, temperature)
    else:
        # Fallback to file-based analysis
        result = await analyze_and_save_company_jd(...)
```

### 6. **Job Description Saving** (`app/routes/skills_analysis.py`)

**Current**: Saves JD to `jd_original.json`  
**Change**: Also process JD when saving

**Location**: Where JD is saved (around line ~1705)

```python
# When saving JD original
jd_original_file = company_dir / f"jd_original_{timestamp}.json"
with open(jd_original_file, 'w', encoding='utf-8') as f:
    json.dump({"text": jd_text, "saved_at": datetime.now().isoformat()}, f, ...)

# ADD: Process JD after saving
from app.services.jd_processing_service import get_jd_processing_service

jd_service = get_jd_processing_service(user_email)
await jd_service.process_jd_if_needed(
    company_name=company_name,
    jd_text=jd_text,
    job_title=job_title,
    job_url=jd_url,
    user=user  # Get user from request context
)
```

## Integration Pattern

The standard integration pattern is:

1. **Get JD Processing Service**:
   ```python
   from app.services.jd_processing_service import get_jd_processing_service
   jd_service = get_jd_processing_service(user_email)
   ```

2. **Get Processed JD Text** (for AI operations):
   ```python
   jd_text = jd_service.get_jd_text_for_ai(company_name, prefer_processed=True)
   ```

3. **Process JD When Saving** (non-blocking):
   ```python
   await jd_service.process_jd_if_needed(
       company_name=company_name,
       jd_text=jd_text,
       job_title=job_title,
       job_url=job_url,
       user=user
   )
   ```

## Benefits

1. **Better AI Performance**: Processed JD removes noise and organizes content, improving AI analysis accuracy
2. **Consistent Structure**: All JDs follow the same section structure
3. **Backward Compatible**: Falls back to original JD if processed JD doesn't exist
4. **Non-Breaking**: Existing functionality continues to work

## Testing

After integration, test:
1. ✅ JD analysis works with processed JD
2. ✅ CV-JD matching uses processed JD
3. ✅ Skills analysis uses processed JD
4. ✅ Tailored CV generation uses processed JD
5. ✅ Fallback to original JD when processed JD doesn't exist

## Files Modified

- `app/services/jd_analysis/jd_analyzer.py` - Use processed JD
- `app/services/cv_jd_matching/cv_jd_matcher.py` - Use processed JD
- `app/routes/skills_analysis.py` - Process JD when saving, use processed JD
- `app/tailored_cv/services/cv_tailoring_service.py` - Use processed JD
- `app/routes/jd_analysis.py` - Use processed JD

## Notes

- Processed JD is saved as `jd_processed_{timestamp}.json` in company directory
- Original JD remains unchanged for backward compatibility
- Processing happens asynchronously and doesn't block user operations
- If processing fails, system falls back to original JD automatically

