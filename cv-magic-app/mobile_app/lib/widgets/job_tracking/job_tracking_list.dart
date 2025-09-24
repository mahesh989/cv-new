///
/// Job Tracking List Widget
///
/// A reusable list component for displaying job applications
/// with status indicators, actions, and animations
///

import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../utils/responsive_utils.dart';

class JobTrackingList extends StatefulWidget {
  final List<Map<String, dynamic>> jobs;
  final bool isLoading;
  final Function(Map<String, dynamic>) onJobTap;
  final Function(Map<String, dynamic>) onJobEdit;
  final Function(Map<String, dynamic>) onJobDelete;
  final Function(Map<String, dynamic>, String) onStatusUpdate;

  const JobTrackingList({
    super.key,
    required this.jobs,
    required this.isLoading,
    required this.onJobTap,
    required this.onJobEdit,
    required this.onJobDelete,
    required this.onStatusUpdate,
  });

  @override
  State<JobTrackingList> createState() => _JobTrackingListState();
}

class _JobTrackingListState extends State<JobTrackingList>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeOut,
    ));

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.isLoading) {
      return _buildLoadingState();
    }

    if (widget.jobs.isEmpty) {
      return _buildEmptyState();
    }

    return FadeTransition(
      opacity: _fadeAnimation,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Job Applications (${widget.jobs.length})',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.neutralGray700,
                ),
          ),
          const SizedBox(height: 16),
          _buildJobList(),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(AppTheme.primaryTeal),
          ),
          const SizedBox(height: 16),
          Text(
            'Loading jobs...',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.neutralGray600,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppTheme.neutralGray100,
              shape: BoxShape.circle,
            ),
            child: Icon(
              Icons.work_outline,
              size: 48,
              color: AppTheme.neutralGray400,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'No jobs found',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppTheme.neutralGray600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Add your first job application to get started',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.neutralGray500,
                ),
            textAlign: TextAlign.center,
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
      itemBuilder: (context, index) {
        final job = widget.jobs[index];
        return _buildJobCard(job, index);
      },
    );
  }

  Widget _buildJobCard(Map<String, dynamic> job, int index) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: AppTheme.createCard(
        child: InkWell(
          onTap: () => widget.onJobTap(job),
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header row with title and status
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            job['title'] ?? 'Unknown Title',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: AppTheme.neutralGray800,
                                ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            job['company'] ?? 'Unknown Company',
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  color: AppTheme.neutralGray600,
                                ),
                          ),
                        ],
                      ),
                    ),
                    _buildStatusChip(job['status'] ?? 'Unknown'),
                  ],
                ),

                const SizedBox(height: 12),

                // Job details
                _buildJobDetails(job),

                const SizedBox(height: 12),

                // Action buttons
                _buildActionButtons(job),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    Color statusColor;
    Color backgroundColor;

    switch (status.toLowerCase()) {
      case 'applied':
        statusColor = Colors.blue;
        backgroundColor = Colors.blue.withValues(alpha: 0.1);
        break;
      case 'interview':
        statusColor = Colors.orange;
        backgroundColor = Colors.orange.withValues(alpha: 0.1);
        break;
      case 'rejected':
        statusColor = Colors.red;
        backgroundColor = Colors.red.withValues(alpha: 0.1);
        break;
      case 'offered':
        statusColor = Colors.green;
        backgroundColor = Colors.green.withValues(alpha: 0.1);
        break;
      default:
        statusColor = AppTheme.neutralGray500;
        backgroundColor = AppTheme.neutralGray100;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: statusColor.withValues(alpha: 0.3),
          width: 1,
        ),
      ),
      child: Text(
        status,
        style: TextStyle(
          color: statusColor,
          fontSize: context.isMobile ? 10 : 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildJobDetails(Map<String, dynamic> job) {
    return Row(
      children: [
        if (job['location'] != null) ...[
          Icon(
            Icons.location_on,
            size: 16,
            color: AppTheme.neutralGray500,
          ),
          const SizedBox(width: 4),
          Text(
            job['location'],
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.neutralGray600,
                ),
          ),
          const SizedBox(width: 16),
        ],
        if (job['salary'] != null) ...[
          Icon(
            Icons.attach_money,
            size: 16,
            color: AppTheme.neutralGray500,
          ),
          const SizedBox(width: 4),
          Text(
            job['salary'],
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.neutralGray600,
                ),
          ),
        ],
      ],
    );
  }

  Widget _buildActionButtons(Map<String, dynamic> job) {
    return Row(
      children: [
        Expanded(
          child: _buildActionButton(
            icon: Icons.edit,
            label: 'Edit',
            onTap: () => widget.onJobEdit(job),
            color: AppTheme.primaryTeal,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildActionButton(
            icon: Icons.delete,
            label: 'Delete',
            onTap: () => widget.onJobDelete(job),
            color: Colors.red,
          ),
        ),
        const SizedBox(width: 8),
        _buildStatusDropdown(job),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    required Color color,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: color.withValues(alpha: 0.3),
            width: 1,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 16,
              color: color,
            ),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: context.isMobile ? 10 : 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusDropdown(Map<String, dynamic> job) {
    final statuses = ['Applied', 'Interview', 'Rejected', 'Offered'];
    final currentStatus = job['status'] ?? 'Applied';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: AppTheme.neutralGray100,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: AppTheme.neutralGray300,
          width: 1,
        ),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: currentStatus,
          isDense: true,
          style: TextStyle(
            color: AppTheme.neutralGray700,
            fontSize: context.isMobile ? 10 : 12,
            fontWeight: FontWeight.w500,
          ),
          items: statuses.map((String status) {
            return DropdownMenuItem<String>(
              value: status,
              child: Text(status),
            );
          }).toList(),
          onChanged: (String? newStatus) {
            if (newStatus != null && newStatus != currentStatus) {
              widget.onStatusUpdate(job, newStatus);
            }
          },
        ),
      ),
    );
  }
}
