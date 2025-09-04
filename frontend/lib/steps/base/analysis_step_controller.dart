import 'package:flutter/foundation.dart';
import 'step_result.dart';
import 'step_config.dart';
import '../analysis_orchestrator.dart';

/// Abstract base class for all analysis step controllers.
/// Defines the contract and common functionality for all analysis steps.
abstract class AnalysisStepController extends ChangeNotifier {
  /// Configuration for this step
  final StepConfig config;

  /// Current execution state
  bool _isRunning = false;
  bool _isCompleted = false;
  String? _error;
  StepResult? _result;

  /// Timestamp when execution started
  DateTime? _startTime;

  /// Timestamp when execution completed
  DateTime? _endTime;

  /// Reference to the orchestrator (set by orchestrator when registering)
  AnalysisOrchestrator? orchestrator;

  AnalysisStepController(this.config);

  // ==================== STATE GETTERS ====================

  /// Whether the step is currently running
  bool get isRunning => _isRunning;

  /// Whether the step has completed successfully
  bool get isCompleted => _isCompleted;

  /// Error message if the step failed
  String? get error => _error;

  /// Result data from the step execution
  StepResult? get result => _result;

  /// Whether the step has any result (success or error)
  bool get hasResult => _result != null || _error != null;

  /// Execution duration in milliseconds
  int? get executionDuration {
    if (_startTime == null) return null;
    final endTime = _endTime ?? DateTime.now();
    return endTime.difference(_startTime!).inMilliseconds;
  }

  // ==================== EXECUTION METHODS ====================

  /// Execute this step with the given input data
  ///
  /// [inputData] contains the results from previous steps
  /// Returns a [StepResult] on success, throws on error
  Future<StepResult> execute(Map<String, dynamic> inputData);

  /// Reset this step to its initial state
  void reset() {
    _isRunning = false;
    _isCompleted = false;
    _error = null;
    _result = null;
    _startTime = null;
    _endTime = null;
    notifyListeners();
  }

  /// Load cached results for this step
  /// Returns true if cached data was found and loaded
  Future<bool> loadCachedResults(String cvFilename, String jdText);

  /// Save results to cache
  Future<void> saveToCache(String cvFilename, String jdText);

  // ==================== PROTECTED HELPER METHODS ====================

  /// Start execution of this step
  void startExecution() {
    _isRunning = true;
    _isCompleted = false;
    _error = null;
    _startTime = DateTime.now();
    notifyListeners();
  }

  /// Complete execution successfully
  void completeExecution(StepResult result) {
    _isRunning = false;
    _isCompleted = true;
    _result = result;
    _endTime = DateTime.now();
    notifyListeners();
  }

  /// Fail execution with error
  void failExecution(String error) {
    _isRunning = false;
    _isCompleted = false;
    _error = error;
    _endTime = DateTime.now();
    notifyListeners();
  }

  /// Check if required dependencies are available in input data
  @protected
  bool _checkDependencies(Map<String, dynamic> inputData) {
    for (final dependency in config.dependencies) {
      if (!inputData.containsKey(dependency)) {
        return false;
      }
    }
    return true;
  }

  /// Validate input data for this step
  @protected
  bool _validateInput(Map<String, dynamic> inputData) {
    // Override in subclasses for specific validation
    return true;
  }

  // ==================== UTILITY METHODS ====================

  /// Get a human-readable description of this step
  String get description => config.description;

  /// Get the step title
  String get title => config.title;

  /// Get the step order
  int get order => config.order;

  /// Whether this step is enabled
  bool get isEnabled => config.isEnabled;

  /// Get the step's dependencies
  List<String> get dependencies => config.dependencies;

  /// Get the step's timeout duration
  Duration get timeout => config.timeout;

  /// Get custom settings for this step
  Map<String, dynamic> get customSettings => config.customSettings;
}
