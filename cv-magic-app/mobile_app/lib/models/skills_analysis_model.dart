import 'package:flutter/foundation.dart';

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
  });

  factory SkillsAnalysisResult.fromJson(Map<String, dynamic> json) {
    // Debug logging to see what data is received
    debugPrint('🔍 [MODEL_DEBUG] Parsing SkillsAnalysisResult from JSON');
    debugPrint('   Keys in JSON: ${json.keys.toList()}');
    debugPrint(
        '   cv_comprehensive_analysis present: ${json.containsKey("cv_comprehensive_analysis")}');
    debugPrint(
        '   jd_comprehensive_analysis present: ${json.containsKey("jd_comprehensive_analysis")}');
    debugPrint(
        '   expandable_analysis present: ${json.containsKey("expandable_analysis")}');
    debugPrint(
        '   analyze_match present: ${json.containsKey("analyze_match")}');

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
        '   cv_comprehensive_analysis length: ${cvComprehensiveAnalysis?.length ?? 0}');
    debugPrint(
        '   jd_comprehensive_analysis length: ${jdComprehensiveAnalysis?.length ?? 0}');

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
          json['analyze_match'] as Map<String, dynamic>);
    }

    // Parse pre-extracted comparison
    String? preextractedRaw;
    String? preextractedCompany;
    if (json['preextracted_skills_comparison'] != null) {
      final m = json['preextracted_skills_comparison'] as Map<String, dynamic>;
      preextractedRaw = m['raw_output'] as String?;
      preextractedCompany = m['company_name'] as String?;
      debugPrint(
          '   preextracted_skills_comparison raw length: ${preextractedRaw?.length ?? 0}');
    }

    // Debug final values
    debugPrint(
        '   FINAL cvComprehensiveAnalysis length: ${cvComprehensiveAnalysis?.length ?? 0}');
    debugPrint(
        '   FINAL jdComprehensiveAnalysis length: ${jdComprehensiveAnalysis?.length ?? 0}');
    debugPrint('   FINAL analyzeMatch present: ${analyzeMatch != null}');

    return SkillsAnalysisResult(
      cvSkills: SkillsData.fromJson(json['cv_skills'] ?? {}),
      jdSkills: SkillsData.fromJson(json['jd_skills'] ?? {}),
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
    };
  }

  bool get isEmpty => cvSkills.isEmpty && jdSkills.isEmpty;

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
        '   raw_analysis length: ${(json['raw_analysis'] as String?)?.length ?? 0}');

    return AnalyzeMatchResult(
      rawAnalysis: json['raw_analysis'] as String? ?? '',
      companyName: json['company_name'] as String?,
      filePath: json['analyze_match_file_path'] as String?,
      error: json['error'] as String?,
    );
  }

  factory AnalyzeMatchResult.error(String errorMessage) {
    return AnalyzeMatchResult(
      rawAnalysis: '',
      error: errorMessage,
    );
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
