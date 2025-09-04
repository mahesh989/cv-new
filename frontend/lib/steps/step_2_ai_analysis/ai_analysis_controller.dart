import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../base/analysis_step_controller.dart';
import '../base/step_result.dart';
import '../base/step_config.dart';
import '../../services/keyword_cache_service.dart';
import '../../services/api_service.dart' as api;

/// Controller for Step 2: AI Analysis
/// Performs match analysis using AI to compare CV and JD
class AIAnalysisController extends AnalysisStepController {
  AIAnalysisController()
      : super(
          const StepConfig(
            stepId: 'ai_analysis',
            title: 'AI Analysis',
            description: 'Perform AI-powered match analysis between CV and JD',
            order: 2,
            dependencies: ['preliminary_analysis'],
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
      final currentPrompt = inputData['current_prompt'] as String? ?? '';

      if (cvFilename.isEmpty || jdText.isEmpty) {
        throw ArgumentError('CV filename and JD text are required');
      }

      debugPrint('[AI_ANALYSIS] Starting AI analysis...');
      debugPrint('   CV: $cvFilename');
      debugPrint('   JD text length: ${jdText.length} chars');
      debugPrint('   Prompt length: ${currentPrompt.length} chars');

      // Call the AI analysis API
      final response = await http.post(
        Uri.parse('${api.ApiService.baseUrl}/analyze-fit/'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'cv_filename': cvFilename,
          'text': jdText,
        },
      ).timeout(timeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        debugPrint('[AI_ANALYSIS] Response data keys: ${data.keys.toList()}');
        debugPrint('[AI_ANALYSIS] Response data: $data');

        final analysisResult = data['raw_analysis'] ??
            data['raw'] ??
            data['result'] ??
            'No analysis result';

        debugPrint('[AI_ANALYSIS] Extracted analysis result: $analysisResult');

        // Create the result
        final result = StepResult.success(
          stepId: config.stepId,
          data: {
            'analysis_result': analysisResult,
            'raw_response': data,
          },
          executionDuration: executionDuration ?? 0,
        );

        completeExecution(result);

        // Cache the results
        await saveToCache(cvFilename, jdText);

        debugPrint('[AI_ANALYSIS] AI analysis completed successfully');
        return result;
      } else {
        final errorMessage =
            'API Error: ${response.statusCode} - ${response.body}';
        debugPrint('❌ [AI_ANALYSIS] $errorMessage');

        final result = StepResult.failure(
          stepId: config.stepId,
          errorMessage: errorMessage,
          executionDuration: executionDuration ?? 0,
        );

        failExecution(errorMessage);
        return result;
      }
    } catch (e) {
      final errorMessage = 'AI analysis failed: $e';
      debugPrint('❌ [AI_ANALYSIS] $errorMessage');

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
      final cachedData = await KeywordCacheService.getAIAnalysis(
        cvFilename,
        jdText,
      );

      if (cachedData != null) {
        final result = StepResult.success(
          stepId: config.stepId,
          data: {
            'analysis_result': cachedData,
            'raw_response': {'raw': cachedData},
          },
          executionDuration: 0,
        );

        completeExecution(result);
        debugPrint('[AI_ANALYSIS] Loaded cached results');
        return true;
      }

      return false;
    } catch (e) {
      debugPrint('[AI_ANALYSIS] Error loading cache: $e');
      return false;
    }
  }

  @override
  Future<void> saveToCache(String cvFilename, String jdText) async {
    if (result != null) {
      try {
        final analysisResult = result!.data['analysis_result'] as String;
        await KeywordCacheService.saveAIAnalysis(
          cvFilename: cvFilename,
          jdText: jdText,
          result: analysisResult,
        );
        debugPrint('[AI_ANALYSIS] Results cached successfully');
      } catch (e) {
        debugPrint('[AI_ANALYSIS] Error saving to cache: $e');
      }
    }
  }

  // ==================== CONVENIENCE GETTERS ====================

  /// Get the AI analysis result
  String? get analysisResult {
    return result?.getValue<String>('analysis_result');
  }

  /// Get the raw API response
  Map<String, dynamic>? get rawResponse {
    return result?.getValue<Map<String, dynamic>>('raw_response');
  }
}
