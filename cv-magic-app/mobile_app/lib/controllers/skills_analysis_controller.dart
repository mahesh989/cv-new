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
  bool _showATSLoading = false;
  bool _showATSResults = false;
  bool _showAIRecommendationLoading = false;
  bool _showAIRecommendationResults = false;
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
  bool get showATSLoading => _showATSLoading;
  bool get showATSResults => _showATSResults;
  bool get showAIRecommendationLoading => _showAIRecommendationLoading;
  bool get showAIRecommendationResults => _showAIRecommendationResults;

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

  // Component Analysis getters (used by ATS widgets)
  ComponentAnalysisResult? get componentAnalysis => _result?.componentAnalysis;
  bool get hasComponentAnalysis => _result?.componentAnalysis != null;
  double get skillsRelevanceScore =>
      _result?.componentAnalysis?.skillsRelevance ?? 0.0;
  double get experienceAlignmentScore =>
      _result?.componentAnalysis?.experienceAlignment ?? 0.0;
  double get industryFitScore => _result?.componentAnalysis?.industryFit ?? 0.0;
  double get roleSeniorityScore =>
      _result?.componentAnalysis?.roleSeniority ?? 0.0;
  double get technicalDepthScore =>
      _result?.componentAnalysis?.technicalDepth ?? 0.0;

  // ATS Result getters
  ATSResult? get atsResult => _result?.atsResult;
  bool get hasATSResult => _result?.atsResult != null;
  double get atsScore => _result?.atsResult?.finalATSScore ?? 0.0;
  String get atsStatus => _result?.atsResult?.categoryStatus ?? '';
  String get atsRecommendation => _result?.atsResult?.recommendation ?? '';

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

      // Perform basic skills extraction first (fast response)
      print('=== CONTROLLER CALLING SERVICE (BASIC) ===');
      debugPrint('[SKILLS_ANALYSIS] Starting basic skills extraction...');
      debugPrint('   CV: $cvFilename');
      debugPrint('   JD text length: ${jdText.length} chars');

      // Show starting notification
      _showNotification('🚀 Starting skills extraction...');

      final result = await SkillsAnalysisService.performBasicSkillsExtraction(
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
    _showATSLoading = false;
    _showATSResults = false;
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
    _showATSLoading = false;
    _showATSResults = false;
    _showAIRecommendationLoading = false;
    _showAIRecommendationResults = false;

    // Step 1: Show initial skills immediately (side-by-side display)
    // Include analyze match and preextracted comparison if already available from backend
    _result = SkillsAnalysisResult(
      cvSkills: _fullResult!.cvSkills,
      jdSkills: _fullResult!.jdSkills,
      cvComprehensiveAnalysis: _fullResult!.cvComprehensiveAnalysis,
      jdComprehensiveAnalysis: _fullResult!.jdComprehensiveAnalysis,
      expandableAnalysis: _fullResult!.expandableAnalysis,
      extractedKeywords: _fullResult!.extractedKeywords,
      executionDuration: _fullResult!.executionDuration,
      isSuccess: true,
      // Include results that are already available from backend
      analyzeMatch: _fullResult!.analyzeMatch,
      preextractedRawOutput: _fullResult!.preextractedRawOutput,
      preextractedCompanyName: _fullResult!.preextractedCompanyName,
    );

    _setState(SkillsAnalysisState.completed);
    _showNotification(
      '✅ Skills extracted! Found ${_fullResult!.cvSkills.totalSkillsCount} CV skills and ${_fullResult!.jdSkills.totalSkillsCount} JD skills.',
    );

    // Start polling immediately for additional pipeline results (analyze match, skills comparison, ATS, AI recommendations)
    _startPollingForCompleteResults();
  }

  /// Start polling for component analysis and ATS calculation results
  void _startPollingForCompleteResults() async {
    final company = _fullResult?.preextractedCompanyName;
    if (company == null || company.isEmpty) {
      print('❌ [POLLING] No company name found for polling');
      _finishAnalysis();
      return;
    }

    print('🔄 [POLLING] Starting polling for progressive results...');

    try {
      // Poll for results
      final results =
          await SkillsAnalysisService.waitForCompleteResults(company);
      if (results == null) {
        print('⚠️ [POLLING] No results available yet');
        return;
      }

      if (completeResults != null) {
        print('✅ [POLLING] Complete results obtained!');

        // Parse component analysis
        ComponentAnalysisResult? componentAnalysis;
        if (completeResults['component_analysis'] != null) {
          componentAnalysis = ComponentAnalysisResult.fromJson(
              completeResults['component_analysis']);
          print(
              '📊 [POLLING] Component analysis parsed: ${componentAnalysis.extractedScores.length} scores');
        }

        // Parse ATS result
        ATSResult? atsResult;
        if (completeResults['ats_score'] != null) {
          atsResult = ATSResult.fromJson(completeResults['ats_score']);
          print('🎯 [POLLING] ATS result parsed: ${atsResult.finalATSScore}');
        }

        // Parse AI recommendation
        AIRecommendationResult? aiRecommendation;
        if (completeResults['ai_recommendation'] != null) {
          aiRecommendation = AIRecommendationResult.fromJson(
              completeResults['ai_recommendation']);
          print(
              '🤖 [POLLING] AI recommendation parsed: ${aiRecommendation.content.length} chars');
        }

        // Store the complete results for progressive reveal
        _fullResult = _fullResult!.copyWith(
          componentAnalysis: componentAnalysis,
          atsResult: atsResult,
          aiRecommendation: aiRecommendation,
        );

        // Update result with component analysis first (component analysis can show immediately)
      }

      // Handle analyze match results if available
      if (results['analyze_match'] != null && !_showAnalyzeMatch) {
        _showAnalyzeMatch = true;
        _result = _result!.copyWith(
          analyzeMatch: AnalyzeMatchResult.fromJson(results['analyze_match']),
        );
        notifyListeners();
        _showNotification('🎯 Recruiter assessment completed!');
      }

      // Handle preextracted comparison if available
      if (results['preextracted_comparison'] != null &&
          !_showPreextractedComparison) {
        _showPreextractedComparison = true;
        _result = _result!.copyWith(
          preextractedRawOutput: results['preextracted_comparison']
              ['raw_content'],
          preextractedCompanyName: results['preextracted_comparison']
              ['company_name'],
        );
        notifyListeners();
        _showNotification('📊 Skills comparison analysis completed!');
      }

      // Handle component analysis if available
      if (results['component_analysis'] != null) {
        ComponentAnalysisResult componentAnalysis =
            ComponentAnalysisResult.fromJson(results['component_analysis']);
        _result = _result!.copyWith(componentAnalysis: componentAnalysis);
        notifyListeners();
      }

      // Handle ATS results if available
      if (results['ats_score'] != null && !_showATSResults) {
        _showATSResults = true;
        ATSResult atsResult = ATSResult.fromJson(results['ats_score']);
        _result = _result!.copyWith(atsResult: atsResult);
        notifyListeners();
        _showNotification(
            '🎯 ATS Score: ${atsResult.finalATSScore.toStringAsFixed(1)}/100 (${atsResult.categoryStatus})');
      }

      // Handle AI recommendation if available
      if (results['ai_recommendation'] != null &&
          !_showAIRecommendationResults) {
        _showAIRecommendationResults = true;
        AIRecommendationResult aiRecommendation =
            AIRecommendationResult.fromJson(results['ai_recommendation']);
        _result = _result!.copyWith(aiRecommendation: aiRecommendation);
        notifyListeners();
        _showNotification('✅ AI recommendations completed!');
      }

      // Continue polling if any component is missing
      if (!_hasAllComponents()) {
        print(
            '🔄 [POLLING] Some components still missing, continuing to poll...');
        Timer(Duration(seconds: 2), () {
          _startPollingForCompleteResults();
        });
      } else {
        print('✅ [POLLING] All components received');
        _finishAnalysis();
      }
    } catch (e) {
      print('❌ [POLLING] Error during polling: $e');
      _showNotification('⚠️ Some analysis components could not be loaded');
      _finishAnalysis();
    }
  }

  bool _hasAllComponents() {
    return _result?.analyzeMatch != null &&
        _result?.preextractedRawOutput != null &&
        _result?.componentAnalysis != null &&
        _result?.atsResult != null &&
        _result?.aiRecommendation != null;
  }

  /// Finish the analysis process
  void _finishAnalysis() {
    _executionDuration = _fullResult?.executionDuration ?? Duration.zero;
    notifyListeners();
    print('🏁 [CONTROLLER] Analysis fully completed');
  }
}
