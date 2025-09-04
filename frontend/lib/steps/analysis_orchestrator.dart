import 'package:flutter/foundation.dart';
import 'base/analysis_step_controller.dart';
import 'base/step_result.dart';

/// Orchestrates the execution of multiple analysis steps in a pipeline.
/// Manages step registration, sequencing, data flow, and error handling.
class AnalysisOrchestrator extends ChangeNotifier {
  /// Registered steps mapped by their step ID
  final Map<String, AnalysisStepController> _steps = {};

  /// Current execution state
  bool _isRunning = false;
  bool _isCompleted = false;
  String? _error;

  /// Current step being executed
  String? _currentStepId;

  /// Results from all completed steps
  final Map<String, StepResult> _stepResults = {};

  /// Execution start time
  DateTime? _startTime;

  /// Execution end time
  DateTime? _endTime;

  // ==================== STATE GETTERS ====================

  /// Whether the pipeline is currently running
  bool get isRunning => _isRunning;

  /// Whether the pipeline has completed successfully
  bool get isCompleted => _isCompleted;

  /// Error message if the pipeline failed
  String? get error => _error;

  /// ID of the step currently being executed
  String? get currentStepId => _currentStepId;

  /// All registered step controllers
  Map<String, AnalysisStepController> get steps => Map.unmodifiable(_steps);

  /// Results from all completed steps
  Map<String, StepResult> get stepResults => Map.unmodifiable(_stepResults);

  /// Whether any step has results
  bool get hasResults => _stepResults.isNotEmpty;

  /// Total execution duration in milliseconds
  int? get executionDuration {
    if (_startTime == null) return null;
    final endTime = _endTime ?? DateTime.now();
    return endTime.difference(_startTime!).inMilliseconds;
  }

  // ==================== STEP MANAGEMENT ====================

  /// Register a step with the orchestrator
  void registerStep(AnalysisStepController step) {
    step.orchestrator = this;
    _steps[step.config.stepId] = step;
    debugPrint('[ORCHESTRATOR] Registered step: ${step.config.stepId}');
  }

  /// Unregister a step from the orchestrator
  void unregisterStep(String stepId) {
    _steps.remove(stepId);
    _stepResults.remove(stepId);
    debugPrint('[ORCHESTRATOR] Unregistered step: $stepId');
  }

  /// Get a specific step controller
  AnalysisStepController? getStep(String stepId) {
    return _steps[stepId];
  }

  /// Get all steps sorted by their execution order
  List<AnalysisStepController> getStepsInOrder() {
    final stepsList = _steps.values.toList();
    stepsList.sort((a, b) => a.config.order.compareTo(b.config.order));
    return stepsList;
  }

  // ==================== EXECUTION METHODS ====================

  /// Execute all enabled steps in order
  Future<void> executeAllSteps({
    required String cvFilename,
    required String jdText,
    Map<String, dynamic>? initialData,
  }) async {
    if (_isRunning) {
      throw StateError('Pipeline is already running');
    }

    _startExecution();

    try {
      // Get steps in execution order
      final stepsToExecute =
          getStepsInOrder().where((step) => step.config.isEnabled).toList();

      if (stepsToExecute.isEmpty) {
        throw StateError('No enabled steps to execute');
      }

      debugPrint(
          '[ORCHESTRATOR] Starting execution of ${stepsToExecute.length} steps');

      // Initialize data with initial values
      final data = Map<String, dynamic>.from(initialData ?? {});
      data['cv_filename'] = cvFilename;
      data['jd_text'] = jdText;

      // Execute steps sequentially
      for (final step in stepsToExecute) {
        await _executeStep(step, data);

        // Check if we should stop on error
        if (step.error != null && step.config.stopOnError) {
          _failExecution('Step ${step.config.stepId} failed: ${step.error}');
          return;
        }
      }

      _completeExecution();
    } catch (e) {
      _failExecution('Pipeline execution failed: $e');
    }
  }

  /// Execute a specific step
  Future<void> executeStep(
    String stepId, {
    required String cvFilename,
    required String jdText,
    Map<String, dynamic>? inputData,
  }) async {
    final step = _steps[stepId];
    if (step == null) {
      throw ArgumentError('Step $stepId not found');
    }

    if (!step.config.isEnabled) {
      throw StateError('Step $stepId is disabled');
    }

    final data = Map<String, dynamic>.from(inputData ?? {});
    data['cv_filename'] = cvFilename;
    data['jd_text'] = jdText;

    await _executeStep(step, data);
  }

  /// Execute steps from a specific step onwards
  Future<void> executeStepsFrom(
    String startStepId, {
    required String cvFilename,
    required String jdText,
    Map<String, dynamic>? initialData,
  }) async {
    final startStep = _steps[startStepId];
    if (startStep == null) {
      throw ArgumentError('Start step $startStepId not found');
    }

    final stepsToExecute = getStepsInOrder()
        .where((step) =>
            step.config.isEnabled &&
            step.config.order >= startStep.config.order)
        .toList();

    if (stepsToExecute.isEmpty) {
      throw StateError('No steps to execute from $startStepId');
    }

    final data = Map<String, dynamic>.from(initialData ?? {});
    data['cv_filename'] = cvFilename;
    data['jd_text'] = jdText;

    for (final step in stepsToExecute) {
      await _executeStep(step, data);

      if (step.error != null && step.config.stopOnError) {
        _failExecution('Step ${step.config.stepId} failed: ${step.error}');
        return;
      }
    }

    _completeExecution();
  }

  // ==================== CACHING METHODS ====================

  /// Load cached results for all steps
  Future<void> loadCachedResults(String cvFilename, String jdText) async {
    debugPrint('[ORCHESTRATOR] Loading cached results for all steps');

    for (final step in _steps.values) {
      try {
        final hasCached = await step.loadCachedResults(cvFilename, jdText);
        if (hasCached && step.result != null) {
          _stepResults[step.config.stepId] = step.result!;
          debugPrint(
              '[ORCHESTRATOR] Loaded cached result for ${step.config.stepId}');
        }
      } catch (e) {
        debugPrint(
            '[ORCHESTRATOR] Error loading cache for ${step.config.stepId}: $e');
      }
    }

    notifyListeners();
  }

  /// Clear all cached results
  void clearCache() {
    for (final step in _steps.values) {
      step.reset();
    }
    _stepResults.clear();
    notifyListeners();
  }

  // ==================== RESET METHODS ====================

  /// Reset the orchestrator to its initial state
  void reset() {
    _isRunning = false;
    _isCompleted = false;
    _error = null;
    _currentStepId = null;
    _stepResults.clear();
    _startTime = null;
    _endTime = null;

    // Reset all steps
    for (final step in _steps.values) {
      step.reset();
    }

    notifyListeners();
  }

  // ==================== PRIVATE HELPER METHODS ====================

  /// Execute a single step
  Future<void> _executeStep(
      AnalysisStepController step, Map<String, dynamic> data) async {
    _currentStepId = step.config.stepId;
    notifyListeners();

    debugPrint('[ORCHESTRATOR] Executing step: ${step.config.stepId}');

    try {
      // Check dependencies
      final missingDeps = step.config.dependencies
          .where((dep) => !data.containsKey(dep))
          .toList();
      if (missingDeps.isNotEmpty) {
        throw StateError(
            'Missing dependencies for step ${step.config.stepId}: ${missingDeps.join(', ')}');
      }

      // Execute the step
      final result = await step.execute(data);

      // Store the result
      _stepResults[step.config.stepId] = result;

      // Add step result to data for next steps
      data[step.config.stepId] = result.data;

      debugPrint(
          '[ORCHESTRATOR] Step ${step.config.stepId} completed successfully');
    } catch (e) {
      debugPrint('[ORCHESTRATOR] Step ${step.config.stepId} failed: $e');
      rethrow;
    } finally {
      _currentStepId = null;
      notifyListeners();
    }
  }

  /// Start pipeline execution
  void _startExecution() {
    _isRunning = true;
    _isCompleted = false;
    _error = null;
    _startTime = DateTime.now();
    notifyListeners();
  }

  /// Complete pipeline execution successfully
  void _completeExecution() {
    _isRunning = false;
    _isCompleted = true;
    _endTime = DateTime.now();
    notifyListeners();
  }

  /// Fail pipeline execution
  void _failExecution(String error) {
    _isRunning = false;
    _isCompleted = false;
    _error = error;
    _endTime = DateTime.now();
    notifyListeners();
  }

  // ==================== UTILITY METHODS ====================

  /// Get the progress percentage (0.0 to 1.0)
  double get progress {
    if (_steps.isEmpty) return 0.0;

    final enabledSteps =
        _steps.values.where((step) => step.config.isEnabled).toList();

    if (enabledSteps.isEmpty) return 0.0;

    final completedSteps =
        enabledSteps.where((step) => step.isCompleted).length;

    return completedSteps.toDouble() / enabledSteps.length.toDouble();
  }

  /// Get the number of completed steps
  int get completedStepsCount {
    return _steps.values
        .where((step) => step.config.isEnabled && step.isCompleted)
        .length;
  }

  /// Get the total number of enabled steps
  int get totalStepsCount {
    return _steps.values.where((step) => step.config.isEnabled).length;
  }

  /// Check if all enabled steps are completed
  bool get allStepsCompleted {
    return _steps.values
        .where((step) => step.config.isEnabled)
        .every((step) => step.isCompleted);
  }

  /// Check if any step has an error
  bool get hasErrors {
    return _steps.values.any((step) => step.error != null);
  }

  /// Get all error messages from steps
  List<String> get errorMessages {
    return _steps.values
        .where((step) => step.error != null)
        .map((step) => '${step.config.stepId}: ${step.error}')
        .toList();
  }
}
