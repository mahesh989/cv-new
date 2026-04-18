import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';
import '../services/results_clearing_service.dart';
import '../core/config/app_config.dart';
import '../widgets/cv_generation/cv_header_card.dart';
import '../widgets/cv_generation/cv_generation_card.dart';
import '../services/auth_service.dart';

class CVGenerationScreen extends StatefulWidget {
  final VoidCallback? onNavigateToCVMagic;
  final VoidCallback? onNavigateToCVMagicWithoutClearing;

  const CVGenerationScreen({
    super.key,
    this.onNavigateToCVMagic,
    this.onNavigateToCVMagicWithoutClearing,
  });

  @override
  State<CVGenerationScreen> createState() => _CVGenerationScreenState();
}

class _CVGenerationScreenState extends State<CVGenerationScreen> {
  bool _isGenerating = false;
  bool _isEditMode = false;
  bool _isLoadingCV = false;
  String? _currentCompany;
  String? tailoredCVContent;
  final TextEditingController _editController = TextEditingController();
  Timer? _autoSaveTimer;

  @override
  void initState() {
    super.initState();
    _loadTailoredCV();
  }

  @override
  void dispose() {
    _editController.dispose();
    _autoSaveTimer?.cancel();
    super.dispose();
  }

  // ── Build ──────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const CVHeaderCard(),
          const SizedBox(height: 20),
          CVGenerationCard(
            isGenerating: _isGenerating,
            tailoredCVContent: tailoredCVContent,
            isLoadingCV: _isLoadingCV,
            isEditMode: _isEditMode,
            editController: _editController,
            onGenerate: _loadTailoredCV,
            onClear: _clearCV,
            onContentChanged: _onContentChanged,
            onToggleEditMode: _toggleEditMode,
            onAdditionalPrompt: _showAdditionalPromptDialog,
            onRunATSAgain: _runATSAgain,
          ),
        ],
      ),
    );
  }

  // ── Data loading ───────────────────────────────────────────────────────────

  Future<void> _loadTailoredCV() async {
    setState(() {
      _isLoadingCV = true;
      _isGenerating = true;
      tailoredCVContent = null;
    });

    try {
      final token = await authService.getIdToken();

      if (token == null) {
        _setContent('Please log in to view your tailored CVs');
        return;
      }

      final headers = {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };

      final companiesResponse = await http.get(
        Uri.parse('${AppConfig.baseUrl}/api/tailored-cv/available-companies-real'),
        headers: headers,
      );

      if (companiesResponse.statusCode == 200) {
        final companies = List<Map<String, dynamic>>.from(
          json.decode(companiesResponse.body)['companies'] ?? [],
        );

        if (companies.isEmpty) {
          _setContent('No tailored CVs available for your account');
          return;
        }

        companies.sort((a, b) => b['last_updated'].compareTo(a['last_updated']));
        final companyName = companies.first['company'] as String;

        final response = await http.get(
          Uri.parse('${AppConfig.baseUrl}/api/tailored-cv/content/$companyName'),
          headers: headers,
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          setState(() {
            tailoredCVContent = data['content'] ?? 'No content available';
            _currentCompany = data['company'] ?? companyName;
          });
        } else if (response.statusCode == 401) {
          _setContent('Your session has expired. Please log in again.');
        } else {
          _setContent('Failed to load tailored CV. Status: ${response.statusCode}');
        }
      } else if (companiesResponse.statusCode == 401) {
        _setContent('Your session has expired. Please log in again.');
      } else {
        _setContent(
            'Failed to get companies list. Status: ${companiesResponse.statusCode}');
      }
    } catch (e) {
      _setContent('Error loading tailored CV: $e');
    } finally {
      setState(() {
        _isLoadingCV = false;
        _isGenerating = false;
      });
    }
  }

  void _setContent(String message) {
    setState(() => tailoredCVContent = message);
  }

  void _clearCV() {
    setState(() {
      tailoredCVContent = null;
      _isLoadingCV = false;
      _isGenerating = false;
    });
  }

  // ── Edit mode ──────────────────────────────────────────────────────────────

  void _toggleEditMode() {
    setState(() {
      if (_isEditMode) {
        tailoredCVContent = _editController.text;
        _saveEditedContent();
      } else {
        _editController.text = tailoredCVContent ?? '';
      }
      _isEditMode = !_isEditMode;
    });
  }

  void _onContentChanged(String value) {
    if (_isEditMode) {
      tailoredCVContent = value;
      _debounceAutoSave();
    }
  }

  void _debounceAutoSave() {
    _autoSaveTimer?.cancel();
    _autoSaveTimer = Timer(const Duration(seconds: 2), _saveEditedContent);
  }

  Future<void> _saveEditedContent() async {
    if (_currentCompany == null || tailoredCVContent == null) return;

    try {
      final token = await authService.getIdToken();

      final response = await http.post(
        Uri.parse('${AppConfig.baseUrl}/api/tailored-cv/save-edited'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'company': _currentCompany,
          'content': tailoredCVContent,
        }),
      );

      if (response.statusCode == 200 && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('CV saved successfully!'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving CV: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  // ── Additional prompt ──────────────────────────────────────────────────────

  void _showAdditionalPromptDialog() {
    final promptController = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
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
      ),
    );
  }

  Future<void> _saveAdditionalPrompt(String promptText) async {
    if (promptText.trim().isEmpty || _currentCompany == null) return;

    try {
      final response = await http.post(
        Uri.parse('${AppConfig.baseUrl}/api/tailored-cv/save-additional-prompt'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'company': _currentCompany,
          'prompt': promptText.trim(),
        }),
      );

      if (response.statusCode == 200 && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Additional prompt saved successfully!'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving prompt: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    }
  }

  // ── ATS / Navigation ───────────────────────────────────────────────────────

  void _runATSAgain() async {
    try {
      await ResultsClearingService.clearAnalysisResultsOnly();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
                'Analysis results cleared, JD inputs preserved. Navigating to CV Magic tab.'),
            backgroundColor: Colors.blue,
            duration: Duration(seconds: 4),
          ),
        );
      }
      _navigateToCVMagicTabWithoutClearing();
    } catch (_) {
      _navigateToCVMagicTab();
    }
  }

  void _navigateToCVMagicTab() => widget.onNavigateToCVMagic?.call();

  void _navigateToCVMagicTabWithoutClearing() =>
      widget.onNavigateToCVMagicWithoutClearing?.call();

  /// Resets all tailored CV state (called externally when generating a new CV).
  void resetTailoredCVResults() {
    setState(() {
      tailoredCVContent = null;
      _currentCompany = null;
      _isGenerating = false;
      _isEditMode = false;
      _editController.clear();
    });
  }
}
