///
/// Optimized CV Preview Module
///
/// This optimized version loads and displays CV content immediately,
/// then triggers the save-for-analysis operation in the background
/// without blocking the UI.
///

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class CVPreviewModuleOptimized extends StatefulWidget {
  final String? selectedCVFilename;

  const CVPreviewModuleOptimized({
    super.key,
    required this.selectedCVFilename,
  });

  @override
  State<CVPreviewModuleOptimized> createState() => _CVPreviewModuleOptimizedState();
}

class _CVPreviewModuleOptimizedState extends State<CVPreviewModuleOptimized> {
  String? cvContent;
  bool isLoadingContent = false;
  bool isSavingForAnalysis = false;
  String? analysisSaveStatus;

  @override
  void initState() {
    super.initState();
    if (widget.selectedCVFilename != null) {
      _loadCVContent(widget.selectedCVFilename!);
    }
  }

  @override
  void didUpdateWidget(CVPreviewModuleOptimized oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.selectedCVFilename != oldWidget.selectedCVFilename) {
      if (widget.selectedCVFilename != null) {
        _loadCVContent(widget.selectedCVFilename!);
      } else {
        setState(() {
          cvContent = null;
          analysisSaveStatus = null;
        });
      }
    }
  }

  Future<void> _loadCVContent(String filename) async {
    setState(() {
      isLoadingContent = true;
      analysisSaveStatus = null;
    });

    try {
      // Load CV content immediately for display
      final response = await http
          .get(Uri.parse('http://localhost:8000/api/cv/content/$filename'))
          .timeout(const Duration(seconds: 5)); // Add timeout for faster response
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // Display content immediately
        setState(() {
          cvContent = data['content'];
          isLoadingContent = false;
        });

        // Trigger background save after content is displayed
        // This runs asynchronously without blocking the UI
        _triggerBackgroundAnalysisSave(filename);
      } else {
        setState(() {
          cvContent = 'Failed to load CV content';
          isLoadingContent = false;
        });
      }
    } catch (e) {
      setState(() {
        cvContent = 'Error loading CV content: $e';
        isLoadingContent = false;
      });
    }
  }

  Future<void> _triggerBackgroundAnalysisSave(String filename) async {
    // Run this completely in the background
    // Don't block on this operation
    setState(() {
      isSavingForAnalysis = true;
      analysisSaveStatus = 'Preparing CV for analysis...';
    });

    // Use a separate isolate/async operation
    Timer.run(() async {
      try {
        // Call the async endpoint that doesn't block
        final response = await http.post(
          Uri.parse('http://localhost:8000/api/cv/save-for-analysis-async/$filename'),
          headers: {'Content-Type': 'application/json'},
        ).timeout(
          const Duration(seconds: 2),
          onTimeout: () {
            // If it takes too long, just continue - it's processing in background
            return http.Response('{"status": "processing"}', 202);
          },
        );

        if (mounted) {
          if (response.statusCode == 200 || response.statusCode == 202) {
            setState(() {
              isSavingForAnalysis = false;
              analysisSaveStatus = 'CV ready for analysis ✓';
            });
            
            // Show brief success message
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('CV prepared for analysis'),
                backgroundColor: Colors.green,
                duration: const Duration(seconds: 1),
              ),
            );
          } else {
            setState(() {
              isSavingForAnalysis = false;
              analysisSaveStatus = 'Analysis preparation pending';
            });
          }
        }
      } catch (e) {
        // Silent fail for background save - don't interrupt user experience
        debugPrint('Background save info: $e');
        if (mounted) {
          setState(() {
            isSavingForAnalysis = false;
            analysisSaveStatus = 'Analysis will be available shortly';
          });
        }
      }
    });
  }

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
            // Header with status indicator
            Row(
              children: [
                const Icon(Icons.preview, color: Colors.blue),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'CV Preview: ${widget.selectedCVFilename ?? ""}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ),
                // Background save status indicator
                if (isSavingForAnalysis)
                  SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade300),
                    ),
                  )
                else if (analysisSaveStatus != null && analysisSaveStatus!.contains('✓'))
                  Icon(Icons.check_circle, color: Colors.green, size: 16),
              ],
            ),
            
            // Small status text for analysis preparation
            if (analysisSaveStatus != null)
              Padding(
                padding: const EdgeInsets.only(top: 4, left: 32),
                child: Text(
                  analysisSaveStatus!,
                  style: TextStyle(
                    fontSize: 11,
                    color: analysisSaveStatus!.contains('✓') 
                        ? Colors.green 
                        : Colors.grey[600],
                  ),
                ),
              ),
            
            const SizedBox(height: 16),
            
            // Content display - loads immediately
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
                        color: Colors.grey[900], // Black background like terminal
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.grey[700]!),
                      ),
                      child: SingleChildScrollView(
                        child: SelectableText(
                          _formatCVContent(cvContent!),
                          style: TextStyle(
                            fontSize: 13,
                            height: 1.6,
                            fontFamily: 'monospace',
                            color: Colors.grey[100], // Light text
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

/// Service class for CV preview operations
class CVPreviewServiceOptimized {
  /// Load CV content from backend (fast, no processing)
  static Future<String?> loadCVContent(String filename) async {
    try {
      final response = await http
          .get(Uri.parse('http://localhost:8000/api/cv/content/$filename'))
          .timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['content'];
      }
    } catch (e) {
      debugPrint('Error loading CV content: $e');
    }
    return null;
  }

  /// Trigger background analysis save (non-blocking)
  static Future<void> triggerBackgroundSave(String filename) async {
    try {
      // Fire and forget - don't wait for response
      http.post(
        Uri.parse('http://localhost:8000/api/cv/save-for-analysis-async/$filename'),
      ).timeout(
        const Duration(seconds: 1),
        onTimeout: () => http.Response('', 202), // Continue even on timeout
      );
    } catch (e) {
      // Ignore errors - this is background operation
      debugPrint('Background save initiated: $e');
    }
  }
}