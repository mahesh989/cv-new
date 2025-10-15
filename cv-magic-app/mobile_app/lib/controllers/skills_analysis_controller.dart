import 'dart:async';
import 'package:flutter/foundation.dart';
import '../models/skills_analysis_model.dart';
import '../services/skills_analysis_service.dart';
import '../services/skills_analysis_handler.dart';
import '../services/job_parser.dart';
import '../services/jobs_state_manager.dart';

/// States for skills analysis
enum SkillsAnalysisState { idle, loading, completed, error, cancelled }

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
  bool get isCancelled => _state == SkillsAnalysisState.cancelled;
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
    Function(String message, {bool isError}) callback,
  ) {
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
          '🔍 [CONTROLLER_DEBUG] No cached results found, proceeding with fresh analysis',
        );
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

        // Save job details if analysis was successful
        await SkillsAnalysisHandler.handleAnalysisResult(
          jdText: jdText,
          result: result,
        );
        debugPrint('   CV Skills: ${result.cvSkills.totalSkillsCount}');
        debugPrint('   JD Skills: ${result.jdSkills.totalSkillsCount}');
        debugPrint('   Duration: ${result.executionDuration.inSeconds}s');

        // 🔧 Also fetch AI recommendations for standard analysis when company is available
        try {
          final company = result.preextractedCompanyName;
          if (company != null && company.trim().isNotEmpty) {
            unawaited(_tryShowLatestAIRecommendation(company));
          }
        } catch (_) {}

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

  /// Perform context-aware analysis with intelligent CV selection
  Future<void> performContextAwareAnalysis({
    required String jdUrl,
    required String company,
    required bool isRerun,
    bool includeTailoring = true,
  }) async {
    // Validate inputs
    if (jdUrl.trim().isEmpty) {
      _setError('Please provide a job description URL');
      _showNotification('Please provide a job description URL', isError: true);
      return;
    }

    if (company.trim().isEmpty) {
      _setError('Please provide a company name');
      _showNotification('Please provide a company name', isError: true);
      return;
    }

    _setState(SkillsAnalysisState.loading);
    _currentJdText = jdUrl; // Store for compatibility
    _currentCvFilename = company; // Store for compatibility

    try {
      print('🚀 [SKILLS_ANALYSIS_CONTROLLER] Starting context-aware analysis');

      // First, parse the job description and save job details
      try {
        final jobDetails = JobParser.parseJobDetails(jdUrl);
        if (jobDetails['company_name'] != null &&
            jobDetails['job_title'] != null &&
            jobDetails['location'] != null) {
          await JobsStateManager.saveNewJob(
            companyName: jobDetails['company_name']!,
            jobTitle: jobDetails['job_title']!,
            jobUrl: jobDetails['job_url'] ?? '',
            location: jobDetails['location']!,
            phoneNumber: jobDetails['phone_number'],
            email: jobDetails['email'],
          );
        }
      } catch (e) {
        debugPrint('⚠️ [SKILLS_CONTROLLER] Error saving job details: $e');
        // Continue with analysis even if saving fails
      }
      print('   JD URL: $jdUrl');
      print('   Company: $company');
      print('   Is Rerun: $isRerun');

      _result = await SkillsAnalysisService.performContextAwareAnalysis(
        jdUrl: jdUrl,
        company: company,
        isRerun: isRerun,
        includeTailoring: includeTailoring,
      );

      if (_result!.isSuccess) {
        _setState(SkillsAnalysisState.completed);
        _showNotification('Context-aware analysis completed successfully!');

        // Surface backend warnings (e.g., cv_minimal) as snackbars
        try {
          final warnings = _result!.warnings ?? [];
          if (warnings.isNotEmpty) {
            // If cv_minimal present, show a focused message
            final hasCvMinimal = warnings.any(
              (w) =>
                  (w is Map && (w['type'] == 'cv_minimal')) ||
                  (w is String && w.contains('cv_minimal')),
            );
            if (hasCvMinimal) {
              _showNotification(
                'Your CV appears minimal. We continued the analysis and generated enrichment suggestions.',
                isError: false,
              );
            } else {
              _showNotification(
                'Analysis completed with warnings.',
                isError: false,
              );
            }
          }
        } catch (_) {}

        // Save job details if analysis was successful
        await SkillsAnalysisHandler.handleAnalysisResult(
          jdText: jdUrl,
          result: _result!,
        );

        _startProgressiveDisplay();

        // Always display latest AI recommendation for this company (no fallback logic)
        // Fetch immediately and surface if available, independent of other steps
        unawaited(_tryShowLatestAIRecommendation(company));
      } else {
        _setError(_result!.errorMessage ?? 'Context-aware analysis failed');
        _showNotification(
          _result!.errorMessage ?? 'Context-aware analysis failed',
          isError: true,
        );
      }
    } catch (e) {
      _setError('Context-aware analysis failed: $e');
      _showNotification('Context-aware analysis failed: $e', isError: true);
      debugPrint('❌ [SKILLS_ANALYSIS_CONTROLLER] Error: $e');
    }
  }

  // Always fetch and display the latest AI recommendation for the company
  // This is invoked right after a successful context-aware analysis
  Future<void> _tryShowLatestAIRecommendation(String company) async {
    print(
        '🔍 [AI_REC] Fetching for company: $company, loading: $_showAIRecommendationLoading, results: $_showAIRecommendationResults');
    // Avoid regressing UI if we already have results
    if (_showAIRecommendationResults && _result?.aiRecommendation != null) {
      print('ℹ️ [AI_REC] Recommendations already present; skipping fetch');
      return;
    }
    // Strict behavior: set loading, then require file to exist; otherwise surface error
    _showAIRecommendationLoading = true;
    _showAIRecommendationResults = false;
    notifyListeners();

    try {
      // Try aggregate endpoint first
      final data =
          await SkillsAnalysisService.getCompleteAnalysisResults(company);
      if (data != null && data['ai_recommendation'] != null) {
        final aiRecommendation = AIRecommendationResult.fromJson(
          data['ai_recommendation'] as Map<String, dynamic>,
        );
        if (aiRecommendation.isEmpty) {
          throw Exception('AI recommendation exists but content is empty');
        }
        // Store AI recommendation but don't show it yet - wait for ATS score to be displayed first
        if (_fullResult != null) {
          _fullResult =
              _fullResult!.copyWith(aiRecommendation: aiRecommendation);
        }
        print(
            '✅ [AI_REC] Found recommendation, storing for later display (content length: ${aiRecommendation.content.length})');

        // Only show AI recommendations if ATS score has already been displayed
        if (_showATSResults) {
          _showAIRecommendationLoading = false;
          _showAIRecommendationResults = true;
          if (_result != null) {
            _result = _result!.copyWith(aiRecommendation: aiRecommendation);
          }
          notifyListeners();
          _showNotification('🤖 Latest AI recommendations are ready!');
          print(
              '✅ [AI_REC] Showing AI recommendations (ATS score already displayed)');
        } else {
          print(
              '⏳ [AI_REC] AI recommendations ready but waiting for ATS score to be displayed first');
        }
        return;
      }

      // Strict endpoint: must exist
      final latest =
          await SkillsAnalysisService.fetchLatestAIRecommendation(company);
      if (latest == null || !latest.hasContent) {
        // One short retry for race conditions
        await Future.delayed(const Duration(seconds: 3));
        final retry =
            await SkillsAnalysisService.fetchLatestAIRecommendation(company);
        if (retry == null || !retry.hasContent) {
          throw Exception(
              'AI recommendation file not found for company: $company');
        }

        // Store AI recommendation but don't show it yet - wait for ATS score to be displayed first
        if (_fullResult != null) {
          _fullResult = _fullResult!.copyWith(aiRecommendation: retry);
        }
        print(
            '✅ [AI_REC] Found recommendation after retry, storing for later display (content length: ${retry.content.length})');

        // Only show AI recommendations if ATS score has already been displayed
        if (_showATSResults) {
          _showAIRecommendationLoading = false;
          _showAIRecommendationResults = true;
          if (_result != null) {
            _result = _result!.copyWith(aiRecommendation: retry);
          }
          notifyListeners();
          _showNotification('🤖 Latest AI recommendations are ready!');
          print(
              '✅ [AI_REC] Showing AI recommendations after retry (ATS score already displayed)');
        } else {
          print(
              '⏳ [AI_REC] AI recommendations ready after retry but waiting for ATS score to be displayed first');
        }
        return;
      }

      // Store AI recommendation but don't show it yet - wait for ATS score to be displayed first
      if (_fullResult != null) {
        _fullResult = _fullResult!.copyWith(aiRecommendation: latest);
      }
      print(
          '✅ [AI_REC] Found recommendation, storing for later display (content length: ${latest.content.length})');

      // Only show AI recommendations if ATS score has already been displayed
      if (_showATSResults) {
        _showAIRecommendationLoading = false;
        _showAIRecommendationResults = true;
        if (_result != null) {
          _result = _result!.copyWith(aiRecommendation: latest);
        }
        notifyListeners();
        _showNotification('🤖 Latest AI recommendations are ready!');
        print(
            '✅ [AI_REC] Showing AI recommendations (ATS score already displayed)');
      } else {
        print(
            '⏳ [AI_REC] AI recommendations ready but waiting for ATS score to be displayed first');
      }
    } catch (e) {
      _showAIRecommendationLoading = false;
      _showAIRecommendationResults = false;
      notifyListeners();
      final errorMsg = 'Failed to load AI recommendations: ${e.toString()}';
      debugPrint('❌ [AI_REC] $errorMsg');
      _showNotification('❌ $errorMsg', isError: true);
    }
  }

  /// Clear all results and reset to idle state
  /// Note: This is called internally to clear analysis state, not UI inputs
  void clearResults() async {
    await SkillsAnalysisHandler.clearResults();
    _triggerClearResults();
    debugPrint('🧹 [CONTROLLER] clearResults() called');
    debugPrint('🧹 [CONTROLLER] Current state before clear: $_state');
    debugPrint('🧹 [CONTROLLER] Has results before clear: $hasResults');

    _progressiveTimer?.cancel();
    _progressiveTimer = null;
    _fullResult = null;
    _showAnalyzeMatch = false;
    _showPreextractedComparison = false;
    _showATSLoading = false;
    _showATSResults = false;
    _showAIRecommendationLoading = false;
    _showAIRecommendationResults = false;
    _result = null;
    // Keep _currentCvFilename and _currentJdText for re-runs - they're just internal tracking
    // The UI controllers are managed separately in the CV Magic page
    _currentCvFilename = null;
    _currentJdText = null;
    _executionDuration = Duration.zero;
    _clearError();
    
    // Only reset to idle if not in cancelled state (preserve cancelled state for UI)
    if (_state != SkillsAnalysisState.cancelled) {
      _setState(SkillsAnalysisState.idle);
    }

    debugPrint('🧹 [CONTROLLER] State after clear: $_state');
    debugPrint('🧹 [CONTROLLER] Has results after clear: $hasResults');
    debugPrint('🧹 [CONTROLLER] clearResults() completed');
  }

  /// Cancel the current analysis and reset to idle state
  void cancelAnalysis() {
    if (_state == SkillsAnalysisState.loading) {
      debugPrint('🛑 [CONTROLLER] Cancelling analysis...');

      // Cancel any ongoing timers
      _progressiveTimer?.cancel();
      _progressiveTimer = null;

      // Clear any partial results
      _result = null;
      _fullResult = null;
      _showAnalyzeMatch = false;
      _showPreextractedComparison = false;
      _showATSLoading = false;
      _showATSResults = false;
      _showAIRecommendationLoading = false;
      _showAIRecommendationResults = false;

      // Set cancelled state
      _setState(SkillsAnalysisState.cancelled);
      _clearError();

      // Show notification
      _showNotification('🛑 Analysis cancelled by user');

      debugPrint('🛑 [CONTROLLER] Analysis cancelled successfully');
    }
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
      debugPrint('🧹 [CONTROLLER] _setState: $_state -> $newState');
      _state = newState;
      debugPrint('🧹 [CONTROLLER] Calling notifyListeners()');
      notifyListeners();
      debugPrint('🧹 [CONTROLLER] notifyListeners() completed');
    } else {
      debugPrint('🧹 [CONTROLLER] _setState: No state change needed ($_state)');
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

    // Reset progressive state (but keep ATS states as they're managed by polling)
    _showAnalyzeMatch = false;
    _showPreextractedComparison = false;
    _showAIRecommendationLoading = false;
    _showAIRecommendationResults = false;
    // Don't reset ATS loading states here - they're managed by the polling process

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
        _result = _result!.copyWith(analyzeMatch: _fullResult!.analyzeMatch);
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

            // Step 4: Start polling for component analysis and ATS results
            _startPollingForCompleteResults();
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

          // Step 4: Start polling for component analysis and ATS results
          _startPollingForCompleteResults();
        });
      }
    }
  }

  /// Start polling for component analysis and ATS calculation results
  void _startPollingForCompleteResults() async {
    String? company = _fullResult?.preextractedCompanyName;

    // Use the top-level company name from backend response if available
    if ((company == null || company.isEmpty) && _fullResult != null) {
      // Check if there's a top-level company name in the response
      final topLevelCompany = _fullResult!.company;
      if (topLevelCompany != null && topLevelCompany.isNotEmpty) {
        company = topLevelCompany;
        print(
            '🔄 [POLLING] Using top-level company name from backend: $company');
      }
    }

    if (company == null || company.trim().isEmpty) {
      print('❌ [POLLING] No company name found for polling');
      _finishAnalysis();
      return;
    }

    print('🔄 [POLLING] Using company name for polling: $company');

    print('🔄 [POLLING] Starting polling for complete results...');
    _showNotification(
      '🔧 Running advanced analysis (component analysis & ATS calculation)...',
    );

    try {
      final completeResults =
          await SkillsAnalysisService.waitForCompleteResults(company);

      if (completeResults != null) {
        print('✅ [POLLING] Complete results obtained!');

        // Parse component analysis
        ComponentAnalysisResult? componentAnalysis;
        if (completeResults['component_analysis'] != null) {
          componentAnalysis = ComponentAnalysisResult.fromJson(
            completeResults['component_analysis'],
          );
          print(
            '📊 [POLLING] Component analysis parsed: ${componentAnalysis.extractedScores.length} scores',
          );
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
            completeResults['ai_recommendation'],
          );
          print(
            '🤖 [POLLING] AI recommendation parsed: ${aiRecommendation.content.length} chars',
          );
        }

        // Store the complete results for progressive reveal
        _fullResult = _fullResult!.copyWith(
          componentAnalysis: componentAnalysis,
          atsResult: atsResult,
          aiRecommendation: aiRecommendation,
        );

        // Store AI recommendation but don't show it yet - wait for ATS score to be displayed first
        if (aiRecommendation != null && !_showAIRecommendationResults) {
          print(
              '✅ [POLLING] AI recommendation available, storing for later display');
          // Don't show AI recommendations yet - they will be shown after ATS score
          // Just store the data for when it's time to display
        }

        // Update result with component analysis first (component analysis can show immediately)
        // DO NOT include AI recommendation yet - it will be added when it's time to display
        _result = _result!.copyWith(
          componentAnalysis: componentAnalysis,
          // aiRecommendation: aiRecommendation, // ❌ REMOVED - Don't add until display time
        );
        notifyListeners();

        // Step 5: Wait for AI-Powered Skills Analysis to complete, then show ATS loading
        if (atsResult != null) {
          // Wait for AI-Powered Skills Analysis to complete (it has a 10s timer)
          // Then show ATS loading after AI Skills Analysis is done
          Timer(Duration(seconds: 12), () {
            // Show ATS loading state and notification
            print('🔍 [CONTROLLER] Setting ATS loading state to true');
            _showATSLoading = true;
            notifyListeners();
            _showNotification('⚡ Generating enhanced ATS analysis...');

            Timer(Duration(seconds: 10), () {
              // Show ATS results after 10-second delay
              _showATSResults = true;
              _result = _result!.copyWith(
                atsResult: _fullResult!.atsResult,
                // aiRecommendation: _fullResult!.aiRecommendation, // ❌ REMOVED - Don't add until display time
              );
              notifyListeners();

              // Use the stored ATS result from _fullResult for notification
              final finalAtsResult = _fullResult!.atsResult;
              if (finalAtsResult != null) {
                _showNotification(
                  '🎯 ATS Score: ${finalAtsResult.finalATSScore.toStringAsFixed(1)}/100 (${finalAtsResult.categoryStatus})',
                );
              } else {
                _showNotification('✅ ATS Analysis completed!');
              }

              // Step 6: Now show AI recommendations AFTER ATS score is displayed
              Timer(Duration(seconds: 2), () {
                if (_fullResult?.aiRecommendation != null &&
                    !_showAIRecommendationResults) {
                  print(
                      '✅ [ATS_COMPLETE] Now showing AI recommendations after ATS score');
                  _showAIRecommendationLoading = false;
                  _showAIRecommendationResults = true;
                  _result = _result!.copyWith(
                      aiRecommendation: _fullResult!.aiRecommendation);
                  notifyListeners();
                  _showNotification('🤖 AI recommendations are ready!');
                }
                _finishAnalysis();
              });
            });
          });
        } else {
          _showNotification('✅ Advanced analysis completed!');
          _finishAnalysis();
        }
      } else {
        print('⚠️ [POLLING] Polling timed out, analysis incomplete');
        _showNotification(
          '⚠️ Advanced analysis timed out - basic analysis complete',
        );
        _finishAnalysis();
      }
    } catch (e) {
      print('❌ [POLLING] Error during polling: $e');
      _showNotification(
        '⚠️ Advanced analysis failed - basic analysis complete',
      );
      _finishAnalysis();
    }
  }

  /// Finish the analysis process
  Future<void> _saveJobFromAnalysis(String jdText) async {
    try {
      final jobDetails = JobParser.parseJobDetails(jdText);
      if (jobDetails['company_name'] != null &&
          jobDetails['job_title'] != null &&
          jobDetails['location'] != null) {
        await JobsStateManager.saveNewJob(
          companyName: jobDetails['company_name']!,
          jobTitle: jobDetails['job_title']!,
          jobUrl: jobDetails['job_url'] ?? '',
          location: jobDetails['location']!,
          phoneNumber: jobDetails['phone_number'],
          email: jobDetails['email'],
        );
      }
    } catch (e) {
      debugPrint('⚠️ [SKILLS_CONTROLLER] Error saving job details: $e');
      // Continue with analysis even if saving fails
    }
  }

  void _finishAnalysis() {
    _executionDuration = _fullResult?.executionDuration ?? Duration.zero;
    notifyListeners();
    debugPrint('🏁 [CONTROLLER] Analysis fully completed');

    // File check for latest AI recommendation existence
    (() async {
      try {
        final company =
            _fullResult?.preextractedCompanyName ?? _currentCvFilename ?? '';
        if (company.isNotEmpty) {
          final aiFile =
              await SkillsAnalysisService.fetchLatestAIRecommendation(company);
          print(
              '📁 [FILE_CHECK] AI file exists and has content: ${aiFile?.hasContent}');
        }
      } catch (_) {}
    })();
  }

  void _triggerClearResults() {
    _executionDuration = _fullResult?.executionDuration ?? Duration.zero;
    notifyListeners();
    print('🏁 [CONTROLLER] Analysis fully completed');
  }
}
