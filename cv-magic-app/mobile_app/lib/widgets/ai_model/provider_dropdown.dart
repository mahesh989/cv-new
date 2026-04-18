import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Provider definition used by [ProviderDropdown].
class _ProviderOption {
  final String id;
  final String name;
  final IconData icon;
  final Color color;

  const _ProviderOption({
    required this.id,
    required this.name,
    required this.icon,
    required this.color,
  });
}

/// Dropdown for selecting the AI provider.
///
/// Each non-placeholder item includes a "Configure" button that triggers
/// [onConfigureProvider] so the parent can show the API-key dialog.
class ProviderDropdown extends StatelessWidget {
  final String selectedProvider;
  final ValueChanged<String> onProviderChanged;
  final ValueChanged<String> onConfigureProvider;

  const ProviderDropdown({
    super.key,
    required this.selectedProvider,
    required this.onProviderChanged,
    required this.onConfigureProvider,
  });

  static const List<_ProviderOption> _providers = [
    _ProviderOption(
      id: 'select',
      name: 'Select AI Provider',
      icon: Icons.arrow_drop_down_rounded,
      color: AppTheme.neutralGray500,
    ),
    _ProviderOption(
      id: 'openai',
      name: 'OpenAI',
      icon: Icons.auto_awesome_rounded,
      color: AppTheme.primaryCosmic,
    ),
    _ProviderOption(
      id: 'anthropic',
      name: 'Anthropic (Claude)',
      icon: Icons.psychology_alt_rounded,
      color: AppTheme.primaryAurora,
    ),
    _ProviderOption(
      id: 'deepseek',
      name: 'DeepSeek',
      icon: Icons.code_rounded,
      color: AppTheme.primaryEmerald,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<String>(
      value: selectedProvider,
      isExpanded: true,
      menuMaxHeight: 200,
      decoration: InputDecoration(
        labelText: 'Select AI Provider',
        prefixIcon: const Icon(Icons.cloud_rounded),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      items: _providers.map((p) => _buildItem(p)).toList(),
      onChanged: (value) {
        if (value != null && value != selectedProvider) {
          onProviderChanged(value);
        }
      },
    );
  }

  DropdownMenuItem<String> _buildItem(_ProviderOption p) {
    final isPlaceholder = p.id == 'select';
    return DropdownMenuItem<String>(
      value: p.id,
      child: Row(
        children: [
          Icon(p.icon, color: p.color, size: 18),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              p.name,
              style: AppTheme.bodySmall.copyWith(
                fontWeight: FontWeight.w600,
                color: isPlaceholder ? AppTheme.neutralGray500 : null,
              ),
              overflow: TextOverflow.ellipsis,
              maxLines: 1,
            ),
          ),
          if (!isPlaceholder)
            TextButton(
              onPressed: () => onConfigureProvider(p.id),
              style: TextButton.styleFrom(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                minimumSize: Size.zero,
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              child: Text(
                'Configure',
                style: AppTheme.labelSmall.copyWith(
                  color: AppTheme.primaryTeal,
                  fontSize: 10,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
