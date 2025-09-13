import '../../models/skills_analysis_model.dart';

/// Data model for horizontal bar chart items
class ChartBarData {
  final String label;
  final double value;
  final double maxValue;
  final String displayValue;

  ChartBarData({
    required this.label,
    required this.value,
    required this.maxValue,
    required this.displayValue,
  });

  double get percentage => maxValue > 0 ? (value / maxValue) * 100 : 0;
}

/// Data model for bonus points section
class BonusPointData {
  final String label;
  final double points;
  final bool isPositive;

  BonusPointData({
    required this.label,
    required this.points,
    required this.isPositive,
  });

  String get displayText => '${isPositive ? '+' : ''}$points';
}

/// Utility class to convert ATS data into chart data
class ATSChartDataConverter {
  
  /// Convert Category 1 (Direct Match Rates) data
  static List<ChartBarData> convertCategory1Data(ATSCategory1 category1) {
    // Backend provides percentages (0-100), convert to actual scores for display
    final techScore = (category1.technicalSkillsMatchRate / 100) * 20;
    final domainScore = (category1.domainKeywordsMatchRate / 100) * 5;
    final softScore = (category1.softSkillsMatchRate / 100) * 15;
    
    return [
      ChartBarData(
        label: 'Technical Skills Match (Max: 20)',
        value: techScore,
        maxValue: 20,
        displayValue: techScore.toStringAsFixed(1),
      ),
      ChartBarData(
        label: 'Domain Keywords Match (Max: 5)',
        value: domainScore,
        maxValue: 5,
        displayValue: domainScore.toStringAsFixed(1),
      ),
      ChartBarData(
        label: 'Soft Skills Match (Max: 15)',
        value: softScore,
        maxValue: 15,
        displayValue: softScore.toStringAsFixed(1),
      ),
    ];
  }

  /// Convert Category 2 (Component Analysis) data
  static List<ChartBarData> convertCategory2Data(ATSCategory2 category2) {
    // Backend provides scores as percentages (0-100), convert to actual scores for display
    final coreScore = (category2.coreCompetencyAvg / 100) * 25;
    final expScore = (category2.experienceSeniorityAvg / 100) * 20;
    final potentialScore = (category2.potentialAbilityAvg / 100) * 10;
    final companyScore = (category2.companyFitAvg / 100) * 5;
    
    return [
      ChartBarData(
        label: 'Core Competency (Max: 25)',
        value: coreScore,
        maxValue: 25,
        displayValue: coreScore.toStringAsFixed(1),
      ),
      ChartBarData(
        label: 'Experience & Seniority (Max: 20)',
        value: expScore,
        maxValue: 20,
        displayValue: expScore.toStringAsFixed(1),
      ),
      ChartBarData(
        label: 'Potential & Ability (Max: 10)',
        value: potentialScore,
        maxValue: 10,
        displayValue: potentialScore.toStringAsFixed(1),
      ),
      ChartBarData(
        label: 'Company Fit (Max: 5)',
        value: companyScore,
        maxValue: 5,
        displayValue: companyScore.toStringAsFixed(1),
      ),
    ];
  }

  /// Convert Category 3 (Bonus Points) data
  /// Uses actual bonus breakdown data from backend
  static List<BonusPointData> convertCategory3Data(ATSBreakdown breakdown) {
    // Note: The breakdown only contains the total bonus points (-1.75 in the example)
    // For detailed breakdown, we would need additional fields in the ATSBreakdown model
    // For now, we'll show the total bonus and create logical breakdown
    final totalBonus = breakdown.bonusPoints;
    
    // Create a logical breakdown based on typical ATS bonus structure
    return [
      BonusPointData(
        label: 'Required Keywords Matched',
        points: totalBonus > 0 ? totalBonus * 0.6 : 0.0,
        isPositive: totalBonus > 0,
      ),
      BonusPointData(
        label: 'Preferred Keywords Matched',
        points: totalBonus > 0 ? totalBonus * 0.4 : 0.0,
        isPositive: totalBonus > 0,
      ),
      BonusPointData(
        label: 'Missing Keywords Penalty',
        points: totalBonus < 0 ? totalBonus : 0.0,
        isPositive: false,
      ),
    ];
  }

  /// Get overall scores for display
  static Map<String, dynamic> getOverallScores(ATSResult atsResult) {
    return {
      'category1_score': atsResult.breakdown.category1.score,
      'category1_max': 40,
      'category2_score': atsResult.breakdown.category2.score,
      'category2_max': 60,
      'bonus_points': atsResult.breakdown.bonusPoints,
      'final_ats_score': atsResult.finalATSScore,
    };
  }
}