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
    if (json['preextracted_skills_comparison'] != null) {
      final m = json['preextracted_skills_comparison'] as Map<String, dynamic>;
      preextractedRaw = m['raw_output'] as String?;
      preextractedCompany = m['company_name'] as String?;
      debugPrint(
        '   preextracted_skills_comparison raw length: ${preextractedRaw?.length ?? 0}',
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
      atsResult = ATSResult.fromJson(json['ats_score'] as Map<String, dynamic>);
      debugPrint('   ats_score parsed successfully');
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

/// ATS Score calculation result
class ATSResult {
  final String timestamp;
  final double finalATSScore;
  final String categoryStatus;
  final String recommendation;
  final ATSBreakdown breakdown;

  ATSResult({
    required this.timestamp,
    required this.finalATSScore,
    required this.categoryStatus,
    required this.recommendation,
    required this.breakdown,
  });

  factory ATSResult.fromJson(Map<String, dynamic> json) {
    return ATSResult(
      timestamp: json['timestamp'] as String? ?? '',
      finalATSScore: (json['final_ats_score'] as num?)?.toDouble() ?? 0.0,
      categoryStatus: json['category_status'] as String? ?? '',
      recommendation: json['recommendation'] as String? ?? '',
      breakdown: ATSBreakdown.fromJson(
        json['breakdown'] as Map<String, dynamic>? ?? {},
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp,
      'final_ats_score': finalATSScore,
      'category_status': categoryStatus,
      'recommendation': recommendation,
      'breakdown': breakdown.toJson(),
    };
  }
}

/// ATS Breakdown containing detailed scoring
class ATSBreakdown {
  final ATSCategory1 category1;
  final ATSCategory2 category2;
  final double ats1Score;
  final double bonusPoints;

  ATSBreakdown({
    required this.category1,
    required this.category2,
    required this.ats1Score,
    required this.bonusPoints,
  });

  factory ATSBreakdown.fromJson(Map<String, dynamic> json) {
    return ATSBreakdown(
      category1: ATSCategory1.fromJson(
        json['category1'] as Map<String, dynamic>? ?? {},
      ),
      category2: ATSCategory2.fromJson(
        json['category2'] as Map<String, dynamic>? ?? {},
      ),
      ats1Score: (json['ats1_score'] as num?)?.toDouble() ?? 0.0,
      bonusPoints: (json['bonus_points'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'category1': category1.toJson(),
      'category2': category2.toJson(),
      'ats1_score': ats1Score,
      'bonus_points': bonusPoints,
    };
  }
}

/// ATS Category 1 - Skills matching
class ATSCategory1 {
  final double score;
  final double technicalSkillsMatchRate;
  final double domainKeywordsMatchRate;
  final double softSkillsMatchRate;
  final Map<String, int> missingCounts;

  ATSCategory1({
    required this.score,
    required this.technicalSkillsMatchRate,
    required this.domainKeywordsMatchRate,
    required this.softSkillsMatchRate,
    required this.missingCounts,
  });

  factory ATSCategory1.fromJson(Map<String, dynamic> json) {
    final missingCounts = json['missing_counts'] as Map<String, dynamic>? ?? {};
    return ATSCategory1(
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      technicalSkillsMatchRate:
          (json['technical_skills_match_rate'] as num?)?.toDouble() ?? 0.0,
      domainKeywordsMatchRate:
          (json['domain_keywords_match_rate'] as num?)?.toDouble() ?? 0.0,
      softSkillsMatchRate:
          (json['soft_skills_match_rate'] as num?)?.toDouble() ?? 0.0,
      missingCounts: {
        'technical': missingCounts['technical'] as int? ?? 0,
        'domain': missingCounts['domain'] as int? ?? 0,
        'soft': missingCounts['soft'] as int? ?? 0,
      },
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'score': score,
      'technical_skills_match_rate': technicalSkillsMatchRate,
      'domain_keywords_match_rate': domainKeywordsMatchRate,
      'soft_skills_match_rate': softSkillsMatchRate,
      'missing_counts': missingCounts,
    };
  }
}

/// ATS Category 2 - Experience and competency
class ATSCategory2 {
  final double score;
  final double coreCompetencyAvg;
  final double experienceSeniorityAvg;
  final double potentialAbilityAvg;
  final double companyFitAvg;

  ATSCategory2({
    required this.score,
    required this.coreCompetencyAvg,
    required this.experienceSeniorityAvg,
    required this.potentialAbilityAvg,
    required this.companyFitAvg,
  });

  factory ATSCategory2.fromJson(Map<String, dynamic> json) {
    return ATSCategory2(
      score: (json['score'] as num?)?.toDouble() ?? 0.0,
      coreCompetencyAvg:
          (json['core_competency_avg'] as num?)?.toDouble() ?? 0.0,
      experienceSeniorityAvg:
          (json['experience_seniority_avg'] as num?)?.toDouble() ?? 0.0,
      potentialAbilityAvg:
          (json['potential_ability_avg'] as num?)?.toDouble() ?? 0.0,
      companyFitAvg: (json['company_fit_avg'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'score': score,
      'core_competency_avg': coreCompetencyAvg,
      'experience_seniority_avg': experienceSeniorityAvg,
      'potential_ability_avg': potentialAbilityAvg,
      'company_fit_avg': companyFitAvg,
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
