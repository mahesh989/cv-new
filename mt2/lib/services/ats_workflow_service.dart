import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/ats_service.dart';
import '../services/generate_tailored_cv.dart';
import '../services/llm_service.dart';
import '../state/session_state.dart';
import '../models/ats_models.dart';
import '../utils/notification_service.dart';
import '../pages/multi_job_ats_dashboard.dart';

class ATSWorkflowService {
  // Use localhost for development, change to production URL when deploying
  static const String _baseUrl = 'http://localhost:8000';
  final ATSService _atsService = ATSService();
  final TailoredCVService _cvService = TailoredCVService(_baseUrl);

  // Initialize and determine the initial state based on session data
  ATSWorkflowState determineInitialState() {
    // Check if this is a new job by comparing current JD URL with stored one
    final currentJobUrl = SessionState.jdUrl ?? '';
    final storedJobUrl = SessionState.lastJobUrl ?? '';

    debugPrint("🔍 [WORKFLOW] Checking job change:");
    debugPrint("📄 [WORKFLOW] Current job URL: $currentJobUrl");
    debugPrint("📄 [WORKFLOW] Stored job URL: $storedJobUrl");

    // Only reset if we have a DIFFERENT non-empty URL
    final isActuallyNewJob = currentJobUrl.isNotEmpty &&
        storedJobUrl.isNotEmpty &&
        currentJobUrl != storedJobUrl;

    if (isActuallyNewJob) {
      debugPrint("🆕 [WORKFLOW] New job detected! Starting fresh...");
      return ATSWorkflowState.initial;
    }

    // If same job and we have SessionState data indicating completed workflow, show portfolio
    if (SessionState.tailoredCVFilename?.isNotEmpty == true &&
        currentJobUrl == storedJobUrl &&
        currentJobUrl.isNotEmpty) {
      debugPrint("🔄 [WORKFLOW] Restoring previous session for same job");
      return ATSWorkflowState.cvGenerated;
    }

    debugPrint("🆕 [WORKFLOW] Ready for ATS testing - showing initial state");
    return ATSWorkflowState.initial;
  }

  // Reset session for new job
  void resetForNewJob() {
    debugPrint("🔄 [WORKFLOW] Resetting for new job...");

    // Clear session state for new job
    SessionState.tailoredCVFilename = null;
    // Update stored job URL to current one
    SessionState.lastJobUrl = SessionState.jdUrl;
    // Save the updated session state to disk
    SessionState.saveToDisk();

    debugPrint("✅ [WORKFLOW] Session reset complete for new job");
  }

  // Run ATS test on a CV
  Future<ATSResult> runATSTest({
    required String cvFilename,
    required String jdText,
    required String cvType,
  }) async {
    debugPrint("🚀 [WORKFLOW] Starting ATS test on $cvFilename");

    final atsResult = await _atsService.testATSCompatibility(
      cvFilename: cvFilename,
      jdText: jdText,
      cvType: cvType,
    );

    debugPrint(
        "✅ [WORKFLOW] ATS test completed. Score: ${atsResult.overallScore}%");
    return atsResult;
  }

  // Generate tailored CV
  Future<String> generateTailoredCV({
    required String cvFilename,
    required String jdText,
    required String additionalPrompt,
    required bool useLastTested,
  }) async {
    debugPrint("🚀 [WORKFLOW] Starting CV generation");
    debugPrint("💬 [WORKFLOW] Additional prompt: $additionalPrompt");
    debugPrint("📄 [WORKFLOW] Base CV: $cvFilename");
    debugPrint("🔍 [WORKFLOW] useLastTested: $useLastTested");

    final basePrompt = SessionState.customPrompts['cv_generation'] ??
        'Generate a tailored CV based on the job description and additional instructions.';
    final combinedPrompt =
        '$basePrompt\n\nADDITIONAL INSTRUCTIONS:\n$additionalPrompt';

    // Use the real job link if available from SessionState
    String jobLink = SessionState.jdUrl ??
        "Manual Save - ${DateTime.now().millisecondsSinceEpoch}";

    final result = await _cvService.generateTailoredCV(
      cvFilename: cvFilename,
      jdText: jdText,
      prompt: combinedPrompt,
      source: 'ats_workflow',
      useLastTested: useLastTested,
      jobLink: jobLink,
    );

    final newTailoredCV = result['tailored_cv_filename'] ?? '';
    debugPrint("📄 [WORKFLOW] New CV filename: $newTailoredCV");

    if (newTailoredCV.isNotEmpty) {
      SessionState.tailoredCVFilename = newTailoredCV;
    }

    return newTailoredCV;
  }

  // Get CV content for preview (for PDF files, this just returns a placeholder)
  Future<String> getCVContent(String cvName) async {
    try {
      // For PDF files, we don't need to fetch text content
      // The PDF viewer will handle displaying the PDF directly
      if (cvName.endsWith('.pdf')) {
        return 'PDF content available for viewing';
      }

      // For legacy .docx files, try the old endpoint
      final response = await http.get(
        Uri.parse('http://localhost:8000/tailored-cvs/$cvName'),
      );
      if (response.statusCode == 200) {
        return response.body;
      } else {
        return 'Failed to load CV content';
      }
    } catch (e) {
      return 'Error loading CV content: $e';
    }
  }

  // Save ATS result to multi-job dashboard
  Future<void> saveToMultiJobDashboard(
      ATSResult atsResult, String cvName, String jdText) async {
    try {
      debugPrint('💾 [WORKFLOW] Saving to multi-job dashboard');

      String jobId = SessionState.jdUrl ?? '';
      String jobTitle = 'Unknown Position';
      String company = 'Unknown Company';

      if (jdText.isNotEmpty) {
        try {
          final llmService = LLMService();
          final jobInfo = await llmService.extractJobInformation(
            jobDescription: jdText,
          );

          if (jobInfo['jobTitle'] != null && jobInfo['jobTitle']!.isNotEmpty) {
            jobTitle = jobInfo['jobTitle']!;
          }
          if (jobInfo['company'] != null && jobInfo['company']!.isNotEmpty) {
            company = jobInfo['company']!;
          }
        } catch (e) {
          debugPrint('❌ [WORKFLOW] LLM extraction failed: $e');
        }
      }

      // Create consistent job identifier if URL is not available
      if (jobId.isEmpty) {
        final normalizedTitle =
            jobTitle.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '');
        final normalizedCompany =
            company.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '');
        jobId = '${normalizedCompany}_${normalizedTitle}';
      }

      // Calculate match rate
      final totalMatched = atsResult.matchedHardSkills.length +
          atsResult.matchedSoftSkills.length;
      final totalMissed =
          atsResult.missedHardSkills.length + atsResult.missedSoftSkills.length;
      final totalSkills = totalMatched + totalMissed;
      final matchRate = totalSkills > 0
          ? '${(totalMatched / totalSkills * 100).round()}%'
          : '0%';

      final jobUrlForDashboard =
          (SessionState.jdUrl?.startsWith('http') == true)
              ? SessionState.jdUrl!
              : jobId;

      await MultiJobATSDashboard.addATSResult(
        jobUrl: jobUrlForDashboard,
        jobTitle: jobTitle,
        company: company,
        atsScore: atsResult.overallScore,
        matchedSkills:
            atsResult.matchedHardSkills + atsResult.matchedSoftSkills,
        missedSkills: atsResult.missedHardSkills + atsResult.missedSoftSkills,
        matchRate: matchRate,
      );

      debugPrint('✅ [WORKFLOW] ATS result saved to multi-job dashboard');
    } catch (e) {
      debugPrint('❌ [WORKFLOW] Error saving to multi-job dashboard: $e');
    }
  }

  // Save job application to jobs table
  Future<void> saveToJobsTable({
    required String cvName,
    required String jdText,
    required String originalCVName,
    ATSResult? atsResult,
  }) async {
    debugPrint("💾 [WORKFLOW] Starting save process for CV: $cvName");

    if (jdText.isEmpty || cvName.isEmpty) {
      throw Exception(
          'Missing CV or Job Description for saving! Please go to CV tab and add job description first.');
    }

    // Use latestATSResult for metadata if available
    Map<String, dynamic> cvMetadata = {};
    int? atsScore;
    if (atsResult != null) {
      cvMetadata = {
        'matched_hard_skills': atsResult.matchedHardSkills,
        'matched_soft_skills': atsResult.matchedSoftSkills,
        'missed_hard_skills': atsResult.missedHardSkills,
        'missed_soft_skills': atsResult.missedSoftSkills,
        'length': 0,
      };
      atsScore = atsResult.overallScore;
    }

    String jobLink = SessionState.jdUrl ??
        "Manual Save - ${DateTime.now().millisecondsSinceEpoch}";

    await _cvService.saveJobApplication(
      jobLink: jobLink,
      jdText: jdText,
      tailoredCvFilename: cvName,
      applied: false,
      originalCv: originalCVName,
      cvMetadata: cvMetadata,
      atsScore: atsScore,
      generationSource: 'manual_save',
      cvDisplayName: cvName,
    );

    debugPrint('✅ [WORKFLOW] Job saved successfully to jobs table: $cvName');
    NotificationService.showSuccess('✅ Job saved successfully as $cvName!');
  }
}
