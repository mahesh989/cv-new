import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../base/analysis_step_controller.dart';
import '../base/step_result.dart';
import '../base/step_config.dart';
import '../../services/keyword_cache_service.dart';
import '../../services/api_service.dart' as api;

/// Controller for Step 5: AI Recommendations
/// Generates AI-powered CV tailoring recommendations
class AIRecommendationsController extends AnalysisStepController {
  AIRecommendationsController()
      : super(
          const StepConfig(
            stepId: 'ai_recommendations',
            title: 'AI Recommendations',
            description: 'Generate AI-powered CV tailoring recommendations',
            order: 5,
            dependencies: ['enhanced_ats'],
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

      debugPrint(
          '[AI_RECOMMENDATIONS] Starting AI Recommendations generation...');
      debugPrint('   CV: $cvFilename');
      debugPrint('   JD text length: ${jdText.length} chars');

      // Call the API to generate AI Recommendations using backend's default prompt
      final response = await http
          .post(
            Uri.parse(
                '${api.ApiService.baseUrl}/api/llm/generate-recommendations-from-analysis'),
            headers: {'Content-Type': 'application/json'},
            body: json.encode({
              'cv_filename': cvFilename,
              'jd_text': jdText,
            }),
          )
          .timeout(timeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final recommendations =
            data['recommendations'] ?? 'No recommendations generated';

        // Create the result
        final result = StepResult.success(
          stepId: config.stepId,
          data: {
            'recommendations': recommendations,
            'raw_response': data,
          },
          executionDuration: executionDuration ?? 0,
        );

        completeExecution(result);

        // Cache the results
        await saveToCache(cvFilename, jdText);

        debugPrint(
            '[AI_RECOMMENDATIONS] AI Recommendations completed successfully');
        return result;
      } else {
        debugPrint('❌ [AI_RECOMMENDATIONS] API Error: ${response.statusCode}');
        debugPrint('❌ [AI_RECOMMENDATIONS] Response: ${response.body}');

        // Throw API error instead of using fallback
        throw Exception(
            'Failed to generate AI Recommendations: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      final errorMessage = 'AI Recommendations failed: $e';
      debugPrint('❌ [AI_RECOMMENDATIONS] $errorMessage');

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
      final cachedData = await KeywordCacheService.getAIRecommendations(
        cvFilename,
        jdText,
      );

      if (cachedData != null) {
        final result = StepResult.success(
          stepId: config.stepId,
          data: {
            'recommendations': cachedData,
            'raw_response': {'cached': true},
          },
          executionDuration: 0,
        );

        completeExecution(result);
        debugPrint('[AI_RECOMMENDATIONS] Loaded cached results');
        return true;
      }

      return false;
    } catch (e) {
      debugPrint('[AI_RECOMMENDATIONS] Error loading cache: $e');
      return false;
    }
  }

  @override
  Future<void> saveToCache(String cvFilename, String jdText) async {
    if (result != null) {
      try {
        // Save to cache
        final recommendations = result!.data['recommendations'] as String;
        await KeywordCacheService.saveAIRecommendations(
          cvFilename: cvFilename,
          jdText: jdText,
          result: recommendations,
        );
        debugPrint('[AI_RECOMMENDATIONS] Results cached successfully');

        // Save to file
        try {
          await api.ApiService().saveAnalysisResults(
            cvFilename: cvFilename,
            jdText: jdText,
            analysisData: result!.data,
          );
          debugPrint('[AI_RECOMMENDATIONS] Results saved to file successfully');
        } catch (e) {
          debugPrint('[AI_RECOMMENDATIONS] Error saving to file: $e');
          // Don't throw - file saving is optional
        }
      } catch (e) {
        debugPrint('[AI_RECOMMENDATIONS] Error saving to cache: $e');
      }
    }
  }

  // ==================== HELPER METHODS ====================

  // Note: Fallback recommendations have been removed. API errors are now thrown directly.

  // ==================== CONVENIENCE GETTERS ====================

  /// Get the AI recommendations
  String? get recommendations {
    return result?.getValue<String>('recommendations');
  }

  /// Get the raw API response
  Map<String, dynamic>? get rawResponse {
    return result?.getValue<Map<String, dynamic>>('raw_response');
  }
}
