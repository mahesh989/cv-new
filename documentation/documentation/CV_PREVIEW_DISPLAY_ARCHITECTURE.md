# CV Preview Display Architecture in Frontend

## Overview
The CV preview functionality in the CV Magic application follows a modular architecture with separate components for handling CV content extraction, display, and formatting. This document explains how the CV preview is displayed in the frontend.

## Architecture Components

### 1. Frontend Components (Flutter Mobile App)

#### CVPreviewModule (`lib/modules/cv/cv_preview_module.dart`)
The main widget responsible for displaying CV previews with the following features:
- **Stateful widget** that manages CV content loading and display
- **Auto-save functionality** for analysis when content is loaded
- **Content formatting** with visual enhancements
- **Dark theme preview** with monospace font styling

Key methods:
- `_loadCVContent()`: Fetches CV content from backend API
- `_formatCVContent()`: Applies formatting rules for better readability
- `_autoSaveForAnalysis()`: Automatically saves CV for analysis

#### CV Magic Page (`lib/screens/cv_magic_page.dart`)
The main page that integrates CV preview functionality:
- Contains CV selection dropdown
- Displays CVPreviewModule when a CV is selected
- Handles file uploads and CV list management

### 2. Backend API Endpoints

#### Content Retrieval Endpoints
- **GET `/api/cv/content/{filename}`**: Returns full CV text content
- **GET `/api/cv/preview/{filename}`**: Returns truncated preview with metadata
- **POST `/api/cv/save-for-analysis/{filename}`**: Saves CV for analysis

#### Backend Services
- **CVPreviewService** (`backend/app/modules/cv/preview.py`):
  - Extracts text from uploaded CV files
  - Generates previews with customizable length
  - Provides metadata about CV content
  - Supports multiple file formats (PDF, DOCX, TXT)

### 3. Data Flow

```
User selects CV → Frontend requests content → Backend extracts text → 
→ Backend returns JSON → Frontend formats & displays → Auto-save for analysis
```

## Display Features

### Visual Formatting
The CV preview includes special formatting for:

1. **Section Headers**: Displayed with decorative borders
   - All-caps sections get special formatting
   - Visual separators using box-drawing characters

2. **Job Information**: 
   - Date ranges highlighted with 📅 emoji
   - Company names marked with 🏢 emoji

3. **Education Entries**:
   - Universities and degrees marked with 🎓 emoji

4. **Contact Information**:
   - Email and social links marked with 📧 emoji

5. **Bullet Points**:
   - Indented for better readability

### Styling
```dart
// Dark theme styling (similar to terminal)
Container(
  color: Colors.grey[900],  // Black background
  child: SelectableText(
    style: TextStyle(
      fontFamily: 'monospace',  // Terminal-like font
      color: Colors.grey[100],   // Light text
      fontSize: 13,
      height: 1.6,              // Comfortable line spacing
    ),
  ),
)
```

## Content Processing Pipeline

### 1. File Upload
- User uploads CV through FilePicker
- CV saved to `uploads/` directory
- File added to available CVs list

### 2. Content Extraction
Backend uses `cv_processor` to:
- Extract text from PDF/DOCX/TXT files
- Clean and normalize text content
- Extract metadata (word count, character count)

### 3. Frontend Display
- Content loaded via HTTP GET request
- Text formatted with `_formatCVContent()` method
- Displayed in scrollable container with dark theme

### 4. Auto-Save for Analysis
When CV is loaded:
- Automatically saved as `cv-analysis/original_cv.txt`
- Also processed to `cv-analysis/original_cv.json` for structured analysis
- User notified via SnackBar

## API Response Format

### Content Endpoint Response
```json
{
  "filename": "cv.pdf",
  "content": "Full CV text content...",
  "metadata": {
    "pages": 2,
    "author": "John Doe"
  },
  "file_info": {
    "size": 102400,
    "type": "PDF",
    "uploaded_date": 1234567890
  },
  "extraction_info": {
    "method": "pdfplumber",
    "character_count": 5000,
    "word_count": 800
  }
}
```

### Preview Endpoint Response
```json
{
  "filename": "cv.pdf",
  "preview": "First 500 characters...",
  "full_length": 5000,
  "preview_length": 500,
  "is_truncated": true,
  "basic_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "extraction_method": "pdfplumber"
}
```

## UI Components

### Preview Container Structure
```
Card Widget
├── Header Row
│   ├── Preview Icon (blue)
│   └── CV Filename
├── Loading Indicator (when loading)
├── Content Container
│   ├── Metadata Bar
│   │   ├── File icon
│   │   ├── "CV Content" label
│   │   └── Character count
│   └── Scrollable Text Area
│       └── Formatted CV Text (selectable)
└── Empty State (when no CV selected)
```

### Responsive Design
- Full width containers
- Fixed height (300px) for preview area
- Scrollable content for long CVs
- Selectable text for copying

## Error Handling

### Frontend Error States
- "Failed to load CV content" - HTTP error
- "Error loading CV content: [error]" - Network/parsing error
- Empty state message when no CV selected

### Backend Error Responses
- 404: CV file not found
- 500: Text extraction failed
- Detailed error messages in response

## Performance Optimizations

1. **Lazy Loading**: Content only loaded when CV selected
2. **Caching**: Previous content cleared on new selection
3. **Preview Truncation**: Configurable max_length parameter
4. **Efficient Formatting**: Single-pass text formatting algorithm
5. **Auto-save**: Async operation with silent fail handling

## Future Enhancements

Potential improvements identified:
- Real-time preview updates during editing
- Syntax highlighting for specific CV sections
- Export preview as formatted document
- Side-by-side comparison of multiple CVs
- Advanced search within CV content
- Template-based formatting options

## Related Components

- **CV Upload**: `CvUploader` widget for file selection
- **CV Selection**: Dropdown for choosing uploaded CVs
- **API Service**: `APIService` class for backend communication
- **CV Processor**: Backend service for text extraction

## Conclusion

The CV preview display system provides a clean, formatted view of uploaded CVs with automatic processing for analysis. The modular architecture allows for easy maintenance and extension of features while maintaining a consistent user experience across the application.