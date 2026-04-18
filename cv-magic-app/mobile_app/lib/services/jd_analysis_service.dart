import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../core/config/app_config.dart';

class JDAnalysisService {
  static const String baseUrl = AppConfig.baseUrl; // Configured backend URL

  // Authentication token - you'll need to implement proper auth
  String? _authToken;

  void setAuthToken(String token) {
    _authToken = token;
  }

  Map<String, String> _getHeaders() {
    final headers = {
      'Content-Type': 'application/json',
    };

    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }

    return headers;
  }

  /// Login to get authentication token
  Future<String> login() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': '', // Empty for development
          'password': '', // Empty for development
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['access_token'];
        setAuthToken(token);
        return token;
      } else {
        throw JDAnalysisException(
            'Login failed: ${response.statusCode}', response.body);
      }
    } catch (e) {
      throw JDAnalysisException('Login error: $e');
    }
  }

  /// Analyze job description and get categorized skills
  Future<JDAnalysisResult> analyzeSkills({
    required String companyName,
    bool forceRefresh = false,
    double temperature = 0.3,
  }) async {
    try {
      // Ensure we have a token
      if (_authToken == null) {
        await login();
      }

      final response = await http.post(
        Uri.parse('$baseUrl/api/analyze-jd/$companyName'),
        headers: _getHeaders(),
        body: jsonEncode({
          'force_refresh': forceRefresh,
          'temperature': temperature,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return JDAnalysisResult.fromJson(data['data']);
      } else {
        throw JDAnalysisException(
          'Analysis failed: ${response.statusCode}',
          response.body,
        );
      }
    } catch (e) {
      debugPrint('Error analyzing skills: $e');
      rethrow;
    }
  }

  /// Get saved analysis results
  Future<JDAnalysisResult> getAnalysis(String companyName) async {
    try {
      // Ensure we have a token
      if (_authToken == null) {
        await login();
      }

      final response = await http.get(
        Uri.parse('$baseUrl/api/jd-analysis/$companyName'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return JDAnalysisResult.fromJson(data['data']);
      } else {
        throw JDAnalysisException(
          'Failed to get analysis: ${response.statusCode}',
          response.body,
        );
      }
    } catch (e) {
      debugPrint('Error getting analysis: $e');
      rethrow;
    }
  }

  /// Get technical skills only
  Future<List<String>> getTechnicalSkills({
    required String companyName,
    bool requiredOnly = false,
  }) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$baseUrl/api/jd-analysis/$companyName/technical?required_only=$requiredOnly'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['data']['skills']);
      } else {
        throw JDAnalysisException(
          'Failed to get technical skills: ${response.statusCode}',
          response.body,
        );
      }
    } catch (e) {
      debugPrint('Error getting technical skills: $e');
      rethrow;
    }
  }

  /// Get soft skills only
  Future<List<String>> getSoftSkills({
    required String companyName,
    bool requiredOnly = false,
  }) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$baseUrl/api/jd-analysis/$companyName/soft-skills?required_only=$requiredOnly'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['data']['skills']);
      } else {
        throw JDAnalysisException(
          'Failed to get soft skills: ${response.statusCode}',
          response.body,
        );
      }
    } catch (e) {
      debugPrint('Error getting soft skills: $e');
      rethrow;
    }
  }

  /// Get experience requirements
  Future<List<String>> getExperienceRequirements({
    required String companyName,
    bool requiredOnly = false,
  }) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$baseUrl/api/jd-analysis/$companyName/experience?required_only=$requiredOnly'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['data']['requirements']);
      } else {
        throw JDAnalysisException(
          'Failed to get experience requirements: ${response.statusCode}',
          response.body,
        );
      }
    } catch (e) {
      debugPrint('Error getting experience requirements: $e');
      rethrow;
    }
  }

  /// Get domain knowledge
  Future<List<String>> getDomainKnowledge({
    required String companyName,
    bool requiredOnly = false,
  }) async {
    try {
      final response = await http.get(
        Uri.parse(
            '$baseUrl/api/jd-analysis/$companyName/domain-knowledge?required_only=$requiredOnly'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['data']['knowledge']);
      } else {
        throw JDAnalysisException(
          'Failed to get domain knowledge: ${response.statusCode}',
          response.body,
        );
      }
    } catch (e) {
      debugPrint('Error getting domain knowledge: $e');
      rethrow;
    }
  }

  /// Get all categorized skills
  Future<CategorizedSkills> getCategorizedSkills(String companyName) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/jd-analysis/$companyName/categorized'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return CategorizedSkills.fromJson(data['data']);
      } else {
        throw JDAnalysisException(
          'Failed to get categorized skills: ${response.statusCode}',
          response.body,
        );
      }
    } catch (e) {
      debugPrint('Error getting categorized skills: $e');
      rethrow;
    }
  }

  /// Check analysis status
  Future<AnalysisStatus> getAnalysisStatus(String companyName) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/jd-analysis/$companyName/status'),
        headers: _getHeaders(),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return AnalysisStatus.fromJson(data['data']);
      } else {
        throw JDAnalysisException(
          'Failed to get analysis status: ${response.statusCode}',
          response.body,
        );
      }
    } catch (e) {
      debugPrint('Error getting analysis status: $e');
      rethrow;
    }
  }
}

/// Exception class for JD Analysis errors
class JDAnalysisException implements Exception {
  final String message;
  final String? details;

  JDAnalysisException(this.message, [this.details]);

  @override
  String toString() =>
      'JDAnalysisException: $message${details != null ? '\nDetails: $details' : ''}';
}

/// Main analysis result model
class JDAnalysisResult {
  final String companyName;
  final List<String> requiredKeywords;
  final List<String> preferredKeywords;
  final List<String> allKeywords;
  final int? experienceYears;
  final RequiredSkills requiredSkills;
  final PreferredSkills preferredSkills;
  final SkillSummary skillSummary;
  final String analysisTimestamp;
  final String aiModelUsed;
  final String processingStatus;
  final bool fromCache;

  JDAnalysisResult({
    required this.companyName,
    required this.requiredKeywords,
    required this.preferredKeywords,
    required this.allKeywords,
    this.experienceYears,
    required this.requiredSkills,
    required this.preferredSkills,
    required this.skillSummary,
    required this.analysisTimestamp,
    required this.aiModelUsed,
    required this.processingStatus,
    required this.fromCache,
  });

  factory JDAnalysisResult.fromJson(Map<String, dynamic> json) {
    return JDAnalysisResult(
      companyName: json['company_name'] ?? '',
      requiredKeywords: List<String>.from(json['required_keywords'] ?? []),
      preferredKeywords: List<String>.from(json['preferred_keywords'] ?? []),
      allKeywords: List<String>.from(json['all_keywords'] ?? []),
      experienceYears: json['experience_years'],
      requiredSkills: RequiredSkills.fromJson(json['required_skills'] ?? {}),
      preferredSkills: PreferredSkills.fromJson(json['preferred_skills'] ?? {}),
      skillSummary: SkillSummary.fromJson(json['skill_summary'] ?? {}),
      analysisTimestamp: json['analysis_timestamp'] ?? '',
      aiModelUsed: json['ai_model_used'] ?? '',
      processingStatus: json['processing_status'] ?? '',
      fromCache: json['from_cache'] ?? false,
    );
  }

  /// Get all technical skills (required + preferred)
  List<String> get allTechnicalSkills {
    final skills = <String>[];
    skills.addAll(requiredSkills.technical);
    skills.addAll(preferredSkills.technical);
    return skills.toSet().toList(); // Remove duplicates
  }

  /// Get all soft skills (required + preferred)
  List<String> get allSoftSkills {
    final skills = <String>[];
    skills.addAll(requiredSkills.softSkills);
    skills.addAll(preferredSkills.softSkills);
    return skills.toSet().toList(); // Remove duplicates
  }

  /// Get all experience requirements (required + preferred)
  List<String> get allExperienceRequirements {
    final requirements = <String>[];
    requirements.addAll(requiredSkills.experience);
    requirements.addAll(preferredSkills.experience);
    return requirements.toSet().toList(); // Remove duplicates
  }

  /// Get all domain knowledge (required + preferred)
  List<String> get allDomainKnowledge {
    final knowledge = <String>[];
    knowledge.addAll(requiredSkills.domainKnowledge);
    knowledge.addAll(preferredSkills.domainKnowledge);
    return knowledge.toSet().toList(); // Remove duplicates
  }
}

/// Required skills model
class RequiredSkills {
  final List<String> technical;
  final List<String> softSkills;
  final List<String> experience;
  final List<String> domainKnowledge;

  RequiredSkills({
    required this.technical,
    required this.softSkills,
    required this.experience,
    required this.domainKnowledge,
  });

  factory RequiredSkills.fromJson(Map<String, dynamic> json) {
    return RequiredSkills(
      technical: List<String>.from(json['technical'] ?? []),
      softSkills: List<String>.from(json['soft_skills'] ?? []),
      experience: List<String>.from(json['experience'] ?? []),
      domainKnowledge: List<String>.from(json['domain_knowledge'] ?? []),
    );
  }
}

/// Preferred skills model
class PreferredSkills {
  final List<String> technical;
  final List<String> softSkills;
  final List<String> experience;
  final List<String> domainKnowledge;

  PreferredSkills({
    required this.technical,
    required this.softSkills,
    required this.experience,
    required this.domainKnowledge,
  });

  factory PreferredSkills.fromJson(Map<String, dynamic> json) {
    return PreferredSkills(
      technical: List<String>.from(json['technical'] ?? []),
      softSkills: List<String>.from(json['soft_skills'] ?? []),
      experience: List<String>.from(json['experience'] ?? []),
      domainKnowledge: List<String>.from(json['domain_knowledge'] ?? []),
    );
  }
}

/// Skill summary model
class SkillSummary {
  final int totalRequired;
  final int totalPreferred;
  final int requiredTechnical;
  final int requiredSoftSkills;
  final int requiredExperience;
  final int requiredDomainKnowledge;
  final int preferredTechnical;
  final int preferredSoftSkills;
  final int preferredExperience;
  final int preferredDomainKnowledge;

  SkillSummary({
    required this.totalRequired,
    required this.totalPreferred,
    required this.requiredTechnical,
    required this.requiredSoftSkills,
    required this.requiredExperience,
    required this.requiredDomainKnowledge,
    required this.preferredTechnical,
    required this.preferredSoftSkills,
    required this.preferredExperience,
    required this.preferredDomainKnowledge,
  });

  factory SkillSummary.fromJson(Map<String, dynamic> json) {
    return SkillSummary(
      totalRequired: json['total_required'] ?? 0,
      totalPreferred: json['total_preferred'] ?? 0,
      requiredTechnical: json['required_technical'] ?? 0,
      requiredSoftSkills: json['required_soft_skills'] ?? 0,
      requiredExperience: json['required_experience'] ?? 0,
      requiredDomainKnowledge: json['required_domain_knowledge'] ?? 0,
      preferredTechnical: json['preferred_technical'] ?? 0,
      preferredSoftSkills: json['preferred_soft_skills'] ?? 0,
      preferredExperience: json['preferred_experience'] ?? 0,
      preferredDomainKnowledge: json['preferred_domain_knowledge'] ?? 0,
    );
  }
}

/// Categorized skills model
class CategorizedSkills {
  final RequiredSkills required;
  final PreferredSkills preferred;
  final SkillSummary skillSummary;
  final int? experienceYears;

  CategorizedSkills({
    required this.required,
    required this.preferred,
    required this.skillSummary,
    this.experienceYears,
  });

  factory CategorizedSkills.fromJson(Map<String, dynamic> json) {
    return CategorizedSkills(
      required:
          RequiredSkills.fromJson(json['categorized_skills']['required'] ?? {}),
      preferred: PreferredSkills.fromJson(
          json['categorized_skills']['preferred'] ?? {}),
      skillSummary: SkillSummary.fromJson(json['skill_summary'] ?? {}),
      experienceYears: json['experience_years'],
    );
  }
}

/// Analysis status model
class AnalysisStatus {
  final String companyName;
  final bool analysisExists;
  final bool jdFileExists;
  final bool canAnalyze;
  final bool needsAnalysis;
  final String? analysisTimestamp;
  final String? aiModelUsed;
  final Map<String, int>? keywordCounts;

  AnalysisStatus({
    required this.companyName,
    required this.analysisExists,
    required this.jdFileExists,
    required this.canAnalyze,
    required this.needsAnalysis,
    this.analysisTimestamp,
    this.aiModelUsed,
    this.keywordCounts,
  });

  factory AnalysisStatus.fromJson(Map<String, dynamic> json) {
    return AnalysisStatus(
      companyName: json['company_name'] ?? '',
      analysisExists: json['analysis_exists'] ?? false,
      jdFileExists: json['jd_file_exists'] ?? false,
      canAnalyze: json['can_analyze'] ?? false,
      needsAnalysis: json['needs_analysis'] ?? false,
      analysisTimestamp: json['analysis_timestamp'],
      aiModelUsed: json['ai_model_used'],
      keywordCounts: json['keyword_counts'] != null
          ? Map<String, int>.from(json['keyword_counts'])
          : null,
    );
  }
}
