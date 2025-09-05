/// Configuration for an analysis step
class StepConfig {
  /// Unique identifier for this step
  final String stepId;

  /// Human-readable title for this step
  final String title;

  /// Human-readable description of what this step does
  final String description;

  /// Execution order (1, 2, 3, etc.)
  final int order;

  /// Whether this step is enabled
  final bool isEnabled;

  /// List of step IDs that this step depends on
  final List<String> dependencies;

  /// Timeout duration for this step
  final Duration timeout;

  /// Whether to stop the entire pipeline if this step fails
  final bool stopOnError;

  /// Whether to enable retry logic for this step
  final bool enableRetry;

  /// Maximum number of retry attempts
  final int maxRetries;

  /// Delay between retry attempts
  final Duration retryDelay;

  /// Custom settings specific to this step
  final Map<String, dynamic> customSettings;

  const StepConfig({
    required this.stepId,
    required this.title,
    required this.description,
    required this.order,
    this.isEnabled = true,
    this.dependencies = const [],
    this.timeout = const Duration(seconds: 60),
    this.stopOnError = true,
    this.enableRetry = false,
    this.maxRetries = 3,
    this.retryDelay = const Duration(seconds: 2),
    this.customSettings = const {},
  });

  /// Create a copy of this config with updated values
  StepConfig copyWith({
    String? stepId,
    String? title,
    String? description,
    int? order,
    bool? isEnabled,
    List<String>? dependencies,
    Duration? timeout,
    bool? stopOnError,
    bool? enableRetry,
    int? maxRetries,
    Duration? retryDelay,
    Map<String, dynamic>? customSettings,
  }) {
    return StepConfig(
      stepId: stepId ?? this.stepId,
      title: title ?? this.title,
      description: description ?? this.description,
      order: order ?? this.order,
      isEnabled: isEnabled ?? this.isEnabled,
      dependencies: dependencies ?? this.dependencies,
      timeout: timeout ?? this.timeout,
      stopOnError: stopOnError ?? this.stopOnError,
      enableRetry: enableRetry ?? this.enableRetry,
      maxRetries: maxRetries ?? this.maxRetries,
      retryDelay: retryDelay ?? this.retryDelay,
      customSettings: customSettings ?? this.customSettings,
    );
  }

  /// Convert to JSON for serialization
  Map<String, dynamic> toJson() {
    return {
      'stepId': stepId,
      'title': title,
      'description': description,
      'order': order,
      'isEnabled': isEnabled,
      'dependencies': dependencies,
      'timeout': timeout.inMilliseconds,
      'stopOnError': stopOnError,
      'enableRetry': enableRetry,
      'maxRetries': maxRetries,
      'retryDelay': retryDelay.inMilliseconds,
      'customSettings': customSettings,
    };
  }

  /// Create from JSON for deserialization
  factory StepConfig.fromJson(Map<String, dynamic> json) {
    return StepConfig(
      stepId: json['stepId'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      order: json['order'] as int,
      isEnabled: json['isEnabled'] as bool? ?? true,
      dependencies: List<String>.from(json['dependencies'] as List? ?? []),
      timeout: Duration(milliseconds: json['timeout'] as int? ?? 60000),
      stopOnError: json['stopOnError'] as bool? ?? true,
      enableRetry: json['enableRetry'] as bool? ?? false,
      maxRetries: json['maxRetries'] as int? ?? 3,
      retryDelay: Duration(milliseconds: json['retryDelay'] as int? ?? 2000),
      customSettings:
          Map<String, dynamic>.from(json['customSettings'] as Map? ?? {}),
    );
  }

  /// Get a custom setting value
  T? getCustomSetting<T>(String key) {
    final value = customSettings[key];
    if (value is T) {
      return value;
    }
    return null;
  }

  /// Set a custom setting value
  StepConfig withCustomSetting(String key, dynamic value) {
    final newSettings = Map<String, dynamic>.from(customSettings);
    newSettings[key] = value;
    return copyWith(customSettings: newSettings);
  }

  @override
  String toString() {
    return 'StepConfig(stepId: $stepId, title: $title, order: $order, enabled: $isEnabled)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is StepConfig &&
        other.stepId == stepId &&
        other.order == order;
  }

  @override
  int get hashCode {
    return stepId.hashCode ^ order.hashCode;
  }
}
