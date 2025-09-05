import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import '../dialogs/custom_popup.dart';
import '../dialogs/save_job_dialog.dart';
import '../helpers/session_updater.dart';
import '../dialogs/duplicate_cv_dialog.dart';
import 'dart:math' show max;
import 'ats_service.dart';

enum DuplicateCVAction {
  replace,
  newVersion,
  cancel,
}

class TailoredCVService {
  // Use localhost for development, change to production URL when deploying
  static const String _baseUrl = 'http://localhost:8000';
  final String baseUrl;

  TailoredCVService([this.baseUrl = _baseUrl]);

  // 🧠 Generate tailored CV only
  // generate_tailored_cv.dart
  Future<Map<String, String>> generateTailoredCV({
    required String cvFilename,
    required String jdText,
    required String prompt,
    String source = 'initial',
    bool useLastTested = false,
    String? jobLink,
  }) async {
    debugPrint("📤 Sending CV with source: $source");
    debugPrint("🔄 [CV] Starting CV generation with source: $source");
    debugPrint("📄 CV Filename: $cvFilename");
    debugPrint("📄 JD length: ${jdText.length}");
    debugPrint("🧠 Prompt length: ${prompt.length}");
    debugPrint("🔄 Use Last Tested: $useLastTested");

    try {
      // Check if we're generating a new CV or modifying an existing one
      // For first time generation: use original CV (isNewCV = false, useLastTested = false)
      // For improvements: use tailored CV (isNewCV = false, useLastTested = true)
      // Only for completely new CV creation without any base: isNewCV = true
      final isNewCV = source == 'initial' && !useLastTested;

      debugPrint("🔍 [CV] Generation Logic:");
      debugPrint("   - Source: $source");
      debugPrint("   - Use Last Tested: $useLastTested");
      debugPrint("   - Is New CV: $isNewCV");
      debugPrint(
          "   - Expected Base: ${useLastTested ? 'Tailored CV' : 'Original CV'}");

      final response = await http
          .post(
            Uri.parse('$baseUrl/generate-tailored-cv/'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'cv_filename': cvFilename,
              'jd_text': jdText,
              'custom_prompt': prompt,
              'source': source,
              'use_last_tested': useLastTested,
              'is_new_cv': isNewCV, // Add flag to indicate if this is a new CV
              'job_link': jobLink ?? '',
            }),
          )
          .timeout(const Duration(seconds: 120));

      debugPrint("📥 Server response: ${response.statusCode}");
      debugPrint("📥 Response body: ${response.body}");

      if (response.statusCode != 200) {
        final errorBody = json.decode(response.body);
        final errorMessage = errorBody['error'] ?? 'Unknown server error';
        throw Exception('Failed to generate tailored CV: $errorMessage');
      }

      final data = json.decode(response.body) as Map<String, dynamic>;
      debugPrint("📦 Response data: ${data.toString()}");

      if (!data.containsKey('tailored_cv_filename')) {
        throw Exception(
            "Server response missing required 'tailored_cv_filename' field");
      }

      final filename = data['tailored_cv_filename'] as String?;
      if (filename == null || filename.isEmpty) {
        throw Exception("Server returned empty or null filename");
      }

      debugPrint("✅ [CV] Successfully generated tailored CV:");
      debugPrint("   - Source: $source");
      debugPrint("   - Original CV: $cvFilename");
      debugPrint("   - New CV: $filename");
      debugPrint("   - Use Last Tested: $useLastTested");
      debugPrint("   - Is New CV: $isNewCV");

      // Preview is now handled directly by the PDF generation
      final previewText = 'PDF preview available';

      SessionUpdater.updateTailoredCV(filename);
      SessionUpdater.updatePrompt(prompt);

      return {
        'preview': previewText,
        'downloadLink': '$baseUrl/download-cv/$filename',
        'tailored_cv_filename': filename,
      };
    } catch (e, stackTrace) {
      debugPrint("❌ CV generation failed: $e");
      debugPrint("🧵 Stack trace: $stackTrace");
      rethrow;
    }
  }

  // 🧠 Update a specific job's CV display name (fallback method)
  Future<void> _updateJobCVName(String jobId, String newCvName) async {
    // This method is kept for potential future backend support
    final response = await http.patch(
      Uri.parse('$baseUrl/update-cv-name/$jobId'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'cv_display_name': newCvName,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('❌ Failed to update CV name for job $jobId.');
    }
  }

  // 🧠 Check if CV name exists and get its details
  Future<Map<String, dynamic>?> checkExistingCV(String cvName) async {
    try {
      final existingJobs = await fetchSavedJobs();
      final existingCV = existingJobs.firstWhere(
        (job) => job['cv_display_name'] == cvName,
        orElse: () => {},
      );
      return existingCV.isNotEmpty ? existingCV : null;
    } catch (e) {
      debugPrint('Error checking existing CV: $e');
      return null;
    }
  }

  // 🧠 Generate a proper CV name based on company and existing versions
  Future<String> generateCVName(String company, String jdText, String jobLink,
      BuildContext context) async {
    // Clean company name
    String cleanCompany = company.replaceAll(RegExp(r'[^a-zA-Z0-9]'), '');
    if (cleanCompany.isEmpty) {
      cleanCompany = 'Company';
    }

    try {
      // Let the backend handle the versioning by passing the company name and job link
      final response = await http.post(
        Uri.parse('$baseUrl/generate-cv-name/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'company': cleanCompany,
          'job_link': jobLink,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['filename'];
      } else {
        throw Exception('Failed to generate CV name: ${response.statusCode}');
      }
    } catch (e) {
      debugPrint('❌ Error generating CV name: $e');
      // Fallback to a timestamp-based name if something goes wrong
      return '${cleanCompany}_${DateTime.now().millisecondsSinceEpoch}.docx';
    }
  }

  // 🧠 Save a job manually with comprehensive metadata
  Future<void> saveJobApplication({
    required String jobLink,
    required String jdText,
    required String tailoredCvFilename,
    required bool applied,
    String? originalCv,
    Map<String, dynamic>? cvMetadata,
    int? atsScore,
    String? generationSource,
    String? cvDisplayName,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/save-job/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'job_link': jobLink,
        'jd_text': jdText,
        'tailored_cv': tailoredCvFilename,
        'applied': applied,
        'original_cv': originalCv ?? '',
        'cv_metadata': cvMetadata ?? {},
        'ats_score': atsScore ?? 0,
        'generation_source': generationSource ?? 'manual',
        'cv_display_name': cvDisplayName ?? tailoredCvFilename,
      }),
    );

    if (response.statusCode != 200) {
      throw Exception('❌ Failed to save job application.');
    }
  }

  // 🧠 Fetch all saved jobs - combines both regular saved jobs AND ATS dashboard results
  Future<List<Map<String, dynamic>>> fetchSavedJobs() async {
    List<Map<String, dynamic>> allJobs = [];

    try {
      // 1. Fetch regular saved jobs from /jobs/
      final regularJobsResponse = await http.get(Uri.parse('$baseUrl/jobs/'));
      if (regularJobsResponse.statusCode == 200) {
        final List regularJobs = json.decode(regularJobsResponse.body);
        print('📊 Found ${regularJobs.length} regular saved jobs');

        // Convert regular jobs to consistent format
        for (var job in regularJobs) {
          allJobs.add({
            'sn': job['sn'] ?? 'unknown',
            'company': job['company'] ?? 'Unknown Company',
            'role': 'Job Application', // Regular jobs don't have specific role
            'level': 'Not specified',
            'industry': 'Not specified',
            'work_type': 'Not specified',
            'phone': job['phone'] ?? 'Not found',
            'date_applied':
                job['date_applied'] ?? DateTime.now().toString().split(' ')[0],
            'location': job['location'] ?? 'Not specified',
            'job_link': job['job_link'] ?? '',
            'tailored_cv': job['tailored_cv'] ?? 'Unknown CV',
            'original_cv': '',
            'applied': job['applied'] ?? false,
            'ats_score': 0, // Regular jobs don't have ATS scores
            'generation_source': 'regular_job',
            'key_skills': [],
            'cv_display_name': job['tailored_cv'] ?? 'Unknown CV',
          });
        }
      } else {
        print(
            '⚠️ Failed to fetch regular jobs: ${regularJobsResponse.statusCode}');
      }
    } catch (e) {
      print('❌ Error fetching regular jobs: $e');
    }

    try {
      // 2. Fetch ATS dashboard results from /ats-dashboard/results/
      final atsResponse =
          await http.get(Uri.parse('$baseUrl/ats-dashboard/results/'));
      if (atsResponse.statusCode == 200) {
        final List atsData = json.decode(atsResponse.body);
        print('📊 Found ${atsData.length} ATS dashboard results');

        // Convert ATS results to consistent format
        for (var item in atsData) {
          allJobs.add({
            'sn': item['jobId'],
            'company': item['company'],
            'role': item['jobTitle'], // Use actual job title from ATS dashboard
            'level': 'Not specified',
            'industry': 'Not specified',
            'work_type': 'Not specified',
            'phone': 'Not found', // Not available in ATS dashboard
            'date_applied': item['testDate']?.split('T')[0] ??
                DateTime.now().toString().split(' ')[0], // Extract date part
            'location': 'Not specified', // Not available in ATS dashboard
            'job_link': item['metadata']?['originalJobUrl'] ??
                item['jobId'], // Use original job URL if available
            'tailored_cv': item['cvName'], // Use CV name from ATS dashboard
            'original_cv': '', // Not tracked in ATS dashboard
            'applied': false, // Not tracked in ATS dashboard
            'ats_score': item['atsScore'] ?? 0,
            'generation_source': 'ats_dashboard',
            'key_skills': item['matchedSkills'] ?? [],
            'cv_display_name': item['cvName'],
            'generation_details': {
              'matched_skills': item['matchedSkills'] ?? [],
              'missed_skills': item['missedSkills'] ?? [],
            },
          });
        }
      } else {
        print('⚠️ Failed to fetch ATS results: ${atsResponse.statusCode}');
      }
    } catch (e) {
      print('❌ Error fetching ATS results: $e');
    }

    print('✅ Combined total: ${allJobs.length} saved jobs (regular + ATS)');
    return allJobs;
  }

  // 🧠 Fetch CV preview - now returns PDF preview info
  Future<String> fetchCVPreview(String filename) async {
    if (filename.isEmpty) {
      throw Exception('❌ Invalid filename provided for preview.');
    }

    // For PDF files, we can directly return that preview is available
    // since the PDF generation handles the preview internally
    if (filename.endsWith('.pdf')) {
      return 'PDF preview available';
    } else {
      throw Exception('❌ Only PDF CVs are supported for preview.');
    }
  }

  // 🧠 Delete a specific job from ATS dashboard
  Future<void> deleteJob(String? jobId) async {
    if (jobId == null || jobId.isEmpty) {
      throw Exception("❌ Invalid job ID.");
    }

    final response = await http.delete(
      Uri.parse('$baseUrl/ats-dashboard/delete/$jobId'),
      headers: {'Content-Type': 'application/json'},
    );

    if (response.statusCode != 200) {
      throw Exception('❌ Failed to delete job from ATS dashboard.');
    }
  }

  // 🧠 Delete all jobs from ATS dashboard
  Future<Map<String, dynamic>> deleteAllJobs() async {
    final response =
        await http.delete(Uri.parse('$baseUrl/ats-dashboard/clear/'));

    if (response.statusCode != 200) {
      throw Exception('❌ Failed to delete all jobs from ATS dashboard.');
    }

    // Parse the response to get cleanup information
    final data = json.decode(response.body);
    return data;
  }

  // 🧠 Clean up orphaned CV files
  Future<Map<String, dynamic>> cleanupOrphanedCVs() async {
    final response =
        await http.post(Uri.parse('$baseUrl/cleanup-orphaned-cvs/'));

    if (response.statusCode != 200) {
      throw Exception('❌ Failed to cleanup orphaned CV files.');
    }

    final data = json.decode(response.body);
    return data;
  }

  // 🧠 Toggle applied/unapplied (Note: ATS dashboard doesn't track applied status)
  Future<void> toggleApplied({required String sn}) async {
    // ATS dashboard doesn't support applied status tracking yet
    // This could be enhanced in the future if needed
    throw Exception(
        '❌ Applied status tracking not available for ATS dashboard jobs.');
  }

  // 🧠 Full Flow: Generate CV → Ask to Save → Save → Download CV
  Future<void> generateAndSaveTailoredCV({
    required BuildContext context,
    required String cvFilename,
    required String jdText,
    required String jobLink,
    required String customPrompt,
  }) async {
    try {
      showDialog(
        context: context,
        useRootNavigator: true,
        barrierDismissible: false,
        builder: (_) => const Center(child: CircularProgressIndicator()),
      );

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
      String cvDisplayName =
          await generateCVName(company, jdText, jobLink, context);

      final result = await generateTailoredCV(
        cvFilename: cvDisplayName,
        jdText: jdText,
        prompt: customPrompt,
        source: 'initial',
        jobLink: jobLink,
      );

      if (!context.mounted) return;
      Navigator.of(context).pop();

      final downloadUrl = result['downloadLink'] ?? '';
      //final previewText = result['preview'] ?? 'No preview available';

      if (downloadUrl.isEmpty) {
        throw Exception("❌ Download link missing in the response.");
      }

      final shouldSave = await showSaveJobDialog(context);
      if (shouldSave == true) {
        final tailoredFilename = result['tailored_cv_filename'];
        if (tailoredFilename == null || tailoredFilename.isEmpty) {
          throw Exception("❌ Tailored CV filename missing in the response.");
        }

        await saveJobApplication(
          jobLink: jobLink.isEmpty ? "N/A" : jobLink,
          jdText: jdText,
          tailoredCvFilename: tailoredFilename,
          applied: false,
          cvDisplayName: cvDisplayName,
        );

        if (!context.mounted) return;

        await showCustomPopup(
          context: context,
          type: PopupType.success,
          message: 'CV saved as $cvDisplayName!',
        );
      }

      final uri = Uri.tryParse(downloadUrl);
      if (uri != null && await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        if (!context.mounted) return;
        await showCustomPopup(
          context: context,
          type: PopupType.warning,
          message: 'Could not open the download link!',
        );
      }
    } catch (e) {
      if (!context.mounted) return;
      Navigator.of(context).pop();
      await showCustomPopup(
        context: context,
        type: PopupType.error,
        message: "Something went wrong: ${e.toString()}",
      );
    }
  }

  // Run ATS test for a tailored CV
  Future<Map<String, dynamic>> runATSTest({
    required String cvFilename,
    required String jdText,
    String cvType = 'tailored',
    String prompt = '',
  }) async {
    final atsService = ATSService();
    final atsResult = await atsService.testATSCompatibility(
      cvFilename: cvFilename,
      jdText: jdText,
      cvType: cvType,
    );
    // Convert ATSResult to Map<String, dynamic> for dialog use
    return {
      'keyword_match': atsResult.keywordMatch,
      'skills_match': atsResult.skillsMatch,
      'overall_score': atsResult.overallScore,
      'matched_hard_skills': atsResult.matchedHardSkills,
      'missed_hard_skills': atsResult.missedHardSkills,
      'matched_soft_skills': atsResult.matchedSoftSkills,
      'missed_soft_skills': atsResult.missedSoftSkills,
      'matched_domain_keywords': atsResult.matchedDomainKeywords,
      'missed_domain_keywords': atsResult.missedDomainKeywords,
      'tips': atsResult.tips,
    };
  }
}
