import 'package:flutter/foundation.dart';
import '../controllers/skills_analysis_controller.dart';
import '../controllers/context_aware_analysis_controller.dart';

class ResultsClearingService {
  static SkillsAnalysisController? _skillsController;
  static ContextAwareAnalysisController? _contextAwareController;

  static void registerSkillsController(SkillsAnalysisController controller) {
    _skillsController = controller;
    debugPrint('📝 [RESULTS_CLEARING] Registered skills controller');
  }

  static void unregisterSkillsController() {
    _skillsController = null;
    debugPrint('🗑 [RESULTS_CLEARING] Unregistered skills controller');
  }

  static void registerContextAwareController(
      ContextAwareAnalysisController controller) {
    _contextAwareController = controller;
    debugPrint('📝 [RESULTS_CLEARING] Registered context-aware controller');
  }

  static void unregisterContextAwareController() {
    _contextAwareController = null;
    debugPrint('🗑 [RESULTS_CLEARING] Unregistered context-aware controller');
  }

  static Future<void> clearAllResults() async {
    debugPrint('🧹 [RESULTS_CLEARING] Clearing all results');

    try {
      // Clear context-aware controller results if registered (priority)
      if (_contextAwareController != null) {
        debugPrint(
            '🔄 [RESULTS_CLEARING] Clearing context-aware controller results');
        _contextAwareController!.clearResults();
        debugPrint(
            '✅ [RESULTS_CLEARING] Context-aware controller results cleared');
      }

      // Clear skills controller results if registered (fallback)
      if (_skillsController != null) {
        debugPrint('🔄 [RESULTS_CLEARING] Clearing skills controller results');
        _skillsController!.clearResults();
        debugPrint('✅ [RESULTS_CLEARING] Skills controller results cleared');
      }

      // Clear any other persisted results (files, cache, etc.)
      debugPrint('✅ [RESULTS_CLEARING] All results cleared successfully');
    } catch (e) {
      debugPrint('❌ [RESULTS_CLEARING] Error clearing results: $e');
      rethrow;
    }
  }

  static Future<void> clearAnalysisResultsOnly() async {
    debugPrint(
        '🧹 [RESULTS_CLEARING] Clearing analysis results only (preserving JD inputs)');

    try {
      // Clear context-aware controller results if registered (priority)
      if (_contextAwareController != null) {
        debugPrint(
            '🔄 [RESULTS_CLEARING] Clearing context-aware controller results only');
        _contextAwareController!.clearResults();
        debugPrint(
            '✅ [RESULTS_CLEARING] Context-aware controller results cleared (JD inputs preserved)');
      }

      // Clear skills controller results if registered (fallback)
      if (_skillsController != null) {
        debugPrint(
            '🔄 [RESULTS_CLEARING] Clearing skills controller results only');
        _skillsController!.clearResults();
        debugPrint(
            '✅ [RESULTS_CLEARING] Skills controller results cleared (JD inputs preserved)');
      }

      debugPrint(
          '✅ [RESULTS_CLEARING] Analysis results cleared successfully (JD inputs preserved)');
    } catch (e) {
      debugPrint('❌ [RESULTS_CLEARING] Error clearing analysis results: $e');
      rethrow;
    }
  }
}
