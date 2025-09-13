import 'package:flutter/material.dart';
import 'services/jd_analysis_service.dart';

/// Simple test widget to verify Flutter integration works
class FlutterIntegrationTest extends StatefulWidget {
  const FlutterIntegrationTest({Key? key}) : super(key: key);

  @override
  _FlutterIntegrationTestState createState() => _FlutterIntegrationTestState();
}

class _FlutterIntegrationTestState extends State<FlutterIntegrationTest> {
  final JDAnalysisService _service = JDAnalysisService();
  JDAnalysisResult? _result;
  String _status = 'Ready to test';
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Flutter Integration Test'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'JD Analysis Integration Test',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),

            // Status
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Status: $_status',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    if (_isLoading) ...[
                      const SizedBox(height: 8),
                      const LinearProgressIndicator(),
                    ],
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Test buttons
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _testLogin,
                    icon: const Icon(Icons.login),
                    label: const Text('Test Login'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _testAnalysis,
                    icon: const Icon(Icons.analytics),
                    label: const Text('Test Analysis'),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Results
            if (_result != null) _buildResults(),
          ],
        ),
      ),
    );
  }

  Widget _buildResults() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Analysis Results',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),

            // Quick summary
            Row(
              children: [
                Expanded(
                  child: _buildResultCard(
                    'Company',
                    _result!.companyName,
                    Colors.blue,
                    Icons.business,
                  ),
                ),
                Expanded(
                  child: _buildResultCard(
                    'Experience',
                    '${_result!.experienceYears ?? 'N/A'} years',
                    Colors.purple,
                    Icons.work,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildResultCard(
                    'Required',
                    '${_result!.skillSummary.totalRequired}',
                    Colors.red,
                    Icons.check_circle,
                  ),
                ),
                Expanded(
                  child: _buildResultCard(
                    'Preferred',
                    '${_result!.skillSummary.totalPreferred}',
                    Colors.orange,
                    Icons.star,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Categorized skills
            Text(
              'Categorized Skills',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 8),

            _buildSkillCategory(
              'Technical Skills',
              _result!.requiredSkills.technical,
              _result!.preferredSkills.technical,
              Colors.blue,
              Icons.code,
            ),

            _buildSkillCategory(
              'Soft Skills',
              _result!.requiredSkills.softSkills,
              _result!.preferredSkills.softSkills,
              Colors.green,
              Icons.people,
            ),

            _buildSkillCategory(
              'Experience',
              _result!.requiredSkills.experience,
              _result!.preferredSkills.experience,
              Colors.purple,
              Icons.work,
            ),

            _buildSkillCategory(
              'Domain Knowledge',
              _result!.requiredSkills.domainKnowledge,
              _result!.preferredSkills.domainKnowledge,
              Colors.orange,
              Icons.business,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard(
      String title, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildSkillCategory(String title, List<String> required,
      List<String> preferred, Color color, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          SizedBox(
            width: 120,
            child: Text(title),
          ),
          Expanded(
            child: Row(
              children: [
                Container(
                  width: 50,
                  height: 20,
                  decoration: BoxDecoration(
                    color: Colors.red.shade100,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Center(
                    child: Text(
                      '${required.length}',
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
                  width: 50,
                  height: 20,
                  decoration: BoxDecoration(
                    color: Colors.orange.shade100,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Center(
                    child: Text(
                      '${preferred.length}',
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

  Future<void> _testLogin() async {
    setState(() {
      _isLoading = true;
      _status = 'Testing login...';
    });

    try {
      final token = await _service.login();
      setState(() {
        _status = 'Login successful! Token: ${token.substring(0, 20)}...';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _status = 'Login failed: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _testAnalysis() async {
    setState(() {
      _isLoading = true;
      _status = 'Testing analysis...';
    });

    try {
      final result = await _service.getAnalysis('Australia_for_UNHCR');
      setState(() {
        _result = result;
        _status =
            'Analysis successful! Found ${result.skillSummary.totalRequired} required skills.';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _status = 'Analysis failed: $e';
        _isLoading = false;
      });
    }
  }
}

/// Simple usage example
class SimpleUsageExample extends StatefulWidget {
  const SimpleUsageExample({Key? key}) : super(key: key);

  @override
  _SimpleUsageExampleState createState() => _SimpleUsageExampleState();
}

class _SimpleUsageExampleState extends State<SimpleUsageExample> {
  final JDAnalysisService _service = JDAnalysisService();
  JDAnalysisResult? _result;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Simple Usage Example')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('Your existing content here...'),
            const SizedBox(height: 32),

            // This is how you integrate the analyze button
            ElevatedButton.icon(
              onPressed: _analyzeSkills,
              icon: const Icon(Icons.analytics),
              label: const Text('Analyze Skills'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),

            const SizedBox(height: 16),

            if (_result != null) ...[
              const Text('Analysis Complete!',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(
                  'Technical Skills: ${_result!.requiredSkills.technical.length}'),
              Text('Soft Skills: ${_result!.requiredSkills.softSkills.length}'),
              Text('Experience: ${_result!.experienceYears} years'),
            ],
          ],
        ),
      ),
    );
  }

  Future<void> _analyzeSkills() async {
    try {
      final result = await _service.getAnalysis('Australia_for_UNHCR');
      setState(() {
        _result = result;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Analysis completed successfully!'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Analysis failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
