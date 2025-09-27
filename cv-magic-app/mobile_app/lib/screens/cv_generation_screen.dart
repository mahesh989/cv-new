import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import '../core/theme/app_theme.dart';
import '../services/skills_analysis_handler.dart';

class CVGenerationScreen extends StatefulWidget {
  final VoidCallback? onNavigateToCVMagic;

  const CVGenerationScreen({
    super.key,
    this.onNavigateToCVMagic,
  });

  @override
  State<CVGenerationScreen> createState() => _CVGenerationScreenState();
}

class _CVGenerationScreenState extends State<CVGenerationScreen> {
  bool _isGenerating = false;
  bool _isEditMode = false;
  String? _currentCompany;
  String? tailoredCVContent;
  final TextEditingController _editController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeaderCard(),
          const SizedBox(height: 20),
          _buildCVGenerationCard(),
        ],
      ),
    );
  }

  Widget _buildHeaderCard() {
    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  gradient: AppTheme.primaryGradient,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  color: Colors.white,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'CV Generation',
                      style: AppTheme.headingSmall.copyWith(
                        color: AppTheme.primaryTeal,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Generate professional CVs with AI assistance',
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.neutralGray600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  bool _isLoadingCV = false;

  Future<void> _loadTailoredCV() async {
    setState(() {
      _isLoadingCV = true;
      _isGenerating = true;
      tailoredCVContent = null; // Reset content before loading
    });

    try {
      // Load the latest tailored CV across all companies
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/cv/latest-tailored-cv'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          tailoredCVContent = data['content'] ?? 'No content available';
          _currentCompany = data['company'] ?? 'Unknown';
        });
      } else {
        setState(() {
          tailoredCVContent =
              'Failed to load tailored CV. Status: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        tailoredCVContent = 'Error loading tailored CV: $e';
      });
    } finally {
      setState(() {
        _isLoadingCV = false;
        _isGenerating = false;
      });
    }
  }

  String _formatTailoredCVContent(String content) {
    final lines = content.split('\n');
    final formattedLines = <String>[];

    for (final line in lines) {
      if (line.trim().isEmpty) {
        formattedLines.add('');
        continue;
      }

      // Skip metadata header section - filter out any metadata lines
      if (line.contains('TAILORED CV TEXT') ||
          line.contains('Target Company:') ||
          line.contains('Generated:') ||
          line.contains('ATS Score:') ||
          line.contains('Framework Version:') ||
          line.contains('CV GENERATION METADATA') ||
          line.startsWith('===') ||
          line.startsWith('=')) {
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

  Widget _buildCVPreview() {
    if (_isLoadingCV) {
      return const Center(child: CircularProgressIndicator());
    }

    if (tailoredCVContent == null) {
      return const SizedBox.shrink();
    }

    return Container(
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
              const Icon(Icons.preview, color: Colors.blue),
              const SizedBox(width: 8),
              Text(
                'Tailored CV Preview',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            height: 300,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[900], // Black background like original CV
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey[700]!),
            ),
            child: SingleChildScrollView(
              child: _isEditMode
                  ? _buildEditableContent()
                  : SelectableText(
                      _formatTailoredCVContent(tailoredCVContent!),
                      style: TextStyle(
                        fontSize: 13,
                        height: 1.6,
                        fontFamily:
                            'monospace', // Monospace font like original CV
                        color: Colors.grey[100], // Light text like original CV
                      ),
                    ),
            ),
          ),
          const SizedBox(height: 16),
          // Action buttons
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildCVGenerationCard() {
    return AppTheme.createCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Tailored CV Generation',
            style: AppTheme.headingMedium.copyWith(
              color: AppTheme.primaryTeal,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Generate an optimized CV using our AI-powered framework. The system will automatically find and display the latest tailored CV from your analysis pipeline.',
            style: AppTheme.bodyMedium.copyWith(color: AppTheme.neutralGray600),
          ),
          const SizedBox(height: 20),

          // Demo Info Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.primaryTeal.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppTheme.primaryTeal.withOpacity(0.3),
                width: 1,
              ),
            ),
            child: Row(
              children: [
                Icon(Icons.info_outline, color: AppTheme.primaryTeal, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'The system automatically finds the most recent tailored CV from your analysis pipeline and displays it in the preview.',
                    style: AppTheme.bodySmall.copyWith(
                      color: AppTheme.primaryTeal,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Generate Button and Close Button Row
          Row(
            children: [
              // Generate Button
              Expanded(
                child: ElevatedButton(
                  onPressed: _isGenerating
                      ? null
                      : () async {
                          await _loadTailoredCV();
                        },
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    backgroundColor: AppTheme.primaryTeal,
                    disabledBackgroundColor: AppTheme.neutralGray300,
                  ),
                  child: _isGenerating
                      ? Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  Colors.white,
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              'Generating CV...',
                              style: AppTheme.bodyMedium.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        )
                      : Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(
                              Icons.auto_awesome,
                              color: Colors.white,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              'Generate Tailored CV',
                              style: AppTheme.bodyMedium.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                ),
              ),

              // Close Button
              if (tailoredCVContent != null) ...[
                const SizedBox(width: 12),
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.red[100],
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.red[300]!, width: 1),
                  ),
                  child: IconButton(
                    onPressed: () {
                      setState(() {
                        tailoredCVContent = null;
                        _isLoadingCV = false;
                        _isGenerating = false;
                      });
                    },
                    icon: Icon(Icons.close, color: Colors.red[600], size: 20),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 20),
          if (tailoredCVContent != null) _buildCVPreview(),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        // Edit Button
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _toggleEditMode,
            icon: Icon(_isEditMode ? Icons.save : Icons.edit),
            label: Text(_isEditMode ? 'Save' : 'Edit'),
            style: ElevatedButton.styleFrom(
              backgroundColor: _isEditMode ? Colors.green : Colors.blue,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
        const SizedBox(width: 12),

        // Additional Prompt Button
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _showAdditionalPromptDialog,
            icon: const Icon(Icons.add_comment),
            label: const Text('Additional Prompt'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
        const SizedBox(width: 12),

        // Run ATS Again Button
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _runATSAgain,
            icon: const Icon(Icons.analytics),
            label: const Text('Run ATS Again'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.purple,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildEditableContent() {
    if (_editController.text.isEmpty && tailoredCVContent != null) {
      _editController.text = tailoredCVContent!;
    }

    return TextField(
      controller: _editController,
      maxLines: null,
      style: TextStyle(
        fontSize: 13,
        height: 1.6,
        fontFamily: 'monospace',
        color: Colors.grey[100],
      ),
      decoration: const InputDecoration(
        border: InputBorder.none,
        hintText: 'Edit your CV content here...',
        hintStyle: TextStyle(color: Colors.grey),
      ),
      onChanged: _onContentChanged,
    );
  }

  void _toggleEditMode() {
    setState(() {
      if (_isEditMode) {
        // Save mode - update the content and save to backend
        tailoredCVContent = _editController.text;
        _saveEditedContent();
      } else {
        // Edit mode - populate the text field
        _editController.text = tailoredCVContent ?? '';
      }
      _isEditMode = !_isEditMode;
    });
  }

  void _onContentChanged(String value) {
    // Real-time auto-save every 2 seconds after user stops typing
    if (_isEditMode) {
      tailoredCVContent = value;
      _debounceAutoSave();
    }
  }

  Timer? _autoSaveTimer;
  void _debounceAutoSave() {
    _autoSaveTimer?.cancel();
    _autoSaveTimer = Timer(const Duration(seconds: 2), () {
      _saveEditedContent();
    });
  }

  Future<void> _saveEditedContent() async {
    if (_currentCompany == null || tailoredCVContent == null) return;

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/tailored-cv/save-edited'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'company': _currentCompany,
          'content': tailoredCVContent,
        }),
      );

      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✅ CV saved successfully!'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 2),
            ),
          );
        }
      }
    } catch (e) {
      print('Error saving edited content: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error saving CV: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  void _showAdditionalPromptDialog() {
    final TextEditingController promptController = TextEditingController();

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Additional Prompt'),
          content: SizedBox(
            width: double.maxFinite,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text(
                  'Enter additional instructions for CV improvement:',
                  style: TextStyle(fontSize: 14),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: promptController,
                  maxLines: 5,
                  decoration: const InputDecoration(
                    hintText:
                        'E.g., "Add more technical skills", "Emphasize leadership experience", etc.',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                _saveAdditionalPrompt(promptController.text);
              },
              child: const Text('Save'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _saveAdditionalPrompt(String promptText) async {
    if (promptText.trim().isEmpty || _currentCompany == null) return;

    try {
      final response = await http.post(
        Uri.parse(
            'http://localhost:8000/api/tailored-cv/save-additional-prompt'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'company': _currentCompany,
          'prompt': promptText.trim(),
        }),
      );

      if (response.statusCode == 200) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✅ Additional prompt saved successfully!'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 2),
            ),
          );
        }
      }
    } catch (e) {
      print('Error saving additional prompt: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Error saving prompt: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  void _runATSAgain() async {
    debugPrint('🗑 [CV_GENERATION] Run ATS Again clicked - clearing results');

    try {
      // Clear all results first
      await SkillsAnalysisHandler.clearResults();
      debugPrint('✅ [CV_GENERATION] Results cleared successfully');

      // Navigate to CV Magic tab
      _navigateToCVMagicTab();
    } catch (e) {
      debugPrint('⚠️ [CV_GENERATION] Error clearing results: $e');
      // Still try to navigate even if clearing fails
      _navigateToCVMagicTab();
    }
    // Navigate back to CV Magic tab and clear results
    if (mounted) {
      // Show notification
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
              '🔄 Navigating to CV Magic tab. Previous results cleared for fresh analysis with tailored CV.'),
          backgroundColor: Colors.blue,
          duration: Duration(seconds: 4),
        ),
      );

      // Navigate to CV Magic tab (index 1) and clear results
      _navigateToCVMagicTab();
    }
  }

  void _navigateToCVMagicTab() {
    debugPrint('🔀 [CV_GENERATION] Navigating to CV Magic tab');
    // Use the callback to navigate to CV Magic tab
    if (widget.onNavigateToCVMagic != null) {
      widget.onNavigateToCVMagic!();
      debugPrint(
          '✅ Navigated to CV Magic tab - clearing should happen in CV Magic tab');
    } else {
      debugPrint('❌ No navigation callback provided');
    }
  }

  /// Reset tailored CV results when generating new CV
  void resetTailoredCVResults() {
    debugPrint('🗑️ [CV_GENERATION] Resetting tailored CV results');
    setState(() {
      tailoredCVContent = null;
      _currentCompany = null;
      _isGenerating = false;
      _isEditMode = false;
      _editController.clear();
    });
    debugPrint('✅ [CV_GENERATION] Tailored CV results cleared successfully');
  }

  @override
  void dispose() {
    _editController.dispose();
    _autoSaveTimer?.cancel();
    super.dispose();
  }
}
