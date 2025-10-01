///
/// CV Preview Module
///
/// Handles CV content extraction and preview functionality.
///

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../core/config/environment_config.dart';

class CVPreviewModule extends StatefulWidget {
  final String? selectedCVFilename;

  const CVPreviewModule({
    super.key,
    required this.selectedCVFilename,
  });

  @override
  State<CVPreviewModule> createState() => _CVPreviewModuleState();
}

class _CVPreviewModuleState extends State<CVPreviewModule> {
  String? cvContent;
  bool isLoadingContent = false;

  @override
  void initState() {
    super.initState();
    if (widget.selectedCVFilename != null) {
      _loadCVContent(widget.selectedCVFilename!);
    }
  }

  @override
  void didUpdateWidget(CVPreviewModule oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.selectedCVFilename != oldWidget.selectedCVFilename) {
      if (widget.selectedCVFilename != null) {
        _loadCVContent(widget.selectedCVFilename!);
      } else {
        setState(() {
          cvContent = null;
        });
      }
    }
  }

  Future<void> _loadCVContent(String filename) async {
    setState(() {
      isLoadingContent = true;
    });

    try {
      final response = await http
          .get(Uri.parse('EnvironmentConfig.baseUrl/api/cv/content/$filename'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          cvContent = data['content'];
        });
      } else {
        setState(() {
          cvContent = 'Failed to load CV content';
        });
      }
    } catch (e) {
      setState(() {
        cvContent = 'Error loading CV content: $e';
      });
    } finally {
      setState(() {
        isLoadingContent = false;
      });
    }
  }

  // Removed auto-save for analysis here; saving now happens on explicit selection

  String _formatCVContent(String content) {
    if (content.isEmpty) return content;

    // Split content into lines
    List<String> lines = content.split('\n');
    List<String> formattedLines = [];

    for (int i = 0; i < lines.length; i++) {
      String line = lines[i].trim();

      // Skip empty lines
      if (line.isEmpty) {
        formattedLines.add('');
        continue;
      }

      // Format section headers (all caps words)
      if (line == line.toUpperCase() &&
          line.length > 3 &&
          !line.contains('•')) {
        formattedLines.add('');
        formattedLines.add('┌─ ' + line + ' ─' + '─' * (70 - line.length));
        formattedLines.add('');
        continue;
      }

      // Format bullet points
      if (line.startsWith('•')) {
        formattedLines.add('  ' + line);
        continue;
      }

      // Format job titles (lines ending with date ranges)
      if (line.contains(' – ') ||
          line.contains(' - ') ||
          (line.contains('Present') ||
              line.contains('2024') ||
              line.contains('2023') ||
              line.contains('2022') ||
              line.contains('2021') ||
              line.contains('2020'))) {
        formattedLines.add('');
        formattedLines.add('📅 ' + line);
        formattedLines.add('');
        continue;
      }

      // Format company names (lines that might be company names)
      if (line.contains(',') &&
          (line.contains('Australia') ||
              line.contains('France') ||
              line.contains('Sydney') ||
              line.contains('Victoria') ||
              line.contains('Cergy'))) {
        formattedLines.add('🏢 ' + line);
        formattedLines.add('');
        continue;
      }

      // Format education entries
      if (line.contains('University') ||
          line.contains('Master') ||
          line.contains('PhD')) {
        formattedLines.add('');
        formattedLines.add('🎓 ' + line);
        continue;
      }

      // Format contact information
      if (line.contains('@') ||
          line.contains('|') ||
          line.contains('LinkedIn') ||
          line.contains('GitHub') ||
          line.contains('Portfolio')) {
        formattedLines.add('📧 ' + line);
        continue;
      }

      // Regular content
      formattedLines.add(line);
    }

    return formattedLines.join('\n');
  }

  @override
  Widget build(BuildContext context) {
    if (widget.selectedCVFilename == null) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.preview, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  'CV Preview: ${widget.selectedCVFilename ?? ""}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (isLoadingContent)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: CircularProgressIndicator(),
                ),
              )
            else if (cvContent != null)
              Container(
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
                        Icon(
                          Icons.file_copy,
                          color: Colors.blue,
                          size: 16,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'CV Content',
                          style: TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 14,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          '${cvContent!.length} characters',
                          style:
                              TextStyle(color: Colors.grey[600], fontSize: 12),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Container(
                      width: double.infinity,
                      height: 300,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.grey[900], // Black background like mt2
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.grey[700]!),
                      ),
                      child: SingleChildScrollView(
                        child: SelectableText(
                          _formatCVContent(cvContent!),
                          style: TextStyle(
                            fontSize: 13,
                            height: 1.6,
                            fontFamily: 'monospace', // Monospace font like mt2
                            color: Colors.grey[100], // Light text like mt2
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              )
            else
              Container(
                width: double.infinity,
                height: 100,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey[300]!),
                ),
                child: const Center(
                  child: Text(
                    'Select a CV to view its content',
                    style: TextStyle(
                      color: Colors.grey,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class CVPreviewService {
  /// Load CV content from backend
  static Future<String?> loadCVContent(String filename) async {
    try {
      final response = await http
          .get(Uri.parse('EnvironmentConfig.baseUrl/api/cv/content/$filename'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['content'];
      }
    } catch (e) {
      debugPrint('Error loading CV content: $e');
    }
    return null;
  }

  /// Load CV preview from backend
  static Future<Map<String, dynamic>?> loadCVPreview(String filename,
      {int maxLength = 500}) async {
    try {
      final response = await http.get(Uri.parse(
          'EnvironmentConfig.baseUrl/api/cv/preview/$filename?max_length=$maxLength'));
      if (response.statusCode == 200) {
        return json.decode(response.body);
      }
    } catch (e) {
      debugPrint('Error loading CV preview: $e');
    }
    return null;
  }
}
