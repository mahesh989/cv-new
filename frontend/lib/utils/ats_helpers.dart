import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../models/ats_models.dart';

class ATSHelpers {
  static Color getScoreColor(int score) {
    if (score >= 80) return AppTheme.successGreen;
    if (score >= 60) return AppTheme.warningOrange;
    if (score >= 40) return AppTheme.primaryTeal;
    return AppTheme.primaryCosmic;
  }

  static String getScoreMessage(int score) {
    if (score >= 80) return 'Excellent! Your CV is highly optimized.';
    if (score >= 60) return 'Good score! Some improvements possible.';
    if (score >= 40) return 'Fair score. Consider optimizations.';
    return 'Needs improvement. Let\'s enhance your CV!';
  }

  static String getScoreGrade(int score) {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Work';
  }

  static Color getStepColor(WaterfallStepType type) {
    switch (type) {
      case WaterfallStepType.atsResult:
        return AppTheme.primaryCosmic;
      case WaterfallStepType.cvPreview:
        return AppTheme.primaryTeal;
      case WaterfallStepType.loading:
        return AppTheme.warningOrange;
      case WaterfallStepType.improvement:
        return AppTheme.successGreen;
    }
  }

  static IconData getStepIcon(WaterfallStepType type) {
    switch (type) {
      case WaterfallStepType.atsResult:
        return Icons.analytics;
      case WaterfallStepType.cvPreview:
        return Icons.description;
      case WaterfallStepType.loading:
        return Icons.hourglass_empty;
      case WaterfallStepType.improvement:
        return Icons.auto_fix_high;
    }
  }

  static String getStepTitle(WaterfallStepType type, int index) {
    switch (type) {
      case WaterfallStepType.atsResult:
        return index == 0
            ? 'Initial ATS Test Results'
            : 'ATS Test Results #${index + 1}';
      case WaterfallStepType.cvPreview:
        return 'CV Preview';
      case WaterfallStepType.loading:
        return 'Processing...';
      case WaterfallStepType.improvement:
        return 'CV Improvement';
    }
  }

  static String formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${timestamp.day}/${timestamp.month} ${timestamp.hour}:${timestamp.minute.toString().padLeft(2, '0')}';
    }
  }

  static Color getTimelineStepColor(String type) {
    switch (type) {
      case 'ats_result':
        return AppTheme.primaryCosmic;
      case 'cv_generation':
        return AppTheme.primaryTeal;
      default:
        return AppTheme.primaryCosmic;
    }
  }

  static IconData getTimelineStepIcon(String type) {
    switch (type) {
      case 'ats_result':
        return Icons.analytics;
      case 'cv_generation':
        return Icons.description;
      default:
        return Icons.info;
    }
  }

  static String getTimelineStepTitle(String type, int index) {
    switch (type) {
      case 'ats_result':
        return index == 0 ? 'Initial ATS Test Results' : 'ATS Test Results';
      case 'cv_generation':
        return 'CV Generated';
      default:
        return 'Step ${index + 1}';
    }
  }

  static String getCVCardActionText(Map<String, dynamic> cv) {
    final isOriginal = cv['isOriginal'] as bool;
    final status = cv['status'] as String;

    if (isOriginal) return 'Preview';
    if (status == 'best') return 'Download';
    return 'Preview';
  }

  static String getJobTitle(String jdText) {
    if (jdText.length > 100) {
      // Try to extract job title from the beginning of JD
      final lines = jdText.split('\n');
      for (String line in lines.take(3)) {
        if (line.trim().length > 10 && line.trim().length < 80) {
          return line.trim();
        }
      }
    }
    return jdText.length > 50 ? '${jdText.substring(0, 47)}...' : jdText;
  }
}
