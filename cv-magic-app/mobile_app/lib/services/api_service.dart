import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:file_picker/file_picker.dart';
import 'ai_model_service.dart';
import 'auth_service.dart';

class APIService {
  static const String baseUrl = 'https://cvagent.duckdns.org';
  static const String apiPrefix = '/api';

  // Get the current selected model from AI service
  static String? get currentModelId => aiModelService.currentModelId;

  // Get auth token from shared preferences (deprecated - use AuthService)
  static Future<String?> _getAuthToken() async {
    return await AuthService.getValidAuthToken();
  }

  // Make authenticated API call with current model
  static Future<Map<String, dynamic>> makeAuthenticatedCall({
    required String endpoint,
    required String method,
    Map<String, dynamic>? body,
    Map<String, String>? headers,
  }) async {
    final token = await _getAuthToken();
    final url = Uri.parse('$baseUrl$apiPrefix$endpoint');

    print('🔍 [API_SERVICE] Making authenticated call to: $endpoint');
    print('🔍 [API_SERVICE] Token available: ${token != null}');
    print(
      '🔍 [API_SERVICE] Token preview: ${token?.substring(0, 20) ?? "null"}...',
    );

    final requestHeaders = {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
      // Include current model in headers if available
      if (currentModelId != null) 'X-Current-Model': currentModelId!,
      ...?headers,
    };

    http.Response response;

    switch (method.toUpperCase()) {
      case 'GET':
        response = await http.get(url, headers: requestHeaders);
        break;
      case 'POST':
        response = await http.post(
          url,
          headers: requestHeaders,
          body: body != null ? jsonEncode(body) : null,
        );
        break;
      case 'PUT':
        response = await http.put(
          url,
          headers: requestHeaders,
          body: body != null ? jsonEncode(body) : null,
        );
        break;
      case 'DELETE':
        response = await http.delete(url, headers: requestHeaders);
        break;
      default:
        throw Exception('Unsupported HTTP method: $method');
    }

    print('🔍 [API_SERVICE] Response status: ${response.statusCode}');
    print(
      '🔍 [API_SERVICE] Response body preview: ${response.body.substring(0, response.body.length > 200 ? 200 : response.body.length)}...',
    );

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body);
    } else {
      // Try to parse error response for better error handling
      try {
        final errorData = jsonDecode(response.body);
        if (errorData is Map<String, dynamic> &&
            errorData.containsKey('error')) {
          // Use the clean error message directly
          throw Exception(errorData['error']);
        }
      } catch (e) {
        // If we can't parse the error, fall back to original behavior
        rethrow; // Re-throw our custom error
      }

      throw Exception(
        'API call failed: ${response.statusCode} - ${response.body}',
      );
    }
  }

  // AI-specific API calls that automatically use current model
  static Future<Map<String, dynamic>> chatCompletion({
    required String prompt,
    String? systemPrompt,
    double temperature = 0.7,
    int? maxTokens,
  }) async {
    return await makeAuthenticatedCall(
      endpoint: '/ai/chat',
      method: 'POST',
      body: {
        'prompt': prompt,
        'system_prompt': systemPrompt,
        'temperature': temperature,
        'max_tokens': maxTokens,
        // Model is automatically included via headers
      },
    );
  }

  static Future<Map<String, dynamic>> analyzeCV({
    required String cvText,
    String? jobDescription,
  }) async {
    return await makeAuthenticatedCall(
      endpoint: '/ai/analyze-cv',
      method: 'POST',
      body: {
        'cv_text': cvText,
        'job_description': jobDescription,
        // Model is automatically included via headers
      },
    );
  }

  static Future<Map<String, dynamic>> compareJob({
    required String cvText,
    required String jobDescription,
  }) async {
    return await makeAuthenticatedCall(
      endpoint: '/ai/compare-job',
      method: 'POST',
      body: {
        'cv_text': cvText,
        'job_description': jobDescription,
        // Model is automatically included via headers
      },
    );
  }

  // Generic AI completion with current model
  static Future<Map<String, dynamic>> aiCompletion({
    required String prompt,
    String? systemPrompt,
    Map<String, dynamic>? additionalParams,
  }) async {
    final body = {
      'prompt': prompt,
      'system_prompt': systemPrompt,
      ...?additionalParams,
    };

    return await makeAuthenticatedCall(
      endpoint: '/ai/chat',
      method: 'POST',
      body: body,
    );
  }

  // Get current AI status
  static Future<Map<String, dynamic>> getAIStatus() async {
    return await makeAuthenticatedCall(endpoint: '/ai/status', method: 'GET');
  }

  // Switch model (this will also update the frontend service)
  static Future<Map<String, dynamic>> switchModel(String modelId) async {
    final result = await makeAuthenticatedCall(
      endpoint: '/ai/switch-model',
      method: 'POST',
      body: {'model': modelId},
    );

    // Update frontend service to match backend
    await aiModelService.changeModel(modelId);

    return result;
  }

  // CV Upload functionality
  static Future<void> uploadCV(PlatformFile file) async {
    final token = await _getAuthToken();
    final url = Uri.parse('$baseUrl$apiPrefix/cv/upload');

    final request = http.MultipartRequest('POST', url);

    // Add auth header
    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }

    // Add current model header if available
    if (currentModelId != null) {
      request.headers['X-Current-Model'] = currentModelId!;
    }

    // Replace if exists: backend will overwrite on same filename. We still send the file normally.
    request.files.add(
      http.MultipartFile.fromBytes('cv', file.bytes!, filename: file.name),
    );

    final response = await request.send();

    if (response.statusCode >= 200 && response.statusCode < 300) {
      // Success
      return;
    } else {
      final responseBody = await response.stream.bytesToString();
      throw Exception(
        'CV upload failed: ${response.statusCode} - $responseBody',
      );
    }
  }

  // List uploaded CVs
  static Future<List<String>> fetchUploadedCVs() async {
    final result = await makeAuthenticatedCall(
      endpoint: '/cv/list',
      method: 'GET',
    );

    return List<String>.from(result['uploaded_cvs'] ?? []);
  }

  // Check if a CV filename already exists on the backend
  static Future<bool> cvExists(String filename) async {
    final list = await fetchUploadedCVs();
    return list.contains(filename);
  }

  // Save selected CV for analysis: creates original_cv.txt and original_cv.json
  static Future<void> saveCVForAnalysis(String filename) async {
    await makeAuthenticatedCall(
      endpoint: '/cv/save-for-analysis/$filename',
      method: 'POST',
    );
  }

  // Job Description functionality
  static Future<String?> scrapeJobDescription(String url) async {
    try {
      final result = await makeAuthenticatedCall(
        endpoint: '/job/scrape',
        method: 'POST',
        body: {'url': url},
      );
      return result['job_description'];
    } catch (e) {
      throw Exception('Failed to scrape job description: $e');
    }
  }

  static Future<Map<String, dynamic>> extractJobMetadata(
    String jobDescription,
  ) async {
    return await makeAuthenticatedCall(
      endpoint: '/job/extract-metadata',
      method: 'POST',
      body: {'job_description': jobDescription},
    );
  }

  // Job Analysis functionality
  static Future<Map<String, dynamic>> extractAndSaveJob({
    required String jobDescription,
    String? jobUrl,
  }) async {
    return await makeAuthenticatedCall(
      endpoint: '/job-analysis/extract-and-save',
      method: 'POST',
      body: {'job_description': jobDescription, 'job_url': jobUrl},
    );
  }

  static Future<List<Map<String, dynamic>>> listAnalyzedJobs() async {
    final result = await makeAuthenticatedCall(
      endpoint: '/job-analysis/list',
      method: 'GET',
    );
    return List<Map<String, dynamic>>.from(result['jobs'] ?? []);
  }

  static Future<Map<String, dynamic>> getJobInfo(String companySlug) async {
    return await makeAuthenticatedCall(
      endpoint: '/job-analysis/job-info/$companySlug',
      method: 'GET',
    );
  }

  static Future<void> deleteJobAnalysis(String companySlug) async {
    await makeAuthenticatedCall(
      endpoint: '/job-analysis/delete/$companySlug',
      method: 'DELETE',
    );
  }
}

// Convenience class for AI operations
class AIAPI {
  static Future<String> generateText({
    required String prompt,
    String? systemPrompt,
    double temperature = 0.7,
  }) async {
    final response = await APIService.chatCompletion(
      prompt: prompt,
      systemPrompt: systemPrompt,
      temperature: temperature,
    );

    return response['content'] ?? '';
  }

  static Future<Map<String, dynamic>> analyzeResume({
    required String resumeText,
    String? jobDescription,
  }) async {
    return await APIService.analyzeCV(
      cvText: resumeText,
      jobDescription: jobDescription,
    );
  }

  static Future<Map<String, dynamic>> matchJob({
    required String resumeText,
    required String jobDescription,
  }) async {
    return await APIService.compareJob(
      cvText: resumeText,
      jobDescription: jobDescription,
    );
  }
}
