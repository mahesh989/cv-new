import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'background_api_service.dart';
import 'api_service.dart';

/// Enhanced API service that uses background processing to handle tab switching
class EnhancedApiService extends ApiService {
  final BackgroundApiService _bgService = BackgroundApiService();
  final JobApiService _jobService = JobApiService();
  
  static final EnhancedApiService _instance = EnhancedApiService._internal();
  factory EnhancedApiService() => _instance;
  EnhancedApiService._internal() {
    _bgService.initialize();
  }

  @override
  Future<MatchResult> analyzeMatch({
    required String cvFilename,
    required String jdText,
    required String prompt,
  }) async {
    debugPrint('🔍 [Enhanced] Starting analyze match with background support');
    
    try {
      // For long-running analysis, use job-based approach
      final result = await _jobService.executeJob(
        jobType: 'analyze_match',
        jobData: {
          'cv_filename': cvFilename,
          'jd_text': jdText,
          'prompt': prompt,
        },
      );
      
      if (result['status'] == 'completed') {
        return MatchResult.fromJson(result['result']);
      } else {
        throw Exception('Analysis job failed: ${result['error']}');
      }
    } catch (e) {
      debugPrint('⚠️ [Enhanced] Job-based analysis failed, falling back to direct API: $e');
      
      // Fallback to direct API call with background support
      return _analyzeMatchDirect(
        cvFilename: cvFilename,
        jdText: jdText,
        prompt: prompt,
      );
    }
  }

  Future<MatchResult> _analyzeMatchDirect({
    required String cvFilename,
    required String jdText,
    required String prompt,
  }) async {
    debugPrint('🔄 [Enhanced] Direct API analysis with background support');
    
    final response = await _bgService.post(
      '${ApiService.baseUrl}/analyze-fit/',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'cv_filename=$cvFilename&text=${Uri.encodeComponent(jdText)}&prompt=${Uri.encodeComponent(prompt)}',
      timeout: const Duration(seconds: 180), // Extended timeout
      critical: true, // Mark as critical for background processing
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return MatchResult.fromJson(data);
    } else {
      throw Exception('Server error: ${response.statusCode} - ${response.body}');
    }
  }

  @override
  Future<ATSResult> atsTest({
    required String cvFilename,
    required String jdText,
    required String prompt,
    required String cvType,
  }) async {
    debugPrint('🔍 [Enhanced] Starting ATS test with background support');
    
    try {
      // Use job-based approach for ATS testing
      final result = await _jobService.executeJob(
        jobType: 'ats_test',
        jobData: {
          'cv_filename': cvFilename,
          'jd_text': jdText,
          'prompt': prompt,
          'cv_type': cvType,
        },
      );
      
      if (result['status'] == 'completed') {
        return ATSResult.fromJson(result['result']);
      } else {
        throw Exception('ATS test job failed: ${result['error']}');
      }
    } catch (e) {
      debugPrint('⚠️ [Enhanced] Job-based ATS test failed, falling back to direct API: $e');
      
      // Fallback to direct API call with background support
      return _atsTestDirect(
        cvFilename: cvFilename,
        jdText: jdText,
        prompt: prompt,
        cvType: cvType,
      );
    }
  }

  Future<ATSResult> _atsTestDirect({
    required String cvFilename,
    required String jdText,
    required String prompt,
    required String cvType,
  }) async {
    debugPrint('🔄 [Enhanced] Direct ATS test with background support');
    
    final response = await _bgService.post(
      '${ApiService.baseUrl}/ats-test/',
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'cv_filename': cvFilename,
        'jd_text': jdText,
        'prompt': prompt,
        'cv_type': cvType,
      }),
      timeout: const Duration(seconds: 180),
      critical: true,
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ATSResult.fromJson(data);
    } else {
      throw Exception('ATS test failed: ${response.body}');
    }
  }

  @override
  Future<Map<String, dynamic>> extractSkillsDynamic({
    required String mode,
    String? cvFilename,
    String? jdUrl,
    String? jdText,
  }) async {
    debugPrint('🔍 [Enhanced] Extracting skills dynamically with background support');
    
    final payload = {
      'mode': mode,
      if (cvFilename != null) 'cv_filename': cvFilename,
      if (jdText != null) 'jd_text': jdText,
      if (jdUrl != null) 'jd_url': jdUrl,
    };

    final response = await _bgService.post(
      '${ApiService.baseUrl}/extract-skills-dynamic/',
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(payload),
      timeout: const Duration(seconds: 120),
      critical: false,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);

      if (data.containsKey('error')) {
        throw Exception('Skill extraction error: ${data['error']}');
      }

      return {
        'soft_skills': List<String>.from(data['soft_skills'] ?? []),
        'technical_skills': List<String>.from(data['technical_skills'] ?? []),
        'domain_keywords': List<String>.from(data['domain_keywords'] ?? []),
        'comprehensive_analysis': data['comprehensive_analysis'] ?? '',
        'raw_response': data['raw_response'] ?? '',
      };
    } else {
      throw Exception('Failed to extract skills: ${response.body}');
    }
  }

  @override
  Future<Map<String, dynamic>> preliminaryAnalysis({
    required String cvFilename,
    required String jdText,
  }) async {
    debugPrint('🔍 [Enhanced] Running preliminary analysis with background support');
    
    try {
      // Use job-based approach for preliminary analysis
      final result = await _jobService.executeJob(
        jobType: 'preliminary_analysis',
        jobData: {
          'cv_filename': cvFilename,
          'jd_text': jdText,
        },
      );
      
      if (result['status'] == 'completed') {
        return result['result'];
      } else {
        throw Exception('Preliminary analysis job failed: ${result['error']}');
      }
    } catch (e) {
      debugPrint('⚠️ [Enhanced] Job-based preliminary analysis failed, falling back: $e');
      
      // Fallback to direct API call
      return _preliminaryAnalysisDirect(
        cvFilename: cvFilename,
        jdText: jdText,
      );
    }
  }

  Future<Map<String, dynamic>> _preliminaryAnalysisDirect({
    required String cvFilename,
    required String jdText,
  }) async {
    final response = await _bgService.post(
      '${ApiService.baseUrl}/preliminary-analysis/',
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'cv_filename': cvFilename,
        'jd_text': jdText,
      }),
      timeout: const Duration(seconds: 120),
      critical: false,
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);

      if (data.containsKey('error')) {
        throw Exception('Preliminary analysis error: ${data['error']}');
      }

      return data;
    } else {
      throw Exception('Failed to run preliminary analysis: ${response.body}');
    }
  }

  @override
  Future<String> fetchJobDescription(String url) async {
    debugPrint('🔍 [Enhanced] Fetching job description with background support');
    
    final response = await _bgService.post(
      '${ApiService.baseUrl}/scrape-job-description/',
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'url': url}),
      timeout: const Duration(seconds: 60),
      critical: false,
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['job_description'] ?? '';
    }
    return '';
  }

  @override
  Future<Map<String, dynamic>> saveAnalysisResults({
    required String cvFilename,
    required String jdText,
    required Map<String, dynamic> analysisData,
  }) async {
    debugPrint('💾 [Enhanced] Saving analysis results with background support');
    
    // Extract company name from JD text
    String? companyName;
    try {
      final lines = jdText.split('\n');
      for (final line in lines) {
        if (line.toLowerCase().contains('company') ||
            line.toLowerCase().contains('organization') ||
            line.toLowerCase().contains('about')) {
          companyName = line.trim();
          break;
        }
      }
    } catch (e) {
      companyName = 'Unknown_Company';
    }

    final requestData = {
      'cv_text': analysisData['cv_text'] ?? 'CV content from $cvFilename',
      'jd_text': jdText,
      'skill_comparison': analysisData['skill_comparison'] ??
          analysisData['skill_comparison_output'] ??
          {'status': 'completed'},
      'ats_results': analysisData['ats_results'] ??
          analysisData['enhanced_ats_results'] ??
          analysisData,
      'company_name': companyName,
    };

    final response = await _bgService.post(
      '${ApiService.baseUrl}/api/save-analysis-results',
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(requestData),
      timeout: const Duration(seconds: 60),
      critical: true, // Mark as critical since this saves user work
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      debugPrint('✅ [Enhanced] Analysis results saved successfully');
      return data;
    } else {
      throw Exception('Failed to save analysis results: ${response.statusCode}');
    }
  }

  /// Upload CV with background support
  @override
  Future<void> uploadCv(PlatformFile file) async {
    debugPrint('📤 [Enhanced] Uploading CV with background support');
    
    // Note: Multipart uploads are more complex with our background service
    // For now, we'll use the standard upload but with enhanced error handling
    try {
      final uri = Uri.parse('${ApiService.baseUrl}/upload-cv/');
      final request = http.MultipartRequest('POST', uri);
      request.files.add(http.MultipartFile.fromBytes(
        'cv',
        file.bytes!,
        filename: file.name,
      ));
      
      // Add background request headers
      request.headers.addAll({
        'X-Keep-Alive': 'true',
        'X-Background-Request': 'true',
      });
      
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);
      
      if (response.statusCode != 200) {
        throw Exception('CV upload failed: ${response.statusCode}');
      }
      
      debugPrint('✅ [Enhanced] CV uploaded successfully');
    } catch (e) {
      debugPrint('❌ [Enhanced] CV upload failed: $e');
      rethrow;
    }
  }

  /// Get service status including background service status
  Map<String, dynamic> getServiceStatus() {
    final bgStatus = _bgService.getStatus();
    return {
      'enhanced_api_service': 'active',
      'background_service': bgStatus,
      'job_service': 'active',
    };
  }

  /// Cleanup resources
  void dispose() {
    _bgService.dispose();
  }
}

/// Singleton instance for easy access throughout the app
final enhancedApiService = EnhancedApiService();
