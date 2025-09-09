import 'dart:convert';
import '../models/skills_analysis_model.dart';
import 'api_service.dart';

/// Service for handling skills analysis (preliminary analysis) operations
class SkillsAnalysisService {
  /// Perform preliminary analysis to extract skills from CV and JD
  static Future<SkillsAnalysisResult> performPreliminaryAnalysis({
    required String cvFilename,
    required String jdText,
  }) async {
    print('=== FRONTEND SERVICE CALLED ===');
    print('CV: $cvFilename');
    print('JD length: ${jdText.length}');
    try {
      print('🚀 [SERVICE_DEBUG] Starting performPreliminaryAnalysis');
      print('   CV: $cvFilename');
      print('   JD text length: ${jdText.length}');

      final stopwatch = Stopwatch()..start();

      final result = await APIService.makeAuthenticatedCall(
        endpoint: '/preliminary-analysis',
        method: 'POST',
        body: {
          'cv_filename': cvFilename,
          'jd_text': jdText,
        },
      );

      print('📡 [SERVICE_DEBUG] Received response from API');
      print('   Response type: ${result.runtimeType}');
      print('   Response keys: ${result.keys.toList()}');
      print(
          '   cv_comprehensive_analysis present: ${result.containsKey("cv_comprehensive_analysis")}');
      print(
          '   jd_comprehensive_analysis present: ${result.containsKey("jd_comprehensive_analysis")}');
      if (result.containsKey('cv_comprehensive_analysis')) {
        final cvAnalysis = result['cv_comprehensive_analysis'] as String?;
        print(
            '   cv_comprehensive_analysis length: ${cvAnalysis?.length ?? 0}');
      }
      if (result.containsKey('jd_comprehensive_analysis')) {
        final jdAnalysis = result['jd_comprehensive_analysis'] as String?;
        print(
            '   jd_comprehensive_analysis length: ${jdAnalysis?.length ?? 0}');
      }

      stopwatch.stop();

      print('📊 [SERVICE_DEBUG] About to parse SkillsAnalysisResult from JSON');
      final analysisResult = SkillsAnalysisResult.fromJson(result);
      print('📊 [SERVICE_DEBUG] Successfully parsed SkillsAnalysisResult');
      print(
          '   CV comprehensive analysis length: ${analysisResult.cvComprehensiveAnalysis?.length ?? 0}');
      print(
          '   JD comprehensive analysis length: ${analysisResult.jdComprehensiveAnalysis?.length ?? 0}');

      // Return with execution duration
      return SkillsAnalysisResult(
        cvSkills: analysisResult.cvSkills,
        jdSkills: analysisResult.jdSkills,
        cvComprehensiveAnalysis: analysisResult.cvComprehensiveAnalysis,
        jdComprehensiveAnalysis: analysisResult.jdComprehensiveAnalysis,
        expandableAnalysis: analysisResult.expandableAnalysis,
        extractedKeywords: analysisResult.extractedKeywords,
        executionDuration: stopwatch.elapsed,
        isSuccess: true,
      );
    } catch (e, stackTrace) {
      print('❌ [SERVICE_ERROR] Exception in performPreliminaryAnalysis: $e');
      print('❌ [SERVICE_ERROR] Stack trace: $stackTrace');

      // Enhanced error handling for CV not found
      if (e.toString().contains('404') || e.toString().contains('not found')) {
        return SkillsAnalysisResult.error(
            'CV file not found. Please upload a CV file first.');
      } else if (e.toString().contains('401')) {
        return SkillsAnalysisResult.error(
            'Authentication required. Please log in again.');
      } else if (e.toString().contains('500')) {
        return SkillsAnalysisResult.error(
            'Server error. Please try again later.');
      } else {
        return SkillsAnalysisResult.error(
            'Failed to perform skills analysis: $e');
      }
    }
  }

  /// Check if skills analysis results are cached for given inputs
  static Future<SkillsAnalysisResult?> getCachedAnalysis({
    required String cvFilename,
    required String jdText,
  }) async {
    try {
      // Try to get cached results from the backend
      final result = await APIService.makeAuthenticatedCall(
        endpoint: '/preliminary-analysis/cache',
        method: 'GET',
        body: {
          'cv_filename': cvFilename,
          'jd_text_hash': _generateTextHash(jdText),
        },
      );

      if (result['cached'] == true) {
        return SkillsAnalysisResult.fromJson(result['data']);
      }

      return null;
    } catch (e) {
      // If cache retrieval fails, just return null to proceed with fresh analysis
      return null;
    }
  }

  /// Generate a simple hash for JD text for caching purposes
  static String _generateTextHash(String text) {
    return text.hashCode.toString();
  }

  /// Validate inputs for skills analysis
  static String? validateAnalysisInputs({
    required String? cvFilename,
    required String? jdText,
  }) {
    if (cvFilename == null || cvFilename.trim().isEmpty) {
      return 'Please select a CV file first. Upload a CV file using the CV upload feature.';
    }

    if (jdText == null || jdText.trim().isEmpty) {
      return 'Please enter a job description';
    }

    if (jdText.trim().length < 50) {
      return 'Job description seems too short. Please provide more details.';
    }

    return null; // No validation errors
  }

  /// Get analysis status - useful for showing progress
  static Future<Map<String, dynamic>?> getAnalysisStatus() async {
    try {
      return await APIService.makeAuthenticatedCall(
        endpoint: '/preliminary-analysis/status',
        method: 'GET',
      );
    } catch (e) {
      return null;
    }
  }
}
