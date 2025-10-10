import '../exceptions/cv_exceptions.dart';
import '../models/skills_analysis_model.dart';
import 'api_service.dart';

/// Service for handling context-aware analysis operations
class ContextAwareAnalysisService {
  /// Perform context-aware analysis with intelligent CV selection and JD caching
  static Future<ContextAwareAnalysisResult> performContextAwareAnalysis({
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

      // Check for tailored CV not found error
      if (result['error_type'] == 'tailored_cv_not_found') {
        throw TailoredCVNotFoundException(result['error'] as String);
      }

      stopwatch.stop();

      print(
          '📊 [CONTEXT_AWARE_SERVICE] About to parse ContextAwareAnalysisResult from JSON');
      final analysisResult = ContextAwareAnalysisResult.fromJson(result);
      print(
          '📊 [CONTEXT_AWARE_SERVICE] Successfully parsed ContextAwareAnalysisResult');

      // Return with execution duration
      final finalResult = ContextAwareAnalysisResult(
        success: analysisResult.success,
        analysisContext: analysisResult.analysisContext,
        results: analysisResult.results,
        warnings: analysisResult.warnings,
        errors: analysisResult.errors,
        processingTime: stopwatch.elapsed,
      );

      return finalResult;
    } catch (e, stackTrace) {
      print(
          '❌ [CONTEXT_AWARE_SERVICE] Exception in performContextAwareAnalysis: $e');
      print('❌ [CONTEXT_AWARE_SERVICE] Stack trace: $stackTrace');

      // Enhanced error handling for different error types
      if (e.toString().contains('404') || e.toString().contains('not found')) {
        return ContextAwareAnalysisResult.error(
            'Analysis resources not found. Please check your inputs.');
      } else if (e.toString().contains('401')) {
        return ContextAwareAnalysisResult.error(
            'Authentication required. Please log in again.');
      } else if (e.toString().contains('500')) {
        return ContextAwareAnalysisResult.error(
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
            return ContextAwareAnalysisResult.error(errorMsg);
          }
        }
        return ContextAwareAnalysisResult.error(
            'Failed to perform context-aware analysis: $e');
      }
    }
  }

  /// Get CV context information for UI feedback
  static Future<CVContextResult> getCVContext({
    required String company,
    required bool isRerun,
  }) async {
    print('=== CV CONTEXT SERVICE CALLED ===');
    print('Company: $company');
    print('Is Rerun: $isRerun');

    try {
      print('🔍 [CV_CONTEXT_SERVICE] Getting CV context information');

      final result = await APIService.makeAuthenticatedCall(
        endpoint: '/cv-context/$company?is_rerun=$isRerun',
        method: 'GET',
      );

      print('📡 [CV_CONTEXT_SERVICE] Received response from API');
      print('📡 [CV_CONTEXT_SERVICE] Raw result keys: ${result.keys.toList()}');

      final contextResult = CVContextResult.fromJson(result);
      print('📊 [CV_CONTEXT_SERVICE] Successfully parsed CVContextResult');

      return contextResult;
    } catch (e, stackTrace) {
      print('❌ [CV_CONTEXT_SERVICE] Exception in getCVContext: $e');
      print('❌ [CV_CONTEXT_SERVICE] Stack trace: $stackTrace');

      return CVContextResult.error('Failed to get CV context: $e');
    }
  }

  /// Validate inputs for context-aware analysis
  static String? validateContextAwareInputs({
    required String? jdUrl,
    required String? company,
  }) {
    if (jdUrl == null || jdUrl.trim().isEmpty) {
      return 'Please provide a job description URL';
    }

    if (company == null || company.trim().isEmpty) {
      return 'Please provide a company name';
    }

    // Basic URL validation
    if (!jdUrl.startsWith('http://') && !jdUrl.startsWith('https://')) {
      return 'Please provide a valid URL starting with http:// or https://';
    }

    return null; // No validation errors
  }

  /// Extract company name from JD URL for context
  static String extractCompanyFromUrl(String jdUrl) {
    try {
      final uri = Uri.parse(jdUrl);
      final host = uri.host.toLowerCase();

      // Remove common domain suffixes
      final company = host
          .replaceAll(RegExp(r'\.(com|org|net|co|io|ai|tech)$'), '')
          .replaceAll(RegExp(r'^(www\.|careers\.|jobs\.)'), '')
          .replaceAll('-', ' ')
          .replaceAll('_', ' ')
          .split(' ')
          .map((word) =>
              word.isNotEmpty ? word[0].toUpperCase() + word.substring(1) : '')
          .join(' ');

      return company.isNotEmpty ? company : 'Unknown Company';
    } catch (e) {
      return 'Unknown Company';
    }
  }
}

/// Result model for context-aware analysis
class ContextAwareAnalysisResult {
  final bool success;
  final AnalysisContext? analysisContext;
  final AnalysisResults? results;
  final List<String> warnings;
  final List<String> errors;
  final Duration processingTime;

  ContextAwareAnalysisResult({
    required this.success,
    this.analysisContext,
    this.results,
    this.warnings = const [],
    this.errors = const [],
    this.processingTime = Duration.zero,
  });

  factory ContextAwareAnalysisResult.fromJson(Map<String, dynamic> json) {
    return ContextAwareAnalysisResult(
      success: json['success'] ?? false,
      analysisContext: json['analysis_context'] != null
          ? AnalysisContext.fromJson(json['analysis_context'])
          : null,
      results: json['results'] != null
          ? AnalysisResults.fromJson(json['results'])
          : null,
      warnings: List<String>.from(json['warnings'] ?? []),
      errors: List<String>.from(json['errors'] ?? []),
    );
  }

  factory ContextAwareAnalysisResult.error(String errorMessage) {
    return ContextAwareAnalysisResult(
      success: false,
      errors: [errorMessage],
    );
  }

  bool get hasError => errors.isNotEmpty;
  bool get hasWarnings => warnings.isNotEmpty;
}

/// Analysis context information
class AnalysisContext {
  final String company;
  final String jdUrl;
  final bool isRerun;
  final CVSelectionContext cvSelection;
  final JDCacheStatus jdCacheStatus;
  final double processingTime;
  final List<String> stepsCompleted;
  final List<String> stepsSkipped;

  AnalysisContext({
    required this.company,
    required this.jdUrl,
    required this.isRerun,
    required this.cvSelection,
    required this.jdCacheStatus,
    required this.processingTime,
    required this.stepsCompleted,
    required this.stepsSkipped,
  });

  factory AnalysisContext.fromJson(Map<String, dynamic> json) {
    return AnalysisContext(
      company: json['company'] ?? '',
      jdUrl: json['jd_url'] ?? '',
      isRerun: json['is_rerun'] ?? false,
      cvSelection: CVSelectionContext.fromJson(json['cv_selection'] ?? {}),
      jdCacheStatus: JDCacheStatus.fromJson(json['jd_cache_status'] ?? {}),
      processingTime: (json['processing_time'] ?? 0.0).toDouble(),
      stepsCompleted: List<String>.from(json['steps_completed'] ?? []),
      stepsSkipped: List<String>.from(json['steps_skipped'] ?? []),
    );
  }
}

/// CV selection context
class CVSelectionContext {
  final String cvType;
  final String version;
  final String source;
  final bool exists;
  final String? jsonPath;
  final String? txtPath;
  final String? company;
  final String? timestamp;
  final bool isRerun;

  CVSelectionContext({
    required this.cvType,
    required this.version,
    required this.source,
    required this.exists,
    this.jsonPath,
    this.txtPath,
    this.company,
    this.timestamp,
    required this.isRerun,
  });

  factory CVSelectionContext.fromJson(Map<String, dynamic> json) {
    return CVSelectionContext(
      cvType: json['cv_type'] ?? 'unknown',
      version: json['version'] ?? '1.0',
      source: json['source'] ?? 'unknown',
      exists: json['exists'] ?? false,
      jsonPath: json['json_path'],
      txtPath: json['txt_path'],
      company: json['company'],
      timestamp: json['timestamp'],
      isRerun: json['is_rerun'] ?? false,
    );
  }

  String get displayName => '$cvType CV v$version';
  String get sourceDescription {
    switch (source) {
      case 'original_cv_fresh_analysis':
        return 'Using original CV for fresh analysis';
      case 'tailored_cv_rerun':
        return 'Using latest tailored CV for improved results';
      case 'original_cv_rerun_fallback':
        return 'Using original CV (no tailored version available)';
      default:
        return 'Using $cvType CV';
    }
  }
}

/// JD cache status
class JDCacheStatus {
  final bool cached;
  final JDCacheStats? cacheStats;

  JDCacheStatus({
    required this.cached,
    this.cacheStats,
  });

  factory JDCacheStatus.fromJson(Map<String, dynamic> json) {
    return JDCacheStatus(
      cached: json['cached'] ?? false,
      cacheStats: json['cache_stats'] != null
          ? JDCacheStats.fromJson(json['cache_stats'])
          : null,
    );
  }
}

/// JD cache statistics
class JDCacheStats {
  final bool hasCache;
  final String company;
  final String? jdUrl;
  final String? cachedAt;
  final String? lastUsed;
  final int useCount;
  final bool cacheValid;
  final double ageHours;

  JDCacheStats({
    required this.hasCache,
    required this.company,
    this.jdUrl,
    this.cachedAt,
    this.lastUsed,
    required this.useCount,
    required this.cacheValid,
    required this.ageHours,
  });

  factory JDCacheStats.fromJson(Map<String, dynamic> json) {
    return JDCacheStats(
      hasCache: json['has_cache'] ?? false,
      company: json['company'] ?? '',
      jdUrl: json['jd_url'],
      cachedAt: json['cached_at'],
      lastUsed: json['last_used'],
      useCount: json['use_count'] ?? 0,
      cacheValid: json['cache_valid'] ?? false,
      ageHours: (json['age_hours'] ?? 0.0).toDouble(),
    );
  }

  String get ageDescription {
    if (ageHours < 1) {
      return 'Less than 1 hour old';
    } else if (ageHours < 24) {
      return '${ageHours.toStringAsFixed(1)} hours old';
    } else {
      final days = (ageHours / 24).floor();
      return '$days day${days == 1 ? '' : 's'} old';
    }
  }
}

/// Analysis results container
class AnalysisResults {
  final Map<String, dynamic> cvSkills;
  final Map<String, dynamic> jdSkills;
  final Map<String, dynamic> jdAnalysis;
  final Map<String, dynamic> jobInfo;
  final Map<String, dynamic> cvJdMatching;
  final Map<String, dynamic> componentAnalysis;
  final Map<String, dynamic> atsRecommendations;
  final Map<String, dynamic> aiRecommendations;
  final String? tailoredCvPath;

  AnalysisResults({
    required this.cvSkills,
    required this.jdSkills,
    required this.jdAnalysis,
    required this.jobInfo,
    required this.cvJdMatching,
    required this.componentAnalysis,
    required this.atsRecommendations,
    required this.aiRecommendations,
    this.tailoredCvPath,
  });

  factory AnalysisResults.fromJson(Map<String, dynamic> json) {
    return AnalysisResults(
      cvSkills: Map<String, dynamic>.from(json['cv_skills'] ?? {}),
      jdSkills: Map<String, dynamic>.from(json['jd_skills'] ?? {}),
      jdAnalysis: Map<String, dynamic>.from(json['jd_analysis'] ?? {}),
      jobInfo: Map<String, dynamic>.from(json['job_info'] ?? {}),
      cvJdMatching: Map<String, dynamic>.from(json['cv_jd_matching'] ?? {}),
      componentAnalysis:
          Map<String, dynamic>.from(json['component_analysis'] ?? {}),
      atsRecommendations:
          Map<String, dynamic>.from(json['ats_recommendations'] ?? {}),
      aiRecommendations:
          Map<String, dynamic>.from(json['ai_recommendations'] ?? {}),
      tailoredCvPath: json['tailored_cv_path'] ??
          (json['tailored_cv'] != null &&
                  json['tailored_cv']['available'] == true
              ? json['tailored_cv']['file_path']
              : null),
    );
  }
}

/// Result model for CV context information
class CVContextResult {
  final bool success;
  final String company;
  final CVSelectionContext cvContext;
  final List<CVVersion> availableCvVersions;
  final JDCacheStats jdCacheStatus;
  final CVRecommendation recommendation;
  final String? error;

  CVContextResult({
    required this.success,
    required this.company,
    required this.cvContext,
    required this.availableCvVersions,
    required this.jdCacheStatus,
    required this.recommendation,
    this.error,
  });

  factory CVContextResult.fromJson(Map<String, dynamic> json) {
    return CVContextResult(
      success: json['success'] ?? false,
      company: json['company'] ?? '',
      cvContext: CVSelectionContext.fromJson(json['cv_context'] ?? {}),
      availableCvVersions: (json['available_cv_versions'] as List?)
              ?.map((v) => CVVersion.fromJson(v))
              .toList() ??
          [],
      jdCacheStatus: JDCacheStats.fromJson(json['jd_cache_status'] ?? {}),
      recommendation: CVRecommendation.fromJson(json['recommendation'] ?? {}),
    );
  }

  factory CVContextResult.error(String errorMessage) {
    return CVContextResult(
      success: false,
      company: '',
      cvContext: CVSelectionContext(
        cvType: 'error',
        version: '0.0',
        source: 'error',
        exists: false,
        isRerun: false,
      ),
      availableCvVersions: [],
      jdCacheStatus: JDCacheStats(
        hasCache: false,
        company: '',
        useCount: 0,
        cacheValid: false,
        ageHours: 0.0,
      ),
      recommendation: CVRecommendation(
        suggestedCv: 'error',
        reason: 'error',
        version: '0.0',
      ),
      error: errorMessage,
    );
  }
}

/// CV version information
class CVVersion {
  final String type;
  final String version;
  final String path;
  final String? timestamp;
  final double createdAt;

  CVVersion({
    required this.type,
    required this.version,
    required this.path,
    this.timestamp,
    required this.createdAt,
  });

  factory CVVersion.fromJson(Map<String, dynamic> json) {
    return CVVersion(
      type: json['type'] ?? 'unknown',
      version: json['version'] ?? '1.0',
      path: json['path'] ?? '',
      timestamp: json['timestamp'],
      createdAt: (json['created_at'] ?? 0.0).toDouble(),
    );
  }
}

/// CV recommendation
class CVRecommendation {
  final String suggestedCv;
  final String reason;
  final String version;

  CVRecommendation({
    required this.suggestedCv,
    required this.reason,
    required this.version,
  });

  factory CVRecommendation.fromJson(Map<String, dynamic> json) {
    return CVRecommendation(
      suggestedCv: json['suggested_cv'] ?? 'original',
      reason: json['reason'] ?? 'unknown',
      version: json['version'] ?? '1.0',
    );
  }
}
