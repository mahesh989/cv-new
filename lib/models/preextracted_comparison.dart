import 'package:flutter/foundation.dart';

@immutable
class CategorySummary {
  final String name;
  final int cvTotal;
  final int jdTotal;
  final int matched;
  final int missing;
  final double matchRatePercent;

  const CategorySummary({
    required this.name,
    required this.cvTotal,
    required this.jdTotal,
    required this.matched,
    required this.missing,
    required this.matchRatePercent,
  });
}

@immutable
class OverallSummary {
  final int totalRequirements;
  final int matched;
  final int missing;
  final double matchRatePercent;

  const OverallSummary({
    required this.totalRequirements,
    required this.matched,
    required this.missing,
    required this.matchRatePercent,
  });
}

@immutable
class MatchedItem {
  final String jdSkill;
  final String cvSkill;
  final String reasoning;

  const MatchedItem({
    required this.jdSkill,
    required this.cvSkill,
    required this.reasoning,
  });
}

@immutable
class MissingItem {
  final String jdSkill;
  final String reasoning;

  const MissingItem({
    required this.jdSkill,
    required this.reasoning,
  });
}

@immutable
class PreextractedComparisonResult {
  final OverallSummary overall;
  final List<CategorySummary> categories;
  final List<MatchedItem> matched;
  final List<MissingItem> missing;
  final String rawText;

  const PreextractedComparisonResult({
    required this.overall,
    required this.categories,
    required this.matched,
    required this.missing,
    required this.rawText,
  });
}
