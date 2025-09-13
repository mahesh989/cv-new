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
      print('📡 [SERVICE_DEBUG] Raw result type: ${result.runtimeType}');
      print('📡 [SERVICE_DEBUG] Raw result: $result');
      print('   Response keys: ${result.keys.toList()}');
      print(
          '   cv_comprehensive_analysis present: ${result.containsKey("cv_comprehensive_analysis")}');
      print(
          '   jd_comprehensive_analysis present: ${result.containsKey("jd_comprehensive_analysis")}');
      print(
          '🔍 [ANALYZE_MATCH_SERVICE] analyze_match present: ${result.containsKey("analyze_match")}');
      if (result.containsKey('analyze_match')) {
        final analyzeMatch = result['analyze_match'] as Map<String, dynamic>?;
        print('🔍 [ANALYZE_MATCH_SERVICE] analyze_match data: $analyzeMatch');
        if (analyzeMatch != null) {
          print(
              '🔍 [ANALYZE_MATCH_SERVICE] raw_analysis length: ${(analyzeMatch['raw_analysis'] as String?)?.length ?? 0}');
          print(
              '🔍 [ANALYZE_MATCH_SERVICE] company_name: ${analyzeMatch['company_name']}');
          print(
              '🔍 [ANALYZE_MATCH_SERVICE] has error: ${analyzeMatch.containsKey('error')}');
        }
      }
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
      print(
          '🔍 [ANALYZE_MATCH_SERVICE] analyzeMatch in parsed result: ${analysisResult.analyzeMatch != null}');
      if (analysisResult.analyzeMatch != null) {
        print(
            '🔍 [ANALYZE_MATCH_SERVICE] analyzeMatch raw analysis length: ${analysisResult.analyzeMatch!.rawAnalysis.length}');
        print(
            '🔍 [ANALYZE_MATCH_SERVICE] analyzeMatch company name: ${analysisResult.analyzeMatch!.companyName}');
      }

      // Return with execution duration
      final finalResult = SkillsAnalysisResult(
        cvSkills: analysisResult.cvSkills,
        jdSkills: analysisResult.jdSkills,
        cvComprehensiveAnalysis: analysisResult.cvComprehensiveAnalysis,
        jdComprehensiveAnalysis: analysisResult.jdComprehensiveAnalysis,
        expandableAnalysis: analysisResult.expandableAnalysis,
        extractedKeywords: analysisResult.extractedKeywords,
        analyzeMatch: analysisResult.analyzeMatch,
        executionDuration: stopwatch.elapsed,
        isSuccess: true,
        // carry pre-extracted comparison fields through to the UI
        preextractedRawOutput: analysisResult.preextractedRawOutput,
        preextractedCompanyName: analysisResult.preextractedCompanyName,
      );

      print(
          '🔍 [SERVICE_DEBUG] Final result analyzeMatch: ${finalResult.analyzeMatch != null}');
      if (finalResult.analyzeMatch != null) {
        print(
            '🔍 [SERVICE_DEBUG] Final result analyzeMatch raw analysis length: ${finalResult.analyzeMatch!.rawAnalysis.length}');
      }

      return finalResult;
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
        print('🔍 [CACHE_DEBUG] Found cached results');
        print(
            '🔍 [CACHE_DEBUG] Cached data keys: ${result['data'].keys.toList()}');
        print(
            '🔍 [CACHE_DEBUG] Cached analyze_match present: ${result['data'].containsKey('analyze_match')}');
        final cachedResult = SkillsAnalysisResult.fromJson(result['data']);
        print(
            '🔍 [CACHE_DEBUG] Parsed cached analyzeMatch: ${cachedResult.analyzeMatch != null}');
        if (cachedResult.analyzeMatch != null) {
          print(
              '🔍 [CACHE_DEBUG] Cached analyzeMatch raw analysis length: ${cachedResult.analyzeMatch!.rawAnalysis.length}');
        }
        return cachedResult;
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

  /// Poll for complete analysis results (component analysis + ATS)
  static Future<Map<String, dynamic>?> getCompleteAnalysisResults(String company) async {
    try {
      print('📊 [POLLING] Checking for complete results for company: $company');
      
      final result = await APIService.makeAuthenticatedCall(
        endpoint: '/analysis-results/$company',
        method: 'GET',
      );
      
      if (result['success'] == true && result['data'] != null) {
        final data = result['data'] as Map<String, dynamic>;
        print('📊 [POLLING] Component analysis present: ${data.containsKey("component_analysis")}');
        print('📊 [POLLING] ATS score present: ${data.containsKey("ats_score")}');
        
        if (data.containsKey('component_analysis') && data.containsKey('ats_score')) {
          print('✅ [POLLING] Complete results found!');
          return data;
        } else {
          print('⏳ [POLLING] Still waiting for complete results...');
          return null;
        }
      }
      
      return null;
    } catch (e) {
      print('❌ [POLLING] Error getting complete results: $e');
      return null;
    }
  }

  /// Wait for complete analysis results with polling
  static Future<Map<String, dynamic>?> waitForCompleteResults(String company, {int maxWaitTimeSeconds = 30}) async {
    print('🔄 [POLLING] Starting polling for complete results...');
    
    const pollInterval = Duration(seconds: 2);
    final maxAttempts = maxWaitTimeSeconds ~/ 2;
    
    for (int attempt = 1; attempt <= maxAttempts; attempt++) {
      print('🔄 [POLLING] Attempt $attempt/$maxAttempts');
      
      final completeResults = await getCompleteAnalysisResults(company);
      if (completeResults != null) {
        print('✅ [POLLING] Complete results obtained after ${attempt * 2} seconds');
        return completeResults;
      }
      
      if (attempt < maxAttempts) {
        print('⏳ [POLLING] Waiting ${pollInterval.inSeconds}s before next attempt...');
        await Future.delayed(pollInterval);
      }
    }
    
    print('⚠️ [POLLING] Polling timed out after $maxWaitTimeSeconds seconds');
    return null;
  }
}
