import 'package:flutter/foundation.dart';
import '../base/analysis_step_controller.dart';
import '../base/step_result.dart';
import '../base/step_config.dart';
import '../../services/keyword_cache_service.dart';
import '../../services/skill_comparison_service.dart';

/// Controller for Step 3: Skill Comparison
/// Compares CV and JD skills to identify matches and gaps
class SkillComparisonController extends AnalysisStepController {
  SkillComparisonController()
      : super(
          const StepConfig(
            stepId: 'skill_comparison',
            title: 'Skill Comparison',
            description:
                'Compare CV and JD skills to identify matches and gaps',
            order: 3,
            dependencies: ['preliminary_analysis'],
            timeout: Duration(seconds: 60),
            stopOnError: true,
          ),
        );

  @override
  Future<StepResult> execute(Map<String, dynamic> inputData) async {
    startExecution();

    try {
      final cvFilename = inputData['cv_filename'] as String;
      final jdText = inputData['jd_text'] as String;

      if (cvFilename.isEmpty || jdText.isEmpty) {
        throw ArgumentError('CV filename and JD text are required');
      }

      debugPrint('[SKILL_COMPARISON] Starting skill comparison...');
      debugPrint('   CV: $cvFilename');
      debugPrint('   JD text length: ${jdText.length} chars');

      // Get skills from preliminary analysis
      final preliminaryResults =
          inputData['preliminary_analysis'] as Map<String, dynamic>?;
      if (preliminaryResults == null) {
        throw ArgumentError('Preliminary analysis results are required');
      }

      final cvSkillsDynamic = preliminaryResults['cv_skills'];
      final jdSkillsDynamic = preliminaryResults['jd_skills'];

      debugPrint('[SKILL_COMPARISON] Raw CV skills: $cvSkillsDynamic');
      debugPrint('[SKILL_COMPARISON] Raw JD skills: $jdSkillsDynamic');

      // Convert to proper format
      final cvSkills = _convertToSkillsMap(cvSkillsDynamic);
      final jdSkills = _convertToSkillsMap(jdSkillsDynamic);

      debugPrint('[SKILL_COMPARISON] Converted CV skills: $cvSkills');
      debugPrint('[SKILL_COMPARISON] Converted JD skills: $jdSkills');

      // Check if skills are empty after conversion
      final cvHasSkills = cvSkills.values.any((skills) => skills.isNotEmpty);
      final jdHasSkills = jdSkills.values.any((skills) => skills.isNotEmpty);

      debugPrint('[SKILL_COMPARISON] Skills availability - CV: $cvHasSkills, JD: $jdHasSkills');

      // Handle empty skills gracefully
      if (!cvHasSkills && !jdHasSkills) {
        debugPrint('[SKILL_COMPARISON] Both CV and JD skills are empty - returning empty comparison');
        final emptyResult = {
          'status': 'no_skills_found',
          'message': 'No skills could be extracted from either CV or JD',
          'cv_has_skills': false,
          'jd_has_skills': false,
          'matched_skills': <String, dynamic>{},
          'missing_skills': <String, dynamic>{},
          'match_percentage': 0.0,
        };
        
        final result = StepResult.success(
          stepId: config.stepId,
          data: emptyResult,
          executionDuration: executionDuration ?? 0,
        );
        
        completeExecution(result);
        return result;
      }
      
      if (!cvHasSkills) {
        debugPrint('[SKILL_COMPARISON] CV skills are empty - creating basic comparison with JD skills only');
        final cvEmptyResult = {
          'status': 'cv_skills_empty',
          'message': 'No skills could be extracted from CV',
          'cv_has_skills': false,
          'jd_has_skills': true,
          'jd_skills': jdSkills,
          'matched_skills': <String, dynamic>{},
          'missing_skills': jdSkills, // All JD skills are missing
          'match_percentage': 0.0,
        };
        
        final result = StepResult.success(
          stepId: config.stepId,
          data: cvEmptyResult,
          executionDuration: executionDuration ?? 0,
        );
        
        completeExecution(result);
        return result;
      }

      debugPrint('[SKILL_COMPARISON] CV Skills: $cvSkills');
      debugPrint('[SKILL_COMPARISON] JD Skills: $jdSkills');

      // Perform skill comparison
      final comparisonResults = await SkillComparisonService.compareSkills(
        cvSkills: cvSkills,
        jdSkills: jdSkills,
        jdText: jdText,
      );

      debugPrint(
          '[SKILL_COMPARISON] Comparison results keys: ${comparisonResults.keys.toList()}');
      debugPrint('[SKILL_COMPARISON] Comparison results: $comparisonResults');

      // Create the result
      final result = StepResult.success(
        stepId: config.stepId,
        data: comparisonResults,
        executionDuration: executionDuration ?? 0,
      );

      completeExecution(result);

      // Cache the results
      await saveToCache(cvFilename, jdText);

      debugPrint('[SKILL_COMPARISON] Skill comparison completed successfully');
      return result;
    } catch (e) {
      final errorMessage = 'Skill comparison failed: $e';
      debugPrint('❌ [SKILL_COMPARISON] $errorMessage');

      final result = StepResult.failure(
        stepId: config.stepId,
        errorMessage: errorMessage,
        executionDuration: executionDuration ?? 0,
      );

      failExecution(errorMessage);
      return result;
    }
  }

  @override
  Future<bool> loadCachedResults(String cvFilename, String jdText) async {
    try {
      final cachedData = await KeywordCacheService.getComparisonResults(
        cvFilename: cvFilename,
        jdText: jdText,
      );

      if (cachedData != null) {
        final result = StepResult.success(
          stepId: config.stepId,
          data: cachedData,
          executionDuration: 0,
        );

        completeExecution(result);
        debugPrint('[SKILL_COMPARISON] Loaded cached results');
        return true;
      }

      return false;
    } catch (e) {
      debugPrint('[SKILL_COMPARISON] Error loading cache: $e');
      return false;
    }
  }

  @override
  Future<void> saveToCache(String cvFilename, String jdText) async {
    if (result != null) {
      try {
        await KeywordCacheService.saveComparisonResults(
          cvFilename: cvFilename,
          jdText: jdText,
          comparisonResults: result!.data,
        );
        debugPrint('[SKILL_COMPARISON] Results cached successfully');
      } catch (e) {
        debugPrint('[SKILL_COMPARISON] Error saving to cache: $e');
      }
    }
  }

  // ==================== HELPER METHODS ====================

  /// Convert dynamic skills data to proper format
  Map<String, List<String>> _convertToSkillsMap(dynamic skillsDynamic) {
    if (skillsDynamic == null) return {};

    if (skillsDynamic is Map<String, List<String>>) {
      return skillsDynamic;
    }

    if (skillsDynamic is Map<String, dynamic>) {
      final result = <String, List<String>>{};

      // Handle nested structure from preliminary analysis
      if (skillsDynamic.containsKey('soft_skills') ||
          skillsDynamic.containsKey('technical_skills') ||
          skillsDynamic.containsKey('domain_keywords')) {
        // This is the nested structure from preliminary analysis
        result['soft_skills'] =
            _extractSkillsList(skillsDynamic['soft_skills']);
        result['technical_skills'] =
            _extractSkillsList(skillsDynamic['technical_skills']);
        result['domain_keywords'] =
            _extractSkillsList(skillsDynamic['domain_keywords']);
      } else {
        // Handle flat structure
        skillsDynamic.forEach((key, value) {
          if (value is List) {
            result[key] = value.map((item) => item.toString()).toList();
          }
        });
      }
      return result;
    }

    return {};
  }

  /// Extract skills list from dynamic data
  List<String> _extractSkillsList(dynamic skillsData) {
    if (skillsData == null) return [];
    if (skillsData is List) {
      return skillsData.map((item) => item.toString()).toList();
    }
    return [];
  }

  // ==================== CONVENIENCE GETTERS ====================

  /// Get matched technical skills
  List<String>? get matchedTechnicalSkills {
    final matched = result?.getValue<Map<String, dynamic>>('matched');
    if (matched != null) {
      final technicalSkills = matched['technical_skills'] as List<dynamic>?;
      return technicalSkills
          ?.map((item) {
            if (item is Map<String, dynamic>) {
              return item['jd_skill'] ?? item['jd_requirement'] ?? '';
            }
            return item.toString();
          })
          .cast<String>()
          .toList();
    }
    return null;
  }

  /// Get matched soft skills
  List<String>? get matchedSoftSkills {
    final matched = result?.getValue<Map<String, dynamic>>('matched');
    if (matched != null) {
      final softSkills = matched['soft_skills'] as List<dynamic>?;
      return softSkills
          ?.map((item) {
            if (item is Map<String, dynamic>) {
              return item['jd_skill'] ?? item['jd_requirement'] ?? '';
            }
            return item.toString();
          })
          .cast<String>()
          .toList();
    }
    return null;
  }

  /// Get matched domain keywords
  List<String>? get matchedDomainKeywords {
    final matched = result?.getValue<Map<String, dynamic>>('matched');
    if (matched != null) {
      final domainKeywords = matched['domain_keywords'] as List<dynamic>?;
      return domainKeywords
          ?.map((item) {
            if (item is Map<String, dynamic>) {
              return item['jd_skill'] ?? item['jd_requirement'] ?? '';
            }
            return item.toString();
          })
          .cast<String>()
          .toList();
    }
    return null;
  }

  /// Get missing technical skills
  List<String>? get missingTechnicalSkills {
    final missing = result?.getValue<Map<String, dynamic>>('missing');
    if (missing != null) {
      final technicalSkills = missing['technical_skills'] as List<dynamic>?;
      return technicalSkills?.cast<String>();
    }
    return null;
  }

  /// Get missing soft skills
  List<String>? get missingSoftSkills {
    final missing = result?.getValue<Map<String, dynamic>>('missing');
    if (missing != null) {
      final softSkills = missing['soft_skills'] as List<dynamic>?;
      return softSkills?.cast<String>();
    }
    return null;
  }

  /// Get missing domain keywords
  List<String>? get missingDomainKeywords {
    final missing = result?.getValue<Map<String, dynamic>>('missing');
    if (missing != null) {
      final domainKeywords = missing['domain_keywords'] as List<dynamic>?;
      return domainKeywords?.cast<String>();
    }
    return null;
  }

  /// Get the overall match percentage
  double? get matchPercentage {
    final matchSummary =
        result?.getValue<Map<String, dynamic>>('match_summary');
    if (matchSummary != null) {
      final percentage = matchSummary['match_percentage'];
      if (percentage is double) return percentage;
      if (percentage is int) return percentage.toDouble();
      if (percentage is String) return double.tryParse(percentage);
    }
    return null;
  }

  /// Get the comparison summary
  String? get comparisonSummary {
    final matchSummary =
        result?.getValue<Map<String, dynamic>>('match_summary');
    if (matchSummary != null) {
      final totalMatched = matchSummary['total_matched'] ?? 0;
      final totalMissing = matchSummary['total_missing'] ?? 0;
      final totalRequirements = matchSummary['total_requirements'] ?? 0;
      final percentage = matchSummary['match_percentage'] ?? 0;

      return 'Matched: $totalMatched, Missing: $totalMissing, Total: $totalRequirements, Match Rate: ${percentage.toStringAsFixed(1)}%';
    }
    return null;
  }

  /// Get enhanced reasoning data for detailed analysis
  Map<String, List<Map<String, dynamic>>>? get enhancedReasoning {
    return result?.getValue<Map<String, List<Map<String, dynamic>>>>(
        'enhanced_reasoning');
  }

  /// Check if enhanced analysis is available
  bool get hasEnhancedAnalysis {
    final matchSummary =
        result?.getValue<Map<String, dynamic>>('match_summary');
    return matchSummary?['enhanced_analysis'] == true;
  }

  /// Get detailed matched skills with reasoning
  List<Map<String, dynamic>>? get detailedMatchedTechnicalSkills {
    final matched = result?.getValue<Map<String, dynamic>>('matched');
    if (matched != null) {
      final technicalSkills = matched['technical_skills'] as List<dynamic>?;
      return technicalSkills?.cast<Map<String, dynamic>>();
    }
    return null;
  }

  /// Get detailed matched soft skills with reasoning
  List<Map<String, dynamic>>? get detailedMatchedSoftSkills {
    final matched = result?.getValue<Map<String, dynamic>>('matched');
    if (matched != null) {
      final softSkills = matched['soft_skills'] as List<dynamic>?;
      return softSkills?.cast<Map<String, dynamic>>();
    }
    return null;
  }

  /// Get detailed matched domain keywords with reasoning
  List<Map<String, dynamic>>? get detailedMatchedDomainKeywords {
    final matched = result?.getValue<Map<String, dynamic>>('matched');
    if (matched != null) {
      final domainKeywords = matched['domain_keywords'] as List<dynamic>?;
      return domainKeywords?.cast<Map<String, dynamic>>();
    }
    return null;
  }

  /// Get CV technical skills count (for summary table)
  List<String>? get cvTechnicalSkills {
    // Get from preliminary analysis results
    final prelimData = _getPreliminaryAnalysisData();
    if (prelimData != null) {
      final cvSkills = prelimData['cv_skills'] as Map<String, dynamic>?;
      if (cvSkills != null) {
        final technicalSkills = cvSkills['technical_skills'] as List<dynamic>?;
        return technicalSkills?.cast<String>();
      }
    }
    return [];
  }

  /// Get CV soft skills count (for summary table)
  List<String>? get cvSoftSkills {
    // Get from preliminary analysis results
    final prelimData = _getPreliminaryAnalysisData();
    if (prelimData != null) {
      final cvSkills = prelimData['cv_skills'] as Map<String, dynamic>?;
      if (cvSkills != null) {
        final softSkills = cvSkills['soft_skills'] as List<dynamic>?;
        return softSkills?.cast<String>();
      }
    }
    return [];
  }

  /// Get CV domain keywords count (for summary table)
  List<String>? get domainKeywords {
    // Get from preliminary analysis results
    final prelimData = _getPreliminaryAnalysisData();
    if (prelimData != null) {
      final cvSkills = prelimData['cv_skills'] as Map<String, dynamic>?;
      if (cvSkills != null) {
        final domainKeywords = cvSkills['domain_keywords'] as List<dynamic>?;
        return domainKeywords?.cast<String>();
      }
    }
    return [];
  }

  /// Get JD technical skills count (for summary table)
  List<String>? get jdTechnicalSkills {
    // Get from preliminary analysis results
    final prelimData = _getPreliminaryAnalysisData();
    if (prelimData != null) {
      final jdSkills = prelimData['jd_skills'] as Map<String, dynamic>?;
      if (jdSkills != null) {
        final technicalSkills = jdSkills['technical_skills'] as List<dynamic>?;
        return technicalSkills?.cast<String>();
      }
    }
    return [];
  }

  /// Get JD soft skills count (for summary table)
  List<String>? get jdSoftSkills {
    // Get from preliminary analysis results
    final prelimData = _getPreliminaryAnalysisData();
    if (prelimData != null) {
      final jdSkills = prelimData['jd_skills'] as Map<String, dynamic>?;
      if (jdSkills != null) {
        final softSkills = jdSkills['soft_skills'] as List<dynamic>?;
        return softSkills?.cast<String>();
      }
    }
    return [];
  }

  /// Get JD domain keywords count (for summary table)
  List<String>? get jdDomainKeywords {
    // Get from preliminary analysis results
    final prelimData = _getPreliminaryAnalysisData();
    if (prelimData != null) {
      final jdSkills = prelimData['jd_skills'] as Map<String, dynamic>?;
      if (jdSkills != null) {
        final domainKeywords = jdSkills['domain_keywords'] as List<dynamic>?;
        return domainKeywords?.cast<String>();
      }
    }
    return [];
  }

  /// Helper method to get preliminary analysis data
  Map<String, dynamic>? _getPreliminaryAnalysisData() {
    // Try to get from orchestrator if available
    if (orchestrator != null) {
      final prelimResult = orchestrator!.stepResults['preliminary_analysis'];
      if (prelimResult != null) {
        return prelimResult.data;
      }
    }
    return null;
  }
}
