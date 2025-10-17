import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:html' as html;
import '../../core/theme/app_theme.dart';

class SavedJobsTable extends StatefulWidget {
  final List<Map<String, dynamic>> jobs;
  final Function(Map<String, dynamic>, bool)? onAppliedStatusChanged;
  final Function(Map<String, dynamic>, String)? onRemarksChanged;

  const SavedJobsTable({
    super.key,
    required this.jobs,
    this.onAppliedStatusChanged,
    this.onRemarksChanged,
  });

  @override
  State<SavedJobsTable> createState() => _SavedJobsTableState();
}

class _SavedJobsTableState extends State<SavedJobsTable> {
  final Map<String, bool> _appliedStatus = {};
  final Map<String, String> _remarks = {};
  final Set<String> _hoveredRows = {};

  @override
  void initState() {
    super.initState();
    _loadSavedStatuses();
  }

  Future<void> _loadSavedStatuses() async {
    final prefs = await SharedPreferences.getInstance();
    for (var job in widget.jobs) {
      final key = _getJobKey(job);
      setState(() {
        _appliedStatus[key] = prefs.getBool('applied_$key') ?? false;
        _remarks[key] = prefs.getString('remarks_$key') ?? '';
      });
    }
  }

  Future<void> _saveStatus(String key, bool value) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final prefKey = 'applied_$key';
      final success = await prefs.setBool(prefKey, value);

      // Verify the save
      final savedValue = prefs.getBool(prefKey);

      if (success && savedValue == value) {
        print('✅ [SAVED_JOBS_TABLE] Saved applied status: $prefKey = $value');
      } else {
        print(
            '❌ [SAVED_JOBS_TABLE] Failed to save applied status: $prefKey, expected $value, got $savedValue');
      }
    } catch (e) {
      print('❌ [SAVED_JOBS_TABLE] Error saving applied status: $e');
    }
  }


  String _getJobKey(Map<String, dynamic> job) {
    // Create a more robust key using multiple fields and normalize them
    // This MUST match the key generation in JobTrackingScreen
    final companyName =
        (job['company_name'] ?? '').toString().trim().toLowerCase();
    final jobUrl = (job['job_url'] ?? '').toString().trim();
    final jobTitle = (job['job_title'] ?? '').toString().trim().toLowerCase();

    // Use a combination of fields to create a unique, stable key
    final key = '${companyName}_${jobTitle}_${jobUrl.hashCode}';
    return key;
  }

  String _formatDate(String? dateString) {
    if (dateString == null || dateString.isEmpty) {
      return 'Unknown Date';
    }

    try {
      final date = DateTime.parse(dateString);
      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return 'Invalid Date';
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: SizedBox(
        width: 1200, // Fixed minimum width
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildTableHeader(),
            const SizedBox(height: 8),
            widget.jobs.isEmpty ? _buildEmptyState() : _buildJobList(),
          ],
        ),
      ),
    );
  }

  Widget _buildTableHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          // Name column
          Expanded(
            flex: 3,
            child: Text(
              'Name',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Location column
          Expanded(
            flex: 2,
            child: Text(
              'Location',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Post column
          Expanded(
            flex: 3,
            child: Text(
              'Post',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Date column
          Expanded(
            flex: 2,
            child: Text(
              'Date',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Contact column
          Expanded(
            flex: 2,
            child: Text(
              'Contact',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Already Applied? column
          SizedBox(
            width: 120,
            child: Text(
              'Already Applied?',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          // Remarks column
          Expanded(
            flex: 2,
            child: Text(
              'Remarks',
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildJobList() {
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: widget.jobs.length,
      itemBuilder: (context, index) => _buildJobRow(widget.jobs[index]),
    );
  }

  Widget _buildJobRow(Map<String, dynamic> job) {
    final key = _getJobKey(job);
    final isHovered = _hoveredRows.contains(key);
    final isApplied = _appliedStatus[key] ?? false;

    return MouseRegion(
      onEnter: (_) => setState(() => _hoveredRows.add(key)),
      onExit: (_) => setState(() => _hoveredRows.remove(key)),
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isHovered ? AppTheme.neutralGray50 : Colors.white,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: AppTheme.neutralGray200,
            width: 1,
          ),
        ),
        child: Row(
          children: [
            // Name (company_name) - clickable if has URL
            Expanded(
              flex: 3,
              child: GestureDetector(
                onTap: job['job_url'] != null
                    ? () => _launchUrl(job['job_url'])
                    : null,
                child: Text(
                  job['company_name'] ?? 'Unknown Company',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                        color: job['job_url'] != null
                            ? (isHovered ? Colors.blue : AppTheme.primaryTeal)
                            : AppTheme.neutralGray700,
                        decoration: job['job_url'] != null && isHovered
                            ? TextDecoration.underline
                            : null,
                      ),
                ),
              ),
            ),
            // Location
            Expanded(
              flex: 2,
              child: Text(
                job['location'] ?? 'Unknown Location',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.neutralGray600,
                    ),
              ),
            ),
            // Post (job_title)
            Expanded(
              flex: 3,
              child: Text(
                job['job_title'] ?? 'Unknown Position',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.neutralGray700,
                    ),
              ),
            ),
            // Date (extracted_at)
            Expanded(
              flex: 2,
              child: Text(
                _formatDate(job['extracted_at']),
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppTheme.neutralGray600,
                    ),
              ),
            ),
            // Contact info (email/phone)
            Expanded(
              flex: 2,
              child: _buildContactInfo(job),
            ),
            // Already Applied? toggle
            SizedBox(
              width: 120,
              child: Switch(
                value: isApplied,
                onChanged: (value) async {
                  print(
                      '🔄 [SAVED_JOBS_TABLE] Toggle clicked for ${job['company_name']}: $value');
                  print('🔑 [SAVED_JOBS_TABLE] Generated key: $key');
                  setState(() => _appliedStatus[key] = value);
                  await _saveStatus(key, value);
                  // Notify parent about status change
                  widget.onAppliedStatusChanged?.call(job, value);
                  print(
                      '📞 [SAVED_JOBS_TABLE] Called parent callback for ${job['company_name']}: $value');
                },
                activeColor: Colors.green,
              ),
            ),
            // Actions (Preview & Download)
            Expanded(
              flex: 2,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                decoration: BoxDecoration(
                  color: AppTheme.neutralGray50,
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(
                    color: AppTheme.neutralGray200,
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    // Preview Icon
                    GestureDetector(
                      onTap: () => _showCVPreview(job),
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(
                            color: Colors.blue.shade200,
                            width: 1,
                          ),
                        ),
                        child: Icon(
                          Icons.visibility,
                          size: 16,
                          color: Colors.blue.shade600,
                        ),
                      ),
                    ),
                    // Download Icon
                    GestureDetector(
                      onTap: () => _downloadCV(job),
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.green.shade50,
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(
                            color: Colors.green.shade200,
                            width: 1,
                          ),
                        ),
                        child: Icon(
                          Icons.download,
                          size: 16,
                          color: Colors.green.shade600,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContactInfo(Map<String, dynamic> job) {
    final email = job['email'];
    final phone = job['phone_number'];

    if (email == null && phone == null) {
      return Text(
        'N/A',
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppTheme.neutralGray500,
              fontStyle: FontStyle.italic,
            ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (email != null)
          InkWell(
            onTap: () => _launchUrl('mailto:$email'),
            child: Text(
              email,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.blue,
                    decoration: TextDecoration.underline,
                  ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        if (email != null && phone != null) const SizedBox(height: 4),
        if (phone != null)
          InkWell(
            onTap: () => _launchUrl('tel:$phone'),
            child: Text(
              phone,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.blue,
                    decoration: TextDecoration.underline,
                  ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
      ],
    );
  }

  Future<void> _launchUrl(String url) async {
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    }
  }

  void _showCVPreview(Map<String, dynamic> job) async {
    final companyName = job['company_name'] ?? 'Unknown Company';
    
    try {
      // Show loading dialog
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          content: Row(
            children: [
              const CircularProgressIndicator(),
              const SizedBox(width: 16),
              Text('Loading CV preview...'),
            ],
          ),
        ),
      );

      // Get tailored CV content
      final cvContent = await _getTailoredCVContent(companyName);
      
      // Close loading dialog
      Navigator.of(context).pop();
      
      if (cvContent != null) {
        // Show CV preview dialog
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: Row(
              children: [
                Icon(Icons.visibility, color: Colors.blue.shade600),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'CV Preview - $companyName',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppTheme.neutralGray800,
                        ),
                  ),
                ),
              ],
            ),
            content: Container(
              width: double.maxFinite,
              height: 400,
              child: SingleChildScrollView(
                child: Text(
                  cvContent,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppTheme.neutralGray700,
                        height: 1.5,
                      ),
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: Text(
                  'Close',
                  style: TextStyle(color: AppTheme.neutralGray600),
                ),
              ),
            ],
          ),
        );
      } else {
        // Show error message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('No tailored CV found for $companyName'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    } catch (e) {
      // Close loading dialog if still open
      Navigator.of(context).pop();
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error loading CV preview: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _downloadCV(Map<String, dynamic> job) async {
    final companyName = job['company_name'] ?? 'Unknown Company';
    
    try {
      // Show loading indicator
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(strokeWidth: 2),
              ),
              const SizedBox(width: 12),
              Text('Preparing download...'),
            ],
          ),
          duration: const Duration(seconds: 2),
        ),
      );

      // Download the PDF
      await _downloadTailoredCVPDF(companyName);
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('CV downloaded successfully!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Download failed: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppTheme.neutralGray200),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.work_outline,
            size: 48,
            color: AppTheme.neutralGray400,
          ),
          const SizedBox(height: 16),
          Text(
            'No jobs found',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppTheme.neutralGray600,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Your saved jobs will appear here',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.neutralGray500,
                ),
          ),
        ],
      ),
    );
  }

  // Helper function to get tailored CV content
  Future<String?> _getTailoredCVContent(String companyName) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');

      final url = Uri.parse(
          'https://cvagent.duckdns.org/api/tailored-cv/content/$companyName');

      final response = await http.get(url, headers: {
        if (token != null) 'Authorization': 'Bearer $token',
      });

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['content'] as String?;
      } else {
        print('Failed to get CV content: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('Error getting CV content: $e');
      return null;
    }
  }

  // Helper function to download tailored CV PDF
  Future<void> _downloadTailoredCVPDF(String companyName) async {
    try {
      // Use the existing PDF download logic from CV generation screen
      await _downloadPDFDirectly(companyName);
    } catch (e) {
      print('Error downloading CV PDF: $e');
      rethrow;
    }
  }

  // Direct PDF download using the same logic as CV generation screen
  Future<void> _downloadPDFDirectly(String companyName) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token');

      final url = Uri.parse(
          'https://cvagent.duckdns.org/api/tailored-cv/export-pdf/$companyName');

      final response = await http.get(url, headers: {
        if (token != null) 'Authorization': 'Bearer $token',
      });

      if (response.statusCode == 200) {
        final bytes = response.bodyBytes;
        final blob = html.Blob([bytes], 'application/pdf');
        final urlObject = html.Url.createObjectUrlFromBlob(blob);
        final anchor = html.AnchorElement(href: urlObject)
          ..download = '${companyName}_tailored_resume.pdf'
          ..style.display = 'none';
        html.document.body!.append(anchor);
        anchor.click();
        anchor.remove();
        html.Url.revokeObjectUrl(urlObject);
      } else {
        throw Exception('Failed to download PDF: ${response.statusCode}');
      }
    } catch (e) {
      print('Error in direct PDF download: $e');
      rethrow;
    }
  }

}
