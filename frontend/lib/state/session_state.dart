import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

class SessionState {
  static String? originalCVFilename;
  static String? jdText;
  static String? jdUrl;
  static String? lastJobUrl; // Track the last job URL to detect job changes
  static String? tailoredCVFilename;
  static String? currentPrompt;
  static String? basePrompt;
  static String? matchResult;

  // Caching configuration
  static const Duration _cacheExpiration = Duration(hours: 24);
  static const String _cachePrefix = 'ats_session_cache_';

  // Cache data fields
  static DateTime? _lastCacheTime;
  static Map<String, dynamic>? _cachedATSResult;
  static List<String>? _cachedSkills;
  static Map<String, dynamic>? _cachedKeywords;
  static List<String>? _cachedKeyPhrases;
  static double? _cachedATSScore;
  static List<String>? keywords;
  static List<String>? keyPhrases;

  // Flag to indicate when new analysis is started from CV Magic
  static bool newAnalysisStarted = false;

  // ATS state persistence for tab switching
  static String? lastATSState;
  static int? lastATSScore;
  static Map<String, dynamic>? lastATSResult;

  // CV parsing results persistence
  static Map<String, dynamic>? lastCVParsingResult;

  // 🚀 NEW: Caching mechanism for last session data
  static bool enableCaching = true; // Toggle for caching behavior
  static Map<String, dynamic>? lastCachedData;

  // Cache keys
  static const String _cacheKeyEnabled = 'cache_enabled';
  static const String _cacheKeyLastCV = 'last_cv_filename';
  static const String _cacheKeyLastJD = 'last_jd_text';
  static const String _cacheKeyLastJDUrl = 'last_jd_url';
  static const String _cacheKeyLastATSResult = 'last_ats_result';
  static const String _cacheKeyLastATSScore = 'last_ats_score';
  static const String _cacheKeyLastSkills = 'last_extracted_skills';
  static const String _cacheKeyLastKeywords = 'last_keywords';
  static const String _cacheKeyLastKeyPhrases = 'last_key_phrases';
  static const String _cacheKeyTimestamp = 'cache_timestamp';

  // Cache expiration (24 hours)
  static const Duration cacheExpiration = Duration(hours: 24);

  // 🚀 NEW: Operation tracking for tab switching
  static bool isOperationInProgress = false;
  static String?
      currentOperationType; // 'cv_generation', 'ats_testing', 'cv_improvement'
  static DateTime? operationStartTime;
  static String? operationContext; // Additional context about the operation
  static Map<String, dynamic>? operationData; // Data related to the operation

  // Persistent UI state
  static List<Map<String, dynamic>>? inlineOptimizationSteps;
  static String? currentCVName;
  static String? originalCVName;

  // Custom prompts storage
  static Map<String, String> customPrompts = {};

  static bool isCVExtractionInProgress = false;
  static bool isCVDialogOpen = false;
  static bool isATSTestInProgress = false;
  static bool isATSTestDialogOpen = false;
  static bool shouldNavigateToCVMagic = false;

  static Future<void> loadFromDisk() async {
    final prefs = await SharedPreferences.getInstance();

    // Only load custom prompts - clear CV and job data every session
    currentPrompt = prefs.getString('currentPrompt');
    basePrompt = prefs.getString('basePrompt');

    // Load custom prompts
    final promptKeys = [
      // User Interface prompts
      'cv_analysis',
      'cv_generation',
      'ats_test',
      'skill_extraction',
      // Core System prompts
      'ats_system',
      'cv_tailoring',
      // Skill Analysis prompts
      'technical_skills',
      'soft_skills',
      'domain_keywords',
      // Job Processing prompts
      'job_metadata',
      'ai_matcher',
      // Skill Matching prompts
      'skill_synonyms',
      'skill_comparison_technical',
      'skill_comparison_soft',
      'domain_comparison'
    ];
    for (String key in promptKeys) {
      final value = prefs.getString('custom_prompt_$key');
      if (value != null) {
        customPrompts[key] = value;
      }
    }

    // Clear session-specific data (CV, JD, etc.) on every app start
    originalCVFilename = null;
    jdText = null;
    jdUrl = null;
    lastJobUrl = null;
    tailoredCVFilename = null;
    matchResult = null;
    keywords = null;
    keyPhrases = null;
    newAnalysisStarted = false;
    lastATSState = null;
    lastATSScore = null;
    lastATSResult = null;

    // Clear operation tracking on app start
    isOperationInProgress = false;
    currentOperationType = null;
    operationStartTime = null;
    operationContext = null;
    operationData = null;
    inlineOptimizationSteps = null;
    currentCVName = null;
    originalCVName = null;

    // Note: multi_job_ats_results (job dashboard data) is kept separate
    // and managed by MultiJobATSDashboard - not cleared here
  }

  static Future<void> saveToDisk() async {
    final prefs = await SharedPreferences.getInstance();

    // Only save prompts persistently - don't save CV/job data
    await prefs.setString('currentPrompt', currentPrompt ?? '');
    await prefs.setString('basePrompt', basePrompt ?? '');

    // Save custom prompts
    for (String key in customPrompts.keys) {
      await prefs.setString('custom_prompt_$key', customPrompts[key] ?? '');
    }

    // Don't save CV/job data to disk - keep only in memory for current session
    // This ensures CV page is cleared every time app starts
  }

  static Future<void> clearAll() async {
    originalCVFilename = null;
    jdText = null;
    jdUrl = null;
    lastJobUrl = null;
    tailoredCVFilename = null;
    currentPrompt = null;
    basePrompt = null;
    matchResult = null;
    keywords = null;
    keyPhrases = null;
    newAnalysisStarted = false;
    lastATSState = null;
    lastATSScore = null;
    lastATSResult = null;

    // Clear operation tracking
    isOperationInProgress = false;
    currentOperationType = null;
    operationStartTime = null;
    operationContext = null;
    operationData = null;
    inlineOptimizationSteps = null;
    currentCVName = null;
    originalCVName = null;

    customPrompts.clear();

    final prefs = await SharedPreferences.getInstance();
    // Only clear session data, keep job dashboard data
    await prefs.remove('currentPrompt');
    await prefs.remove('basePrompt');
    for (String key in [
      // User Interface prompts
      'cv_analysis',
      'cv_generation',
      'ats_test',
      'skill_extraction',
      // Core System prompts
      'ats_system',
      'cv_tailoring',
      // Skill Analysis prompts
      'technical_skills',
      'soft_skills',
      'domain_keywords',
      // Job Processing prompts
      'job_metadata',
      'ai_matcher',
      // Skill Matching prompts
      'skill_synonyms',
      'skill_comparison_technical',
      'skill_comparison_soft',
      'domain_comparison'
    ]) {
      await prefs.remove('custom_prompt_$key');
    }
    // Note: Don't clear 'multi_job_ats_results' - keep job dashboard data
  }

  // 🚀 NEW: Operation tracking methods
  static void startOperation(String operationType,
      {String? context, Map<String, dynamic>? data}) {
    isOperationInProgress = true;
    currentOperationType = operationType;
    operationStartTime = DateTime.now();
    operationContext = context;
    operationData = data;
    print(
        "🚀 [SESSION] Started operation: $operationType with context: $context");
  }

  static void completeOperation() {
    print("✅ [SESSION] Completed operation: $currentOperationType");
    isOperationInProgress = false;
    currentOperationType = null;
    operationStartTime = null;
    operationContext = null;
    operationData = null;
  }

  static bool isOperationExpired(
      {Duration timeout = const Duration(minutes: 5)}) {
    if (!isOperationInProgress || operationStartTime == null) return false;
    return DateTime.now().difference(operationStartTime!) > timeout;
  }

  static String getOperationDuration() {
    if (operationStartTime == null) return "Unknown";
    final duration = DateTime.now().difference(operationStartTime!);
    final minutes = duration.inMinutes;
    final seconds = duration.inSeconds % 60;
    return "${minutes}m ${seconds}s";
  }

  // 🔄 NEW: Methods to check if keywords should be reloaded
  static bool shouldReloadKeywords() {
    return originalCVFilename != null && jdText != null && jdText!.isNotEmpty;
  }

  static String? getCurrentCVJDCombination() {
    if (originalCVFilename != null && jdText != null && jdText!.isNotEmpty) {
      return '${originalCVFilename}_${jdText.hashCode}';
    }
    return null;
  }
}
