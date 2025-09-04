import 'package:http/http.dart' as http;
import 'dart:convert';

class SkillComparisonService {
  static const String baseUrl = 'http://localhost:8000';

  /// Compares CV and JD skills using LLM and categorizes them into 6 categories:
  /// - Matched Technical Skills
  /// - Matched Soft Skills
  /// - Matched Domain Keywords
  /// - Missing Technical Skills (from JD not in CV)
  /// - Missing Soft Skills (from JD not in CV)
  /// - Missing Domain Keywords (from JD not in CV)
  static Future<Map<String, dynamic>> compareSkills({
    required Map<String, List<String>> cvSkills,
    required Map<String, List<String>> jdSkills,
    String? jdText,
  }) async {
    try {
      print('🚀 [SkillComparison] Starting skill comparison...');
      print('📋 [SkillComparison] CV Skills: $cvSkills');
      print('📋 [SkillComparison] JD Skills: $jdSkills');

      final requestBody = {
        'cv_skills': cvSkills,
        'jd_skills': jdSkills,
        'prompt': _generateComparisonPrompt(cvSkills, jdSkills),
        if (jdText != null) 'jd_text': jdText,
      };

      print(
          '📤 [SkillComparison] Sending request to: $baseUrl/api/llm/compare-skills');
      print(
          '📤 [SkillComparison] Request body keys: ${requestBody.keys.toList()}');

      final response = await http.post(
        Uri.parse('$baseUrl/api/llm/compare-skills'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(requestBody),
      );

      print('📥 [SkillComparison] Response status: ${response.statusCode}');
      print(
          '📥 [SkillComparison] Response body length: ${response.body.length}');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('✅ [SkillComparison] Successfully decoded response JSON');

        // Check if we got enhanced reasoning from new implementation
        if (data['enhanced_reasoning'] == true) {
          print('🧠 [SkillComparison] Enhanced AI reasoning detected');
          return _parseEnhancedComparisonResult(data);
        } else {
          print('🔄 [SkillComparison] Using standard parsing');
          return _parseComparisonResult(data);
        }
      } else {
        print('❌ [SkillComparison] API error: ${response.statusCode}');
        print('❌ [SkillComparison] Response body: ${response.body}');
        throw Exception('Failed to compare skills: ${response.statusCode}');
      }
    } catch (e) {
      // Fallback to local comparison if API fails
      print('🔄 [SkillComparison] API failed, using fallback: $e');
      print('🔄 [SkillComparison] Error type: ${e.runtimeType}');
      return _fallbackComparison(cvSkills, jdSkills);
    }
  }

  /// Generates the LLM prompt for intelligent skill comparison
  /// Focuses on JD → CV matching (what JD needs vs what CV has)
  static String _generateComparisonPrompt(
    Map<String, List<String>> cvSkills,
    Map<String, List<String>> jdSkills,
  ) {
    return '''
You are an expert ATS skill matcher analyzing CACHED keywords from CV and JD extractions.

**OBJECTIVE**: Determine which JD requirements are satisfied by CV skills, and which are missing.

**CRITICAL RULES**:
- Direction: JD → CV (match JD requirements against CV skills)
- MATCHED: JD requirement has a corresponding CV skill 
- MISSING: JD requirement has NO corresponding CV skill
- Use intelligent semantic matching (not just exact text)
- Each JD requirement appears only once (no duplicates)
- Focus on helping candidate identify CV gaps

**CACHED CV SKILLS** (What candidate has):
Technical: ${cvSkills['technical_skills']?.join(', ') ?? 'None'}
Soft: ${cvSkills['soft_skills']?.join(', ') ?? 'None'}  
Domain: ${cvSkills['domain_keywords']?.join(', ') ?? 'None'}

**CACHED JD REQUIREMENTS** (What job needs):
Technical: ${jdSkills['technical_skills']?.join(', ') ?? 'None'}
Soft: ${jdSkills['soft_skills']?.join(', ') ?? 'None'}
Domain: ${jdSkills['domain_keywords']?.join(', ') ?? 'None'}

**MATCHING EXAMPLES**:
- "Python programming" (CV) satisfies "Python" (JD) → MATCHED
- "Communication skills" (CV) satisfies "Communication" (JD) → MATCHED  
- "AWS" (JD) with no cloud skills in CV → MISSING
- "Leadership" (CV) satisfies "Management skills" (JD) → MATCHED (semantic)

**OUTPUT** (JSON only):
{
  "matched": {
    "technical_skills": [
      {"cv_skill": "Python programming", "jd_requirement": "Python", "match_reason": "Exact match"}
    ],
    "soft_skills": [
      {"cv_skill": "Communication skills", "jd_requirement": "Communication", "match_reason": "Exact match"}
    ],
    "domain_keywords": [
      {"cv_skill": "Data analysis", "jd_requirement": "Statistical analysis", "match_reason": "Semantic match"}
    ]
  },
  "missing": {
    "technical_skills": ["AWS", "Docker"],
    "soft_skills": ["Project management"],
    "domain_keywords": ["Cloud computing"]
  },
  "match_summary": {
    "total_jd_requirements": ${(jdSkills['technical_skills']?.length ?? 0) + (jdSkills['soft_skills']?.length ?? 0) + (jdSkills['domain_keywords']?.length ?? 0)},
    "total_matches": 0,
    "match_percentage": 0,
    "critical_gaps": []
  }
}

Return ONLY the JSON object.
''';
  }

  /// Parses the LLM response into a structured format
  static Map<String, dynamic> _parseComparisonResult(
      Map<String, dynamic> data) {
    try {
      print(
          '🔍 [SkillComparison] Raw API response keys: ${data.keys.toList()}');
      print('🔍 [SkillComparison] Full API response: $data');

      // If the response has the expected structure, return it
      if (data.containsKey('matched') && data.containsKey('missing')) {
        print('✅ [SkillComparison] Found direct matched/missing structure');
        return data;
      }

      // Try to parse from 'comparison_result' field
      if (data.containsKey('comparison_result')) {
        print('🔍 [SkillComparison] Found comparison_result field');
        final comparisonData = data['comparison_result'];
        final validationData = data['validation'];

        // Log validation results
        if (validationData != null) {
          final isValid = validationData['valid'] ?? false;
          final processedCount = validationData['processed_count'] ?? 0;
          print(
              '📊 [VALIDATION] Comparison validation: ${isValid ? "PASSED" : "FAILED"}');
          print('📊 [VALIDATION] Processed requirements: $processedCount');
          if (!isValid) {
            final message =
                validationData['message'] ?? 'Unknown validation error';
            print('⚠️ [VALIDATION] Issue: $message');
          }
        }

        // Consolidate matched skills and return the full comparison data
        if (comparisonData is Map<String, dynamic> &&
            comparisonData.containsKey('matched')) {
          final matchedSkills = comparisonData['matched'];
          if (matchedSkills is Map<String, dynamic>) {
            // Convert matched skills to the expected format for consolidation
            final matchedForConsolidation =
                <String, List<Map<String, String>>>{};
            for (final category in [
              'technical_skills',
              'soft_skills',
              'domain_keywords'
            ]) {
              if (matchedSkills[category] is List) {
                matchedForConsolidation[category] =
                    List<Map<String, String>>.from((matchedSkills[category]
                            as List)
                        .map((item) => Map<String, String>.from(item as Map)));
              } else {
                matchedForConsolidation[category] = <Map<String, String>>[];
              }
            }

            // Consolidate matched skills
            final consolidatedMatched =
                _consolidateMatchedSkills(matchedForConsolidation);

            // Update the comparison data with consolidated results
            final result = Map<String, dynamic>.from(comparisonData);
            result['matched'] = consolidatedMatched;

            print('✅ [SkillComparison] Successfully compared skills');
            return result;
          }
        }

        print(
            '✅ [SkillComparison] Successfully compared skills (no consolidation needed)');
        return comparisonData;
      }

      // Try to parse from 'raw_response' field
      if (data.containsKey('raw_response')) {
        print('🔍 [SkillComparison] Trying to parse from raw_response');
        final rawResponse = data['raw_response'];
        print(
            '🔍 [SkillComparison] raw_response type: ${rawResponse.runtimeType}');

        if (rawResponse is String) {
          print(
              '🔍 [SkillComparison] raw_response first 200 chars: ${rawResponse.substring(0, rawResponse.length > 200 ? 200 : rawResponse.length)}');
          // Try to extract JSON from the response
          final jsonMatch =
              RegExp(r'\{.*\}', dotAll: true).firstMatch(rawResponse);
          if (jsonMatch != null) {
            print('✅ [SkillComparison] Found JSON in raw_response');
            final parsed = json.decode(jsonMatch.group(0)!);
            print(
                '✅ [SkillComparison] Successfully parsed JSON from raw_response');
            return parsed;
          } else {
            print('❌ [SkillComparison] No JSON found in raw_response');
          }
        } else {
          print(
              '❌ [SkillComparison] raw_response is not a String: ${rawResponse.runtimeType}');
        }
      }

      print('❌ [SkillComparison] No valid data structure found');
      throw Exception('Unable to parse comparison result');
    } catch (e) {
      print('🔄 [SkillComparison] Parse error: $e');
      print('🔄 [SkillComparison] Error type: ${e.runtimeType}');
      print('🔄 [SkillComparison] Stack trace: ${StackTrace.current}');
      return _createEmptyResult();
    }
  }

  /// Parses enhanced comparison result with detailed AI reasoning
  /// Handles the Python-inspired backend response with semantic matching
  static Map<String, dynamic> _parseEnhancedComparisonResult(
      Map<String, dynamic> data) {
    try {
      print('🧠 [Enhanced] Parsing enhanced AI comparison result');

      final comparisonResult = data['comparison_result'] ?? {};
      final matched = comparisonResult['matched'] ?? {};
      final missing = comparisonResult['missing'] ?? {};
      final matchSummary = comparisonResult['match_summary'] ?? {};

      print('🧠 [Enhanced] Raw matched data: $matched');
      print('🧠 [Enhanced] Raw missing data: $missing');
      print('🧠 [Enhanced] Match summary: $matchSummary');

      // Enhanced result structure with detailed reasoning
      final result = <String, dynamic>{
        'matched': <String, List<Map<String, String>>>{},
        'missing': <String, List<String>>{},
        'enhanced_reasoning':
            <String, List<Map<String, String>>>{}, // New field for reasoning
      };

      // Process each category with enhanced reasoning
      for (final category in [
        'technical_skills',
        'soft_skills',
        'domain_keywords'
      ]) {
        print('🔍 [Enhanced] Processing $category');

        // Process matched skills with reasoning
        final categoryMatched = <Map<String, String>>[];
        final categoryReasoning = <Map<String, String>>[];

        if (matched[category] != null) {
          for (final match in matched[category]) {
            final matchData = <String, String>{
              'jd_skill': (match['jd_requirement'] ?? match['jd_skill'] ?? '')
                  .toString(),
              'cv_skill': (match['cv_skill'] ?? match['cv_equivalent'] ?? '')
                  .toString(),
              'match_reason': (match['match_reason'] ??
                      match['reasoning'] ??
                      'AI semantic match')
                  .toString(),
              'reasoning': (match['reasoning'] ??
                      match['match_reason'] ??
                      'Intelligent AI matching')
                  .toString(),
            };

            categoryMatched.add(matchData);

            // Add to reasoning collection for display
            categoryReasoning.add(<String, String>{
              'skill': matchData['jd_skill']!,
              'reasoning': matchData['reasoning']!,
              'type': 'matched',
              'cv_equivalent': matchData['cv_skill']!,
            });
          }
        }

        result['matched'][category] = categoryMatched;

        // Process missing skills with reasoning
        final categoryMissing = <String>[];

        if (missing[category] != null) {
          for (final missingItem in missing[category]) {
            String missingSkill;
            String reasoning;

            if (missingItem is String) {
              missingSkill = missingItem;
              reasoning = 'Not found in CV';
            } else if (missingItem is Map) {
              missingSkill = missingItem['jd_skill'] ?? missingItem.toString();
              reasoning = missingItem['reasoning'] ?? 'Not found in CV';
            } else {
              missingSkill = missingItem.toString();
              reasoning = 'Not found in CV';
            }

            categoryMissing.add(missingSkill);

            // Add to reasoning collection
            categoryReasoning.add(<String, String>{
              'skill': missingSkill,
              'reasoning': reasoning,
              'type': 'missing',
              'cv_equivalent': 'N/A',
            });
          }
        }

        result['missing'][category] = categoryMissing;
        result['enhanced_reasoning'][category] = categoryReasoning;

        print(
            '✅ [Enhanced] $category: ${categoryMatched.length} matched, ${categoryMissing.length} missing');
      }

      // Enhanced match summary with Python-style analytics
      final enhancedSummary = {
        'total_matched': matchSummary['total_matched'] ?? 0,
        'total_missing': matchSummary['total_missing'] ?? 0,
        'total_requirements': matchSummary['total_requirements'] ?? 0,
        'match_percentage': matchSummary['match_percentage'] ?? 0,
        'enhanced_analysis': true,
        'ai_powered': true,
      };

      // Add category-wise breakdown if available
      if (matchSummary['categories'] != null) {
        enhancedSummary['categories'] = matchSummary['categories'];
      }

      result['match_summary'] = enhancedSummary;

      print('✅ [Enhanced] Enhanced parsing completed');
      print(
          '📊 [Enhanced] Match rate: ${enhancedSummary['match_percentage']}%');

      return result;
    } catch (e, stackTrace) {
      print('❌ [Enhanced] Error parsing enhanced result: $e');
      print('❌ [Enhanced] Stack trace: $stackTrace');

      // Fallback to standard parsing if enhanced fails
      return _parseComparisonResult(data);
    }
  }

  /// Fallback comparison when LLM API is not available
  /// Follows the same JD → CV matching logic as the LLM version
  static Map<String, dynamic> _fallbackComparison(
    Map<String, List<String>> cvSkills,
    Map<String, List<String>> jdSkills,
  ) {
    print('🔄 [SkillComparison] Using fallback comparison logic');
    print('📋 [Fallback] CV Skills: $cvSkills');
    print('📋 [Fallback] JD Skills: $jdSkills');

    final matched = <String, List<Map<String, String>>>{};
    final missing = <String, List<String>>{};

    for (final category in [
      'technical_skills',
      'soft_skills',
      'domain_keywords'
    ]) {
      final cvList = cvSkills[category] ?? [];
      final jdList = jdSkills[category] ?? [];

      print(
          '🔍 [Fallback] Comparing $category: ${jdList.length} JD requirements vs ${cvList.length} CV skills');

      final categoryMatched = <Map<String, String>>[];
      final categoryMissing = <String>[];

      // For each JD requirement, check if it's satisfied by any CV skill
      for (final jdRequirement in jdList) {
        bool found = false;
        String? matchedCVSkill;
        String matchReason = 'Basic text match';

        // Try to find a matching CV skill
        for (final cvSkill in cvList) {
          if (_isBasicMatch(cvSkill, jdRequirement)) {
            found = true;
            matchedCVSkill = cvSkill;

            // Determine match type
            if (cvSkill.toLowerCase().trim() ==
                jdRequirement.toLowerCase().trim()) {
              matchReason = 'Exact match';
            } else if (cvSkill
                    .toLowerCase()
                    .contains(jdRequirement.toLowerCase()) ||
                jdRequirement.toLowerCase().contains(cvSkill.toLowerCase())) {
              matchReason = 'Partial match';
            } else {
              matchReason = 'Semantic match';
            }
            break;
          }
        }

        if (found && matchedCVSkill != null) {
          categoryMatched.add({
            'cv_skill': matchedCVSkill,
            'jd_requirement': jdRequirement,
            'match_reason': matchReason
          });
          print(
              '✅ [Fallback] Matched: "$jdRequirement" → "$matchedCVSkill" ($matchReason)');
        } else {
          categoryMissing.add(jdRequirement);
          print('❌ [Fallback] Missing: "$jdRequirement" (not found in CV)');
        }
      }

      matched[category] = categoryMatched;
      missing[category] = categoryMissing;
    }

    final totalRequirements = jdSkills.values.expand((list) => list).length;
    final totalMatches = matched.values.expand((list) => list).length;
    final matchPercentage = totalRequirements > 0
        ? (totalMatches / totalRequirements * 100).round()
        : 0;

    final criticalGaps = <String>[];
    missing.values.forEach((list) => criticalGaps.addAll(list));

    // Remove duplicates from matched results
    final consolidatedMatched = _consolidateMatchedSkills(matched);
    final consolidatedTotalMatches =
        consolidatedMatched.values.expand((list) => list).length;
    final consolidatedMatchPercentage = totalRequirements > 0
        ? (consolidatedTotalMatches / totalRequirements * 100).round()
        : 0;

    print('📊 [Fallback] Final Results:');
    print('📊 [Fallback] Total JD Requirements: $totalRequirements');
    print('📊 [Fallback] Total Unique Matches: $consolidatedTotalMatches');
    print('📊 [Fallback] Match Percentage: $consolidatedMatchPercentage%');
    print('📊 [Fallback] Critical Gaps: ${criticalGaps.take(5).toList()}');

    return {
      'matched': consolidatedMatched,
      'missing': missing,
      'match_summary': {
        'total_jd_requirements': totalRequirements,
        'total_matches': consolidatedTotalMatches,
        'match_percentage': consolidatedMatchPercentage,
        'critical_gaps': criticalGaps.take(5).toList(), // Top 5 critical gaps
      }
    };
  }

  /// Basic text matching for fallback comparison
  static bool _isBasicMatch(String cvSkill, String jdSkill) {
    final cv = cvSkill.toLowerCase().trim();
    final jd = jdSkill.toLowerCase().trim();

    // Exact match
    if (cv == jd) return true;

    // Contains match
    if (cv.contains(jd) || jd.contains(cv)) return true;

    // Common abbreviations
    final abbreviations = {
      'javascript': ['js'],
      'python': ['py'],
      'machine learning': ['ml'],
      'artificial intelligence': ['ai'],
      'database': ['db'],
      'application programming interface': ['api'],
    };

    for (final entry in abbreviations.entries) {
      if ((cv == entry.key && entry.value.contains(jd)) ||
          (jd == entry.key && entry.value.contains(cv))) {
        return true;
      }
    }

    return false;
  }

  /// Creates an empty result structure
  static Map<String, dynamic> _createEmptyResult() {
    return {
      'matched': {
        'technical_skills': <Map<String, String>>[],
        'soft_skills': <Map<String, String>>[],
        'domain_keywords': <Map<String, String>>[],
      },
      'missing': {
        'technical_skills': <String>[],
        'soft_skills': <String>[],
        'domain_keywords': <String>[],
      },
      'match_summary': {
        'total_jd_requirements': 0,
        'total_matches': 0,
        'match_percentage': 0,
        'critical_gaps': <String>[],
      }
    };
  }

  /// Consolidates matched skills to remove duplicates
  /// Each CV skill should appear only once, even if it matches multiple JD requirements
  static Map<String, List<Map<String, String>>> _consolidateMatchedSkills(
      Map<String, List<Map<String, String>>> matched) {
    final consolidatedMatched = <String, List<Map<String, String>>>{};

    for (final category in [
      'technical_skills',
      'soft_skills',
      'domain_keywords'
    ]) {
      final categoryMatches = matched[category] ?? [];

      // Group by CV skill to remove duplicates
      final cvSkillGroups = <String, Map<String, dynamic>>{};

      for (final match in categoryMatches) {
        final cvSkill = match['cv_skill'] ?? '';
        final jdRequirement = match['jd_requirement'] ?? '';
        final matchReason = match['match_reason'] ?? '';

        if (!cvSkillGroups.containsKey(cvSkill)) {
          cvSkillGroups[cvSkill] = {
            'cv_skill': cvSkill,
            'jd_requirements': <String>[],
            'match_reasons': <String>[],
          };
        }

        cvSkillGroups[cvSkill]!['jd_requirements'].add(jdRequirement);
        cvSkillGroups[cvSkill]!['match_reasons'].add(matchReason);
      }

      // Create consolidated matches with unique CV skills
      final consolidatedCategory = <Map<String, String>>[];

      for (final entry in cvSkillGroups.entries) {
        final cvSkill = entry.key;
        final group = entry.value;
        final jdRequirements = List<String>.from(group['jd_requirements']);
        final matchReasons = List<String>.from(group['match_reasons']);

        // Use the first JD requirement and combine reasons if multiple
        final primaryJD = jdRequirements.isNotEmpty ? jdRequirements.first : '';

        String combinedReason;
        if (jdRequirements.length > 1) {
          // Multiple JD requirements matched to this CV skill
          combinedReason =
              'Matches ${jdRequirements.length} requirements: ${jdRequirements.join(', ')}';
        } else {
          combinedReason = matchReasons.isNotEmpty ? matchReasons.first : '';
        }

        consolidatedCategory.add({
          'cv_skill': cvSkill,
          'jd_requirement': primaryJD,
          'match_reason': combinedReason,
        });
      }

      consolidatedMatched[category] = consolidatedCategory;
    }

    print('✨ [Consolidation] Removed duplicate CV skills from matched results');
    return consolidatedMatched;
  }
}
