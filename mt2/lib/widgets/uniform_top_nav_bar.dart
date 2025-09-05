import 'package:flutter/material.dart';

class UniformTopNavBar extends StatelessWidget {
  final IconData? icon;
  final String title;
  final String? subtitle;
  final List<Widget>? actions;
  final Gradient? backgroundGradient;
  final EdgeInsetsGeometry? padding;

  const UniformTopNavBar({
    Key? key,
    this.icon,
    required this.title,
    this.subtitle,
    this.actions,
    this.backgroundGradient,
    this.padding,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding:
          padding ?? const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        gradient: backgroundGradient ??
            LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Colors.blue.shade600,
                Colors.purple.shade600,
              ],
            ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.15),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isMobile = constraints.maxWidth < 600;

          if (isMobile) {
            // Mobile: Stack vertically for better space usage
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    if (icon != null)
                      Padding(
                        padding: const EdgeInsets.only(right: 12),
                        child: Icon(icon, color: Colors.white, size: 24),
                      ),
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                        overflow: TextOverflow.ellipsis,
                        maxLines: 1,
                      ),
                    ),
                    if (actions != null)
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: actions!,
                      ),
                  ],
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    subtitle!,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white.withOpacity(0.9),
                    ),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 2,
                  ),
                ],
              ],
            );
          } else {
            // Desktop: Keep horizontal layout with proper constraints
            return Row(
              children: [
                if (icon != null)
                  Padding(
                    padding: const EdgeInsets.only(right: 12),
                    child: Icon(icon, color: Colors.white, size: 28),
                  ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                        overflow: TextOverflow.ellipsis,
                        maxLines: 1,
                      ),
                      if (subtitle != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            subtitle!,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.white.withOpacity(0.9),
                            ),
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                          ),
                        ),
                    ],
                  ),
                ),
                if (actions != null)
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: actions!,
                  ),
              ],
            );
          }
        },
      ),
    );
  }
}
