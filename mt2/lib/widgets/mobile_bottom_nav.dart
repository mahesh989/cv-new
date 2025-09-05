import 'package:flutter/material.dart';
import '../utils/responsive_utils.dart';
import '../theme/app_theme.dart';

class TabData {
  final IconData icon;
  final String label;
  final LinearGradient gradient;
  final Color color;

  TabData({
    required this.icon,
    required this.label,
    required this.gradient,
    required this.color,
  });
}

class MobileBottomNav extends StatefulWidget {
  final int currentIndex;
  final Function(int) onTabTapped;
  final List<TabData> tabData;

  const MobileBottomNav({
    super.key,
    required this.currentIndex,
    required this.onTabTapped,
    required this.tabData,
  });

  @override
  State<MobileBottomNav> createState() => _MobileBottomNavState();
}

class _MobileBottomNavState extends State<MobileBottomNav>
    with TickerProviderStateMixin {
  late AnimationController _animationController;
  late List<AnimationController> _tabAnimationControllers;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );

    _tabAnimationControllers = List.generate(
      widget.tabData.length,
      (index) => AnimationController(
        duration: const Duration(milliseconds: 200),
        vsync: this,
      ),
    );

    // Animate in the current tab
    if (widget.currentIndex < _tabAnimationControllers.length) {
      _tabAnimationControllers[widget.currentIndex].forward();
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    for (var controller in _tabAnimationControllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  void didUpdateWidget(MobileBottomNav oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.currentIndex != widget.currentIndex) {
      // Animate out old tab
      if (oldWidget.currentIndex < _tabAnimationControllers.length) {
        _tabAnimationControllers[oldWidget.currentIndex].reverse();
      }
      // Animate in new tab
      if (widget.currentIndex < _tabAnimationControllers.length) {
        _tabAnimationControllers[widget.currentIndex].forward();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomPadding = MediaQuery.of(context).padding.bottom;

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 20,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        top: false, // Don't apply safe area to top
        child: Container(
          height: context.isMobile ? 60 : 70,
          padding: EdgeInsets.only(
            left: context.isMobile ? 8 : 16,
            right: context.isMobile ? 8 : 16,
            top: context.isMobile ? 8 : 12,
            bottom: context.isMobile ? 8 : 12,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: List.generate(
              widget.tabData.length,
              (index) => _buildNavItem(context, index),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNavItem(BuildContext context, int index) {
    final tabData = widget.tabData[index];
    final isSelected = widget.currentIndex == index;
    final animationController = _tabAnimationControllers[index];

    return Expanded(
      child: GestureDetector(
        onTap: () => widget.onTabTapped(index),
        behavior: HitTestBehavior.opaque,
        child: Container(
          margin: EdgeInsets.symmetric(
            horizontal: context.isMobile ? 1 : 4,
          ),
          child: AnimatedBuilder(
            animation: animationController,
            builder: (context, child) {
              return Column(
                mainAxisSize: MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Icon with animation
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding: EdgeInsets.all(context.isMobile ? 4 : 6),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      gradient: isSelected
                          ? tabData.gradient
                          : const LinearGradient(
                              colors: [
                                Colors.transparent,
                                Colors.transparent,
                              ],
                            ),
                    ),
                    child: Icon(
                      tabData.icon,
                      size: context.isMobile ? 20 : 24,
                      color: isSelected ? Colors.white : Colors.grey[600],
                    ),
                  ),

                  // Label - always show but with smaller font on mobile
                  const SizedBox(height: 2),
                  AnimatedOpacity(
                    duration: const Duration(milliseconds: 200),
                    opacity: isSelected ? 1.0 : 0.7,
                    child: Text(
                      tabData.label,
                      style: TextStyle(
                        fontSize: context.isMobile ? 9 : 11,
                        fontWeight:
                            isSelected ? FontWeight.w600 : FontWeight.w500,
                        color: isSelected ? tabData.color : Colors.grey[600],
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

// Mobile-optimized floating action button for primary actions
class MobileFloatingActionButton extends StatelessWidget {
  final VoidCallback onPressed;
  final IconData icon;
  final String tooltip;
  final LinearGradient? gradient;

  const MobileFloatingActionButton({
    super.key,
    required this.onPressed,
    required this.icon,
    required this.tooltip,
    this.gradient,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: context.isMobile ? 56 : 64,
      height: context.isMobile ? 56 : 64,
      decoration: BoxDecoration(
        gradient: gradient ?? AppTheme.primaryGradient,
        borderRadius: BorderRadius.circular(context.isMobile ? 28 : 32),
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
          onTap: onPressed,
          borderRadius: BorderRadius.circular(context.isMobile ? 28 : 32),
          child: Icon(
            icon,
            size: context.isMobile ? 24 : 28,
            color: Colors.white,
          ),
        ),
      ),
    );
  }
}
