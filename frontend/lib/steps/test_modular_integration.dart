import 'package:flutter/material.dart';
import 'analysis_orchestrator.dart';
import 'step_1_preliminary_analysis/preliminary_analysis_controller.dart';
import 'step_2_ai_analysis/ai_analysis_controller.dart';
import 'step_3_skill_comparison/skill_comparison_controller.dart';
import 'step_4_enhanced_ats/enhanced_ats_controller.dart';
import 'step_5_ai_recommendations/ai_recommendations_controller.dart';

/// Simple test to verify modular integration
class ModularIntegrationTest {
  static void testOrchestratorSetup() {
    print('🧪 Testing Modular Integration...');

    final orchestrator = AnalysisOrchestrator();

    // Register all steps
    orchestrator.registerStep(PreliminaryAnalysisController());
    orchestrator.registerStep(AIAnalysisController());
    orchestrator.registerStep(SkillComparisonController());
    orchestrator.registerStep(EnhancedATSController());
    orchestrator.registerStep(AIRecommendationsController());

    // Verify all steps are registered
    final expectedSteps = [
      'preliminary_analysis',
      'ai_analysis',
      'skill_comparison',
      'enhanced_ats',
      'ai_recommendations'
    ];

    bool allStepsRegistered = true;
    for (final stepId in expectedSteps) {
      if (!orchestrator.steps.containsKey(stepId)) {
        print('❌ Step $stepId not registered');
        allStepsRegistered = false;
      }
    }

    if (allStepsRegistered) {
      print('✅ All 5 steps registered successfully');
      print('📊 Total steps: ${orchestrator.steps.length}');
      print(
          '📋 Steps in order: ${orchestrator.getStepsInOrder().map((s) => s.config.stepId).toList()}');
    } else {
      print('❌ Some steps failed to register');
    }

    // Test step dependencies
    print('\n🔗 Testing dependencies:');
    for (final step in orchestrator.getStepsInOrder()) {
      print('  ${step.config.stepId}: depends on ${step.config.dependencies}');
    }

    print('\n🎯 Modular Integration Test Complete!');
  }
}
