import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import '../services/enhanced_api_service.dart';
import '../services/api_service.dart';

/// Demo widget to showcase background API functionality
class BackgroundApiDemo extends StatefulWidget {
  const BackgroundApiDemo({Key? key}) : super(key: key);

  @override
  State<BackgroundApiDemo> createState() => _BackgroundApiDemoState();
}

class _BackgroundApiDemoState extends State<BackgroundApiDemo> {
  bool _isRunningDemo = false;
  List<String> _demoLogs = [];
  String _serviceStatus = '';

  @override
  void initState() {
    super.initState();
    _updateServiceStatus();
  }

  void _updateServiceStatus() {
    final status = enhancedApiService.getServiceStatus();
    setState(() {
      _serviceStatus = '''
Enhanced API Service: ${status['enhanced_api_service']}
Background Service: ${status['background_service']['initialized'] ? 'Initialized' : 'Not Initialized'}
Tab Visible: ${status['background_service']['tab_visible']}
Active Requests: ${status['background_service']['active_requests']}
Queued Requests: ${status['background_service']['queued_requests']}
Job Service: ${status['job_service']}
''';
    });
  }

  void _addLog(String message) {
    setState(() {
      _demoLogs.add('${DateTime.now().toIso8601String().substring(11, 19)}: $message');
    });
  }

  Future<void> _runBackgroundApiDemo() async {
    if (_isRunningDemo) return;

    setState(() {
      _isRunningDemo = true;
      _demoLogs.clear();
    });

    _addLog('🚀 Starting background API demo...');
    _addLog('💡 Try switching tabs while this demo runs!');

    try {
      // Demo 1: Simple API call with background support
      _addLog('📡 Starting simple API health check...');
      
      final healthResponse = await enhancedApiService.get(
        '${ApiService.baseUrl}/health',
        timeout: const Duration(seconds: 10),
      );

      if (healthResponse.statusCode == 200) {
        _addLog('✅ Health check completed successfully');
      } else {
        _addLog('⚠️ Health check returned: ${healthResponse.statusCode}');
      }

      await Future.delayed(const Duration(seconds: 2));

      // Demo 2: Long-running operation simulation
      _addLog('🔄 Starting simulated long-running analysis...');
      _addLog('💡 This would normally take 30+ seconds - perfect time to switch tabs!');

      // Simulate a preliminary analysis call
      if (kIsWeb) {
        _addLog('🌐 Web platform detected - background support active');
      } else {
        _addLog('📱 Mobile platform detected - standard behavior');
      }

      // Check if we have uploaded CVs to work with
      final uploadedCVs = await enhancedApiService.fetchUploadedCVs();
      
      if (uploadedCVs.isNotEmpty) {
        _addLog('📄 Found ${uploadedCVs.length} uploaded CV(s)');
        
        // Use the first CV for demo
        final testCV = uploadedCVs.first;
        final testJD = '''
Software Engineer Position
We are looking for a talented Software Engineer with experience in:
- Flutter development
- API integration  
- Mobile applications
- Problem solving
- Team collaboration
        ''';

        _addLog('🧪 Running preliminary analysis with background support...');
        _addLog('⏱️ This operation supports tab switching!');

        final analysisResult = await enhancedApiService.preliminaryAnalysis(
          cvFilename: testCV,
          jdText: testJD,
        );

        if (analysisResult.containsKey('error')) {
          _addLog('⚠️ Analysis completed with message: ${analysisResult['error']}');
        } else {
          _addLog('✅ Preliminary analysis completed successfully!');
          
          // Show some results
          final cvSkills = analysisResult['cv_skills'];
          final jdSkills = analysisResult['jd_skills'];
          
          if (cvSkills != null && cvSkills['technical_skills'] != null) {
            final techSkills = cvSkills['technical_skills'] as List;
            _addLog('🔧 Found ${techSkills.length} technical skills in CV');
          }
          
          if (jdSkills != null && jdSkills['technical_skills'] != null) {
            final techSkills = jdSkills['technical_skills'] as List;
            _addLog('📋 Found ${techSkills.length} technical skills in JD');
          }
        }
      } else {
        _addLog('📭 No uploaded CVs found - using mock analysis');
        
        // Simulate delay for demo purposes
        for (int i = 1; i <= 10; i++) {
          await Future.delayed(const Duration(seconds: 1));
          _addLog('⏳ Mock analysis progress: ${i * 10}%');
          _updateServiceStatus(); // Update status during the process
        }
        
        _addLog('✅ Mock analysis completed successfully!');
      }

      // Demo 3: Show final status
      _addLog('📊 Final service status check...');
      _updateServiceStatus();
      _addLog('✅ Background API demo completed successfully!');
      _addLog('💡 If you switched tabs during this demo, the requests continued in the background!');

    } catch (e) {
      _addLog('❌ Demo failed: $e');
    } finally {
      setState(() {
        _isRunningDemo = false;
      });
      _updateServiceStatus();
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
            Row(
              children: [
                const Icon(Icons.science, color: Colors.blue),
                const SizedBox(width: 8),
                const Text(
                  'Background API Demo',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                ElevatedButton(
                  onPressed: _isRunningDemo ? null : _runBackgroundApiDemo,
                  child: _isRunningDemo
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Run Demo'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'This demo showcases the background API functionality. '
              'Try switching to another tab while the demo is running to see how '
              'API calls continue in the background!',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 16),
            ExpansionTile(
              title: const Text('Service Status'),
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    _serviceStatus,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (_demoLogs.isNotEmpty) ...[
              const Text(
                'Demo Logs:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Container(
                height: 200,
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[900],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: ListView.builder(
                  itemCount: _demoLogs.length,
                  itemBuilder: (context, index) {
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text(
                        _demoLogs[index],
                        style: const TextStyle(
                          color: Colors.green,
                          fontFamily: 'monospace',
                          fontSize: 12,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
            if (_demoLogs.isNotEmpty) const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.orange[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.orange[300]!),
              ),
              child: const Row(
                children: [
                  Icon(Icons.lightbulb, color: Colors.orange),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Tip: Open browser dev tools to see network requests continuing even when you switch tabs!',
                      style: TextStyle(fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
