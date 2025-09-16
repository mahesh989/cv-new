import 'package:flutter/foundation.dart';
import 'dart:convert';
import 'api_service.dart';

/// CV Tailoring Service for generating optimized CVs
class CVTailoringService {
  /// Tailor a CV based on job recommendations
  static Future<CVTailoringResult> tailorCV({
    required Map<String, dynamic> originalCV,
    required Map<String, dynamic> recommendations,
    String? customInstructions,
    int targetATSScore = 85,
    String? companyFolder,
  }) async {
    try {
      debugPrint('🎯 Starting CV tailoring process...');
      
      final requestBody = {
        'original_cv': originalCV,
        'recommendations': recommendations,
        'custom_instructions': customInstructions,
        'target_ats_score': targetATSScore,
        'company_folder': companyFolder,
      };

      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/tailor',
        method: 'POST',
        body: requestBody,
      );

      debugPrint('✅ CV tailoring completed successfully');
      return CVTailoringResult.fromJson(response);
    } catch (e) {
      debugPrint('❌ CV tailoring failed: $e');
      return CVTailoringResult.error(e.toString());
    }
  }

  /// Validate CV structure and content
  static Future<CVValidationResult> validateCV(
      Map<String, dynamic> cvData) async {
    try {
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/validate-cv',
        method: 'POST',
        body: cvData,
      );

      return CVValidationResult.fromJson(response);
    } catch (e) {
      return CVValidationResult.error(e.toString());
    }
  }

  /// Get available companies with recommendations
  static Future<List<CompanyRecommendation>> getAvailableCompanies({
    required String dataFolder,
  }) async {
    try {
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/companies?data_folder=$dataFolder',
        method: 'GET',
      );

      final List<dynamic> companiesJson = response['companies'] ?? [];
      return companiesJson
          .map((json) => CompanyRecommendation.fromJson(json))
          .toList();
    } catch (e) {
      debugPrint('❌ Failed to get available companies: $e');
      return [];
    }
  }

  /// Get recommendation for a specific company
  static Future<Map<String, dynamic>?> getCompanyRecommendation({
    required String companyName,
    required String dataFolder,
  }) async {
    try {
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/recommendations/$companyName?data_folder=$dataFolder',
        method: 'GET',
      );

      return response;
    } catch (e) {
      debugPrint('❌ Failed to get company recommendation: $e');
      return null;
    }
  }

  /// Batch tailor CV for multiple companies
  static Future<BatchTailoringResult> batchTailorCV({
    required Map<String, dynamic> originalCV,
    required List<String> companyNames,
    required String dataFolder,
  }) async {
    try {
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/batch-tailor?data_folder=$dataFolder',
        method: 'POST',
        body: {
          'original_cv': originalCV,
          'company_names': companyNames,
        },
      );

      return BatchTailoringResult.fromJson(response);
    } catch (e) {
      return BatchTailoringResult.error(e.toString());
    }
  }

  /// Get batch tailoring status
  static Future<ProcessingStatus> getBatchStatus(String taskId) async {
    try {
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/batch-status/$taskId',
        method: 'GET',
      );

      return ProcessingStatus.fromJson(response);
    } catch (e) {
      return ProcessingStatus.error(e.toString());
    }
  }

  /// Tailor CV using real data for a specific company
  static Future<CVTailoringResult> tailorCVWithRealData({
    required String company,
    String? customInstructions,
    int targetATSScore = 85,
  }) async {
    try {
      debugPrint('🎯 Starting real CV tailoring for $company...');
      
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/tailor-real',
        method: 'POST',
        body: {
          'company': company,
          'custom_instructions': customInstructions,
          'target_ats_score': targetATSScore,
        },
      );

      debugPrint('✅ Real CV tailoring completed successfully');
      return CVTailoringResult.fromJson(response);
    } catch (e) {
      debugPrint('❌ Real CV tailoring failed: $e');
      return CVTailoringResult.error(e.toString());
    }
  }

  /// Get available companies with real recommendation data
  static Future<List<RealCompanyData>> getAvailableRealCompanies() async {
    try {
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/available-companies-real',
        method: 'GET',
      );

      final List<dynamic> companiesJson = response['companies'] ?? [];
      return companiesJson
          .map((json) => RealCompanyData.fromJson(json))
          .toList();
    } catch (e) {
      debugPrint('❌ Failed to get available real companies: $e');
      return [];
    }
  }

  /// Get CV optimization framework content
  static Future<String?> getFrameworkContent() async {
    try {
      final response = await APIService.makeAuthenticatedCall(
        endpoint: '/tailored-cv/framework',
        method: 'GET',
      );

      return response['framework_content'];
    } catch (e) {
      debugPrint('❌ Failed to get framework content: $e');
      return null;
    }
  }
}

/// CV Tailoring Result
class CVTailoringResult {
  final TailoredCV? tailoredCV;
  final Map<String, dynamic> processingSummary;
  final List<String> recommendationsApplied;
  final List<String>? warnings;
  final bool success;
  final String? errorMessage;

  CVTailoringResult({
    this.tailoredCV,
    required this.processingSummary,
    required this.recommendationsApplied,
    this.warnings,
    required this.success,
    this.errorMessage,
  });

  factory CVTailoringResult.fromJson(Map<String, dynamic> json) {
    return CVTailoringResult(
      tailoredCV: json['tailored_cv'] != null
          ? TailoredCV.fromJson(json['tailored_cv'])
          : null,
      processingSummary: json['processing_summary'] ?? {},
      recommendationsApplied: List<String>.from(json['recommendations_applied'] ?? []),
      warnings: json['warnings'] != null
          ? List<String>.from(json['warnings'])
          : null,
      success: json['success'] ?? false,
    );
  }

  factory CVTailoringResult.error(String errorMessage) {
    return CVTailoringResult(
      processingSummary: {'error': errorMessage},
      recommendationsApplied: [],
      success: false,
      errorMessage: errorMessage,
    );
  }
}

/// Tailored CV model
class TailoredCV {
  final ContactInfo contact;
  final List<Education> education;
  final List<ExperienceEntry> experience;
  final List<Project>? projects;
  final List<SkillCategory> skills;
  
  // Optimization metadata
  final String targetCompany;
  final String targetRole;
  final Map<String, dynamic> enhancements;
  final List<String> keywordsIntegrated;
  final int? estimatedATSScore;
  final String frameworkVersion;

  TailoredCV({
    required this.contact,
    required this.education,
    required this.experience,
    this.projects,
    required this.skills,
    required this.targetCompany,
    required this.targetRole,
    required this.enhancements,
    required this.keywordsIntegrated,
    this.estimatedATSScore,
    required this.frameworkVersion,
  });

  factory TailoredCV.fromJson(Map<String, dynamic> json) {
    return TailoredCV(
      contact: ContactInfo.fromJson(json['contact'] ?? {}),
      education: (json['education'] as List?)
              ?.map((e) => Education.fromJson(e))
              .toList() ??
          [],
      experience: (json['experience'] as List?)
              ?.map((e) => ExperienceEntry.fromJson(e))
              .toList() ??
          [],
      projects: (json['projects'] as List?)
          ?.map((p) => Project.fromJson(p))
          .toList(),
      skills: (json['skills'] as List?)
              ?.map((s) => SkillCategory.fromJson(s))
              .toList() ??
          [],
      targetCompany: json['target_company'] ?? '',
      targetRole: json['target_role'] ?? '',
      enhancements: json['enhancements_applied'] ?? {},
      keywordsIntegrated: List<String>.from(json['keywords_integrated'] ?? []),
      estimatedATSScore: json['estimated_ats_score'],
      frameworkVersion: json['framework_version'] ?? '1.0',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'contact': contact.toJson(),
      'education': education.map((e) => e.toJson()).toList(),
      'experience': experience.map((e) => e.toJson()).toList(),
      'projects': projects?.map((p) => p.toJson()).toList(),
      'skills': skills.map((s) => s.toJson()).toList(),
      'target_company': targetCompany,
      'target_role': targetRole,
      'enhancements_applied': enhancements,
      'keywords_integrated': keywordsIntegrated,
      'estimated_ats_score': estimatedATSScore,
      'framework_version': frameworkVersion,
    };
  }
}

/// Supporting data models
class ContactInfo {
  final String name;
  final String? phone;
  final String email;
  final String? linkedin;
  final String? location;

  ContactInfo({
    required this.name,
    this.phone,
    required this.email,
    this.linkedin,
    this.location,
  });

  factory ContactInfo.fromJson(Map<String, dynamic> json) {
    return ContactInfo(
      name: json['name'] ?? '',
      phone: json['phone'],
      email: json['email'] ?? '',
      linkedin: json['linkedin'],
      location: json['location'],
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'phone': phone,
        'email': email,
        'linkedin': linkedin,
        'location': location,
      };
}

class Education {
  final String institution;
  final String degree;
  final String? location;
  final String? graduationDate;
  final String? gpa;

  Education({
    required this.institution,
    required this.degree,
    this.location,
    this.graduationDate,
    this.gpa,
  });

  factory Education.fromJson(Map<String, dynamic> json) {
    return Education(
      institution: json['institution'] ?? '',
      degree: json['degree'] ?? '',
      location: json['location'],
      graduationDate: json['graduation_date'],
      gpa: json['gpa'],
    );
  }

  Map<String, dynamic> toJson() => {
        'institution': institution,
        'degree': degree,
        'location': location,
        'graduation_date': graduationDate,
        'gpa': gpa,
      };
}

class ExperienceEntry {
  final String company;
  final String title;
  final String? location;
  final String startDate;
  final String? endDate;
  final List<String> bullets;

  ExperienceEntry({
    required this.company,
    required this.title,
    this.location,
    required this.startDate,
    this.endDate,
    required this.bullets,
  });

  factory ExperienceEntry.fromJson(Map<String, dynamic> json) {
    return ExperienceEntry(
      company: json['company'] ?? '',
      title: json['title'] ?? '',
      location: json['location'],
      startDate: json['start_date'] ?? '',
      endDate: json['end_date'],
      bullets: List<String>.from(json['bullets'] ?? []),
    );
  }

  Map<String, dynamic> toJson() => {
        'company': company,
        'title': title,
        'location': location,
        'start_date': startDate,
        'end_date': endDate,
        'bullets': bullets,
      };
}

class Project {
  final String name;
  final String? context;
  final List<String>? technologies;
  final List<String> bullets;

  Project({
    required this.name,
    this.context,
    this.technologies,
    required this.bullets,
  });

  factory Project.fromJson(Map<String, dynamic> json) {
    return Project(
      name: json['name'] ?? '',
      context: json['context'],
      technologies: json['technologies'] != null
          ? List<String>.from(json['technologies'])
          : null,
      bullets: List<String>.from(json['bullets'] ?? []),
    );
  }

  Map<String, dynamic> toJson() => {
        'name': name,
        'context': context,
        'technologies': technologies,
        'bullets': bullets,
      };
}

class SkillCategory {
  final String category;
  final List<String> skills;

  SkillCategory({
    required this.category,
    required this.skills,
  });

  factory SkillCategory.fromJson(Map<String, dynamic> json) {
    return SkillCategory(
      category: json['category'] ?? '',
      skills: List<String>.from(json['skills'] ?? []),
    );
  }

  Map<String, dynamic> toJson() => {
        'category': category,
        'skills': skills,
      };
}

class CVValidationResult {
  final bool isValid;
  final List<String> errors;
  final List<String> warnings;
  final List<String> suggestions;
  final String? errorMessage;

  CVValidationResult({
    required this.isValid,
    required this.errors,
    required this.warnings,
    required this.suggestions,
    this.errorMessage,
  });

  factory CVValidationResult.fromJson(Map<String, dynamic> json) {
    return CVValidationResult(
      isValid: json['is_valid'] ?? false,
      errors: List<String>.from(json['errors'] ?? []),
      warnings: List<String>.from(json['warnings'] ?? []),
      suggestions: List<String>.from(json['suggestions'] ?? []),
    );
  }

  factory CVValidationResult.error(String errorMessage) {
    return CVValidationResult(
      isValid: false,
      errors: [],
      warnings: [],
      suggestions: [],
      errorMessage: errorMessage,
    );
  }
}

class CompanyRecommendation {
  final String company;
  final String jobTitle;
  final String filePath;
  final DateTime lastUpdated;

  CompanyRecommendation({
    required this.company,
    required this.jobTitle,
    required this.filePath,
    required this.lastUpdated,
  });

  factory CompanyRecommendation.fromJson(Map<String, dynamic> json) {
    return CompanyRecommendation(
      company: json['company'] ?? '',
      jobTitle: json['job_title'] ?? '',
      filePath: json['file_path'] ?? '',
      lastUpdated: DateTime.tryParse(json['last_updated'] ?? '') ?? DateTime.now(),
    );
  }
}

class BatchTailoringResult {
  final bool success;
  final String? taskId;
  final List<String> companies;
  final String message;
  final String? errorMessage;

  BatchTailoringResult({
    required this.success,
    this.taskId,
    required this.companies,
    required this.message,
    this.errorMessage,
  });

  factory BatchTailoringResult.fromJson(Map<String, dynamic> json) {
    return BatchTailoringResult(
      success: json['success'] ?? false,
      taskId: json['task_id'],
      companies: List<String>.from(json['companies'] ?? []),
      message: json['message'] ?? '',
    );
  }

  factory BatchTailoringResult.error(String errorMessage) {
    return BatchTailoringResult(
      success: false,
      companies: [],
      message: '',
      errorMessage: errorMessage,
    );
  }
}

class ProcessingStatus {
  final String status;
  final int progress;
  final String currentStep;
  final String? message;
  final String? errorMessage;

  ProcessingStatus({
    required this.status,
    required this.progress,
    required this.currentStep,
    this.message,
    this.errorMessage,
  });

  factory ProcessingStatus.fromJson(Map<String, dynamic> json) {
    return ProcessingStatus(
      status: json['status'] ?? '',
      progress: json['progress'] ?? 0,
      currentStep: json['current_step'] ?? '',
      message: json['message'],
    );
  }

  factory ProcessingStatus.error(String errorMessage) {
    return ProcessingStatus(
      status: 'error',
      progress: 0,
      currentStep: '',
      errorMessage: errorMessage,
    );
  }
}

class RealCompanyData {
  final String company;
  final String displayName;
  final String recommendationFile;
  final DateTime lastUpdated;

  RealCompanyData({
    required this.company,
    required this.displayName,
    required this.recommendationFile,
    required this.lastUpdated,
  });

  factory RealCompanyData.fromJson(Map<String, dynamic> json) {
    return RealCompanyData(
      company: json['company'] ?? '',
      displayName: json['display_name'] ?? '',
      recommendationFile: json['recommendation_file'] ?? '',
      lastUpdated: DateTime.tryParse(json['last_updated'] ?? '') ?? DateTime.now(),
    );
  }
}
