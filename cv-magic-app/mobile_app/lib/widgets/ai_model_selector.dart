import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import '../core/theme/app_theme.dart';
import '../models/ai_model.dart';
import '../services/ai_model_service.dart';

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

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: AppTheme.smoothCurve,
    ));

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _changeModel(String modelId) async {
    final aiModelService = Provider.of<AIModelService>(context, listen: false);
    await aiModelService.changeModel(modelId);

    if (widget.onModelChanged != null) {
      widget.onModelChanged!();
    }

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            '✅ Switched to ${aiModelService.currentModel.name}',
          ),
          backgroundColor: AppTheme.primaryTeal,
          behavior: SnackBarBehavior.floating,
          duration: const Duration(seconds: 2),
        ),
      );
    }
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AIModelService>(
      builder: (context, aiModelService, child) {
        if (!aiModelService.isInitialized) {
          return AppTheme.createCard(
            child: const Center(
              child: SpinKitFadingCircle(
                color: AppTheme.primaryTeal,
                size: 24,
              ),
            ),
          );
        }

        final currentModel = aiModelService.currentModel;
        final allModels = aiModelService.getAllModels();
        final recommendedModels = aiModelService.getRecommendedModels();

        return AnimatedBuilder(
          animation: _animationController,
          builder: (context, child) {
            return FadeTransition(
              opacity: _fadeAnimation,
              child: AppTheme.createCard(
                child: Column(
                  children: [
                    _buildHeader(currentModel),
                    if (_isExpanded) ...[
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        child: Column(
                          children: [
                            const Divider(color: AppTheme.neutralGray200),
                            const SizedBox(height: 16),
                            _buildCurrentModelDisplay(currentModel),
                            const SizedBox(height: 16),
                            _buildModelDropdown(allModels, currentModel.id),
                            const SizedBox(height: 16),
                            _buildRecommendedModels(recommendedModels, currentModel.id),
                            const SizedBox(height: 16),
                            _buildModelInfo(),
                            const SizedBox(height: 16),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildHeader(AIModel currentModel) {
    return InkWell(
      onTap: _toggleExpanded,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                gradient: AppTheme.cosmicGradient,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryCosmic.withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Icon(
                Icons.smart_toy_rounded,
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
                    '🤖 AI Model Configuration',
                    style: AppTheme.headingSmall.copyWith(
                      color: AppTheme.primaryCosmic,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Currently using: ${currentModel.name}',
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
              size: 28,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCurrentModelDisplay(AIModel currentModel) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            currentModel.color.withOpacity(0.1),
            currentModel.color.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: currentModel.color.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: currentModel.color,
              shape: BoxShape.circle,
            ),
            child: Icon(
              currentModel.icon,
              color: Colors.white,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      currentModel.name,
                      style: AppTheme.bodyMedium.copyWith(
                        fontWeight: FontWeight.bold,
                        color: currentModel.color,
                      ),
                    ),
                    if (currentModel.isRecommended) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.orange,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'RECOMMENDED',
                          style: AppTheme.labelSmall.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  currentModel.description,
                  style: AppTheme.bodySmall.copyWith(
                    color: AppTheme.neutralGray600,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(
                      Icons.speed_rounded,
                      size: 14,
                      color: AppTheme.neutralGray500,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${currentModel.speed} • ${currentModel.cost} Cost',
                      style: AppTheme.bodySmall.copyWith(
                        color: AppTheme.neutralGray500,
                      ),
                    ),
                  ],
                ),
                if (currentModel.capabilities.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 6,
                    runSpacing: 4,
                    children: currentModel.capabilities.map((capability) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: currentModel.color.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: currentModel.color.withOpacity(0.3),
                          ),
                        ),
                        child: Text(
                          capability,
                          style: AppTheme.labelSmall.copyWith(
                            color: currentModel.color,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ],
            ),
          ),
          Icon(
            Icons.check_circle_rounded,
            color: currentModel.color,
            size: 24,
          ),
        ],
      ),
    );
  }

  Widget _buildModelDropdown(List<AIModel> allModels, String currentModelId) {
    return DropdownButtonFormField<String>(
      value: currentModelId,
      isExpanded: true,
      menuMaxHeight: 200,
      decoration: InputDecoration(
        labelText: 'Select AI Model',
        prefixIcon: const Icon(Icons.psychology_rounded),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 12,
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
                size: 18,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  model.isRecommended 
                    ? '${model.name} ⭐'
                    : model.name,
                  style: AppTheme.bodySmall.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              ),
            ],
          ),
        );
      }).toList(),
      onChanged: (String? newValue) {
        if (newValue != null && newValue != currentModelId) {
          _changeModel(newValue);
        }
      },
    );
  }

  Widget _buildRecommendedModels(
      List<AIModel> recommendedModels, String currentModelId) {
    if (recommendedModels.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(
              Icons.star_rounded,
              color: Colors.orange,
              size: 18,
            ),
            const SizedBox(width: 8),
            Text(
              'Recommended Models',
              style: AppTheme.labelMedium.copyWith(
                fontWeight: FontWeight.bold,
                color: AppTheme.neutralGray700,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: recommendedModels.map((model) {
              final isSelected = model.id == currentModelId;
              return Padding(
                padding: const EdgeInsets.only(right: 12),
                child: GestureDetector(
                  onTap: () {
                    if (!isSelected) {
                      _changeModel(model.id);
                    }
                  },
                  child: Container(
                    width: 140,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      gradient: isSelected
                          ? LinearGradient(
                              colors: [model.color, model.color.withOpacity(0.8)]
                            )
                          : null,
                      color: isSelected ? null : AppTheme.neutralGray50,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: isSelected
                            ? model.color
                            : AppTheme.neutralGray300,
                        width: isSelected ? 2 : 1,
                      ),
                    ),
                    child: Column(
                      children: [
                        Icon(
                          model.icon,
                          color: isSelected ? Colors.white : model.color,
                          size: 20,
                        ),
                        const SizedBox(height: 6),
                        Text(
                          model.name,
                          style: AppTheme.labelSmall.copyWith(
                            color: isSelected
                                ? Colors.white
                                : AppTheme.neutralGray700,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          model.provider,
                          style: AppTheme.labelSmall.copyWith(
                            color: isSelected
                                ? Colors.white.withOpacity(0.9)
                                : AppTheme.neutralGray500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildModelInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: AppTheme.cosmicGradient.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppTheme.primaryCosmic.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.info_outline_rounded,
                color: AppTheme.primaryCosmic,
                size: 18,
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
          const SizedBox(height: 12),
          Text(
            '• The selected model will be used for all AI operations\n'
            '• GPT models are fast and versatile for most tasks\n'
            '• Claude models excel at analysis and reasoning\n'
            '• DeepSeek models offer excellent performance at low cost\n'
            '• You can change the model anytime from this screen',
            style: AppTheme.bodySmall.copyWith(
              color: AppTheme.neutralGray700,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }
}
