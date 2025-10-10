import '../models/skills_analysis_model.dart';

/// Utility class to extract structured skills from comprehensive analysis text
/// when the backend doesn't return properly structured cv_skills data
class SkillsExtractor {
  
  /// Extracts structured skills from comprehensive analysis text
  /// This is a fallback when cv_skills comes back as empty arrays
  static SkillsData extractFromComprehensiveAnalysis(String? comprehensiveAnalysis) {
    if (comprehensiveAnalysis == null || comprehensiveAnalysis.trim().isEmpty) {
      return SkillsData(
        technicalSkills: [],
        softSkills: [],
        domainKeywords: [],
      );
    }
    
    final List<String> technicalSkills = [];
    final List<String> softSkills = [];
    final List<String> domainKeywords = [];
    
    // Split the text into lines for processing
    final lines = comprehensiveAnalysis.split('\n');
    
    String? currentSection;
    
    for (final line in lines) {
      final trimmedLine = line.trim();
      
      // Skip empty lines
      if (trimmedLine.isEmpty) continue;
      
      // Detect section headers
      if (trimmedLine.toUpperCase().contains('TECHNICAL SKILLS')) {
        currentSection = 'technical';
        continue;
      } else if (trimmedLine.toUpperCase().contains('SOFT SKILLS')) {
        currentSection = 'soft';
        continue;
      } else if (trimmedLine.toUpperCase().contains('DOMAIN KEYWORDS')) {
        currentSection = 'domain';
        continue;
      }
      
      // Extract skills from bullet points
      if (trimmedLine.startsWith('-') && currentSection != null) {
        final skill = trimmedLine.substring(1).trim();
        if (skill.isNotEmpty) {
          switch (currentSection) {
            case 'technical':
              technicalSkills.add(skill);
              break;
            case 'soft':
              softSkills.add(skill);
              break;
            case 'domain':
              domainKeywords.add(skill);
              break;
          }
        }
      }
    }
    
    print('🔧 [SKILLS_EXTRACTOR] Extracted from comprehensive analysis:');
    print('   Technical Skills: ${technicalSkills.length} - ${technicalSkills.take(3).join(", ")}${technicalSkills.length > 3 ? "..." : ""}');
    print('   Soft Skills: ${softSkills.length} - ${softSkills.take(3).join(", ")}${softSkills.length > 3 ? "..." : ""}');
    print('   Domain Keywords: ${domainKeywords.length} - ${domainKeywords.take(3).join(", ")}${domainKeywords.length > 3 ? "..." : ""}');
    
    return SkillsData(
      technicalSkills: technicalSkills,
      softSkills: softSkills,
      domainKeywords: domainKeywords,
    );
  }
  
  /// Enhanced extraction that also handles comma-separated skills
  static SkillsData extractWithAdvancedParsing(String? comprehensiveAnalysis) {
    if (comprehensiveAnalysis == null || comprehensiveAnalysis.trim().isEmpty) {
      return SkillsData(
        technicalSkills: [],
        softSkills: [],
        domainKeywords: [],
      );
    }
    
    final List<String> technicalSkills = [];
    final List<String> softSkills = [];
    final List<String> domainKeywords = [];
    
    // Try the standard bullet-point extraction first
    final basicResult = extractFromComprehensiveAnalysis(comprehensiveAnalysis);
    technicalSkills.addAll(basicResult.technicalSkills);
    softSkills.addAll(basicResult.softSkills);
    domainKeywords.addAll(basicResult.domainKeywords);
    
    // If we didn't find much, try parsing comma-separated or space-separated lists
    if (technicalSkills.isEmpty && softSkills.isEmpty && domainKeywords.isEmpty) {
      // Look for patterns like "Skills: Python, SQL, Tableau"
      final skillPatterns = [
        RegExp(r'Skills?[:\-\s]+(.*?)(?:\n|$)', caseSensitive: false),
        RegExp(r'Technical[:\-\s]+(.*?)(?:\n|$)', caseSensitive: false),
        RegExp(r'Technologies?[:\-\s]+(.*?)(?:\n|$)', caseSensitive: false),
      ];
      
      for (final pattern in skillPatterns) {
        final matches = pattern.allMatches(comprehensiveAnalysis);
        for (final match in matches) {
          final skillsText = match.group(1);
          if (skillsText != null) {
            // Split by comma and clean up
            final skills = skillsText
                .split(',')
                .map((s) => s.trim())
                .where((s) => s.isNotEmpty)
                .toList();
            
            // Add to technical skills as default
            technicalSkills.addAll(skills);
          }
        }
      }
    }
    
    // Remove duplicates and clean up
    final cleanedTechnical = technicalSkills.toSet().toList();
    final cleanedSoft = softSkills.toSet().toList();
    final cleanedDomain = domainKeywords.toSet().toList();
    
    print('🔧 [SKILLS_EXTRACTOR] Advanced extraction completed:');
    print('   Technical Skills: ${cleanedTechnical.length}');
    print('   Soft Skills: ${cleanedSoft.length}');
    print('   Domain Keywords: ${cleanedDomain.length}');
    
    return SkillsData(
      technicalSkills: cleanedTechnical,
      softSkills: cleanedSoft,
      domainKeywords: cleanedDomain,
    );
  }
}