import 'package:http/http.dart' as http;
import 'dart:convert';

class LLMService {
  // Use localhost for development, change to production URL when deploying
  static const String _baseUrl = 'http://localhost:8000';
  final String baseUrl;

  LLMService({this.baseUrl = _baseUrl});

  // Optimize CV based on ATS results
  Future<String> optimizeCV({
    required String cvContent,
    required Map<String, dynamic> atsResult,
    required String jobDescription,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/llm/optimize-cv'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'cv_content': cvContent,
          'ats_result': atsResult,
          'job_description': jobDescription,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['optimized_cv'] as String;
      } else {
        throw Exception('Failed to optimize CV: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error optimizing CV: $e');
    }
  }

  // Get improvement suggestions
  Future<List<String>> getImprovementSuggestions({
    required String cvContent,
    required Map<String, dynamic> atsResult,
    required String jobDescription,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/llm/suggestions'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'cv_content': cvContent,
          'ats_result': atsResult,
          'job_description': jobDescription,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<String>.from(data['suggestions'] ?? []);
      } else {
        throw Exception('Failed to get suggestions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting suggestions: $e');
    }
  }

  // Generate targeted improvements for specific skills
  Future<String> generateTargetedImprovement({
    required String cvContent,
    required List<String> missingSkills,
    required String jobDescription,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/llm/targeted-improvement'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'cv_content': cvContent,
          'missing_skills': missingSkills,
          'job_description': jobDescription,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['improved_cv'] as String;
      } else {
        throw Exception(
            'Failed to generate targeted improvement: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error generating targeted improvement: $e');
    }
  }

  // Analyze CV content and provide feedback
  Future<Map<String, dynamic>> analyzeCVContent({
    required String cvContent,
    required String jobDescription,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/llm/analyze'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'cv_content': cvContent,
          'job_description': jobDescription,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception('Failed to analyze CV: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error analyzing CV: $e');
    }
  }

  // Generate CV summary
  Future<String> generateCVSummary({
    required String cvContent,
    required String jobDescription,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/llm/summary'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'cv_content': cvContent,
          'job_description': jobDescription,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['summary'] as String;
      } else {
        throw Exception('Failed to generate summary: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error generating summary: $e');
    }
  }

  // Get keyword optimization suggestions
  Future<List<String>> getKeywordSuggestions({
    required String cvContent,
    required String jobDescription,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/llm/keywords'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'cv_content': cvContent,
          'job_description': jobDescription,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<String>.from(data['keywords'] ?? []);
      } else {
        throw Exception(
            'Failed to get keyword suggestions: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error getting keyword suggestions: $e');
    }
  }

  // Extract job information (title and company) from job description
  Future<Map<String, String?>> extractJobInformation({
    required String jobDescription,
  }) async {
    try {
      print(
          '🌐 LLM Service: Making request to $baseUrl/api/llm/extract-job-info');
      print('📄 LLM Service: JD length: ${jobDescription.length}');

      final response = await http
          .post(
            Uri.parse('$baseUrl/api/llm/extract-job-info'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'job_description': jobDescription,
            }),
          )
          .timeout(const Duration(seconds: 30));

      print('📡 LLM Service: Response status: ${response.statusCode}');
      print('📡 LLM Service: Response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as Map<String, dynamic>;

        final result = {
          'jobTitle': data['job_title'] as String?,
          'company': data['company'] as String?,
        };

        print(
            '✅ LLM Service: Extracted - Title: "${result['jobTitle']}", Company: "${result['company']}"');
        return result;
      } else {
        print('❌ LLM Service: HTTP ${response.statusCode} - ${response.body}');
        throw Exception(
            'Failed to extract job info: HTTP ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('❌ LLM Service: Exception - $e');
      if (e.toString().contains('SocketException') ||
          e.toString().contains('Connection refused')) {
        throw Exception(
            'LLM API server is not running. Please start the backend server at $baseUrl');
      } else if (e.toString().contains('TimeoutException')) {
        throw Exception(
            'LLM API request timed out. The server may be overloaded.');
      } else {
        throw Exception('Error extracting job info: $e');
      }
    }
  }
}
