import 'package:flutter/material.dart';
import '../services/generate_tailored_cv.dart';
import '../dialogs/cv_generation_dialog.dart';
import '../utils/notification_service.dart';
import 'package:url_launcher/url_launcher.dart';

class TailoredCVRegenDialog extends StatefulWidget {
  final String cvFilename;
  final String jdText;
  final String initialPrompt;
  final String initialPreview;
  final String initialDownloadLink;
  final TailoredCVService tailoredCVService;
  final String jobLink;

  const TailoredCVRegenDialog({
    super.key,
    required this.cvFilename,
    required this.jdText,
    required this.initialPrompt,
    required this.initialPreview,
    required this.initialDownloadLink,
    required this.tailoredCVService,
    required this.jobLink,
  });

  @override
  State<TailoredCVRegenDialog> createState() => _TailoredCVRegenDialogState();
}

class _TailoredCVRegenDialogState extends State<TailoredCVRegenDialog> {
  late TextEditingController _promptController;
  String preview = '';
  String downloadLink = '';
  String latestTailoredCVFilename = '';
  Map<String, dynamic>? atsResult;
  bool isATSLoading = false;

  @override
  void initState() {
    super.initState();
    _promptController = TextEditingController(text: widget.initialPrompt);
    preview = widget.initialPreview;
    downloadLink = widget.initialDownloadLink;
    // Extract tailored filename from download link (e.g., .../download-cv/tailored_xxx.docx)
    final uri = Uri.tryParse(widget.initialDownloadLink);
    if (uri != null && uri.pathSegments.isNotEmpty) {
      latestTailoredCVFilename = uri.pathSegments.last;
    } else {
      latestTailoredCVFilename = widget.cvFilename; // fallback
    }
  }

  void _dismissLoadingAndReset() {
    debugPrint('[REGEN] _dismissLoadingAndReset called');
    if (Navigator.canPop(context)) {
      Navigator.of(context).pop(); // Dismiss loading dialog
    }
    if (mounted) {
      setState(() {
        // Reset any loading states if needed
      });
    }
  }

  Future<void> _runATSTest() async {
    setState(() {
      isATSLoading = true;
      atsResult = null;
    });
    debugPrint('[ATS] Started ATS test for $latestTailoredCVFilename');
    try {
      final result = await widget.tailoredCVService.runATSTest(
        cvFilename: latestTailoredCVFilename,
        jdText: widget.jdText,
        cvType: 'tailored',
      );
      debugPrint('[ATS] Received ATS result: ${result.toString()}');
      setState(() {
        atsResult = result;
        isATSLoading = false;
      });
      debugPrint('[ATS] setState called, UI should update now.');
    } catch (e) {
      setState(() {
        isATSLoading = false;
      });
      debugPrint('[ATS] Error running ATS test: ${e.toString()}');
      if (!mounted) return;
      showDialog(
        context: context,
        useRootNavigator: true,
        builder: (context) => AlertDialog(
          title: const Text('Error'),
          content: Text('Failed to run ATS test: $e'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  Future<void> _regenerateCV() async {
    debugPrint('[REGEN] _regenerateCV method called');
    debugPrint('[REGEN] Prompt text: ${_promptController.text.trim()}');

    if (_promptController.text.trim().isEmpty) {
      NotificationService.showError(
          'Please provide additional instructions for CV tailoring');
      return;
    }

    debugPrint('[REGEN] Showing loading dialog');
    // Show animated loading dialog
    showDialog(
      context: context,
      useRootNavigator: true,
      barrierDismissible: false,
      builder: (_) =>
          const CVGenerationDialog(type: CVGenerationType.atsImprovement),
    );

    try {
      // Extract company name from JD text for proper naming
      String company = 'Company';
      final companyMatch = RegExp(
              r'(?:company|organization|firm)[:\s]+([^\n\r.,]+)',
              caseSensitive: false)
          .firstMatch(widget.jdText);
      if (companyMatch != null) {
        company = companyMatch.group(1)!.trim();
      }

      // Generate proper CV display name
      String cvDisplayName = await widget.tailoredCVService
          .generateCVName(company, widget.jdText, widget.jobLink, context);

      final result = await widget.tailoredCVService.generateTailoredCV(
        cvFilename: cvDisplayName,
        jdText: widget.jdText,
        prompt: _promptController.text,
        source: 'regeneration',
        useLastTested: true,
        jobLink: widget.jobLink,
      );

      if (!mounted) return;
      Navigator.of(context).pop();

      debugPrint('[REGEN] Received result: ${result.toString()}');
      debugPrint('[REGEN] Preview length: ${result['preview']?.length ?? 0}');
      debugPrint('[REGEN] Download link: ${result['downloadLink']}');
      debugPrint('[REGEN] Filename: ${result['tailored_cv_filename']}');

      setState(() {
        preview = result['preview'] ?? 'No preview available';
        downloadLink = result['downloadLink'] ?? '';
        latestTailoredCVFilename = result['tailored_cv_filename'] ?? '';
        atsResult = null; // Clear previous ATS result
      });

      debugPrint('[REGEN] setState called, preview length: ${preview.length}');
      debugPrint('[REGEN] downloadLink: $downloadLink');

      if (downloadLink.isEmpty) {
        throw Exception("❌ Download link missing in the response.");
      }

      NotificationService.showSuccess(
        "CV regenerated successfully!",
      );
    } catch (e) {
      debugPrint('[REGEN] Error occurred: $e');
      if (!mounted) return;
      Navigator.of(context).pop();
      if (!mounted) return;
      showDialog(
        context: context,
        useRootNavigator: true,
        builder: (context) => AlertDialog(
          title: const Text('Error'),
          content: Text('Failed to regenerate CV: $e'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  Future<void> _saveCV() async {
    try {
      // Extract company name from JD text for proper naming
      String company = 'Company';
      final companyMatch = RegExp(
              r'(?:company|organization|firm)[:\s]+([^\n\r.,]+)',
              caseSensitive: false)
          .firstMatch(widget.jdText);
      if (companyMatch != null) {
        company = companyMatch.group(1)!.trim();
      }

      // Generate proper CV display name
      String cvDisplayName;
      try {
        cvDisplayName = await widget.tailoredCVService
            .generateCVName(company, widget.jdText, widget.jobLink, context);
      } catch (e) {
        cvDisplayName =
            '${company.replaceAll(RegExp(r'[^a-zA-Z0-9\s]'), '').replaceAll(RegExp(r'\s+'), '_')}_V1';
      }

      await widget.tailoredCVService.saveJobApplication(
        jobLink: widget.jobLink,
        jdText: widget.jdText,
        tailoredCvFilename: latestTailoredCVFilename,
        applied: false,
        cvDisplayName: cvDisplayName,
      );
      if (!mounted) return;
      showDialog(
        context: context,
        useRootNavigator: true,
        builder: (context) => AlertDialog(
          title: const Text('Success'),
          content: Text('CV saved as $cvDisplayName!'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    } catch (e) {
      if (!mounted) return;
      showDialog(
        context: context,
        useRootNavigator: true,
        builder: (context) => AlertDialog(
          title: const Text('Error'),
          content: Text('Failed to save CV: $e'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Tailored CV Preview & Optimization'),
      content: SizedBox(
        width: 550,
        height: 600,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // CV Preview
            const Text('🔍 CV Preview:',
                style: TextStyle(fontWeight: FontWeight.bold)),
            Expanded(
              child: Container(
                margin: const EdgeInsets.symmetric(vertical: 8),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: SingleChildScrollView(child: Text(preview)),
              ),
            ),
            // Download Button (if download link is available)
            if (downloadLink.isNotEmpty) ...[
              const SizedBox(height: 8),
              ElevatedButton.icon(
                onPressed: () async {
                  final Uri downloadUri = Uri.parse(downloadLink);
                  if (await canLaunchUrl(downloadUri)) {
                    await launchUrl(downloadUri);
                  } else {
                    if (!mounted) return;
                    showDialog(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Error'),
                        content: const Text('Could not launch download link'),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.of(context).pop(),
                            child: const Text('OK'),
                          ),
                        ],
                      ),
                    );
                  }
                },
                icon: const Icon(Icons.download),
                label: const Text("Download CV"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
            // ATS Test Button
            ElevatedButton.icon(
              onPressed: _runATSTest,
              icon: const Icon(Icons.analytics),
              label: const Text("ATS TEST"),
            ),
            // ATS Results
            if (isATSLoading) ...[
              const SizedBox(height: 16),
              const Center(child: CircularProgressIndicator()),
              const Text('Running ATS test...'),
            ] else if (atsResult != null) ...[
              const SizedBox(height: 16),
              Text('ATS Results:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              Text('Overall Score: ${atsResult!["overall_score"]}%'),
              // Add more fields as needed, e.g. matched/missed skills, tips, etc.
              if (atsResult!["tips"] != null) ...[
                const SizedBox(height: 8),
                Text('Tips:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...List<Widget>.from(
                    (atsResult!["tips"] as List).map((tip) => Text('- $tip'))),
              ]
            ],
            // Additional Prompt
            const SizedBox(height: 16),
            const Text('✏️ Additional Instructions:',
                style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _promptController,
              maxLines: 3,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Enter additional instructions for CV improvement...',
              ),
            ),
            const SizedBox(height: 12),
            ElevatedButton.icon(
              onPressed: _regenerateCV,
              icon: const Icon(Icons.refresh),
              label: const Text('Regenerate CV'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text("Close"),
        ),
        ElevatedButton.icon(
          onPressed: _saveCV,
          icon: const Icon(Icons.save),
          label: const Text("Save to Jobs Table"),
        ),
      ],
    );
  }
}
