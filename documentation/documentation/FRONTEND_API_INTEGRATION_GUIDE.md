# Frontend API Integration Guide for Analysis Results

## API Response Structure

The `/api/analysis-results/{company}` endpoint returns data in the following structure:

```json
{
  "success": true,
  "data": {
    "company": "GfK",
    "skills_analysis": {
      "cv_skills": { ... },
      "jd_skills": { ... }
    },
    "preextracted_comparison": { ... },
    "component_analysis": { ... },
    "ats_score": {
      "timestamp": "2025-09-13T17:11:07.443",
      "final_ats_score": 70.15,
      "category_status": "⚠️ Moderate fit",
      "recommendation": "Consider if other factors are strong",
      "breakdown": {
        "category1": {
          "score": 25.3,
          "technical_skills_match_rate": 90.0,
          "domain_keywords_match_rate": 14.0,
          "soft_skills_match_rate": 44.0,
          "missing_counts": {
            "technical": 1,
            "domain": 6,
            "soft": 5
          }
        },
        "category2": {
          "score": 46.45,
          "core_competency_avg": 83.75,
          "experience_seniority_avg": 71.0,
          "potential_ability_avg": 78.75,
          "company_fit_avg": 68.75
        },
        "ats1_score": 71.75,
        "bonus_points": -1.6
      }
    }
  }
}
```

## Frontend Integration Examples

### JavaScript/React Example

```javascript
// Service function to fetch analysis results
async function fetchAnalysisResults(company) {
  try {
    const response = await fetch(`/api/analysis-results/${company}`, {
      headers: {
        'Authorization': `Bearer ${getAuthToken()}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Check if the response is successful and has data
    if (result.success && result.data) {
      return result.data;  // Return the data object
    } else {
      throw new Error(result.error || 'Failed to fetch analysis results');
    }
  } catch (error) {
    console.error('Error fetching analysis results:', error);
    throw error;
  }
}

// Component usage
function AnalysisResultsComponent({ company }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    async function loadResults() {
      try {
        setLoading(true);
        const analysisData = await fetchAnalysisResults(company);
        setData(analysisData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    
    loadResults();
  }, [company]);
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data available</div>;
  
  // Display ATS Score
  const { ats_score } = data;
  
  return (
    <div>
      {ats_score && (
        <div className="ats-score-section">
          <h2>ATS Score Analysis</h2>
          <div className="score-display">
            <span className="score">{ats_score.final_ats_score.toFixed(1)}</span>
            <span className="status">{ats_score.category_status}</span>
          </div>
          <p className="recommendation">{ats_score.recommendation}</p>
          
          <div className="breakdown">
            <h3>Match Rates</h3>
            <ul>
              <li>Technical Skills: {ats_score.breakdown.category1.technical_skills_match_rate}%</li>
              <li>Soft Skills: {ats_score.breakdown.category1.soft_skills_match_rate}%</li>
              <li>Domain Keywords: {ats_score.breakdown.category1.domain_keywords_match_rate}%</li>
            </ul>
            
            <h3>Component Scores</h3>
            <ul>
              <li>Core Competency: {ats_score.breakdown.category2.core_competency_avg}%</li>
              <li>Experience & Seniority: {ats_score.breakdown.category2.experience_seniority_avg}%</li>
              <li>Potential & Ability: {ats_score.breakdown.category2.potential_ability_avg}%</li>
              <li>Company Fit: {ats_score.breakdown.category2.company_fit_avg}%</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Flutter/Dart Example

```dart
// Service class
class AnalysisApiService {
  static Future<Map<String, dynamic>> fetchAnalysisResults(String company) async {
    final uri = Uri.parse('${API_BASE_URL}/api/analysis-results/$company');
    
    try {
      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer ${getAuthToken()}',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        final Map<String, dynamic> result = json.decode(response.body);
        
        // Check if the response is successful and has data
        if (result['success'] == true && result['data'] != null) {
          return result['data'];  // Return the data object
        } else {
          throw Exception(result['error'] ?? 'Failed to fetch analysis results');
        }
      } else {
        throw Exception('Failed to load analysis results: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching analysis results: $e');
      rethrow;
    }
  }
}

// Widget usage
class AnalysisResultsWidget extends StatelessWidget {
  final Map<String, dynamic> analysisData;
  
  const AnalysisResultsWidget({Key? key, required this.analysisData}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    final atsScore = analysisData['ats_score'];
    
    if (atsScore == null) {
      return Text('No ATS score available');
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ATS Score: ${atsScore['final_ats_score'].toStringAsFixed(1)}',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
        ),
        Text(
          atsScore['category_status'],
          style: TextStyle(fontSize: 18, color: _getStatusColor(atsScore['category_status'])),
        ),
        Text(
          atsScore['recommendation'],
          style: TextStyle(fontSize: 16),
        ),
        SizedBox(height: 20),
        _buildMatchRates(atsScore['breakdown']['category1']),
        SizedBox(height: 20),
        _buildComponentScores(atsScore['breakdown']['category2']),
      ],
    );
  }
  
  Widget _buildMatchRates(Map<String, dynamic> category1) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Match Rates:', style: TextStyle(fontWeight: FontWeight.bold)),
        Text('Technical Skills: ${category1['technical_skills_match_rate']}%'),
        Text('Soft Skills: ${category1['soft_skills_match_rate']}%'),
        Text('Domain Keywords: ${category1['domain_keywords_match_rate']}%'),
      ],
    );
  }
  
  Widget _buildComponentScores(Map<String, dynamic> category2) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Component Scores:', style: TextStyle(fontWeight: FontWeight.bold)),
        Text('Core Competency: ${category2['core_competency_avg']}%'),
        Text('Experience & Seniority: ${category2['experience_seniority_avg']}%'),
        Text('Potential & Ability: ${category2['potential_ability_avg']}%'),
        Text('Company Fit: ${category2['company_fit_avg']}%'),
      ],
    );
  }
  
  Color _getStatusColor(String status) {
    if (status.contains('Excellent')) return Colors.green;
    if (status.contains('Good')) return Colors.blue;
    if (status.contains('Moderate')) return Colors.orange;
    return Colors.red;
  }
}
```

## Key Points for Frontend Implementation

1. **Response Structure**: The API returns data wrapped in a `success` and `data` structure
2. **Error Handling**: Always check `result.success` before accessing `result.data`
3. **ATS Score Path**: Access ATS score at `result.data.ats_score`
4. **Null Checks**: ATS score may be null if analysis hasn't completed yet
5. **Number Formatting**: Format scores to 1 decimal place for display

## Error Handling

```javascript
// Handle different error scenarios
if (!result.success) {
  // API returned an error
  console.error('API Error:', result.error);
} else if (!result.data) {
  // No data available
  console.error('No data in response');
} else if (!result.data.ats_score) {
  // ATS calculation not yet complete
  console.log('ATS score not yet available, try triggering complete pipeline');
}
```

## Triggering Complete Pipeline

If ATS scores are missing, trigger the complete pipeline:

```javascript
async function triggerCompletePipeline(company) {
  const response = await fetch(`/api/trigger-complete-pipeline/${company}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAuthToken()}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (response.ok) {
    const result = await response.json();
    console.log('Pipeline completed:', result);
    // Wait a moment then fetch updated results
    setTimeout(() => fetchAnalysisResults(company), 1000);
  }
}
```
