import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/optimization_session.dart';
import '../services/optimization_workspace_service.dart';
import '../utils/notification_service.dart';

class JobOptimizationDashboard extends StatefulWidget {
  final String? jobUrl;
  final String? jobTitle;
  final String? company;
  final String? jdText;

  const JobOptimizationDashboard({
    Key? key,
    this.jobUrl,
    this.jobTitle,
    this.company,
    this.jdText,
  }) : super(key: key);

  @override
  State<JobOptimizationDashboard> createState() =>
      _JobOptimizationDashboardState();
}

class _JobOptimizationDashboardState extends State<JobOptimizationDashboard> {
  late OptimizationWorkspaceService _workspaceService;
  JobOptimizationWorkspace? _workspace;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _initializeServices();
  }

  Future<void> _initializeServices() async {
    final prefs = await SharedPreferences.getInstance();
    _workspaceService = OptimizationWorkspaceService(prefs: prefs);
    await _loadWorkspaceData();
  }

  Future<void> _loadWorkspaceData() async {
    setState(() => _isLoading = true);

    try {
      // Get or create workspace if jobUrl is provided
      if (widget.jobUrl != null && widget.jobUrl!.isNotEmpty) {
        _workspace = await _workspaceService.getWorkspaceForJob(widget.jobUrl!);

        if (_workspace == null) {
          _workspace = await _workspaceService.createWorkspace(
            jobUrl: widget.jobUrl!,
            jobTitle: widget.jobTitle ?? 'Unknown Position',
            company: widget.company ?? 'Unknown Company',
          );
        }
      }
    } catch (e) {
      NotificationService.showError('Failed to load workspace data: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Job Dashboard'),
          backgroundColor: Colors.blue.shade50,
        ),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    final displayJobTitle =
        widget.jobTitle ?? _workspace?.jobTitle ?? 'Unknown Position';
    final displayCompany =
        widget.company ?? _workspace?.company ?? 'Unknown Company';

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              displayJobTitle,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            Text(
              displayCompany,
              style:
                  const TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
            ),
          ],
        ),
        backgroundColor: Colors.blue.shade50,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Job Information Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Job Information',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    _buildInfoRow('Position', displayJobTitle),
                    _buildInfoRow('Company', displayCompany),
                    _buildInfoRow(
                        'First Optimization',
                        _workspace?.firstOptimization != null
                            ? DateFormat('MMM dd, yyyy')
                                .format(_workspace!.firstOptimization)
                            : 'N/A'),
                    if (widget.jobUrl != null)
                      _buildInfoRow('Job URL', widget.jobUrl!, isUrl: true),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // CV Versions
            if (_workspace?.sessions.isNotEmpty == true) ...[
              const Text(
                'CV Versions',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),
              ..._workspace!.sessions
                  .map((session) => _buildSessionCard(session)),
            ],

            const SizedBox(height: 16),

            // Notice about new dashboard
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.purple.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.purple.shade200),
              ),
              child: Column(
                children: [
                  Icon(Icons.info, color: Colors.purple.shade600),
                  const SizedBox(height: 8),
                  Text(
                    'Multi-Job Dashboard Available',
                    style: TextStyle(
                      color: Colors.purple.shade700,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Access the new Multi-Job ATS Dashboard from the main ATS tab for comprehensive analytics across all your job applications.',
                    style: TextStyle(color: Colors.purple.shade600),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, {bool isUrl = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
          Expanded(
            child: Text(
              value,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSessionCard(OptimizationSession session) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(
                  'Session ${session.sessionId}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const Spacer(),
                Text(
                  DateFormat('MMM dd, yyyy').format(session.startTime),
                  style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Text('Status: ${session.status}'),
                const Spacer(),
                if (session.finalScore != null)
                  Text('Score: ${session.finalScore}/100'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
