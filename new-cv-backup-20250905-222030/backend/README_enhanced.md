# Enhanced CV Analysis Backend API

This enhanced backend provides comprehensive CV and Job Description (JD) processing capabilities with intelligent analysis and skill matching.

## 🚀 New Features

### Enhanced CV Processing
- **Multi-format Support**: PDF, DOCX, and TXT file uploads
- **Advanced Text Extraction**: Using `pdfplumber` and `python-docx` for better accuracy
- **Background Processing**: Asynchronous file processing with status tracking
- **Metadata Extraction**: Automatic extraction of emails, phone numbers, and key sections
- **File Management**: Secure file storage and retrieval system

### Intelligent JD Extraction
- **Web Scraping**: Extract job descriptions from popular job sites (Seek, Indeed, LinkedIn, etc.)
- **Direct Text Processing**: Process JD content from copied text
- **Structured Content**: Clean and organize extracted content
- **Multi-source Support**: URL extraction and direct text input
- **Site-specific Optimization**: Tailored extraction for different job portals

### Advanced Analysis Engine
- **Skill Matching**: Compare CV skills against JD requirements
- **Experience Analysis**: Evaluate experience relevance and level
- **Overall Fit Scoring**: Comprehensive compatibility assessment
- **Gap Analysis**: Identify missing skills and suggest improvements
- **Multiple Analysis Types**: Skill match, experience match, and overall fit

## 📁 Project Structure

```
backend/
├── app/
│   ├── routes/
│   │   ├── cv_enhanced.py         # Enhanced CV processing routes
│   │   ├── jd_enhanced.py         # Enhanced JD extraction routes
│   │   ├── analysis_enhanced.py   # CV-JD analysis routes
│   │   └── __init__.py           # Route registration
│   ├── services/
│   │   ├── cv_processor.py       # CV text extraction service
│   │   └── jd_extractor.py      # JD web scraping service
│   ├── enhanced_database.py     # Enhanced database operations
│   ├── models.py                # Enhanced data models
│   └── main.py                  # Updated FastAPI application
├── test_enhanced_api.py         # Comprehensive API test suite
├── requirements.txt             # Updated dependencies
└── README_enhanced.md          # This documentation
```

## 🛠️ Technology Stack

### Core Framework
- **FastAPI**: Modern, high-performance web framework
- **SQLite**: File-based database for enhanced operations
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server implementation

### Document Processing
- **pdfplumber**: Advanced PDF text extraction
- **python-docx**: DOCX document processing
- **PyPDF2**: Fallback PDF processing

### Web Scraping
- **BeautifulSoup4**: HTML parsing and extraction
- **Requests**: HTTP client for web scraping
- **lxml**: Fast XML and HTML parser

## 🔧 Installation & Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Database Initialization**:
   ```bash
   # The enhanced database will be created automatically
   # on first run in: storage/enhanced_cv_analysis.db
   ```

4. **Start the Server**:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Run Tests**:
   ```bash
   python test_enhanced_api.py
   ```

## 📚 API Endpoints

### Enhanced CV Processing (`/api/cv-enhanced`)

#### Upload CV
```http
POST /api/cv-enhanced/upload
Content-Type: multipart/form-data

- cv_file: File (PDF/DOCX/TXT)
- title: Optional string
- description: Optional string
```

#### List CVs
```http
GET /api/cv-enhanced/list?page=1&limit=10
```

#### Get CV Content
```http
GET /api/cv-enhanced/{cv_id}
```

#### Get CV Preview
```http
GET /api/cv-enhanced/{cv_id}/preview?max_length=500
```

#### Download CV
```http
GET /api/cv-enhanced/{cv_id}/download
```

#### CV Statistics
```http
GET /api/cv-enhanced/{cv_id}/stats
```

#### Delete CV
```http
DELETE /api/cv-enhanced/{cv_id}
```

#### Reprocess CV
```http
POST /api/cv-enhanced/{cv_id}/reprocess
```

### Enhanced JD Processing (`/api/jd-enhanced`)

#### Extract from URL
```http
POST /api/jd-enhanced/extract
Content-Type: application/json

{
  "url": "https://seek.com.au/job/123456",
  "title": "Optional job title",
  "company": "Optional company name",
  "location": "Optional location"
}
```

#### Extract from Text
```http
POST /api/jd-enhanced/extract-text
Content-Type: application/json

{
  "text": "Job description content...",
  "title": "Software Engineer",
  "company": "Tech Corp",
  "location": "Sydney, AU"
}
```

#### List JDs
```http
GET /api/jd-enhanced/list?page=1&limit=10&source=url
```

#### Get JD Content
```http
GET /api/jd-enhanced/{jd_id}
```

#### Get JD Preview
```http
GET /api/jd-enhanced/{jd_id}/preview
```

#### Test URL Extraction
```http
POST /api/jd-enhanced/test-url?url=https://example.com/job
```

#### Supported Sites
```http
GET /api/jd-enhanced/supported-sites/list
```

### Enhanced Analysis (`/api/analysis-enhanced`)

#### Create Analysis
```http
POST /api/analysis-enhanced/analyze
Content-Type: application/json

{
  "cv_id": "uuid-string",
  "jd_id": "uuid-string",
  "analysis_type": "skill_match",
  "include_suggestions": true
}
```

#### Get Analysis Result
```http
GET /api/analysis-enhanced/{analysis_id}
```

#### Extract Skills from Text
```http
POST /api/analysis-enhanced/extract-skills
Content-Type: application/json

{
  "text": "Text content to analyze...",
  "text_type": "cv",
  "extract_technical": true,
  "extract_soft": true
}
```

#### List Analyses
```http
GET /api/analysis-enhanced/list?page=1&limit=10
```

#### CV-specific Analyses
```http
GET /api/analysis-enhanced/cv/{cv_id}/analyses
```

#### JD-specific Analyses
```http
GET /api/analysis-enhanced/jd/{jd_id}/analyses
```

## 🔍 Analysis Types

### 1. Skill Match Analysis
- Compares technical and soft skills between CV and JD
- Identifies matched, missing, and additional skills
- Provides match percentage and suggestions

### 2. Experience Match Analysis
- Evaluates experience level and relevance
- Analyzes years of experience and role seniority
- Provides experience scoring and recommendations

### 3. Overall Fit Analysis
- Combines skill and experience analysis
- Generates comprehensive fit score and level
- Provides detailed recommendations for improvement

## 🧪 Testing

The project includes a comprehensive test suite (`test_enhanced_api.py`) that validates:

- ✅ API health and connectivity
- ✅ CV upload and text extraction
- ✅ JD extraction from text and URLs
- ✅ CV-JD analysis and skill matching
- ✅ Skill extraction from arbitrary text

Run tests with:
```bash
python test_enhanced_api.py
```

## 🌐 Supported Job Sites

The JD extractor supports the following job posting websites:

- **Seek.com.au** - Australia's #1 job site
- **Indeed.com** - Global job search engine
- **LinkedIn.com** - Professional networking platform
- **EthicalJobs.com.au** - Purpose-driven job board
- **Generic sites** - Fallback extraction for other sites

## 💾 Database Schema

The enhanced database includes the following main tables:

- **cvs**: CV metadata and processing status
- **cv_content**: Extracted CV text content
- **jds**: Job description metadata
- **jd_content**: Extracted JD text content
- **analyses**: Analysis requests and results
- **analysis_results**: Detailed analysis outcomes

## 🔒 Security Features

- **File Type Validation**: Only allows PDF, DOCX, TXT uploads
- **File Size Limits**: 10MB max for CV uploads, 50KB for text
- **Input Sanitization**: All text inputs are validated and cleaned
- **Error Handling**: Comprehensive error handling and logging

## 📊 Performance Optimizations

- **Background Processing**: Long-running tasks use background jobs
- **Async Operations**: Non-blocking I/O operations
- **Pagination**: Efficient data retrieval with pagination
- **Caching**: Results caching for improved response times
- **File Storage**: Efficient file storage and retrieval system

## 🚀 Future Enhancements

### Planned Features
1. **AI-Powered Analysis**: Integration with GPT/Claude for advanced text analysis
2. **Resume Optimization**: AI-driven suggestions for CV improvements
3. **Industry-Specific Matching**: Tailored analysis for different industries
4. **Real-time Processing**: WebSocket support for real-time status updates
5. **Advanced Scraping**: Support for more job sites and dynamic content
6. **Export Features**: Generate reports in PDF/DOCX format
7. **Bulk Operations**: Batch processing for multiple CVs/JDs
8. **Analytics Dashboard**: Comprehensive statistics and insights

### Integration Points
- **Mobile App**: Flutter frontend integration
- **Email Integration**: Automated notifications and reports
- **Calendar Integration**: Interview scheduling and tracking
- **Job Application Tracking**: Complete application lifecycle management

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Issues**: Check file permissions for storage directory
   ```bash
   mkdir -p storage
   chmod 755 storage
   ```

3. **File Upload Issues**: Verify file size and type restrictions

4. **Web Scraping Failures**: Some sites may block automated requests

### Debugging

Enable debug logging by setting `DEBUG=True` in your environment or configuration.

## 📞 Support

For issues or questions about the enhanced backend:

1. Check the test suite output for specific error details
2. Review server logs for debugging information
3. Ensure all dependencies are correctly installed
4. Verify database permissions and storage directory access

---

## 📈 API Usage Examples

### Complete Workflow Example

```python
import aiohttp
import asyncio

async def complete_workflow_example():
    async with aiohttp.ClientSession() as session:
        # 1. Upload CV
        with open('my_cv.pdf', 'rb') as cv_file:
            data = aiohttp.FormData()
            data.add_field('cv_file', cv_file, filename='my_cv.pdf')
            data.add_field('title', 'My Professional CV')
            
            async with session.post('http://localhost:8000/api/cv-enhanced/upload', data=data) as resp:
                cv_result = await resp.json()
                cv_id = cv_result['id']
        
        # 2. Extract JD from URL
        jd_payload = {
            "url": "https://seek.com.au/job/123456789",
            "title": "Senior Software Engineer"
        }
        async with session.post('http://localhost:8000/api/jd-enhanced/extract', json=jd_payload) as resp:
            jd_result = await resp.json()
            jd_id = jd_result['id']
        
        # 3. Wait for processing (in real app, use webhooks or polling)
        await asyncio.sleep(5)
        
        # 4. Perform analysis
        analysis_payload = {
            "cv_id": cv_id,
            "jd_id": jd_id,
            "analysis_type": "overall_fit"
        }
        async with session.post('http://localhost:8000/api/analysis-enhanced/analyze', json=analysis_payload) as resp:
            analysis_result = await resp.json()
            analysis_id = analysis_result['id']
        
        # 5. Get analysis results
        await asyncio.sleep(3)
        async with session.get(f'http://localhost:8000/api/analysis-enhanced/{analysis_id}') as resp:
            final_result = await resp.json()
            print(f"Match Score: {final_result['result']['overall_score']}%")
            print(f"Fit Level: {final_result['result']['fit_level']}")

# Run the example
asyncio.run(complete_workflow_example())
```

This enhanced backend provides a solid foundation for building sophisticated CV analysis and job matching applications with modern web technologies and best practices.
