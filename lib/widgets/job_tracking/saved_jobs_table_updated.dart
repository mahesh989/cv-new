import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/theme/app_theme.dart';

class SavedJobsTable extends StatefulWidget {
  final List<Map<String, dynamic>> jobs;

  const SavedJobsTable({
    super.key,
    required this.jobs,
  });

  @override
  State<SavedJobsTable> createState() => _SavedJobsTableState();
}

class _SavedJobsTableState extends State<SavedJobsTable> {
  final Map<String, bool> _appliedStatus = {};
  final Map<String, String> _remarks = {};
  final Set<String> _hoveredCompanies = {};

  @override
  void initState() {
    super.initState();
    _loadSavedStatuses();
  }

  Future<void> _loadSavedStatuses() async {
    final prefs = await SharedPreferences.getInstance();
    
    for (var job in widget.jobs) {
      final jobKey = _getJobKey(job);
      final isApplied = prefs.getBool('job_applied_$jobKey') ?? false;
      final remark = prefs.getString('job_remark_$jobKey') ?? '';
      
      setState(() {
        _appliedStatus[jobKey] = isApplied;
        _remarks[jobKey] = remark;
      });
    }
  }

  String _getJobKey(Map<String, dynamic> job) {
    return '${job['company_name']}_${job['job_url']}';
  }

  Future<void> _saveStatus(String jobKey, bool isApplied) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('job_applied_$jobKey', isApplied);
  }

  Future<void> _saveRemark(String jobKey, String remark) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('job_remark_$jobKey', remark);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      constraints: BoxConstraints(minWidth: 800),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 16),
          _buildJobsList(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
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

  Widget _buildJobsList() {
    if (widget.jobs.isEmpty) {
      return _buildEmptyState();
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: NeverScrollableScrollPhysics(),
      itemCount: widget.jobs.length,
      itemBuilder: (context, index) {
        final job = widget.jobs[index];
        return _buildJobRow(job);
      },
    );
  }

  Widget _buildJobRow(Map<String, dynamic> job) {
    final jobKey = _getJobKey(job);
    final bool isApplied = _appliedStatus[jobKey] ?? false;
    final String remark = _remarks[jobKey] ?? '';
    final bool isHovered = _hoveredCompanies.contains(jobKey);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppTheme.neutralGray200,
          width: 1,
        ),
      ),
      child: Row(
        children: [
          // Company Name with URL
          Expanded(
            flex: 3,
            child: MouseRegion(
              cursor: job['job_url'] != null 
                  ? SystemMouseCursors.click 
                  : SystemMouseCursors.basic,
              onEnter: (_) => job['job_url'] != null 
                  ? setState(() => _hoveredCompanies.add(jobKey))
                  : null,
              onExit: (_) => job['job_url'] != null 
                  ? setState(() => _hoveredCompanies.remove(jobKey))
                  : null,
              child: GestureDetector(
                onTap: job['job_url'] != null 
                    ? () => _launchUrl(job['job_url'])
                    : null,
                child: Text(
                  job['company_name'] ?? 'Unknown Company',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: isHovered ? Colors.blue : AppTheme.neutralGray800,
                        decoration: isHovered ? TextDecoration.underline : null,
                      ),
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
          
          // Post (Job Title)
          Expanded(
            flex: 3,
            child: Text(
              job['job_title'] ?? 'Unknown Position',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppTheme.neutralGray700,
                  ),
            ),
          ),
          
          // Contact
          Expanded(
            flex: 2,
            child: _buildContactInfo(job),
          ),
          
          // Already Applied Toggle
          SizedBox(
            width: 120,
            child: Switch(
              value: isApplied,
              onChanged: (bool value) {
                setState(() => _appliedStatus[jobKey] = value);
                _saveStatus(jobKey, value);
              },
              activeColor: Colors.green,
            ),
          ),
          
          // Remarks
          Expanded(
            flex: 2,
            child: GestureDetector(
              onTap: () => _showRemarksDialog(job),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppTheme.neutralGray50,
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(
                    color: AppTheme.neutralGray200,
                    width: 1,
                  ),
                ),
                child: Text(
                  remark.isEmpty ? 'Add note...' : remark,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: remark.isEmpty 
                            ? AppTheme.neutralGray400 
                            : AppTheme.neutralGray700,
                        fontStyle: remark.isEmpty 
                            ? FontStyle.italic 
                            : FontStyle.normal,
                      ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ),
          ),
        ],
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
          GestureDetector(
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
        if (email != null && phone != null)
          const SizedBox(height: 4),
        if (phone != null)
          GestureDetector(
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

  Future<void> _launchUrl(String urlString) async {
    try {
      final url = Uri.parse(urlString);
      if (await canLaunchUrl(url)) {
        await launchUrl(url);
      }
    } catch (e) {
      debugPrint('Error launching URL: $e');
    }
  }

  void _showRemarksDialog(Map<String, dynamic> job) {
    final jobKey = _getJobKey(job);
    final currentRemark = _remarks[jobKey] ?? '';
    final controller = TextEditingController(text: currentRemark);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Add Remarks'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${job['company_name']} - ${job['job_title']}',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Add your notes here...',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() => _remarks[jobKey] = controller.text);
              _saveRemark(jobKey, controller.text);
              Navigator.of(context).pop();
            },
            child: Text('Save'),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppTheme.neutralGray200,
          width: 1,
        ),
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
            'No saved jobs found',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppTheme.neutralGray600,
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Jobs you save will appear here',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.neutralGray500,
                ),
          ),
        ],
      ),
    );
  }
}