import 'package:flutter/foundation.dart';
import '../utils/skills_extractor.dart';

/// Data models for skills analysis results
class SkillsData {
  final List<String> technicalSkills;
  final List<String> softSkills;
  final List<String> domainKeywords;

  SkillsData({
    required this.technicalSkills,
    required this.softSkills,
    required this.domainKeywords,
  });

  factory SkillsData.fromJson(Map<String, dynamic> json) {
    return SkillsData(
      technicalSkills: List<String>.from(json['technical_skills'] ?? []),
      softSkills: List<String>.from(json['soft_skills'] ?? []),
      domainKeywords: List<String>.from(json['domain_keywords'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'technical_skills': technicalSkills,
      'soft_skills': softSkills,
      'domain_keywords': domainKeywords,
    };
  }

  bool get isEmpty =>
      technicalSkills.isEmpty && softSkills.isEmpty && domainKeywords.isEmpty;

  int get totalSkillsCount =>
      technicalSkills.length + softSkills.length + domainKeywords.length;
}

/// Complete skills analysis result containing both CV and JD skills
class SkillsAnalysisResult {
  final SkillsData cvSkills;
  final SkillsData jdSkills;
  final String? cvComprehensiveAnalysis;
  final String? jdComprehensiveAnalysis;
  final Map<String, dynamic>? expandableAnalysis;
  final List<String>? extractedKeywords;
  final AnalyzeMatchResult? analyzeMatch;
  final Duration executionDuration;
  final bool isSuccess;
  final String? errorMessage;
  // New: Pre-extracted comparison raw output (formatted text) and company name
  final String? preextractedRawOutput;
  final String? preextractedCompanyName;
  // New: Top-level company name from backend response
  final String? company;
  // New: Component analysis and ATS calculation results
  final ComponentAnalysisResult? componentAnalysis;
  final ATSResult? atsResult;
  // New: AI recommendation content
  final AIRecommendationResult? aiRecommendation;
  // New: warnings and suggestions from backend (e.g., cv_minimal)
  final List<dynamic>? warnings;
  final Map<String, dynamic>? suggestions;

  SkillsAnalysisResult({
    required this.cvSkills,
    required this.jdSkills,
    this.cvComprehensiveAnalysis,
    this.jdComprehensiveAnalysis,
    this.expandableAnalysis,
    this.extractedKeywords,
    this.analyzeMatch,
    this.executionDuration = Duration.zero,
    this.isSuccess = true,
    this.errorMessage,
    this.preextractedRawOutput,
    this.preextractedCompanyName,
    this.company,
    this.componentAnalysis,
    this.atsResult,
    this.aiRecommendation,
    this.warnings,
    this.suggestions,
  });

  factory SkillsAnalysisResult.fromJson(Map<String, dynamic> json) {
    // Debug logging to see what data is received
    debugPrint('🔍 [MODEL_DEBUG] Parsing SkillsAnalysisResult from JSON');
    debugPrint('   Keys in JSON: ${json.keys.toList()}');
    debugPrint(
      '   cv_comprehensive_analysis present: ${json.containsKey("cv_comprehensive_analysis")}',
    );
    debugPrint(
      '   jd_comprehensive_analysis present: ${json.containsKey("jd_comprehensive_analysis")}',
    );
    debugPrint(
      '   expandable_analysis present: ${json.containsKey("expandable_analysis")}',
    );
    debugPrint(
      '   analyze_match present: ${json.containsKey("analyze_match")}',
    );

    // Handle expandable_analysis structure
    final expandableAnalysis =
        json['expandable_analysis'] as Map<String, dynamic>?;

    // Get comprehensive analysis with fallback to expandable_analysis content
    String? cvComprehensiveAnalysis =
        json['cv_comprehensive_analysis'] as String?;
    String? jdComprehensiveAnalysis =
        json['jd_comprehensive_analysis'] as String?;

    // Debug the lengths
    debugPrint(
      '   cv_comprehensive_analysis length: ${cvComprehensiveAnalysis?.length ?? 0}',
    );
    debugPrint(
      '   jd_comprehensive_analysis length: ${jdComprehensiveAnalysis?.length ?? 0}',
    );

    // If comprehensive analysis is empty, try to get from expandable_analysis
    if ((cvComprehensiveAnalysis == null ||
            cvComprehensiveAnalysis.trim().isEmpty) &&
        expandableAnalysis != null) {
      final cvAnalysis =
          expandableAnalysis['cv_analysis'] as Map<String, dynamic>?;
      if (cvAnalysis != null) {
        cvComprehensiveAnalysis = cvAnalysis['content'] as String?;
      }
    }

    if ((jdComprehensiveAnalysis == null ||
            jdComprehensiveAnalysis.trim().isEmpty) &&
        expandableAnalysis != null) {
      final jdAnalysis =
          expandableAnalysis['jd_analysis'] as Map<String, dynamic>?;
      if (jdAnalysis != null) {
        jdComprehensiveAnalysis = jdAnalysis['content'] as String?;
      }
    }

    // Parse analyze match
    AnalyzeMatchResult? analyzeMatch;
    if (json['analyze_match'] != null) {
      analyzeMatch = AnalyzeMatchResult.fromJson(
        json['analyze_match'] as Map<String, dynamic>,
      );
    }

    // Parse pre-extracted comparison
    String? preextractedRaw;
    String? preextractedCompany;
    // Support both field name variations
    final preextractedData = json['preextracted_skills_comparison'] as Map<String, dynamic>? ??
        json['preextracted_comparison'] as Map<String, dynamic>?;
    if (preextractedData != null) {
      // Support both 'raw_output' and 'raw_content' field names
      preextractedRaw = preextractedData['raw_output'] as String? ??
          preextractedData['raw_content'] as String?;
      preextractedCompany = preextractedData['company_name'] as String?;
      debugPrint(
        '   preextracted comparison raw length: ${preextractedRaw?.length ?? 0}',
      );
      debugPrint(
        '   preextracted company: ${preextractedCompany ?? "null"}',
      );
    }
    // If backend attached company at top-level, use it as canonical company for polling
    final topLevelCompany = json['company'] as String?;
    if ((preextractedCompany == null || preextractedCompany.isEmpty) &&
        topLevelCompany != null &&
        topLevelCompany.isNotEmpty) {
      preextractedCompany = topLevelCompany;
    }

    // Debug final values
    debugPrint(
      '   FINAL cvComprehensiveAnalysis length: ${cvComprehensiveAnalysis?.length ?? 0}',
    );
    debugPrint(
      '   FINAL jdComprehensiveAnalysis length: ${jdComprehensiveAnalysis?.length ?? 0}',
    );
    debugPrint('   FINAL analyzeMatch present: ${analyzeMatch != null}');

    // Parse component analysis and ATS results (from polling response)
    ComponentAnalysisResult? componentAnalysis;
    ATSResult? atsResult;

    if (json['component_analysis'] != null) {
      componentAnalysis = ComponentAnalysisResult.fromJson(
        json['component_analysis'] as Map<String, dynamic>,
      );
      debugPrint('   component_analysis parsed successfully');
    }

    if (json['ats_score'] != null) {
      debugPrint('🔍 [SKILLS_RESULT] Found ats_score in JSON');
      final atsJson = json['ats_score'] as Map<String, dynamic>;
      debugPrint('   ats_score keys: ${atsJson.keys.toList()}');
      debugPrint('   final_ats_score: ${atsJson['final_ats_score']}');
      debugPrint('   scoring_version: ${atsJson['scoring_version']}');
      debugPrint('   breakdown present: ${atsJson.containsKey('breakdown')}');
      
      atsResult = ATSResult.fromJson(atsJson);
      debugPrint('✅ [SKILLS_RESULT] ats_score parsed successfully');
      debugPrint('   Parsed score: ${atsResult.finalATSScore}');
      debugPrint('   Parsed version: ${atsResult.scoringVersion}');
    } else {
      debugPrint('⚠️ [SKILLS_RESULT] No ats_score found in JSON');
    }

    // Parse AI recommendation content
    AIRecommendationResult? aiRecommendation;
    if (json['ai_recommendation'] != null) {
      aiRecommendation = AIRecommendationResult.fromJson(
        json['ai_recommendation'] as Map<String, dynamic>,
      );
      debugPrint('   ai_recommendation parsed successfully');
    }

    // Parse warnings and suggestions (optional)
    final warnings = json['warnings'] as List<dynamic>?;
    final suggestions = json['suggestions'] as Map<String, dynamic>?;

    // Parse CV skills with fallback extraction
    SkillsData cvSkills = SkillsData.fromJson(json['cv_skills'] ?? {});

    // If cv_skills is empty but we have comprehensive analysis, extract skills from text
    if (cvSkills.isEmpty &&
        cvComprehensiveAnalysis != null &&
        cvComprehensiveAnalysis.trim().isNotEmpty) {
      debugPrint(
        '🔧 [MODEL_DEBUG] cv_skills is empty, attempting fallback extraction from comprehensive analysis',
      );
      cvSkills = SkillsExtractor.extractFromComprehensiveAnalysis(
        cvComprehensiveAnalysis,
      );
      debugPrint(
        '   Fallback extracted CV skills: ${cvSkills.totalSkillsCount}',
      );
    }

    // Parse JD skills (normally these are fine, but add same fallback just in case)
    SkillsData jdSkills = SkillsData.fromJson(json['jd_skills'] ?? {});

    if (jdSkills.isEmpty &&
        jdComprehensiveAnalysis != null &&
        jdComprehensiveAnalysis.trim().isNotEmpty) {
      debugPrint(
        '🔧 [MODEL_DEBUG] jd_skills is empty, attempting fallback extraction from comprehensive analysis',
      );
      jdSkills = SkillsExtractor.extractFromComprehensiveAnalysis(
        jdComprehensiveAnalysis,
      );
      debugPrint(
        '   Fallback extracted JD skills: ${jdSkills.totalSkillsCount}',
      );
    }

    return SkillsAnalysisResult(
      cvSkills: cvSkills,
      jdSkills: jdSkills,
      cvComprehensiveAnalysis: cvComprehensiveAnalysis,
      jdComprehensiveAnalysis: jdComprehensiveAnalysis,
      expandableAnalysis: expandableAnalysis,
      extractedKeywords: json['extracted_keywords'] != null
          ? List<String>.from(json['extracted_keywords'])
          : null,
      analyzeMatch: analyzeMatch,
      isSuccess: true,
      preextractedRawOutput: preextractedRaw,
      preextractedCompanyName: preextractedCompany,
      company: topLevelCompany,
      componentAnalysis: componentAnalysis,
      atsResult: atsResult,
      aiRecommendation: aiRecommendation,
      warnings: warnings,
      suggestions: suggestions,
    );
  }

  factory SkillsAnalysisResult.error(String errorMessage) {
    return SkillsAnalysisResult(
      cvSkills: SkillsData(
        technicalSkills: [],
        softSkills: [],
        domainKeywords: [],
      ),
      jdSkills: SkillsData(
        technicalSkills: [],
        softSkills: [],
        domainKeywords: [],
      ),
      expandableAnalysis: null,
      analyzeMatch: null,
      isSuccess: false,
      errorMessage: errorMessage,
      componentAnalysis: null,
      atsResult: null,
      aiRecommendation: null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'cv_skills': cvSkills.toJson(),
      'jd_skills': jdSkills.toJson(),
      'cv_comprehensive_analysis': cvComprehensiveAnalysis,
      'jd_comprehensive_analysis': jdComprehensiveAnalysis,
      'expandable_analysis': expandableAnalysis,
      'extracted_keywords': extractedKeywords,
      'analyze_match': analyzeMatch?.toJson(),
      'is_success': isSuccess,
      'error_message': errorMessage,
      'preextracted_skills_comparison': preextractedRawOutput == null
          ? null
          : {
              'raw_output': preextractedRawOutput,
              'company_name': preextractedCompanyName,
            },
      'component_analysis': componentAnalysis?.toJson(),
      'ats_score': atsResult?.toJson(),
      'ai_recommendation': aiRecommendation?.toJson(),
      'warnings': warnings,
      'suggestions': suggestions,
    };
  }

  bool get isEmpty => cvSkills.isEmpty && jdSkills.isEmpty;

  /// Create a copy of this result with updated fields
  SkillsAnalysisResult copyWith({
    SkillsData? cvSkills,
    SkillsData? jdSkills,
    String? cvComprehensiveAnalysis,
    String? jdComprehensiveAnalysis,
    Map<String, dynamic>? expandableAnalysis,
    List<String>? extractedKeywords,
    AnalyzeMatchResult? analyzeMatch,
    Duration? executionDuration,
    bool? isSuccess,
    String? errorMessage,
    String? preextractedRawOutput,
    String? preextractedCompanyName,
    String? company,
    ComponentAnalysisResult? componentAnalysis,
    ATSResult? atsResult,
    AIRecommendationResult? aiRecommendation,
    List<dynamic>? warnings,
    Map<String, dynamic>? suggestions,
  }) {
    return SkillsAnalysisResult(
      cvSkills: cvSkills ?? this.cvSkills,
      jdSkills: jdSkills ?? this.jdSkills,
      cvComprehensiveAnalysis:
          cvComprehensiveAnalysis ?? this.cvComprehensiveAnalysis,
      jdComprehensiveAnalysis:
          jdComprehensiveAnalysis ?? this.jdComprehensiveAnalysis,
      expandableAnalysis: expandableAnalysis ?? this.expandableAnalysis,
      extractedKeywords: extractedKeywords ?? this.extractedKeywords,
      analyzeMatch: analyzeMatch ?? this.analyzeMatch,
      executionDuration: executionDuration ?? this.executionDuration,
      isSuccess: isSuccess ?? this.isSuccess,
      errorMessage: errorMessage ?? this.errorMessage,
      preextractedRawOutput:
          preextractedRawOutput ?? this.preextractedRawOutput,
      preextractedCompanyName:
          preextractedCompanyName ?? this.preextractedCompanyName,
      company: company ?? this.company,
      componentAnalysis: componentAnalysis ?? this.componentAnalysis,
      atsResult: atsResult ?? this.atsResult,
      aiRecommendation: aiRecommendation ?? this.aiRecommendation,
      warnings: warnings ?? this.warnings,
      suggestions: suggestions ?? this.suggestions,
    );
  }

  bool get hasPreextractedComparison =>
      (preextractedRawOutput != null && preextractedRawOutput!.isNotEmpty);
}

/// Analyze match result containing recruiter-style assessment
class AnalyzeMatchResult {
  final String rawAnalysis;
  final String? companyName;
  final String? filePath;
  final String? error;

  AnalyzeMatchResult({
    required this.rawAnalysis,
    this.companyName,
    this.filePath,
    this.error,
  });

  factory AnalyzeMatchResult.fromJson(Map<String, dynamic> json) {
    debugPrint('🔍 [MODEL_DEBUG] Parsing AnalyzeMatchResult from JSON');
    debugPrint('   Keys in JSON: ${json.keys.toList()}');
    debugPrint(
      '   raw_analysis length: ${(json['raw_analysis'] as String?)?.length ?? 0}',
    );

    return AnalyzeMatchResult(
      rawAnalysis: json['raw_analysis'] as String? ?? '',
      companyName: json['company_name'] as String?,
      filePath: json['analyze_match_file_path'] as String?,
      error: json['error'] as String?,
    );
  }

  factory AnalyzeMatchResult.error(String errorMessage) {
    return AnalyzeMatchResult(rawAnalysis: '', error: errorMessage);
  }

  Map<String, dynamic> toJson() {
    return {
      'raw_analysis': rawAnalysis,
      'company_name': companyName,
      'analyze_match_file_path': filePath,
      'error': error,
    };
  }

  bool get isEmpty => rawAnalysis.trim().isEmpty;
  bool get hasError => error != null && error!.isNotEmpty;
}

/// ATS Score calculation result (v2 only - 65/35 split)
class ATSResult {
  final String timestamp;
  final double finalATSScore;
  final String categoryStatus;
  final String recommendation;
  final ATSBreakdown breakdown;
  final String scoringVersion; // Always 'v2_65_35_split'

  ATSResult({
    required this.timestamp,
    required this.finalATSScore,
    required this.categoryStatus,
    required this.recommendation,
    required this.breakdown,
    required this.scoringVersion,
  });

  factory ATSResult.fromJson(Map<String, dynamic> json) {
    debugPrint('🔍 [ATS_RESULT] Parsing ATSResult from JSON');
    debugPrint('   Keys: ${json.keys.toList()}');
    debugPrint('   final_ats_score: ${json['final_ats_score']}');
    debugPrint('   category_status: ${json['category_status']}');
    debugPrint('   scoring_version: ${json['scoring_version']}');
    
    final breakdownJson = json['breakdown'] as Map<String, dynamic>? ?? {};
    debugPrint('   breakdown keys: ${breakdownJson.keys.toList()}');
    
    final result = ATSResult(
      timestamp: json['timestamp'] as String? ?? '',
      finalATSScore: (json['final_ats_score'] as num?)?.toDouble() ?? 0.0,
      categoryStatus: json['category_status'] as String? ?? '',
      recommendation: json['recommendation'] as String? ?? '',
      breakdown: ATSBreakdown.fromJson(breakdownJson),
      scoringVersion: json['scoring_version'] as String? ?? 'v2_65_35_split',
    );
    
    debugPrint('✅ [ATS_RESULT] Parsed: score=${result.finalATSScore}, version=${result.scoringVersion}');
    return result;
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp,
      'final_ats_score': finalATSScore,
      'category_status': categoryStatus,
      'recommendation': recommendation,
      'breakdown': breakdown.toJson(),
      'scoring_version': scoringVersion,
    };
  }
}

/// ATS Breakdown containing detailed scoring (v2 only)
class ATSBreakdown {
  final ATSCategory1 category1;
  final ATSCategory2 category2;
  final double baseScore;
  final double bonusPoints;
  final double boostApplied;

  ATSBreakdown({
    required this.category1,
    required this.category2,
    required this.baseScore,
    required this.bonusPoints,
    required this.boostApplied,
  });

  factory ATSBreakdown.fromJson(Map<String, dynamic> json) {
    debugPrint('🔍 [ATS_BREAKDOWN] Parsing ATSBreakdown from JSON');
    debugPrint('   Keys: ${json.keys.toList()}');
    debugPrint('   base_score: ${json['base_score']}');
    debugPrint('   bonus_points: ${json['bonus_points']}');
    debugPrint('   boost_applied: ${json['boost_applied']}');
    
    final category1Json = json['category1'] as Map<String, dynamic>? ?? {};
    final category2Json = json['category2'] as Map<String, dynamic>? ?? {};
    
    debugPrint('   category1 keys: ${category1Json.keys.toList()}');
    debugPrint('   category2 keys: ${category2Json.keys.toList()}');
    
    final result = ATSBreakdown(
      category1: ATSCategory1.fromJson(category1Json),
      category2: ATSCategory2.fromJson(category2Json),
      baseScore: (json['base_score'] as num?)?.toDouble() ?? 0.0,
      bonusPoints: (json['bonus_points'] as num?)?.toDouble() ?? 0.0,
      boostApplied: (json['boost_applied'] as num?)?.toDouble() ?? 0.0,
    );
    
    debugPrint('✅ [ATS_BREAKDOWN] Parsed: base=${result.baseScore}, bonus=${result.bonusPoints}, boost=${result.boostApplied}');
    return result;
  }

  Map<String, dynamic> toJson() {
    return {
      'category1': category1.toJson(),
      'category2': category2.toJson(),
      'base_score': baseScore,
      'bonus_points': bonusPoints,
      'boost_applied': boostApplied,
    };
  }
}

/// ATS Category 1 - Keyword Matching (v2 only - 65 points)
class ATSCategory1 {
  final double score;
  final double maxPoints; // Always 65 for v2
  final double technicalSkillsMatchRate;
  final double domainKeywordsMatchRate;
  final double softSkillsMatchRate;
  final double technicalPoints; // Points from technical skills (max 40)
  final double domainPoints; // Points from domain keywords (max 10)
  final double softPoints; // Points from soft skills (max 15)
  final Map<String, int> missingCounts;

  ATSCategory1({
    required this.score,
    required this.maxPoints,
    required this.technicalSkillsMatchRate,
    required this.domainKeywordsMatchRate,
    required this.softSkillsMatchRate,
    required this.technicalPoints,
    required this.domainPoints,
    required this.softPoints,
    required this.missingCounts,
  });

  factory ATSCategory1.fromJson(Map<String, dynamic> json) {
    debugPrint('🔍 [CATEGORY1] Parsing ATSCategory1 from JSON');
    debugPrint('   Keys: ${json.keys.toList()}');
    debugPrint('   score: ${json['score']}');
    debugPrint('   max_points: ${json['max_points']}');
    debugPrint('   technical_skills_match_rate: ${json['technical_skills_match_rate']}');
    debugPrint('   technical_points: ${json['technical_points']}');
    
    final missingCounts = json['missing_counts'] as Map<String, dynamic>? ?? {};
    
    final result = ATSCategory1(
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      maxPoints: (json['max_points'] as num?)?.toDouble() ?? 65.0,
      technicalSkillsMatchRate:
          (json['technical_skills_match_rate'] as num?)?.toDouble() ?? 0.0,
      domainKeywordsMatchRate:
          (json['domain_keywords_match_rate'] as num?)?.toDouble() ?? 0.0,
      softSkillsMatchRate:
          (json['soft_skills_match_rate'] as num?)?.toDouble() ?? 0.0,
      technicalPoints: (json['technical_points'] as num?)?.toDouble() ?? 0.0,
      domainPoints: (json['domain_points'] as num?)?.toDouble() ?? 0.0,
      softPoints: (json['soft_points'] as num?)?.toDouble() ?? 0.0,
      missingCounts: {
        'technical': missingCounts['technical'] as int? ?? 0,
        'domain': missingCounts['domain'] as int? ?? 0,
        'soft': missingCounts['soft'] as int? ?? 0,
      },
    );
    
    debugPrint('✅ [CATEGORY1] Parsed: score=${result.score}/${result.maxPoints}, tech=${result.technicalPoints}/40, domain=${result.domainPoints}/10, soft=${result.softPoints}/15');
    return result;
  }

  Map<String, dynamic> toJson() {
    return {
      'score': score,
      'max_points': maxPoints,
      'technical_skills_match_rate': technicalSkillsMatchRate,
      'domain_keywords_match_rate': domainKeywordsMatchRate,
      'soft_skills_match_rate': softSkillsMatchRate,
      'technical_points': technicalPoints,
      'domain_points': domainPoints,
      'soft_points': softPoints,
      'missing_counts': missingCounts,
    };
  }
}

/// ATS Category 2 - AI Component Analysis (v2 only - 35 points)
class ATSCategory2 {
  final double score;
  final double maxPoints; // Always 35 for v2
  final ATSCategory2Component technicalSkillsComponent; // 22 points
  final ATSCategory2Component experienceFitComponent; // 13 points

  ATSCategory2({
    required this.score,
    required this.maxPoints,
    required this.technicalSkillsComponent,
    required this.experienceFitComponent,
  });

  factory ATSCategory2.fromJson(Map<String, dynamic> json) {
    debugPrint('🔍 [CATEGORY2] Parsing ATSCategory2 from JSON');
    debugPrint('   Keys: ${json.keys.toList()}');
    debugPrint('   score: ${json['score']}');
    debugPrint('   max_points: ${json['max_points']}');
    debugPrint('   technical_skills_component: ${json['technical_skills_component']}');
    debugPrint('   experience_fit_component: ${json['experience_fit_component']}');
    
    final techSkillsJson = json['technical_skills_component'] as Map<String, dynamic>?;
    final expFitJson = json['experience_fit_component'] as Map<String, dynamic>?;
    
    if (techSkillsJson == null || expFitJson == null) {
      debugPrint('❌ [CATEGORY2] Missing required components!');
      throw Exception('Category2 must have both technical_skills_component and experience_fit_component');
    }
    
    final result = ATSCategory2(
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      maxPoints: (json['max_points'] as num?)?.toDouble() ?? 35.0,
      technicalSkillsComponent: ATSCategory2Component.fromJson(techSkillsJson, defaultMaxPoints: 22.0),
      experienceFitComponent: ATSCategory2Component.fromJson(expFitJson, defaultMaxPoints: 13.0),
    );
    
    debugPrint('✅ [CATEGORY2] Parsed: score=${result.score}/${result.maxPoints}, tech=${result.technicalSkillsComponent.score}/22, exp=${result.experienceFitComponent.score}/13');
    return result;
  }

  Map<String, dynamic> toJson() {
    return {
      'score': score,
      'max_points': maxPoints,
      'technical_skills_component': technicalSkillsComponent.toJson(),
      'experience_fit_component': experienceFitComponent.toJson(),
    };
  }
}

/// ATS Category 2 Component (v2 structure)
class ATSCategory2Component {
  final double score;
  final double maxPoints;
  final double average;

  ATSCategory2Component({
    required this.score,
    required this.maxPoints,
    required this.average,
  });

  factory ATSCategory2Component.fromJson(
    Map<String, dynamic> json, {
    double? defaultMaxPoints,
  }) {
    debugPrint('🔍 [CATEGORY2_COMPONENT] Parsing component');
    debugPrint('   score: ${json['score']}');
    debugPrint('   max_points: ${json['max_points']}');
    debugPrint('   average: ${json['average']}');
    debugPrint('   defaultMaxPoints: $defaultMaxPoints');
    
    final result = ATSCategory2Component(
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      maxPoints: (json['max_points'] as num?)?.toDouble() ?? defaultMaxPoints ?? 0.0,
      average: (json['average'] as num?)?.toDouble() ?? 0.0,
    );
    
    debugPrint('✅ [CATEGORY2_COMPONENT] Parsed: ${result.score}/${result.maxPoints} (avg: ${result.average}%)');
    return result;
  }

  Map<String, dynamic> toJson() {
    return {
      'score': score,
      'max_points': maxPoints,
      'average': average,
    };
  }
}

/// Component Analysis Result
class ComponentAnalysisResult {
  final String timestamp;
  final Map<String, double> extractedScores;
  final Map<String, dynamic> componentDetails;

  ComponentAnalysisResult({
    required this.timestamp,
    required this.extractedScores,
    required this.componentDetails,
  });

  factory ComponentAnalysisResult.fromJson(Map<String, dynamic> json) {
    final scoresMap = json['extracted_scores'] as Map<String, dynamic>? ?? {};
    final extractedScores = <String, double>{};

    // Convert all score values to doubles
    scoresMap.forEach((key, value) {
      if (value is num) {
        extractedScores[key] = value.toDouble();
      }
    });

    return ComponentAnalysisResult(
      timestamp: json['timestamp'] as String? ?? '',
      extractedScores: extractedScores,
      componentDetails:
          json['component_details'] as Map<String, dynamic>? ?? {},
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp,
      'extracted_scores': extractedScores,
      'component_details': componentDetails,
    };
  }

  // Get key scores for display
  double get skillsRelevance => extractedScores['skills_relevance'] ?? 0.0;
  double get experienceAlignment =>
      extractedScores['experience_alignment'] ?? 0.0;
  double get industryFit => extractedScores['industry_fit'] ?? 0.0;
  double get roleSeniority => extractedScores['role_seniority'] ?? 0.0;
  double get technicalDepth => extractedScores['technical_depth'] ?? 0.0;
}

/// AI Recommendation Result containing markdown content and metadata
class AIRecommendationResult {
  final String content;
  final String? generatedAt;
  final Map<String, dynamic>? modelInfo;

  AIRecommendationResult({
    required this.content,
    this.generatedAt,
    this.modelInfo,
  });

  factory AIRecommendationResult.fromJson(Map<String, dynamic> json) {
    return AIRecommendationResult(
      content: json['content'] as String? ?? '',
      generatedAt: json['generated_at'] as String?,
      modelInfo: json['model_info'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'content': content,
      'generated_at': generatedAt,
      'model_info': modelInfo,
    };
  }

  bool get isEmpty => content.trim().isEmpty;
  bool get hasContent => content.trim().isNotEmpty;
}
