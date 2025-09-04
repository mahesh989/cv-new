import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'dart:html' as html;
import '../services/ats_service.dart';
import '../dialogs/cv_generation_dialog.dart';
import '../state/session_state.dart';
import '../utils/notification_service.dart';
import 'dart:convert';

class TailoredCVPreviewDialog extends StatefulWidget {
  final String tailoredCVFilename;
  final String originalCVFilename;
  final String jdText;
  final int atsScore;
  final String? previewOverride;
  final String? prompt;

  const TailoredCVPreviewDialog({
    super.key,
    required this.tailoredCVFilename,
    required this.originalCVFilename,
    required this.jdText,
    required this.atsScore,
    this.previewOverride,
    this.prompt,
  });

  @override
  State<TailoredCVPreviewDialog> createState() =>
      _TailoredCVPreviewDialogState();
}

class _TailoredCVPreviewDialogState extends State<TailoredCVPreviewDialog>
    with TickerProviderStateMixin {
  String previewText = 'Loading preview...';
  bool isLoading = true;
  int atsScore = 0;
  bool isSaving = false;
  double _fontSize = 14.0;
  bool _isDarkMode = false;

  late AnimationController _fadeController;
  late AnimationController _scaleController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    atsScore = widget.atsScore;

    // Initialize animations
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeInOut,
    ));

    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _scaleController,
      curve: Curves.elasticOut,
    ));

    _loadPreview();
    _fadeController.forward();
    _scaleController.forward();
  }

  @override
  void dispose() {
    _fadeController.dispose();
    _scaleController.dispose();
    super.dispose();
  }

  String _formatCVText(String rawText) {
    if (rawText.isEmpty) return rawText;

    // Replace bullet symbols with asterisks
    String formatted =
        rawText.replaceAll('•', '*').replaceAll('–', '*').replaceAll('▪', '*');

    // Add spacing between sections
    final sections = [
      'CONTACT INFORMATION',
      'EDUCATION',
      'EXPERIENCE',
      'PROJECTS',
      'SKILLS'
    ];
    for (String section in sections) {
      formatted = formatted.replaceAll(section, '\n\n$section\n');
    }

    // Ensure bullet points are on separate lines
    formatted = formatted.replaceAllMapped(RegExp(r'\*([^*\n]+)'),
        (match) => '\n* ${match.group(1)?.trim() ?? ''}');

    // Clean up multiple line breaks
    formatted = formatted.replaceAll(RegExp(r'\n{3,}'), '\n\n');
    formatted = formatted.replaceAll(RegExp(r'^\n+'), '');

    return formatted.trim();
  }

  Future<void> _loadPreview() async {
    if (widget.previewOverride != null) {
      setState(() {
        previewText = _formatCVText(widget.previewOverride!);
        isLoading = false;
      });
      return;
    }

    try {
      final baseFilename = widget.tailoredCVFilename.contains('.')
          ? widget.tailoredCVFilename
              .substring(0, widget.tailoredCVFilename.lastIndexOf('.'))
          : widget.tailoredCVFilename;

      final response = await http
          .get(
            Uri.parse(
                'http://localhost:8000/tailored-cvs/$baseFilename/preview'),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        setState(() {
          previewText = response.body.isNotEmpty
              ? _formatCVText(response.body)
              : '⚠️ No preview content available.';
          isLoading = false;
        });
      } else {
        throw Exception('Failed to load preview: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        previewText = 'Error loading CV preview: $e';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isSmallScreen = screenSize.width < 600;

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: EdgeInsets.symmetric(
        horizontal: isSmallScreen ? 16 : 32,
        vertical: isSmallScreen ? 24 : 32,
      ),
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: Container(
                width: screenSize.width * 0.9,
                height: screenSize.height * 0.85,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.3),
                      blurRadius: 30,
                      spreadRadius: 0,
                      offset: const Offset(0, 15),
                    ),
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      spreadRadius: 0,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(24),
                  child: Material(
                    color: _isDarkMode ? const Color(0xFF1E1E1E) : Colors.white,
                    child: Column(
                      children: [
                        _buildHeader(),
                        _buildToolbar(),
                        Expanded(child: _buildContent()),
                        _buildFooter(),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: _isDarkMode
              ? [const Color(0xFF2D2D2D), const Color(0xFF1E1E1E)]
              : [const Color(0xFF667EEA), const Color(0xFF764BA2)],
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(
              Icons.description_outlined,
              color: Colors.white,
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'CV Preview',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  widget.tailoredCVFilename,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.white.withValues(alpha: 0.8),
                  ),
                ),
              ],
            ),
          ),
          _buildATSBadge(),
          const SizedBox(width: 16),
          IconButton(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(Icons.close, color: Colors.white),
            style: IconButton.styleFrom(
              backgroundColor: Colors.white.withOpacity(0.2),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildATSBadge() {
    final color = atsScore >= 80
        ? Colors.green
        : atsScore >= 60
            ? Colors.orange
            : Colors.red;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.analytics_outlined,
            size: 16,
            color: Colors.white,
          ),
          const SizedBox(width: 6),
          Text(
            'ATS: $atsScore%',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.w600,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildToolbar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      decoration: BoxDecoration(
        color: _isDarkMode ? const Color(0xFF2D2D2D) : const Color(0xFFF8F9FA),
        border: Border(
          bottom: BorderSide(
            color: _isDarkMode ? Colors.grey[700]! : Colors.grey[200]!,
          ),
        ),
      ),
      child: Row(
        children: [
          _buildToolbarButton(
            icon: Icons.copy_outlined,
            label: 'Copy',
            onPressed: _copyToClipboard,
          ),
          const SizedBox(width: 12),
          _buildToolbarButton(
            icon: Icons.download_outlined,
            label: 'Download',
            onPressed: _downloadCV,
          ),
          const SizedBox(width: 12),
          _buildToolbarButton(
            icon: Icons.refresh_outlined,
            label: 'Test ATS',
            onPressed: _rerunATSTest,
          ),
          const Spacer(),
          _buildFontSizeControls(),
          const SizedBox(width: 16),
          _buildThemeToggle(),
        ],
      ),
    );
  }

  Widget _buildToolbarButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 18,
                color: _isDarkMode ? Colors.grey[300] : Colors.grey[600],
              ),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                  color: _isDarkMode ? Colors.grey[300] : Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFontSizeControls() {
    return Row(
      children: [
        IconButton(
          onPressed: () =>
              setState(() => _fontSize = (_fontSize - 1).clamp(10, 20)),
          icon: Icon(Icons.text_decrease, size: 18),
          style: IconButton.styleFrom(
            minimumSize: const Size(32, 32),
            padding: EdgeInsets.zero,
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: _isDarkMode ? Colors.grey[700] : Colors.grey[200],
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            '${_fontSize.toInt()}',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: _isDarkMode ? Colors.grey[300] : Colors.grey[600],
            ),
          ),
        ),
        IconButton(
          onPressed: () =>
              setState(() => _fontSize = (_fontSize + 1).clamp(10, 20)),
          icon: Icon(Icons.text_increase, size: 18),
          style: IconButton.styleFrom(
            minimumSize: const Size(32, 32),
            padding: EdgeInsets.zero,
          ),
        ),
      ],
    );
  }

  Widget _buildThemeToggle() {
    return IconButton(
      onPressed: () => setState(() => _isDarkMode = !_isDarkMode),
      icon: Icon(
        _isDarkMode ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
        size: 18,
      ),
      style: IconButton.styleFrom(
        backgroundColor: _isDarkMode
            ? Colors.yellow.withOpacity(0.2)
            : Colors.grey.withOpacity(0.2),
        minimumSize: const Size(36, 36),
      ),
    );
  }

  Widget _buildContent() {
    if (isLoading) {
      return _buildLoadingState();
    }

    return Container(
      margin: const EdgeInsets.all(24),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _isDarkMode ? const Color(0xFF252525) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _isDarkMode ? Colors.grey[700]! : Colors.grey[200]!,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: SelectableText(
          previewText,
          style: TextStyle(
            fontSize: _fontSize,
            height: 1.6,
            color: _isDarkMode ? Colors.grey[100] : Colors.grey[800],
            fontFamily: 'monospace',
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: _isDarkMode
                  ? Colors.grey[800]!.withOpacity(0.5)
                  : Colors.grey[100],
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              children: [
                SizedBox(
                  width: 60,
                  height: 60,
                  child: CircularProgressIndicator(
                    strokeWidth: 3,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      _isDarkMode ? Colors.blue[300]! : Colors.blue[600]!,
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'Loading your CV preview...',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: _isDarkMode ? Colors.grey[300] : Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'This might take a few seconds',
                  style: TextStyle(
                    fontSize: 14,
                    color: _isDarkMode ? Colors.grey[400] : Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _isDarkMode ? const Color(0xFF2D2D2D) : const Color(0xFFF8F9FA),
        border: Border(
          top: BorderSide(
            color: _isDarkMode ? Colors.grey[700]! : Colors.grey[200]!,
          ),
        ),
      ),
      child: Center(
        child: Text(
          'Preview generated from: ${widget.tailoredCVFilename}',
          style: TextStyle(
            fontSize: 12,
            color: _isDarkMode ? Colors.grey[400] : Colors.grey[500],
          ),
        ),
      ),
    );
  }

  void _copyToClipboard() {
    Clipboard.setData(ClipboardData(text: previewText));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Row(
          children: [
            Icon(Icons.check_circle, color: Colors.white, size: 20),
            SizedBox(width: 8),
            Text('CV content copied to clipboard!'),
          ],
        ),
        backgroundColor: Colors.green[600],
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _downloadCV() {
    try {
      String baseFilename = widget.tailoredCVFilename;
      if (baseFilename.contains('.')) {
        baseFilename = baseFilename.substring(0, baseFilename.lastIndexOf('.'));
      }

      // Default to PDF download
      final url = 'http://localhost:8000/download-cv/$baseFilename/format/pdf';

      // Trigger download using dart:html
      html.window.open(url, '_blank');

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Row(
            children: [
              Icon(Icons.download, color: Colors.white, size: 20),
              SizedBox(width: 8),
              Text('Download started!'),
            ],
          ),
          backgroundColor: Colors.blue[600],
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          duration: const Duration(seconds: 2),
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Download failed: $e'),
          backgroundColor: Colors.red[600],
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      );
    }
  }

  Future<void> _rerunATSTest() async {
    // Show the animated ATS loading dialog
    showDialog(
      context: context,
      useRootNavigator: true,
      barrierDismissible: false,
      builder: (_) =>
          const CVGenerationDialog(type: CVGenerationType.atsRegeneration),
    );

    try {
      final atsService = ATSService();

      // Use standard LLM testing
      final result = await atsService.testATSCompatibility(
        cvFilename: widget.tailoredCVFilename,
        jdText: widget.jdText,
        cvType: 'tailored',
      );

      if (!context.mounted) return;
      if (context.mounted) {
        Navigator.pop(context); // Close ATS dialog
      }

      setState(() {
        atsScore = result.overallScore;
        isLoading = false;
      });

      // Close the current preview dialog
      Navigator.of(context).pop();

      // Show the full ATS result dialog
      await showDialog(
        context: context,
        useRootNavigator: true,
        builder: (context) {
          final additionalPromptController = TextEditingController();
          return StatefulBuilder(
            builder: (context, setState) {
              return AlertDialog(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                title: const Text('ATS Test Result'),
                contentPadding: const EdgeInsets.fromLTRB(24, 20, 24, 10),
                content: SizedBox(
                  width: double.maxFinite,
                  child: SingleChildScrollView(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('ATS Score: ${result.overallScore}%'),
                        const Divider(height: 24),
                        const TextField(
                          decoration: InputDecoration(
                            labelText: 'Additional improvements',
                            hintText: 'Enter additional instructions...',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Close'),
                  ),
                  ElevatedButton.icon(
                    icon: const Icon(Icons.refresh),
                    label: const Text('Regenerate CV'),
                    onPressed: () async {
                      final extra = additionalPromptController.text.trim();
                      if (extra.isEmpty) {
                        NotificationService.showError(
                          'Please provide additional instructions to improve your CV.',
                        );
                        return;
                      }

                      // Show loading dialog
                      showDialog(
                        context: context,
                        useRootNavigator: true,
                        barrierDismissible: false,
                        builder: (_) => const CVGenerationDialog(
                            type: CVGenerationType.atsImprovement),
                      );

                      try {
                        // 🚀 NEW: CV Evolution Engine Integration
                        debugPrint(
                            "🚀 [EVOLUTION] Starting AI-powered CV improvement analysis...");

                        // Step 1: Get intelligent improvement suggestions
                        final evolutionResponse = await http.post(
                          Uri.parse(
                              'http://localhost:8000/cv-evolution/analyze/'),
                          headers: {'Content-Type': 'application/json'},
                          body: json.encode({
                            'cv_filename': widget.tailoredCVFilename,
                            'jd_text': widget.jdText,
                            'gap_analysis': {
                              'overall_score': SessionState.lastATSScore ?? 35,
                            }
                          }),
                        );

                        if (evolutionResponse.statusCode == 200) {
                          final suggestions =
                              json.decode(evolutionResponse.body);
                          debugPrint(
                              "✅ [EVOLUTION] Received ${suggestions['suggestions']?.length ?? 0} improvement suggestions");

                          if (context.mounted) {
                            Navigator.pop(context); // Close loading

                            // Show evolution suggestions dialog
                            showDialog(
                              context: context,
                              builder: (context) => AlertDialog(
                                title: Row(
                                  children: [
                                    Icon(Icons.auto_awesome,
                                        color: Colors.purple),
                                    SizedBox(width: 8),
                                    Text("🚀 CV Evolution Engine"),
                                  ],
                                ),
                                content: Container(
                                  width: double.maxFinite,
                                  constraints: BoxConstraints(maxHeight: 500),
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      // Score improvement preview
                                      Container(
                                        padding: EdgeInsets.all(16),
                                        decoration: BoxDecoration(
                                          gradient: LinearGradient(
                                            colors: [
                                              Colors.blue.shade50,
                                              Colors.purple.shade50
                                            ],
                                          ),
                                          borderRadius:
                                              BorderRadius.circular(12),
                                        ),
                                        child: Row(
                                          mainAxisAlignment:
                                              MainAxisAlignment.spaceBetween,
                                          children: [
                                            Column(
                                              children: [
                                                Text("Current Score",
                                                    style: TextStyle(
                                                        fontWeight:
                                                            FontWeight.bold)),
                                                Text(
                                                    "${suggestions['current_score'] ?? 35}%",
                                                    style: TextStyle(
                                                        fontSize: 24,
                                                        color: Colors.blue)),
                                              ],
                                            ),
                                            Icon(Icons.arrow_forward, size: 32),
                                            Column(
                                              children: [
                                                Text("Potential Score",
                                                    style: TextStyle(
                                                        fontWeight:
                                                            FontWeight.bold)),
                                                Text(
                                                    "${suggestions['potential_score'] ?? 50}%",
                                                    style: TextStyle(
                                                        fontSize: 24,
                                                        color: Colors.green)),
                                              ],
                                            ),
                                          ],
                                        ),
                                      ),
                                      SizedBox(height: 16),

                                      // Improvement suggestions list
                                      Expanded(
                                        child: ListView.builder(
                                          itemCount: suggestions['suggestions']
                                                  ?.length ??
                                              0,
                                          itemBuilder: (context, index) {
                                            final suggestion =
                                                suggestions['suggestions']
                                                    [index];
                                            final priority =
                                                suggestion['priority'] ??
                                                    'medium';
                                            final impact = suggestion[
                                                    'predicted_impact'] ??
                                                0;

                                            return Card(
                                              margin:
                                                  EdgeInsets.only(bottom: 8),
                                              child: ListTile(
                                                leading: CircleAvatar(
                                                  backgroundColor:
                                                      priority == 'high'
                                                          ? Colors.red.shade100
                                                          : priority == 'medium'
                                                              ? Colors.orange
                                                                  .shade100
                                                              : Colors.blue
                                                                  .shade100,
                                                  child: Text(
                                                    "+$impact%",
                                                    style: TextStyle(
                                                      fontWeight:
                                                          FontWeight.bold,
                                                      color: priority == 'high'
                                                          ? Colors.red.shade700
                                                          : priority == 'medium'
                                                              ? Colors.orange
                                                                  .shade700
                                                              : Colors.blue
                                                                  .shade700,
                                                    ),
                                                  ),
                                                ),
                                                title: Text(
                                                  suggestion['title'] ??
                                                      'Improvement',
                                                  style: TextStyle(
                                                      fontWeight:
                                                          FontWeight.bold),
                                                ),
                                                subtitle: Text(
                                                    suggestion['description'] ??
                                                        ''),
                                                trailing: Container(
                                                  padding: EdgeInsets.symmetric(
                                                      horizontal: 8,
                                                      vertical: 4),
                                                  decoration: BoxDecoration(
                                                    color: priority == 'high'
                                                        ? Colors.red.shade100
                                                        : priority == 'medium'
                                                            ? Colors
                                                                .orange.shade100
                                                            : Colors
                                                                .blue.shade100,
                                                    borderRadius:
                                                        BorderRadius.circular(
                                                            12),
                                                  ),
                                                  child: Text(
                                                    priority.toUpperCase(),
                                                    style: TextStyle(
                                                      fontSize: 10,
                                                      fontWeight:
                                                          FontWeight.bold,
                                                      color: priority == 'high'
                                                          ? Colors.red.shade700
                                                          : priority == 'medium'
                                                              ? Colors.orange
                                                                  .shade700
                                                              : Colors.blue
                                                                  .shade700,
                                                    ),
                                                  ),
                                                ),
                                                onTap: () async {
                                                  // Apply single improvement
                                                  debugPrint(
                                                      "🔧 [EVOLUTION] Applying improvement: ${suggestion['title']}");
                                                  Navigator.pop(
                                                      context); // Close suggestions dialog

                                                  // Show loading
                                                  showDialog(
                                                    context: context,
                                                    barrierDismissible: false,
                                                    builder: (context) =>
                                                        AlertDialog(
                                                      content: Row(
                                                        children: [
                                                          CircularProgressIndicator(),
                                                          SizedBox(width: 16),
                                                          Text(
                                                              "Applying improvement..."),
                                                        ],
                                                      ),
                                                    ),
                                                  );

                                                  try {
                                                    // Generate improved CV
                                                    final improveResponse =
                                                        await http.post(
                                                      Uri.parse(
                                                          'http://localhost:8000/generate-tailored-cv/'),
                                                      headers: {
                                                        'Content-Type':
                                                            'application/json'
                                                      },
                                                      body: json.encode({
                                                        'cv_filename': widget
                                                            .tailoredCVFilename,
                                                        'jd_text':
                                                            widget.jdText,
                                                        'custom_prompt':
                                                            suggestion[
                                                                'prompt'],
                                                        'source':
                                                            'cv_evolution',
                                                        'use_last_tested': true,
                                                      }),
                                                    );

                                                    if (improveResponse
                                                            .statusCode ==
                                                        200) {
                                                      final result =
                                                          json.decode(
                                                              improveResponse
                                                                  .body);
                                                      debugPrint(
                                                          "✅ [EVOLUTION] Improvement applied: ${result['tailored_cv_filename']}");

                                                      if (context.mounted) {
                                                        Navigator.pop(
                                                            context); // Close loading

                                                        // Show success dialog
                                                        showDialog(
                                                          context: context,
                                                          builder: (context) =>
                                                              AlertDialog(
                                                            title: Row(
                                                              children: [
                                                                Icon(
                                                                    Icons
                                                                        .check_circle,
                                                                    color: Colors
                                                                        .green),
                                                                SizedBox(
                                                                    width: 8),
                                                                Text(
                                                                    "CV Evolved! 🎉"),
                                                              ],
                                                            ),
                                                            content: Column(
                                                              mainAxisSize:
                                                                  MainAxisSize
                                                                      .min,
                                                              children: [
                                                                Text(
                                                                    "Successfully applied: ${suggestion['title']}"),
                                                                SizedBox(
                                                                    height: 16),
                                                                Text(
                                                                    "New CV: ${result['tailored_cv_filename'] ?? 'Generated'}"),
                                                              ],
                                                            ),
                                                            actions: [
                                                              TextButton(
                                                                onPressed: () {
                                                                  Navigator.pop(
                                                                      context); // Close success dialog
                                                                  Navigator.pop(
                                                                      context); // Close original dialog
                                                                },
                                                                child: Text(
                                                                    "Continue"),
                                                              ),
                                                            ],
                                                          ),
                                                        );
                                                      }
                                                    } else {
                                                      throw Exception(
                                                          'Failed to apply improvement');
                                                    }
                                                  } catch (e) {
                                                    debugPrint(
                                                        "❌ [EVOLUTION] Error applying improvement: $e");
                                                    if (context.mounted) {
                                                      Navigator.pop(
                                                          context); // Close loading
                                                      ScaffoldMessenger.of(
                                                              context)
                                                          .showSnackBar(
                                                        SnackBar(
                                                            content: Text(
                                                                "Failed to apply improvement: $e")),
                                                      );
                                                    }
                                                  }
                                                },
                                              ),
                                            );
                                          },
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                actions: [
                                  TextButton(
                                    onPressed: () => Navigator.pop(context),
                                    child: Text("Cancel"),
                                  ),
                                  ElevatedButton.icon(
                                    onPressed: () async {
                                      // Apply top 3 improvements simultaneously
                                      debugPrint(
                                          "🚀 [EVOLUTION] Applying top improvements...");
                                      Navigator.pop(
                                          context); // Close suggestions dialog

                                      // Show loading
                                      showDialog(
                                        context: context,
                                        barrierDismissible: false,
                                        builder: (context) => AlertDialog(
                                          content: Row(
                                            children: [
                                              CircularProgressIndicator(),
                                              SizedBox(width: 16),
                                              Text("Optimizing CV..."),
                                            ],
                                          ),
                                        ),
                                      );

                                      try {
                                        final topSuggestions = (suggestions[
                                                'suggestions'] as List)
                                            .take(3)
                                            .map((s) => s['prompt'] as String)
                                            .toList();

                                        final optimizeResponse =
                                            await http.post(
                                          Uri.parse(
                                              'http://localhost:8000/cv-evolution/apply-best/'),
                                          headers: {
                                            'Content-Type': 'application/json'
                                          },
                                          body: json.encode({
                                            'cv_filename':
                                                widget.tailoredCVFilename,
                                            'selected_improvements':
                                                topSuggestions,
                                            'jd_text': widget.jdText,
                                          }),
                                        );

                                        if (optimizeResponse.statusCode ==
                                            200) {
                                          final result = json
                                              .decode(optimizeResponse.body);
                                          print(
                                              "🎉 [EVOLUTION] CV optimized: ${result['optimized_cv']}");

                                          if (context.mounted) {
                                            Navigator.pop(
                                                context); // Close loading

                                            // Show success dialog
                                            showDialog(
                                              context: context,
                                              builder: (context) => AlertDialog(
                                                title: Row(
                                                  children: [
                                                    Icon(Icons.auto_awesome,
                                                        color: Colors.purple),
                                                    SizedBox(width: 8),
                                                    Text("CV Optimized! 🚀"),
                                                  ],
                                                ),
                                                content: Column(
                                                  mainAxisSize:
                                                      MainAxisSize.min,
                                                  children: [
                                                    Text(
                                                        "Applied ${result['improvements_applied']} improvements"),
                                                    SizedBox(height: 16),
                                                    Text(
                                                        "Optimized CV: ${result['optimized_cv']}"),
                                                  ],
                                                ),
                                                actions: [
                                                  TextButton(
                                                    onPressed: () {
                                                      Navigator.pop(
                                                          context); // Close success dialog
                                                      Navigator.pop(
                                                          context); // Close original dialog
                                                    },
                                                    child: Text("Awesome!"),
                                                  ),
                                                ],
                                              ),
                                            );
                                          }
                                        } else {
                                          throw Exception(
                                              'Failed to optimize CV');
                                        }
                                      } catch (e) {
                                        print(
                                            "❌ [EVOLUTION] Error optimizing CV: $e");
                                        if (context.mounted) {
                                          Navigator.pop(
                                              context); // Close loading
                                          ScaffoldMessenger.of(context)
                                              .showSnackBar(
                                            SnackBar(
                                                content: Text(
                                                    "Failed to optimize CV: $e")),
                                          );
                                        }
                                      }
                                    },
                                    icon: Icon(Icons.rocket_launch),
                                    label: Text("Apply Top 3"),
                                  ),
                                ],
                              ),
                            );
                          }
                        } else {
                          throw Exception(
                              'Failed to get improvement suggestions');
                        }

                        // TODO: Remove old implementation below
                        await Future.delayed(const Duration(seconds: 2));
                        if (context.mounted) {
                          Navigator.pop(context); // Close loading
                          Navigator.pop(context); // Close ATS result
                        }
                      } catch (e) {
                        print("❌ [EVOLUTION] Error in CV Evolution: $e");
                        if (context.mounted) {
                          Navigator.pop(context); // Close loading
                          NotificationService.showError(
                            'Failed to analyze CV for improvements: $e',
                          );
                        }
                      }
                    },
                  ),
                ],
              );
            },
          );
        },
      );
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context); // Close loading dialog
        NotificationService.showError('ATS test failed: $e');
      }
    }
  }

  // ... rest of the existing methods would continue here
}
