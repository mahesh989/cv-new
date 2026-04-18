import 'package:flutter/material.dart';

/// Three-button action row shown beneath the tailored CV preview:
/// Edit/Save toggle, Additional Prompt, and Run ATS Again.
class CVActionButtons extends StatelessWidget {
  final bool isEditMode;
  final VoidCallback onToggleEditMode;
  final VoidCallback onAdditionalPrompt;
  final VoidCallback onRunATSAgain;

  const CVActionButtons({
    super.key,
    required this.isEditMode,
    required this.onToggleEditMode,
    required this.onAdditionalPrompt,
    required this.onRunATSAgain,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: onToggleEditMode,
            icon: Icon(isEditMode ? Icons.save : Icons.edit),
            label: Text(isEditMode ? 'Save' : 'Edit'),
            style: ElevatedButton.styleFrom(
              backgroundColor: isEditMode ? Colors.green : Colors.blue,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 12),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: ElevatedButton.icon(
            onPressed: onAdditionalPrompt,
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
        Expanded(
          child: ElevatedButton.icon(
            onPressed: onRunATSAgain,
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
}
