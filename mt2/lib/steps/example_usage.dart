import 'package:flutter/material.dart';
import 'analysis_orchestrator.dart';
import 'step_1_preliminary_analysis/preliminary_analysis_controller.dart';
import 'step_1_preliminary_analysis/preliminary_analysis_widget.dart';
import 'step_2_ai_analysis/ai_analysis_controller.dart';
import 'step_2_ai_analysis/ai_analysis_widget.dart';
import 'step_3_skill_comparison/skill_comparison_controller.dart';
import 'step_3_skill_comparison/skill_comparison_widget.dart';
import 'step_4_enhanced_ats/enhanced_ats_controller.dart';
import 'step_4_enhanced_ats/enhanced_ats_widget.dart';
import 'step_5_ai_recommendations/ai_recommendations_controller.dart';
import 'step_5_ai_recommendations/ai_recommendations_widget.dart';

/// Example demonstrating how to use the modular analysis architecture
/// This shows how to set up the orchestrator and integrate it into a Flutter widget
class ModularAnalysisExample extends StatefulWidget {
  const ModularAnalysisExample({super.key});

  @override
  State<ModularAnalysisExample> createState() => _ModularAnalysisExampleState();
}

class _ModularAnalysisExampleState extends State<ModularAnalysisExample> {
  late final AnalysisOrchestrator _orchestrator;
  final TextEditingController _cvFilenameController = TextEditingController();
  final TextEditingController _jdTextController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _setupOrchestrator();
  }

  /// Set up the orchestrator with all analysis steps
  void _setupOrchestrator() {
    _orchestrator = AnalysisOrchestrator();

    // Register all 5 steps
    _orchestrator.registerStep(PreliminaryAnalysisController());
    _orchestrator.registerStep(AIAnalysisController());
    _orchestrator.registerStep(SkillComparisonController());
    _orchestrator.registerStep(EnhancedATSController());
    _orchestrator.registerStep(AIRecommendationsController());

    debugPrint(
        '[EXAMPLE] Orchestrator setup complete with ${_orchestrator.steps.length} steps');
  }

  @override
  void dispose() {
    _orchestrator.dispose();
    _cvFilenameController.dispose();
    _jdTextController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Modular Analysis Example'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Input Section
            _buildInputSection(),

            const SizedBox(height: 24),

            // Control Section
            _buildControlSection(),

            const SizedBox(height: 24),

            // Progress Section
            _buildProgressSection(),

            const SizedBox(height: 24),

            // Results Section
            Expanded(
              child: _buildResultsSection(),
            ),
          ],
        ),
      ),
    );
  }

  /// Build the input section for CV filename and JD text
  Widget _buildInputSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Input Data',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _cvFilenameController,
              decoration: const InputDecoration(
                labelText: 'CV Filename',
                hintText: 'e.g., maheshwor_tiwari.pdf',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _jdTextController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Job Description',
                hintText: 'Paste the job description here...',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Build the control section with action buttons
  Widget _buildControlSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Controls',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        _orchestrator.isRunning ? null : _executeAllSteps,
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('Execute All Steps'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        _orchestrator.isRunning ? null : _resetOrchestrator,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Reset'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.orange,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        _orchestrator.isRunning ? null : _executeSingleStep,
                    icon: const Icon(Icons.play_circle_outline),
                    label: const Text('Execute Step 1 Only'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.green,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed:
                        _orchestrator.isRunning ? null : _loadCachedResults,
                    icon: const Icon(Icons.download),
                    label: const Text('Load Cache'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.blue,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Build the progress section
  Widget _buildProgressSection() {
    return ListenableBuilder(
      listenable: _orchestrator,
      builder: (context, _) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Progress',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                LinearProgressIndicator(
                  value: _orchestrator.progress,
                  backgroundColor: Colors.grey[300],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _orchestrator.isCompleted ? Colors.green : Colors.blue,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '${_orchestrator.completedStepsCount}/${_orchestrator.totalStepsCount} steps completed',
                  style: const TextStyle(fontSize: 14),
                ),
                if (_orchestrator.currentStepId != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    'Current: ${_orchestrator.currentStepId}',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: Colors.blue,
                    ),
                  ),
                ],
                if (_orchestrator.error != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    'Error: ${_orchestrator.error}',
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.red,
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  /// Build the results section
  Widget _buildResultsSection() {
    return ListenableBuilder(
      listenable: _orchestrator,
      builder: (context, _) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Results',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        // Display Step 1: Preliminary Analysis results
                        if (_orchestrator.steps
                            .containsKey('preliminary_analysis')) ...[
                          PreliminaryAnalysisWidget(
                            controller:
                                _orchestrator.steps['preliminary_analysis']!
                                    as PreliminaryAnalysisController,
                          ),
                          const SizedBox(height: 16),
                        ],

                        // Display Step 2: AI Analysis results
                        if (_orchestrator.steps.containsKey('ai_analysis')) ...[
                          AIAnalysisWidget(
                            controller: _orchestrator.steps['ai_analysis']!
                                as AIAnalysisController,
                          ),
                          const SizedBox(height: 16),
                        ],

                        // Display Step 3: Skill Comparison results
                        if (_orchestrator.steps
                            .containsKey('skill_comparison')) ...[
                          SkillComparisonWidget(
                            controller: _orchestrator.steps['skill_comparison']!
                                as SkillComparisonController,
                          ),
                          const SizedBox(height: 16),
                        ],

                        // Display Step 4: Enhanced ATS results
                        if (_orchestrator.steps
                            .containsKey('enhanced_ats')) ...[
                          EnhancedATSWidget(
                            controller: _orchestrator.steps['enhanced_ats']!
                                as EnhancedATSController,
                          ),
                          const SizedBox(height: 16),
                        ],

                        // Display Step 5: AI Recommendations results
                        if (_orchestrator.steps
                            .containsKey('ai_recommendations')) ...[
                          AIRecommendationsWidget(
                            controller:
                                _orchestrator.steps['ai_recommendations']!
                                    as AIRecommendationsController,
                          ),
                          const SizedBox(height: 16),
                        ],

                        // Show message if no results
                        if (!_orchestrator.hasResults) ...[
                          const Center(
                            child: Text(
                              'No results yet. Execute the analysis to see results.',
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  // ==================== ACTION METHODS ====================

  /// Execute all steps
  Future<void> _executeAllSteps() async {
    final cvFilename = _cvFilenameController.text.trim();
    final jdText = _jdTextController.text.trim();

    if (cvFilename.isEmpty || jdText.isEmpty) {
      _showSnackBar('Please enter both CV filename and JD text');
      return;
    }

    try {
      await _orchestrator.executeAllSteps(
        cvFilename: cvFilename,
        jdText: jdText,
      );
      _showSnackBar('Analysis completed successfully!');
    } catch (e) {
      _showSnackBar('Analysis failed: $e');
    }
  }

  /// Execute only Step 1
  Future<void> _executeSingleStep() async {
    final cvFilename = _cvFilenameController.text.trim();
    final jdText = _jdTextController.text.trim();

    if (cvFilename.isEmpty || jdText.isEmpty) {
      _showSnackBar('Please enter both CV filename and JD text');
      return;
    }

    try {
      await _orchestrator.executeStep(
        'preliminary_analysis',
        cvFilename: cvFilename,
        jdText: jdText,
      );
      _showSnackBar('Step 1 completed successfully!');
    } catch (e) {
      _showSnackBar('Step 1 failed: $e');
    }
  }

  /// Load cached results
  Future<void> _loadCachedResults() async {
    final cvFilename = _cvFilenameController.text.trim();
    final jdText = _jdTextController.text.trim();

    if (cvFilename.isEmpty || jdText.isEmpty) {
      _showSnackBar('Please enter both CV filename and JD text');
      return;
    }

    try {
      await _orchestrator.loadCachedResults(cvFilename, jdText);
      _showSnackBar('Cached results loaded!');
    } catch (e) {
      _showSnackBar('Failed to load cache: $e');
    }
  }

  /// Reset the orchestrator
  void _resetOrchestrator() {
    _orchestrator.reset();
    _showSnackBar('Orchestrator reset');
  }

  /// Show a snackbar message
  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }
}
