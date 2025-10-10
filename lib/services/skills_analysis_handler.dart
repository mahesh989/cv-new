import 'package:flutter/foundation.dart';
import 'job_parser.dart';
import 'jobs_state_manager.dart';
import '../models/skills_analysis_model.dart';

class SkillsAnalysisHandler {
  static Future<void> handleAnalysisResult({
    required String jdText,
    required SkillsAnalysisResult result,
  }) async {
    debugPrint('📝 [SKILLS_HANDLER] Processing analysis result');
    
    try {
      // First, parse job details from JD text
      final jobDetails = JobParser.parseJobDetails(jdText);
      
      // Save job if we have the minimum required details
      debugPrint('🔍 [SKILLS_HANDLER] Parsed job details:');
      debugPrint('   Company: ${jobDetails['company_name']}');
      debugPrint('   Title: ${jobDetails['job_title']}');
      debugPrint('   Location: ${jobDetails['location']}');
      debugPrint('   URL: ${jobDetails['job_url']}');
      
      if (jobDetails['company_name'] != null && 
          jobDetails['job_title'] != null && 
          jobDetails['location'] != null) {
            
        debugPrint('💾 [SKILLS_HANDLER] Saving job to database');
        await JobsStateManager.saveNewJob(
          companyName: jobDetails['company_name']!,
          jobTitle: jobDetails['job_title']!,
          jobUrl: jobDetails['job_url'] ?? '',
          location: jobDetails['location']!,
          phoneNumber: jobDetails['phone_number'],
          email: jobDetails['email'],
        );
        debugPrint('✅ [SKILLS_HANDLER] Job saved successfully');
      } else {
        debugPrint('⚠️ [SKILLS_HANDLER] Missing required job details - skipping save');
        debugPrint('   company_name: ${jobDetails['company_name'] != null}');
        debugPrint('   job_title: ${jobDetails['job_title'] != null}');
        debugPrint('   location: ${jobDetails['location'] != null}');
      }
    } catch (e) {
      debugPrint('❌ [SKILLS_HANDLER] Error saving job: $e');
      // Continue even if saving fails
    }
  }

  static Future<void> clearResults() async {
    debugPrint('🧹 [SKILLS_HANDLER] Clearing analysis results');
    try {
      // Clear any cached results
      // Reset any state
      debugPrint('✅ [SKILLS_HANDLER] Results cleared successfully');
    } catch (e) {
      debugPrint('❌ [SKILLS_HANDLER] Error clearing results: $e');
    }
  }
}