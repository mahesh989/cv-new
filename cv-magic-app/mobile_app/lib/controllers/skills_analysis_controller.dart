import 'package:flutter/material.dart';
import '../models/skills_analysis_model.dart';
import '../services/skills_analysis_service.dart';

/// States for skills analysis
enum SkillsAnalysisState {
  idle,
  loading,
  completed,
  error,
}

/// Controller for managing skills analysis operations and state
class SkillsAnalysisController extends ChangeNotifier {
  SkillsAnalysisState _state = SkillsAnalysisState.idle;
  SkillsAnalysisResult? _result;
  String? _errorMessage;
  String? _currentCvFilename;
  String? _currentJdText;
  Duration _executionDuration = Duration.zero;

  // Notification callbacks
  Function(String message, {bool isError})? _onNotification;

  // Getters for state management
  SkillsAnalysisState get state => _state;
  SkillsAnalysisResult? get result => _result;
  String? get errorMessage => _errorMessage;
  String? get currentCvFilename => _currentCvFilename;
  String? get currentJdText => _currentJdText;
  Duration get executionDuration => _executionDuration;

  // Convenience getters for UI
  bool get isLoading => _state == SkillsAnalysisState.loading;
  bool get hasResults =>
      _state == SkillsAnalysisState.completed && _result != null;
  bool get hasError => _state == SkillsAnalysisState.error;
  bool get isEmpty => _result?.isEmpty ?? true;

  // CV Skills getters
  SkillsData? get cvSkills => _result?.cvSkills;
  List<String> get cvTechnicalSkills => _result?.cvSkills.technicalSkills ?? [];
  List<String> get cvSoftSkills => _result?.cvSkills.softSkills ?? [];
  List<String> get cvDomainKeywords => _result?.cvSkills.domainKeywords ?? [];
  String? get cvComprehensiveAnalysis => _result?.cvComprehensiveAnalysis;

  // JD Skills getters
  SkillsData? get jdSkills => _result?.jdSkills;
  List<String> get jdTechnicalSkills => _result?.jdSkills.technicalSkills ?? [];
  List<String> get jdSoftSkills => _result?.jdSkills.softSkills ?? [];
  List<String> get jdDomainKeywords => _result?.jdSkills.domainKeywords ?? [];
  String? get jdComprehensiveAnalysis => _result?.jdComprehensiveAnalysis;

  // Additional getters
  List<String> get extractedKeywords => _result?.extractedKeywords ?? [];

  // Analyze Match getters
  AnalyzeMatchResult? get analyzeMatch => _result?.analyzeMatch;
  String? get analyzeMatchRawAnalysis => _result?.analyzeMatch?.rawAnalysis;
  String? get analyzeMatchCompanyName => _result?.analyzeMatch?.companyName;
  String? get analyzeMatchFilePath => _result?.analyzeMatch?.filePath;
  bool get hasAnalyzeMatch =>
      _result?.analyzeMatch != null && !_result!.analyzeMatch!.isEmpty;
  bool get hasAnalyzeMatchError => _result?.analyzeMatch?.hasError ?? false;

  // Skill counts for UI display
  int get cvTotalSkills => cvSkills?.totalSkillsCount ?? 0;
  int get jdTotalSkills => jdSkills?.totalSkillsCount ?? 0;

  // Get analysis results in a format suitable for the simple results widget
  Map<String, dynamic>? get analysisResults {
    if (_result == null) return null;

    return {
      'cv_skills': {
        'technical_skills': _result!.cvSkills.technicalSkills,
        'soft_skills': _result!.cvSkills.softSkills,
        'domain_keywords': _result!.cvSkills.domainKeywords,
      },
      'jd_skills': {
        'technical_skills': _result!.jdSkills.technicalSkills,
        'soft_skills': _result!.jdSkills.softSkills,
        'domain_keywords': _result!.jdSkills.domainKeywords,
      },
      'match_analysis': _result!.analyzeMatch?.rawAnalysis,
      'ats_score': _result!.preextractedRawOutput,
      'recommendations': _result!.cvComprehensiveAnalysis,
    };
  }

  // Notification methods
  void setNotificationCallback(
      Function(String message, {bool isError}) callback) {
    _onNotification = callback;
  }

  void _showNotification(String message, {bool isError = false}) {
    _onNotification?.call(message, isError: isError);
  }

  /// Perform skills analysis with the given CV filename and JD text
  Future<void> performAnalysis({
    required String cvFilename,
    required String jdText,
  }) async {
    // Validate inputs
    final validationError = SkillsAnalysisService.validateAnalysisInputs(
      cvFilename: cvFilename,
      jdText: jdText,
    );

    if (validationError != null) {
      _setError(validationError);
      return;
    }

    _currentCvFilename = cvFilename;
    _currentJdText = jdText;
    _setState(SkillsAnalysisState.loading);
    _clearError();

    try {
      // Check for cached results first
      print('🔍 [CONTROLLER_DEBUG] Checking for cached results...');
      final cachedResult = await SkillsAnalysisService.getCachedAnalysis(
        cvFilename: cvFilename,
        jdText: jdText,
      );

      if (cachedResult != null) {
        print('🔍 [CONTROLLER_DEBUG] Found cached results!');
        _result = cachedResult;
        _executionDuration = Duration.zero; // Cached results are instant
        _setState(SkillsAnalysisState.completed);
        debugPrint('✅ [SKILLS_ANALYSIS] Used cached results');
        _showNotification('✅ Analysis completed using cached results!');
        return;
      } else {
        print(
            '🔍 [CONTROLLER_DEBUG] No cached results found, proceeding with fresh analysis');
      }

      // Perform fresh analysis
      print('=== CONTROLLER CALLING SERVICE ===');
      debugPrint('[SKILLS_ANALYSIS] Starting fresh analysis...');
      debugPrint('   CV: $cvFilename');
      debugPrint('   JD text length: ${jdText.length} chars');

      // Show starting notification
      _showNotification('🚀 Starting skills analysis...');

      final result = await SkillsAnalysisService.performPreliminaryAnalysis(
        cvFilename: cvFilename,
        jdText: jdText,
      );

      print('=== CONTROLLER RECEIVED RESULT ===');
      print('Result success: ${result.isSuccess}');

      if (result.isSuccess) {
        _result = result;
        _executionDuration = result.executionDuration;
        _setState(SkillsAnalysisState.completed);
        debugPrint('✅ [SKILLS_ANALYSIS] Analysis completed successfully');
        debugPrint('   CV Skills: ${result.cvSkills.totalSkillsCount}');
        debugPrint('   JD Skills: ${result.jdSkills.totalSkillsCount}');
        debugPrint('   Duration: ${result.executionDuration.inSeconds}s');

        // Show success notification
        _showNotification(
          '✅ Analysis completed! Found ${result.cvSkills.totalSkillsCount} CV skills and ${result.jdSkills.totalSkillsCount} JD skills.',
        );

        // Show analyze match notification if available
        if (result.analyzeMatch != null && !result.analyzeMatch!.isEmpty) {
          _showNotification(
            '🎯 Recruiter assessment completed!',
          );
        } else if (result.analyzeMatch != null &&
            result.analyzeMatch!.hasError) {
          _showNotification(
            '⚠️ Recruiter assessment failed: ${result.analyzeMatch!.error}',
            isError: true,
          );
        }
      } else {
        _setError(result.errorMessage ?? 'Unknown error occurred');
      }
    } catch (e) {
      _setError('Skills analysis failed: $e');
      debugPrint('❌ [SKILLS_ANALYSIS] Error: $e');
    }
  }

  /// Refresh current analysis with same inputs
  Future<void> refreshAnalysis() async {
    if (_currentCvFilename != null && _currentJdText != null) {
      await performAnalysis(
        cvFilename: _currentCvFilename!,
        jdText: _currentJdText!,
      );
    }
  }

  /// Clear all results and reset to idle state
  void clearResults() {
    _result = null;
    _currentCvFilename = null;
    _currentJdText = null;
    _executionDuration = Duration.zero;
    _clearError();
    _setState(SkillsAnalysisState.idle);
  }

  /// Check if we can perform analysis with current inputs
  bool canPerformAnalysis(String? cvFilename, String? jdText) {
    return SkillsAnalysisService.validateAnalysisInputs(
          cvFilename: cvFilename,
          jdText: jdText,
        ) ==
        null;
  }

  // Private methods
  void _setState(SkillsAnalysisState newState) {
    if (_state != newState) {
      _state = newState;
      notifyListeners();
    }
  }

  void _setError(String error) {
    _errorMessage = error;
    _setState(SkillsAnalysisState.error);
  }

  void _clearError() {
    _errorMessage = null;
  }
}
