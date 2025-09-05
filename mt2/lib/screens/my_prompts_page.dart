import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../theme/app_theme.dart';
import '../state/session_state.dart';
import '../utils/notification_service.dart';
import '../widgets/uniform_top_nav_bar.dart';
import '../config/prompt_config.dart';

class MyPromptsPage extends StatefulWidget {
  const MyPromptsPage({super.key});

  @override
  State<MyPromptsPage> createState() => _MyPromptsPageState();
}

class _MyPromptsPageState extends State<MyPromptsPage>
    with TickerProviderStateMixin {
  late AnimationController _cardController;
  late AnimationController _saveController;
  late TabController _tabController;

  // Controllers for all prompts
  final Map<String, TextEditingController> _controllers = {};

  bool _isModified = false;
  bool _isSaving = false;

  // Use centralized prompt system
  final Map<String, Map<String, String>> _allPrompts = PromptConfig.allPrompts;

  // Tab categories
  final List<String> _categories = [
    'User Interface',
    'Core System',
    'Skill Analysis',
    'Job Processing',
    'Skill Matching'
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _categories.length, vsync: this);
    _cardController = AnimationController(
      duration: AppTheme.normalAnimation,
      vsync: this,
    );
    _saveController = AnimationController(
      duration: AppTheme.fastAnimation,
      vsync: this,
    );

    _initializeControllers();
    _loadPrompts();
    _cardController.forward();
  }

  void _initializeControllers() {
    // Create controllers for all prompts
    for (String category in _allPrompts.keys) {
      for (String promptKey in _allPrompts[category]!.keys) {
        _controllers[promptKey] = TextEditingController();
      }
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    _cardController.dispose();
    _saveController.dispose();
    for (var controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  void _loadPrompts() {
    // Load saved prompts or use defaults
    for (String category in _allPrompts.keys) {
      for (String promptKey in _allPrompts[category]!.keys) {
        _controllers[promptKey]!.text = SessionState.customPrompts[promptKey] ??
            _allPrompts[category]![promptKey]!;

        // Add listeners to detect changes
        _controllers[promptKey]!.addListener(_onPromptChanged);
      }
    }
  }

  void _onPromptChanged() {
    if (!_isModified) {
      setState(() => _isModified = true);
    }
  }

  Future<void> _savePrompts() async {
    setState(() => _isSaving = true);
    _saveController.forward();

    try {
      // Save all prompts to session state
      Map<String, String> allPrompts = {};
      for (String category in _allPrompts.keys) {
        for (String promptKey in _allPrompts[category]!.keys) {
          allPrompts[promptKey] = _controllers[promptKey]!.text;
        }
      }

      SessionState.customPrompts = allPrompts;
      await SessionState.saveToDisk();

      await Future.delayed(
          const Duration(milliseconds: 500)); // Simulate save delay

      setState(() {
        _isModified = false;
        _isSaving = false;
      });

      _saveController.reverse();

      NotificationService.showToast(
        "🎉 All prompts saved successfully!",
        backgroundColor: Colors.green,
      );
    } catch (e) {
      setState(() => _isSaving = false);
      _saveController.reverse();

      NotificationService.showToast(
        "❌ Failed to save prompts: $e",
        backgroundColor: Colors.red,
      );
    }
  }

  void _resetToDefaults() {
    showDialog(
      context: context,
      useRootNavigator: true,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: AppTheme.cardRadius),
        title: Row(
          children: [
            Icon(Icons.warning_amber_rounded, color: AppTheme.warningOrange),
            const SizedBox(width: 8),
            const Text('Reset to Defaults'),
          ],
        ),
        content: const Text(
          'Are you sure you want to reset all prompts to their default values? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _performReset();
            },
            style: AppTheme.dangerButtonStyle,
            child: const Text('Reset All'),
          ),
        ],
      ),
    );
  }

  void _performReset() {
    setState(() {
      for (String category in _allPrompts.keys) {
        for (String promptKey in _allPrompts[category]!.keys) {
          _controllers[promptKey]!.text = _allPrompts[category]![promptKey]!;
        }
      }
      _isModified = true;
    });

    NotificationService.showToast(
      "🔄 All prompts reset to defaults",
      backgroundColor: Colors.orange,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Prompts'),
        backgroundColor: AppTheme.primaryCosmic,
        foregroundColor: Colors.white,
        elevation: 0,
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
          tabAlignment: TabAlignment.start,
          tabs: _categories
              .map((category) => Tab(
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 120),
                      child: Text(
                        category,
                        style: const TextStyle(fontSize: 14),
                        overflow: TextOverflow.ellipsis,
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ))
              .toList(),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.backgroundGradient,
        ),
        child: TabBarView(
          controller: _tabController,
          children: _categories
              .map((category) => _buildCategoryView(category))
              .toList(),
        ),
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              offset: const Offset(0, -2),
              blurRadius: 8,
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: ElevatedButton(
                onPressed: _isModified && !_isSaving ? _savePrompts : null,
                style: AppTheme.primaryButtonStyle,
                child: _isSaving
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor:
                              AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      )
                    : const Text('💾 Save All Changes'),
              ),
            ),
            const SizedBox(width: 12),
            ElevatedButton(
              onPressed: _resetToDefaults,
              style: AppTheme.secondaryButtonStyle,
              child: const Text('🔄 Reset'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCategoryView(String category) {
    final prompts = _allPrompts[category] ?? {};

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Category Header
          AnimatedBuilder(
            animation: _cardController,
            builder: (context, child) {
              return Transform.translate(
                offset: Offset(0, (1 - _cardController.value) * 50),
                child: Opacity(
                  opacity: _cardController.value,
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: AppTheme.cardGradient,
                      borderRadius: AppTheme.cardRadius,
                      boxShadow: AppTheme.cardShadow,
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              _getCategoryIcon(category),
                              color: AppTheme.primaryCosmic,
                              size: 24,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                category,
                                style: AppTheme.headingMedium,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _getCategoryDescription(category),
                          style: AppTheme.bodyMedium.copyWith(
                            color: AppTheme.neutralGray600,
                          ),
                        ),
                        const SizedBox(height: 12),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: AppTheme.primaryCosmic.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: AppTheme.primaryCosmic.withOpacity(0.3),
                            ),
                          ),
                          child: Text(
                            "${prompts.length} prompts",
                            style: AppTheme.bodySmall.copyWith(
                              color: AppTheme.primaryCosmic,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),

          const SizedBox(height: 24),

          // Prompt Cards
          ...prompts.entries
              .map((entry) => _buildPromptCard(
                    entry.key,
                    entry.value,
                    _controllers[entry.key]!,
                  ))
              .toList(),
        ],
      ),
    );
  }

  Widget _buildPromptCard(String promptKey, String defaultPrompt,
      TextEditingController controller) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: AppTheme.cardRadius,
        boxShadow: AppTheme.cardShadow,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.neutralGray50,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.chat_bubble_outline,
                  color: AppTheme.primaryCosmic,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _getPromptTitle(promptKey),
                    style: AppTheme.bodyLarge.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Description
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Text(
              PromptConfig.getPromptDescription(promptKey),
              style: AppTheme.bodySmall.copyWith(
                color: AppTheme.neutralGray600,
              ),
            ),
          ),

          // Text Editor
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: controller,
              maxLines: 15,
              decoration: InputDecoration(
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(color: AppTheme.neutralGray300),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide:
                      BorderSide(color: AppTheme.primaryCosmic, width: 2),
                ),
                hintText: 'Enter your custom prompt...',
                hintStyle: AppTheme.bodyMedium.copyWith(
                  color: AppTheme.neutralGray400,
                ),
              ),
              style: AppTheme.bodyMedium,
            ),
          ),

          // Footer
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                TextButton.icon(
                  onPressed: () {
                    controller.text = defaultPrompt;
                  },
                  icon: const Icon(Icons.refresh, size: 16),
                  label: const Text('Reset to Default'),
                  style: TextButton.styleFrom(
                    foregroundColor: AppTheme.neutralGray600,
                  ),
                ),
                const Spacer(),
                Text(
                  "${controller.text.length} characters",
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.neutralGray500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'Core System':
        return Icons.settings_applications;
      case 'User Interface':
        return Icons.dashboard;
      case 'Skill Analysis':
        return Icons.analytics;
      case 'Job Processing':
        return Icons.work;
      case 'Skill Matching':
        return Icons.compare_arrows;
      default:
        return Icons.description;
    }
  }

  String _getCategoryDescription(String category) {
    switch (category) {
      case 'Core System':
        return 'Main ATS evaluation and CV tailoring engine prompts';
      case 'User Interface':
        return 'User-facing prompts for analysis and generation';
      case 'Skill Analysis':
        return 'Prompts for extracting and categorizing skills';
      case 'Job Processing':
        return 'Prompts for processing job descriptions and metadata';
      case 'Skill Matching':
        return 'Prompts for comparing and matching skills between CV and JD';
      default:
        return 'Custom prompts for AI interactions';
    }
  }

  String _getPromptTitle(String promptKey) {
    switch (promptKey) {
      case 'ats_system':
        return 'ATS System Prompt';
      case 'cv_tailoring':
        return 'CV Tailoring Prompt';
      case 'tailor_initial':
        return 'Initial CV Tailoring';
      case 'tailor_iterative':
        return 'Iterative CV Refinement';
      case 'analyze_match_fit':
        return 'CV-JD Match Analysis';
      case 'cv_analysis':
        return 'CV Analysis';
      case 'cv_generation':
        return 'CV Generation';
      case 'ats_test':
        return 'ATS Test';
      case 'skill_extraction':
        return 'Skill Extraction';
      case 'technical_skills':
        return 'Technical Skills Extraction';
      case 'soft_skills':
        return 'Soft Skills Extraction';
      case 'domain_keywords':
        return 'Domain Keywords Extraction';
      case 'job_metadata':
        return 'Job Metadata Extraction';
      case 'ai_matcher':
        return 'AI Matcher';
      default:
        return promptKey.replaceAll('_', ' ').toUpperCase();
    }
  }
}
