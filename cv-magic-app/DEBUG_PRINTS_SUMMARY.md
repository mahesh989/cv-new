# Debug Prints Summary - CV Processing Pipeline

This document summarizes all the debug prints added to trace CV upload, parsing, and saving operations.

## Files Modified

### 1. `/backend/app/services/structured_cv_parser.py`
**Main CV Parser - Converts text to structured JSON**

Debug prints added to:
- `parse_cv_content()` - Entry point for parsing
  - Shows input type, length, user info
  - Tracks if content is already structured
  - Shows section headers extracted
  - Shows quality and completeness scores
  
- `_parse_with_llm()` - LLM-based parsing
  - Shows CV text length
  - Shows prompt creation
  - Shows AI service call
  - Shows JSON parsing success
  - Shows merge with default structure
  
- `save_structured_cv()` - Saves JSON to file
  - Shows target file path
  - Shows directory creation
  - Shows file write operation
  - Shows file size after save

### 2. `/backend/app/services/enhanced_cv_upload_service.py`
**Main Upload Service - Handles CV upload and orchestration**

Debug prints added to:
- `upload_cv_only()` - Simple upload without processing
  - Shows filename and user email
  - Shows file validation
  - Shows file save location
  
- `upload_and_process_cv()` - Full upload and processing
  - Shows all parameters (filename, user, title, description)
  - Shows each step: validation, read, save, extract, parse, validate, save
  - Shows quality scores
  - Shows final save location
  
- `_extract_text_content()` - Text extraction from files
  - Shows file path and extension
  - Shows extraction method used
  - Shows characters extracted
  
- `_parse_to_structured_format()` - Converts text to structured CV
  - Shows all input parameters
  - Shows AI service initialization
  - Shows provider selection
  - Shows content type detection (JSON vs raw text)
  - Shows metadata addition
  
- `_save_structured_cv()` - Saves to original_cv.json
  - Shows target path (always original_cv.json)
  - Shows metadata addition
  - Shows call to structured_parser

### 3. `/backend/app/services/cv_processor.py`
**Text Extraction Service - Extracts text from PDF/DOCX/TXT**

Debug prints added to:
- `extract_text_from_file()` - Main extraction entry point
  - Shows file path, exists status, suffix
  - Shows which extraction method is used (PDF/DOCX/TXT)
  
- `_extract_from_pdf()` - PDF text extraction
  - Shows PyPDF2 import success
  - Shows page count
  - Shows each page extraction
  - Shows total characters extracted
  
- `_extract_from_docx()` - DOCX text extraction
  - Shows python-docx import success
  - Shows paragraph count
  - Shows bullet detection
  - Shows total characters and bullets found
  
- `_extract_from_txt()` - TXT text extraction
  - Shows characters extracted

### 4. `/backend/app/routes/flutter_compat.py`
**API Routes - Flutter-compatible endpoints**

Debug prints added to:
- `/api/upload-cv` endpoint
  - Shows endpoint was called
  - Shows filename

### 5. `/backend/app/routes/cv_enhanced.py`
**API Routes - Enhanced CV endpoints**

Debug prints added to:
- `/cv-enhanced/upload` endpoint
  - Shows endpoint was called
  - Shows filename, title, description

## Debug Print Format

All debug prints follow this format:
```
================================================================================
🔍 [SERVICE_NAME] function_name() CALLED
================================================================================
📊 Parameter 1: value
📊 Parameter 2: value
================================================================================

🔧 [SERVICE_NAME] Step description...
✅ [SERVICE_NAME] Success message
❌ [SERVICE_NAME] Error message
📁 [SERVICE_NAME] File path info
```

## How to Trace CV Upload

When you upload a CV, you should see debug output in this order:

1. **API Endpoint Called**
   - `[FLUTTER_COMPAT]` or `[CV_ENHANCED]` - Shows which endpoint received the request

2. **CV Upload Service**
   - `[CV_UPLOAD_SERVICE] upload_and_process_cv()` - Main orchestrator
   
3. **Text Extraction**
   - `[CV_PROCESSOR] extract_text_from_file()` - File type detection
   - `[CV_PROCESSOR] _extract_from_pdf/docx/txt()` - Actual extraction

4. **Structured Parsing**
   - `[CV_UPLOAD_SERVICE] _parse_to_structured_format()` - Preparation
   - `[STRUCTURED_CV_PARSER] parse_cv_content()` - Main parsing entry
   - `[STRUCTURED_CV_PARSER] _parse_with_llm()` - LLM-based parsing

5. **Saving**
   - `[CV_UPLOAD_SERVICE] _save_structured_cv()` - Prepares save
   - `[STRUCTURED_CV_PARSER] save_structured_cv()` - Actual file write

## What to Look For

- ✅ Check which endpoint is being called (flutter_compat vs cv_enhanced)
- ✅ Check which extraction method is used (PDF/DOCX/TXT)
- ✅ Check if AI service is initialized properly
- ✅ Check if LLM parsing is successful
- ✅ Check final file save location (should be original_cv.json)
- ✅ Check quality and completeness scores

## Common Issues to Debug

1. **File not being extracted**: Look for `[CV_PROCESSOR]` messages
2. **LLM not parsing**: Look for `[STRUCTURED_CV_PARSER]` AI service messages
3. **Not saving to correct location**: Look for `[CV_UPLOAD_SERVICE] _save_structured_cv()` path
4. **Wrong service being used**: Look for which API endpoint is called first

## Files That Save CVs

Based on the code:
- **TXT Format**: `original_cv.txt` (saved by cv_processor if enabled)
- **JSON Format**: `original_cv.json` (always saved by enhanced_cv_upload_service)
- **Location**: `{user_base_path}/cvs/original/`

Note: The service ALWAYS saves as `original_cv.json` (replaces existing file).
