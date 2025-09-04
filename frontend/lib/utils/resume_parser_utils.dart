import 'dart:convert';

class ResumeParserUtils {
  /// Post-processes experience bullets to fix common parsing issues
  static List<String> fixExperienceBullets(List<dynamic> rawBullets) {
    if (rawBullets.isEmpty) return [];
    
    List<String> fixedBullets = [];
    String? currentBullet;
    
    for (int i = 0; i < rawBullets.length; i++) {
      final item = rawBullets[i];
      final itemText = item.toString().trim();
      
      if (itemText.isEmpty) continue;
      
      // Check if this looks like a bullet continuation
      if (currentBullet != null && _isBulletContinuation(itemText)) {
        // Merge with previous bullet
        currentBullet = '$currentBullet $itemText';
      } else {
        // Save previous bullet if exists
        if (currentBullet != null) {
          fixedBullets.add(currentBullet);
        }
        
        // Start new bullet
        currentBullet = _cleanBulletText(itemText);
      }
    }
    
    // Add the last bullet
    if (currentBullet != null) {
      fixedBullets.add(currentBullet);
    }
    
    return fixedBullets;
  }
  
  /// Checks if a text fragment is likely a continuation of a bullet point
  static bool _isBulletContinuation(String text) {
    // Remove common bullet indicators
    final cleanText = text.replaceAll(RegExp(r'^[•\-\*▪▫]\s*'), '').trim();
    
    // Check if it starts with lowercase (likely continuation)
    if (cleanText.isNotEmpty && cleanText[0] == cleanText[0].toLowerCase()) {
      return true;
    }
    
    // Check if it's a short phrase without proper sentence structure
    if (cleanText.length < 50 && !cleanText.contains('.') && 
        !RegExp(r'\b\d{4}\b').hasMatch(cleanText)) {
      return true;
    }
    
    // Check for common continuation patterns
    if (cleanText.startsWith(RegExp(r'^(and|or|by|to|with|through|using|for|in|on|at|from)\s+', caseSensitive: false))) {
      return true;
    }
    
    return false;
  }
  
  /// Cleans bullet text by removing duplicate indicators and formatting
  static String _cleanBulletText(String text) {
    // Remove bullet indicators
    String cleaned = text.replaceAll(RegExp(r'^[•\-\*▪▫]\s*'), '').trim();
    
    // Remove duplicate spaces
    cleaned = cleaned.replaceAll(RegExp(r'\s+'), ' ');
    
    return cleaned;
  }
  
  /// Validates and cleans experience data
  static Map<String, dynamic> validateExperienceEntry(Map<String, dynamic> exp) {
    final Map<String, dynamic> cleaned = Map.from(exp);
    
    // Clean bullets
    if (cleaned['bullets'] is List) {
      cleaned['bullets'] = fixExperienceBullets(cleaned['bullets']);
    }
    
    // Validate job title and company
    String title = cleaned['title']?.toString().trim() ?? '';
    String company = cleaned['company']?.toString().trim() ?? '';
    String location = cleaned['location']?.toString().trim() ?? '';
    String date = cleaned['date']?.toString().trim() ?? '';
    
    // Check if title contains date pattern (misclassified)
    if (title.isNotEmpty && RegExp(r'\b\d{4}\b').hasMatch(title)) {
      // Extract date from title
      final dateMatch = RegExp(r'(\w{3}\s+\d{4}.*?\d{4}|\d{4}\s*[-–—]\s*\d{4}|\d{4}\s*[-–—]\s*Present)', caseSensitive: false).firstMatch(title);
      if (dateMatch != null) {
        date = dateMatch.group(1) ?? date;
        title = title.replaceAll(dateMatch.group(0)!, '').trim();
      }
    }
    
    // Check if company contains location info
    if (company.isNotEmpty && company.contains(',')) {
      final parts = company.split(',');
      if (parts.length >= 2) {
        company = parts[0].trim();
        if (location.isEmpty) {
          location = parts.sublist(1).join(', ').trim();
        }
      }
    }
    
    cleaned['title'] = title;
    cleaned['company'] = company;
    cleaned['location'] = location;
    cleaned['date'] = date;
    
    return cleaned;
  }
  
  /// Validates and cleans project data
  static Map<String, dynamic> validateProjectEntry(Map<String, dynamic> proj) {
    final Map<String, dynamic> cleaned = Map.from(proj);
    
    // Clean project title
    String title = cleaned['title']?.toString().trim() ?? '';
    String description = cleaned['description']?.toString().trim() ?? '';
    
    // Clean technologies
    List<String> technologies = [];
    if (cleaned['technologies'] is List) {
      technologies = (cleaned['technologies'] as List)
          .map((tech) => _cleanText(tech.toString()))
          .where((tech) => tech.isNotEmpty)
          .toList();
    } else if (cleaned['technologies'] is String) {
      final techString = cleaned['technologies'].toString().trim();
      if (techString.isNotEmpty) {
        // Split by common separators
        technologies = techString
            .split(RegExp(r'[,;|]'))
            .map((tech) => _cleanText(tech))
            .where((tech) => tech.isNotEmpty)
            .toList();
      }
    }
    
    cleaned['title'] = title;
    cleaned['description'] = description;
    cleaned['technologies'] = technologies;
    
    return cleaned;
  }
  
  /// Post-processes entire resume data to fix parsing issues while preserving original structure
  static Map<String, dynamic> postProcessResumeData(Map<String, dynamic> rawData) {
    final Map<String, dynamic> processed = Map.from(rawData);
    
    // Fix experience section
    if (processed['experience'] is List) {
      final List<dynamic> rawExperience = processed['experience'];
      final List<Map<String, dynamic>> fixedExperience = [];
      
      for (final exp in rawExperience) {
        if (exp is Map<String, dynamic>) {
          final validatedExp = validateExperienceEntry(exp);
          
          // Only add if it has meaningful content
          if (validatedExp['title'].toString().trim().isNotEmpty ||
              validatedExp['company'].toString().trim().isNotEmpty) {
            fixedExperience.add(validatedExp);
          }
        }
      }
      
      processed['experience'] = fixedExperience;
    }
    
    // Fix projects section
    if (processed['projects'] is List) {
      final List<dynamic> rawProjects = processed['projects'];
      final List<Map<String, dynamic>> fixedProjects = [];
      
      for (final proj in rawProjects) {
        if (proj is Map<String, dynamic>) {
          final validatedProj = validateProjectEntry(proj);
          
          // Only add if it has meaningful content
          if (validatedProj['title'].toString().trim().isNotEmpty) {
            fixedProjects.add(validatedProj);
          }
        }
      }
      
      processed['projects'] = fixedProjects;
    }
    
    // Clean summary
    if (processed['summary'] is String) {
      processed['summary'] = _cleanText(processed['summary']);
    }
    
    // Process skills section - convert to structured format if it's a simple list
    if (processed['skills'] != null) {
      if (processed['skills'] is Map<String, dynamic>) {
        // Skills already have structured format with title and content
        final skillsMap = processed['skills'] as Map<String, dynamic>;
        if (skillsMap.containsKey('content') && skillsMap['content'] is List) {
          skillsMap['content'] = (skillsMap['content'] as List)
              .map((skill) => _cleanText(skill.toString()))
              .where((skill) => skill.isNotEmpty)
              .toList();
        }
      } else if (processed['skills'] is List) {
        // Convert simple list to structured format with "Technical Skills" as default title
        final skillsList = (processed['skills'] as List)
            .map((skill) => _cleanText(skill.toString()))
            .where((skill) => skill.isNotEmpty)
            .toList();
        
        // Convert to structured format for consistency
        processed['skills'] = {
          'title': 'Technical Skills',
          'content': skillsList,
          'type': 'bullets',
        };
      }
    }
    
    // Process other sections while preserving their original structure
    final knownKeys = {'contact_info', 'experience', 'education', 'skills', 'summary', 'certifications', 'projects', 'languages'};
    for (final key in processed.keys.toList()) {
      if (!knownKeys.contains(key) && processed[key] != null) {
        processed[key] = _processDynamicSection(processed[key], key);
      }
    }
    
    // Clean certifications
    if (processed['certifications'] is List) {
      processed['certifications'] = (processed['certifications'] as List)
          .map((cert) => _cleanText(cert.toString()))
          .where((cert) => cert.isNotEmpty)
          .toList();
    }
    
    // Clean languages
    if (processed['languages'] is List) {
      processed['languages'] = (processed['languages'] as List)
          .map((lang) => _cleanText(lang.toString()))
          .where((lang) => lang.isNotEmpty)
          .toList();
    }
    
    return processed;
  }
  
  /// Cleans text by removing excessive whitespace and formatting issues
  static String _cleanText(String text) {
    return text.trim()
        .replaceAll(RegExp(r'\s+'), ' ')
        .replaceAll(RegExp(r'^\s*[-•*]\s*'), '')
        .trim();
  }
  
  /// Validates if a string looks like a job title with date
  static bool _isJobTitleWithDate(String text) {
    return RegExp(r'\b\d{4}\b').hasMatch(text) &&
           (RegExp(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', caseSensitive: false).hasMatch(text) ||
            RegExp(r'\d{4}\s*[-–—]\s*(Present|\d{4})').hasMatch(text));
  }
  
  /// Detects if text is likely a bullet continuation
  static bool looksLikeBulletTail(String text) {
    final cleanText = text.trim();
    
    // Check length (short phrases are likely tails)
    if (cleanText.length < 80) {
      // Check if starts with lowercase
      if (cleanText.isNotEmpty && cleanText[0] == cleanText[0].toLowerCase()) {
        return true;
      }
      
      // Check for continuation words
      if (cleanText.startsWith(RegExp(r'^(and|or|by|to|with|through|using|for|in|on|at|from|efficiency|processes|satisfaction)', caseSensitive: false))) {
        return true;
      }
      
      // Check if it doesn't contain a date (real job titles usually have dates)
      if (!_isJobTitleWithDate(cleanText)) {
        return true;
      }
    }
    
    return false;
  }
  
  /// Processes dynamic sections while preserving their original structure
  static dynamic _processDynamicSection(dynamic sectionData, String sectionKey) {
    if (sectionData is Map<String, dynamic>) {
      // Already structured - just clean the content
      final Map<String, dynamic> cleanedSection = Map.from(sectionData);
      
      if (cleanedSection.containsKey('content') && cleanedSection['content'] is List) {
        cleanedSection['content'] = (cleanedSection['content'] as List)
            .map((item) => _cleanText(item.toString()))
            .where((item) => item.isNotEmpty)
            .toList();
      }
      
      return cleanedSection;
    } else if (sectionData is List) {
      // Convert list to structured format
      final cleanedList = (sectionData as List)
          .map((item) => _cleanText(item.toString()))
          .where((item) => item.isNotEmpty)
          .toList();
      
      // Return as structured format
      return {
        'title': _formatSectionTitle(sectionKey),
        'content': cleanedList,
        'type': 'bullets',
      };
    }
    
    return sectionData;
  }
  
  /// Formats section keys into proper titles
  static String _formatSectionTitle(String key) {
    // Handle common section key variations
    final titleMap = {
      'technical_skills': 'Technical Skills',
      'core_competencies': 'Core Competencies',
      'key_skills': 'Key Skills',
      'professional_skills': 'Professional Skills',
      'soft_skills': 'Soft Skills',
      'achievements': 'Achievements',
      'awards': 'Awards',
      'publications': 'Publications',
      'volunteer_experience': 'Volunteer Experience',
      'additional_information': 'Additional Information',
    };
    
    if (titleMap.containsKey(key.toLowerCase())) {
      return titleMap[key.toLowerCase()]!;
    }
    
    // Default formatting
    return key.split('_')
        .map((word) => word[0].toUpperCase() + word.substring(1))
        .join(' ');
  }
}
