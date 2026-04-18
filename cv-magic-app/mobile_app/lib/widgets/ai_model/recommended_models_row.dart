import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/ai_model.dart';

/// Horizontal scrollable row of recommended model chips.
///
/// The currently selected model is highlighted with its brand colour.
class RecommendedModelsRow extends StatelessWidget {
  final List<AIModel> models;
  final String currentModelId;
  final ValueChanged<String> onModelChanged;

  const RecommendedModelsRow({
    super.key,
    required this.models,
    required this.currentModelId,
    required this.onModelChanged,
  });

  @override
  Widget build(BuildContext context) {
    if (models.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.star_rounded, color: Colors.orange, size: 18),
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
            children: models.map((model) {
              final isSelected = model.id == currentModelId;
              return Padding(
                padding: const EdgeInsets.only(right: 12),
                child: GestureDetector(
                  onTap: isSelected ? null : () => onModelChanged(model.id),
                  child: Container(
                    width: 140,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      gradient: isSelected
                          ? LinearGradient(colors: [
                              model.color,
                              model.color.withOpacity(0.8),
                            ])
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
}
