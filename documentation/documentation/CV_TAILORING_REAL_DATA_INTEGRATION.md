# CV Tailoring with Real Data Integration

## Overview

The CV tailoring system has been enhanced to work with real data from the `cv-analysis` folder. The system now properly handles dynamic company names and saves tailored CVs to the correct location.

## Key Features

### 🎯 Dynamic Company Support
- Works with any company that has an AI recommendation file
- Automatically detects available companies
- Provides clear error messages when companies are not found

### 📁 File Structure
```
cv-analysis/
├── original_cv.json                    # Original CV data
├── tailored_cv.json                   # Generated tailored CV
└── {company}/
    └── {company}_ai_recommendation.json # AI recommendation for company
```

## New API Endpoints

### 1. Tailor CV with Real Data
```http
POST /api/tailored-cv/tailor-with-real-data/{company}
```

**Description**: Tailors CV using real data from the cv-analysis folder

**Parameters**:
- `company` (path): Company name (e.g., "Australia_for_UNHCR", "Google")
- `custom_instructions` (optional): Custom tailoring instructions

**Example**:
```bash
curl -X POST "http://localhost:8001/api/tailored-cv/tailor-with-real-data/Australia_for_UNHCR" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"custom_instructions": "Focus on data analysis skills"}'
```

### 2. Get Available Companies
```http
GET /api/tailored-cv/available-companies
```

**Description**: Returns list of companies with AI recommendation files

**Response**:
```json
{
  "success": true,
  "companies": ["Australia_for_UNHCR"],
  "total_count": 1,
  "message": "Found 1 companies with AI recommendations"
}
```

## How It Works

### 1. Company Detection
The system scans the `cv-analysis` folder and looks for:
- Company directories (e.g., `Australia_for_UNHCR/`)
- AI recommendation files (e.g., `Australia_for_UNHCR_ai_recommendation.json`)

### 2. Data Loading
For each tailoring request, the system:
1. Loads `original_cv.json` from the cv-analysis folder
2. Loads the company-specific AI recommendation file
3. Parses both files into the appropriate data models

### 3. CV Tailoring
The AI-powered tailoring service:
1. Analyzes the original CV and AI recommendations
2. Determines optimization strategy
3. Generates tailored content using OpenAI/Anthropic
4. Estimates ATS score improvement

### 4. File Saving
The tailored CV is saved as:
- **Location**: `/cv-analysis/tailored_cv.json`
- **Format**: Structured JSON with all CV sections
- **Includes**: Metadata, processing summary, and optimization details

## Error Handling

### Company Not Found
```json
{
  "status_code": 404,
  "detail": "Company 'Google' not found. Available companies: ['Australia_for_UNHCR']"
}
```

### Missing Files
```json
{
  "status_code": 404,
  "detail": "Required files not found for company 'Google': Company folder not found"
}
```

### Processing Errors
```json
{
  "status_code": 500,
  "detail": "CV tailoring failed: [specific error message]"
}
```

## Usage Examples

### Frontend Integration
```javascript
// Get available companies
const companies = await fetch('/api/tailored-cv/available-companies');

// Tailor CV for specific company
const response = await fetch('/api/tailored-cv/tailor-with-real-data/Australia_for_UNHCR', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    custom_instructions: "Focus on technical skills and quantifiable achievements"
  })
});
```

### CLI Testing
```bash
# Test the system
python test_cv_tailoring_real_data.py

# Expected output:
# ✅ Found 1 companies with AI recommendations
# ✅ Successfully loaded data for Australia_for_UNHCR
# ✅ All tests passed!
```

## Current Status

### ✅ Available Companies
- **Australia_for_UNHCR**: Senior Data Analyst role
  - Original CV: Maheshwor Tiwari
  - AI recommendation file: Available
  - Ready for tailoring

### 📝 To Add More Companies
1. Create company folder: `cv-analysis/{company_name}/`
2. Add AI recommendation file: `{company_name}_ai_recommendation.json`
3. The system will automatically detect the new company

## Benefits

1. **Dynamic**: Works with any company that has recommendation data
2. **Automatic Detection**: No manual configuration needed
3. **Proper Error Handling**: Clear messages when files are missing
4. **Consistent Saving**: Always saves to `cv-analysis/tailored_cv.json`
5. **Real Data Integration**: Uses actual CV and recommendation data

---

**Next Steps**: When you want to tailor a CV for a different company (e.g., "Google"), simply ensure there's a `cv-analysis/Google/Google_ai_recommendation.json` file, and the system will work automatically.