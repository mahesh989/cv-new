# Complete CV Save Functionality (Frontend + Backend)

## 📋 Overview

When a user selects a CV from the dropdown, the system automatically saves it as both `original_cv.txt` and `original_cv.json` files in the user's analysis folder.

---

## 🎨 Frontend Flow

### 1. **CV Selection Module** (`cv_selection_module.dart`)

**Location:** `mobile_app/lib/modules/cv/cv_selection_module.dart`

**What it does:**
- Displays dropdown with available CVs
- Fetches CV list from API
- Calls callback when user selects a CV

**Key Code:**
```dart
class CVSelectionModule extends StatefulWidget {
  final String? selectedCVFilename;
  final Function(String?) onCVSelected;
  final int refreshToken;
  
  // ... widget implementation
}

// Inside the widget:
DropdownButton<String>(
  value: selectedCVFilename,
  hint: const Text('Choose CV'),
  isExpanded: true,
  items: availableCVs.map((cv) => DropdownMenuItem(
    value: cv,
    child: Text(cv),
  )).toList(),
  onChanged: (value) {
    // Callback to parent widget
    onCVSelected(value);
  },
)
```

---

### 2. **Main Screen Handler** (`cv_magic_organized_page.dart`)

**Location:** `mobile_app/lib/screens/cv_magic_organized_page.dart`

**Function:** `_onCVSelected()` (lines 496-508)

**What it does:**
- Updates selected CV filename in state
- Calls API to save CV files to backend

**Key Code:**
```dart
void _onCVSelected(String? filename) {
  setState(() {
    selectedCVFilename = filename;
  });
  
  // Persist selection by saving original CV artifacts
  if (filename != null && filename.isNotEmpty) {
    APIService.saveCVForAnalysis(filename).then((_) {
      _showSnackBar('Saved original CV files for "$filename"');
    }).catchError((e) {
      _showSnackBar('Failed to save original CV: $e', isError: true);
    });
  }
}
```

**Usage in Widget:**
```dart
CVSelectionWidget(
  selectedCVFilename: selectedCVFilename,
  onCVSelected: _onCVSelected,  // ← Calls this when CV selected
  refreshToken: cvRefreshToken,
)
```

---

### 3. **API Service** (`api_service.dart`)

**Location:** `mobile_app/lib/services/api_service.dart`

**Function:** `saveCVForAnalysis()` (lines 297-302)

**What it does:**
- Makes authenticated POST request to backend
- Sends CV filename to save endpoint

**Key Code:**
```dart
static Future<void> saveCVForAnalysis(String filename) async {
  await makeAuthenticatedCall(
    endpoint: '/cv/save-for-analysis/$filename',
    method: 'POST',
  );
}
```

**How it works:**
- Uses `makeAuthenticatedCall()` which:
  1. Gets auth token from `AuthService`
  2. Adds `Authorization: Bearer {token}` header
  3. Makes POST request to `https://cvagent.duckdns.org/api/cv/save-for-analysis/{filename}`

---

## ⚙️ Backend Flow

### 1. **API Endpoint** (`cv_organized.py`)

**Location:** `backend/app/routes/cv_organized.py`

**Endpoint:** `POST /api/cv/save-for-analysis/{filename}`

**Function:** `save_cv_for_analysis()` (lines 67-181)

**What it does:**
1. Gets CV content from CV preview service
2. Creates `original_cv.txt` immediately
3. Creates `original_cv.json` immediately (minimal structure)
4. Starts background task to enhance JSON with structured data

**Complete Code:**
```python
@router.post("/save-for-analysis/{filename}")
async def save_cv_for_analysis(filename: str, current_user: UserData = Depends(get_current_user)):
    """Save selected CV as both original_cv.txt and original_cv.json in cv-analysis folder"""
    try:
        # Step 1: Get CV content
        from app.modules.cv.preview import CVPreviewService
        user_cv_preview_service = CVPreviewService(user_email=current_user.email)
        cv_content_result = user_cv_preview_service.get_cv_content(filename)
        
        if not cv_content_result.get('content'):
            raise HTTPException(status_code=404, detail=f"CV content not found for: {filename}")
        
        # Step 2: Create directories
        analysis_base: Path = get_user_base_path(current_user.email)
        analysis_base.mkdir(parents=True, exist_ok=True)
        original_folder = analysis_base / "cvs" / "original"
        original_folder.mkdir(parents=True, exist_ok=True)
        
        # Step 3: Define file paths
        txt_filepath = original_folder / "original_cv.txt"
        json_filepath = original_folder / "original_cv.json"
        
        # Step 4: Save original_cv.txt (ALWAYS OVERWRITE)
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(cv_content_result['content'])
        
        logger.info(f"✅ CV saved as text (overwritten): {txt_filepath}")
        
        # Step 5: Save minimal original_cv.json (ALWAYS OVERWRITE)
        import json
        from datetime import datetime
        minimal_json = {
            "filename": filename,
            "text": cv_content_result['content'],
            "saved_at": datetime.now().isoformat(),
            "content_type": "text",
            "processing_status": "pending_structured_parsing"
        }
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(minimal_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ CV saved as minimal JSON (overwritten): {json_filepath}")
        
        # Step 6: Start background enhancement (non-blocking)
        async def background_structured_processing():
            try:
                # Parse to structured format
                from app.services.enhanced_cv_upload_service import EnhancedCVUploadService
                user_enhanced_cv_upload_service = EnhancedCVUploadService(user_email=current_user.email)
                
                structured_cv = await user_enhanced_cv_upload_service._parse_to_structured_format(
                    text_content=cv_content_result['content'],
                    filename=filename,
                    user=current_user
                )
                
                # Update JSON with structured data
                if not structured_cv.get('parsing_error'):
                    structured_cv['filename'] = filename
                    structured_cv['saved_at'] = datetime.now().isoformat()
                    structured_cv['content_type'] = "structured"
                    structured_cv['processing_status'] = "completed"
                    
                    with open(json_filepath, 'w', encoding='utf-8') as f:
                        json.dump(structured_cv, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"✅ Background: CV enhanced with structured JSON: {json_filepath}")
            except Exception as e:
                logger.error(f"❌ Background: Error enhancing structured CV: {str(e)}")
        
        # Start background task
        asyncio.create_task(background_structured_processing())
        
        # Step 7: Return success response
        return JSONResponse(content={
            "message": "CV saved for analysis successfully",
            "filename": filename,
            "txt_path": str(txt_filepath),
            "json_path": str(json_filepath),
            "structured_success": "minimal_json_created_immediately_enhancement_in_background",
            "content_length": len(cv_content_result['content']),
            "note": "Both original_cv.txt and original_cv.json created immediately. JSON will be enhanced with structured data in background."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save CV for analysis: {str(e)}")
```

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Flutter)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. User selects CV from dropdown                           │
│     ↓                                                        │
│  2. CVSelectionWidget calls onCVSelected(filename)          │
│     ↓                                                        │
│  3. cv_magic_organized_page.dart                            │
│     _onCVSelected(filename)                                 │
│     ↓                                                        │
│  4. APIService.saveCVForAnalysis(filename)                  │
│     ↓                                                        │
│  5. POST /api/cv/save-for-analysis/{filename}               │
│     Headers: Authorization: Bearer {token}                 │
│                                                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  6. cv_organized.py                                          │
│     save_cv_for_analysis(filename)                          │
│     ↓                                                        │
│  7. Get CV content from CVPreviewService                    │
│     ↓                                                        │
│  8. Create directories:                                     │
│     /app/user/{email}/cv-analysis/cvs/original/             │
│     ↓                                                        │
│  9. Save original_cv.txt (IMMEDIATE)                        │
│     ↓                                                        │
│  10. Save original_cv.json (IMMEDIATE - minimal)            │
│     ↓                                                        │
│  11. Start background task to enhance JSON                  │
│     ↓                                                        │
│  12. Return success response                                │
│                                                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    FILE SYSTEM                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /app/user/{email}/cv-analysis/cvs/original/                 │
│  ├── original_cv.txt          ← Created immediately         │
│  └── original_cv.json         ← Created immediately        │
│                                (enhanced in background)      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

### Frontend Files

1. **`mobile_app/lib/widgets/cv_selection_widget.dart`**
   - CV dropdown widget
   - Calls `onCVSelected` callback

2. **`mobile_app/lib/screens/cv_magic_organized_page.dart`**
   - Main screen
   - `_onCVSelected()` handler (line 496)
   - Calls `APIService.saveCVForAnalysis()`

3. **`mobile_app/lib/services/api_service.dart`**
   - `saveCVForAnalysis()` method (line 297)
   - Makes POST request to backend

### Backend Files

1. **`backend/app/routes/cv_organized.py`**
   - `save_cv_for_analysis()` endpoint (line 67)
   - Creates both TXT and JSON files
   - Handles background enhancement

2. **`backend/app/modules/cv/preview.py`**
   - `CVPreviewService.get_cv_content()` 
   - Retrieves CV content from storage

3. **`backend/app/services/enhanced_cv_upload_service.py`**
   - `_parse_to_structured_format()`
   - Converts text CV to structured JSON

---

## 🔑 Key Features

### ✅ Immediate File Creation
- Both `original_cv.txt` and `original_cv.json` are created **immediately**
- No waiting for background processing
- Files always exist when needed

### ✅ Always Overwrites
- When user selects a new CV, old files are **overwritten**
- Ensures latest CV is always used

### ✅ Background Enhancement
- JSON file starts with minimal structure
- Enhanced with full structured data in background
- System works even if enhancement fails

### ✅ Error Handling
- Frontend shows success/error messages
- Backend logs all operations
- Graceful fallback if enhancement fails

---

## 📝 Example Request/Response

### Request (Frontend → Backend)
```http
POST /api/cv/save-for-analysis/my_cv.pdf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Response (Backend → Frontend)
```json
{
  "message": "CV saved for analysis successfully",
  "filename": "my_cv.pdf",
  "txt_path": "user/rashmi@gmail.com/cv-analysis/cvs/original/original_cv.txt",
  "json_path": "user/rashmi@gmail.com/cv-analysis/cvs/original/original_cv.json",
  "structured_success": "minimal_json_created_immediately_enhancement_in_background",
  "content_length": 12345,
  "note": "Both original_cv.txt and original_cv.json created immediately. JSON will be enhanced with structured data in background."
}
```

---

## 🎯 Summary

**Frontend:**
- User selects CV → `_onCVSelected()` → `APIService.saveCVForAnalysis()` → POST request

**Backend:**
- Receives request → Gets CV content → Creates TXT file → Creates JSON file → Returns success

**Result:**
- Both files created immediately in `/app/user/{email}/cv-analysis/cvs/original/`
- Files always overwritten when new CV is selected
- JSON enhanced in background with structured data

---

## ✅ Testing

To test the complete flow:

1. **Select CV from dropdown** (frontend)
2. **Check backend logs** for:
   - `✅ CV saved as text (overwritten): ...`
   - `✅ CV saved as minimal JSON (overwritten): ...`
3. **Verify files exist**:
   ```bash
   docker compose exec backend ls -la /app/user/{email}/cv-analysis/cvs/original/
   ```
4. **Check frontend** for success message: "Saved original CV files for..."

---

**This is the complete end-to-end functionality!** 🎉

