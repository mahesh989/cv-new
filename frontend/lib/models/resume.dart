class Resume {
  final ContactInfo contact;
  final List<Experience> experience;
  final List<Education> education;
  final List<String> skills;
  final String summary;
  final List<String> certifications;
  final List<Project> projects;
  final List<String> languages;
  final Map<String, ResumeSection> dynamicSections;

  Resume({
    required this.contact,
    required this.experience,
    required this.education,
    required this.skills,
    required this.summary,
    required this.certifications,
    required this.projects,
    required this.languages,
    this.dynamicSections = const {},
  });

  factory Resume.fromJson(Map<String, dynamic> json) {
    // Extract known sections
    final Map<String, ResumeSection> dynamicSections = {};

    // Check for skills section with custom title and structure
    if (json.containsKey('skills')) {
      final skillsData = json['skills'];
      if (skillsData is Map<String, dynamic>) {
        // New structured format
        dynamicSections['skills'] = ResumeSection(
          title: skillsData['section_title'] ?? 'Skills',
          content: List<dynamic>.from(skillsData['content'] ?? []),
          type: skillsData['format'] ?? 'bullets',
        );
      }
    }

    // Check for other dynamic sections
    final knownKeys = {
      'contact_info',
      'experience',
      'education',
      'skills',
      'summary',
      'certifications',
      'projects',
      'languages'
    };
    for (final key in json.keys) {
      if (!knownKeys.contains(key) && json[key] != null) {
        if (json[key] is Map<String, dynamic>) {
          dynamicSections[key] =
              ResumeSection.fromJson(json[key] as Map<String, dynamic>);
        } else if (json[key] is List) {
          dynamicSections[key] = ResumeSection(
            title: _formatSectionTitle(key),
            content: json[key] as List<dynamic>,
            type: 'list',
          );
        }
      }
    }

    return Resume(
      contact: ContactInfo.fromJson(json['contact_info'] ?? {}),
      experience: (json['experience'] as List? ?? [])
          .map((e) => Experience.fromJson(e))
          .toList(),
      education: (json['education'] as List? ?? [])
          .map((e) => Education.fromJson(e))
          .toList(),
      skills: _extractSkillsList(json['skills']),
      summary: json['summary'] ?? '',
      certifications: List<String>.from(json['certifications'] ?? []),
      projects: (json['projects'] as List? ?? [])
          .map((e) => Project.fromJson(e))
          .toList(),
      languages: List<String>.from(json['languages'] ?? []),
      dynamicSections: dynamicSections,
    );
  }

  static List<String> _extractSkillsList(dynamic skillsData) {
    if (skillsData is List) {
      // Old format - list of strings
      return List<String>.from(skillsData);
    } else if (skillsData is Map<String, dynamic>) {
      // New format - structured object with content array
      final content = skillsData['content'];
      if (content is List) {
        return List<String>.from(content);
      }
    }
    return [];
  }

  static String _formatSectionTitle(String key) {
    return key
        .split('_')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }
}

class ContactInfo {
  final String name, email, phone, location;
  final List<String> links;

  ContactInfo({
    required this.name,
    required this.email,
    required this.phone,
    required this.location,
    required this.links,
  });

  factory ContactInfo.fromJson(Map<String, dynamic> json) => ContactInfo(
        name: json['name'] ?? '',
        email: json['email'] ?? '',
        phone: json['phone'] ?? '',
        location: json['location'] ?? '',
        links: List<String>.from(json['links'] ?? []),
      );
}

class Experience {
  final String company, location, title, date;
  final List<String> bullets;

  Experience({
    required this.company,
    required this.location,
    required this.title,
    required this.date,
    required this.bullets,
  });

  factory Experience.fromJson(Map<String, dynamic> json) => Experience(
        company: json['company'] ?? '',
        location: json['location'] ?? '',
        title: json['title'] ?? '',
        date: json['date'] ?? '',
        bullets: List<String>.from(json['bullets'] ?? []),
      );
}

class Education {
  final String degree, institution, date;

  Education({
    required this.degree,
    required this.institution,
    required this.date,
  });

  factory Education.fromJson(Map<String, dynamic> json) => Education(
        degree: json['degree'] ?? '',
        institution: json['institution'] ?? '',
        date: json['date'] ?? '',
      );
}

class Project {
  final String title, description, context, date;
  final List<String> technologies;
  final List<String> bullets;

  Project({
    required this.title,
    required this.description,
    required this.context,
    required this.date,
    required this.technologies,
    required this.bullets,
  });

  factory Project.fromJson(Map<String, dynamic> json) => Project(
        title: json['title'] ?? '',
        description: json['description'] ?? '',
        context: json['context'] ?? '',
        date: json['date'] ?? '',
        technologies: List<String>.from(json['technologies'] ?? []),
        bullets: List<String>.from(json['bullets'] ?? []),
      );
}

class ResumeSection {
  final String title;
  final List<dynamic> content;
  final String type; // 'list', 'bullets', 'text', 'structured'
  final String? description;

  ResumeSection({
    required this.title,
    required this.content,
    required this.type,
    this.description,
  });

  factory ResumeSection.fromJson(Map<String, dynamic> json) => ResumeSection(
        title: json['title'] ?? '',
        content: List<dynamic>.from(json['content'] ?? []),
        type: json['type'] ?? 'list',
        description: json['description'],
      );

  Map<String, dynamic> toJson() => {
        'title': title,
        'content': content,
        'type': type,
        if (description != null) 'description': description,
      };
}
