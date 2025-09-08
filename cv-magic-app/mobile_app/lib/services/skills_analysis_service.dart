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
    try {
      final stopwatch = Stopwatch()..start();
      
      final result = await APIService.makeAuthenticatedCall(
        endpoint: '/preliminary-analysis',
        method: 'POST',
        body: {
          'cv_filename': cvFilename,
          'jd_text': jdText,
        },
      );
      
      stopwatch.stop();
      
      final analysisResult = SkillsAnalysisResult.fromJson(result);
      
      // Return with execution duration
      return SkillsAnalysisResult(
        cvSkills: analysisResult.cvSkills,
        jdSkills: analysisResult.jdSkills,
        cvComprehensiveAnalysis: analysisResult.cvComprehensiveAnalysis,
        jdComprehensiveAnalysis: analysisResult.jdComprehensiveAnalysis,
        extractedKeywords: analysisResult.extractedKeywords,
        executionDuration: stopwatch.elapsed,
        isSuccess: true,
      );
    } catch (e) {
      return SkillsAnalysisResult.error('Failed to perform skills analysis: $e');
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
      return 'Please select a CV file first';
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
