import 'dart:async';
import 'package:flutter/foundation.dart';
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
  SkillsAnalysisResult? _result;
  String? _currentCvFilename;
  String? _currentJdText;
  String? _errorMessage;
  SkillsAnalysisState _state = SkillsAnalysisState.idle;
  Duration _executionDuration = Duration.zero;
  
  // Progressive display state
  SkillsAnalysisResult? _fullResult; // Complete result from API
  bool _showAnalyzeMatch = false;
  bool _showPreextractedComparison = false;
  Timer? _progressiveTimer;

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
  
  // Progressive display getters
  bool get showAnalyzeMatch => _showAnalyzeMatch;
  bool get showPreextractedComparison => _showPreextractedComparison;

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
        debugPrint('✅ [SKILLS_ANALYSIS] Analysis completed successfully');
        debugPrint('   CV Skills: ${result.cvSkills.totalSkillsCount}');
        debugPrint('   JD Skills: ${result.jdSkills.totalSkillsCount}');
        debugPrint('   Duration: ${result.executionDuration.inSeconds}s');

        // Store full result and start progressive display
        _fullResult = result;
        _startProgressiveDisplay();
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
    _progressiveTimer?.cancel();
    _progressiveTimer = null;
    _fullResult = null;
    _showAnalyzeMatch = false;
    _showPreextractedComparison = false;
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
  
  /// Start progressive display of results
  void _startProgressiveDisplay() {
    if (_fullResult == null) return;
    
    // Reset progressive state
    _showAnalyzeMatch = false;
    _showPreextractedComparison = false;
    
    // Step 1: Show skills immediately (side-by-side display)
    _result = SkillsAnalysisResult(
      cvSkills: _fullResult!.cvSkills,
      jdSkills: _fullResult!.jdSkills,
      cvComprehensiveAnalysis: _fullResult!.cvComprehensiveAnalysis,
      jdComprehensiveAnalysis: _fullResult!.jdComprehensiveAnalysis,
      expandableAnalysis: _fullResult!.expandableAnalysis,
      extractedKeywords: _fullResult!.extractedKeywords,
      executionDuration: _fullResult!.executionDuration,
      isSuccess: true,
      // Don't show these yet
      analyzeMatch: null,
      preextractedRawOutput: null,
      preextractedCompanyName: null,
    );
    
    _setState(SkillsAnalysisState.completed);
    _showNotification(
      '✅ Skills extracted! Found ${_fullResult!.cvSkills.totalSkillsCount} CV skills and ${_fullResult!.jdSkills.totalSkillsCount} JD skills.',
    );
    
    // Step 2: Show analyze match loading immediately, then results after 10 seconds
    if (_fullResult?.analyzeMatch != null) {
      // Immediately show loading state and notification
      _showAnalyzeMatch = true;
      notifyListeners();
      _showNotification('📎 Starting recruiter assessment analysis...');
      
      Timer(Duration(seconds: 10), () {
        // Show analyze match results
        _result = _result!.copyWith(
          analyzeMatch: _fullResult!.analyzeMatch,
        );
        notifyListeners();
        _showNotification('🎯 Recruiter assessment completed!');
        
        // Step 3: Immediately show preextracted comparison loading
        if (_fullResult?.preextractedRawOutput != null) {
          _showPreextractedComparison = true;
          notifyListeners();
          _showNotification('📈 Starting skills comparison analysis...');
          
          Timer(Duration(seconds: 10), () {
            // Show preextracted comparison results
            _result = _result!.copyWith(
              preextractedRawOutput: _fullResult!.preextractedRawOutput,
              preextractedCompanyName: _fullResult!.preextractedCompanyName,
            );
            notifyListeners();
            _showNotification('📊 Skills comparison analysis completed!');
            
            // Final step: Analysis fully complete
            Timer(Duration(seconds: 1), () {
              _executionDuration = _fullResult!.executionDuration;
              notifyListeners();
            });
          });
        }
      });
    } else {
      // No analyze match, go directly to preextracted comparison
      if (_fullResult?.preextractedRawOutput != null) {
        _showPreextractedComparison = true;
        notifyListeners();
        _showNotification('📈 Starting skills comparison analysis...');
        
        Timer(Duration(seconds: 10), () {
          _result = _result!.copyWith(
            preextractedRawOutput: _fullResult!.preextractedRawOutput,
            preextractedCompanyName: _fullResult!.preextractedCompanyName,
          );
          notifyListeners();
          _showNotification('📊 Skills comparison analysis completed!');
          
          Timer(Duration(seconds: 1), () {
            _executionDuration = _fullResult!.executionDuration;
            notifyListeners();
          });
        });
      }
    }
  }
}
