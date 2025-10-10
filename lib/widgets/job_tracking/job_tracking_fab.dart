///
/// Job Tracking Floating Action Button Widget
///
/// A reusable floating action button component with quick actions
/// for adding jobs and performing common tasks
///

import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../utils/responsive_utils.dart';

class JobTrackingFAB extends StatefulWidget {
  final VoidCallback onAddJob;
  final VoidCallback onQuickActions;
  final bool isExtended;

  const JobTrackingFAB({
    super.key,
    required this.onAddJob,
    required this.onQuickActions,
    this.isExtended = false,
  });

  @override
  State<JobTrackingFAB> createState() => _JobTrackingFABState();
}

class _JobTrackingFABState extends State<JobTrackingFAB>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotationAnimation;

  bool _isExpanded = false;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
  }

  void _initializeAnimations() {
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.1,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.elasticOut,
    ));

    _rotationAnimation = Tween<double>(
      begin: 0.0,
      end: 0.125, // 45 degrees
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Quick actions menu (when expanded)
        if (_isExpanded) _buildQuickActionsMenu(),

        // Main FAB
        _buildMainFAB(),
      ],
    );
  }

  Widget _buildMainFAB() {
    return Positioned(
      bottom: 16,
      right: 16,
      child: GestureDetector(
        onTap: _handleMainFABTap,
        onLongPress: _handleLongPress,
        child: AnimatedBuilder(
          animation: _animationController,
          builder: (context, child) {
            return Transform.scale(
              scale: _scaleAnimation.value,
              child: Transform.rotate(
                angle: _rotationAnimation.value * 2 * 3.14159,
                child: Container(
                  width: context.isMobile ? 56 : 64,
                  height: context.isMobile ? 56 : 64,
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius:
                        BorderRadius.circular(context.isMobile ? 28 : 32),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.2),
                        blurRadius: 12,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Material(
                    color: Colors.transparent,
                    child: InkWell(
                      onTap: _handleMainFABTap,
                      borderRadius:
                          BorderRadius.circular(context.isMobile ? 28 : 32),
                      child: Icon(
                        _isExpanded ? Icons.close : Icons.add,
                        size: context.isMobile ? 24 : 28,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildQuickActionsMenu() {
    return Positioned(
      bottom: 80,
      right: 16,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildQuickActionButton(
            icon: Icons.work,
            label: 'Add Job',
            onTap: widget.onAddJob,
            color: AppTheme.primaryTeal,
          ),
          const SizedBox(height: 12),
          _buildQuickActionButton(
            icon: Icons.upload,
            label: 'Import',
            onTap: () {
              // Handle import action
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                    content: Text('Import functionality coming soon!')),
              );
            },
            color: Colors.blue,
          ),
          const SizedBox(height: 12),
          _buildQuickActionButton(
            icon: Icons.download,
            label: 'Export',
            onTap: () {
              // Handle export action
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                    content: Text('Export functionality coming soon!')),
              );
            },
            color: Colors.green,
          ),
          const SizedBox(height: 12),
          _buildQuickActionButton(
            icon: Icons.settings,
            label: 'Settings',
            onTap: widget.onQuickActions,
            color: AppTheme.neutralGray600,
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    required Color color,
  }) {
    return GestureDetector(
      onTap: () {
        _toggleExpanded();
        onTap();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 20,
              color: color,
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                color: AppTheme.neutralGray700,
                fontSize: context.isMobile ? 12 : 14,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _handleMainFABTap() {
    if (_isExpanded) {
      _toggleExpanded();
    } else {
      widget.onAddJob();
    }
  }

  void _handleLongPress() {
    _toggleExpanded();
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
    });

    if (_isExpanded) {
      _animationController.forward();
    } else {
      _animationController.reverse();
    }
  }
}
