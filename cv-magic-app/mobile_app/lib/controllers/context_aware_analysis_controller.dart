import 'dart:async';
import 'package:flutter/foundation.dart';
import '../exceptions/cv_exceptions.dart';
import '../models/skills_analysis_model.dart';
import '../services/context_aware_analysis_service.dart';
import '../services/skills_analysis_service.dart';

/// States for context-aware analysis
enum ContextAwareAnalysisState {
  idle,
  loading,
  completed,
  error,
  cancelled,
}

/// Controller for managing context-aware analysis operations and state
class ContextAwareAnalysisController extends ChangeNotifier {
  ContextAwareAnalysisResult? _result;
  InitialAnalysisResult? _initialResult; // New: initial analysis result
  CVContextResult? _cvContext;
  String? _currentJdUrl;
  String? _currentCompany;
  bool _isRerun = false;
  String? _errorMessage;
  ContextAwareAnalysisState _state = ContextAwareAnalysisState.idle;
  Duration _executionDuration = Duration.zero;

  // Progressive display state
  bool _showCVContext = false;
  bool _showAnalysisResults = false;
  bool _showTailoredCV = false;
  bool _waitingForUserDecision = false; // New: flag for user decision
  SkillsAnalysisResult? _displayResult;
  bool _showAnalyzeMatchDisplay = false;
  bool _showPreextractedComparisonDisplay = false;
  bool _showATSLoading = false;
  bool _showATSResults = false;
  bool _showAIRecommendationLoading = false;
  bool _showAIRecommendationResults = false;
  Timer? _progressiveTimer;

  // Notification callbacks
  Function(String message, {bool isError})? _onNotification;

  // Getters for state management
  ContextAwareAnalysisState get state => _state;
  ContextAwareAnalysisResult? get contextResult => _result;
  SkillsAnalysisResult? get result => _displayResult;
  InitialAnalysisResult? get initialResult => _initialResult; // New
  CVContextResult? get cvContext => _cvContext;
  String? get errorMessage => _errorMessage;
  String? get currentJdUrl => _currentJdUrl;
  String? get currentCompany => _currentCompany;
  bool get isRerun => _isRerun;
  Duration get executionDuration => _executionDuration;
  bool get waitingForUserDecision => _waitingForUserDecision; // New

  // Convenience getters for UI
  bool get isLoading => _state == ContextAwareAnalysisState.loading;
  bool get hasResults =>
      _state == ContextAwareAnalysisState.completed && _displayResult != null;
  bool get hasError => _state == ContextAwareAnalysisState.error;
  bool get isCancelled => _state == ContextAwareAnalysisState.cancelled;
  bool get hasInitialResults => _initialResult != null && _initialResult!.success; // New
  bool get hasCVContext => _cvContext != null;

  // Progressive display getters
  bool get showCVContext => _showCVContext;
  bool get showAnalysisResults => _showAnalysisResults;
  bool get showTailoredCV => _showTailoredCV;
  bool get showAnalyzeMatch => _showAnalyzeMatchDisplay;
  bool get showPreextractedComparison => _showPreextractedComparisonDisplay;
  bool get showATSLoading => _showATSLoading;
  bool get showATSResults => _showATSResults;
  bool get showAIRecommendationLoading => _showAIRecommendationLoading;
  bool get showAIRecommendationResults => _showAIRecommendationResults;

  // CV Context getters
  String get cvDisplayName => _cvContext?.cvContext.displayName ?? 'Unknown CV';
  String get cvSourceDescription =>
      _cvContext?.cvContext.sourceDescription ?? '';
  bool get isUsingTailoredCV => _cvContext?.cvContext.cvType == 'tailored';
  bool get isUsingOriginalCV => _cvContext?.cvContext.cvType == 'original';

  // JD Cache getters
  bool get isJDCached => _cvContext?.jdCacheStatus.hasCache ?? false;
  String get jdCacheDescription =>
      _cvContext?.jdCacheStatus.ageDescription ?? '';
  int get jdCacheUseCount => _cvContext?.jdCacheStatus.useCount ?? 0;

  // Analysis context getters
  double get processingTime => _result?.analysisContext?.processingTime ?? 0.0;
  List<String> get stepsCompleted =>
      _result?.analysisContext?.stepsCompleted ?? [];
  List<String> get stepsSkipped => _result?.analysisContext?.stepsSkipped ?? [];
  bool get hasWarnings => _result?.hasWarnings ?? false;
  List<String> get warnings => _result?.warnings ?? [];

  // Results getters (compatible with existing UI)
  SkillsData? get cvSkills =>
      _displayResult?.cvSkills ?? _extractSkillsData(_result?.results?.cvSkills);
  SkillsData? get jdSkills =>
      _displayResult?.jdSkills ?? _extractSkillsData(_result?.results?.jdSkills);
  String? get cvComprehensiveAnalysis =>
      _displayResult?.cvComprehensiveAnalysis ??
      _result?.results?.cvSkills['comprehensive_analysis'];
  String? get jdComprehensiveAnalysis =>
      _displayResult?.jdComprehensiveAnalysis ??
      _result?.results?.jdSkills['comprehensive_analysis'];
  List<String> get extractedKeywords =>
      _displayResult?.extractedKeywords ??
      List<String>.from(_result?.results?.cvSkills['extracted_keywords'] ?? []);

  // Analyze Match getters (if available in results)
  AnalyzeMatchResult? get analyzeMatch =>
      _displayResult?.analyzeMatch ??
      _extractAnalyzeMatch(_result?.results?.cvJdMatching);
  String? get analyzeMatchRawAnalysis => analyzeMatch?.rawAnalysis;
  String? get analyzeMatchCompanyName => analyzeMatch?.companyName;
  bool get hasAnalyzeMatch => analyzeMatch != null && !analyzeMatch!.isEmpty;
  
  // New: Analyze Match Decision getters (from initial analysis)
  AnalyzeMatchDecision? get analyzeMatchDecision => _initialResult?.analyzeMatchDecision;
  bool get hasAnalyzeMatchDecision => analyzeMatchDecision != null;
  bool get shouldProceedWithFullAnalysis => _initialResult?.shouldProceed ?? false;

  // Component Analysis getters
  ComponentAnalysisResult? get componentAnalysis =>
      _displayResult?.componentAnalysis ??
      _extractComponentAnalysis(_result?.results?.componentAnalysis);
  bool get hasComponentAnalysis => componentAnalysis != null;
  double get skillsRelevanceScore =>
      componentAnalysis?.extractedScores['skills_relevance'] ?? 0.0;
  double get experienceAlignmentScore =>
      componentAnalysis?.extractedScores['experience_alignment'] ?? 0.0;
  double get industryFitScore =>
      componentAnalysis?.extractedScores['industry_fit'] ?? 0.0;
  double get roleSeniorityScore =>
      componentAnalysis?.extractedScores['role_seniority'] ?? 0.0;
  double get technicalDepthScore =>
      componentAnalysis?.extractedScores['technical_depth'] ?? 0.0;

  ATSResult? get atsResult => _displayResult?.atsResult;
  bool get hasATSResult => atsResult != null;
  AIRecommendationResult? get aiRecommendation =>
      _displayResult?.aiRecommendation;

  // Tailored CV getters
  String? get tailoredCvPath => _result?.results?.tailoredCvPath;
  bool get hasTailoredCV =>
      tailoredCvPath != null && tailoredCvPath!.isNotEmpty;

  // Skill counts for UI display
  int get cvTotalSkills => cvSkills?.totalSkillsCount ?? 0;
  int get jdTotalSkills => jdSkills?.totalSkillsCount ?? 0;

  /// Set notification callback for UI feedback
  void setNotificationCallback(
      Function(String message, {bool isError}) callback) {
    _onNotification = callback;
  }

  void _showNotification(String message, {bool isError = false}) {
    _onNotification?.call(message, isError: isError);
  }

  /// Perform context-aware analysis
  Future<void> performContextAwareAnalysis({
    required String jdUrl,
    required String company,
    required bool isRerun,
    bool includeTailoring = true,
  }) async {
    // Validate inputs
    final validationError =
        ContextAwareAnalysisService.validateContextAwareInputs(
      jdUrl: jdUrl,
      company: company,
    );

    if (validationError != null) {
      _setError(validationError);
      _showNotification(validationError, isError: true);
      return;
    }

    _setLoading();
    _currentJdUrl = jdUrl;
    _currentCompany = company;
    _isRerun = isRerun;

    try {
      print('🚀 [CONTEXT_AWARE_CONTROLLER] Starting context-aware analysis');
      print('   JD URL: $jdUrl');
      print('   Company: $company');
      print('   Is Rerun: $isRerun');

      // First, get CV context for user feedback
      print('🔍 [CONTEXT_AWARE_CONTROLLER] Getting CV context...');
      _cvContext = await ContextAwareAnalysisService.getCVContext(
        company: company,
        isRerun: isRerun,
      );

      if (_cvContext != null) {
        _showCVContext = true;
        notifyListeners();

        // Show context information to user
        final contextMessage = _buildContextMessage();
        _showNotification(contextMessage);

        // Brief delay to show context
        await Future.delayed(const Duration(milliseconds: 500));
      }

      // Perform initial analysis (stops after analyze match)
      print('🔍 [CONTEXT_AWARE_CONTROLLER] Performing initial analysis...');
      _initialResult = await ContextAwareAnalysisService.performInitialAnalysis(
        jdUrl: jdUrl,
        company: company,
        isRerun: isRerun,
      );

      if (_initialResult!.success) {
        _executionDuration = _initialResult!.processingTime;
        debugPrint('✅ [CONTEXT_AWARE_CONTROLLER] Initial analysis successful');
        debugPrint('   requiresUserDecision: ${_initialResult!.requiresUserDecision}');
        debugPrint('   analyzeMatchDecision: ${_initialResult!.analyzeMatchDecision != null}');
        
        // Convert initial results to SkillsAnalysisResult for UI display
        // This allows showing CV vs JD skills BEFORE analyze match decision
        if (_initialResult!.results != null) {
          final initialResults = _initialResult!.results!;
          _displayResult = SkillsAnalysisResult(
            cvSkills: SkillsData.fromJson(initialResults.cvSkills),
            jdSkills: SkillsData.fromJson(initialResults.jdSkills),
            cvComprehensiveAnalysis: '',
            jdComprehensiveAnalysis: '',
            expandableAnalysis: null,
            extractedKeywords: [],
            executionDuration: _initialResult!.processingTime,
            isSuccess: true,
            analyzeMatch: null, // Will be shown in decision card
            preextractedRawOutput: null,
            preextractedCompanyName: _currentCompany,
          );
          debugPrint('✅ [CONTEXT_AWARE_CONTROLLER] Created _displayResult with initial skills');
          debugPrint('   CV Skills count: ${_displayResult!.cvSkills.totalSkillsCount}');
          debugPrint('   JD Skills count: ${_displayResult!.jdSkills.totalSkillsCount}');
          debugPrint('   CV Technical: ${_displayResult!.cvSkills.technicalSkills}');
          debugPrint('   CV Soft: ${_displayResult!.cvSkills.softSkills}');
          debugPrint('   JD Technical: ${_displayResult!.jdSkills.technicalSkills}');
          debugPrint('   JD Soft: ${_displayResult!.jdSkills.softSkills}');
        }
        
        // ALWAYS stop after initial analysis - require user decision
        // Check if user decision is required
        if (_initialResult!.requiresUserDecision && _initialResult!.analyzeMatchDecision != null) {
          debugPrint('⏸️ [CONTEXT_AWARE_CONTROLLER] Stopping for user decision');
          _waitingForUserDecision = true;
          _setCompleted(); // Set completed but waiting for decision
          debugPrint('   State after setCompleted: $_state');
          debugPrint('   _displayResult != null: ${_displayResult != null}');
          debugPrint('   hasResults getter will return: ${_state == ContextAwareAnalysisState.completed && _displayResult != null}');
          debugPrint('   About to call notifyListeners()');
          
          // Show decision message
          final decision = _initialResult!.analyzeMatchDecision!;
          final decisionMessage = _buildDecisionMessage(decision);
          _showNotification(decisionMessage);
          
          debugPrint('📊 [CONTEXT_AWARE_CONTROLLER] Decision: ${decision.decision}, Score: ${decision.matchScore}%');
          debugPrint('   waitingForUserDecision: $_waitingForUserDecision');
          debugPrint('   hasAnalyzeMatchDecision: ${hasAnalyzeMatchDecision}');
          debugPrint('   hasResults (for UI): $hasResults');
          
          notifyListeners();
          return; // Stop here, wait for user decision - DO NOT CONTINUE AUTOMATICALLY
        } else {
          // If no decision data, still show what we have and wait
          debugPrint('⚠️ [CONTEXT_AWARE_CONTROLLER] No decision data, but stopping anyway');
          _waitingForUserDecision = true;
          _setCompleted();
          notifyListeners();
          return; // Stop here - don't continue automatically
        }
      } else {
        String errorMessage = _initialResult!.errors.isNotEmpty
            ? _initialResult!.errors.first
            : 'Initial analysis failed';
        _setError(errorMessage);
        _showNotification(errorMessage, isError: true);
      }
    } catch (e) {
      if (e is TailoredCVNotFoundException) {
        String errorMessage =
            'No tailored CV is available. Please create a tailored CV first.';
        _setError(errorMessage);
        _showNotification(errorMessage, isError: true);
      } else {
        _setError('Context-aware analysis failed: $e');
        _showNotification('Context-aware analysis failed: $e', isError: true);
      }
      debugPrint('❌ [CONTEXT_AWARE_CONTROLLER] Error: $e');
    }
  }

  /// Continue full analysis after user decision
  Future<void> continueFullAnalysis({bool includeTailoring = true}) async {
    if (_currentCompany == null) {
      _setError('No company selected for continuation');
      return;
    }

    if (!_waitingForUserDecision) {
      _setError('Not waiting for user decision');
      return;
    }

    await _continueFullAnalysis(includeTailoring: includeTailoring);
  }

  /// Internal method to continue full analysis
  Future<void> _continueFullAnalysis({bool includeTailoring = true}) async {
    try {
      // Don't call _setLoading() to keep initial results visible
      // Just update the state to indicate we're processing
      _state = ContextAwareAnalysisState.loading;
      _waitingForUserDecision = false;
      // Keep _showCVContext true so initial results remain visible
      notifyListeners();

      print('🚀 [CONTEXT_AWARE_CONTROLLER] Continuing full analysis...');
      _result = await ContextAwareAnalysisService.continueFullAnalysis(
        company: _currentCompany!,
        includeTailoring: includeTailoring,
      );

      if (_result!.success) {
        _executionDuration = _result!.processingTime;
        _setCompleted();
        _showAnalysisResults = true;

        // Build display-friendly result
        _initializeDisplayResult();

        // Show completion message
        final completionMessage = _buildCompletionMessage();
        _showNotification(completionMessage);

        // Start progressive display
        _startProgressiveDisplay();
      } else {
        // STOP processing on error - don't continue or poll
        String errorMessage = _result!.errors.isNotEmpty
            ? _result!.errors.first
            : 'Full analysis failed';
        _setError(errorMessage);
        _showNotification(errorMessage, isError: true);
        debugPrint('❌ [CONTEXT_AWARE_CONTROLLER] Analysis failed, stopping all processing');
        // Cancel any timers to prevent further attempts
        _progressiveTimer?.cancel();
        _progressiveTimer = null;
        return; // STOP here, don't continue
      }
    } catch (e) {
      // STOP processing on exception
      _setError('Failed to continue full analysis: $e');
      _showNotification('Failed to continue full analysis: $e', isError: true);
      debugPrint('❌ [CONTEXT_AWARE_CONTROLLER] Error continuing: $e');
      // Cancel any timers
      _progressiveTimer?.cancel();
      _progressiveTimer = null;
      return; // STOP here, don't continue
    }
  }

  /// Skip full analysis (user declined)
  void skipFullAnalysis() {
    if (_waitingForUserDecision) {
      _waitingForUserDecision = false;
      _setCompleted();
      _showNotification('⏭️ Skipped full analysis. Initial results available.');
      notifyListeners();
    }
  }

  /// Refresh current analysis with same inputs (rerun)
  Future<void> refreshAnalysis() async {
    if (_currentJdUrl != null && _currentCompany != null) {
      await performContextAwareAnalysis(
        jdUrl: _currentJdUrl!,
        company: _currentCompany!,
        isRerun: true, // Always rerun when refreshing
        includeTailoring: true,
      );
    }
  }

  /// Clear all results and reset to idle state
  void clearResults() {
    _progressiveTimer?.cancel();
    _progressiveTimer = null;

    _result = null;
    _displayResult = null;
    _initialResult = null; // New
    _cvContext = null;
    _currentJdUrl = null;
    _currentCompany = null;
    _isRerun = false;
    _errorMessage = null;
    _state = ContextAwareAnalysisState.idle;
    _executionDuration = Duration.zero;

    _showCVContext = false;
    _showAnalysisResults = false;
    _showTailoredCV = false;
    _waitingForUserDecision = false; // New
    _showAnalyzeMatchDisplay = false;
    _showPreextractedComparisonDisplay = false;
    _showATSLoading = false;
    _showATSResults = false;
    _showAIRecommendationLoading = false;
    _showAIRecommendationResults = false;

    notifyListeners();
  }

  /// Cancel the current analysis and reset to idle state
  void cancelAnalysis() {
    if (_state == ContextAwareAnalysisState.loading) {
      debugPrint('🛑 [CONTEXT_AWARE_CONTROLLER] Cancelling analysis...');

      // Cancel any ongoing timers
      _progressiveTimer?.cancel();
      _progressiveTimer = null;

      // Clear any partial results
      _result = null;
      _cvContext = null;
      _showCVContext = false;
      _showAnalysisResults = false;
      _showTailoredCV = false;

      // Set cancelled state
      _state = ContextAwareAnalysisState.cancelled;
      _errorMessage = null;

      // Show notification
      _showNotification('🛑 Analysis cancelled by user');

      notifyListeners();
      debugPrint(
          '🛑 [CONTEXT_AWARE_CONTROLLER] Analysis cancelled successfully');
    }
  }

  /// Set loading state
  void _setLoading() {
    _state = ContextAwareAnalysisState.loading;
    _errorMessage = null;
    _showCVContext = false;
    _showAnalysisResults = false;
    _showTailoredCV = false;
    notifyListeners();
  }

  /// Set completed state
  void _setCompleted() {
    _state = ContextAwareAnalysisState.completed;
    _errorMessage = null;
    notifyListeners();
  }

  /// Set error state
  void _setError(String error) {
    _state = ContextAwareAnalysisState.error;
    _errorMessage = error;
    notifyListeners();
  }

  /// Start progressive display of results
  void _startProgressiveDisplay() {
    _progressiveTimer?.cancel();

    // Show analysis results after a brief delay
    _progressiveTimer = Timer(const Duration(milliseconds: 800), () {
      _showAnalysisResults = true;
      notifyListeners();
    });

    // Show tailored CV if available after another delay
    if (hasTailoredCV) {
      _progressiveTimer = Timer(const Duration(milliseconds: 1500), () {
        _showTailoredCV = true;
        notifyListeners();
      });
    }
  }

  void _initializeDisplayResult() {
    final results = _result?.results;
    if (results == null) {
      _displayResult = null;
      return;
    }

    final baseJson = <String, dynamic>{
      'cv_skills': results.cvSkills,
      'jd_skills': results.jdSkills,
      'cv_comprehensive_analysis':
          results.cvSkills['comprehensive_analysis'],
      'jd_comprehensive_analysis':
          results.jdSkills['comprehensive_analysis'],
      'analyze_match': results.cvJdMatching,
      'company': _currentCompany,
      'warnings': _result?.warnings,
      'suggestions': results.jobInfo['suggestions'],
    };

    if (results.aiRecommendations.isNotEmpty) {
      baseJson['ai_recommendation'] = results.aiRecommendations;
    }
    if (results.componentAnalysis.isNotEmpty) {
      baseJson['component_analysis'] = results.componentAnalysis;
    }
    if (results.jobInfo['preextracted_skills_comparison'] != null) {
      baseJson['preextracted_skills_comparison'] =
          results.jobInfo['preextracted_skills_comparison'];
    }

    _displayResult = SkillsAnalysisResult.fromJson(baseJson);
    _updateDisplayFlags();

    // Begin polling for complete ATS/component results
    _showATSLoading = true;
    if (_displayResult?.aiRecommendation == null) {
      _showAIRecommendationLoading = true;
    }
    notifyListeners();
    unawaited(_pollForCompleteResults());
  }

  Future<void> _pollForCompleteResults() async {
    if (_currentCompany == null) {
      return;
    }

    final completeResults =
        await SkillsAnalysisService.waitForCompleteResults(
      _currentCompany!,
      maxWaitTimeSeconds: 120,
    );

    if (completeResults == null) {
      _showATSLoading = false;
      _showAIRecommendationLoading = false;
      notifyListeners();
      return;
    }

    final preextracted =
        completeResults['preextracted_skills_comparison'] as Map<String, dynamic>?;

    _displayResult = (_displayResult ??
            SkillsAnalysisResult.fromJson({
              'cv_skills': _result?.results?.cvSkills ?? {},
              'jd_skills': _result?.results?.jdSkills ?? {},
            }))
        .copyWith(
      componentAnalysis: completeResults['component_analysis'] != null
          ? ComponentAnalysisResult.fromJson(
              completeResults['component_analysis'])
          : _displayResult?.componentAnalysis,
      atsResult: completeResults['ats_score'] != null
          ? ATSResult.fromJson(completeResults['ats_score'])
          : _displayResult?.atsResult,
      aiRecommendation: completeResults['ai_recommendation'] != null
          ? AIRecommendationResult.fromJson(
              completeResults['ai_recommendation'])
          : _displayResult?.aiRecommendation,
      preextractedRawOutput:
          preextracted?['raw_output'] ?? _displayResult?.preextractedRawOutput,
      preextractedCompanyName: preextracted?['company_name'] ??
          completeResults['company'] ??
          _displayResult?.preextractedCompanyName,
      company: completeResults['company'] ?? _displayResult?.company,
    );

    _showATSLoading = false;
    _updateDisplayFlags();
    notifyListeners();
  }

  void _updateDisplayFlags() {
    _showAnalyzeMatchDisplay = _displayResult?.analyzeMatch != null;
    _showPreextractedComparisonDisplay =
        _displayResult?.hasPreextractedComparison ?? false;
    final hasATS = _displayResult?.atsResult != null;
    if (hasATS) {
      _showATSResults = true;
    }
    final hasAI = _displayResult?.aiRecommendation?.hasContent ?? false;
    if (hasAI) {
      _showAIRecommendationLoading = false;
      _showAIRecommendationResults = true;
    }
  }

  /// Build context message for user feedback
  String _buildContextMessage() {
    if (_cvContext == null) return '';

    final cvContext = _cvContext!.cvContext;

    String message = '📄 ${cvContext.displayName}';

    if (isJDCached) {
      message += ' • ♻️ JD cached (${jdCacheDescription})';
    } else {
      message += ' • 🆕 Fresh JD analysis';
    }

    if (isRerun) {
      message += ' • 🔄 Rerun analysis';
    } else {
      message += ' • 🆕 Fresh analysis';
    }

    return message;
  }

  /// Build decision message for analyze match
  String _buildDecisionMessage(AnalyzeMatchDecision decision) {
    String message = '🔍 Analyze Match: ';
    
    if (decision.isProceed) {
      message += '✅ Strong Match (${decision.matchScore}%) - Proceed recommended';
    } else if (decision.isMaybe) {
      message += '⚠️ Conditional Match (${decision.matchScore}%) - Consider proceeding';
    } else if (decision.isDontProceed) {
      message += '❌ Not Recommended (${decision.matchScore}%) - Consider skipping';
    } else {
      message += '❓ Unknown (${decision.matchScore}%)';
    }
    
    if (decision.primaryReason.isNotEmpty) {
      message += '\n${decision.primaryReason}';
    }
    
    return message;
  }

  /// Build completion message
  String _buildCompletionMessage() {
    if (_result == null) return 'Analysis completed';

    String message =
        '✅ Analysis completed in ${processingTime.toStringAsFixed(1)}s';

    if (stepsSkipped.isNotEmpty) {
      message += ' • ⚡ ${stepsSkipped.length} steps optimized';
    }

    if (hasTailoredCV) {
      message += ' • ✨ Tailored CV generated';
    }

    if (hasWarnings) {
      message += ' • ⚠️ ${warnings.length} warnings';
    }

    return message;
  }

  /// Extract SkillsData from analysis results
  SkillsData? _extractSkillsData(Map<String, dynamic>? skillsData) {
    if (skillsData == null) return null;

    return SkillsData(
      technicalSkills: List<String>.from(skillsData['technical_skills'] ?? []),
      softSkills: List<String>.from(skillsData['soft_skills'] ?? []),
      domainKeywords: List<String>.from(skillsData['domain_keywords'] ?? []),
    );
  }

  /// Extract AnalyzeMatchResult from analysis results
  AnalyzeMatchResult? _extractAnalyzeMatch(Map<String, dynamic>? matchingData) {
    if (matchingData == null) return null;

    return AnalyzeMatchResult(
      rawAnalysis: matchingData['raw_analysis'] ?? '',
      companyName: matchingData['company_name'] ?? '',
      filePath: matchingData['file_path'],
      error: matchingData['has_error'] == true ? 'Analysis error' : null,
    );
  }

  /// Extract ComponentAnalysisResult from analysis results
  ComponentAnalysisResult? _extractComponentAnalysis(
      Map<String, dynamic>? componentData) {
    if (componentData == null) return null;

    // Create extracted scores map
    final extractedScores = <String, double>{
      'skills_relevance': (componentData['skills_relevance'] ?? 0.0).toDouble(),
      'experience_alignment':
          (componentData['experience_alignment'] ?? 0.0).toDouble(),
      'industry_fit': (componentData['industry_fit'] ?? 0.0).toDouble(),
      'role_seniority': (componentData['role_seniority'] ?? 0.0).toDouble(),
      'technical_depth': (componentData['technical_depth'] ?? 0.0).toDouble(),
    };

    return ComponentAnalysisResult(
      timestamp: DateTime.now().toIso8601String(),
      extractedScores: extractedScores,
      componentDetails: componentData,
    );
  }

  @override
  void dispose() {
    _progressiveTimer?.cancel();
    super.dispose();
  }
}
