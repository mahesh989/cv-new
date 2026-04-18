import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/ai_model.dart';

/// Displays the currently selected AI model with its badge, description,
/// speed/cost metadata, and capability chips.
class CurrentModelCard extends StatelessWidget {
  final AIModel model;

  const CurrentModelCard({super.key, required this.model});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [model.color.withOpacity(0.1), model.color.withOpacity(0.05)],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: model.color.withOpacity(0.3), width: 2),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: model.color, shape: BoxShape.circle),
            child: Icon(model.icon, color: Colors.white, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      model.name,
                      style: AppTheme.bodyMedium.copyWith(
                        fontWeight: FontWeight.bold,
                        color: model.color,
                      ),
                    ),
                    if (model.isRecommended) ...[
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
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
                  model.description,
                  style: AppTheme.bodySmall.copyWith(color: AppTheme.neutralGray600),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Icon(Icons.speed_rounded,
                        size: 14, color: AppTheme.neutralGray500),
                    const SizedBox(width: 4),
                    Text(
                      '${model.speed} • ${model.cost} Cost',
                      style: AppTheme.bodySmall
                          .copyWith(color: AppTheme.neutralGray500),
                    ),
                  ],
                ),
                if (model.capabilities.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 6,
                    runSpacing: 4,
                    children: model.capabilities.map((cap) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: model.color.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                              color: model.color.withOpacity(0.3)),
                        ),
                        child: Text(
                          cap,
                          style: AppTheme.labelSmall.copyWith(
                            color: model.color,
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
          Icon(Icons.check_circle_rounded, color: model.color, size: 24),
        ],
      ),
    );
  }
}
