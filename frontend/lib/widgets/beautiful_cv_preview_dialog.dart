import 'dart:convert';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../theme/app_theme.dart';
import '../utils/notification_service.dart';

class BeautifulCVPreviewDialog extends StatefulWidget {
  final String cvFilename;

  const BeautifulCVPreviewDialog({
    super.key,
    required this.cvFilename,
  });

  @override
  State<BeautifulCVPreviewDialog> createState() =>
      _BeautifulCVPreviewDialogState();
}

class _BeautifulCVPreviewDialogState extends State<BeautifulCVPreviewDialog>
    with TickerProviderStateMixin {
  static final Map<String, dynamic> _cvCache = {};
  static final Map<String, Map<String, dynamic>> _parsingMetadataCache = {};
  dynamic cvData;
  Map<String, dynamic>? parsingMetadata;
  bool isLoading = true;
  String? error;

  // Animation controllers similar to CV analysis dialog
  late AnimationController _rotationController;
  late AnimationController _pulseController;
  late AnimationController _textController;
  late AnimationController _fadeController;

  int _currentStep = 0;
  Timer? _stepTimer;

  final List<Map<String, dynamic>> _steps = [
    {
      'icon': Icons.upload_file,
      'text': 'Reading CV content...',
      'color': AppTheme.primaryCosmic,
      'emoji': '📄',
    },
    {
      'icon': Icons.person_outline,
      'text': 'Extracting contact info...',
      'color': AppTheme.successGreen,
      'emoji': '👤',
    },
    {
      'icon': Icons.work_outline,
      'text': 'Parsing experience...',
      'color': AppTheme.warningOrange,
      'emoji': '💼',
    },
    {
      'icon': Icons.school_outlined,
      'text': 'Identifying education...',
      'color': AppTheme.primaryAurora,
      'emoji': '🎓',
    },
    {
      'icon': Icons.psychology,
      'text': 'Analyzing skills...',
      'color': AppTheme.primaryNeon,
      'emoji': '🧠',
    },
  ];

  @override
  void initState() {
    super.initState();

    // Initialize animation controllers like CV analysis dialog
    _rotationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    )..repeat(reverse: true);

    _textController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _startStepAnimation();
    _loadCVData();
  }

  void _startStepAnimation() {
    _stepTimer = Timer.periodic(const Duration(milliseconds: 2800), (timer) {
      if (mounted && _currentStep < _steps.length - 1 && isLoading) {
        setState(() {
          _currentStep++;
        });
        _textController.reset();
        _textController.forward();
      }
    });
  }

  @override
  void dispose() {
    _rotationController.dispose();
    _pulseController.dispose();
    _textController.dispose();
    _fadeController.dispose();
    _stepTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadCVData() async {
    try {
      // Get the CV filename without extension
      String baseFilename = widget.cvFilename;
      if (baseFilename.contains('.')) {
        baseFilename = baseFilename.substring(0, baseFilename.lastIndexOf('.'));
      }

      // Clear cache to ensure fresh data
      _cvCache.remove(baseFilename);
      _parsingMetadataCache.remove(baseFilename);

      print('🔍 Loading CV data for: $baseFilename');

      // Try to get JSON template from tailored CVs first
      try {
        final response = await http.get(
          Uri.parse(
              'http://localhost:8000/tailored-cvs/$baseFilename/json-template'),
        );

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          print('📦 Response data type: ${data.runtimeType}');
          print('📦 Response keys: ${data.keys.toList()}');

          final jsonTemplate = data['json_template'];
          print('📋 json_template type: ${jsonTemplate.runtimeType}');

          if (jsonTemplate is List) {
            print('✅ Received List with ${jsonTemplate.length} sections');
          } else {
            print('❌ Expected List but got ${jsonTemplate.runtimeType}');
          }

          setState(() {
            cvData = jsonTemplate;
            parsingMetadata = data['parsing_metadata'];
            isLoading = false;
          });

          // Store in cache
          _cvCache[baseFilename] = jsonTemplate;
          _parsingMetadataCache[baseFilename] = parsingMetadata ?? {};

          _stepTimer?.cancel(); // Stop step animation when loading is complete
          _fadeController.forward();
          return;
        }
      } catch (e) {
        print('⚠️ JSON template not available, trying raw CV content...');
      }

      // Fallback: Get raw CV content for uploaded CVs
      try {
        final response = await http.get(
          Uri.parse(
              'http://localhost:8000/get-cv-content/${widget.cvFilename}'),
        );

        if (response.statusCode == 200) {
          final cvContent = response.body;

          // Parse CV content into structured sections
          final parsedSections = _parseCVContent(cvContent);

          // 🔍 DEBUG: Print parsed CV JSON structure
          print(List.filled(80, '=').join());
          print("🔍 [FRONTEND DEBUG] CV PARSING DEBUG OUTPUT");
          print(List.filled(80, '=').join());
          print("📄 Filename: ${widget.cvFilename}");
          print("📏 Content Length: ${cvContent.length} characters");
          print("📊 Parsed Sections: ${parsedSections.length}");
          print(List.filled(80, '=').join());

          for (int i = 0; i < parsedSections.length; i++) {
            final section = parsedSections[i];
            print("Section ${i + 1}: ${section['section_title']}");
            print("  Content items: ${(section['content'] as List).length}");

            final content = section['content'] as List;
            for (int j = 0; j < content.length && j < 3; j++) {
              final item = content[j] as Map<String, dynamic>;
              final itemType = item['type'] ?? 'unknown';
              final itemText = (item['text'] ?? '').toString();
              final truncatedText = itemText.length > 100
                  ? '${itemText.substring(0, 100)}...'
                  : itemText;
              print("    Item ${j + 1} ($itemType): $truncatedText");
            }
            if (content.length > 3) {
              print("    ... and ${content.length - 3} more items");
            }
            print('');
          }
          print(List.filled(80, '=').join());

          setState(() {
            cvData = parsedSections;
            parsingMetadata = {
              "parsing_confidence": 0.8,
              "total_sections": parsedSections.length,
              "content_length": cvContent.length,
              "filename": widget.cvFilename,
              "parsed_at": DateTime.now().toIso8601String(),
              "note": "Intelligently parsed content"
            };
            isLoading = false;
          });

          _stepTimer?.cancel();
          _fadeController.forward();
        } else {
          throw Exception('Failed to load CV content: ${response.statusCode}');
        }
      } catch (e) {
        print('❌ Error loading CV content: $e');
        setState(() {
          error = 'Error loading CV: $e';
          isLoading = false;
        });
        _stepTimer?.cancel();
      }
    } catch (e, stackTrace) {
      print('❌ Error loading CV data: $e');
      print('🧵 Stack trace: $stackTrace');
      setState(() {
        error = 'Error loading CV: $e';
        isLoading = false;
      });
      _stepTimer?.cancel();
    }
  }

  List<dynamic> _processSectionContent(List<String> content,
      {String? sectionTitle}) {
    final processedContent = <dynamic>[];
    for (int i = 0; i < content.length; i++) {
      final trimmedLine = content[i].trim();
      if (trimmedLine.isEmpty) continue;

      // Check if line contains bullet points or is a list item
      if (trimmedLine.startsWith('•') ||
          trimmedLine.startsWith('*') ||
          trimmedLine.startsWith('-') ||
          trimmedLine.startsWith('▪') ||
          trimmedLine.startsWith('▫') ||
          RegExp(r'^\d+\.').hasMatch(trimmedLine)) {
        // Extract bullet content
        String bulletContent = trimmedLine;
        if (trimmedLine.startsWith('•')) {
          bulletContent = trimmedLine.substring(1).trim();
        } else if (trimmedLine.startsWith('*')) {
          bulletContent = trimmedLine.substring(1).trim();
        } else if (trimmedLine.startsWith('-')) {
          bulletContent = trimmedLine.substring(1).trim();
        } else if (trimmedLine.startsWith('▪')) {
          bulletContent = trimmedLine.substring(1).trim();
        } else if (trimmedLine.startsWith('▫')) {
          bulletContent = trimmedLine.substring(1).trim();
        } else if (RegExp(r'^\d+\.').hasMatch(trimmedLine)) {
          bulletContent = trimmedLine.replaceFirst(RegExp(r'^\d+\.\s*'), '');
        }
        processedContent.add({
          'type': 'bullet',
          'text': bulletContent,
        });
        continue;
      }

      // Check if this is a job title/position line (contains date range)
      bool isJobTitle = false;
      if (RegExp(r'\d{4}\s*[-–—]\s*(Present|\d{4})').hasMatch(trimmedLine) ||
          RegExp(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}')
              .hasMatch(trimmedLine)) {
        isJobTitle = true;
      }

      // Improved: If in EXPERIENCE section, treat as job title if next line is a date
      if ((sectionTitle != null &&
              sectionTitle.toUpperCase().contains('EXPERIENCE')) &&
          !isJobTitle) {
        if (i + 1 < content.length) {
          final nextLine = content[i + 1].trim();
          if (RegExp(r'\d{4}\s*[-–—]\s*(Present|\d{4})').hasMatch(nextLine) ||
              RegExp(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}')
                  .hasMatch(nextLine)) {
            isJobTitle = true;
          }
        }
      }

      if (isJobTitle) {
        processedContent.add({
          'type': 'job_title',
          'text': trimmedLine,
        });
        continue;
      }

      // Education institution
      if (trimmedLine.contains(',') &&
          (trimmedLine.contains('University') ||
              trimmedLine.contains('College') ||
              trimmedLine.contains('School'))) {
        processedContent.add({
          'type': 'education',
          'text': trimmedLine,
        });
        continue;
      }

      // Regular text line
      processedContent.add({
        'type': 'text',
        'text': trimmedLine,
      });
    }
    return processedContent;
  }

  List<Map<String, dynamic>> _parseCVContent(String rawContent) {
    final sections = <Map<String, dynamic>>[];
    final lines = rawContent.split('\n');

    String currentSection = '';
    List<String> currentContent = [];
    bool hasContactInfo = false;

    // Define major CV sections that should be treated as headers
    final majorSections = [
      'EDUCATION',
      'EXPERIENCE',
      'WORK EXPERIENCE',
      'EMPLOYMENT HISTORY',
      'PROJECTS',
      'SKILLS',
      'TECHNICAL SKILLS',
      'CERTIFICATIONS',
      'AWARDS',
      'PUBLICATIONS',
      'VOLUNTEER',
      'INTERESTS',
      'REFERENCES'
    ];

    for (int i = 0; i < lines.length; i++) {
      String line = lines[i];
      final trimmedLine = line.trim();
      if (trimmedLine.isEmpty) continue;

      // Check if this is a major section header (standalone, all caps)
      bool isMajorHeader = false;
      String matchedHeader = '';

      // Only treat as header if it's a standalone line in all caps
      if (trimmedLine == trimmedLine.toUpperCase() && trimmedLine.length > 2) {
        for (String header in majorSections) {
          if (trimmedLine == header.toUpperCase()) {
            isMajorHeader = true;
            matchedHeader = header;
            break;
          }
        }
      }

      if (isMajorHeader) {
        // Save previous section if exists
        if (currentSection.isNotEmpty && currentContent.isNotEmpty) {
          sections.add({
            'section_title': currentSection,
            'content': _processSectionContent(currentContent,
                sectionTitle: currentSection),
          });
        }
        currentSection = matchedHeader.isNotEmpty ? matchedHeader : trimmedLine;
        currentContent = [];
      } else {
        // Handle contact information and personal info
        if (sections.isEmpty && currentSection.isEmpty && !hasContactInfo) {
          if (trimmedLine.contains('@') ||
              trimmedLine.contains('|') ||
              trimmedLine.contains('Phone') ||
              trimmedLine.contains('LinkedIn') ||
              trimmedLine.contains('GitHub') ||
              trimmedLine.contains('Blogs') ||
              trimmedLine.contains('Portfolio')) {
            // This is likely contact information
            if (currentContent.isEmpty) {
              currentSection = 'CONTACT INFORMATION';
              hasContactInfo = true;
            }
          } else if (i < 5 && currentContent.isEmpty) {
            // First few lines without contact indicators - likely name and basic info
            currentSection = 'PERSONAL INFORMATION';
          }
        }
        // Handle career profile section (special case)
        if (trimmedLine.toUpperCase() == 'CAREER PROFILE') {
          if (currentSection.isNotEmpty && currentContent.isNotEmpty) {
            sections.add({
              'section_title': currentSection,
              'content': _processSectionContent(currentContent,
                  sectionTitle: currentSection),
            });
          }
          currentSection = 'CAREER PROFILE';
          currentContent = [];
        } else {
          currentContent.add(trimmedLine);
        }
      }
    }
    // Add the last section
    if (currentSection.isNotEmpty && currentContent.isNotEmpty) {
      sections.add({
        'section_title': currentSection,
        'content': _processSectionContent(currentContent,
            sectionTitle: currentSection),
      });
    }
    // If no sections were found, create a general content section
    if (sections.isEmpty) {
      sections.add({
        'section_title': 'CV Content',
        'content': _processSectionContent(
            lines.where((line) => line.trim().isNotEmpty).toList()),
      });
    }
    return sections;
  }

  @override
  Widget build(BuildContext context) {
    return Dialog.fullscreen(
      child: Scaffold(
        backgroundColor: const Color(0xFFF8FAFC),
        appBar: _buildAppBar(),
        body: isLoading
            ? _buildLoadingState()
            : error != null
                ? _buildErrorState()
                : _buildCVContent(),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    final confidence = parsingMetadata?['parsing_confidence'] ?? 0.0;
    return AppBar(
      elevation: 0,
      backgroundColor: Colors.white,
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.blue.shade600, Colors.purple.shade600],
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.description, color: Colors.white, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Professional CV Preview',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                if (!isLoading && error == null)
                  Text(
                    '${(confidence * 100).toStringAsFixed(0)}% parsing accuracy',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
      leading: IconButton(
        icon: const Icon(Icons.close, color: Colors.black87),
        onPressed: () => Navigator.pop(context),
      ),
      actions: [
        if (!isLoading && error == null)
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: confidence > 0.8
                  ? Colors.green
                  : confidence > 0.6
                      ? Colors.orange
                      : Colors.red,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  confidence > 0.8
                      ? Icons.check_circle
                      : confidence > 0.6
                          ? Icons.warning
                          : Icons.error,
                  color: Colors.white,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Text(
                  confidence > 0.8
                      ? 'Excellent'
                      : confidence > 0.6
                          ? 'Good'
                          : 'Needs Review',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildLoadingState() {
    final currentStepData = _steps[_currentStep];

    return Center(
      child: Container(
        padding: const EdgeInsets.all(32),
        margin: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.white,
              Colors.blue.shade50,
              Colors.purple.shade50,
            ],
          ),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: currentStepData['color'].withOpacity(0.3),
              blurRadius: 30,
              offset: const Offset(0, 15),
              spreadRadius: 5,
            ),
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Main animated icon like CV analysis dialog
            AnimatedBuilder(
              animation: _rotationController,
              builder: (context, child) {
                return Transform.rotate(
                  angle: _rotationController.value * 2 * 3.14159,
                  child: AnimatedBuilder(
                    animation: _pulseController,
                    builder: (context, child) {
                      return Transform.scale(
                        scale: 1.0 + (_pulseController.value * 0.2),
                        child: Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            color: currentStepData['color'].withOpacity(0.1),
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: currentStepData['color'],
                              width: 3,
                            ),
                          ),
                          child: Stack(
                            alignment: Alignment.center,
                            children: [
                              Icon(
                                Icons.description,
                                size: 35,
                                color: currentStepData['color'],
                              ),
                              Positioned(
                                top: 5,
                                right: 5,
                                child: Text(
                                  currentStepData['emoji'],
                                  style: const TextStyle(fontSize: 16),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                );
              },
            ),

            const SizedBox(height: 24),

            // Title with gradient text
            ShaderMask(
              shaderCallback: (bounds) => LinearGradient(
                colors: [
                  AppTheme.primaryCosmic,
                  AppTheme.primaryAurora,
                ],
              ).createShader(bounds),
              child: const Text(
                'AI-Powered CV Parsing',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
            ),

            const SizedBox(height: 20),

            // Current step with animation like CV analysis dialog
            AnimatedBuilder(
              animation: _textController,
              builder: (context, child) {
                return Opacity(
                  opacity: _textController.value,
                  child: Transform.translate(
                    offset: Offset(0, 20 * (1 - _textController.value)),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 16),
                      decoration: BoxDecoration(
                        color: currentStepData['color'].withOpacity(0.1),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(
                          color: currentStepData['color'].withOpacity(0.3),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            currentStepData['emoji'],
                            style: const TextStyle(fontSize: 24),
                          ),
                          const SizedBox(width: 12),
                          Flexible(
                            child: Text(
                              currentStepData['text'],
                              style: TextStyle(
                                fontSize: 16,
                                color: currentStepData['color'],
                                fontWeight: FontWeight.w600,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),

            const SizedBox(height: 24),

            // Progress indicator with glow
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: currentStepData['color'].withOpacity(0.4),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: LinearProgressIndicator(
                  value: (_currentStep + 1) / _steps.length,
                  backgroundColor: AppTheme.neutralGray200,
                  valueColor:
                      AlwaysStoppedAnimation<Color>(currentStepData['color']),
                  minHeight: 8,
                ),
              ),
            ),

            const SizedBox(height: 12),

            Text(
              'Step ${_currentStep + 1} of ${_steps.length}',
              style: AppTheme.bodySmall.copyWith(
                fontWeight: FontWeight.w500,
                color: AppTheme.neutralGray600,
              ),
            ),

            const SizedBox(height: 20),

            // Tip section
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blue.shade200),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.psychology,
                    color: Colors.blue.shade600,
                    size: 20,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Using Claude AI to extract contact info, experience, education, skills, and more with high accuracy.',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.blue.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Container(
        margin: const EdgeInsets.all(32),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 20,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline, color: Colors.red.shade400, size: 48),
            const SizedBox(height: 16),
            Text(
              'Unable to load CV',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Colors.grey.shade800,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              error ?? 'Unknown error occurred',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCVContent() {
    if (cvData == null) {
      return const Center(child: Text('No CV data available.'));
    }
    // The new format: cvData is a List of sections
    final sections = cvData is List ? cvData as List : [];
    if (sections.isEmpty) {
      return const Center(child: Text('No sections found in CV.'));
    }
    return FadeTransition(
      opacity: Tween<double>(begin: 0.0, end: 1.0).animate(_fadeController),
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            for (final section in sections) _buildSection(section),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(dynamic section) {
    final title = section['section_title']?.toString() ?? '';
    final content = section['content'];
    // Debug print for section data
    print('DEBUG: Rendering section: '
        'title=$title, contentType=${content.runtimeType}, content=$content');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (title.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(bottom: 8, top: 32),
            child: Row(
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade700,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Divider(
                    color: Colors.blue.shade100,
                    thickness: 2,
                  ),
                ),
              ],
            ),
          ),
        if (content is String)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(content, style: const TextStyle(fontSize: 15)),
          )
        else if (content is List && content.isNotEmpty)
          ..._buildListContent(content, sectionTitle: title)
        else if (content != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child:
                Text(content.toString(), style: const TextStyle(fontSize: 15)),
          ),
      ],
    );
  }

  List<Widget> _buildListContent(List content, {String? sectionTitle}) {
    print('DEBUG: _buildListContent for section=$sectionTitle, '
        'contentType=${content.runtimeType}, content=$content');
    if (content.isEmpty) return [];
    final firstItem = content.first;
    // Use custom renderers for specific sections
    if (sectionTitle != null && sectionTitle.toUpperCase().contains('SKILL')) {
      return [_buildBulletedBoldList(content)];
    }
    if (sectionTitle != null &&
        sectionTitle.toUpperCase().contains('EDUCATION')) {
      return [_buildEducationList(content)];
    }
    if (sectionTitle != null &&
        sectionTitle.toUpperCase().contains('EXPERIENCE')) {
      return [_buildExperienceList(content)];
    }
    if (firstItem is Map && firstItem.containsKey('type')) {
      return [_buildParsedContent(content, sectionTitle: sectionTitle)];
    }
    // fallback to default
    return [_simpleList(content)];
  }

  Widget _buildExperienceList(List items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: _buildExperienceEntries(items),
    );
  }

  List<Widget> _buildExperienceEntries(List items) {
    List<Widget> entries = [];
    
    // Use the improved grouping logic exclusively
    List<ExperienceEntry> jobEntries = _groupExperienceItems(items);
    
    // Process each grouped entry consistently
    for (final jobEntry in jobEntries) {
      entries.add(_buildExperienceEntry(
        jobEntry.title,
        jobEntry.company,
        jobEntry.date,
        jobEntry.bullets,
        location: jobEntry.location,
      ));
    }
    
    // Handle any remaining ungrouped items that weren't processed
    final processedItems = Set<int>();
    
    // Mark all items that were processed in grouping
    for (int i = 0; i < items.length; i++) {
      final item = items[i];
      if (item is Map) {
        final type = item['type']?.toString() ?? '';
        if (type == 'job_title' || type == 'text' || type == 'bullet') {
          processedItems.add(i);
        }
      }
    }
    
    // Process any remaining items as standalone content
    for (int i = 0; i < items.length; i++) {
      if (processedItems.contains(i)) continue;
      
      final item = items[i];
      if (item is Map) {
        final type = item['type']?.toString() ?? '';
        final text = item['text']?.toString() ?? '';
        
        // Handle structured experience data (direct format)
        if (item.containsKey('job_title') || item.containsKey('company')) {
          final jobTitle = item['job_title']?.toString() ?? '';
          final company = item['company']?.toString() ?? '';
          final date = item['date']?.toString() ?? '';
          final location = item['location']?.toString() ?? '';
          final bullets = (item['bullets'] ?? item['bullet_points'] ?? []) as List? ?? [];
          
          entries.add(_buildExperienceEntry(
            jobTitle,
            company.isNotEmpty ? company : null,
            date.isNotEmpty ? date : null,
            bullets.map((b) => _formatBulletPoint(b.toString())).toList(),
            location: location.isNotEmpty ? location : null,
          ));
        } else {
          // Treat as standalone text
          entries.add(Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text(text, style: const TextStyle(fontSize: 15)),
          ));
        }
      } else {
        // Non-map items, treat as regular text
        entries.add(Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Text(item.toString(), style: const TextStyle(fontSize: 15)),
        ));
      }
    }
    
    return entries;
  }
  
  Widget _buildExperienceEntry(String jobTitle, String? company, String? date, List<String> bullets, {String? location}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Job title with enhanced formatting
          Text(
            jobTitle,
            style: const TextStyle(
              fontWeight: FontWeight.w600,
              fontSize: 16,
              color: Colors.black87,
              letterSpacing: 0.2,
            ),
          ),
          // Company with fallback handling
          if (company != null && company.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(
                company,
                style: TextStyle(
                  color: Colors.blue.shade600,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          // Date and location in a row
          if ((date != null && date.isNotEmpty) || (location != null && location.isNotEmpty))
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Row(
                children: [
                  if (date != null && date.isNotEmpty)
                    Expanded(
                      child: Text(
                        date,
                        style: TextStyle(
                          color: Colors.grey.shade500,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  if (location != null && location.isNotEmpty)
                    Text(
                      location,
                      style: TextStyle(
                        color: Colors.grey.shade500,
                        fontSize: 14,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                ],
              ),
            ),
          // Bullets with enhanced formatting
          if (bullets.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: bullets
                    .where((b) => b.trim().isNotEmpty)
                    .map<Widget>((b) => Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                margin: const EdgeInsets.only(top: 8, right: 10),
                                width: 6,
                                height: 6,
                                decoration: BoxDecoration(
                                  color: Colors.blue.shade600,
                                  shape: BoxShape.circle,
                                ),
                              ),
                              Expanded(
                                child: Text(
                                  b,
                                  style: const TextStyle(
                                    fontSize: 14,
                                    height: 1.5,
                                    color: Colors.black87,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ))
                    .toList(),
              ),
            ),
        ],
      ),
    );
  }
  
  bool _isCompanyInfo(String text) {
    final lowerText = text.toLowerCase();
    
    // Must contain comma (suggesting company, location format) OR specific company indicators
    final hasComma = text.contains(',');
    final hasCompanyIndicators = lowerText.contains('company') ||
           lowerText.contains('corp') ||
           lowerText.contains('inc') ||
           lowerText.contains('ltd') ||
           lowerText.contains('pty') ||
           lowerText.contains('university') ||
           lowerText.contains('institute') ||
           lowerText.contains('organization') ||
           lowerText.contains('agency') ||
           lowerText.contains('group') ||
           lowerText.contains('solutions') ||
           lowerText.contains('technologies') ||
           lowerText.contains('systems') ||
           lowerText.contains('consulting') ||
           lowerText.contains('services');
    
    // Additional checks to avoid false positives
    final isNotBulletPoint = !text.trim().startsWith('•') && 
                            !text.trim().startsWith('-') && 
                            !text.trim().startsWith('*');
    
    final isNotTooLong = text.length < 200; // Avoid treating long descriptions as companies
    
    return (hasComma || hasCompanyIndicators) && isNotBulletPoint && isNotTooLong;
  }
  
  Map<String, String?> _parseJobTitleAndDate(String text) {
    // Enhanced parsing for job title, date, and location
    String? title;
    String? date;
    String? location;
    
    // Enhanced date patterns
    final datePattern = RegExp(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}[^\d]*\d{4}|\d{4}[^\d]*\d{4}|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}[^\d]*Present|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s*[-–—]\s*Present|\d{4}\s*[-–—]\s*Present');
    final dateMatch = datePattern.firstMatch(text);
    
    if (dateMatch != null) {
      date = dateMatch.group(0);
      title = text.substring(0, dateMatch.start).trim();
      
      // Look for location in the remaining text
      final remainingText = text.substring(dateMatch.end).trim();
      if (remainingText.isNotEmpty) {
        location = remainingText;
      }
    } else {
      // No date found, check for location clues
      final locationPattern = RegExp(r'\b(Australia|Sydney|Melbourne|Brisbane|Perth|Adelaide|Darwin|Canberra|NSW|QLD|VIC|SA|WA|TAS|NT|ACT)\b', caseSensitive: false);
      final locationMatch = locationPattern.firstMatch(text);
      
      if (locationMatch != null) {
        title = text.substring(0, locationMatch.start).trim();
        location = text.substring(locationMatch.start).trim();
      } else {
        // No date or location found, treat entire text as title
        title = text.trim();
      }
    }
    
    return {
      'title': title,
      'date': date,
      'location': location,
    };
  }

  Widget _buildParsedContent(List content, {String? sectionTitle}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (int i = 0; i < content.length; i++) ...[
          _buildParsedItem(content, i, content, sectionTitle: sectionTitle),
        ]
      ],
    );
  }

  Widget _buildParsedItem(List content, int i, List all,
      {String? sectionTitle}) {
    final item = content[i];
    if (item is! Map) return SizedBox.shrink();
    final type = item['type']?.toString() ?? '';
    final text = item['text']?.toString() ?? '';
    // Lookahead for supporting info (e.g., company/date after job_title)
    if (type == 'job_title' || type == 'degree' || type == 'project_title') {
      // Try to find supporting info (next line is text or education)
      String? supporting;
      if (i + 1 < all.length) {
        final next = all[i + 1];
        if (next is Map &&
            (next['type'] == 'text' || next['type'] == 'education')) {
          supporting = next['text']?.toString();
        }
      }
      return Padding(
        padding: const EdgeInsets.only(bottom: 8, top: 18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              text,
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.bold,
                color: Colors.black87,
                letterSpacing: 0.2,
              ),
            ),
            if (supporting != null && supporting.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 2),
                child: Text(
                  supporting,
                  style: TextStyle(
                    fontSize: 14,
                    fontStyle: FontStyle.italic,
                    color: Colors.grey.shade700,
                  ),
                ),
              ),
          ],
        ),
      );
    } else if (type == 'education') {
      return Padding(
        padding: const EdgeInsets.only(bottom: 4),
        child: Text(
          text,
          style: TextStyle(
            fontSize: 15,
            fontStyle: FontStyle.italic,
            color: Colors.blue.shade700,
          ),
        ),
      );
    } else if (type == 'bullet') {
      return Padding(
        padding: const EdgeInsets.only(bottom: 8, left: 24),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              margin: const EdgeInsets.only(top: 8, right: 12),
              width: 7,
              height: 7,
              decoration: const BoxDecoration(
                color: Colors.blue,
                shape: BoxShape.circle,
              ),
            ),
            Expanded(
              child: Text(
                text,
                style: const TextStyle(
                  fontSize: 15,
                  height: 1.5,
                ),
              ),
            ),
          ],
        ),
      );
    } else if (type == 'text') {
      return Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Text(
          text,
          style: const TextStyle(
            fontSize: 15,
            height: 1.5,
          ),
        ),
      );
    }
    // fallback
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        text,
        style: const TextStyle(fontSize: 15),
      ),
    );
  }

  Widget _buildEducationEntry(Map item) {
    final degree = item['degree']?.toString() ?? '';
    final school = item['school']?.toString() ?? '';
    final date = item['date']?.toString() ?? '';
    final location = item['location']?.toString() ?? '';

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              if (degree.isNotEmpty)
                Text(degree,
                    style: const TextStyle(fontWeight: FontWeight.w600)),
              if (date.isNotEmpty) ...[
                const Spacer(),
                Text(date, style: const TextStyle(color: Colors.grey)),
              ],
            ],
          ),
          if (school.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(school,
                  style: const TextStyle(color: Colors.blueAccent)),
            ),
          if (location.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(location, style: const TextStyle(color: Colors.grey)),
            ),
        ],
      ),
    );
  }

  Widget _buildBulletedBoldList(List items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: items.map<Widget>((item) {
        String text;
        if (item is Map && item.containsKey('text')) {
          text = item['text']?.toString() ?? '';
        } else {
          text = item.toString();
        }
        return Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('• ', style: TextStyle(fontSize: 16)),
              Expanded(child: Text(text)),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildEducationList(List items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: _buildEducationEntries(items),
    );
  }

  List<Widget> _buildEducationEntries(List items) {
    List<Widget> entries = [];
    String? currentDegree;
    String? currentInstitution;
    String? currentDate;
    
    for (int i = 0; i < items.length; i++) {
      final item = items[i];
      
      if (item is Map) {
        final type = item['type']?.toString() ?? '';
        final text = item['text']?.toString() ?? '';
        
        // Handle structured education data
        if (item.containsKey('degree')) {
          final degree = item['degree']?.toString() ?? '';
          final school = item['school']?.toString() ?? '';
          final date = item['date']?.toString() ?? '';
          
          entries.add(Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(degree, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                if (school.isNotEmpty) 
                  Text(school, style: TextStyle(color: Colors.grey.shade600)),
                if (date.isNotEmpty) 
                  Text(date, style: TextStyle(color: Colors.grey.shade500, fontSize: 14)),
              ],
            ),
          ));
        } else if (type == 'text' && text.isNotEmpty) {
          // This might be a degree title
          if (_isDegreeTitle(text)) {
            currentDegree = text;
            currentInstitution = null;
            currentDate = null;
          } else {
            entries.add(Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('• ', style: TextStyle(fontSize: 16)),
                  Expanded(child: Text(text)),
                ],
              ),
            ));
          }
        } else if (type == 'job_title' && text.isNotEmpty) {
          // This might be institution and date info
          if (currentDegree != null) {
            // Parse institution and date from the text
            final parts = _parseInstitutionAndDate(text);
            currentInstitution = parts['institution'];
            currentDate = parts['date'];
            
            // Create education entry
            entries.add(Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(currentDegree!, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                  if (currentInstitution != null && currentInstitution!.isNotEmpty) 
                    Text(currentInstitution!, style: TextStyle(color: Colors.grey.shade600)),
                  if (currentDate != null && currentDate!.isNotEmpty) 
                    Text(currentDate!, style: TextStyle(color: Colors.grey.shade500, fontSize: 14)),
                ],
              ),
            ));
            
            // Reset for next entry
            currentDegree = null;
            currentInstitution = null;
            currentDate = null;
          } else {
            entries.add(Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('• ', style: TextStyle(fontSize: 16)),
                  Expanded(child: Text(text)),
                ],
              ),
            ));
          }
        } else {
          entries.add(Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('• ', style: TextStyle(fontSize: 16)),
                Expanded(child: Text(text)),
              ],
            ),
          ));
        }
      } else {
        entries.add(Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('• ', style: TextStyle(fontSize: 16)),
              Expanded(child: Text(item.toString())),
            ],
          ),
        ));
      }
    }
    
    // Handle any remaining degree without institution
    if (currentDegree != null) {
      entries.add(Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: Text(currentDegree!, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
      ));
    }
    
    return entries;
  }
  
  bool _isDegreeTitle(String text) {
    final lowerText = text.toLowerCase();
    return lowerText.contains('master') || 
           lowerText.contains('bachelor') || 
           lowerText.contains('phd') || 
           lowerText.contains('degree') ||
           lowerText.contains('diploma') ||
           lowerText.contains('certificate');
  }
  
  Map<String, String?> _parseInstitutionAndDate(String text) {
    // Try to extract institution and date from text like "Charles Darwin University, Sydney, AustraliaGPA Mar 2023 - Nov 2024"
    String? institution;
    String? date;
    
    // Look for date patterns
    final datePattern = RegExp(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}[^\d]*\d{4}|\d{4}[^\d]*\d{4}');
    final dateMatch = datePattern.firstMatch(text);
    
    if (dateMatch != null) {
      date = dateMatch.group(0);
      institution = text.substring(0, dateMatch.start).trim();
      
      // Remove "GPA" if it's at the end of institution
      if (institution != null && institution.endsWith('GPA')) {
        institution = institution.substring(0, institution.length - 3).trim();
      }
    } else {
      // No date found, treat entire text as institution
      institution = text.trim();
    }
    
    return {
      'institution': institution,
      'date': date,
    };
  }

  Widget _buildExperienceOrProjectEntry(Map item) {
    final title = item['title']?.toString() ?? '';
    final jobTitle = item['job_title']?.toString() ?? '';
    final company = item['company']?.toString() ?? '';
    final date = item['date']?.toString() ?? '';
    final location = item['location']?.toString() ?? '';
    final description = item['description']?.toString() ?? '';
    final url = item['url']?.toString() ?? '';
    final bullets =
        (item['bullets'] ?? item['bullet_points'] ?? []) as List? ?? [];

    // Use job_title if available, otherwise use title
    final displayTitle = jobTitle.isNotEmpty ? jobTitle : title;

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Job title and date on first row
          Row(
            children: [
              if (displayTitle.isNotEmpty)
                Expanded(
                  child: Text(displayTitle,
                      style: const TextStyle(
                          fontWeight: FontWeight.w600, fontSize: 16)),
                ),
              if (date.isNotEmpty)
                Text(date, style: const TextStyle(color: Colors.grey)),
            ],
          ),
          // Company name on second row
          if (company.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(company,
                  style: const TextStyle(
                      color: Colors.blueAccent,
                      fontSize: 14,
                      fontWeight: FontWeight.w500)),
            ),
          if (location.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(location, style: const TextStyle(color: Colors.grey)),
            ),
          if (url.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Row(
                children: [
                  const Icon(Icons.link, size: 14, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(url,
                      style: const TextStyle(color: Colors.blue, fontSize: 13)),
                ],
              ),
            ),
          if (description.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(description,
                  style: const TextStyle(fontSize: 14, color: Colors.black87)),
            ),
          if (bullets.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: bullets
                    .map<Widget>((b) => Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('• ', style: TextStyle(fontSize: 16)),
                            Expanded(child: Text(b.toString())),
                          ],
                        ))
                    .toList(),
              ),
            ),
        ],
      ),
    );
  }

  Widget _simpleList(List items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: items.map<Widget>((item) {
        final text = item.toString().trim();
        // Check if the text already starts with a bullet point
        final alreadyBulleted = text.startsWith('• ') || text.startsWith('•');

        return Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Text(alreadyBulleted ? text : '• $text'),
        );
      }).toList(),
    );
  }

  static void invalidateCacheFor(String filename) {
    String baseFilename = filename;
    if (baseFilename.contains('.')) {
      baseFilename = baseFilename.substring(0, baseFilename.lastIndexOf('.'));
    }
    _cvCache.remove(baseFilename);
    _parsingMetadataCache.remove(baseFilename);
  }

  static void clearAllCache() {
    _cvCache.clear();
    _parsingMetadataCache.clear();
  }
  
  // Enhanced parsing helper methods
  Map<String, String?> _parseCompanyInfo(String text) {
    String? company;
    String? location;
    
    // Split by comma to separate company and location
    final parts = text.split(',');
    if (parts.length >= 2) {
      company = parts[0].trim();
      location = parts.sublist(1).join(', ').trim();
    } else {
      company = text.trim();
    }
    
    return {
      'company': company,
      'location': location,
    };
  }
  
  bool _isLocationInfo(String text) {
    final lowerText = text.toLowerCase();
    return lowerText.contains('australia') ||
           lowerText.contains('sydney') ||
           lowerText.contains('melbourne') ||
           lowerText.contains('brisbane') ||
           lowerText.contains('perth') ||
           lowerText.contains('adelaide') ||
           lowerText.contains('darwin') ||
           lowerText.contains('canberra') ||
           lowerText.contains('nsw') ||
           lowerText.contains('qld') ||
           lowerText.contains('vic') ||
           lowerText.contains('sa') ||
           lowerText.contains('wa') ||
           lowerText.contains('tas') ||
           lowerText.contains('nt') ||
           lowerText.contains('act');
  }
  
  bool _isDateInfo(String text) {
    return RegExp(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|\d{4}\s*[-–—]\s*\d{4}|\d{4}\s*[-–—]\s*Present').hasMatch(text);
  }
  
  String _formatBulletPoint(String text) {
    // Remove existing bullet points and clean up
    String cleaned = text.replaceAll(RegExp(r'^[•*\-▪▫]\s*'), '').trim();
    return cleaned;
  }
  
  bool _isBulletIncomplete(String text) {
    // Enhanced logic to detect incomplete bullets with more precision
    final trimmed = text.trim();
    
    // Complete if ends with proper punctuation
    if (trimmed.endsWith('.') || trimmed.endsWith('!') || trimmed.endsWith('?') || 
        trimmed.endsWith(':') || trimmed.endsWith(';')) {
      return false;
    }
    
    // Complete if ends with specific patterns
    if (RegExp(r'\d+%$').hasMatch(trimmed) || // Ends with percentage
        RegExp(r'\d+$').hasMatch(trimmed) || // Ends with number
        RegExp(r'\w+\)$').hasMatch(trimmed) || // Ends with word in parentheses
        RegExp(r'[A-Z]{2,}$').hasMatch(trimmed)) { // Ends with acronym
      return false;
    }
    
    // Incomplete if it's reasonably long and doesn't end with typical completions
    if (trimmed.length > 15) {
      // Check if it ends with common incomplete patterns
      final endsWithPreposition = RegExp(r'\b(in|on|at|to|for|with|by|from|of|and|or|but|the|a|an)$', caseSensitive: false).hasMatch(trimmed);
      final endsWithVerb = RegExp(r'\b(was|were|is|are|been|being|have|has|had|will|would|can|could|may|might|must|should|shall)$', caseSensitive: false).hasMatch(trimmed);
      
      return endsWithPreposition || endsWithVerb;
    }
    
    return false;
  }
  
  String _mergeBulletContinuation(String original, String continuation) {
    // Smart merging of bullet continuation with improved logic
    String cleaned = continuation.replaceAll(RegExp(r'^[•*\-▪▫]\s*'), '').trim();
    
    if (cleaned.isEmpty) return original;
    
    // Check if continuation starts with a lowercase letter (likely continuation)
    final startsWithLowercase = cleaned[0].toLowerCase() == cleaned[0] && cleaned[0].toUpperCase() != cleaned[0];
    
    // Check if original ends with proper punctuation
    final originalEndsWithPunctuation = original.endsWith('.') || original.endsWith('!') || 
                                       original.endsWith('?') || original.endsWith(':') || 
                                       original.endsWith(';');
    
    if (startsWithLowercase && !originalEndsWithPunctuation) {
      // Direct continuation
      return '$original $cleaned';
    } else if (!originalEndsWithPunctuation) {
      // Add period and continue
      return '$original. $cleaned';
    } else {
      // Original already has punctuation, start new sentence
      return '$original ${cleaned[0].toUpperCase()}${cleaned.substring(1)}';
    }
  }
  
  List<ExperienceEntry> _groupExperienceItems(List items) {
    List<ExperienceEntry> entries = [];
    ExperienceEntry? currentEntry;
    String? pendingBulletContinuation;
    
    for (int i = 0; i < items.length; i++) {
      final item = items[i];
      
      if (item is Map) {
        final type = item['type']?.toString() ?? '';
        final text = item['text']?.toString() ?? '';
        
        if (type == 'job_title' && text.isNotEmpty) {
          // Finalize previous entry if exists
          if (currentEntry != null) {
            _finalizeBulletContinuation(currentEntry, pendingBulletContinuation);
            entries.add(currentEntry);
          }
          
          final parsed = _parseJobTitleAndDate(text);
          currentEntry = ExperienceEntry(
            title: parsed['title'] ?? text,
            date: parsed['date'],
            location: parsed['location'],
          );
          pendingBulletContinuation = null;
        } else if (currentEntry != null) {
          if (type == 'text' && text.isNotEmpty) {
            // Handle pending bullet continuation first
            if (pendingBulletContinuation != null) {
              final lastBulletIndex = currentEntry.bullets.length - 1;
              if (lastBulletIndex >= 0) {
                currentEntry.bullets[lastBulletIndex] = _mergeBulletContinuation(
                  currentEntry.bullets[lastBulletIndex],
                  text,
                );
              }
              pendingBulletContinuation = null;
            } else if (currentEntry.company == null && _isCompanyInfo(text)) {
              final companyInfo = _parseCompanyInfo(text);
              currentEntry.company = companyInfo['company'];
              if (currentEntry.location == null) {
                currentEntry.location = companyInfo['location'];
              }
            } else if (_isLocationInfo(text)) {
              currentEntry.location = text;
            } else if (_isDateInfo(text)) {
              currentEntry.date = text;
            } else {
              // Add as bullet point
              final formattedBullet = _formatBulletPoint(text);
              currentEntry.bullets.add(formattedBullet);
              
              // Check if this bullet needs continuation
              if (_isBulletIncomplete(formattedBullet)) {
                pendingBulletContinuation = formattedBullet;
              }
            }
          } else if (type == 'bullet' && text.isNotEmpty) {
            final formattedBullet = _formatBulletPoint(text);
            currentEntry.bullets.add(formattedBullet);
            
            // Check if this bullet needs continuation
            if (_isBulletIncomplete(formattedBullet)) {
              pendingBulletContinuation = formattedBullet;
            } else {
              pendingBulletContinuation = null;
            }
          }
        }
      }
    }
    
    // Finalize the last entry
    if (currentEntry != null) {
      _finalizeBulletContinuation(currentEntry, pendingBulletContinuation);
      entries.add(currentEntry);
    }
    
    return entries;
  }
  
  void _finalizeBulletContinuation(ExperienceEntry entry, String? pendingContinuation) {
    // Clean up any incomplete bullet continuations
    if (pendingContinuation != null && entry.bullets.isNotEmpty) {
      final lastIndex = entry.bullets.length - 1;
      if (entry.bullets[lastIndex] == pendingContinuation) {
        // Add period if the bullet doesn't end with proper punctuation
        if (!pendingContinuation.endsWith('.') && 
            !pendingContinuation.endsWith('!') && 
            !pendingContinuation.endsWith('?')) {
          entry.bullets[lastIndex] = '$pendingContinuation.';
        }
      }
    }
  }
  
  // Usage: Call BeautifulCVPreviewDialog.invalidateCacheFor(filename) after a CV is re-uploaded or modified.
}

// Helper class for structured experience data
class ExperienceEntry {
  String title;
  String? company;
  String? date;
  String? location;
  List<String> bullets;
  
  ExperienceEntry({
    required this.title,
    this.company,
    this.date,
    this.location,
    List<String>? bullets,
  }) : bullets = bullets ?? [];
}
