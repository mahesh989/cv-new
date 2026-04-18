import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../core/theme/app_theme.dart';
import '../models/ai_model.dart';
import '../services/ai_model_service.dart';
import 'api_key_input_dialog.dart';
import 'ai_model/ai_model_header.dart';
import 'ai_model/current_model_card.dart';
import 'ai_model/provider_dropdown.dart';
import 'ai_model/model_dropdown.dart';
import 'ai_model/recommended_models_row.dart';
import 'ai_model/model_info_card.dart';

class AIModelSelector extends StatefulWidget {
  final VoidCallback? onModelChanged;
  final bool isExpanded;

  const AIModelSelector({
    super.key,
    this.onModelChanged,
    this.isExpanded = true,
  });

  @override
  State<AIModelSelector> createState() => _AIModelSelectorState();
}

class _AIModelSelectorState extends State<AIModelSelector>
    with SingleTickerProviderStateMixin {
  bool _isExpanded = true;
  String _selectedProvider = 'select';

  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _isExpanded = widget.isExpanded;
    _animationController = AnimationController(
      duration: AppTheme.normalAnimation,
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: AppTheme.smoothCurve),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  // ── Helpers ────────────────────────────────────────────────────────────────

  String _getProviderFromModel(String modelId) {
    if (modelId.startsWith('gpt-')) return 'openai';
    if (modelId.startsWith('claude-')) return 'anthropic';
    if (modelId.startsWith('deepseek-')) return 'deepseek';
    return 'unknown';
  }

  String _getProviderDisplayName(String provider) {
    switch (provider) {
      case 'openai':
        return 'OpenAI';
      case 'anthropic':
        return 'Anthropic (Claude)';
      case 'deepseek':
        return 'DeepSeek';
      default:
        return provider;
    }
  }

  // ── Actions ────────────────────────────────────────────────────────────────

  Future<void> _changeModel(String modelId) async {
    final aiModelService = Provider.of<AIModelService>(context, listen: false);
    await aiModelService.changeModel(modelId);
    widget.onModelChanged?.call();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content:
              Text('Switched to ${aiModelService.currentModel?.name ?? 'Unknown'}'),
          backgroundColor: AppTheme.primaryTeal,
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  void _changeProvider(String provider) {
    setState(() => _selectedProvider = provider);
    if (provider == 'select') return;
    _showAPIKeyDialog(provider);
  }

  void _showAPIKeyDialog(String provider) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => APIKeyInputDialog(
        provider: provider,
        providerDisplayName: _getProviderDisplayName(provider),
        onSuccess: () async {
          // Switch to the first model from this provider after key is saved.
          final svc = Provider.of<AIModelService>(context, listen: false);
          final providerModels = svc
              .getAllModels()
              .where((m) => _getProviderFromModel(m.id) == provider)
              .toList();
          if (providerModels.isNotEmpty) {
            await _changeModel(providerModels.first.id);
            setState(() => _selectedProvider = provider);
          }
        },
        onCancel: () {},
      ),
    );
  }

  // ── Build ──────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Consumer<AIModelService>(
      builder: (context, aiModelService, _) {
        if (!aiModelService.isInitialized) {
          return AppTheme.createCard(
            child: const Center(
              child: SpinKitFadingCircle(color: AppTheme.primaryTeal, size: 24),
            ),
          );
        }

        final currentModel = aiModelService.currentModel;
        if (currentModel == null) {
          return _buildSelectionPrompt();
        }

        return AnimatedBuilder(
          animation: _animationController,
          builder: (_, __) => FadeTransition(
            opacity: _fadeAnimation,
            child: AppTheme.createCard(
              child: Column(
                children: [
                  AIModelHeader(
                    currentModel: currentModel,
                    isExpanded: _isExpanded,
                    onToggle: () => setState(() => _isExpanded = !_isExpanded),
                  ),
                  if (_isExpanded)
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Column(
                        children: [
                          const Divider(color: AppTheme.neutralGray200),
                          const SizedBox(height: 16),
                          CurrentModelCard(model: currentModel),
                          const SizedBox(height: 16),
                          ProviderDropdown(
                            selectedProvider: _selectedProvider,
                            onProviderChanged: _changeProvider,
                            onConfigureProvider: _showAPIKeyDialog,
                          ),
                          const SizedBox(height: 16),
                          ModelDropdown(
                            models: aiModelService.getAllModels(),
                            currentModelId: currentModel.id,
                            onModelChanged: _changeModel,
                          ),
                          const SizedBox(height: 16),
                          RecommendedModelsRow(
                            models: aiModelService.getRecommendedModels(),
                            currentModelId: currentModel.id,
                            onModelChanged: _changeModel,
                          ),
                          const SizedBox(height: 16),
                          const ModelInfoCard(),
                          const SizedBox(height: 16),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSelectionPrompt() {
    return AppTheme.createCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(Icons.smart_toy_rounded,
                size: 48, color: AppTheme.neutralGray400),
            const SizedBox(height: 16),
            Text(
              '🤖 AI Model Configuration',
              style: AppTheme.headingSmall.copyWith(
                color: AppTheme.primaryCosmic,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Please select a provider and configure your API key to use AI features',
              style:
                  AppTheme.bodySmall.copyWith(color: AppTheme.neutralGray600),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ProviderDropdown(
              selectedProvider: _selectedProvider,
              onProviderChanged: _changeProvider,
              onConfigureProvider: _showAPIKeyDialog,
            ),
          ],
        ),
      ),
    );
  }
}
