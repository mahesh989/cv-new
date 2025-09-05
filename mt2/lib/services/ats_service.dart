import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ATSService {
  // Use localhost for development, change to production URL when deploying
  static const String _baseUrl = 'http://localhost:8000';
  final String baseUrl = _baseUrl;
  static final Map<String, ATSResult> atsResultCache = {};

  Future<ATSResult> testATSCompatibility({
    required String cvFilename,
    required String jdText,
    required String cvType,
    String prompt =
        "Analyze the CV compatibility with the job description and provide detailed feedback.",
  }) async {
    try {
      debugPrint("\n🔍 [ATS] Starting ATS Test...");
      debugPrint("📄 CV Filename: $cvFilename");
      debugPrint("📄 CV Type: $cvType");
      debugPrint("📄 JD Length: ${jdText.length} characters");

      final response = await http
          .post(
            Uri.parse('$baseUrl/ats-test/'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'cv_filename': cvFilename,
              'jd_text': jdText,
              'cv_type': cvType,
              'prompt': prompt,
            }),
          )
          .timeout(const Duration(seconds: 120));

      if (response.statusCode != 200) {
        final errorBody = json.decode(response.body);
        if (errorBody['detail']?.toString().contains('insufficient_quota') ==
            true) {
          throw Exception(
              'OpenAI API quota exceeded. Please try again later or contact support.');
        } else if (response.statusCode == 429) {
          throw Exception(
              'Rate limit exceeded. Please try again in a few minutes.');
        }
        throw Exception(
            'ATS test failed: ${errorBody['detail'] ?? 'Unknown error'}');
      }

      final result = ATSResult.fromJson(json.decode(response.body));

      // Print comprehensive ATS results
      debugPrint("\n📊 [ATS] Test Results Summary:");
      debugPrint("----------------------------------------");
      debugPrint("🎯 Overall Scores:");
      debugPrint("• Keyword Match: ${result.keywordMatch}%");
      debugPrint("• Skills Match: ${result.skillsMatch}%");
      debugPrint("• Overall Score: ${result.overallScore}%");

      debugPrint("\n📋 Job Description Analysis:");
      debugPrint("• Technical Skills: ${result.jdTechnicalSkills.join(", ")}");
      debugPrint("• Soft Skills: ${result.jdSoftSkills.join(", ")}");
      debugPrint("• Domain Keywords: ${result.jdDomainKeywords.join(", ")}");

      debugPrint("\n🎯 Matching Results:");
      debugPrint(
          "• Matched Technical Skills: ${result.matchedHardSkills.join(", ")}");
      debugPrint(
          "• Matched Soft Skills: ${result.matchedSoftSkills.join(", ")}");
      debugPrint(
          "• Matched Extra Keywords: ${result.matchedDomainKeywords.join(", ")}");
      debugPrint(
          "• Missed Technical Skills: ${result.missedHardSkills.join(", ")}");
      debugPrint("• Missed Soft Skills: ${result.missedSoftSkills.join(", ")}");
      debugPrint(
          "• Missed Other Keywords: ${result.missedDomainKeywords.join(", ")}");

      debugPrint("\n📈 Detailed Scores:");
      debugPrint("Skills Summary:");
      debugPrint(
          "• Technical Skills: ${result.matchedHardSkills.length} matched, ${result.missedHardSkills.length} missed");
      debugPrint(
          "• Soft Skills: ${result.matchedSoftSkills.length} matched, ${result.missedSoftSkills.length} missed");
      debugPrint(
          "• Domain Keywords: ${result.matchedDomainKeywords.length} matched, ${result.missedDomainKeywords.length} missed");

      debugPrint("\n⚠️ Identified Gaps:");
      for (var gap in result.gaps) {
        debugPrint("• $gap");
      }

      debugPrint("\n💡 Improvement Tips:");
      for (var tip in result.tips) {
        debugPrint("• $tip");
      }

      debugPrint("\n----------------------------------------");
      debugPrint("✅ [ATS] Test completed successfully\n");

      return result;
    } catch (e) {
      debugPrint("\n❌ [ATS] Test failed with error: $e");
      if (e.toString().contains('insufficient_quota') ||
          e.toString().contains('429')) {
        rethrow;
      }
      throw Exception('Failed to run ATS test: $e');
    }
  }
}

class ATSResult {
  final int keywordMatch;
  final int skillsMatch;
  final int overallScore;
  final List<String> jdTechnicalSkills;
  final List<String> jdSoftSkills;
  final List<String> jdDomainKeywords;
  final List<String> matchedSkills;
  final List<String> matchedHardSkills;
  final List<String> matchedSoftSkills;
  final List<String> matchedDomainKeywords;
  final List<String> missedHardSkills;
  final List<String> missedSoftSkills;
  final List<String> missedDomainKeywords;
  final List<String> gaps;
  final List<String> tips;

  ATSResult({
    required this.keywordMatch,
    required this.skillsMatch,
    required this.overallScore,
    required this.jdTechnicalSkills,
    required this.jdSoftSkills,
    required this.jdDomainKeywords,
    required this.matchedSkills,
    required this.matchedHardSkills,
    required this.matchedSoftSkills,
    required this.matchedDomainKeywords,
    required this.missedHardSkills,
    required this.missedSoftSkills,
    required this.missedDomainKeywords,
    required this.gaps,
    required this.tips,
  });

  factory ATSResult.fromJson(Map<String, dynamic> json) {
    return ATSResult(
      keywordMatch: json['keyword_match'] ?? 0,
      skillsMatch: json['skills_match'] ?? 0,
      overallScore: json['overall_score'] ?? 0,
      jdTechnicalSkills: List<String>.from(json['jd_technical_skills'] ?? []),
      jdSoftSkills: List<String>.from(json['jd_soft_skills'] ?? []),
      jdDomainKeywords: List<String>.from(json['jd_domain_keywords'] ?? []),
      matchedSkills: List<String>.from(json['matched_skills'] ?? []),
      matchedHardSkills: List<String>.from(json['matched_hard_skills'] ?? []),
      matchedSoftSkills: List<String>.from(json['matched_soft_skills'] ?? []),
      matchedDomainKeywords:
          List<String>.from(json['matched_domain_keywords'] ?? []),
      missedHardSkills: List<String>.from(json['missed_hard_skills'] ?? []),
      missedSoftSkills: List<String>.from(json['missed_soft_skills'] ?? []),
      missedDomainKeywords:
          List<String>.from(json['missed_domain_keywords'] ?? []),
      gaps: List<String>.from(json['gaps'] ?? []),
      tips: List<String>.from(json['tips'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'keyword_match': keywordMatch,
      'skills_match': skillsMatch,
      'overall_score': overallScore,
      'jd_technical_skills': jdTechnicalSkills,
      'jd_soft_skills': jdSoftSkills,
      'jd_domain_keywords': jdDomainKeywords,
      'matched_skills': matchedSkills,
      'matched_hard_skills': matchedHardSkills,
      'matched_soft_skills': matchedSoftSkills,
      'matched_domain_keywords': matchedDomainKeywords,
      'missed_hard_skills': missedHardSkills,
      'missed_soft_skills': missedSoftSkills,
      'missed_domain_keywords': missedDomainKeywords,
      'gaps': gaps,
      'tips': tips,
    };
  }
}
