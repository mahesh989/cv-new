# CV Parsing Flow - File Structure and Call Chain

## Overview
This document explains which files are involved in CV parsing, the main parsing file, and how it's called from other files.

---

## 🎯 Main Parsing File

### `structured_cv_parser.py`
**Location:** `cv-magic-app/backend/app/services/structured_cv_parser.py`

**Purpose:** Core CV parsing logic using LLM to convert CV text into structured JSON format.

**Key Class:**
- `LLMStructuredCVParser` - Main parser class
- `enhanced_cv_parser` - Global instance (line 496)

**Main Methods:**
1. `parse_cv_content()` - Main entry point for parsing CV text/dict
2. `_parse_with_llm()` - Calls AI service to parse CV using LLM
3. `_create_parsing_prompt()` - Generates the prompt for LLM
4. `validate_cv_structure()` - Validates parsed CV structure
5. `save_structured_cv()` - Saves structured CV to JSON file
6. `load_structured_cv()` - Loads structured CV from JSON file

**Dependencies:**
- `ai_service` - For LLM calls
- Standard library (json, logging, os, datetime, pathlib)

---

## 📞 Service Layer (Calls the Parser)

### `enhanced_cv_upload_service.py`
**Location:** `cv-magic-app/backend/app/services/enhanced_cv_upload_service.py`

**Purpose:** Service that orchestrates CV upload, text extraction, and structured parsing.

**How it uses the parser:**
```python
# Line 40: Creates parser instance
self.structured_parser = LLMStructuredCVParser()

# Line 142: Calls parser in upload_and_process_cv()
structured_cv = await self._parse_to_structured_format(...)

# Line 248: Calls parser in process_existing_cv()
structured_cv = await self._parse_to_structured_format(..., user=user_data)

# Line 413-421: Inside _parse_to_structured_format() - calls parser
structured_cv = await self.structured_parser.parse_cv_content(text_content, user)

# Line 152: Validates using parser
validation_report = self.structured_parser.validate_cv_structure(structured_cv)
```

**Key Methods:**
- `upload_and_process_cv()` - Uploads CV file and processes it
- `process_existing_cv()` - Processes already uploaded CV file
- `_parse_to_structured_format()` - Internal method that calls the parser
- `_extract_text_content()` - Extracts text from PDF/DOCX/TXT files

---

## 🌐 API Route Layer (Calls the Service)

### 1. `cv_structured.py`
**Location:** `cv-magic-app/backend/app/routes/cv_structured.py`

**Purpose:** API endpoints for structured CV processing.

**Endpoints:**
- `POST /api/cv-structured/upload` - Upload and parse CV
- `POST /api/cv-structured/process-existing/{filename}` - Process existing CV
- `GET /api/cv-structured/load` - Load structured CV
- `GET /api/cv-structured/validate` - Validate CV structure
- `GET /api/cv-structured/status/{filename}` - Get processing status

**How it calls the service:**
```python
# Line 17: Imports service
from ..services.enhanced_cv_upload_service import enhanced_cv_upload_service

# Line 42: Calls service method
result = await enhanced_cv_upload_service.upload_and_process_cv(...)

# Line 76: Calls service method
result = await enhanced_cv_upload_service.process_existing_cv(...)

# Line 180: Directly uses parser for validation
validation_report = enhanced_cv_parser.validate_cv_structure(cv_data)
```

### 2. `cv_organized.py`
**Location:** `cv-magic-app/backend/app/routes/cv_organized.py`

**Purpose:** Organized CV API endpoints (simpler interface).

**Key Endpoint:**
- `POST /api/cv/save-for-analysis/{filename}` - Saves CV for analysis

**How it calls the service:**
```python
# Line 19: Imports service
from ..services.enhanced_cv_upload_service import enhanced_cv_upload_service

# Line 149: Creates user-specific service instance
user_enhanced_cv_upload_service = EnhancedCVUploadService(user_email=current_user.email)

# Line 152: Calls service method in background task
processing_result = await user_enhanced_cv_upload_service.process_existing_cv(filename=filename)
```

---

## 🔗 Complete Call Chain

### Flow 1: Upload New CV
```
HTTP Request
    ↓
cv_structured.py::upload_cv_structured()
    ↓
enhanced_cv_upload_service.py::upload_and_process_cv()
    ↓
enhanced_cv_upload_service.py::_parse_to_structured_format()
    ↓
structured_cv_parser.py::parse_cv_content()
    ↓
structured_cv_parser.py::_parse_with_llm()
    ↓
ai_service.generate_response() [LLM Call]
    ↓
structured_cv_parser.py::_merge_with_default_structure()
    ↓
structured_cv_parser.py::save_structured_cv()
    ↓
original_cv.json saved
```

### Flow 2: Process Existing CV
```
HTTP Request
    ↓
cv_organized.py::save_cv_for_analysis()
    ↓
Background Task: background_structured_processing()
    ↓
enhanced_cv_upload_service.py::process_existing_cv()
    ↓
enhanced_cv_upload_service.py::_extract_text_content()
    ↓
enhanced_cv_upload_service.py::_parse_to_structured_format()
    ↓
structured_cv_parser.py::parse_cv_content()
    ↓
[Same LLM parsing flow as above]
```

---

## 📋 File Summary

| File | Role | Calls |
|------|------|-------|
| `structured_cv_parser.py` | **Main Parser** | Called by services |
| `enhanced_cv_upload_service.py` | **Service Layer** | Calls parser, called by routes |
| `cv_structured.py` | **API Routes** | Calls service |
| `cv_organized.py` | **API Routes** | Calls service |
| `main.py` | **App Registration** | Registers routes (lines 289-290) |

---

## 🔑 Key Entry Points

### For Direct Parsing:
```python
from app.services.structured_cv_parser import enhanced_cv_parser

# Parse CV text
structured_cv = await enhanced_cv_parser.parse_cv_content(cv_text, user=user)

# Validate CV
validation = enhanced_cv_parser.validate_cv_structure(structured_cv)

# Save CV
enhanced_cv_parser.save_structured_cv(structured_cv, file_path)
```

### For Upload Processing:
```python
from app.services.enhanced_cv_upload_service import EnhancedCVUploadService

# Create service instance
service = EnhancedCVUploadService(user_email="user@example.com")

# Upload and process
result = await service.upload_and_process_cv(cv_file, user=user)

# Process existing CV
result = await service.process_existing_cv(filename)
```

### For API Endpoints:
- `POST /api/cv-structured/upload` - Upload new CV
- `POST /api/cv-structured/process-existing/{filename}` - Process existing CV
- `POST /api/cv/save-for-analysis/{filename}` - Save CV for analysis

---

## 📝 Notes

1. **User Context Required:** The parser needs a `user` object for AI service calls (line 132 in structured_cv_parser.py)

2. **File Output:** All structured CVs are saved as `original_cv.json` in user-specific paths:
   - `{user_base_path}/cvs/original/original_cv.json`

3. **Text Extraction:** Before parsing, text is extracted from PDF/DOCX using `cv_processor` service

4. **Background Processing:** `cv_organized.py` uses FastAPI BackgroundTasks for non-blocking processing

5. **Global Instance:** `enhanced_cv_parser` is a global instance, but `EnhancedCVUploadService` creates user-specific instances

