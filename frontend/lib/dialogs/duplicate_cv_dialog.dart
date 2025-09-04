import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class DuplicateCVDialog extends StatelessWidget {
  final String proposedName;
  final Map<String, dynamic> existingCV;
  final Function(String) onReplace;
  final Function(String) onNewVersion;
  final VoidCallback onCancel;

  const DuplicateCVDialog({
    super.key,
    required this.proposedName,
    required this.existingCV,
    required this.onReplace,
    required this.onNewVersion,
    required this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.warning_amber_rounded, color: AppTheme.warningOrange),
          const SizedBox(width: 8),
          const Text('Duplicate CV Name'),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'A CV with the name "$proposedName" already exists:',
            style: AppTheme.bodyMedium,
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.neutralGray50,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppTheme.neutralGray200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Company: ${existingCV['company'] ?? 'N/A'}'),
                Text('Role: ${existingCV['role'] ?? 'N/A'}'),
                Text('Date: ${existingCV['date_applied'] ?? 'N/A'}'),
                if (existingCV['ats_score'] != null)
                  Text('ATS Score: ${existingCV['ats_score']}/100'),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'What would you like to do?',
            style: AppTheme.bodyMedium.copyWith(fontWeight: FontWeight.bold),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: onCancel,
          child: const Text('Cancel'),
        ),
        ElevatedButton.icon(
          onPressed: () => onNewVersion(proposedName),
          icon: const Icon(Icons.add),
          label: const Text('Create New Version'),
          style: AppTheme.primaryButtonStyle,
        ),
        ElevatedButton.icon(
          onPressed: () => onReplace(proposedName),
          icon: const Icon(Icons.refresh),
          label: const Text('Replace Existing'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppTheme.warningOrange,
            foregroundColor: Colors.white,
          ),
        ),
      ],
    );
  }
}
