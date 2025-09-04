/// Represents the result of an analysis step execution
class StepResult {
  /// The step identifier
  final String stepId;

  /// The actual result data
  final Map<String, dynamic> data;

  /// Timestamp when the result was created
  final DateTime timestamp;

  /// Execution duration in milliseconds
  final int executionDuration;

  /// Whether the step completed successfully
  final bool isSuccess;

  /// Error message if the step failed
  final String? errorMessage;

  /// Additional metadata about the result
  final Map<String, dynamic> metadata;

  const StepResult({
    required this.stepId,
    required this.data,
    required this.timestamp,
    required this.executionDuration,
    required this.isSuccess,
    this.errorMessage,
    this.metadata = const {},
  });

  /// Create a successful result
  factory StepResult.success({
    required String stepId,
    required Map<String, dynamic> data,
    required int executionDuration,
    Map<String, dynamic> metadata = const {},
  }) {
    return StepResult(
      stepId: stepId,
      data: data,
      timestamp: DateTime.now(),
      executionDuration: executionDuration,
      isSuccess: true,
      metadata: metadata,
    );
  }

  /// Create a failed result
  factory StepResult.failure({
    required String stepId,
    required String errorMessage,
    required int executionDuration,
    Map<String, dynamic> data = const {},
    Map<String, dynamic> metadata = const {},
  }) {
    return StepResult(
      stepId: stepId,
      data: data,
      timestamp: DateTime.now(),
      executionDuration: executionDuration,
      isSuccess: false,
      errorMessage: errorMessage,
      metadata: metadata,
    );
  }

  /// Convert to JSON for serialization
  Map<String, dynamic> toJson() {
    return {
      'stepId': stepId,
      'data': data,
      'timestamp': timestamp.toIso8601String(),
      'executionDuration': executionDuration,
      'isSuccess': isSuccess,
      'errorMessage': errorMessage,
      'metadata': metadata,
    };
  }

  /// Create from JSON for deserialization
  factory StepResult.fromJson(Map<String, dynamic> json) {
    return StepResult(
      stepId: json['stepId'] as String,
      data: Map<String, dynamic>.from(json['data'] as Map),
      timestamp: DateTime.parse(json['timestamp'] as String),
      executionDuration: json['executionDuration'] as int,
      isSuccess: json['isSuccess'] as bool,
      errorMessage: json['errorMessage'] as String?,
      metadata: Map<String, dynamic>.from(json['metadata'] as Map? ?? {}),
    );
  }

  /// Get a specific value from the result data
  T? getValue<T>(String key) {
    final value = data[key];
    if (value is T) {
      return value;
    }
    return null;
  }

  /// Check if the result contains a specific key
  bool containsKey(String key) {
    return data.containsKey(key);
  }

  @override
  String toString() {
    return 'StepResult(stepId: $stepId, isSuccess: $isSuccess, executionDuration: ${executionDuration}ms)';
  }
}
