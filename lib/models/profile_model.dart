/// User Profile Model
/// 
/// Represents user profile data stored in user/{email}/profile.json

class UserProfile {
  final String userEmail;
  final String fullName;
  final String email;
  final String phone;
  final String location;
  final String? linkedinUrl;
  final String? githubUrl;
  final String? portfolioUrl;
  final String? websiteUrl;
  final DateTime createdAt;
  final DateTime updatedAt;

  UserProfile({
    required this.userEmail,
    required this.fullName,
    required this.email,
    required this.phone,
    required this.location,
    this.linkedinUrl,
    this.githubUrl,
    this.portfolioUrl,
    this.websiteUrl,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      userEmail: json['user_email'] ?? '',
      fullName: json['full_name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      location: json['location'] ?? '',
      linkedinUrl: json['linkedin_url'],
      githubUrl: json['github_url'],
      portfolioUrl: json['portfolio_url'],
      websiteUrl: json['website_url'],
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updated_at'] ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_email': userEmail,
      'full_name': fullName,
      'email': email,
      'phone': phone,
      'location': location,
      'linkedin_url': linkedinUrl,
      'github_url': githubUrl,
      'portfolio_url': portfolioUrl,
      'website_url': websiteUrl,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  /// Check if profile has all required fields
  bool get isComplete {
    return userEmail.isNotEmpty &&
           fullName.isNotEmpty &&
           email.isNotEmpty &&
           phone.isNotEmpty &&
           location.isNotEmpty;
  }

  /// Get list of missing required fields
  List<String> get missingFields {
    List<String> missing = [];
    if (userEmail.isEmpty) missing.add('user_email');
    if (fullName.isEmpty) missing.add('full_name');
    if (email.isEmpty) missing.add('email');
    if (phone.isEmpty) missing.add('phone');
    if (location.isEmpty) missing.add('location');
    return missing;
  }

  /// Get profile data formatted for CV generation
  Map<String, dynamic> get cvHeaderData {
    return {
      'full_name': fullName,
      'email': email,
      'phone': phone,
      'location': location,
      'linkedin_url': linkedinUrl,
      'github_url': githubUrl,
      'portfolio_url': portfolioUrl,
      'website_url': websiteUrl,
    };
  }

  /// Get list of clickable links for CV
  List<Map<String, String>> get clickableLinks {
    List<Map<String, String>> links = [];
    
    if (linkedinUrl != null && linkedinUrl!.isNotEmpty) {
      links.add({
        'text': 'LinkedIn',
        'url': linkedinUrl!,
        'type': 'linkedin',
      });
    }
    
    if (githubUrl != null && githubUrl!.isNotEmpty) {
      links.add({
        'text': 'GitHub',
        'url': githubUrl!,
        'type': 'github',
      });
    }
    
    if (portfolioUrl != null && portfolioUrl!.isNotEmpty) {
      links.add({
        'text': 'Portfolio',
        'url': portfolioUrl!,
        'type': 'portfolio',
      });
    }
    
    if (websiteUrl != null && websiteUrl!.isNotEmpty) {
      links.add({
        'text': 'Website',
        'url': websiteUrl!,
        'type': 'website',
      });
    }
    
    return links;
  }

  UserProfile copyWith({
    String? userEmail,
    String? fullName,
    String? email,
    String? phone,
    String? location,
    String? linkedinUrl,
    String? githubUrl,
    String? portfolioUrl,
    String? websiteUrl,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserProfile(
      userEmail: userEmail ?? this.userEmail,
      fullName: fullName ?? this.fullName,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      location: location ?? this.location,
      linkedinUrl: linkedinUrl ?? this.linkedinUrl,
      githubUrl: githubUrl ?? this.githubUrl,
      portfolioUrl: portfolioUrl ?? this.portfolioUrl,
      websiteUrl: websiteUrl ?? this.websiteUrl,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

class ProfileResponse {
  final bool success;
  final String message;
  final UserProfile? profile;
  final List<String>? missingFields;

  ProfileResponse({
    required this.success,
    required this.message,
    this.profile,
    this.missingFields,
  });

  factory ProfileResponse.fromJson(Map<String, dynamic> json) {
    return ProfileResponse(
      success: json['success'] ?? false,
      message: json['message'] ?? '',
      profile: json['profile'] != null ? UserProfile.fromJson(json['profile']) : null,
      missingFields: json['missing_fields'] != null 
          ? List<String>.from(json['missing_fields']) 
          : null,
    );
  }
}
