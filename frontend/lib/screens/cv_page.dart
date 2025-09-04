import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;

import '../dialogs/cv_analysis_dialog.dart';
import '../services/api_service.dart' as api;

import '../state/session_state.dart';
import '../widgets/cv_uploader.dart';
import '../widgets/cv_selector.dart';
import '../widgets/job_input.dart';
import '../widgets/modular_analysis_widget.dart';

import '../theme/app_theme.dart';
import '../../main.dart';
import '../utils/notification_service.dart';
import '../utils/responsive_utils.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../services/keyword_cache_service.dart';

class SectionCard extends StatelessWidget {
  final Widget child;
  const SectionCard({super.key, required this.child});
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: AppTheme.cardRadius,
        boxShadow: AppTheme.cardShadow,
      ),
      child: child,
    );
  }
}

class CvPage extends StatefulWidget {
  const CvPage({super.key});

  // Expose the JD skills cache for other tabs
  static Map<String, Map<String, dynamic>> get jdSkillsCache =>
      _CvPageState.jdSkillsCache;

  // Expose the CV parsing cache for other widgets
  static Map<String, Map<String, dynamic>> get cvParsingCache =>
      _CvPageState.cvParsingCache;

  // Expose the CV content cache for other widgets
  static Map<String, String> get cvContentCache => _CvPageState.cvContentCache;

  @override
  State<CvPage> createState() => _CvPageState();
}

class _CvPageState extends State<CvPage> with AutomaticKeepAliveClientMixin {
  final api.ApiService _apiService = api.ApiService();

  // Modular analysis is now handled by ModularAnalysisWidget

  PlatformFile? pickedFile;
  String? selectedCVFilename;
  List<String> uploadedCVs = [];
  final TextEditingController jdController = TextEditingController();
  final TextEditingController jdUrlController = TextEditingController();
  String matchResult = '';
  bool isSaving = false;
  double uploadProgress = 0;
  String currentPrompt = 'Default analysis prompt';
  bool _initialLoaded = false;

  Map<String, dynamic> cvSkills = {};
  bool isExtractingSkills = false;
  static final Map<String, Map<String, dynamic>> cvSkillsCache = {};

  Map<String, dynamic> jdSkills = {};
  bool isExtractingJDSkills = false;
  static final Map<String, Map<String, dynamic>> jdSkillsCache = {};

  // CV parsing results cache
  static final Map<String, Map<String, dynamic>> cvParsingCache = {};

  bool showFullCVAnalysis = false;
  bool showFullJDAnalysis = false;

  // CV content display
  String cvContent = '';
  bool isLoadingCVContent = false;
  static final Map<String, String> cvContentCache =
      {}; // In-memory cache for CV content
  String? _lastHandledCV = null; // Track last CV we handled tab switch for

  // Preliminary Analysis state
  bool isPreliminaryAnalysisRunning = false;
  Map<String, dynamic>? preliminaryAnalysisResults;
  bool showPreliminaryAnalysis = false;
  static final Map<String, Map<String, dynamic>> preliminaryAnalysisCache =
      {}; // In-memory cache for Preliminary Analysis

  // AI Analysis state (automatically triggered after Preliminary Analysis)
  bool isAIAnalysisRunning = false;
  String aiAnalysisResult = '';
  bool showAIAnalysis = false;
  static final Map<String, String> aiAnalysisCache =
      {}; // In-memory cache for AI Analysis results

  @override
  void initState() {
    super.initState();
    _loadInitial();
    // Cached results are now handled by ModularAnalysisWidget

    // Add listener to JD controller to load cached keywords when text changes
    jdController.addListener(_onJDTextChanged);
  }

  void _onJDTextChanged() {
    final currentText = jdController.text.trim();
    debugPrint(
      '[CVPage] JD text changed: "${currentText.substring(0, currentText.length > 50 ? 50 : currentText.length)}..."',
    );
    if (currentText.isNotEmpty) {
      // Debounce the keyword loading to avoid too many calls
      Future.delayed(const Duration(milliseconds: 500), () {
        if (jdController.text.trim() == currentText) {
          _loadJDKeywordsFromPersistentCache(currentText);
        }
      });
    } else {
      // Clear JD skills when text is empty (but don't clear CV skills!)
      debugPrint(
        '[CVPage] Clearing JD skills due to empty text, but preserving CV skills',
      );
      setState(() {
        jdSkills = {};
        // Don't touch cvSkills here!
      });
    }
  }

  @override
  void dispose() {
    jdController.removeListener(_onJDTextChanged);
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Restore from cache if available
    if (SessionState.lastCVParsingResult != null) {
      cvSkills = SessionState.lastCVParsingResult!;
    }

    // Check if CV extraction is in progress and dialog is not open
    if (SessionState.isCVExtractionInProgress && !SessionState.isCVDialogOpen) {
      SessionState.isCVDialogOpen = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        showDialog(
          context: context,
          useRootNavigator: true,
          barrierDismissible: false,
          builder: (_) => CVAnalysisDialog(
            onCancel: () {
              SessionState.isCVExtractionInProgress = false;
              SessionState.isCVDialogOpen = false;
            },
          ),
        );
      });
    }

    // Check if we should navigate to CV Magic tab
    if (SessionState.shouldNavigateToCVMagic) {
      SessionState.shouldNavigateToCVMagic = false; // Reset the flag
      // Ensure the page is properly loaded
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!_initialLoaded) {
          _loadInitial();
        }
      });
    }
  }

  @override
  void didUpdateWidget(CvPage oldWidget) {
    super.didUpdateWidget(oldWidget);
    // This gets called when the widget is updated, including tab switches
    _handleTabSwitch();
  }

  void _handleTabSwitch() {
    // Restore CV content when tab becomes active
    if (selectedCVFilename != null && selectedCVFilename!.isNotEmpty) {
      // Only handle if this is a different CV or we haven't handled this CV yet
      if (_lastHandledCV != selectedCVFilename) {
        debugPrint(
          "🔄 [CVPage] Tab switch detected - attempting to restore CV content for: $selectedCVFilename",
        );

        // Check if we need to load CV content
        if (cvContent.isEmpty) {
          _loadCVContent(selectedCVFilename!);
        }

        _lastHandledCV = selectedCVFilename;
      }
    }

    // Restore Preliminary Analysis and AI Analysis results when tab becomes active
    if (selectedCVFilename != null && jdController.text.trim().isNotEmpty) {
      if (!showPreliminaryAnalysis || preliminaryAnalysisResults == null) {
        debugPrint(
          "🔄 [CVPage] Tab switch detected - attempting to restore Preliminary Analysis",
        );
        _loadPreliminaryAnalysisFromCache();
      }
    }
  }

  Future<void> _loadInitial() async {
    try {
      final cvs = await _apiService.fetchUploadedCVs();
      final prompt = await _apiService.fetchPrompt();

      if (!mounted) return;

      // Batch state updates - preserve existing skills if they exist
      setState(() {
        uploadedCVs = cvs;
        // Only update selectedCVFilename if it's not already set and we have a value from session
        if (selectedCVFilename == null &&
            SessionState.originalCVFilename != null) {
          selectedCVFilename = SessionState.originalCVFilename;
        }
        jdController.text = SessionState.jdText ?? '';
        jdUrlController.text = SessionState.jdUrl ?? '';
        currentPrompt = prompt; // Always use backend prompt
        matchResult = SessionState.matchResult ?? '';
        _initialLoaded = true;
        // Don't reset cvSkills or jdSkills if they already exist
      });

      debugPrint(
        '🔄 [CVPage] Loaded initial data: CV=${selectedCVFilename}, JD=${jdController.text.length} chars, URL=${jdUrlController.text}',
      );
      debugPrint(
        '🔄 [CVPage] SessionState.originalCVFilename: ${SessionState.originalCVFilename}',
      );
      debugPrint(
        '🔄 [CVPage] cvSkills after loadInitial: isEmpty=${cvSkills.isEmpty}, keys=${cvSkills.keys.toList()}',
      );

      // Removed skill extraction - using new approach

      // Remove automatic JD skills extraction on page load
      // Keywords should only be extracted when user clicks Extract Keywords button

      // Load cached keywords if available
      await _loadCachedKeywords();

      // Load CV content if CV is selected
      if (selectedCVFilename != null && selectedCVFilename!.isNotEmpty) {
        await _loadCVContent(selectedCVFilename!);
      }

      // Load Preliminary Analysis if both CV and JD are available
      if (selectedCVFilename != null && jdController.text.trim().isNotEmpty) {
        await _loadPreliminaryAnalysisFromCache();
      }
    } catch (_) {
      if (mounted) {
        NotificationService.showError("Failed to load initial data.");
      }
    }
  }

  Future<void> _loadCachedKeywords() async {
    debugPrint(
      '[CVPage] _loadCachedKeywords called with CV=$selectedCVFilename, JD=${jdController.text.length} chars',
    );

    // Load CV keywords if CV is selected (independent of JD)
    if (selectedCVFilename != null && selectedCVFilename!.isNotEmpty) {
      final cachedCVKeywords = await KeywordCacheService.getCVKeywords(
        selectedCVFilename!,
      );
      if (cachedCVKeywords != null) {
        debugPrint('[CVPage] Found cached CV keywords, updating state');
        setState(() {
          cvSkills = cachedCVKeywords;
        });
        // Also update in-memory cache
        cvSkillsCache[selectedCVFilename!] = cachedCVKeywords;
        debugPrint(
          '[CVPage] Loaded CV keywords from persistent cache for: $selectedCVFilename',
        );
      } else {
        debugPrint(
          '[CVPage] No cached CV keywords found for: $selectedCVFilename',
        );
      }
    }

    // Load JD keywords if JD text is available (independent of CV)
    final jdText = jdController.text.trim();
    if (jdText.isNotEmpty) {
      final cachedJDKeywords = await KeywordCacheService.getJDKeywords(jdText);
      if (cachedJDKeywords != null) {
        debugPrint('[CVPage] Found cached JD keywords, updating state');
        setState(() {
          jdSkills = cachedJDKeywords;
        });
        // Also update in-memory cache
        jdSkillsCache[jdText] = cachedJDKeywords;
        debugPrint('[CVPage] Loaded JD keywords from persistent cache');
      } else {
        debugPrint('[CVPage] No cached JD keywords found');
      }
    }

    // Removed ATS tab coupling
  }

  Future<void> _loadCVKeywordsFromPersistentCache(String cvFilename) async {
    final cachedKeywords = await KeywordCacheService.getCVKeywords(cvFilename);
    if (cachedKeywords != null) {
      debugPrint('[CVPage] Found cached CV keywords for: $cvFilename');
      debugPrint('[CVPage] CV Keywords: $cachedKeywords');
      setState(() {
        cvSkills = cachedKeywords;
      });
      // Also update in-memory cache
      cvSkillsCache[cvFilename] = cachedKeywords;
      debugPrint(
        '[CVPage] Updated UI with cached CV keywords for: $cvFilename',
      );
    } else {
      debugPrint('[CVPage] No cached CV keywords found for: $cvFilename');
    }
  }

  Future<void> _loadJDKeywordsFromPersistentCache(String jdText) async {
    final cachedKeywords = await KeywordCacheService.getJDKeywords(jdText);
    if (cachedKeywords != null) {
      debugPrint('[CVPage] Found cached JD keywords');
      debugPrint('[CVPage] JD Keywords: $cachedKeywords');
      setState(() {
        jdSkills = cachedKeywords;
      });
      // Also update in-memory cache
      jdSkillsCache[jdText] = cachedKeywords;
      debugPrint('[CVPage] Updated UI with cached JD keywords');
    } else {
      debugPrint('[CVPage] No cached JD keywords found');
    }
  }

  // REMOVED: Using dynamic extraction only - see _onExtractSkillsDynamic

  // REMOVED: Using dynamic extraction only - see _onExtractSkillsDynamic

  void _clearScreen() {
    setState(() {
      pickedFile = null;
      selectedCVFilename = null;
      jdController.clear();
      jdUrlController.clear();
      matchResult = '';
      uploadProgress = 0;

      cvSkills = {};
      jdSkills = {};
      showFullCVAnalysis = false;
      showFullJDAnalysis = false;
      // Clear AI Analysis state
      aiAnalysisResult = '';
      showAIAnalysis = false;
      isAIAnalysisRunning = false;
      // Clear Preliminary Analysis state
      preliminaryAnalysisResults = null;
      showPreliminaryAnalysis = false;
      isPreliminaryAnalysisRunning = false;
    });

    // Clear all cached data
    cvParsingCache.clear(); // Clear CV parsing cache
    cvSkillsCache.clear(); // Clear CV skills cache
    jdSkillsCache.clear(); // Clear JD skills cache
    preliminaryAnalysisCache.clear(); // Clear Preliminary Analysis cache
    aiAnalysisCache.clear(); // Clear AI Analysis cache

    SessionState.originalCVFilename = null;
    SessionState.jdText = null;
    SessionState.jdUrl = null; // Clear the job URL as well
    SessionState.currentPrompt = null;
    SessionState.matchResult = null;
    SessionState.lastCVParsingResult = null; // Clear CV parsing results

    NotificationService.showInfo("Screen cleared completely.");
  }

  Future<void> onFilePicked(PlatformFile file) async {
    final alreadyExists = uploadedCVs.contains(file.name);

    if (alreadyExists) {
      final shouldReplace = await showDialog<bool>(
        context: context,
        useRootNavigator: true,
        builder: (_) => AlertDialog(
          title: const Text("Duplicate CV"),
          content: Text(
            "A CV named '${file.name}' already exists.\nDo you want to replace it?",
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text("Cancel"),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text("Replace"),
            ),
          ],
        ),
      );

      if (shouldReplace != true) {
        NotificationService.showInfo("Upload cancelled.");
        return;
      }
    }

    setState(() {
      pickedFile = file;
      uploadProgress = 0;
    });

    for (int i = 0; i <= 100; i += 5) {
      await Future.delayed(const Duration(milliseconds: 20));
      if (!mounted) return;
      setState(() {
        uploadProgress = i / 100;
      });
    }

    await _apiService.uploadCv(file);
    final updatedCvs = await _apiService.fetchUploadedCVs();

    if (!mounted) return;
    setState(() {
      uploadedCVs = updatedCvs;
      selectedCVFilename = file.name;
      SessionState.originalCVFilename = file.name;
      uploadProgress = 0;
    });

    // Print CV to backend console when uploaded
    await _printCVToBackend(file.name);

    NotificationService.showInfo("CV Uploaded Successfully!");
    // Removed skill extraction - using new approach
  }

  Future<void> _printCVToBackend(String cvFilename) async {
    try {
      final response = await http.post(
        Uri.parse('${api.ApiService.baseUrl}/print-cv-original/'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {'cv_filename': cvFilename},
      );

      if (response.statusCode == 200) {
        debugPrint('✅ CV printed to backend console: $cvFilename');
      } else {
        debugPrint('⚠️ Failed to print CV to backend: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ Error printing CV to backend: $e');
    }
  }

  Future<void> _loadCVContent(String cvFilename) async {
    try {
      setState(() {
        isLoadingCVContent = true;
      });

      // Check in-memory cache first
      if (cvContentCache.containsKey(cvFilename)) {
        setState(() {
          cvContent = cvContentCache[cvFilename]!;
          isLoadingCVContent = false;
        });
        debugPrint('✅ CV content loaded from memory cache: $cvFilename');
        return;
      }

      // Check persistent cache
      final cachedContent = await KeywordCacheService.getCVContent(cvFilename);
      if (cachedContent != null) {
        setState(() {
          cvContent = cachedContent;
          isLoadingCVContent = false;
        });
        // Also update in-memory cache
        cvContentCache[cvFilename] = cachedContent;
        debugPrint('✅ CV content loaded from persistent cache: $cvFilename');
        return;
      }

      // If not cached, fetch from backend
      final response = await http.get(
        Uri.parse('${api.ApiService.baseUrl}/get-cv-content/$cvFilename'),
      );

      if (response.statusCode == 200) {
        final content = response.body;
        setState(() {
          cvContent = content;
          isLoadingCVContent = false;
        });

        // Save to both caches
        cvContentCache[cvFilename] = content;
        await KeywordCacheService.saveCVContent(
          cvFilename: cvFilename,
          content: content,
        );

        debugPrint('✅ CV content loaded from backend and cached: $cvFilename');
      } else {
        setState(() {
          cvContent = 'Failed to load CV content';
          isLoadingCVContent = false;
        });
        debugPrint('⚠️ Failed to load CV content: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        cvContent = 'Error loading CV content: $e';
        isLoadingCVContent = false;
      });
      debugPrint('❌ Error loading CV content: $e');
    }
  }

  String _formatCVContent(String content) {
    if (content.isEmpty) return content;

    // Split content into lines
    List<String> lines = content.split('\n');
    List<String> formattedLines = [];

    for (int i = 0; i < lines.length; i++) {
      String line = lines[i].trim();

      // Skip empty lines
      if (line.isEmpty) {
        formattedLines.add('');
        continue;
      }

      // Format section headers (all caps words)
      if (line == line.toUpperCase() &&
          line.length > 3 &&
          !line.contains('•')) {
        formattedLines.add('');
        formattedLines.add('┌─ ' + line + ' ─' + '─' * (70 - line.length));
        formattedLines.add('');
        continue;
      }

      // Format bullet points
      if (line.startsWith('•')) {
        formattedLines.add('  ' + line);
        continue;
      }

      // Format job titles (lines ending with date ranges)
      if (line.contains(' – ') ||
          line.contains(' - ') ||
          (line.contains('Present') ||
              line.contains('2024') ||
              line.contains('2023') ||
              line.contains('2022') ||
              line.contains('2021') ||
              line.contains('2020'))) {
        formattedLines.add('');
        formattedLines.add('📅 ' + line);
        formattedLines.add('');
        continue;
      }

      // Format company names (lines that might be company names)
      if (line.contains(',') &&
          (line.contains('Australia') ||
              line.contains('France') ||
              line.contains('Sydney') ||
              line.contains('Victoria') ||
              line.contains('Cergy'))) {
        formattedLines.add('🏢 ' + line);
        formattedLines.add('');
        continue;
      }

      // Format education entries
      if (line.contains('University') ||
          line.contains('Master') ||
          line.contains('PhD')) {
        formattedLines.add('');
        formattedLines.add('🎓 ' + line);
        continue;
      }

      // Format contact information
      if (line.contains('@') ||
          line.contains('|') ||
          line.contains('LinkedIn') ||
          line.contains('GitHub') ||
          line.contains('Portfolio')) {
        formattedLines.add('📧 ' + line);
        continue;
      }

      // Regular content
      formattedLines.add(line);
    }

    return formattedLines.join('\n');
  }

  void _onCVSelected(String? v) async {
    final isDifferentCV = selectedCVFilename != v;
    setState(() {
      selectedCVFilename = v;
      SessionState.originalCVFilename = v;
      if (isDifferentCV) {
        cvSkills = {};
        showFullCVAnalysis = false;
        // Clear CV parsing cache for the previous CV
        if (SessionState.lastCVParsingResult != null) {
          SessionState.lastCVParsingResult = null;
        }
        if (v != null) {
          cvParsingCache.remove(v);
        }
        // Reset the tab switch handling flag for new CV
        _lastHandledCV = null;
      }
    });

    // Print CV to backend console and load content for UI display when selected
    if (v != null) {
      await _printCVToBackend(v);
      await _loadCVContent(v);
    }

    if (v != null && cvSkillsCache.containsKey(v)) {
      debugPrint(
        '[CVPage] _onCVSelected: Restoring cvSkills from cache for $v',
      );
      setState(() {
        cvSkills = cvSkillsCache[v]!;
        showFullCVAnalysis = false;
      });
    } else if (v != null) {
      // Check persistent cache if not in memory cache
      _loadCVKeywordsFromPersistentCache(v);
    }

    // Also reload JD keywords if JD text is available
    if (jdController.text.isNotEmpty) {
      _loadJDKeywordsFromPersistentCache(jdController.text.trim());
    }
  }

  // Load Preliminary Analysis from cache
  Future<void> _loadPreliminaryAnalysisFromCache() async {
    if (selectedCVFilename == null || jdController.text.trim().isEmpty) {
      return;
    }

    final cacheKey = '${selectedCVFilename}_${jdController.text.trim()}';

    // Check in-memory cache first
    if (preliminaryAnalysisCache.containsKey(cacheKey)) {
      setState(() {
        preliminaryAnalysisResults = preliminaryAnalysisCache[cacheKey];
        showPreliminaryAnalysis = true;
      });
      debugPrint('✅ [CVPage] Preliminary Analysis loaded from memory cache');
    } else {
      // Check persistent cache
      final cachedResults = await KeywordCacheService.getPreliminaryAnalysis(
        selectedCVFilename!,
        jdController.text.trim(),
      );

      if (cachedResults != null) {
        setState(() {
          preliminaryAnalysisResults = cachedResults;
          showPreliminaryAnalysis = true;
        });
        // Also update in-memory cache
        preliminaryAnalysisCache[cacheKey] = cachedResults;
        debugPrint(
          '✅ [CVPage] Preliminary Analysis loaded from persistent cache',
        );
      } else {
        debugPrint('📂 [CVPage] No cached Preliminary Analysis found');
      }
    }

    // Also load AI Analysis from cache if Preliminary Analysis exists
    await _loadAIAnalysisFromCache();
  }

  // Load AI Analysis from cache
  Future<void> _loadAIAnalysisFromCache() async {
    if (selectedCVFilename == null || jdController.text.trim().isEmpty) {
      return;
    }

    final cacheKey = '${selectedCVFilename}_${jdController.text.trim()}';

    // Check in-memory cache first
    if (aiAnalysisCache.containsKey(cacheKey)) {
      setState(() {
        aiAnalysisResult = aiAnalysisCache[cacheKey]!;
        showAIAnalysis = true;
      });
      debugPrint('✅ [CVPage] AI Analysis loaded from memory cache');
      return;
    }

    // Check persistent cache
    final cachedResult = await KeywordCacheService.getAIAnalysis(
      selectedCVFilename!,
      jdController.text.trim(),
    );

    if (cachedResult != null) {
      setState(() {
        aiAnalysisResult = cachedResult;
        showAIAnalysis = true;
      });
      // Also update in-memory cache
      aiAnalysisCache[cacheKey] = cachedResult;
      debugPrint('✅ [CVPage] AI Analysis loaded from persistent cache');
    } else {
      debugPrint('📂 [CVPage] No cached AI Analysis found');
    }
  }

  Widget _buildCVContentSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.description, color: AppTheme.primaryCosmic, size: 24),
            const SizedBox(width: 12),
            Text(
              '📄 CV Content Preview',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: AppTheme.primaryCosmic,
              ),
            ),
            const Spacer(),
            // Debug info
            if (selectedCVFilename != null) ...[
              Text(
                'Cache: ${cvContentCache.containsKey(selectedCVFilename) ? "✅" : "❌"}',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
              const SizedBox(width: 8),
            ],
            if (isLoadingCVContent)
              SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    AppTheme.primaryCosmic,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 16),
        if (isLoadingCVContent)
          Center(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(
                      AppTheme.primaryCosmic,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Loading CV content...',
                    style: TextStyle(color: Colors.grey[600], fontSize: 14),
                  ),
                ],
              ),
            ),
          )
        else if (cvContent.isNotEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey[300]!),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.file_copy,
                      color: AppTheme.primaryCosmic,
                      size: 16,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Selected CV: $selectedCVFilename',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        color: AppTheme.primaryCosmic,
                        fontSize: 14,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      '${cvContent.length} characters',
                      style: TextStyle(color: Colors.grey[600], fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey[900],
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.grey[700]!),
                  ),
                  child: SelectableText(
                    _formatCVContent(cvContent),
                    style: TextStyle(
                      fontSize: 13,
                      height: 1.6,
                      fontFamily: 'monospace',
                      color: Colors.grey[100],
                    ),
                  ),
                ),
              ],
            ),
          )
        else
          Center(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text(
                    'No CV content available',
                    style: TextStyle(
                      color: Colors.grey[500],
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Debug: CV=${selectedCVFilename ?? "null"}, Content=${cvContent.length} chars, Cache=${cvContentCache.length} items',
                    style: TextStyle(fontSize: 10, color: Colors.grey[400]),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildCVSkillsSection() {
    if (isExtractingSkills) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 16),
        child: Center(child: CircularProgressIndicator()),
      );
    }
    // Always show the section if any skills list is non-empty or if comprehensive_analysis is present
    final softSkills = (cvSkills['soft_skills'] ?? []) as List;
    final techSkills = (cvSkills['technical_skills'] ?? []) as List;
    final domainKeywords = (cvSkills['domain_keywords'] ?? []) as List;
    debugPrint(
      '[CVPage] _buildCVSkillsSection: softSkills=$softSkills, techSkills=$techSkills, domainKeywords=$domainKeywords',
    );

    final hasAnalysis = cvSkills['comprehensive_analysis'] != null &&
        cvSkills['comprehensive_analysis'].toString().trim().isNotEmpty;
    final categoryColors = {
      'soft_skills': Colors.purple.shade100,
      'technical_skills': Colors.blue.shade100,
      'domain_keywords': Colors.orange.shade100,
    };
    final categoryLabels = {
      'soft_skills': 'Soft Skills',
      'technical_skills': 'Technical Skills',
      'domain_keywords': 'Domain Keywords',
    };
    List<Widget> sections = [];
    for (final key in ['soft_skills', 'technical_skills', 'domain_keywords']) {
      var value = (cvSkills[key] ?? []) as List;
      // Filter out empty, whitespace, and 'N/A' values
      value = value
          .where(
            (e) =>
                e != null &&
                e.toString().trim().isNotEmpty &&
                e.toString().trim().toLowerCase() != 'n/a',
          )
          .toList();
      if (value.isNotEmpty) {
        sections.add(
          Padding(
            padding: const EdgeInsets.only(top: 12, bottom: 4),
            child: Text(
              categoryLabels[key] ?? key,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: context.isMobile ? 14 : 16,
              ),
            ),
          ),
        );
        sections.add(
          Wrap(
            spacing: context.isMobile ? 6 : 8,
            runSpacing: context.isMobile ? 6 : 8,
            children: value
                .map<Widget>(
                  (e) => Chip(
                    label: Text(
                      e.toString(),
                      style: TextStyle(fontSize: context.isMobile ? 12 : 14),
                    ),
                    backgroundColor:
                        categoryColors[key] ?? Colors.grey.shade200,
                    padding: EdgeInsets.symmetric(
                      horizontal: context.isMobile ? 6 : 8,
                      vertical: context.isMobile ? 2 : 4,
                    ),
                  ),
                )
                .toList(),
          ),
        );
      }
    }
    // Expandable Markdown display for comprehensive_analysis
    Widget? expandableMarkdownWidget;
    if (hasAnalysis) {
      expandableMarkdownWidget = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 12),
          ElevatedButton.icon(
            onPressed: () =>
                setState(() => showFullCVAnalysis = !showFullCVAnalysis),
            icon: Icon(
              showFullCVAnalysis ? Icons.expand_less : Icons.expand_more,
            ),
            label: Text(
              showFullCVAnalysis
                  ? 'Hide Full Claude Analysis'
                  : 'Show Full Claude AI Analysis',
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.deepPurple.shade100,
              foregroundColor: Colors.deepPurple.shade900,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          if (showFullCVAnalysis)
            Padding(
              padding: const EdgeInsets.only(top: 16.0),
              child: Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: MarkdownBody(
                    data: cvSkills['comprehensive_analysis'],
                    styleSheet: MarkdownStyleSheet(
                      h2: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
                      p: TextStyle(fontSize: 16),
                      listBullet: TextStyle(fontSize: 16),
                    ),
                  ),
                ),
              ),
            ),
        ],
      );
    }
    // If all lists are empty, show a message
    if (sections.isEmpty && !hasAnalysis) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Text(
          'No skills found.',
          style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
        ),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            children: [
              Icon(Icons.auto_awesome, color: Colors.purple, size: 20),
              const SizedBox(width: 8),
              Text(
                '🤖 Claude AI - Extracted Skills & Keywords from CV:',
                style: TextStyle(
                  fontSize: context.isMobile ? 16 : 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        ...sections,
        if (expandableMarkdownWidget != null) expandableMarkdownWidget,
        const Divider(height: 32),
      ],
    );
  }

  Widget _buildJDSkillsSection() {
    if (isExtractingJDSkills) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 16),
        child: Center(child: CircularProgressIndicator()),
      );
    }
    if (jdSkills.isEmpty) {
      return const SizedBox();
    }
    final categoryColors = {
      'soft_skills': Colors.purple.shade100,
      'technical_skills': Colors.blue.shade100,
      'domain_keywords': Colors.orange.shade100,
    };
    final categoryLabels = {
      'soft_skills': 'Required Soft Skills',
      'technical_skills': 'Required Technical Skills',
      'domain_keywords': 'Required Domain Keywords',
    };
    List<Widget> sections = [];
    for (final key in ['soft_skills', 'technical_skills', 'domain_keywords']) {
      var value = (jdSkills[key] ?? []) as List;
      // Filter out empty, whitespace, and 'N/A' values
      value = value
          .where(
            (e) =>
                e != null &&
                e.toString().trim().isNotEmpty &&
                e.toString().trim().toLowerCase() != 'n/a',
          )
          .toList();
      if (value.isNotEmpty) {
        sections.add(
          Padding(
            padding: const EdgeInsets.only(top: 12, bottom: 4),
            child: Text(
              categoryLabels[key] ?? key,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: context.isMobile ? 14 : 16,
              ),
            ),
          ),
        );
        sections.add(
          Wrap(
            spacing: context.isMobile ? 6 : 8,
            runSpacing: context.isMobile ? 6 : 8,
            children: value
                .map<Widget>(
                  (e) => Chip(
                    label: Text(
                      e.toString(),
                      style: TextStyle(fontSize: context.isMobile ? 12 : 14),
                    ),
                    backgroundColor:
                        categoryColors[key] ?? Colors.grey.shade200,
                    padding: EdgeInsets.symmetric(
                      horizontal: context.isMobile ? 6 : 8,
                      vertical: context.isMobile ? 2 : 4,
                    ),
                  ),
                )
                .toList(),
          ),
        );
      }
    }
    // Expandable Markdown display for comprehensive_analysis
    Widget? expandableMarkdownWidget;
    if (jdSkills['comprehensive_analysis'] != null &&
        jdSkills['comprehensive_analysis'].toString().trim().isNotEmpty) {
      expandableMarkdownWidget = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 12),
          ElevatedButton.icon(
            onPressed: () =>
                setState(() => showFullJDAnalysis = !showFullJDAnalysis),
            icon: Icon(
              showFullJDAnalysis ? Icons.expand_less : Icons.expand_more,
            ),
            label: Text(
              showFullJDAnalysis
                  ? 'Hide Full Claude Analysis'
                  : 'Show Full Claude AI Analysis',
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.deepPurple.shade100,
              foregroundColor: Colors.deepPurple.shade900,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          if (showFullJDAnalysis)
            Padding(
              padding: const EdgeInsets.only(top: 16.0),
              child: Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: MarkdownBody(
                    data: jdSkills['comprehensive_analysis'],
                    styleSheet: MarkdownStyleSheet(
                      h2: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
                      p: TextStyle(fontSize: 16),
                      listBullet: TextStyle(fontSize: 16),
                    ),
                  ),
                ),
              ),
            ),
        ],
      );
    }
    // If all lists are empty, show a message
    if (sections.isEmpty &&
        (jdSkills['comprehensive_analysis'] == null ||
            jdSkills['comprehensive_analysis'].toString().trim().isEmpty)) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 16),
        child: Text(
          'No skills found.',
          style: TextStyle(color: Colors.grey, fontStyle: FontStyle.italic),
        ),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 8),
          child: Row(
            children: [
              Icon(Icons.auto_awesome, color: Colors.purple, size: 20),
              const SizedBox(width: 8),
              Text(
                '🤖 Claude AI - Extracted Skills & Keywords from JD:',
                style: TextStyle(
                  fontSize: context.isMobile ? 16 : 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
        ...sections,
        if (expandableMarkdownWidget != null) expandableMarkdownWidget,
        const Divider(height: 32),
      ],
    );
  }

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context);

    // Handle tab switching on every build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _handleTabSwitch();
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('CV Magic'),
        backgroundColor: AppTheme.primaryCosmic,
        foregroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false,
      ),
      body: Container(
        decoration: const BoxDecoration(gradient: AppTheme.backgroundGradient),
        child: AbsorbPointer(
          absorbing: isSaving,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Builder(
              builder: (context) {
                debugPrint(
                  '🔍 [CVPage] Build state - _initialLoaded: $_initialLoaded',
                );
                return _initialLoaded
                    ? Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          SectionCard(
                            child: CvUploader(onFilePicked: onFilePicked),
                          ),
                          const SizedBox(height: 24),
                          SectionCard(
                            child: CvSelector(
                              files: uploadedCVs,
                              selected: selectedCVFilename,
                              onChanged: _onCVSelected,
                              onRefresh: () async {
                                final cvs =
                                    await _apiService.fetchUploadedCVs();
                                if (mounted) setState(() => uploadedCVs = cvs);
                              },
                            ),
                          ),
                          const SizedBox(height: 24),
                          // Show CV content when CV is selected
                          if (selectedCVFilename != null &&
                              selectedCVFilename!.isNotEmpty) ...[
                            SectionCard(child: _buildCVContentSection()),
                            const SizedBox(height: 24),
                          ],

                          // Show CV skills section when CV is selected and skills are extracted
                          if (selectedCVFilename != null &&
                              selectedCVFilename!.isNotEmpty &&
                              (cvSkills.isNotEmpty || isExtractingSkills)) ...[
                            const SizedBox(height: 24),
                            SectionCard(child: _buildCVSkillsSection()),
                          ],
                          SectionCard(
                            child: JobInput(
                              jdController: jdController,
                              jdUrlController: jdUrlController,
                              onExtract: () async {
                                try {
                                  debugPrint(
                                    '[JD EXTRACT] Extracting JD from URL: ' +
                                        jdUrlController.text,
                                  );
                                  final text =
                                      await _apiService.fetchJobDescription(
                                    jdUrlController.text,
                                  );
                                  debugPrint(
                                    '[JD EXTRACT] Extracted text length: ' +
                                        text.length.toString(),
                                  );
                                  if (mounted)
                                    setState(() => jdController.text = text);
                                  SessionState.jdText = jdController.text;
                                  SessionState.jdUrl = jdUrlController.text;
                                  if (text.isEmpty) {
                                    NotificationService.showError(
                                      'No job description found at the provided link.',
                                    );
                                  }
                                } catch (e) {
                                  debugPrint(
                                    '[JD EXTRACT] Error extracting JD: $e',
                                  );
                                  if (mounted) {
                                    NotificationService.showError(
                                      'Failed to extract JD from link: $e',
                                    );
                                  }
                                }
                              },
                            ),
                          ),
                          // Show JD skills section when keywords are extracted
                          if (jdSkills.isNotEmpty || isExtractingJDSkills) ...[
                            const SizedBox(height: 24),
                            SectionCard(child: _buildJDSkillsSection()),
                          ],
                          // Progressive Analysis Workflow
                          const SizedBox(height: 24),
                          SectionCard(
                            child: ModularAnalysisWidget(
                              cvFilename: selectedCVFilename ?? '',
                              jdText: jdController.text.trim(),
                              currentPrompt: currentPrompt,
                            ),
                          ),
                          const SizedBox(height: 24),
                          _buildAnalyzeAndActions(),
                          // Add bottom padding for mobile nav clearance
                          SizedBox(height: context.isMobile ? 100 : 24),
                        ],
                      )
                    : _buildLoadingFallback();
              },
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildAnalyzeButton() {
    // This button is now handled by ModularAnalysisWidget placed in the main layout
    return const SizedBox.shrink();
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        // Go to ATS Test button - only after AI analysis is complete
        if (showAIAnalysis && aiAnalysisResult.isNotEmpty) ...[
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                // Set the flag to reset ATS tab when navigating via "Go to ATS Test"
                SessionState.newAnalysisStarted = true;
                homePageKey.currentState?.switchToTab(
                  4,
                ); // Switch to ATS tab (index 4)
              },
              icon: Icon(Icons.analytics, size: context.isMobile ? 18 : 20),
              label: Text(
                "Go to ATS Test",
                style: TextStyle(
                  fontSize: context.isMobile ? 14 : 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryCosmic,
                foregroundColor: Colors.white,
                padding: EdgeInsets.symmetric(
                  vertical: context.isMobile ? 12 : 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
          SizedBox(height: context.isMobile ? 8 : 12),
        ],
        // Clear Screen button
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _clearScreen,
            icon: Icon(Icons.clear, size: context.isMobile ? 18 : 20),
            label: Text(
              "Clear Screen",
              style: TextStyle(
                fontSize: context.isMobile ? 14 : 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.redAccent,
              foregroundColor: Colors.white,
              padding: EdgeInsets.symmetric(
                vertical: context.isMobile ? 12 : 16,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCombinedKeywordsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Row(
            children: [
              Icon(Icons.compare_arrows, color: Colors.indigo, size: 20),
              const SizedBox(width: 8),
              Text(
                '🔍 Keywords Comparison - CV vs Job Description',
                style: TextStyle(
                  fontSize: context.isMobile ? 16 : 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.indigo.shade700,
                ),
              ),
            ],
          ),
        ),
        Row(
          children: [
            Expanded(
              child: _buildKeywordColumn('CV Keywords', cvSkills, Colors.blue),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildKeywordColumn('JD Keywords', jdSkills, Colors.green),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildKeywordColumn(
    String title,
    Map<String, dynamic> skills,
    MaterialColor baseColor,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: context.isMobile ? 14 : 16,
            color: baseColor.shade700,
          ),
        ),
        const SizedBox(height: 12),
        _buildKeywordChips(
          'Technical Skills',
          skills['technical_skills'] ?? [],
          baseColor.shade100,
        ),
        const SizedBox(height: 8),
        _buildKeywordChips(
          'Soft Skills',
          skills['soft_skills'] ?? [],
          baseColor.shade200,
        ),
        const SizedBox(height: 8),
        _buildKeywordChips(
          'Domain Keywords',
          skills['domain_keywords'] ?? [],
          baseColor.shade300,
        ),
      ],
    );
  }

  Widget _buildKeywordChips(
    String category,
    List<dynamic> keywords,
    Color backgroundColor,
  ) {
    final keywordList = keywords
        .where((k) => k != null && k.toString().trim().isNotEmpty)
        .toList();

    if (keywordList.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$category:',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            'None found',
            style: TextStyle(fontSize: 11, color: Colors.grey),
          ),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$category (${keywordList.length}):',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        Wrap(
          spacing: 4,
          runSpacing: 4,
          children: keywordList
              .take(6)
              .map(
                (keyword) => Chip(
                  label: Text(
                    keyword.toString(),
                    style: const TextStyle(fontSize: 10),
                  ),
                  backgroundColor: backgroundColor,
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  visualDensity: VisualDensity.compact,
                ),
              )
              .toList(),
        ),
        if (keywordList.length > 6)
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Text(
              '... and ${keywordList.length - 6} more',
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
            ),
          ),
      ],
    );
  }

  Widget _buildAnalyzeAndActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildAnalyzeButton(),
        const SizedBox(height: 24),
        _buildActionButtons(),
      ],
    );
  }

  Widget _buildLoadingFallback() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SectionCard(
          child: CvUploader(
            onFilePicked: (file) async {
              await onFilePicked(file);
              // After successful upload, reload initial data
              await _loadInitial();
            },
          ),
        ),
        const SizedBox(height: 24),
        SectionCard(
          child: CvSelector(
            files: uploadedCVs,
            selected: selectedCVFilename,
            onChanged: _onCVSelected,
            onRefresh: () async {
              final cvs = await _apiService.fetchUploadedCVs();
              if (mounted) setState(() => uploadedCVs = cvs);
            },
          ),
        ),
        const SizedBox(height: 24),

        // Show CV skills section when CV is selected and skills are extracted
        if ((selectedCVFilename != null &&
                selectedCVFilename!.isNotEmpty &&
                (cvSkills.isNotEmpty || isExtractingSkills)) ||
            ((cvSkills['technical_skills']?.isNotEmpty ?? false) ||
                (cvSkills['soft_skills']?.isNotEmpty ?? false) ||
                (cvSkills['domain_keywords']?.isNotEmpty ?? false))) ...[
          const SizedBox(height: 24),
          SectionCard(child: _buildCVSkillsSection()),
        ] else ...[
          // Debug: Log why CV skills section is not showing
          Builder(
            builder: (context) {
              debugPrint(
                '[CVPage] CV skills section not showing: CV=${selectedCVFilename}, cvSkills.isEmpty=${cvSkills.isEmpty}, isExtracting=$isExtractingSkills',
              );
              debugPrint('[CVPage] cvSkills keys: ${cvSkills.keys.toList()}');
              debugPrint('[CVPage] cvSkills length: ${cvSkills.length}');
              final hasSkills =
                  (cvSkills['technical_skills']?.isNotEmpty ?? false) ||
                      (cvSkills['soft_skills']?.isNotEmpty ?? false) ||
                      (cvSkills['domain_keywords']?.isNotEmpty ?? false);
              debugPrint('[CVPage] Has actual skills: $hasSkills');
              return const SizedBox.shrink();
            },
          ),
        ],
        SectionCard(
          child: JobInput(
            jdController: jdController,
            jdUrlController: jdUrlController,
            onExtract: () async {
              try {
                debugPrint(
                  '[JD EXTRACT] Extracting JD from URL: ' +
                      jdUrlController.text,
                );
                final text = await _apiService.fetchJobDescription(
                  jdUrlController.text,
                );
                debugPrint(
                  '[JD EXTRACT] Extracted text length: ' +
                      text.length.toString(),
                );
                if (mounted) setState(() => jdController.text = text);
                SessionState.jdText = jdController.text;
                SessionState.jdUrl = jdUrlController.text;
                if (text.isEmpty) {
                  NotificationService.showError(
                    'No job description found at the provided link.',
                  );
                }
              } catch (e) {
                debugPrint('[JD EXTRACT] Error extracting JD: $e');
                if (mounted) {
                  NotificationService.showError(
                    'Failed to extract JD from link: $e',
                  );
                }
              }
            },
          ),
        ),
        // Show JD skills section when keywords are extracted
        if ((jdSkills.isNotEmpty || isExtractingJDSkills) ||
            ((jdSkills['technical_skills']?.isNotEmpty ?? false) ||
                (jdSkills['soft_skills']?.isNotEmpty ?? false) ||
                (jdSkills['domain_keywords']?.isNotEmpty ?? false))) ...[
          const SizedBox(height: 24),
          SectionCard(child: _buildJDSkillsSection()),
        ] else ...[
          // Debug: Log why JD skills section is not showing
          Builder(
            builder: (context) {
              debugPrint(
                '[CVPage] JD skills section not showing: jdSkills.isEmpty=${jdSkills.isEmpty}, isExtracting=$isExtractingJDSkills',
              );
              return const SizedBox.shrink();
            },
          ),
        ],
        // Progressive Analysis Workflow
        const SizedBox(height: 24),
        SectionCard(
          child: ModularAnalysisWidget(
            cvFilename: selectedCVFilename ?? '',
            jdText: jdController.text.trim(),
            currentPrompt: currentPrompt,
          ),
        ),
        // Show combined keywords section when both CV and JD keywords are available
        if ((cvSkills.isNotEmpty && jdSkills.isNotEmpty) ||
            (((cvSkills['technical_skills']?.isNotEmpty ?? false) ||
                    (cvSkills['soft_skills']?.isNotEmpty ?? false) ||
                    (cvSkills['domain_keywords']?.isNotEmpty ?? false)) &&
                ((jdSkills['technical_skills']?.isNotEmpty ?? false) ||
                    (jdSkills['soft_skills']?.isNotEmpty ?? false) ||
                    (jdSkills['domain_keywords']?.isNotEmpty ?? false)))) ...[
          const SizedBox(height: 24),
          SectionCard(child: _buildCombinedKeywordsSection()),
        ] else ...[
          // Debug: Log why combined section is not showing
          Builder(
            builder: (context) {
              debugPrint(
                '[CVPage] Combined keywords section not showing: cvSkills.isEmpty=${cvSkills.isEmpty}, jdSkills.isEmpty=${jdSkills.isEmpty}',
              );
              return const SizedBox.shrink();
            },
          ),
        ],
      ],
    );
  }

  Widget _buildSkillsColumn(
    String title,
    Map<String, dynamic> skills,
    MaterialColor baseColor,
    String type,
  ) {
    final technicalSkills = List<String>.from(skills['technical_skills'] ?? []);
    final softSkills = List<String>.from(skills['soft_skills'] ?? []);
    final domainKeywords = List<String>.from(skills['domain_keywords'] ?? []);
    final comprehensiveAnalysis = skills['comprehensive_analysis'] ?? '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: baseColor.shade50,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: baseColor.shade200),
          ),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: baseColor.shade700,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 16),

        // Technical Skills
        if (technicalSkills.isNotEmpty) ...[
          _buildSkillSection(
            '🔧 Technical Skills',
            technicalSkills,
            baseColor.shade100,
          ),
          const SizedBox(height: 12),
        ],

        // Soft Skills
        if (softSkills.isNotEmpty) ...[
          _buildSkillSection('🤝 Soft Skills', softSkills, baseColor.shade200),
          const SizedBox(height: 12),
        ],

        // Domain Keywords
        if (domainKeywords.isNotEmpty) ...[
          _buildSkillSection(
            '📚 Domain Keywords',
            domainKeywords,
            baseColor.shade300,
          ),
          const SizedBox(height: 12),
        ],

        // Expandable Comprehensive Analysis
        if (comprehensiveAnalysis.isNotEmpty) ...[
          _buildExpandableAnalysis(comprehensiveAnalysis, baseColor, type),
        ],
      ],
    );
  }

  Widget _buildSkillSection(
    String title,
    List<String> skills,
    Color backgroundColor,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade300),
          ),
          child: Wrap(
            spacing: 6,
            runSpacing: 6,
            children: skills
                .map(
                  (skill) => Chip(
                    label: Text(skill, style: const TextStyle(fontSize: 12)),
                    backgroundColor: Colors.white,
                    side: BorderSide(color: Colors.grey.shade400),
                  ),
                )
                .toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildExpandableAnalysis(
    String analysis,
    MaterialColor baseColor,
    String type,
  ) {
    bool isExpanded = false;

    return StatefulBuilder(
      builder: (context, setState) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  setState(() {
                    isExpanded = !isExpanded;
                  });
                },
                icon: Icon(
                  isExpanded ? Icons.expand_less : Icons.expand_more,
                  size: 16,
                ),
                label: Text(
                  isExpanded
                      ? 'Hide Full Claude AI Analysis'
                      : 'Show Full Claude AI Analysis',
                  style: const TextStyle(fontSize: 12),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: baseColor.shade100,
                  foregroundColor: baseColor.shade900,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
            if (isExpanded) ...[
              const SizedBox(height: 12),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                child: SelectableText(
                  analysis,
                  style: const TextStyle(
                    fontSize: 12,
                    height: 1.4,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ],
          ],
        );
      },
    );
  }
}
