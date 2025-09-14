/// Represents a single phase in the progressive analysis
class ProgressiveAnalysisPhase {
  final String id;
  final String loadingMessage;
  final String completionMessage;
  final String? emoji;
  final int delaySeconds;
  final bool isOptional;
  final Function()? onStart;
  final Function()? onComplete;

  const ProgressiveAnalysisPhase({
    required this.id,
    required this.loadingMessage,
    required this.completionMessage,
    this.emoji,
    required this.delaySeconds,
    this.isOptional = false,
    this.onStart,
    this.onComplete,
  });
}

/// Phase configuration for the complete analysis flow
class ProgressiveAnalysisConfig {
  static const List<ProgressiveAnalysisPhase> defaultPhases = [
    ProgressiveAnalysisPhase(
      id: 'skills_extraction',
      loadingMessage: 'Starting analysis...',
      completionMessage:
          'Skills extracted! Found {cvCount} CV skills and {jdCount} JD skills.',
      emoji: '🚀',
      delaySeconds: 0,
    ),
    ProgressiveAnalysisPhase(
      id: 'analyze_match',
      loadingMessage: 'Starting recruiter assessment analysis...',
      completionMessage: 'Recruiter assessment completed!',
      emoji: '📎',
      delaySeconds: 10,
      isOptional: true,
    ),
    ProgressiveAnalysisPhase(
      id: 'skills_comparison',
      loadingMessage: 'Generating skills comparison analysis...',
      completionMessage: 'Skills comparison analysis completed!',
      emoji: '📈',
      delaySeconds: 10,
    ),
    ProgressiveAnalysisPhase(
      id: 'ats_analysis',
      loadingMessage: 'Generating ATS score analysis...',
      completionMessage: 'ATS Score: {score}/100 ({status})',
      emoji: '🎯',
      delaySeconds: 10,
    ),
  ];

  /// Get phase by ID
  static ProgressiveAnalysisPhase? getPhaseById(String id) {
    try {
      return defaultPhases.firstWhere((phase) => phase.id == id);
    } catch (e) {
      return null;
    }
  }

  /// Get all phases that should be shown
  static List<ProgressiveAnalysisPhase> getActivePhases({
    bool hasAnalyzeMatch = true,
    bool hasPreextractedComparison = true,
    bool hasATSResult = true,
  }) {
    return defaultPhases.where((phase) {
      switch (phase.id) {
        case 'analyze_match':
          return hasAnalyzeMatch;
        case 'skills_comparison':
          return hasPreextractedComparison;
        case 'ats_analysis':
          return hasATSResult;
        default:
          return true;
      }
    }).toList();
  }
}
