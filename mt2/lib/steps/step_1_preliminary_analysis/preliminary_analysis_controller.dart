import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../base/analysis_step_controller.dart';
import '../base/step_result.dart';
import '../base/step_config.dart';
import '../../services/keyword_cache_service.dart';
import '../../services/api_service.dart' as api;

/// Controller for Step 1: Preliminary Analysis
/// Extracts CV and JD skills using Claude AI
class PreliminaryAnalysisController extends AnalysisStepController {
  PreliminaryAnalysisController()
      : super(
          const StepConfig(
            stepId: 'preliminary_analysis',
            title: 'Preliminary Analysis',
            description: 'Extract CV and JD skills using Claude AI',
            order: 1,
            dependencies: [],
            timeout: Duration(minutes: 3), // Increased to 3 minutes for DeepSeek API
            stopOnError: true,
          ),
        );

  @override
  Future<StepResult> execute(Map<String, dynamic> inputData) async {
    startExecution();

    try {
      final cvFilename = inputData['cv_filename'] as String;
      final jdText = inputData['jd_text'] as String;

      if (cvFilename.isEmpty || jdText.isEmpty) {
        throw ArgumentError('CV filename and JD text are required');
      }

      debugPrint('[PRELIMINARY_ANALYSIS] Starting analysis...');
      debugPrint('   CV: $cvFilename');
      debugPrint('   JD text length: ${jdText.length} chars');

      // Call the preliminary analysis API
      final response = await http
          .post(
            Uri.parse('${api.ApiService.baseUrl}/preliminary-analysis/'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'cv_filename': cvFilename,
              'jd_text': jdText,
            }),
          )
          .timeout(timeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Create the result
        final result = StepResult.success(
          stepId: config.stepId,
          data: data,
          executionDuration: executionDuration ?? 0,
        );

        completeExecution(result);

        // Cache the results
        await saveToCache(cvFilename, jdText);

        debugPrint('[PRELIMINARY_ANALYSIS] Analysis completed successfully');
        return result;
      } else {
        final errorMessage =
            'API Error: ${response.statusCode} - ${response.body}';
        debugPrint('❌ [PRELIMINARY_ANALYSIS] $errorMessage');

        final result = StepResult.failure(
          stepId: config.stepId,
          errorMessage: errorMessage,
          executionDuration: executionDuration ?? 0,
        );

        failExecution(errorMessage);
        return result;
      }
    } catch (e) {
      final errorMessage = 'Preliminary analysis failed: $e';
      debugPrint('❌ [PRELIMINARY_ANALYSIS] $errorMessage');

      final result = StepResult.failure(
        stepId: config.stepId,
        errorMessage: errorMessage,
        executionDuration: executionDuration ?? 0,
      );

      failExecution(errorMessage);
      return result;
    }
  }

  @override
  Future<bool> loadCachedResults(String cvFilename, String jdText) async {
    try {
      final cachedData = await KeywordCacheService.getPreliminaryAnalysis(
        cvFilename,
        jdText,
      );

      if (cachedData != null) {
        final result = StepResult.success(
          stepId: config.stepId,
          data: cachedData,
          executionDuration: 0,
        );

        completeExecution(result);
        debugPrint('[PRELIMINARY_ANALYSIS] Loaded cached results');
        return true;
      }

      return false;
    } catch (e) {
      debugPrint('[PRELIMINARY_ANALYSIS] Error loading cache: $e');
      return false;
    }
  }

  @override
  Future<void> saveToCache(String cvFilename, String jdText) async {
    if (result != null) {
      try {
        await KeywordCacheService.savePreliminaryAnalysis(
          cvFilename: cvFilename,
          jdText: jdText,
          results: result!.data,
        );
        debugPrint('[PRELIMINARY_ANALYSIS] Results cached successfully');
      } catch (e) {
        debugPrint('[PRELIMINARY_ANALYSIS] Error saving to cache: $e');
      }
    }
  }

  // ==================== CONVENIENCE GETTERS ====================

  /// Get CV skills from the result
  Map<String, dynamic>? get cvSkills {
    return result?.getValue<Map<String, dynamic>>('cv_skills');
  }

  /// Get JD skills from the result
  Map<String, dynamic>? get jdSkills {
    return result?.getValue<Map<String, dynamic>>('jd_skills');
  }

  /// Get extracted keywords from the result
  List<String>? get extractedKeywords {
    final keywords = result?.getValue<List<dynamic>>('extracted_keywords');
    return keywords?.cast<String>();
  }

  /// Get domain keywords from CV skills
  List<String>? get domainKeywords {
    final cvSkills = result?.getValue<Map<String, dynamic>>('cv_skills');
    if (cvSkills != null) {
      final keywords = cvSkills['domain_keywords'] as List<dynamic>?;
      return keywords?.cast<String>();
    }
    return null;
  }

  /// Get CV soft skills
  List<String>? get cvSoftSkills {
    final cvSkills = result?.getValue<Map<String, dynamic>>('cv_skills');
    if (cvSkills != null) {
      final skills = cvSkills['soft_skills'] as List<dynamic>?;
      return skills?.cast<String>();
    }
    return null;
  }

  /// Get CV technical skills
  List<String>? get cvTechnicalSkills {
    final cvSkills = result?.getValue<Map<String, dynamic>>('cv_skills');
    if (cvSkills != null) {
      final skills = cvSkills['technical_skills'] as List<dynamic>?;
      return skills?.cast<String>();
    }
    return null;
  }

  /// Get JD soft skills
  List<String>? get jdSoftSkills {
    final jdSkills = result?.getValue<Map<String, dynamic>>('jd_skills');
    if (jdSkills != null) {
      final skills = jdSkills['soft_skills'] as List<dynamic>?;
      return skills?.cast<String>();
    }
    return null;
  }

  /// Get JD technical skills
  List<String>? get jdTechnicalSkills {
    final jdSkills = result?.getValue<Map<String, dynamic>>('jd_skills');
    if (jdSkills != null) {
      final skills = jdSkills['technical_skills'] as List<dynamic>?;
      return skills?.cast<String>();
    }
    return null;
  }

  /// Get JD domain keywords
  List<String>? get jdDomainKeywords {
    final jdSkills = result?.getValue<Map<String, dynamic>>('jd_skills');
    if (jdSkills != null) {
      final keywords = jdSkills['domain_keywords'] as List<dynamic>?;
      return keywords?.cast<String>();
    }
    return null;
  }

  /// Get CV comprehensive analysis
  String? get cvComprehensiveAnalysis {
    final cvSkills = result?.getValue<Map<String, dynamic>>('cv_skills');
    if (cvSkills != null) {
      final analysis = cvSkills['comprehensive_analysis'];
      return analysis?.toString();
    }
    return null;
  }

  /// Get JD comprehensive analysis
  String? get jdComprehensiveAnalysis {
    final jdSkills = result?.getValue<Map<String, dynamic>>('jd_skills');
    if (jdSkills != null) {
      final analysis = jdSkills['comprehensive_analysis'];
      return analysis?.toString();
    }
    return null;
  }
}
