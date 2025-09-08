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
      technicalSkills.isEmpty && 
      softSkills.isEmpty && 
      domainKeywords.isEmpty;

  int get totalSkillsCount => 
      technicalSkills.length + 
      softSkills.length + 
      domainKeywords.length;
}

/// Complete skills analysis result containing both CV and JD skills
class SkillsAnalysisResult {
  final SkillsData cvSkills;
  final SkillsData jdSkills;
  final String? cvComprehensiveAnalysis;
  final String? jdComprehensiveAnalysis;
  final List<String>? extractedKeywords;
  final Duration executionDuration;
  final bool isSuccess;
  final String? errorMessage;

  SkillsAnalysisResult({
    required this.cvSkills,
    required this.jdSkills,
    this.cvComprehensiveAnalysis,
    this.jdComprehensiveAnalysis,
    this.extractedKeywords,
    this.executionDuration = Duration.zero,
    this.isSuccess = true,
    this.errorMessage,
  });

  factory SkillsAnalysisResult.fromJson(Map<String, dynamic> json) {
    return SkillsAnalysisResult(
      cvSkills: SkillsData.fromJson(json['cv_skills'] ?? {}),
      jdSkills: SkillsData.fromJson(json['jd_skills'] ?? {}),
      cvComprehensiveAnalysis: json['cv_comprehensive_analysis'] as String?,
      jdComprehensiveAnalysis: json['jd_comprehensive_analysis'] as String?,
      extractedKeywords: json['extracted_keywords'] != null
          ? List<String>.from(json['extracted_keywords'])
          : null,
      isSuccess: true,
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
      'extracted_keywords': extractedKeywords,
      'is_success': isSuccess,
      'error_message': errorMessage,
    };
  }

  bool get isEmpty => cvSkills.isEmpty && jdSkills.isEmpty;
}
