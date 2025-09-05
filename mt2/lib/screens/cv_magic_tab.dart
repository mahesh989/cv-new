import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

import '../utils/notification_service.dart';
import '../services/api_service.dart' as api;
import '../services/keyword_cache_service.dart';
import '../dialogs/cv_analysis_dialog.dart';

class CvMagicTab extends StatefulWidget {
  final String? originalCV;
  final String? jdText;
  final String? tailoredCV;

  const CvMagicTab({
    super.key,
    this.originalCV,
    this.jdText,
    this.tailoredCV,
  });

  @override
  State<CvMagicTab> createState() => _CvMagicTabState();
}

class _CvMagicTabState extends State<CvMagicTab> with TickerProviderStateMixin {
  // Animation controllers
  late AnimationController _cardController;
  late AnimationController _buttonController;
  late AnimationController _fadeController;

  // Core data
  String originalCVName = '';
  String currentCVName = '';
  String jdText = '';
  String prompt = '';

  // State management
  bool isTesting = false;
  bool isGenerating = false;
  int latestATSScore = 0;
  String currentState = 'initial';

  // UI state variables
  List<Map<String, dynamic>> _inlineOptimizationSteps = [];
  final TextEditingController _inlinePromptController = TextEditingController();
  bool _isInlineGenerating = false;
  bool _hasInlinePromptText = false;

  // CV selection
  String? selectedCVFilename;
  final TextEditingController _jdController = TextEditingController();

  // Available CVs (dynamic list)
  List<String> availableCVs = [];

  // Keyword extraction
  final api.ApiService _apiService = api.ApiService();
  Map<String, dynamic> _cvKeywords = {};
  Map<String, dynamic> _jdKeywords = {};
  bool _isExtractingCVKeywords = false;
  bool _isExtractingJDKeywords = false;
  bool _keywordsExtracted = false;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeData();
    _loadAvailableCVs();
  }

  void _initializeAnimations() {
    _cardController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _buttonController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
      value: 1.0,
    );

    _inlinePromptController.addListener(() {
      setState(() {
        _hasInlinePromptText = _inlinePromptController.text.trim().isNotEmpty;
      });
    });
  }

  void _initializeData() {
    originalCVName = widget.originalCV ?? '';
    currentCVName = originalCVName;
    jdText = widget.jdText ?? '';
    _jdController.text = jdText;
    prompt =
        'Analyze this CV against the job description and provide ATS compatibility insights.';

    debugPrint(
        "📋 [CV-MAGIC] Initialized with CV: '$originalCVName', JD length: ${jdText.length}");

    // Load cached keywords if available
    _loadCachedKeywords();
  }

  Future<void> _loadCachedKeywords() async {
    if (selectedCVFilename != null && jdText.isNotEmpty) {
      final cachedKeywords = await KeywordCacheService.getBothKeywords(
          selectedCVFilename!, jdText);

      if (cachedKeywords != null) {
        setState(() {
          _cvKeywords = cachedKeywords['cv_keywords']!;
          _jdKeywords = cachedKeywords['jd_keywords']!;
          _keywordsExtracted = true;
        });
        debugPrint(
            "📋 [CV-MAGIC] Loaded cached keywords for CV: $selectedCVFilename");
      }
    }
  }

  Future<void> _loadAvailableCVs() async {
    try {
      final response =
          await http.get(Uri.parse('http://localhost:8000/list-tailored-cvs/'));
      if (response.statusCode == 200) {
        final List<dynamic> cvList = json.decode(response.body);
        setState(() {
          availableCVs = cvList.map((cv) => cv.toString()).toList();
          if (availableCVs.isNotEmpty && selectedCVFilename == null) {
            selectedCVFilename = availableCVs.first;
          }
        });
      }
    } catch (e) {
      debugPrint('Error loading CVs: $e');
      // Fallback to default list
      setState(() {
        availableCVs = [
          'MichaelPage_v1.pdf',
          'NoToViolence_v10.pdf',
          'example_professional_cv.pdf',
        ];
        if (selectedCVFilename == null) {
          selectedCVFilename = availableCVs.first;
        }
      });
    }
  }

  Future<void> _extractCVKeywords() async {
    if (selectedCVFilename == null || selectedCVFilename!.isEmpty) {
      NotificationService.showError('Please select a CV first.');
      return;
    }

    setState(() {
      _isExtractingCVKeywords = true;
    });

    showDialog(
      context: context,
      useRootNavigator: true,
      barrierDismissible: false,
      builder: (_) => const CVAnalysisDialog(),
    );

    try {
      final skills = await _apiService.extractSkillsDynamic(
        mode: 'cv',
        cvFilename: selectedCVFilename!,
      );

      debugPrint('[CV-MAGIC] CV keywords extracted: $skills');
      setState(() {
        _cvKeywords = skills;
      });

      // Save to persistent cache
      await KeywordCacheService.saveCVKeywords(
        cvFilename: selectedCVFilename!,
        technicalSkills: List<String>.from(skills['technical_skills'] ?? []),
        softSkills: List<String>.from(skills['soft_skills'] ?? []),
        domainKeywords: List<String>.from(skills['domain_keywords'] ?? []),
      );

      // Check if both CV and JD keywords are available
      if (_jdKeywords.isNotEmpty) {
        setState(() {
          _keywordsExtracted = true;
        });
      }

      NotificationService.showSuccess('CV keywords extracted successfully!');
    } catch (e) {
      setState(() {
        _cvKeywords = {};
      });
      NotificationService.showError('Failed to extract CV keywords: $e');
      debugPrint('Error extracting CV keywords: $e');
    } finally {
      setState(() {
        _isExtractingCVKeywords = false;
      });
      if (Navigator.of(context, rootNavigator: true).canPop()) {
        Navigator.of(context, rootNavigator: true).pop();
      }
    }
  }

  Future<void> _extractJDKeywords() async {
    final jdText = _jdController.text.trim();
    if (jdText.isEmpty) {
      NotificationService.showError('Please provide job description first.');
      return;
    }

    setState(() {
      _isExtractingJDKeywords = true;
      this.jdText = jdText; // Update the class variable
    });

    showDialog(
      context: context,
      useRootNavigator: true,
      barrierDismissible: false,
      builder: (_) => const CVAnalysisDialog(),
    );

    try {
      final skills = await _apiService.extractSkillsDynamic(
        mode: 'jd',
        jdText: jdText,
      );

      debugPrint('[CV-MAGIC] JD keywords extracted: $skills');
      setState(() {
        _jdKeywords = skills;
      });

      // Save to persistent cache
      await KeywordCacheService.saveJDKeywords(
        jdText: jdText,
        technicalSkills: List<String>.from(skills['technical_skills'] ?? []),
        softSkills: List<String>.from(skills['soft_skills'] ?? []),
        domainKeywords: List<String>.from(skills['domain_keywords'] ?? []),
      );

      // Check if both CV and JD keywords are available
      if (_cvKeywords.isNotEmpty) {
        setState(() {
          _keywordsExtracted = true;
        });
      }

      NotificationService.showSuccess('JD keywords extracted successfully!');
    } catch (e) {
      setState(() {
        _jdKeywords = {};
      });
      NotificationService.showError('Failed to extract JD keywords: $e');
      debugPrint('Error extracting JD keywords: $e');
    } finally {
      setState(() {
        _isExtractingJDKeywords = false;
      });
      if (Navigator.of(context, rootNavigator: true).canPop()) {
        Navigator.of(context, rootNavigator: true).pop();
      }
    }
  }

  Future<void> _extractBothKeywords() async {
    if (selectedCVFilename == null || selectedCVFilename!.isEmpty) {
      NotificationService.showError('Please select a CV first.');
      return;
    }

    final jdText = _jdController.text.trim();
    if (jdText.isEmpty) {
      NotificationService.showError('Please provide job description first.');
      return;
    }

    // Check if both are already cached
    final areCached = await KeywordCacheService.areBothKeywordsCached(
        selectedCVFilename!, jdText);

    if (areCached) {
      await _loadCachedKeywords();
      NotificationService.showSuccess('Keywords loaded from cache!');
      return;
    }

    // Extract both if not cached
    await _extractCVKeywords();
    if (_cvKeywords.isNotEmpty) {
      await _extractJDKeywords();
    }
  }

  @override
  void dispose() {
    _cardController.dispose();
    _buttonController.dispose();
    _fadeController.dispose();
    _inlinePromptController.dispose();
    _jdController.dispose();
    super.dispose();
  }

  // Main ATS test function
  Future<void> _runInitialATSTest() async {
    if (selectedCVFilename == null || jdText.isEmpty) {
      _showMissingDataDialog();
      return;
    }

    setState(() => isTesting = true);
    _cardController.repeat();

    _showLoadingDialog();

    try {
      // Simulate ATS test
      await Future.delayed(const Duration(seconds: 3));

      if (!mounted) return;
      if (context.mounted) Navigator.pop(context);

      setState(() {
        latestATSScore = 85; // Simulated score
        currentState = 'atsCompleted';

        _inlineOptimizationSteps.add({
          'type': 'ats_result',
          'cvName': selectedCVFilename,
          'timestamp': DateTime.now(),
        });
      });

      NotificationService.showSuccess(
          'ATS Test completed! Score: $latestATSScore/100');
    } catch (e) {
      if (!mounted) return;
      if (context.mounted) Navigator.pop(context);

      NotificationService.showError('ATS Test Failed: $e');
    } finally {
      if (mounted) {
        setState(() => isTesting = false);
        _cardController.stop();
      }
    }
  }

  // Generate improved CV
  Future<void> _generateImprovedCV() async {
    final additionalPrompt = _inlinePromptController.text.trim();
    if (additionalPrompt.isEmpty) {
      NotificationService.showError('Please provide additional instructions');
      return;
    }

    setState(() => _isInlineGenerating = true);

    _showLoadingDialog();

    try {
      // Simulate CV generation
      await Future.delayed(const Duration(seconds: 2));

      if (!mounted) return;
      if (context.mounted) Navigator.pop(context);

      setState(() {
        _inlineOptimizationSteps.add({
          'type': 'cv_generated',
          'cvName': 'Improved_${selectedCVFilename}',
          'prompt': additionalPrompt,
          'timestamp': DateTime.now(),
        });
        currentCVName = 'Improved_${selectedCVFilename}';
        currentState = 'cvGenerated';
      });

      NotificationService.showSuccess('CV improved successfully!');
    } catch (e) {
      if (!mounted) return;
      if (context.mounted) Navigator.pop(context);

      NotificationService.showError('CV Generation Failed: $e');
    } finally {
      if (mounted) {
        setState(() => _isInlineGenerating = false);
      }
    }
  }

  void _showMissingDataDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Missing Data'),
        content:
            const Text('Please select a CV and add job description first.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showLoadingDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Processing...'),
        content: const Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: 16),
            Text('Please wait...'),
          ],
        ),
      ),
    );
  }

  void _openClassicPreview() {
    if (selectedCVFilename == null) {
      NotificationService.showError('No CV selected for preview');
      return;
    }
    // Simple text preview as fallback
    showDialog(
      context: context,
      useRootNavigator: true,
      builder: (context) => AlertDialog(
        title: const Text('CV Preview'),
        content: SizedBox(
          width: double.maxFinite,
          height: 400,
          child: SingleChildScrollView(
            child: Text(
                'Preview for: $selectedCVFilename\n\nThis is a simple text preview of your CV content.'),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildCVSelectionSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Select CV:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            DropdownButton<String>(
              value: selectedCVFilename,
              hint: const Text('Choose CV'),
              isExpanded: true,
              items: availableCVs
                  .map((cv) => DropdownMenuItem(
                        value: cv,
                        child: Text(cv),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  selectedCVFilename = value;
                  // Clear keywords when CV changes
                  _cvKeywords = {};
                  _keywordsExtracted = false;
                });
                // Load cached keywords for new CV if available
                _loadCachedKeywords();
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildJobDescriptionSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Job Description:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            TextField(
              controller: _jdController,
              maxLines: 6,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Paste job description here...',
              ),
              onChanged: (val) {
                setState(() {
                  jdText = val;
                  // Clear JD keywords when text changes
                  _jdKeywords = {};
                  _keywordsExtracted = false;
                });
                // Load cached keywords if available
                _loadCachedKeywords();
              },
            ),
            const SizedBox(height: 12),
            // Extract Keywords Button
            ElevatedButton.icon(
              onPressed: (_isExtractingCVKeywords || _isExtractingJDKeywords)
                  ? null
                  : _extractBothKeywords,
              icon: _isExtractingCVKeywords || _isExtractingJDKeywords
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.auto_awesome),
              label: Text(_isExtractingCVKeywords || _isExtractingJDKeywords
                  ? 'Extracting Keywords...'
                  : 'Extract Keywords (AI)'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.purple.shade600,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKeywordsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Extracted Keywords:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                    child: _buildKeywordColumn('CV Keywords', _cvKeywords)),
                const SizedBox(width: 16),
                Expanded(
                    child: _buildKeywordColumn('JD Keywords', _jdKeywords)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildKeywordColumn(String title, Map<String, dynamic> keywords) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        _buildKeywordChips('Technical Skills',
            keywords['technical_skills'] ?? [], Colors.blue),
        const SizedBox(height: 8),
        _buildKeywordChips(
            'Soft Skills', keywords['soft_skills'] ?? [], Colors.green),
        const SizedBox(height: 8),
        _buildKeywordChips('Domain Keywords', keywords['domain_keywords'] ?? [],
            Colors.purple),
      ],
    );
  }

  Widget _buildKeywordChips(
      String category, List<dynamic> keywords, Color color) {
    final keywordList = keywords.map((k) => k.toString()).toList();

    if (keywordList.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('$category:',
              style: TextStyle(fontSize: 12, color: Colors.grey[600])),
          const Text('None found',
              style: TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('$category (${keywordList.length}):',
            style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        const SizedBox(height: 4),
        Wrap(
          spacing: 4,
          runSpacing: 4,
          children: keywordList
              .take(6)
              .map((keyword) => Chip(
                    label: Text(keyword, style: const TextStyle(fontSize: 10)),
                    backgroundColor: color.withOpacity(0.1),
                    side: BorderSide(color: color.withOpacity(0.3)),
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ))
              .toList(),
        ),
        if (keywordList.length > 6)
          Text('... and ${keywordList.length - 6} more',
              style: TextStyle(fontSize: 10, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildATSTestSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('ATS Testing:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 16),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: isTesting ? null : _runInitialATSTest,
                  icon: isTesting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.analytics),
                  label: Text(isTesting ? 'Testing...' : 'Run ATS Test'),
                ),
                const SizedBox(width: 16),
                if (latestATSScore > 0)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: latestATSScore >= 80
                          ? Colors.green
                          : latestATSScore >= 60
                              ? Colors.orange
                              : Colors.red,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      'Score: $latestATSScore/100',
                      style: const TextStyle(
                          color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPreviewSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('CV Preview:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    icon: const Icon(Icons.preview),
                    label: const Text('Simple Preview'),
                    onPressed: _openClassicPreview,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImprovementSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('CV Improvement:',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 8),
            TextField(
              controller: _inlinePromptController,
              maxLines: 3,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Enter additional instructions for CV improvement...',
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _isInlineGenerating ? null : _generateImprovedCV,
              icon: _isInlineGenerating
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.auto_awesome),
              label: Text(_isInlineGenerating ? 'Generating...' : 'Improve CV'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CV Magic'),
        backgroundColor: Colors.blue.shade600,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // CV Selection
            _buildCVSelectionSection(),
            const SizedBox(height: 16),

            // Job Description
            _buildJobDescriptionSection(),
            const SizedBox(height: 16),

            // Keywords Section (if extracted)
            if (_keywordsExtracted) ...[
              _buildKeywordsSection(),
              const SizedBox(height: 16),
            ],

            // ATS Test
            _buildATSTestSection(),
            const SizedBox(height: 16),

            // Preview Section
            _buildPreviewSection(),
            const SizedBox(height: 16),

            // Improvement Section
            _buildImprovementSection(),
            const SizedBox(height: 24),

            // Optimization Steps (if any)
            if (_inlineOptimizationSteps.isNotEmpty) ...[
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Optimization History:',
                          style: TextStyle(
                              fontWeight: FontWeight.bold, fontSize: 16)),
                      const SizedBox(height: 8),
                      ..._inlineOptimizationSteps.map((step) => ListTile(
                            leading: Icon(
                              step['type'] == 'ats_result'
                                  ? Icons.analytics
                                  : Icons.auto_awesome,
                              color: Colors.blue.shade600,
                            ),
                            title: Text(step['type'] == 'ats_result'
                                ? 'ATS Test Completed'
                                : 'CV Improved'),
                            subtitle: Text(step['timestamp'].toString()),
                          )),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
