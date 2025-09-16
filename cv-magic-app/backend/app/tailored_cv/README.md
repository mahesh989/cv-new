# CV Tailoring System

A comprehensive, AI-powered CV tailoring system that optimizes CVs based on job recommendations and the CV optimization framework. The system transforms original CVs into highly optimized, ATS-friendly versions tailored for specific companies and roles.

## 🎯 Features

- **AI-Powered Optimization**: Uses the centralized AI service for intelligent CV enhancement
- **Impact Statement Formula**: Transforms bullet points using the proven format
- **ATS Optimization**: Targets 80+ ATS scores with strategic keyword integration
- **Company-Specific Tailoring**: Customizes content based on job recommendations
- **Batch Processing**: Process multiple company applications simultaneously
- **Validation & Quality Checks**: Comprehensive CV structure and content validation
- **Modular Architecture**: Clean separation of concerns with services, models, and routes

## 📁 Structure

```
tailored_cv/
├── __init__.py              # Main module exports
├── models/
│   ├── __init__.py
│   └── cv_models.py         # Pydantic models for CV data structures
├── services/
│   ├── __init__.py
│   └── cv_tailoring_service.py  # Core business logic
├── routes/
│   ├── __init__.py
│   └── cv_tailoring_routes.py   # FastAPI endpoints
├── prompts/
│   └── framework.md         # CV optimization framework
├── examples/
│   ├── example_usage.py     # Usage examples and test data
│   └── data/               # Example CV and recommendation files
└── README.md               # This file
```

## 🔧 Core Components

### 1. CV Optimization Framework (`prompts/framework.md`)

The heart of the system - a comprehensive framework that includes:
- **Impact Statement Formula**: `[Action Verb] + [Specific Method/Technology] + [Context/Challenge] + [Quantified Result] + [Business Impact]`
- **Strategic Positioning**: Education placement based on experience level
- **ATS Optimization**: Keyword integration and formatting guidelines
- **Quality Standards**: Authenticity constraints and success validation

### 2. Data Models (`models/cv_models.py`)

Comprehensive Pydantic models for:
- `OriginalCV`: Input CV structure
- `TailoredCV`: Enhanced output CV structure
- `RecommendationAnalysis`: Job recommendation analysis
- `CVTailoringRequest/Response`: API request/response models
- `OptimizationStrategy`: Tailoring strategy configuration

### 3. CV Tailoring Service (`services/cv_tailoring_service.py`)

Main business logic including:
- CV validation and quality checks
- Optimization strategy determination
- AI-powered content enhancement
- ATS score estimation
- File operations and company folder management

### 4. API Routes (`routes/cv_tailoring_routes.py`)

FastAPI endpoints for:
- `POST /api/tailored-cv/tailor` - Main CV tailoring endpoint
- `POST /api/tailored-cv/validate-cv` - CV validation
- `GET /api/tailored-cv/companies` - Available companies list
- `GET /api/tailored-cv/recommendations/{company}` - Company recommendations
- `POST /api/tailored-cv/batch-tailor` - Batch processing
- `GET /api/tailored-cv/framework` - Framework content retrieval

## 🚀 Usage

### Basic CV Tailoring

```python
from app.tailored_cv.models.cv_models import CVTailoringRequest, OriginalCV, RecommendationAnalysis
from app.tailored_cv.services.cv_tailoring_service import cv_tailoring_service

# Create request
request = CVTailoringRequest(
    original_cv=original_cv_data,
    recommendations=recommendation_analysis,
    custom_instructions="Focus on scalability and system design",
    target_ats_score=85
)

# Process CV tailoring
response = await cv_tailoring_service.tailor_cv(request)

if response.success:
    tailored_cv = response.tailored_cv
    print(f"ATS Score: {tailored_cv.estimated_ats_score}")
    print(f"Keywords integrated: {len(tailored_cv.keywords_integrated)}")
```

### API Usage

```bash
# Tailor a CV
curl -X POST "http://localhost:8000/api/tailored-cv/tailor" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "original_cv": {...},
    "recommendations": {...},
    "custom_instructions": "Focus on leadership experience",
    "target_ats_score": 85
  }'

# Get available companies
curl -X GET "http://localhost:8000/api/tailored-cv/companies?data_folder=/path/to/companies" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Batch tailor for multiple companies
curl -X POST "http://localhost:8000/api/tailored-cv/batch-tailor" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "original_cv": {...},
    "company_names": ["Google", "Microsoft", "Amazon"],
    "data_folder": "/path/to/companies"
  }'
```

## 📊 Expected Folder Structure

The system expects company recommendation files to be organized as follows:

```
data/
├── Google/
│   ├── recommendation_analysis.json
│   └── tailored_cv_20241216_143022.json
├── Microsoft/
│   ├── recommendation_analysis.json
│   └── tailored_cv_20241216_143055.json
└── Amazon/
    ├── recommendation_analysis.json
    └── tailored_cv_20241216_143128.json
```

## 🔄 Processing Flow

1. **Input Validation**: Validate CV structure and content quality
2. **Strategy Determination**: Analyze experience level and determine optimization approach
3. **AI Enhancement**: Use AI service to transform content following the framework
4. **Quality Assurance**: Validate enhanced content and estimate ATS score
5. **Output Generation**: Create tailored CV with tracking metadata
6. **File Management**: Save tailored CV to company-specific folders

## ⚙️ Configuration

The system integrates with the existing AI service configuration:
- Uses centralized AI provider management
- Supports multiple AI providers (OpenAI, Anthropic, DeepSeek)
- Configurable temperature and token limits
- Request-specific model selection

## 📈 Optimization Features

### Impact Statement Enhancement
- Transforms weak bullets into quantified achievements
- Adds specific technologies and methodologies
- Includes business impact metrics
- Follows proven formula structure

### ATS Optimization
- Strategic keyword placement
- Natural language integration
- Density optimization without stuffing
- Format compatibility

### Company Alignment
- Values integration
- Industry terminology
- Cultural language alignment
- Role-specific positioning

## 🧪 Testing

Run the example usage:
```python
# Generate example files
cd backend
python -m app.tailored_cv.examples.example_usage

# Test imports
python -c "from app.tailored_cv.services.cv_tailoring_service import cv_tailoring_service; print('Import successful!')"
```

## 🔐 Authentication

All endpoints require valid JWT authentication through the `get_current_user` dependency.

## 📝 Data Models

### OriginalCV
```python
{
    "contact": {...},
    "education": [...],
    "experience": [...],
    "projects": [...],
    "skills": [...],
    "total_years_experience": 3
}
```

### RecommendationAnalysis
```python
{
    "company": "Google",
    "job_title": "Senior Software Engineer",
    "missing_technical_skills": [...],
    "missing_soft_skills": [...],
    "critical_gaps": [...],
    "technical_enhancements": [...],
    "keyword_integration": [...],
    "match_score": 65,
    "target_score": 85
}
```

### TailoredCV
```python
{
    # Enhanced CV structure
    "contact": {...},
    "experience": [...],  # With optimized bullets
    "skills": [...],      # With integrated keywords
    
    # Metadata
    "target_company": "Google",
    "estimated_ats_score": 85,
    "keywords_integrated": [...],
    "optimization_strategy": {...}
}
```

## 🛠️ Integration

The system is fully integrated with the main FastAPI application:
- Added to `main.py` as `/api/tailored-cv` routes
- Uses existing authentication system
- Leverages centralized AI service
- Follows established error handling patterns

## 🎉 Success Criteria

A successful CV tailoring should achieve:
- ✅ 80+ estimated ATS score
- ✅ All critical gaps addressed
- ✅ Impact formula compliance in all bullets
- ✅ Natural keyword integration
- ✅ Company-specific optimization
- ✅ Maintained authenticity (no fabrication)

## 📞 Support

For issues or enhancements:
1. Check existing API documentation at `/docs`
2. Review example usage in `examples/example_usage.py`
3. Validate CV structure using the validation endpoint
4. Check AI service status and provider availability

---

**Built with the vision of transforming careers through AI-powered CV optimization.** 🚀