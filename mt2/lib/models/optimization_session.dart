import '../services/ats_service.dart';

class OptimizationStep {
  final String type; // 'ats_result' or 'cv_generated'
  final DateTime timestamp;
  final String cvName;
  final ATSResult? atsResult;
  final String? cvContent;
  final Map<String, dynamic>? metadata;

  OptimizationStep({
    required this.type,
    required this.timestamp,
    required this.cvName,
    this.atsResult,
    this.cvContent,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
        'type': type,
        'timestamp': timestamp.toIso8601String(),
        'cvName': cvName,
        'atsResult': atsResult?.toJson(),
        'cvContent': cvContent,
        'metadata': metadata,
      };

  factory OptimizationStep.fromJson(Map<String, dynamic> json) =>
      OptimizationStep(
        type: json['type'],
        timestamp: DateTime.parse(json['timestamp']),
        cvName: json['cvName'],
        atsResult: json['atsResult'] != null
            ? ATSResult.fromJson(json['atsResult'])
            : null,
        cvContent: json['cvContent'],
        metadata: json['metadata'],
      );
}

class OptimizationSession {
  final String sessionId;
  final DateTime startTime;
  final DateTime? endTime;
  final String jobUrl;
  final String originalCVName;
  final List<OptimizationStep> steps;
  final int initialScore;
  final int? finalScore;
  final String status; // 'active', 'completed', 'paused'

  OptimizationSession({
    required this.sessionId,
    required this.startTime,
    this.endTime,
    required this.jobUrl,
    required this.originalCVName,
    required this.steps,
    required this.initialScore,
    this.finalScore,
    this.status = 'active',
  });

  // Calculate session metrics
  int get improvementPoints => (finalScore ?? 0) - initialScore;
  double get improvementPercentage =>
      initialScore > 0 ? (improvementPoints / initialScore) * 100 : 0;
  int get iterationCount => steps.where((s) => s.type == 'cv_generated').length;
  Duration get sessionDuration =>
      (endTime ?? DateTime.now()).difference(startTime);

  String get bestCVName =>
      steps.where((s) => s.type == 'cv_generated').lastOrNull?.cvName ??
      originalCVName;

  Map<String, dynamic> toJson() => {
        'sessionId': sessionId,
        'startTime': startTime.toIso8601String(),
        'endTime': endTime?.toIso8601String(),
        'jobUrl': jobUrl,
        'originalCVName': originalCVName,
        'steps': steps.map((s) => s.toJson()).toList(),
        'initialScore': initialScore,
        'finalScore': finalScore,
        'status': status,
      };

  factory OptimizationSession.fromJson(Map<String, dynamic> json) =>
      OptimizationSession(
        sessionId: json['sessionId'],
        startTime: DateTime.parse(json['startTime']),
        endTime:
            json['endTime'] != null ? DateTime.parse(json['endTime']) : null,
        jobUrl: json['jobUrl'],
        originalCVName: json['originalCVName'],
        steps: (json['steps'] as List)
            .map((s) => OptimizationStep.fromJson(s))
            .toList(),
        initialScore: json['initialScore'],
        finalScore: json['finalScore'],
        status: json['status'] ?? 'active',
      );
}

class JobOptimizationWorkspace {
  final String jobUrl;
  final String jobTitle;
  final String company;
  final DateTime firstOptimization;
  final List<OptimizationSession> sessions;
  final Map<String, dynamic> jobMetadata;

  JobOptimizationWorkspace({
    required this.jobUrl,
    required this.jobTitle,
    required this.company,
    required this.firstOptimization,
    required this.sessions,
    this.jobMetadata = const {},
  });

  // Analytics
  int get totalSessions => sessions.length;
  int get completedSessions =>
      sessions.where((s) => s.status == 'completed').length;
  OptimizationSession? get bestSession => sessions.isEmpty
      ? null
      : sessions
          .reduce((a, b) => (a.finalScore ?? 0) > (b.finalScore ?? 0) ? a : b);
  int get bestScore => bestSession?.finalScore ?? 0;
  String get bestCVName => bestSession?.bestCVName ?? '';
  double get averageImprovement => sessions.isEmpty
      ? 0
      : sessions.map((s) => s.improvementPercentage).reduce((a, b) => a + b) /
          sessions.length;
  Duration get totalTimeSpent =>
      sessions.fold(Duration.zero, (sum, s) => sum + s.sessionDuration);

  Map<String, dynamic> toJson() => {
        'jobUrl': jobUrl,
        'jobTitle': jobTitle,
        'company': company,
        'firstOptimization': firstOptimization.toIso8601String(),
        'sessions': sessions.map((s) => s.toJson()).toList(),
        'jobMetadata': jobMetadata,
      };

  factory JobOptimizationWorkspace.fromJson(Map<String, dynamic> json) =>
      JobOptimizationWorkspace(
        jobUrl: json['jobUrl'],
        jobTitle: json['jobTitle'],
        company: json['company'],
        firstOptimization: DateTime.parse(json['firstOptimization']),
        sessions: (json['sessions'] as List)
            .map((s) => OptimizationSession.fromJson(s))
            .toList(),
        jobMetadata: json['jobMetadata'] ?? {},
      );
}

extension ListExtension<T> on List<T> {
  T? get lastOrNull => isEmpty ? null : last;
}
