import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/optimization_session.dart';
import '../services/ats_service.dart';
import 'package:http/http.dart' as http;

class OptimizationWorkspaceService {
  final String baseUrl;
  final SharedPreferences prefs;

  OptimizationWorkspaceService({
    this.baseUrl = 'http://localhost:8000',
    required this.prefs,
  });

  static const String _workspacesKey = 'optimization_workspaces';
  static const String _activeSessionKey = 'active_optimization_session';

  Future<List<JobOptimizationWorkspace>> getWorkspaces() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/workspaces'));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data
            .map((json) => JobOptimizationWorkspace.fromJson(json))
            .toList();
      }
      throw Exception('Failed to load workspaces');
    } catch (e) {
      // Fallback to local storage if API fails
      final String? workspacesJson = prefs.getString(_workspacesKey);
      if (workspacesJson != null) {
        final List<dynamic> data = json.decode(workspacesJson);
        return data
            .map((json) => JobOptimizationWorkspace.fromJson(json))
            .toList();
      }
      return [];
    }
  }

  Future<JobOptimizationWorkspace?> getWorkspace(String jobUrl) async {
    try {
      final response =
          await http.get(Uri.parse('$baseUrl/api/workspaces/$jobUrl'));
      if (response.statusCode == 200) {
        return JobOptimizationWorkspace.fromJson(json.decode(response.body));
      }
      throw Exception('Failed to load workspace');
    } catch (e) {
      // Fallback to local storage if API fails
      final String? workspacesJson = prefs.getString(_workspacesKey);
      if (workspacesJson != null) {
        final List<dynamic> data = json.decode(workspacesJson);
        try {
          final workspace = data
              .map((json) => JobOptimizationWorkspace.fromJson(json))
              .firstWhere((w) => w.jobUrl == jobUrl);
          return workspace;
        } catch (e) {
          return null;
        }
      }
      return null;
    }
  }

  Future<void> updateWorkspace(JobOptimizationWorkspace workspace) async {
    try {
      final response = await http.put(
        Uri.parse('$baseUrl/api/workspaces/${workspace.jobUrl}'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(workspace.toJson()),
      );
      if (response.statusCode != 200) {
        throw Exception('Failed to update workspace');
      }
    } catch (e) {
      // Update local storage if API fails
      final String? workspacesJson = prefs.getString(_workspacesKey);
      if (workspacesJson != null) {
        final List<dynamic> data = json.decode(workspacesJson);
        final workspaces = data
            .map((json) => JobOptimizationWorkspace.fromJson(json))
            .toList();
        final index =
            workspaces.indexWhere((w) => w.jobUrl == workspace.jobUrl);
        if (index != -1) {
          workspaces[index] = workspace;
          await prefs.setString(_workspacesKey,
              json.encode(workspaces.map((w) => w.toJson()).toList()));
        }
      }
    }
  }

  Future<void> deleteWorkspace(String jobUrl) async {
    try {
      final response =
          await http.delete(Uri.parse('$baseUrl/api/workspaces/$jobUrl'));
      if (response.statusCode != 200) {
        throw Exception('Failed to delete workspace');
      }
    } catch (e) {
      // Update local storage if API fails
      final String? workspacesJson = prefs.getString(_workspacesKey);
      if (workspacesJson != null) {
        final List<dynamic> data = json.decode(workspacesJson);
        final workspaces = data
            .map((json) => JobOptimizationWorkspace.fromJson(json))
            .where((w) => w.jobUrl != jobUrl)
            .toList();
        await prefs.setString(_workspacesKey,
            json.encode(workspaces.map((w) => w.toJson()).toList()));
      }
    }
  }

  Future<void> setActiveSession(OptimizationSession session) async {
    await prefs.setString(_activeSessionKey, json.encode(session.toJson()));
  }

  OptimizationSession? getActiveSession() {
    final String? sessionJson = prefs.getString(_activeSessionKey);
    if (sessionJson != null) {
      return OptimizationSession.fromJson(json.decode(sessionJson));
    }
    return null;
  }

  Future<void> clearActiveSession() async {
    await prefs.remove(_activeSessionKey);
  }

  // Get workspace for specific job URL
  Future<JobOptimizationWorkspace?> getWorkspaceForJob(String jobUrl) async {
    final workspaces = await getWorkspaces();
    try {
      return workspaces.firstWhere((w) => w.jobUrl == jobUrl);
    } catch (e) {
      return null;
    }
  }

  // Create new workspace
  Future<JobOptimizationWorkspace> createWorkspace({
    required String jobUrl,
    required String jobTitle,
    required String company,
  }) async {
    final workspace = JobOptimizationWorkspace(
      jobUrl: jobUrl,
      jobTitle: jobTitle,
      company: company,
      firstOptimization: DateTime.now(),
      sessions: [],
    );

    await updateWorkspace(workspace);
    return workspace;
  }

  // Start new optimization session
  Future<OptimizationSession> startNewSession({
    required String jobUrl,
    required String originalCVName,
    required int initialScore,
  }) async {
    final session = OptimizationSession(
      sessionId: DateTime.now().millisecondsSinceEpoch.toString(),
      startTime: DateTime.now(),
      jobUrl: jobUrl,
      originalCVName: originalCVName,
      steps: [],
      initialScore: initialScore,
    );

    // Save as active session
    await setActiveSession(session);

    return session;
  }

  // Add step to current session
  Future<void> addStepToActiveSession(OptimizationStep step) async {
    final session = getActiveSession();
    if (session != null) {
      final updatedSession = OptimizationSession(
        sessionId: session.sessionId,
        startTime: session.startTime,
        endTime: session.endTime,
        jobUrl: session.jobUrl,
        originalCVName: session.originalCVName,
        steps: [...session.steps, step],
        initialScore: session.initialScore,
        finalScore: session.finalScore,
        status: session.status,
      );
      await setActiveSession(updatedSession);
    }
  }

  // Complete current session
  Future<void> completeActiveSession({required int finalScore}) async {
    final session = getActiveSession();
    if (session != null) {
      final completedSession = OptimizationSession(
        sessionId: session.sessionId,
        startTime: session.startTime,
        endTime: DateTime.now(),
        jobUrl: session.jobUrl,
        originalCVName: session.originalCVName,
        steps: session.steps,
        initialScore: session.initialScore,
        finalScore: finalScore,
        status: 'completed',
      );

      // Add to workspace
      await _addSessionToWorkspace(completedSession);

      // Clear active session
      await clearActiveSession();
    }
  }

  // Add completed session to workspace
  Future<void> _addSessionToWorkspace(OptimizationSession session) async {
    final workspaces = await getWorkspaces();
    final workspaceIndex =
        workspaces.indexWhere((w) => w.jobUrl == session.jobUrl);

    if (workspaceIndex != -1) {
      final workspace = workspaces[workspaceIndex];
      final updatedWorkspace = JobOptimizationWorkspace(
        jobUrl: workspace.jobUrl,
        jobTitle: workspace.jobTitle,
        company: workspace.company,
        firstOptimization: workspace.firstOptimization,
        sessions: [...workspace.sessions, session],
        jobMetadata: workspace.jobMetadata,
      );

      await updateWorkspace(updatedWorkspace);
    }
  }

  // Get workspace analytics
  Future<Map<String, dynamic>> getWorkspaceAnalytics(String jobUrl) async {
    final workspace = await getWorkspace(jobUrl);
    if (workspace == null) return {};

    return {
      'total_sessions': workspace.totalSessions,
      'completed_sessions': workspace.completedSessions,
      'best_score': workspace.bestScore,
      'average_improvement': workspace.averageImprovement,
      'total_time_spent': workspace.totalTimeSpent.inMinutes,
    };
  }

  // Get global analytics across all workspaces
  Future<Map<String, dynamic>> getGlobalAnalytics() async {
    final workspaces = await getWorkspaces();

    if (workspaces.isEmpty) return {};

    int totalSessions = 0;
    int completedSessions = 0;
    int bestScore = 0;
    double totalImprovement = 0;
    int totalTimeSpent = 0;

    for (final workspace in workspaces) {
      totalSessions += workspace.totalSessions;
      completedSessions += workspace.completedSessions;
      if (workspace.bestScore > bestScore) {
        bestScore = workspace.bestScore;
      }
      totalImprovement += workspace.averageImprovement;
      totalTimeSpent += workspace.totalTimeSpent.inMinutes;
    }

    return {
      'total_workspaces': workspaces.length,
      'total_sessions': totalSessions,
      'completed_sessions': completedSessions,
      'best_score': bestScore,
      'average_improvement': totalImprovement / workspaces.length,
      'total_time_spent': totalTimeSpent,
    };
  }
}
