// Enhanced workflow states for iterative improvement
enum ATSWorkflowState {
  initial, // Start with ATS test
  atsCompleted, // ATS test done, can generate CV
  cvGenerated, // CV generated, can test again or regenerate
  iterating // In iterative improvement cycle
}

// Waterfall step types for the cascading interface
enum WaterfallStepType {
  atsResult,
  cvPreview,
  loading,
  improvement,
}

// Waterfall step data class
class WaterfallStep {
  final WaterfallStepType type;
  final dynamic atsResult; // Using dynamic to avoid circular imports
  final String cvName;
  final String? cvContent;
  final String? loadingMessage;
  final DateTime timestamp;

  WaterfallStep({
    required this.type,
    required this.cvName,
    required this.timestamp,
    this.atsResult,
    this.cvContent,
    this.loadingMessage,
  });
}
