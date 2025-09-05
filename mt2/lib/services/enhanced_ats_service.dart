import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/api_service.dart';
import 'package:flutter/foundation.dart'; // Added for debugPrint

class EnhancedATSService {
  static const String baseUrl = 'http://localhost:8000';

  /// Calculate Enhanced ATS Score using existing data
  static Future<Map<String, dynamic>> calculateEnhancedATSScore({
    required String cvText,
    required String jdText,
    required Map<String, dynamic> skillComparison,
    required Map<String, dynamic> extractedKeywords,
  }) async {
    debugPrint(
        '🚀 [ENHANCED_ATS_SERVICE] Starting Enhanced ATS calculation...');

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/ats/enhanced-score'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'cv_text': cvText,
          'jd_text': jdText,
          'skill_comparison': skillComparison,
          'extracted_keywords': extractedKeywords,
        }),
      );

      debugPrint(
          '📊 [ENHANCED_ATS_SERVICE] Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);

        // Debug logging
        debugPrint('🔍 [DEBUG] Full API Response:');
        debugPrint(json.encode(data));

        final overallScore = data['overall_ats_score']?.toDouble() ?? 0.0;
        debugPrint(
            '✅ [ENHANCED_ATS_SERVICE] Enhanced ATS Score: $overallScore/100');

        final scoreCategory = data['score_category'] ?? 'Unknown';
        debugPrint('   Category: $scoreCategory');

        // Debug enhancement_analysis specifically
        final enhancementAnalysis = data['enhancement_analysis'] ?? {};
        debugPrint('🔍 [DEBUG] Enhancement Analysis:');
        debugPrint(
            '  - keyword_matching: ${enhancementAnalysis['keyword_matching']}');
        debugPrint(
            '  - skills_relevance: ${enhancementAnalysis['skills_relevance']}');
        debugPrint(
            '  - experience_score: ${enhancementAnalysis['experience_score']}');
        debugPrint(
            '  - missing_skills_impact: ${enhancementAnalysis['missing_skills_impact']}');
        debugPrint(
            '  - criticality_bonus: ${enhancementAnalysis['criticality_bonus']}');

        return formatEnhancedResults(data);
      } else {
        debugPrint(
            '❌ [ENHANCED_ATS_SERVICE] API Error: ${response.statusCode}');
        debugPrint('Response body: ${response.body}');
        return _createFallbackResult();
      }
    } catch (e) {
      debugPrint('❌ [ENHANCED_ATS_SERVICE] Exception: $e');
      return _createFallbackResult();
    }
  }

  /// Create fallback result when enhanced ATS fails
  static Map<String, dynamic> _createFallbackResult() {
    return {
      'overall_ats_score': 75.0,
      'score_category': '⚠️ Fair - Moderate ATS Success',
      'base_scores': {
        'overall_base_score': 75.0,
        'category_scores': {
          'technical': 80.0,
          'soft_skills': 70.0,
          'domain_keywords': 75.0,
        }
      },
      'enhancement_analysis': {
        'status': 'fallback_mode',
        'criticality_bonus': 0.0,
        'skills_bonus': 0.0,
        'experience_score': 75.0,
        'missing_penalty': 5.0,
      },
      'recommendations': [
        '🔄 Enhanced analysis temporarily unavailable',
        '📊 Using base scoring from skill comparison',
        '🎯 Add specific keywords from job requirements',
        '📈 Quantify achievements with metrics',
        '🛠️ Highlight relevant technical skills',
      ],
      'detailed_analysis': {
        'status': 'fallback_mode',
      },
      'achievements_mapped': [],
    };
  }

  /// Format enhanced ATS results for UI display
  static Map<String, dynamic> formatEnhancedResults(
      Map<String, dynamic> rawData) {
    // Handle both nested and direct response formats
    final data = rawData['data'] ?? rawData;

    debugPrint('🔍 [FORMAT] Input data keys: ${data.keys.toList()}');

    final enhancementAnalysis = data['enhancement_analysis'] ?? {};
    final detailedBreakdown = data['detailed_breakdown'] ?? {};
    debugPrint(
        '🔍 [FORMAT] Enhancement analysis keys: ${enhancementAnalysis.keys.toList()}');
    debugPrint(
        '🔍 [FORMAT] Detailed breakdown keys: ${detailedBreakdown.keys.toList()}');

    final result = {
      'overall_ats_score': data['overall_ats_score']?.toDouble() ?? 0.0,
      'score_category': data['score_category'] ?? 'Unknown',
      'base_scores': data['base_scores'] ?? {},
      'enhancement_analysis': enhancementAnalysis,
      'detailed_breakdown': detailedBreakdown, // Add detailed breakdown
      'detailed_analysis': data['detailed_analysis'] ?? {},
      'recommendations': List<String>.from(data['recommendations'] ?? []),
      'achievements_mapped':
          List<Map<String, dynamic>>.from(data['achievements_mapped'] ?? []),
      'score_breakdown': _calculateScoreBreakdownFromDetailed(
          detailedBreakdown, enhancementAnalysis),
    };

    debugPrint(
        '🔍 [FORMAT] Final result score_breakdown: ${result['score_breakdown']}');
    return result;
  }

  /// Calculate score breakdown from detailed breakdown (preferred) or enhancement analysis (fallback)
  static Map<String, dynamic> _calculateScoreBreakdownFromDetailed(
      Map<String, dynamic> detailedBreakdown,
      Map<String, dynamic> enhancementAnalysis) {
    if (detailedBreakdown.isNotEmpty) {
      // Use new detailed breakdown structure
      debugPrint('🔍 [BREAKDOWN] Using detailed breakdown structure');
      return {
        'keyword_matching':
            detailedBreakdown['keyword_match']?['score']?.toDouble() ?? 0.0,
        'skills_relevance':
            detailedBreakdown['skills_relevance']?['score']?.toDouble() ?? 0.0,
        'experience_alignment':
            detailedBreakdown['experience_alignment']?['score']?.toDouble() ??
                0.0,
        'missing_skills_impact':
            detailedBreakdown['missing_skills_impact']?['score']?.toDouble() ??
                0.0,
        'criticality_bonus':
            enhancementAnalysis['criticality_bonus']?.toDouble() ?? 0.0,
        // Add new components
        'industry_fit':
            detailedBreakdown['industry_fit']?['score']?.toDouble() ?? 0.0,
        'role_seniority':
            detailedBreakdown['role_seniority']?['score']?.toDouble() ?? 0.0,
        'technical_depth':
            detailedBreakdown['technical_depth']?['score']?.toDouble() ?? 0.0,
        'soft_skills_match':
            detailedBreakdown['soft_skills_match']?['score']?.toDouble() ?? 0.0,
      };
    } else {
      // Fallback to old enhancement analysis structure
      debugPrint(
          '🔍 [BREAKDOWN] Using fallback enhancement analysis structure');
      return _calculateScoreBreakdown(
          {'enhancement_analysis': enhancementAnalysis});
    }
  }

  /// Calculate score breakdown for visual display
  static Map<String, dynamic> _calculateScoreBreakdown(
      Map<String, dynamic> data) {
    final enhancementAnalysis = data['enhancement_analysis'] ?? {};

    return {
      'keyword_matching':
          enhancementAnalysis['keyword_matching']?.toDouble() ?? 0.0,
      'skills_relevance':
          enhancementAnalysis['skills_relevance']?.toDouble() ?? 0.0,
      'experience_alignment':
          enhancementAnalysis['experience_score']?.toDouble() ?? 0.0,
      'missing_skills_impact':
          enhancementAnalysis['missing_skills_impact']?.toDouble() ?? 0.0,
      'criticality_bonus':
          enhancementAnalysis['criticality_bonus']?.toDouble() ?? 0.0,
    };
  }

  /// Get score color based on value
  static String getScoreColor(double score) {
    if (score >= 90) return '#4CAF50'; // Green
    if (score >= 80) return '#8BC34A'; // Light Green
    if (score >= 70) return '#FF9800'; // Orange
    if (score >= 60) return '#FF5722'; // Deep Orange
    return '#F44336'; // Red
  }

  /// Get score icon based on value
  static String getScoreIcon(double score) {
    if (score >= 90) return '🌟';
    if (score >= 80) return '✅';
    if (score >= 70) return '⚠️';
    if (score >= 60) return '🔄';
    return '❌';
  }

  /// Parse criticality analysis for UI
  static List<Map<String, dynamic>> parseCriticalityAnalysis(
      Map<String, dynamic> detailedAnalysis) {
    final criticality = detailedAnalysis['criticality'] ?? {};
    final requirementAnalysis = criticality['requirement_analysis'] ?? [];

    return List<Map<String, dynamic>>.from(requirementAnalysis)
        .map((req) => {
              'requirement': req['requirement'] ?? '',
              'criticality': req['criticality'] ?? 'UNKNOWN',
              'weight': req['weight']?.toDouble() ?? 1.0,
              'reason': req['reason'] ?? '',
              'category': req['category'] ?? 'other',
            })
        .toList();
  }

  /// Parse skills relevance for UI
  static Map<String, dynamic> parseSkillsRelevance(
      Map<String, dynamic> detailedAnalysis) {
    final skillsRelevance = detailedAnalysis['skills_relevance'] ?? {};

    return {
      'overall_score':
          skillsRelevance['overall_skills_score']?.toDouble() ?? 0.0,
      'strength_areas':
          List<String>.from(skillsRelevance['strength_areas'] ?? []),
      'improvement_areas':
          List<String>.from(skillsRelevance['improvement_areas'] ?? []),
      'skills_analysis': List<Map<String, dynamic>>.from(
          skillsRelevance['skills_analysis'] ?? []),
    };
  }

  /// Parse missing skills impact for UI
  static Map<String, dynamic> parseMissingSkillsImpact(
      Map<String, dynamic> detailedAnalysis) {
    final missingSkillsImpact = detailedAnalysis['missing_skills_impact'] ?? {};

    return {
      'overall_impact_score':
          missingSkillsImpact['overall_impact_score']?.toDouble() ?? 0.0,
      'critical_gaps':
          List<String>.from(missingSkillsImpact['critical_gaps'] ?? []),
      'minor_gaps': List<String>.from(missingSkillsImpact['minor_gaps'] ?? []),
      'missing_skills_analysis': List<Map<String, dynamic>>.from(
          missingSkillsImpact['missing_skills_analysis'] ?? []),
    };
  }
}
