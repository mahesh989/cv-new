import 'package:flutter/material.dart';
import 'cv_action_buttons.dart';

/// Formats raw tailored CV text for display.
///
/// Strips metadata headers and adds visual decorators (emoji prefixes,
/// section borders, etc.) to make the monospace output more readable.
String formatTailoredCVContent(String content) {
  final lines = content.split('\n');
  final formattedLines = <String>[];

  for (final line in lines) {
    if (line.trim().isEmpty) {
      formattedLines.add('');
      continue;
    }

    // Skip metadata header section
    if (line.contains('TAILORED CV TEXT') ||
        line.contains('Target Company:') ||
        line.contains('Generated:') ||
        line.contains('ATS Score:') ||
        line.contains('Framework Version:') ||
        line.contains('CV GENERATION METADATA') ||
        line.startsWith('===') ||
        line.startsWith('=')) {
      continue;
    }

    // Format section headers (all-caps lines)
    if (line == line.toUpperCase() && line.length > 3 && !line.contains('•')) {
      formattedLines.add('');
      formattedLines.add('┌─ $line ─${'─' * (70 - line.length)}');
      formattedLines.add('');
      continue;
    }

    // Format bullet points
    if (line.startsWith('•')) {
      formattedLines.add('  $line');
      continue;
    }

    // Format lines with date ranges (job titles / tenure)
    if (line.contains(' – ') ||
        line.contains(' - ') ||
        line.contains('Present') ||
        line.contains('2024') ||
        line.contains('2023') ||
        line.contains('2022') ||
        line.contains('2021') ||
        line.contains('2020')) {
      formattedLines.add('');
      formattedLines.add('📅 $line');
      formattedLines.add('');
      continue;
    }

    // Format location lines (company names with cities / countries)
    if (line.contains(',') &&
        (line.contains('Australia') ||
            line.contains('France') ||
            line.contains('Sydney') ||
            line.contains('Victoria') ||
            line.contains('Cergy'))) {
      formattedLines.add('🏢 $line');
      formattedLines.add('');
      continue;
    }

    // Format education entries
    if (line.contains('University') ||
        line.contains('Master') ||
        line.contains('PhD')) {
      formattedLines.add('');
      formattedLines.add('🎓 $line');
      continue;
    }

    // Format contact information
    if (line.contains('@') ||
        line.contains('|') ||
        line.contains('LinkedIn') ||
        line.contains('GitHub') ||
        line.contains('Portfolio')) {
      formattedLines.add('📧 $line');
      continue;
    }

    formattedLines.add(line);
  }

  return formattedLines.join('\n');
}

/// Displays the tailored CV content in a dark monospace preview pane.
///
/// Handles three states: loading spinner, edit mode (editable [TextField]),
/// and read-only mode ([SelectableText]).
class CVPreviewWidget extends StatelessWidget {
  final bool isLoadingCV;
  final String? tailoredCVContent;
  final bool isEditMode;
  final TextEditingController editController;
  final ValueChanged<String> onContentChanged;
  final VoidCallback onToggleEditMode;
  final VoidCallback onAdditionalPrompt;
  final VoidCallback onRunATSAgain;

  const CVPreviewWidget({
    super.key,
    required this.isLoadingCV,
    required this.tailoredCVContent,
    required this.isEditMode,
    required this.editController,
    required this.onContentChanged,
    required this.onToggleEditMode,
    required this.onAdditionalPrompt,
    required this.onRunATSAgain,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoadingCV) {
      return const Center(child: CircularProgressIndicator());
    }
    if (tailoredCVContent == null) {
      return const SizedBox.shrink();
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.preview, color: Colors.blue),
              const SizedBox(width: 8),
              const Text(
                'Tailored CV Preview',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            width: double.infinity,
            height: 300,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[900],
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.grey[700]!),
            ),
            child: SingleChildScrollView(
              child: isEditMode
                  ? _buildEditableContent()
                  : SelectableText(
                      formatTailoredCVContent(tailoredCVContent!),
                      style: TextStyle(
                        fontSize: 13,
                        height: 1.6,
                        fontFamily: 'monospace',
                        color: Colors.grey[100],
                      ),
                    ),
            ),
          ),
          const SizedBox(height: 16),
          CVActionButtons(
            isEditMode: isEditMode,
            onToggleEditMode: onToggleEditMode,
            onAdditionalPrompt: onAdditionalPrompt,
            onRunATSAgain: onRunATSAgain,
          ),
        ],
      ),
    );
  }

  Widget _buildEditableContent() {
    return TextField(
      controller: editController,
      maxLines: null,
      style: TextStyle(fontSize: 13, height: 1.6, fontFamily: 'monospace', color: Colors.grey[100]),
      decoration: const InputDecoration(
        border: InputBorder.none,
        hintText: 'Edit your CV content here...',
        hintStyle: TextStyle(color: Colors.grey),
      ),
      onChanged: onContentChanged,
    );
  }
}
