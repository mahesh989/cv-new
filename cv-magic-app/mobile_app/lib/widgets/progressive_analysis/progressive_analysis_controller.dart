import 'dart:async';
import 'package:flutter/foundation.dart';
import 'progressive_analysis_phase.dart';

/// Controller for managing progressive analysis phases
class ProgressiveAnalysisController extends ChangeNotifier {
  final Map<String, bool> _phaseStates = {};
  final Map<String, bool> _phaseLoadingStates = {};
  final Map<String, String> _phaseMessages = {};
  final List<Timer> _activeTimers = [];

  // Callback for notifications
  Function(String message, {bool isError})? _onNotification;

  // Getters
  bool isPhaseActive(String phaseId) => _phaseStates[phaseId] ?? false;
  bool isPhaseLoading(String phaseId) => _phaseLoadingStates[phaseId] ?? false;
  String getPhaseMessage(String phaseId) => _phaseMessages[phaseId] ?? '';

  /// Set notification callback
  void setNotificationCallback(
      Function(String message, {bool isError})? callback) {
    _onNotification = callback;
  }

  /// Show notification
  void _showNotification(String message, {bool isError = false}) {
    _onNotification?.call(message, isError: isError);
  }

  /// Start a specific phase
  void startPhase(ProgressiveAnalysisPhase phase) {
    _phaseStates[phase.id] = true;
    _phaseLoadingStates[phase.id] = true;
    _phaseMessages[phase.id] = phase.loadingMessage;

    // Show notification with emoji
    final notificationMessage = phase.emoji != null
        ? '${phase.emoji} ${phase.loadingMessage}'
        : phase.loadingMessage;
    _showNotification(notificationMessage);

    notifyListeners();

    // Call onStart callback if provided
    phase.onStart?.call();
  }

  /// Complete a specific phase
  void completePhase(ProgressiveAnalysisPhase phase,
      {Map<String, String>? variables}) {
    _phaseLoadingStates[phase.id] = false;

    // Replace variables in completion message
    String completionMessage = phase.completionMessage;
    if (variables != null) {
      variables.forEach((key, value) {
        completionMessage = completionMessage.replaceAll('{$key}', value);
      });
    }

    _phaseMessages[phase.id] = completionMessage;

    // Show notification with emoji
    final notificationMessage = phase.emoji != null
        ? '${phase.emoji} $completionMessage'
        : completionMessage;
    _showNotification(notificationMessage);

    notifyListeners();

    // Call onComplete callback if provided
    phase.onComplete?.call();
  }

  /// Start progressive analysis with delays
  void startProgressiveAnalysis(
    List<ProgressiveAnalysisPhase> phases, {
    Function(ProgressiveAnalysisPhase phase)? onPhaseStart,
    Function(ProgressiveAnalysisPhase phase)? onPhaseComplete,
  }) {
    // Clear any existing timers
    _clearTimers();

    int cumulativeDelay = 0;

    for (final phase in phases) {
      if (phase.delaySeconds > 0) {
        // Schedule phase start with delay
        final timer = Timer(Duration(seconds: cumulativeDelay), () {
          startPhase(phase);
          onPhaseStart?.call(phase);

          // Schedule phase completion
          final completionTimer =
              Timer(Duration(seconds: phase.delaySeconds), () {
            completePhase(phase);
            onPhaseComplete?.call(phase);
          });
          _activeTimers.add(completionTimer);
        });
        _activeTimers.add(timer);
        cumulativeDelay += phase.delaySeconds;
      } else {
        // Start immediately
        startPhase(phase);
        onPhaseStart?.call(phase);
      }
    }
  }

  /// Start a specific phase with delay
  void startPhaseWithDelay(
    ProgressiveAnalysisPhase phase, {
    int delaySeconds = 0,
    Function()? onComplete,
  }) {
    if (delaySeconds > 0) {
      final timer = Timer(Duration(seconds: delaySeconds), () {
        startPhase(phase);

        // Schedule completion
        final completionTimer =
            Timer(Duration(seconds: phase.delaySeconds), () {
          completePhase(phase);
          onComplete?.call();
        });
        _activeTimers.add(completionTimer);
      });
      _activeTimers.add(timer);
    } else {
      startPhase(phase);
      if (onComplete != null) {
        final timer = Timer(Duration(seconds: phase.delaySeconds), () {
          completePhase(phase);
          onComplete();
        });
        _activeTimers.add(timer);
      }
    }
  }

  /// Clear all active timers
  void _clearTimers() {
    for (final timer in _activeTimers) {
      timer.cancel();
    }
    _activeTimers.clear();
  }

  /// Reset all phases
  void reset() {
    _clearTimers();
    _phaseStates.clear();
    _phaseLoadingStates.clear();
    _phaseMessages.clear();
    notifyListeners();
  }

  /// Dispose resources
  @override
  void dispose() {
    _clearTimers();
    super.dispose();
  }
}
