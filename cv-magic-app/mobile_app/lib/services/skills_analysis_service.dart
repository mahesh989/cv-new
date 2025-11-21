import '../models/skills_analysis_model.dart';
import 'api_service.dart';

/// Exception to signal polling should stop (e.g., 404 file not found)
class _PollingStopException implements Exception {
  final String message;
  _PollingStopException(this.message);
  @override
  String toString() => message;
}

/// Service for handling skills analysis (preliminary analysis) operations
class SkillsAnalysisService {
  /// Perform context-aware analysis with intelligent CV selection and JD caching
  static Future<SkillsAnalysisResult> performContextAwareAnalysis({
    required String jdUrl,
    required String company,
    required bool isRerun,
    bool includeTailoring = true,
  }) async {
    print('=== CONTEXT-AWARE ANALYSIS SERVICE CALLED ===');
    print('JD URL: $jdUrl');
    print('Company: $company');
    print('Is Rerun: $isRerun');
    print('Include Tailoring: $includeTailoring');

    try {
      print('🚀 [CONTEXT_AWARE_SERVICE] Starting context-aware analysis');

      final stopwatch = Stopwatch()..start();

      final result = await APIService.makeAuthenticatedCall(
        endpoint: '/context-aware-analysis',
        method: 'POST',
        body: {
          'jd_url': jdUrl,
          'company': company,
          'is_rerun': isRerun,
          'include_tailoring': includeTailoring,
        },
      );

      print('📡 [CONTEXT_AWARE_SERVICE] Received response from API');
      print(
          '📡 [CONTEXT_AWARE_SERVICE] Raw result type: ${result.runtimeType}');
      print(
          '📡 [CONTEXT_AWARE_SERVICE] Raw result keys: ${result.keys.toList()}');

      stopwatch.stop();

      // Convert context-aware result to SkillsAnalysisResult format
      final analysisResult = _convertContextAwareResult(result);
      print(
          '📊 [CONTEXT_AWARE_SERVICE] Successfully converted to SkillsAnalysisResult');

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
        preextractedRawOutput: analysisResult.preextractedRawOutput,
        preextractedCompanyName: analysisResult.preextractedCompanyName,
      );

      return finalResult;
    } catch (e, stackTrace) {
      print(
          '❌ [CONTEXT_AWARE_SERVICE] Exception in performContextAwareAnalysis: $e');
      print('❌ [CONTEXT_AWARE_SERVICE] Stack trace: $stackTrace');

      // Enhanced error handling for different error types
      if (e.toString().contains('404') || e.toString().contains('not found')) {
        return SkillsAnalysisResult.error(
            'Analysis resources not found. Please check your inputs.');
      } else if (e.toString().contains('401')) {
        return SkillsAnalysisResult.error(
            'Authentication required. Please log in again.');
      } else if (e.toString().contains('500')) {
        return SkillsAnalysisResult.error(
            'Server error. Please try again later.');
      } else {
        // Try to extract just the error message from API responses
        String errorMsg = e.toString();
        if (errorMsg.contains('{"error":"') && errorMsg.contains('"}')) {
          // Extract clean error message from JSON response
          final start = errorMsg.indexOf('{"error":"') + 10;
          final end = errorMsg.indexOf('"}', start);
          if (end > start) {
            errorMsg = errorMsg.substring(start, end);
            return SkillsAnalysisResult.error(errorMsg);
          }
        }
        return SkillsAnalysisResult.error(
            'Failed to perform context-aware analysis: $e');
      }
    }
  }

  /// Perform preliminary analysis to extract skills from CV and JD (legacy method)
  static Future<SkillsAnalysisResult> performPreliminaryAnalysis({
    required String cvFilename,
    required String jdText,
    String? jdUrl, // NEW: Add URL parameter (optional)
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
          'jd_url': jdUrl ?? '', // NEW: Add URL if available
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

      // Enhanced error handling for different error types
      if (e.toString().contains('404') || e.toString().contains('not found')) {
        return SkillsAnalysisResult.error(
            'CV file not found. Please upload a CV file first.');
      } else if (e.toString().contains('401')) {
        return SkillsAnalysisResult.error(
            'Authentication required. Please log in again.');
      } else if (e.toString().contains('500')) {
        return SkillsAnalysisResult.error(
            'Server error. Please try again later.');
      } else if (e.toString().contains('analyze the job description first')) {
        return SkillsAnalysisResult.error(
            'Please analyze the job description first before running skills analysis.');
      } else {
        // Try to extract just the error message from API responses
        String errorMsg = e.toString();
        if (errorMsg.contains('{"error":"') && errorMsg.contains('"}')) {
          // Extract clean error message from JSON response
          final start = errorMsg.indexOf('{"error":"') + 10;
          final end = errorMsg.indexOf('"}', start);
          if (end > start) {
            errorMsg = errorMsg.substring(start, end);
            return SkillsAnalysisResult.error(errorMsg);
          }
        }
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

  /// Convert context-aware analysis result to SkillsAnalysisResult format
  static SkillsAnalysisResult _convertContextAwareResult(
      Map<String, dynamic> result) {
    final results = result['results'] as Map<String, dynamic>? ?? {};
    final analysisContext =
        result['analysis_context'] as Map<String, dynamic>? ?? {};

    // Extract CV skills
    final cvSkillsData = results['cv_skills'] as Map<String, dynamic>? ?? {};
    final cvSkills = SkillsData(
      technicalSkills:
          List<String>.from(cvSkillsData['technical_skills'] ?? []),
      softSkills: List<String>.from(cvSkillsData['soft_skills'] ?? []),
      domainKeywords: List<String>.from(cvSkillsData['domain_keywords'] ?? []),
    );

    // Extract JD skills
    final jdSkillsData = results['jd_skills'] as Map<String, dynamic>? ?? {};
    final jdSkills = SkillsData(
      technicalSkills:
          List<String>.from(jdSkillsData['technical_skills'] ?? []),
      softSkills: List<String>.from(jdSkillsData['soft_skills'] ?? []),
      domainKeywords: List<String>.from(jdSkillsData['domain_keywords'] ?? []),
    );

    // Extract comprehensive analysis
    final cvComprehensiveAnalysis =
        cvSkillsData['comprehensive_analysis'] as String?;
    final jdComprehensiveAnalysis =
        jdSkillsData['comprehensive_analysis'] as String?;

    // Extract analyze match if available
    final cvJdMatching =
        results['cv_jd_matching'] as Map<String, dynamic>? ?? {};
    AnalyzeMatchResult? analyzeMatch;
    if (cvJdMatching.isNotEmpty) {
      analyzeMatch = AnalyzeMatchResult(
        rawAnalysis: cvJdMatching['raw_analysis'] ?? '',
        companyName: analysisContext['company'] ?? '',
        filePath: cvJdMatching['file_path'],
        error: cvJdMatching['has_error'] == true ? 'Analysis error' : null,
      );
    }

    // Extract keywords
    final extractedKeywords =
        List<String>.from(cvSkillsData['extracted_keywords'] ?? []);

    return SkillsAnalysisResult(
      cvSkills: cvSkills,
      jdSkills: jdSkills,
      cvComprehensiveAnalysis: cvComprehensiveAnalysis,
      jdComprehensiveAnalysis: jdComprehensiveAnalysis,
      expandableAnalysis: null, // Not available in context-aware result
      extractedKeywords: extractedKeywords,
      analyzeMatch: analyzeMatch,
      executionDuration: Duration.zero, // Will be set by caller
      isSuccess: result['success'] ?? false,
      preextractedRawOutput: null, // Not available in context-aware result
      preextractedCompanyName: analysisContext['company'],
    );
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
  static Future<Map<String, dynamic>?> getCompleteAnalysisResults(
      String company) async {
    try {
      print('📊 [POLLING] Checking for complete results for company: $company');

      final result = await APIService.makeAuthenticatedCall(
        endpoint: '/analysis-results/$company',
        method: 'GET',
      );
      try {
        print('📦 [POLLING] analysis-results keys: ${result.keys.toList()}');
      } catch (_) {}

      if (result['success'] == true && result['data'] != null) {
        final data = result['data'] as Map<String, dynamic>;
        print('📊 [POLLING] data keys: ${data.keys.toList()}');
        print(
            '📊 [POLLING] Component analysis present: ${data['component_analysis'] != null}');
        print('📊 [POLLING] ATS score present: ${data['ats_score'] != null}');
        print(
            '📊 [POLLING] AI recommendation present: ${data['ai_recommendation'] != null}');
        print(
            '📊 [POLLING] Tailored CV present: ${data['tailored_cv'] != null}');
        try {
          final ats = data['ats_score'] as Map<String, dynamic>?;
          if (ats != null) {
            print('🧩 [POLLING] ats_score keys: ${ats.keys.toList()}');
            print('🧩 [POLLING] final_ats_score: ${ats['final_ats_score']}');
            final breakdown = ats['breakdown'] as Map<String, dynamic>?;
            print('🧩 [POLLING] breakdown present: ${breakdown != null}');
          }
          final ai = data['ai_recommendation'] as Map<String, dynamic>?;
          if (ai != null) {
            print('🤖 [POLLING] ai_recommendation keys: ${ai.keys.toList()}');
            print(
                '🤖 [POLLING] content length: ${(ai['content'] as String?)?.length ?? 0}');
          }
        } catch (_) {}

        // For v2, we specifically need ats_score to be present
        // Don't return partial results - wait for ATS score
        final hasATS = data['ats_score'] != null;
        final hasComponent = data['component_analysis'] != null;

        if (hasATS) {
          print('✅ [POLLING] ATS score available - returning results');
          print('   Component analysis present: $hasComponent');
          return data;
        }

        if (hasComponent) {
          print(
              '⏳ [POLLING] Component analysis available but waiting for ATS score...');
        } else {
          print(
              '⏳ [POLLING] Still waiting for results (no component_analysis or ats_score yet)...');
        }
        return null;
      }

      return null;
    } catch (e) {
      final errorString = e.toString();
      // Check if this is a 404 (file not found) - stop polling immediately
      if (errorString.contains('404') ||
          errorString.contains('Not Found') ||
          errorString.contains('not found')) {
        print(
            '🛑 [POLLING] Analysis file not found (404) - stopping polling early');
        // Throw a special exception to signal 404
        throw _PollingStopException('Analysis file not found');
      }
      print('❌ [POLLING] Error getting complete results: $e');
      return null;
    }
  }

  /// Wait for complete analysis results with polling
  static Future<Map<String, dynamic>?> waitForCompleteResults(String company,
      {int maxWaitTimeSeconds = 30}) async {
    print('🔄 [POLLING] Starting polling for complete results...');

    const pollInterval = Duration(seconds: 2);
    final maxAttempts = maxWaitTimeSeconds ~/ 2;

    for (int attempt = 1; attempt <= maxAttempts; attempt++) {
      print('🔄 [POLLING] Attempt $attempt/$maxAttempts');

      try {
        final completeResults = await getCompleteAnalysisResults(company);
        if (completeResults != null) {
          print(
              '✅ [POLLING] Complete results obtained after ${attempt * 2} seconds');
          return completeResults;
        }
      } catch (e) {
        // If we get a _PollingStopException (404), stop polling immediately
        if (e is _PollingStopException) {
          print('🛑 [POLLING] Stopping polling due to: ${e.message}');
          return null;
        }
        // For other errors, continue polling
        print('⚠️ [POLLING] Error in attempt $attempt, continuing...');
      }

      if (attempt < maxAttempts) {
        print(
            '⏳ [POLLING] Waiting ${pollInterval.inSeconds}s before next attempt...');
        await Future.delayed(pollInterval);
      }
    }

    print('⚠️ [POLLING] Polling timed out after $maxWaitTimeSeconds seconds');
    return null;
  }

  /// Fetch the latest AI recommendation for a company directly
  /// Uses the backend endpoint that finds the latest timestamped file per user/company
  static Future<AIRecommendationResult?> fetchLatestAIRecommendation(
      String company) async {
    try {
      final result = await APIService.makeAuthenticatedCall(
        endpoint: '/ai-recommendations/company/$company',
        method: 'GET',
      );

      if (result is Map<String, dynamic> && result['success'] == true) {
        final content = result['recommendation_content'] as String? ?? '';
        final generatedAt = result['generated_at'] as String?;
        final modelInfo = result['ai_model_info'] as Map<String, dynamic>?;

        return AIRecommendationResult(
          content: content,
          generatedAt: generatedAt,
          modelInfo: modelInfo,
        );
      }
    } catch (e) {
      // Silent failure to avoid disrupting UI
      // debugPrint('⚠️ Failed to fetch latest AI recommendation: $e');
    }
    return null;
  }
}
