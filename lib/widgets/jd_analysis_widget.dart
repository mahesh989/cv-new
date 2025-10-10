import 'package:flutter/material.dart';
import '../services/jd_analysis_service.dart';

class JDAnalysisWidget extends StatefulWidget {
  final String companyName;
  final VoidCallback? onAnalysisComplete;
  final bool showDetailedView;

  const JDAnalysisWidget({
    Key? key,
    required this.companyName,
    this.onAnalysisComplete,
    this.showDetailedView = true,
  }) : super(key: key);

  @override
  _JDAnalysisWidgetState createState() => _JDAnalysisWidgetState();
}

class _JDAnalysisWidgetState extends State<JDAnalysisWidget>
    with TickerProviderStateMixin {
  final JDAnalysisService _service = JDAnalysisService();

  JDAnalysisResult? _analysisResult;
  AnalysisStatus? _status;
  bool _isLoading = false;
  bool _isAnalyzing = false;
  String? _error;

  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
    _loadAnalysisStatus();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadAnalysisStatus() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final status = await _service.getAnalysisStatus(widget.companyName);
      setState(() {
        _status = status;
        _isLoading = false;
      });

      // If analysis exists, load it
      if (status.analysisExists) {
        await _loadExistingAnalysis();
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _loadExistingAnalysis() async {
    try {
      final result = await _service.getAnalysis(widget.companyName);
      setState(() {
        _analysisResult = result;
      });
    } catch (e) {
      debugPrint('Error loading existing analysis: $e');
    }
  }

  Future<void> _analyzeSkills({bool forceRefresh = false}) async {
    setState(() {
      _isAnalyzing = true;
      _error = null;
    });

    try {
      final result = await _service.analyzeSkills(
        companyName: widget.companyName,
        forceRefresh: forceRefresh,
      );

      setState(() {
        _analysisResult = result;
        _isAnalyzing = false;
      });

      // Update status
      await _loadAnalysisStatus();

      // Notify parent widget
      widget.onAnalysisComplete?.call();

      // Show success message
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result.fromCache
                  ? 'Analysis loaded from cache'
                  : 'Analysis completed successfully!',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isAnalyzing = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Analysis failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            const SizedBox(height: 16),
            if (_isLoading) _buildLoadingIndicator(),
            if (_error != null) _buildErrorWidget(),
            if (_status != null && !_isLoading && _error == null) ...[
              _buildStatusInfo(),
              const SizedBox(height: 16),
              _buildActionButtons(),
            ],
            if (_analysisResult != null) ...[
              const SizedBox(height: 16),
              if (widget.showDetailedView) _buildDetailedAnalysis(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        const Icon(Icons.analytics, color: Colors.blue),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            'Job Description Analysis',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
        ),
        if (_analysisResult != null)
          Chip(
            label: Text(_analysisResult!.fromCache ? 'Cached' : 'Fresh'),
            backgroundColor: _analysisResult!.fromCache
                ? Colors.orange.shade100
                : Colors.green.shade100,
          ),
      ],
    );
  }

  Widget _buildLoadingIndicator() {
    return const Center(
      child: Padding(
        padding: EdgeInsets.all(32),
        child: CircularProgressIndicator(),
      ),
    );
  }

  Widget _buildErrorWidget() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Column(
        children: [
          Row(
            children: [
              Icon(Icons.error, color: Colors.red.shade600),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Error: $_error',
                  style: TextStyle(color: Colors.red.shade700),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: _loadAnalysisStatus,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusInfo() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Analysis Status',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          _buildStatusRow('Company', _status!.companyName),
          _buildStatusRow(
              'JD File', _status!.jdFileExists ? 'Available' : 'Missing'),
          _buildStatusRow(
              'Analysis', _status!.analysisExists ? 'Available' : 'Not Found'),
          _buildStatusRow('Can Analyze', _status!.canAnalyze ? 'Yes' : 'No'),
          if (_status!.analysisTimestamp != null)
            _buildStatusRow(
                'Last Updated', _formatTimestamp(_status!.analysisTimestamp!)),
          if (_status!.aiModelUsed != null)
            _buildStatusRow('AI Model', _status!.aiModelUsed!),
        ],
      ),
    );
  }

  Widget _buildStatusRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton.icon(
            onPressed: _status!.canAnalyze && !_isAnalyzing
                ? () => _analyzeSkills(forceRefresh: false)
                : null,
            icon: _isAnalyzing
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.analytics),
            label: Text(_isAnalyzing ? 'Analyzing...' : 'Analyze Skills'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
            ),
          ),
        ),
        const SizedBox(width: 8),
        if (_status!.analysisExists)
          ElevatedButton.icon(
            onPressed: _status!.canAnalyze && !_isAnalyzing
                ? () => _analyzeSkills(forceRefresh: true)
                : null,
            icon: const Icon(Icons.refresh),
            label: const Text('Refresh'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange,
              foregroundColor: Colors.white,
            ),
          ),
      ],
    );
  }

  Widget _buildDetailedAnalysis() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Analysis Results',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 16),
        TabBar(
          controller: _tabController,
          isScrollable: true,
          tabs: const [
            Tab(text: 'Overview'),
            Tab(text: 'Technical'),
            Tab(text: 'Soft Skills'),
            Tab(text: 'Experience'),
            Tab(text: 'Domain'),
          ],
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 400,
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildOverviewTab(),
              _buildTechnicalTab(),
              _buildSoftSkillsTab(),
              _buildExperienceTab(),
              _buildDomainTab(),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildOverviewTab() {
    final summary = _analysisResult!.skillSummary;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSummaryCard('Total Skills',
              '${summary.totalRequired + summary.totalPreferred}'),
          const SizedBox(height: 12),
          _buildSummaryCard('Required Skills', '${summary.totalRequired}'),
          const SizedBox(height: 12),
          _buildSummaryCard('Preferred Skills', '${summary.totalPreferred}'),
          const SizedBox(height: 12),
          _buildSummaryCard('Experience Years',
              '${_analysisResult!.experienceYears ?? 'N/A'}'),
          const SizedBox(height: 16),
          Text(
            'Skills Breakdown',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          _buildSkillBreakdown('Technical', summary.requiredTechnical,
              summary.preferredTechnical),
          _buildSkillBreakdown('Soft Skills', summary.requiredSoftSkills,
              summary.preferredSoftSkills),
          _buildSkillBreakdown('Experience', summary.requiredExperience,
              summary.preferredExperience),
          _buildSkillBreakdown(
              'Domain Knowledge',
              summary.requiredDomainKnowledge,
              summary.preferredDomainKnowledge),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(String title, String value) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
            Text(
              value,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSkillBreakdown(String category, int required, int preferred) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(category),
          ),
          Expanded(
            child: Row(
              children: [
                Container(
                  width: 60,
                  height: 20,
                  decoration: BoxDecoration(
                    color: Colors.red.shade100,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Center(
                    child: Text(
                      '$required',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.red.shade700,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  width: 60,
                  height: 20,
                  decoration: BoxDecoration(
                    color: Colors.orange.shade100,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Center(
                    child: Text(
                      '$preferred',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.orange.shade700,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTechnicalTab() {
    return _buildSkillsList(
      'Technical Skills',
      _analysisResult!.requiredSkills.technical,
      _analysisResult!.preferredSkills.technical,
      Icons.code,
      Colors.blue,
    );
  }

  Widget _buildSoftSkillsTab() {
    return _buildSkillsList(
      'Soft Skills',
      _analysisResult!.requiredSkills.softSkills,
      _analysisResult!.preferredSkills.softSkills,
      Icons.people,
      Colors.green,
    );
  }

  Widget _buildExperienceTab() {
    return _buildSkillsList(
      'Experience Requirements',
      _analysisResult!.requiredSkills.experience,
      _analysisResult!.preferredSkills.experience,
      Icons.work,
      Colors.purple,
    );
  }

  Widget _buildDomainTab() {
    return _buildSkillsList(
      'Domain Knowledge',
      _analysisResult!.requiredSkills.domainKnowledge,
      _analysisResult!.preferredSkills.domainKnowledge,
      Icons.business,
      Colors.orange,
    );
  }

  Widget _buildSkillsList(
    String title,
    List<String> required,
    List<String> preferred,
    IconData icon,
    Color color,
  ) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color),
              const SizedBox(width: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (required.isNotEmpty) ...[
            Text(
              'Required (${required.length})',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.red.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: required
                  .map((skill) => Chip(
                        label: Text(skill),
                        backgroundColor: Colors.red.shade100,
                        side: BorderSide(color: Colors.red.shade300),
                      ))
                  .toList(),
            ),
            const SizedBox(height: 16),
          ],
          if (preferred.isNotEmpty) ...[
            Text(
              'Preferred (${preferred.length})',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.orange.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: preferred
                  .map((skill) => Chip(
                        label: Text(skill),
                        backgroundColor: Colors.orange.shade100,
                        side: BorderSide(color: Colors.orange.shade300),
                      ))
                  .toList(),
            ),
          ],
          if (required.isEmpty && preferred.isEmpty)
            const Text('No skills found in this category'),
        ],
      ),
    );
  }

  String _formatTimestamp(String timestamp) {
    try {
      final dateTime = DateTime.parse(timestamp);
      return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return timestamp;
    }
  }
}

/// Simple analyze button widget for integration into existing UI
class AnalyzeSkillsButton extends StatefulWidget {
  final String companyName;
  final VoidCallback? onAnalysisComplete;
  final Widget? child;
  final bool showLoadingState;

  const AnalyzeSkillsButton({
    Key? key,
    required this.companyName,
    this.onAnalysisComplete,
    this.child,
    this.showLoadingState = true,
  }) : super(key: key);

  @override
  _AnalyzeSkillsButtonState createState() => _AnalyzeSkillsButtonState();
}

class _AnalyzeSkillsButtonState extends State<AnalyzeSkillsButton> {
  final JDAnalysisService _service = JDAnalysisService();
  bool _isAnalyzing = false;

  Future<void> _analyzeSkills() async {
    setState(() {
      _isAnalyzing = true;
    });

    try {
      await _service.analyzeSkills(
        companyName: widget.companyName,
        forceRefresh: false,
      );

      widget.onAnalysisComplete?.call();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Skills analysis completed successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Analysis failed: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isAnalyzing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: _isAnalyzing ? null : _analyzeSkills,
      icon: _isAnalyzing && widget.showLoadingState
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Icon(Icons.analytics),
      label: Text(_isAnalyzing ? 'Analyzing...' : 'Analyze Skills'),
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
    );
  }
}
