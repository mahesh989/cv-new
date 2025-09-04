import 'package:flutter/foundation.dart';
import '../base/analysis_step_controller.dart';
import '../base/step_result.dart';
import '../base/step_config.dart';
import '../../services/keyword_cache_service.dart';
import '../../services/enhanced_ats_service.dart';
import '../../services/api_service.dart';

/// Controller for Step 4: Enhanced ATS Score
/// Calculates comprehensive ATS score with detailed breakdown
class EnhancedATSController extends AnalysisStepController {
  EnhancedATSController()
      : super(
          const StepConfig(
            stepId: 'enhanced_ats',
            title: 'Enhanced ATS Score',
            description:
                'Calculate comprehensive ATS score with detailed breakdown',
            order: 4,
            dependencies: ['skill_comparison'],
            timeout: Duration(seconds: 90),
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

      debugPrint('[ENHANCED_ATS] Starting Enhanced ATS calculation...');
      debugPrint('   CV: $cvFilename');
      debugPrint('   JD text length: ${jdText.length} chars');

      // Get CV text from preliminary results
      final cvText = await _getCVTextFromSession(inputData);
      if (cvText.isEmpty) {
        throw ArgumentError('CV text not available from preliminary results');
      }

      // Get skill comparison results
      final skillComparison =
          inputData['skill_comparison'] as Map<String, dynamic>?;
      if (skillComparison == null) {
        throw ArgumentError('Skill comparison results are required');
      }

      // Get preliminary analysis results for extracted keywords
      final preliminaryResults =
          inputData['preliminary_analysis'] as Map<String, dynamic>?;
      if (preliminaryResults == null) {
        throw ArgumentError('Preliminary analysis results are required');
      }

      // Build extracted keywords from preliminary results
      final extractedKeywords = {
        'cv_skills': preliminaryResults['cv_skills'] ?? {},
        'jd_skills': preliminaryResults['jd_skills'] ?? {},
        'cv_text': cvText,
        'jd_text': jdText,
      };

      debugPrint('[ENHANCED_ATS] Calling Enhanced ATS Service...');
      debugPrint('   CV text length: ${cvText.length} chars');
      debugPrint('   Skill comparison keys: ${skillComparison.keys.toList()}');

      // Calculate Enhanced ATS Score
      final atsResults = await EnhancedATSService.calculateEnhancedATSScore(
        cvText: cvText,
        jdText: jdText,
        skillComparison: skillComparison,
        extractedKeywords: extractedKeywords,
      );

      // Create the result
      final result = StepResult.success(
        stepId: config.stepId,
        data: atsResults,
        executionDuration: executionDuration ?? 0,
      );

      completeExecution(result);

      // Cache the results
      await saveToCache(cvFilename, jdText);

      debugPrint(
          '[ENHANCED_ATS] Enhanced ATS calculation completed successfully');
      return result;
    } catch (e) {
      final errorMessage = 'Enhanced ATS calculation failed: $e';
      debugPrint('❌ [ENHANCED_ATS] $errorMessage');

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
      final cachedData = await KeywordCacheService.getEnhancedATSResults(
        cvFilename: cvFilename,
        jdText: jdText,
      );

      if (cachedData != null) {
        final result = StepResult.success(
          stepId: config.stepId,
          data: cachedData,
          executionDuration: 0,
        );

        completeExecution(result);
        debugPrint('[ENHANCED_ATS] Loaded cached results');
        return true;
      }

      return false;
    } catch (e) {
      debugPrint('[ENHANCED_ATS] Error loading cache: $e');
      return false;
    }
  }

  @override
  Future<void> saveToCache(String cvFilename, String jdText) async {
    if (result != null) {
      try {
        // Save to cache
        await KeywordCacheService.saveEnhancedATSResults(
          cvFilename: cvFilename,
          jdText: jdText,
          enhancedATSResults: result!.data,
        );
        debugPrint('[ENHANCED_ATS] Results cached successfully');

        // Save to file
        try {
          final apiService = ApiService();
          await apiService.saveAnalysisResults(
            cvFilename: cvFilename,
            jdText: jdText,
            analysisData: result!.data,
          );
          debugPrint('[ENHANCED_ATS] Results saved to file successfully');
        } catch (e) {
          debugPrint('[ENHANCED_ATS] Error saving to file: $e');
          // Don't throw - file saving is optional
        }
      } catch (e) {
        debugPrint('[ENHANCED_ATS] Error saving to cache: $e');
      }
    }
  }

  // ==================== HELPER METHODS ====================

  /// Get CV text from preliminary results
  Future<String> _getCVTextFromSession(Map<String, dynamic> inputData) async {
    try {
      // Use skills from preliminary results as a text representation
      final preliminaryResults =
          inputData['preliminary_analysis'] as Map<String, dynamic>? ?? {};
      final cvSkills = preliminaryResults['cv_skills'] ?? {};

      if (cvSkills is Map<String, dynamic>) {
        final cvSkillsText = cvSkills.entries
            .map((entry) =>
                '${entry.key.replaceAll('_', ' ').toUpperCase()}: ${(entry.value as List<dynamic>).join(', ')}')
            .join('\n\n');
        return cvSkillsText.isNotEmpty
            ? cvSkillsText
            : 'CV skills extracted successfully';
      }
      return 'CV data available for analysis';
    } catch (e) {
      debugPrint(
          '[ENHANCED_ATS] Warning: Could not create CV text representation: $e');
      return 'CV data available for analysis';
    }
  }

  // ==================== CONVENIENCE GETTERS ====================

  /// Get the overall ATS score
  double? get overallScore {
    return result?.getValue<double>('overall_ats_score');
  }

  /// Get the score category
  String? get scoreCategory {
    return result?.getValue<String>('score_category');
  }

  /// Get base scores
  Map<String, dynamic>? get baseScores {
    return result?.getValue<Map<String, dynamic>>('base_scores');
  }

  /// Get enhancement analysis
  Map<String, dynamic>? get enhancementAnalysis {
    return result?.getValue<Map<String, dynamic>>('enhancement_analysis');
  }

  /// Get recommendations
  List<String>? get recommendations {
    final recs = result?.getValue<List<dynamic>>('recommendations');
    return recs?.cast<String>();
  }

  /// Get detailed breakdown
  Map<String, dynamic>? get detailedBreakdown {
    return result?.getValue<Map<String, dynamic>>('detailed_breakdown');
  }

  /// Get category scores
  Map<String, double>? get categoryScores {
    final baseScores = this.baseScores;
    if (baseScores == null) return null;

    final categoryScores =
        baseScores['category_scores'] as Map<String, dynamic>?;
    if (categoryScores == null) return null;

    return categoryScores
        .map((key, value) => MapEntry(key, (value as num).toDouble()));
  }

  /// Get overall base score
  double? get overallBaseScore {
    final baseScores = this.baseScores;
    if (baseScores == null) return null;

    final score = baseScores['overall_base_score'];
    return score is num ? score.toDouble() : null;
  }
}
