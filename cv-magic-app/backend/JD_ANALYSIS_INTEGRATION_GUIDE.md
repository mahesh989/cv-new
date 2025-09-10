# Job Description Analysis Integration Guide

This guide explains how to integrate the new Job Description Analysis functionality into your Flutter app.

## Overview

The JD Analysis system provides:
- ✅ **Centralized AI-powered keyword extraction**
- ✅ **Automatic caching and file saving**
- ✅ **Flutter-friendly API endpoints**
- ✅ **Required vs Preferred keyword classification**
- ✅ **Integration with existing AI service**

## API Endpoints

### 1. Analyze Job Description
```http
POST /api/analyze-jd/{company_name}
```

**Parameters:**
- `company_name`: Company identifier (e.g., "Australia_for_UNHCR")
- `force_refresh`: Boolean (optional, default: false)
- `temperature`: Float (optional, default: 0.3)

**Response:**
```json
{
  "success": true,
  "message": "Job description analysis completed for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "required_keywords": ["SQL", "Power BI", "Excel", "Python"],
    "preferred_keywords": ["Tableau", "Machine Learning", "Cloud Platforms"],
    "all_keywords": ["SQL", "Power BI", "Excel", "Python", "Tableau", "Machine Learning", "Cloud Platforms"],
    "experience_years": 3,
    "analysis_timestamp": "2024-01-15T10:30:00",
    "ai_model_used": "openai/gpt-4o-mini",
    "processing_status": "completed",
    "from_cache": false
  },
  "metadata": {
    "analysis_duration": "N/A",
    "ai_service_status": {...},
    "saved_path": "/path/to/jd_analysis.json"
  }
}
```

### 2. Get Saved Analysis
```http
GET /api/jd-analysis/{company_name}
```

**Response:**
```json
{
  "success": true,
  "message": "Analysis results retrieved for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "required_keywords": ["SQL", "Power BI", "Excel"],
    "preferred_keywords": ["Tableau", "Python"],
    "all_keywords": ["SQL", "Power BI", "Excel", "Tableau", "Python"],
    "experience_years": 3,
    "analysis_timestamp": "2024-01-15T10:30:00",
    "ai_model_used": "openai/gpt-4o-mini",
    "processing_status": "completed"
  },
  "metadata": {
    "from_cache": true,
    "analysis_age": "N/A"
  }
}
```

### 3. Get Keywords Only
```http
GET /api/jd-analysis/{company_name}/keywords?keyword_type=all
```

**Parameters:**
- `keyword_type`: "all", "required", or "preferred"

**Response:**
```json
{
  "success": true,
  "message": "Retrieved all keywords for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "keyword_type": "all",
    "keywords": ["SQL", "Power BI", "Excel", "Tableau", "Python"],
    "count": 5
  },
  "metadata": {
    "analysis_timestamp": "2024-01-15T10:30:00",
    "ai_model_used": "openai/gpt-4o-mini"
  }
}
```

### 4. Check Analysis Status
```http
GET /api/jd-analysis/{company_name}/status
```

**Response:**
```json
{
  "success": true,
  "message": "Status retrieved for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "analysis_exists": true,
    "jd_file_exists": true,
    "can_analyze": true,
    "needs_analysis": false,
    "analysis_timestamp": "2024-01-15T10:30:00",
    "ai_model_used": "openai/gpt-4o-mini",
    "keyword_counts": {
      "required": 3,
      "preferred": 2,
      "total": 5
    }
  }
}
```

### 5. Delete Analysis
```http
DELETE /api/jd-analysis/{company_name}
```

**Response:**
```json
{
  "success": true,
  "message": "Analysis deleted for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "deleted_file": "/path/to/jd_analysis.json"
  }
}
```

## Flutter Integration Examples

### 1. Basic Analysis Service

```dart
class JDAnalysisService {
  static const String baseUrl = 'http://your-backend-url';
  
  Future<Map<String, dynamic>> analyzeJD(String companyName, {bool forceRefresh = false}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/analyze-jd/$companyName'),
        headers: await _getHeaders(),
        body: jsonEncode({
          'force_refresh': forceRefresh,
          'temperature': 0.3,
        }),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Analysis failed: ${response.statusCode}');
      }
    } catch (e) {
      print('Error analyzing JD: $e');
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> getAnalysis(String companyName) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/jd-analysis/$companyName'),
        headers: await _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to get analysis: ${response.statusCode}');
      }
    } catch (e) {
      print('Error getting analysis: $e');
      rethrow;
    }
  }
  
  Future<List<String>> getKeywords(String companyName, {String type = 'all'}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/jd-analysis/$companyName/keywords?keyword_type=$type'),
        headers: await _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['data']['keywords']);
      } else {
        throw Exception('Failed to get keywords: ${response.statusCode}');
      }
    } catch (e) {
      print('Error getting keywords: $e');
      rethrow;
    }
  }
  
  Future<Map<String, dynamic>> _getHeaders() async {
    // Add your authentication headers here
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer your-token-here',
    };
  }
}
```

### 2. Flutter Widget Example

```dart
class JDAnalysisWidget extends StatefulWidget {
  final String companyName;
  
  const JDAnalysisWidget({Key? key, required this.companyName}) : super(key: key);
  
  @override
  _JDAnalysisWidgetState createState() => _JDAnalysisWidgetState();
}

class _JDAnalysisWidgetState extends State<JDAnalysisWidget> {
  final JDAnalysisService _service = JDAnalysisService();
  Map<String, dynamic>? _analysisData;
  bool _isLoading = false;
  String? _error;
  
  @override
  void initState() {
    super.initState();
    _loadAnalysis();
  }
  
  Future<void> _loadAnalysis() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    
    try {
      // Try to get existing analysis first
      final data = await _service.getAnalysis(widget.companyName);
      setState(() {
        _analysisData = data;
        _isLoading = false;
      });
    } catch (e) {
      // If no analysis exists, perform new analysis
      try {
        final data = await _service.analyzeJD(widget.companyName);
        setState(() {
          _analysisData = data;
          _isLoading = false;
        });
      } catch (analysisError) {
        setState(() {
          _error = analysisError.toString();
          _isLoading = false;
        });
      }
    }
  }
  
  Future<void> _refreshAnalysis() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    
    try {
      final data = await _service.analyzeJD(widget.companyName, forceRefresh: true);
      setState(() {
        _analysisData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('JD Analysis - ${widget.companyName}'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _refreshAnalysis,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }
  
  Widget _buildBody() {
    if (_isLoading) {
      return Center(child: CircularProgressIndicator());
    }
    
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error, size: 64, color: Colors.red),
            SizedBox(height: 16),
            Text('Error: $_error'),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadAnalysis,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }
    
    if (_analysisData == null) {
      return Center(child: Text('No analysis data available'));
    }
    
    final data = _analysisData!['data'];
    final requiredKeywords = List<String>.from(data['required_keywords'] ?? []);
    final preferredKeywords = List<String>.from(data['preferred_keywords'] ?? []);
    
    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAnalysisInfo(data),
          SizedBox(height: 24),
          _buildKeywordsSection('Required Keywords', requiredKeywords, Colors.red),
          SizedBox(height: 16),
          _buildKeywordsSection('Preferred Keywords', preferredKeywords, Colors.orange),
        ],
      ),
    );
  }
  
  Widget _buildAnalysisInfo(Map<String, dynamic> data) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Analysis Information',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            SizedBox(height: 8),
            Text('Company: ${data['company_name']}'),
            Text('Experience Required: ${data['experience_years'] ?? 'N/A'} years'),
            Text('AI Model: ${data['ai_model_used']}'),
            Text('Analysis Date: ${data['analysis_timestamp']}'),
            if (data['from_cache'] == true)
              Chip(
                label: Text('From Cache'),
                backgroundColor: Colors.blue.shade100,
              ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildKeywordsSection(String title, List<String> keywords, Color color) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(color: color),
            ),
            SizedBox(height: 8),
            if (keywords.isEmpty)
              Text('No keywords found', style: TextStyle(color: Colors.grey))
            else
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: keywords.map((keyword) => Chip(
                  label: Text(keyword),
                  backgroundColor: color.withOpacity(0.1),
                  side: BorderSide(color: color),
                )).toList(),
              ),
          ],
        ),
      ),
    );
  }
}
```

## File Structure

The system creates the following file structure:

```
backend/cv-analysis/
├── Australia_for_UNHCR/
│   ├── jd_original.txt          # Original job description
│   └── jd_analysis.json         # Analysis results
├── Company_Name_2/
│   ├── jd_original.txt
│   └── jd_analysis.json
└── ...
```

## Saved Analysis Format

The `jd_analysis.json` file contains:

```json
{
  "required_keywords": ["SQL", "Power BI", "Excel"],
  "preferred_keywords": ["Tableau", "Python"],
  "all_keywords": ["SQL", "Power BI", "Excel", "Tableau", "Python"],
  "experience_years": 3,
  "analysis_timestamp": "2024-01-15T10:30:00",
  "ai_model_used": "openai/gpt-4o-mini",
  "processing_status": "completed",
  "raw_data": {
    "required_keywords": ["SQL", "Power BI", "Excel"],
    "preferred_keywords": ["Tableau", "Python"],
    "all_keywords": ["SQL", "Power BI", "Excel", "Tableau", "Python"],
    "experience_years": 3
  }
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `401`: Authentication required
- `404`: Analysis or file not found
- `500`: Internal server error

Error responses include:
```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly message"
}
```

## Caching Strategy

- **Automatic caching**: Results are automatically saved to JSON files
- **Cache checking**: API checks for existing analysis before re-processing
- **Force refresh**: Use `force_refresh=true` to bypass cache
- **File-based**: Cache persists across server restarts

## Testing

Run the test script to verify everything works:

```bash
cd backend
python test_jd_analysis.py
```

This will test:
- File structure validation
- JD analysis functionality
- Caching and loading
- AI service integration
- Direct text analysis

## Integration Checklist

- [ ] ✅ Files placed in correct locations
- [ ] ✅ Routes added to main.py
- [ ] ✅ AI service integration working
- [ ] ✅ File saving/loading functional
- [ ] ✅ API endpoints responding correctly
- [ ] ✅ Error handling implemented
- [ ] ✅ Authentication integrated
- [ ] ✅ Flutter service created
- [ ] ✅ Testing completed
- [ ] ✅ Documentation updated
