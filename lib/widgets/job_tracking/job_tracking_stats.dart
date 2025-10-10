///
/// Job Tracking Stats Widget
///
/// A reusable stats component that displays job application statistics
/// with animated counters and progress indicators
///

import 'package:flutter/material.dart';
import '../../utils/responsive_utils.dart';

class JobTrackingStats extends StatefulWidget {
  final int totalJobs;
  final int appliedJobs;
  final int interviewJobs;
  final int rejectedJobs;
  final VoidCallback? onStatsTap;

  const JobTrackingStats({
    super.key,
    required this.totalJobs,
    required this.appliedJobs,
    required this.interviewJobs,
    required this.rejectedJobs,
    this.onStatsTap,
  });

  @override
  State<JobTrackingStats> createState() => _JobTrackingStatsState();
}

class _JobTrackingStatsState extends State<JobTrackingStats>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );

    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: const Interval(0.0, 0.6, curve: Curves.easeOut),
    ));

    _scaleAnimation = Tween<double>(
      begin: 0.8,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: const Interval(0.2, 1.0, curve: Curves.elasticOut),
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
    return AnimatedBuilder(
      animation: _animationController,
      builder: (context, child) {
        return FadeTransition(
          opacity: _fadeAnimation,
          child: ScaleTransition(
            scale: _scaleAnimation,
            child: _buildStatsGrid(),
          ),
        );
      },
    );
  }

  Widget _buildStatsGrid() {
    return Row(
      children: [
        Expanded(
          child: _buildStatCard(
            title: 'Total',
            value: widget.totalJobs,
            icon: Icons.work_outline,
            color: Colors.white,
            gradient: LinearGradient(
              colors: [
                Colors.white.withValues(alpha: 0.2),
                Colors.white.withValues(alpha: 0.1),
              ],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            title: 'Applied',
            value: widget.appliedJobs,
            icon: Icons.send,
            color: Colors.blue,
            gradient: LinearGradient(
              colors: [
                Colors.blue.withValues(alpha: 0.8),
                Colors.blue.withValues(alpha: 0.6),
              ],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            title: 'Interview',
            value: widget.interviewJobs,
            icon: Icons.people,
            color: Colors.orange,
            gradient: LinearGradient(
              colors: [
                Colors.orange.withValues(alpha: 0.8),
                Colors.orange.withValues(alpha: 0.6),
              ],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildStatCard(
            title: 'Rejected',
            value: widget.rejectedJobs,
            icon: Icons.close,
            color: Colors.red,
            gradient: LinearGradient(
              colors: [
                Colors.red.withValues(alpha: 0.8),
                Colors.red.withValues(alpha: 0.6),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required int value,
    required IconData icon,
    required Color color,
    required LinearGradient gradient,
  }) {
    return GestureDetector(
      onTap: widget.onStatsTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: gradient,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: Colors.white.withValues(alpha: 0.2),
            width: 1,
          ),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: Colors.white,
              size: context.isMobile ? 20 : 24,
            ),
            const SizedBox(height: 8),
            Text(
              value.toString(),
              style: TextStyle(
                color: Colors.white,
                fontSize: context.isMobile ? 18 : 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: TextStyle(
                color: Colors.white.withValues(alpha: 0.9),
                fontSize: context.isMobile ? 10 : 12,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
