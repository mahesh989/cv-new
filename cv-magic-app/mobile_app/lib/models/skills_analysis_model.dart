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
  final Map<String, dynamic>? expandableAnalysis;
  final List<String>? extractedKeywords;
  final Duration executionDuration;
  final bool isSuccess;
  final String? errorMessage;

  SkillsAnalysisResult({
    required this.cvSkills,
    required this.jdSkills,
    this.cvComprehensiveAnalysis,
    this.jdComprehensiveAnalysis,
    this.expandableAnalysis,
    this.extractedKeywords,
    this.executionDuration = Duration.zero,
    this.isSuccess = true,
    this.errorMessage,
  });

  factory SkillsAnalysisResult.fromJson(Map<String, dynamic> json) {
    // Debug logging to see what data is received
    debugPrint('🔍 [MODEL_DEBUG] Parsing SkillsAnalysisResult from JSON');
    debugPrint('   Keys in JSON: ${json.keys.toList()}');
    debugPrint('   cv_comprehensive_analysis present: ${json.containsKey("cv_comprehensive_analysis")}');
    debugPrint('   jd_comprehensive_analysis present: ${json.containsKey("jd_comprehensive_analysis")}');
    debugPrint('   expandable_analysis present: ${json.containsKey("expandable_analysis")}');
    
    // Handle expandable_analysis structure
    final expandableAnalysis = json['expandable_analysis'] as Map<String, dynamic>?;
    
    // Get comprehensive analysis with fallback to expandable_analysis content
    String? cvComprehensiveAnalysis = json['cv_comprehensive_analysis'] as String?;
    String? jdComprehensiveAnalysis = json['jd_comprehensive_analysis'] as String?;
    
    // Debug the lengths
    debugPrint('   cv_comprehensive_analysis length: ${cvComprehensiveAnalysis?.length ?? 0}');
    debugPrint('   jd_comprehensive_analysis length: ${jdComprehensiveAnalysis?.length ?? 0}');
    
    // If comprehensive analysis is empty, try to get from expandable_analysis
    if ((cvComprehensiveAnalysis == null || cvComprehensiveAnalysis.trim().isEmpty) && 
        expandableAnalysis != null) {
      final cvAnalysis = expandableAnalysis['cv_analysis'] as Map<String, dynamic>?;
      if (cvAnalysis != null) {
        cvComprehensiveAnalysis = cvAnalysis['content'] as String?;
      }
    }
    
    if ((jdComprehensiveAnalysis == null || jdComprehensiveAnalysis.trim().isEmpty) && 
        expandableAnalysis != null) {
      final jdAnalysis = expandableAnalysis['jd_analysis'] as Map<String, dynamic>?;
      if (jdAnalysis != null) {
        jdComprehensiveAnalysis = jdAnalysis['content'] as String?;
      }
    }
    
    // Debug final values
    debugPrint('   FINAL cvComprehensiveAnalysis length: ${cvComprehensiveAnalysis?.length ?? 0}');
    debugPrint('   FINAL jdComprehensiveAnalysis length: ${jdComprehensiveAnalysis?.length ?? 0}');
    if (cvComprehensiveAnalysis != null && cvComprehensiveAnalysis.isNotEmpty) {
      debugPrint('   CV Analysis preview: ${cvComprehensiveAnalysis.substring(0, cvComprehensiveAnalysis.length > 200 ? 200 : cvComprehensiveAnalysis.length)}');
    }
    if (jdComprehensiveAnalysis != null && jdComprehensiveAnalysis.isNotEmpty) {
      debugPrint('   JD Analysis preview: ${jdComprehensiveAnalysis.substring(0, jdComprehensiveAnalysis.length > 200 ? 200 : jdComprehensiveAnalysis.length)}');
    }
    
    return SkillsAnalysisResult(
      cvSkills: SkillsData.fromJson(json['cv_skills'] ?? {}),
      jdSkills: SkillsData.fromJson(json['jd_skills'] ?? {}),
      cvComprehensiveAnalysis: cvComprehensiveAnalysis,
      jdComprehensiveAnalysis: jdComprehensiveAnalysis,
      expandableAnalysis: expandableAnalysis,
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
      expandableAnalysis: null,
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
      'is_success': isSuccess,
      'error_message': errorMessage,
    };
  }

  bool get isEmpty => cvSkills.isEmpty && jdSkills.isEmpty;
}
