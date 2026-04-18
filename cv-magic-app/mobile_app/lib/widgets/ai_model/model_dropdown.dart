import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/ai_model.dart';

/// Dropdown listing every available AI model for selection.
class ModelDropdown extends StatelessWidget {
  final List<AIModel> models;
  final String currentModelId;
  final ValueChanged<String> onModelChanged;

  const ModelDropdown({
    super.key,
    required this.models,
    required this.currentModelId,
    required this.onModelChanged,
  });

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      value: currentModelId,
      isExpanded: true,
      menuMaxHeight: 400,
      decoration: InputDecoration(
        labelText: 'Select AI Model',
        prefixIcon: const Icon(Icons.psychology_rounded),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      items: models.map((model) {
        return DropdownMenuItem<String>(
          value: model.id,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              children: [
                Icon(model.icon, color: model.color, size: 18),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    model.isRecommended ? '${model.name} ⭐' : model.name,
                    style: AppTheme.bodySmall
                        .copyWith(fontWeight: FontWeight.w600),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
      onChanged: (value) {
        if (value != null && value != currentModelId) {
          onModelChanged(value);
        }
      },
    );
  }
}
