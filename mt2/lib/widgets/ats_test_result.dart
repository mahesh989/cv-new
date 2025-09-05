import 'package:flutter/material.dart';
import '../services/api_service.dart' as api;
import '../services/ats_service.dart' as ats;
import '../services/generate_tailored_cv.dart';
import '../widgets/tailored_cv_preview_dialog.dart';
import '../dialogs/cv_generation_dialog.dart';
import '../state/session_state.dart';
import '../main.dart';
import '../theme/app_theme.dart';
import '../utils/notification_service.dart';

Future<void> showATSResultDialog({
  required BuildContext context,
  required ats.ATSResult atsResult,
  required String originalPrompt,
  required String cvFilename,
  required String jdText,
}) async {
  final additionalPromptController = TextEditingController();
  String currentCvFilename = cvFilename; // Track regenerated file

  await showDialog(
    context: context,
    useRootNavigator: true,
    builder: (context) {
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
                    const Text(
                      '📊 Summary:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text('✅ Keyword Match: ${atsResult.keywordMatch}%'),
                    Text('✅ Skills Match: ${atsResult.skillsMatch}%'),
                    Text('🎯 Overall Fit Score: ${atsResult.overallScore}/100'),
                    const Divider(height: 24),
                    const Text(
                      '🟩 Matched Technical Skills:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    _buildChipWrap(
                      atsResult.matchedHardSkills,
                      Colors.blue.shade100,
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      '🟩 Matched Soft Skills:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    _buildChipWrap(
                      atsResult.matchedSoftSkills,
                      Colors.purple.shade100,
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      '🟩 Matched Domain Keywords:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    _buildChipWrap(
                      atsResult.matchedDomainKeywords,
                      Colors.orange.shade100,
                    ),
                    const Divider(height: 24),
                    const Text(
                      '🟥 Missing Technical Skills:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    _buildChipWrap(
                      atsResult.missedHardSkills,
                      Colors.blue.shade100,
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      '🟥 Missing Soft Skills:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    _buildChipWrap(
                      atsResult.missedSoftSkills,
                      Colors.purple.shade100,
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      '🟥 Missing Domain Keywords:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    _buildChipWrap(
                      atsResult.missedDomainKeywords,
                      Colors.orange.shade100,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      '💡 Improvement Tips:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    atsResult.tips.isNotEmpty
                        ? Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: atsResult.tips
                                .map(
                                  (tip) => Padding(
                                    padding: const EdgeInsets.only(bottom: 6),
                                    child: Text('• $tip'),
                                  ),
                                )
                                .toList(),
                          )
                        : const Text('No tips available.'),
                    const SizedBox(height: 24),
                    const Text(
                      '🛠️ Add to Original Prompt:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: additionalPromptController,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        hintText: 'Enter extra instructions here...',
                      ),
                    ),
                  ],
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () {
                  debugPrint("🟥 [ATS] Dialog closed without action");
                  Navigator.pop(context);
                },
                child: const Text('Close'),
              ),
              ElevatedButton.icon(
                icon: const Icon(Icons.preview),
                label: const Text('Preview Tailored CV'),
                onPressed: () {
                  debugPrint("🟦 [ATS] Preview button clicked");
                  if (currentCvFilename.isEmpty ||
                      jdText.isEmpty ||
                      originalPrompt.isEmpty) {
                    NotificationService.showError("Missing required data");
                    return;
                  }
                  showDialog(
                    context: context,
                    builder: (_) => TailoredCVPreviewDialog(
                      tailoredCVFilename: currentCvFilename,
                      originalCVFilename: currentCvFilename,
                      jdText: jdText,
                      atsScore: atsResult.overallScore,
                    ),
                  );
                },
              ),
              ElevatedButton.icon(
                icon: const Icon(Icons.refresh),
                label: const Text('Regenerate & Preview'),
                onPressed: () async {
                  final additional = additionalPromptController.text.trim();

                  // Validate that additional prompt is not empty
                  if (additional.isEmpty) {
                    NotificationService.showError(
                        "Please provide additional instructions to improve your CV.");
                    return;
                  }

                  final combinedPrompt = "$originalPrompt\n\n$additional";

                  debugPrint("🟩 [ATS] Regenerate button clicked");
                  debugPrint("📄 [ATS] CV Filename: $currentCvFilename");
                  debugPrint("📄 [ATS] JD length: ${jdText.length}");
                  debugPrint("🧠 [ATS] Original Prompt: $originalPrompt");
                  debugPrint("🧠 [ATS] Additional Prompt: $additional");
                  debugPrint(
                    "🧠 [ATS] Combined Prompt Length: ${combinedPrompt.length}",
                  );

                  // Validate inputs
                  if (currentCvFilename.isEmpty ||
                      jdText.isEmpty ||
                      combinedPrompt.isEmpty) {
                    NotificationService.showError("Missing CV, JD, or prompt");
                    return;
                  }

                  // Show CV generation loading dialog
                  showDialog(
                    context: context,
                    useRootNavigator: true,
                    barrierDismissible: false,
                    builder: (_) => const CVGenerationDialog(
                        type: CVGenerationType.atsImprovement),
                  );

                  try {
                    debugPrint("🔄 [ATS] Starting CV regeneration...");
                    final service = TailoredCVService("http://localhost:8000");
                    final result = await service.generateTailoredCV(
                      cvFilename: currentCvFilename,
                      jdText: jdText,
                      prompt: combinedPrompt,
                      source: 'ats_regeneration',
                      jobLink: SessionState.jdUrl ?? '',
                    );

                    debugPrint(
                        "📥 [ATS] Server response: ${result.toString()}");

                    // Only use tailored_cv_filename returned from backend
                    final String? newFilename = result['tailored_cv_filename'];
                    if (newFilename == null || newFilename.isEmpty) {
                      debugPrint(
                          "❌ [ATS] Failed to extract filename from server response");
                      throw Exception(
                          "Missing or invalid tailored_cv_filename from server.");
                    }
                    debugPrint("✅ [ATS] New CV generated: $newFilename");

                    if (!context.mounted) {
                      debugPrint(
                          "⚠️ [ATS] Context not mounted after generation");
                      return;
                    }

                    Navigator.of(context).pop(); // close loading
                    Navigator.of(context).pop(); // close ATS dialog

                    await showDialog(
                      context: context,
                      useRootNavigator: true,
                      builder: (_) => TailoredCVPreviewDialog(
                        tailoredCVFilename: newFilename,
                        originalCVFilename: currentCvFilename,
                        jdText: jdText,
                        atsScore: 0,
                      ),
                    );

                    // Update currentCvFilename for next round/regeneration
                    setState(() {
                      currentCvFilename = newFilename;
                    });

                    NotificationService.showSuccess(
                      "CV regenerated successfully!",
                    );
                  } catch (e, stackTrace) {
                    debugPrint("❌ [ATS] Regeneration failed: $e");
                    debugPrint("🧵 [ATS] Stack trace: $stackTrace");

                    if (context.mounted) {
                      Navigator.of(context).pop(); // Remove loader
                      await showDialog(
                        context: context,
                        useRootNavigator: true,
                        builder: (ctx) => AlertDialog(
                          title: const Text('❌ Regeneration Failed'),
                          content: Text(
                            'An error occurred: ${e.toString()}',
                          ),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.of(ctx).pop(),
                              child: const Text('OK'),
                            ),
                          ],
                        ),
                      );
                    }

                    NotificationService.showError(
                      "Failed to regenerate CV: $e",
                    );
                  }
                },
              ),
              ElevatedButton.icon(
                icon: const Icon(Icons.save),
                label: const Text('Save This CV'),
                onPressed: () async {
                  debugPrint("💾 [ATS] Save CV button clicked");
                  try {
                    // Extract company name from JD text for proper naming
                    String company = 'Company';
                    final companyMatch = RegExp(
                            r'(?:company|organization|firm)[:\s]+([^\n\r.,]+)',
                            caseSensitive: false)
                        .firstMatch(jdText);
                    if (companyMatch != null) {
                      company = companyMatch.group(1)!.trim();
                    }

                    // Generate proper CV display name
                    final cvService =
                        TailoredCVService("http://localhost:8000");
                    String cvDisplayName;
                    try {
                      cvDisplayName = await cvService.generateCVName(company,
                          jdText, SessionState.jdUrl ?? 'N/A', context);
                    } catch (e) {
                      cvDisplayName =
                          '${company.replaceAll(RegExp(r'[^a-zA-Z0-9\s]'), '').replaceAll(RegExp(r'\s+'), '_')}_V1';
                    }

                    await cvService.saveJobApplication(
                      jobLink: SessionState.jdUrl?.isNotEmpty == true
                          ? SessionState.jdUrl!
                          : 'N/A',
                      jdText: jdText,
                      tailoredCvFilename: currentCvFilename,
                      applied: false,
                      cvDisplayName: cvDisplayName,
                    );
                    debugPrint(
                        "✅ [ATS] CV saved successfully as $cvDisplayName");
                    if (context.mounted) {
                      Navigator.pop(context);
                    }
                    NotificationService.showSuccess(
                      "✅ CV saved as $cvDisplayName!",
                    );
                  } catch (e, stackTrace) {
                    debugPrint("❌ [ATS] Failed to save CV: $e");
                    debugPrint("🧵 [ATS] Stack trace: $stackTrace");
                    NotificationService.showError(
                      "Failed to save job: ${e.toString()}",
                    );
                  }
                },
              ),
            ],
          );
        },
      );
    },
  );
}

Widget _buildChipWrap(List<String> items, Color backgroundColor) {
  if (items.isEmpty) {
    return const Text('No items found', style: TextStyle(color: Colors.grey));
  }

  return Wrap(
    spacing: 8,
    runSpacing: 8,
    children: items
        .map((item) {
          // Ensure atomic skills by splitting on common delimiters
          final skills = item
              .split(RegExp(r'[,;]'))
              .map((s) => s.trim())
              .where((s) => s.isNotEmpty);
          return skills
              .map((skill) => Chip(
                    label: Text(
                      skill,
                      style: const TextStyle(fontSize: 12),
                    ),
                    backgroundColor: backgroundColor,
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  ))
              .toList();
        })
        .expand((x) => x)
        .toList(),
  );
}

class ATSTestResult extends StatelessWidget {
  final ats.ATSResult result;

  const ATSTestResult({super.key, required this.result});

  Widget _buildSkillSection(String title, List<String> skills, Color color) {
    if (skills.isEmpty || (skills.length == 1 && skills[0] == 'N/A')) {
      return const SizedBox.shrink();
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: skills
              .map((skill) => Chip(
                    label: Text(skill),
                    backgroundColor: color,
                  ))
              .toList(),
        ),
        const SizedBox(height: 16),
      ],
    );
  }

  Widget _buildScoreCircle(String label, int score, Color color) {
    return Column(
      children: [
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withOpacity(0.1),
            border: Border.all(color: color, width: 2),
          ),
          child: Center(
            child: Text(
              '$score%',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'ATS Test Result',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),

          // Overall Scores
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '📊 Overall Scores',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildScoreCircle(
                        'Keyword Match',
                        result.keywordMatch,
                        Colors.blue,
                      ),
                      _buildScoreCircle(
                        'Skills Match',
                        result.skillsMatch,
                        Colors.green,
                      ),
                      _buildScoreCircle(
                        'Overall Score',
                        result.overallScore,
                        Colors.purple,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // JD Analysis
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '📋 Job Description Analysis',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  _buildSkillSection(
                    'Technical Skills',
                    result.jdTechnicalSkills,
                    Colors.blue.shade100,
                  ),
                  _buildSkillSection(
                    'Soft Skills',
                    result.jdSoftSkills,
                    Colors.purple.shade100,
                  ),
                  _buildSkillSection(
                    'Domain Keywords',
                    result.jdDomainKeywords,
                    Colors.orange.shade100,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Matching Results
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '🎯 Matching Results',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  _buildSkillSection(
                    'Matched Technical Skills',
                    result.matchedHardSkills,
                    Colors.blue.shade100,
                  ),
                  _buildSkillSection(
                    'Matched Soft Skills',
                    result.matchedSoftSkills,
                    Colors.purple.shade100,
                  ),
                  _buildSkillSection(
                    'Missed Technical Skills',
                    result.missedHardSkills,
                    Colors.blue.shade100,
                  ),
                  _buildSkillSection(
                    'Missed Soft Skills',
                    result.missedSoftSkills,
                    Colors.purple.shade100,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Detailed Scores
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '📈 Detailed Scores',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 16),
                  // Simplified scores display
                  Text(
                      'Technical Skills: ${result.matchedHardSkills.length} matched, ${result.missedHardSkills.length} missed'),
                  Text(
                      'Soft Skills: ${result.matchedSoftSkills.length} matched, ${result.missedSoftSkills.length} missed'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Gaps and Tips
          if (result.gaps.isNotEmpty || result.tips.isNotEmpty)
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (result.gaps.isNotEmpty) ...[
                      const Text(
                        '⚠️ Identified Gaps',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      ...result.gaps.map((gap) => Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Icon(Icons.warning_amber_rounded,
                                    size: 16),
                                const SizedBox(width: 8),
                                Expanded(child: Text(gap)),
                              ],
                            ),
                          )),
                      const SizedBox(height: 16),
                    ],
                    if (result.tips.isNotEmpty) ...[
                      const Text(
                        '💡 Improvement Tips',
                        style: TextStyle(
                            fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      ...result.tips.map((tip) => Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Icon(Icons.lightbulb_outline, size: 16),
                                const SizedBox(width: 8),
                                Expanded(child: Text(tip)),
                              ],
                            ),
                          )),
                    ],
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}
