import 'package:flutter/material.dart';
import '../utils/responsive_utils.dart';

class SectionCard extends StatelessWidget {
  final Widget child;
  const SectionCard({super.key, required this.child});
  @override
  Widget build(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: 1000),
        child: Container(
          margin: EdgeInsets.symmetric(
            horizontal: context.isMobile ? 0 : 0,
          ),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.06),
                blurRadius: 20,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
