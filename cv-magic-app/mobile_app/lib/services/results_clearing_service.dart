import 'package:flutter/foundation.dart';
import '../controllers/skills_analysis_controller.dart';

class ResultsClearingService {
  static SkillsAnalysisController? _skillsController;

  static void registerSkillsController(SkillsAnalysisController controller) {
    _skillsController = controller;
    debugPrint('📝 [RESULTS_CLEARING] Registered skills controller');
  }

  static void unregisterSkillsController() {
    _skillsController = null;
    debugPrint('🗑 [RESULTS_CLEARING] Unregistered skills controller');
  }

  static Future<void> clearAllResults() async {
    debugPrint('🧹 [RESULTS_CLEARING] Clearing all results');
    
    try {
      // Clear controller results if registered
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
}