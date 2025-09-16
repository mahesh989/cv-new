# AI Recommendation TXT to JSON Conversion

## Overview

The AI recommendation system has been updated to save recommendations in JSON format instead of TXT format. This provides better structure, metadata, and frontend compatibility.

## Changes Made

### 1. Backend Service Updates

**File:** `app/services/ai_recommendation_generator.py`

- **Updated `_get_output_file_path()`**: Now generates `.json` files instead of `.txt`
- **Updated `_structure_ai_response()`**: Returns structured JSON data with metadata
- **Updated `_save_ai_recommendation()`**: Saves JSON format with proper structure
- **Added `convert_txt_to_json()`**: Converts existing TXT files to JSON format
- **Added `batch_convert_txt_to_json()`**: Batch converts all TXT files to JSON

### 2. API Routes Updates

**File:** `app/routes/ai_recommendations.py`

- **Added conversion endpoints**:
  - `POST /ai-recommendations/convert-txt-to-json` - Batch convert all TXT files
  - `POST /ai-recommendations/convert-txt-to-json/{company}` - Convert specific company TXT file

### 3. JSON Structure

The new JSON format contains:

```json
{
  "company": "Company_Name",
  "generated_at": "2025-09-16T20:13:04.227228",
  "recommendation_content": "# AI Recommendation Content...",
  "ai_model_info": {
    "provider": "openai|anthropic|unknown",
    "model": "gpt-4|claude-3-sonnet|unknown",
    "cost": 0.0,
    "tokens_used": 0
  },
  "metadata": {
    "content_length": 3826,
    "format_version": "1.0",
    "converted_from_txt": true
  }
}
```

## Migration Process

### Converting Existing TXT Files

1. **Single Company Conversion:**
   ```python
   from app.services.ai_recommendation_generator import ai_recommendation_generator
   success = ai_recommendation_generator.convert_txt_to_json("Australia_for_UNHCR")
   ```

2. **Batch Conversion:**
   ```python
   from app.services.ai_recommendation_generator import ai_recommendation_generator
   results = ai_recommendation_generator.batch_convert_txt_to_json()
   ```

3. **Via API (when server is running):**
   ```bash
   # Convert all TXT files
   curl -X POST "http://localhost:8001/ai-recommendations/convert-txt-to-json"
   
   # Convert specific company
   curl -X POST "http://localhost:8001/ai-recommendations/convert-txt-to-json/Australia_for_UNHCR"
   ```

## Frontend Compatibility

The JSON structure is fully compatible with the Flutter frontend:

- **AIRecommendationResult model**: Maps correctly to the `content`, `generated_at`, and `model_info` fields
- **Analysis results endpoint**: The `/analysis-results/{company}` endpoint correctly formats the data
- **AI recommendations widget**: Displays the markdown content properly

## Testing

Run the test scripts to verify the conversion:

```bash
# Test conversion functionality
python test_txt_to_json_conversion.py

# Test JSON structure compatibility  
python test_ai_recommendation_json.py
```

## Benefits

1. **Better Structure**: JSON provides clear metadata and organization
2. **Frontend Integration**: Native JSON parsing in frontend applications
3. **Metadata Tracking**: Track AI model info, costs, timestamps, etc.
4. **API Consistency**: Consistent with other API endpoints
5. **Extensibility**: Easy to add new fields and features

## Backward Compatibility

- Existing TXT files are preserved and can be converted using the migration tools
- The conversion process maintains the original content while adding metadata
- Both TXT and JSON files can coexist during transition period

## File Locations

- **Original TXT files**: `cv-analysis/{company}/{company}_ai_recommendation.txt`
- **New JSON files**: `cv-analysis/{company}/{company}_ai_recommendation.json`

## Migration Status

- ✅ Backend service updated to generate JSON format
- ✅ Conversion utilities added
- ✅ API endpoints for conversion added
- ✅ Frontend compatibility verified
- ✅ Australia_for_UNHCR TXT file successfully converted to JSON