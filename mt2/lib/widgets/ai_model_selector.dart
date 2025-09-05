import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../services/ai_model_service.dart';

class AIModelSelector extends StatefulWidget {
  final VoidCallback? onModelChanged;

  const AIModelSelector({
    super.key,
    this.onModelChanged,
  });

  @override
  State<AIModelSelector> createState() => _AIModelSelectorState();
}

class _AIModelSelectorState extends State<AIModelSelector> {
  final AIModelService _aiModelService = AIModelService();
  bool _isExpanded = true;

  @override
  void initState() {
    super.initState();
    _initializeService();
  }

  Future<void> _initializeService() async {
    await _aiModelService.initialize();
    setState(() {});
  }

  Future<void> _changeModel(String modelId) async {
    await _aiModelService.changeModel(modelId);
    setState(() {});

    if (widget.onModelChanged != null) {
      widget.onModelChanged!();
    }
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
    });
  }

  @override
  Widget build(BuildContext context) {
    final currentModel = _aiModelService.currentModel;
    final allModels = _aiModelService.getAllModels();

    return AppTheme.createCard(
      child: SingleChildScrollView(
        child: Column(
          children: [
            // Header with toggle functionality
            InkWell(
              onTap: _toggleExpanded,
              borderRadius: BorderRadius.circular(12),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        gradient: AppTheme.cosmicGradient,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.smart_toy_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '🤖 AI Model Configuration',
                            style: AppTheme.headingSmall.copyWith(
                              color: AppTheme.primaryCosmic,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Select AI model for all tasks',
                            style: AppTheme.bodySmall.copyWith(
                              color: AppTheme.neutralGray600,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      _isExpanded ? Icons.expand_less : Icons.expand_more,
                      color: AppTheme.primaryCosmic,
                    ),
                  ],
                ),
              ),
            ),

            // Expanded content
            if (_isExpanded) ...[
              Container(
                constraints: const BoxConstraints(
                    maxHeight: 600), // Limit overall height
                child: SingleChildScrollView(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                    child: Column(
                      children: [
                        const Divider(),
                        const SizedBox(height: 16),

                        // Current model display
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: currentModel.color.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: currentModel.color.withOpacity(0.3),
                              width: 1,
                            ),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                currentModel.icon,
                                color: currentModel.color,
                                size: 24,
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      currentModel.name,
                                      style: AppTheme.bodyMedium.copyWith(
                                        fontWeight: FontWeight.bold,
                                        color: currentModel.color,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      currentModel.description,
                                      style: AppTheme.bodySmall.copyWith(
                                        color: AppTheme.neutralGray600,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      '${currentModel.speed} • ${currentModel.cost} Cost',
                                      style: AppTheme.bodySmall.copyWith(
                                        color: AppTheme.neutralGray600,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              Icon(
                                Icons.check_circle,
                                color: currentModel.color,
                                size: 20,
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),

                        // Model selector dropdown
                        DropdownButtonFormField<String>(
                          value: _aiModelService.currentModelId,
                          isExpanded: true,
                          menuMaxHeight: 300, // Limit dropdown height
                          decoration: InputDecoration(
                            labelText: 'Select AI Model',
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 8,
                            ),
                          ),
                          items: allModels.map((model) {
                            return DropdownMenuItem<String>(
                              value: model.id,
                              child: Row(
                                children: [
                                  Icon(
                                    model.icon,
                                    color: model.color,
                                    size: 14,
                                  ),
                                  const SizedBox(width: 6),
                                  Expanded(
                                    child: Text(
                                      model.name,
                                      style: AppTheme.bodySmall.copyWith(
                                        fontWeight: FontWeight.w500,
                                      ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                          onChanged: (String? newValue) {
                            if (newValue != null) {
                              _changeModel(newValue);
                            }
                          },
                        ),
                        const SizedBox(height: 16),

                        // Model info section
                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            gradient: AppTheme.cosmicGradient.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: AppTheme.primaryCosmic.withOpacity(0.2),
                              width: 1,
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Icon(
                                    Icons.info_rounded,
                                    color: AppTheme.primaryCosmic,
                                    size: 16,
                                  ),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Model Information',
                                    style: AppTheme.bodyMedium.copyWith(
                                      fontWeight: FontWeight.bold,
                                      color: AppTheme.primaryCosmic,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                '• Claude models are generally more powerful for analysis tasks\n'
                                '• GPT models are faster and more cost-effective\n'
                                '• DeepSeek models offer advanced reasoning and coding capabilities at very low cost\n'
                                '• DeepSeek Reasoner excels at complex analysis tasks\n'
                                '• DeepSeek Coder is specialized for programming-related tasks\n'
                                '• This model will be used for all AI operations in the app',
                                style: AppTheme.bodySmall.copyWith(
                                  color: AppTheme.neutralGray700,
                                  height: 1.4,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
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
