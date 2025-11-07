///
/// CV Preview Module
///
/// Handles CV content extraction and preview functionality.
///

import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class CVPreviewModule extends StatefulWidget {
  final String? selectedCVFilename;

  const CVPreviewModule({super.key, required this.selectedCVFilename});

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
      print('🔍 [CV_PREVIEW] Loading CV content for: $filename');
      final data = await APIService.makeAuthenticatedCall(
        endpoint: '/cv/content/$filename',
        method: 'GET',
      );
      print('🔍 [CV_PREVIEW] API response received: ${data.keys}');
      print('🔍 [CV_PREVIEW] Content length: ${data['content']?.length ?? 0}');
      setState(() {
        cvContent = data['content'];
      });
    } catch (e) {
      print('❌ [CV_PREVIEW] Error loading CV content: $e');
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

    // First, fix bullet points that might be inline (split at •)
    content = content.replaceAll('•', '\n•');
    
    // Fix Skills: line if it's inline - FIXED REGEX BUG
    content = content.replaceAllMapped(
      RegExp(r'(\S)\s+Skills:', multiLine: true),
      (match) => '${match.group(1)}\nSkills:'
    );

    // Split content into lines
    List<String> lines = content.split('\n');
    List<String> formattedLines = [];

    // Known section headers
    final sectionHeaders = [
      'Experience',
      'Education',
      'Featured Projects',
      'Technical Skills',
      'Professional Certifications',
      'Career Highlights',
      'Projects',
      'Certifications',
      'Skills'
    ];

    // Helper function to check if line is a job position with dates
    bool _isJobPosition(String line) {
      return RegExp(r'(Jan\.|Feb\.|Mar\.|Apr\.|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\.|20\d{2})\s*(–|-|to)\s*(Present|20\d{2})').hasMatch(line) ||
             line.contains('Present');
    }

    // Helper function to check if line is a company/location
    bool _isCompanyLocation(String line, int index, List<String> allLines) {
      // Check if next line or this line contains location indicators
      if (line.trim().endsWith('Remote')) return true;
      if (line.contains(',') && (
        line.contains('Australia') || 
        line.contains('France') || 
        line.contains('Nepal') ||
        line.contains('NSW') ||
        line.contains('Victoria') ||
        line.contains('Sydney') ||
        line.contains('Melbourne'))) {
        return true;
      }
      return false;
    }

    // Helper function to check if line is contact info (first 5 lines only)
    bool _isContactInfo(String line, int index) {
      if (index > 5) return false;
      
      // Email with phone or just email
      if (line.contains('@gmail.com') || line.contains('@') && line.contains('+61')) {
        return true;
      }
      
      // LinkedIn/GitHub links
      if (line.contains('linkedin.com/') || line.contains('github.com/')) {
        return true;
      }
      
      return false;
    }

    // Helper function to check if line is a project header
    bool _isProjectHeader(String line) {
      // Project headers typically have name | technologies OR name – description
      return line.contains('|') && (
        line.contains('Flutter') ||
        line.contains('Python') ||
        line.contains('PyTorch') ||
        line.contains('ML') ||
        line.contains('AI') ||
        line.contains('Data') ||
        line.contains('SQL')
      );
    }

    for (int i = 0; i < lines.length; i++) {
      String line = lines[i].trim();

      // Skip empty lines
      if (line.isEmpty) {
        formattedLines.add('');
        continue;
      }

      // Skip dash separator lines
      if (line.trim().replaceAll('-', '').isEmpty && line.contains('-')) {
        continue;
      }

      // Format section headers
      if (sectionHeaders.any((header) => line.trim() == header || line.trim().startsWith(header))) {
        formattedLines.add('');
        formattedLines.add('═══════════════════════════════════════════════════════');
        formattedLines.add('${_getSectionIcon(line)} ${line.toUpperCase()}');
        formattedLines.add('═══════════════════════════════════════════════════════');
        formattedLines.add('');
        continue;
      }

      // Format name (first line, all caps or title case name)
      if (i == 0 && !line.contains('@')) {
        formattedLines.add('');
        formattedLines.add(line);
        formattedLines.add('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        formattedLines.add('');
        continue;
      }

      // Format contact information (email, phone, location - first few lines only)
      if (_isContactInfo(line, i)) {
        // Split email/phone line
        if (line.contains('|') && line.contains('@')) {
          List<String> parts = line.split('|');
          for (var part in parts) {
            part = part.trim();
            if (part.contains('@')) {
              formattedLines.add('📧 $part');
            } else if (part.contains('+')) {
              formattedLines.add('📱 $part');
            } else if (part.isNotEmpty) {
              formattedLines.add('🔗 $part');
            }
          }
        } else {
          formattedLines.add('🔗 ' + line);
        }
        continue;
      }

      // Format location (near beginning, contains address)
      if (i <= 3 && line.contains(',') && (line.contains('NSW') || line.contains('Australia'))) {
        formattedLines.add('📍 ' + line);
        formattedLines.add('');
        continue;
      }

      // Format bullet points
      if (line.startsWith('•')) {
        formattedLines.add('  ' + line);
        continue;
      }
      
      // Format Skills summary line (with colon)
      if (line.startsWith('Skills:')) {
        formattedLines.add('');
        formattedLines.add('⚡ ' + line);
        formattedLines.add('');
        continue;
      }

      // Format job positions (lines with dates)
      if (_isJobPosition(line)) {
        formattedLines.add('');
        formattedLines.add('👔 ' + line);
        continue;
      }

      // Format company/location lines
      if (_isCompanyLocation(line, i, lines)) {
        formattedLines.add('🏢 ' + line);
        continue;
      }

      // Format project headers
      if (_isProjectHeader(line)) {
        // Split project name and technologies
        if (line.contains('|')) {
          List<String> parts = line.split('|');
          if (parts.length >= 2) {
            formattedLines.add('');
            formattedLines.add('🚀 ${parts[0].trim()}');
            formattedLines.add('💻 ${parts.sublist(1).join(" | ").trim()}');
            continue;
          }
        }
        formattedLines.add('');
        formattedLines.add('🚀 ' + line);
        continue;
      }

      // Format education entries (degree lines)
      if (line.contains('University') || 
          (line.contains('Master') && line.contains('20')) ||
          (line.contains('PhD') && line.contains('20')) ||
          (line.contains('Bachelor') && line.contains('20'))) {
        formattedLines.add('🎓 ' + line);
        continue;
      }

      // Format degree year/location lines
      if (i > 0 && lines[i-1].contains('University') && 
          (line.contains('20') || line.contains(',') && !line.startsWith('•'))) {
        formattedLines.add('📅 ' + line);
        continue;
      }

      // Format certifications (lines with – and year)
      if (line.contains('–') && line.contains('20') && 
          !_isJobPosition(line) && 
          (line.contains('Professional') || line.contains('Certification') || line.contains('Training'))) {
        formattedLines.add('🏆 ' + line);
        continue;
      }

      // Format technical skills categories
      if (line.endsWith(':') && 
          (line.startsWith('Programming') || 
           line.startsWith('Machine Learning') ||
           line.startsWith('Data Engineering') ||
           line.startsWith('Visualization') ||
           line.startsWith('Development') ||
           line.startsWith('Analytics'))) {
        formattedLines.add('');
        formattedLines.add('▸ ' + line);
        continue;
      }

      // Format URLs in project details
      if (line.contains('Live:') || line.contains('Code:') || line.contains('github.com')) {
        // Split if multiple URLs on one line
        if (line.contains('|')) {
          List<String> parts = line.split('|');
          for (var part in parts) {
            if (part.trim().isNotEmpty) {
              formattedLines.add('  🔗 ${part.trim()}');
            }
          }
        } else {
          formattedLines.add('  🔗 ' + line);
        }
        continue;
      }

      // Regular content
      formattedLines.add(line);
    }

    return formattedLines.join('\n');
  }

  // Helper method to get section-specific icons
  String _getSectionIcon(String section) {
    if (section.contains('Experience')) return '💼';
    if (section.contains('Education')) return '🎓';
    if (section.contains('Project')) return '🎯';
    if (section.contains('Skills') || section.contains('Technical')) return '⚡';
    if (section.contains('Certification')) return '🏆';
    if (section.contains('Career') || section.contains('Highlight')) return '⭐';
    return '📌';
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
                        Icon(Icons.file_copy, color: Colors.blue, size: 16),
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
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 12,
                          ),
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
      final data = await APIService.makeAuthenticatedCall(
        endpoint: '/cv/content/$filename',
        method: 'GET',
      );
      return data['content'];
    } catch (e) {
      debugPrint('Error loading CV content: $e');
    }
    return null;
  }

  /// Load CV preview from backend
  static Future<Map<String, dynamic>?> loadCVPreview(
    String filename, {
    int maxLength = 500,
  }) async {
    try {
      final data = await APIService.makeAuthenticatedCall(
        endpoint: '/cv/preview/$filename?max_length=$maxLength',
        method: 'GET',
      );
      return data;
    } catch (e) {
      debugPrint('Error loading CV preview: $e');
    }
    return null;
  }
}
