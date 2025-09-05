import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import '../utils/ai_model_utils.dart';

class ApiService {
  // Use localhost for development, change to production URL when deploying
  static const String _baseUrl = 'http://localhost:8000';

  static String get baseUrl => _baseUrl;

  /// Helper method to add current AI model information to request headers
  Map<String, String> _getModelAwareHeaders() {
    final modelInfo = AIModelUtils.getCurrentModelForAPI();
    return {
      'Content-Type': 'application/json',
      'X-AI-Model': modelInfo['model'],
      'X-AI-Provider': modelInfo['provider'],
    };
  }

  /// Helper method to add model information to request body
  Map<String, dynamic> _addModelToRequestBody(Map<String, dynamic> body) {
    final modelInfo = AIModelUtils.getCurrentModelForAPI();
    return {
      ...body,
      'ai_model': modelInfo['model'],
      'ai_provider': modelInfo['provider'],
    };
  }

  // Use 10.0.2.2 for Android emulator, localhost for iOS simulator
  // final String baseUrl =
  //     Platform.isAndroid ? 'http://10.0.2.2:8000' : 'http://localhost:8000';

  Future<void> uploadCv(PlatformFile file) async {
    final uri = Uri.parse('$baseUrl/upload-cv/');
    final request = http.MultipartRequest('POST', uri);
    request.files.add(http.MultipartFile.fromBytes(
      'cv',
      file.bytes!,
      filename: file.name,
    ));
    final response = await request.send();
    if (response.statusCode != 200) {
      throw Exception('CV upload failed');
    }
  }

  Future<List<String>> fetchUploadedCVs() async {
    final response = await http.get(Uri.parse('$baseUrl/list-cvs/'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return List<String>.from(data['uploaded_cvs'] ?? []);
    }
    return [];
  }

  Future<String> fetchPrompt() async {
    final response = await http.get(Uri.parse('$baseUrl/get-prompt/'));
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['prompt'] ?? 'Default analysis prompt';
    }
    return 'Default analysis prompt';
  }

  Future<String> fetchJobDescription(String url) async {
    final response = await http.post(
      Uri.parse('$baseUrl/scrape-job-description/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'url': url}),
    );
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['job_description'] ?? '';
    }
    return '';
  }

  /// Save analysis results to file
  Future<Map<String, dynamic>> saveAnalysisResults({
    required String cvFilename,
    required String jdText,
    required Map<String, dynamic> analysisData,
  }) async {
    try {
      print('💾 [FRONTEND] Saving analysis results to file...');
      print('📄 CV Filename: $cvFilename');
      print('📝 JD Text Length: ${jdText.length} characters');

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
        print('⚠️ [FRONTEND] Could not extract company name: $e');
        companyName = 'Unknown_Company';
      }

      // Prepare data in the format expected by backend
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

      print('📦 [FRONTEND] Analysis data keys: ${analysisData.keys.toList()}');
      print(
          '📦 [FRONTEND] Skill comparison type: ${analysisData['skill_comparison']?.runtimeType}');
      print(
          '📦 [FRONTEND] ATS results type: ${analysisData['ats_results']?.runtimeType}');

      print('📦 [FRONTEND] Request data keys: ${requestData.keys.toList()}');

      final response = await http.post(
        Uri.parse('$baseUrl/api/save-analysis-results'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(requestData),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('✅ [FRONTEND] Analysis results saved successfully');
        print('📁 File saved: ${data['filename'] ?? 'Unknown'}');
        return data;
      } else {
        print(
            '❌ [FRONTEND] Failed to save analysis results: ${response.statusCode}');
        print('📄 Response: ${response.body}');
        throw Exception(
            'Failed to save analysis results: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ [FRONTEND] Error saving analysis results: $e');
      rethrow;
    }
  }

  Future<MatchResult> analyzeMatch({
    required String cvFilename,
    required String jdText,
    required String prompt,
  }) async {
    print('\n${'=' * 80}');
    print('🔍 [FRONTEND] ANALYZE MATCH - START');
    print('=' * 80);
    print('📄 CV Filename: $cvFilename');
    print('📝 JD Text Length: ${jdText.length} characters');
    print(
        '📝 JD Text Preview: ${jdText.length > 200 ? jdText.substring(0, 200) : jdText}...');
    print('🎯 Prompt Length: ${prompt.length} characters');
    print(
        '🎯 Prompt Preview: ${prompt.length > 200 ? prompt.substring(0, 200) : prompt}...');

    try {
      print('\n🔧 [FRONTEND] Testing backend connectivity...');
      // Test backend connectivity first
      final healthCheck = await http
          .get(Uri.parse('$baseUrl/'))
          .timeout(const Duration(seconds: 5));
      if (healthCheck.statusCode != 200) {
        print(
            '❌ [FRONTEND] Backend health check failed: ${healthCheck.statusCode}');
        throw Exception('Backend server is not responding');
      }
      print('✅ [FRONTEND] Backend connectivity confirmed');

      print('\n🚀 [FRONTEND] Sending analyze-fit request to backend...');
      print('📡 [FRONTEND] Endpoint: $baseUrl/analyze-fit/');
      print('📦 [FRONTEND] Request body:');
      print('   cv_filename: $cvFilename');
      print('   text length: ${jdText.length}');
      print('   prompt length: ${prompt.length}');

      final response = await http.post(
        Uri.parse('$baseUrl/analyze-fit/'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'cv_filename': cvFilename,
          'text': jdText,
          'prompt': prompt,
        },
      ).timeout(const Duration(seconds: 120));

      print('\n📥 [FRONTEND] Response received from backend:');
      print('📊 [FRONTEND] Status Code: ${response.statusCode}');
      print(
          '📏 [FRONTEND] Response Body Length: ${response.body.length} characters');

      if (response.statusCode == 200) {
        print('✅ [FRONTEND] Success response received');
        print('📝 [FRONTEND] Response body preview (first 500 chars):');
        print('-' * 50);
        print(response.body.length > 500
            ? response.body.substring(0, 500)
            : response.body);
        print('-' * 50);

        final data = json.decode(response.body);

        print('\n🔄 [FRONTEND] Parsing JSON response:');
        print('📊 [FRONTEND] JSON keys: ${data.keys.toList()}');
        if (data.containsKey('raw_analysis')) {
          print(
              '📝 [FRONTEND] Raw analysis length: ${data['raw_analysis'].toString().length}');
        }
        if (data.containsKey('formatted_result')) {
          print('📋 [FRONTEND] Formatted result: ${data['formatted_result']}');
        }

        final matchResult = MatchResult.fromJson(data);

        print('\n💾 [FRONTEND] MatchResult created:');
        print('   📄 Raw analysis length: ${matchResult.raw.length}');
        print('   🏷️ Keywords count: ${matchResult.keywords.length}');
        print('   🔑 Key phrases count: ${matchResult.keyPhrases.length}');
        print('   📝 Raw analysis preview (first 300 chars):');
        print(
            '   ${matchResult.raw.length > 300 ? matchResult.raw.substring(0, 300) : matchResult.raw}...');

        print('=' * 80);
        print('🔍 [FRONTEND] ANALYZE MATCH - SUCCESS');
        print('=' * 80 + '\n');

        return matchResult;
      } else {
        print('❌ [FRONTEND] Error response from backend:');
        print('   Status: ${response.statusCode}');
        print('   Body: ${response.body}');
        print('=' * 80);
        print('🔍 [FRONTEND] ANALYZE MATCH - ERROR');
        print('=' * 80 + '\n');
        throw Exception(
            'Server error: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('\n❌ [FRONTEND] Exception in analyzeMatch:');
      print('   Error type: ${e.runtimeType}');
      print('   Error message: ${e.toString()}');
      print('=' * 80);
      print('🔍 [FRONTEND] ANALYZE MATCH - EXCEPTION');
      print('=' * 80 + '\n');

      if (e.toString().contains('TimeoutException')) {
        throw Exception(
            'Request timed out. Please check your connection and try again.');
      } else if (e.toString().contains('SocketException')) {
        throw Exception(
            'Cannot connect to server. Please ensure the backend is running.');
      } else {
        throw Exception('Analysis failed: ${e.toString()}');
      }
    }
  }

  Future<ATSResult> atsTest({
    required String cvFilename,
    required String jdText,
    required String prompt,
    required String cvType,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/ats-test/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'cv_filename': cvFilename,
        'jd_text': jdText,
        'prompt': prompt,
        'cv_type': cvType,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ATSResult.fromJson(data);
    } else {
      throw Exception('ATS test failed: ${response.body}');
    }
  }

  // REMOVED: Old CV extraction method - using dynamic extraction only

  // REMOVED: Old JD extraction method - using dynamic extraction only

  // Dynamic skill extraction using Claude-based extractor
  Future<Map<String, dynamic>> extractSkillsDynamic({
    required String mode, // "cv" or "jd"
    String? cvFilename,
    String? jdUrl,
    String? jdText,
  }) async {
    final url = Uri.parse('$baseUrl/extract-skills-dynamic/');
    final payload = {
      'mode': mode,
      if (cvFilename != null) 'cv_filename': cvFilename,
      if (jdText != null) 'jd_text': jdText,
      if (jdUrl != null) 'jd_url': jdUrl,
    };
    debugPrint('[ApiService] Sending POST to $url with payload: $payload');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );
      debugPrint('[ApiService] Response status: ${response.statusCode}');
      debugPrint('[ApiService] Response body: ${response.body}');
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);

        if (data.containsKey('error')) {
          throw Exception('Skill extraction error: ${data['error']}');
        }

        // Return all fields, including comprehensive_analysis and raw_response
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
    } catch (e) {
      debugPrint('[ApiService] Error in extractSkillsDynamic: ${e.toString()}');
      rethrow;
    }
  }

  // Parse resume using Claude API
  Future<Map<String, dynamic>> parseResume(PlatformFile file) async {
    try {
      final uri = Uri.parse('$baseUrl/parse-resume/');
      final request = http.MultipartRequest('POST', uri);

      request.files.add(http.MultipartFile.fromBytes(
        'file',
        file.bytes!,
        filename: file.name,
      ));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        final data = json.decode(responseBody);
        return data;
      } else {
        throw Exception(
            'Resume parsing failed: ${response.statusCode} - $responseBody');
      }
    } catch (e) {
      throw Exception('Error parsing resume: $e');
    }
  }

  // Parse already uploaded CV by filename
  Future<Map<String, dynamic>> parseUploadedCV(String filename) async {
    try {
      final uri = Uri.parse('$baseUrl/parse-uploaded-cv/');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {'cv_filename': filename},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data;
      } else {
        throw Exception(
            'CV parsing failed: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Error parsing uploaded CV: $e');
    }
  }

  // Preliminary Analysis - Run both CV and JD skill extraction
  Future<Map<String, dynamic>> preliminaryAnalysis({
    required String cvFilename,
    required String jdText,
  }) async {
    final url = Uri.parse('$baseUrl/preliminary-analysis/');
    final payload = {
      'cv_filename': cvFilename,
      'jd_text': jdText,
    };
    debugPrint('[ApiService] Sending POST to $url with payload: $payload');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );
      debugPrint('[ApiService] Response status: ${response.statusCode}');
      debugPrint('[ApiService] Response body: ${response.body}');
      if (response.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(response.body);

        if (data.containsKey('error')) {
          throw Exception('Preliminary analysis error: ${data['error']}');
        }

        return data;
      } else {
        throw Exception('Failed to run preliminary analysis: ${response.body}');
      }
    } catch (e) {
      debugPrint('[ApiService] Error in preliminaryAnalysis: ${e.toString()}');
      rethrow;
    }
  }

  // Compare skills and keywords between CV and JD
  Future<Map<String, dynamic>> compareSkills(Map<String, dynamic> data) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/compare-skills'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to compare skills: ${response.statusCode}');
    }
  }
}

class MatchResult {
  final String raw;
  final List<String> keywords;
  final List<String> keyPhrases;

  MatchResult({
    required this.raw,
    required this.keywords,
    required this.keyPhrases,
  });

  factory MatchResult.fromJson(Map<String, dynamic> data) {
    final raw = _stripMarkdown(data['raw_analysis'] ?? '');

    final formatted = data['formatted_result'] ?? {};

    List<String> kw = [];
    if (formatted['keywords'] is List) {
      kw = List<String>.from(formatted['keywords']);
    }

    List<String> phrases = [];
    if (formatted['key_phrases'] is List) {
      phrases = List<String>.from(formatted['key_phrases']);
    }

    return MatchResult(
      raw: raw,
      keywords: kw,
      keyPhrases: phrases,
    );
  }

  static String _stripMarkdown(String input) {
    return input.replaceAllMapped(
        RegExp(r'\*\*(.*?)\*\*'), (match) => match.group(1)!);
  }
}

class ATSResult {
  final int keywordMatch;
  final int skillsMatch;
  final int overallScore;
  final List<String> matchedKeywords;
  final List<String> matchedSkills;
  final List<String> gaps;
  final List<String> tips;

  final List<String> matchedHardSkills;
  final List<String> matchedSoftSkills;
  final List<String> matchedExtraKeywords;
  final List<String> missedHardSkills;
  final List<String> missedSoftSkills;
  final List<String> missedOtherKeywords;

  ATSResult({
    required this.keywordMatch,
    required this.skillsMatch,
    required this.overallScore,
    required this.matchedKeywords,
    required this.matchedSkills,
    required this.gaps,
    required this.tips,
    required this.matchedHardSkills,
    required this.matchedSoftSkills,
    required this.matchedExtraKeywords,
    required this.missedHardSkills,
    required this.missedSoftSkills,
    required this.missedOtherKeywords,
  });

  factory ATSResult.fromJson(Map<String, dynamic> json) {
    return ATSResult(
      keywordMatch: json['keyword_match'] ?? 0,
      skillsMatch: json['skills_match'] ?? 0,
      overallScore: json['overall_score'] ?? 0,
      matchedKeywords: List<String>.from(json['matched_keywords'] ?? []),
      matchedSkills: List<String>.from(json['matched_skills'] ?? []),
      gaps: List<String>.from(json['gaps'] ?? []),
      tips: List<String>.from(json['tips'] ?? []),
      matchedHardSkills: List<String>.from(json['matched_hard_skills'] ?? []),
      matchedSoftSkills: List<String>.from(json['matched_soft_skills'] ?? []),
      matchedExtraKeywords:
          List<String>.from(json['matched_extra_keywords'] ?? []),
      missedHardSkills: List<String>.from(json['missed_hard_skills'] ?? []),
      missedSoftSkills: List<String>.from(json['missed_soft_skills'] ?? []),
      missedOtherKeywords:
          List<String>.from(json['missed_other_keywords'] ?? []),
    );
  }
}
