import 'package:flutter_test/flutter_test.dart';
import 'progressive_analysis_phase.dart';
import 'progressive_analysis_controller.dart';

void main() {
  group('ProgressiveAnalysisConfig Tests', () {
    test('should get phase by ID', () {
      final phase = ProgressiveAnalysisConfig.getPhaseById('skills_extraction');
      expect(phase, isNotNull);
      expect(phase!.id, equals('skills_extraction'));
      expect(phase.delaySeconds, equals(0));
    });

    test('should get active phases based on conditions', () {
      final phases = ProgressiveAnalysisConfig.getActivePhases(
        hasAnalyzeMatch: true,
        hasPreextractedComparison: true,
        hasATSResult: true,
      );

      expect(phases.length, equals(4));
      expect(phases.map((p) => p.id), contains('skills_extraction'));
      expect(phases.map((p) => p.id), contains('analyze_match'));
      expect(phases.map((p) => p.id), contains('skills_comparison'));
      expect(phases.map((p) => p.id), contains('ats_analysis'));
    });

    test('should exclude optional phases when not available', () {
      final phases = ProgressiveAnalysisConfig.getActivePhases(
        hasAnalyzeMatch: false,
        hasPreextractedComparison: true,
        hasATSResult: true,
      );

      expect(phases.length, equals(3));
      expect(phases.map((p) => p.id), isNot(contains('analyze_match')));
    });
  });

  group('ProgressiveAnalysisController Tests', () {
    test('should track phase states correctly', () {
      final controller = ProgressiveAnalysisController();
      final phase =
          ProgressiveAnalysisConfig.getPhaseById('skills_extraction')!;

      expect(controller.isPhaseActive(phase.id), isFalse);
      expect(controller.isPhaseLoading(phase.id), isFalse);

      controller.startPhase(phase);

      expect(controller.isPhaseActive(phase.id), isTrue);
      expect(controller.isPhaseLoading(phase.id), isTrue);

      controller.completePhase(phase);

      expect(controller.isPhaseActive(phase.id), isTrue);
      expect(controller.isPhaseLoading(phase.id), isFalse);
    });

    test('should handle variable substitution in messages', () {
      final controller = ProgressiveAnalysisController();
      final phase =
          ProgressiveAnalysisConfig.getPhaseById('skills_extraction')!;

      controller.completePhase(phase, variables: {
        'cvCount': '25',
        'jdCount': '18',
      });

      final message = controller.getPhaseMessage(phase.id);
      expect(message, contains('25'));
      expect(message, contains('18'));
    });
  });
}
