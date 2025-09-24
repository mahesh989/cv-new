import 'package:flutter/foundation.dart';

class JobParser {
  static Map<String, String?> parseJobDetails(String jobDescription) {
    try {
      debugPrint('🔍 [JOB_PARSER] Parsing job details');

      // Extract company name
      String? companyName = _extractCompanyName(jobDescription);
      debugPrint('👔 [JOB_PARSER] Company name: $companyName');

      // Extract job title
      String? jobTitle = _extractJobTitle(jobDescription);
      debugPrint('📋 [JOB_PARSER] Job title: $jobTitle');

      // Extract location
      String? location = _extractLocation(jobDescription);
      debugPrint('📍 [JOB_PARSER] Location: $location');

      // Extract contact details
      final contactDetails = _extractContactDetails(jobDescription);
      debugPrint('📞 [JOB_PARSER] Contact details: $contactDetails');

      // Extract job URL (if present)
      String? jobUrl = _extractJobUrl(jobDescription);
      debugPrint('🔗 [JOB_PARSER] Job URL: $jobUrl');

      return {
        'company_name': companyName,
        'job_title': jobTitle,
        'location': location,
        'phone_number': contactDetails['phone'],
        'email': contactDetails['email'],
        'job_url': jobUrl,
      };
    } catch (e) {
      debugPrint('❌ [JOB_PARSER] Error parsing job details: $e');
      rethrow;
    }
  }

  static String? _extractCompanyName(String text) {
    try {
      // Company name is usually at the start after the job title
      final lines = text.split('\n');
      for (final line in lines.take(5)) {
        if (line.trim().isNotEmpty && 
            !line.toLowerCase().contains('job title') &&
            !_isCommonJobTitle(line)) {
          return line.trim();
        }
      }
      return null;
    } catch (e) {
      debugPrint('⚠️ [JOB_PARSER] Error extracting company name: $e');
      return null;
    }
  }

  static String? _extractJobTitle(String text) {
    try {
      // Job title is usually the first line or line containing "job title"
      final lines = text.split('\n');
      if (lines.isNotEmpty) {
        final firstLine = lines[0].trim();
        if (_isCommonJobTitle(firstLine)) {
          return firstLine;
        }
      }

      // Look for explicit "job title" or "position" indicators
      for (final line in lines.take(10)) {
        if (line.toLowerCase().contains('job title:') ||
            line.toLowerCase().contains('position:')) {
          final parts = line.split(':');
          if (parts.length > 1) {
            return parts[1].trim();
          }
        }
      }

      return null;
    } catch (e) {
      debugPrint('⚠️ [JOB_PARSER] Error extracting job title: $e');
      return null;
    }
  }

  static String? _extractLocation(String text) {
    try {
      // Look for location information
      final locationIndicators = [
        'location:', 
        'location :', 
        'based in', 
        'work location',
        '(hybrid)',
        '(remote)',
        '(onsite)'
      ];

      final lines = text.split('\n');
      for (final line in lines) {
        final lowerLine = line.toLowerCase();
        for (final indicator in locationIndicators) {
          if (lowerLine.contains(indicator)) {
            // Extract location, handling different formats
            if (line.contains(':')) {
              final parts = line.split(':');
              return parts.length > 1 ? parts[1].trim() : line.trim();
            } else {
              return line.trim();
            }
          }
        }
      }

      return null;
    } catch (e) {
      debugPrint('⚠️ [JOB_PARSER] Error extracting location: $e');
      return null;
    }
  }

  static Map<String, String?> _extractContactDetails(String text) {
    try {
      String? email;
      String? phone;

      // Extract email using regex
      final emailRegex = RegExp(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b');
      final emailMatch = emailRegex.firstMatch(text);
      if (emailMatch != null) {
        email = emailMatch.group(0);
      }

      // Extract phone number using regex
      final phoneRegex = RegExp(r'\b\d{8,12}\b|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b');
      final phoneMatch = phoneRegex.firstMatch(text);
      if (phoneMatch != null) {
        phone = phoneMatch.group(0);
      }

      return {
        'email': email,
        'phone': phone,
      };
    } catch (e) {
      debugPrint('⚠️ [JOB_PARSER] Error extracting contact details: $e');
      return {
        'email': null,
        'phone': null,
      };
    }
  }

  static String? _extractJobUrl(String text) {
    try {
      // Look for URLs
      final urlRegex = RegExp(r'https?://[^\s<>"]+|www\.[^\s<>"]+');
      final match = urlRegex.firstMatch(text);
      return match?.group(0);
    } catch (e) {
      debugPrint('⚠️ [JOB_PARSER] Error extracting job URL: $e');
      return null;
    }
  }

  static bool _isCommonJobTitle(String text) {
    final commonTitles = [
      'developer',
      'engineer',
      'analyst',
      'manager',
      'designer',
      'consultant',
      'specialist',
      'coordinator',
      'administrator',
      'director',
      'lead',
      'architect',
    ];

    final normalized = text.toLowerCase().trim();
    return commonTitles.any((title) => normalized.contains(title));
  }
}