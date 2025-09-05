import 'package:flutter/material.dart';

void showAnimatedDialog(BuildContext context, Widget child) {
  showGeneralDialog(
    context: context,
    barrierDismissible: true,
    barrierLabel: MaterialLocalizations.of(context).modalBarrierDismissLabel,
    pageBuilder: (_, __, ___) => child,
    transitionBuilder: (_, animation, __, widget) {
      return ScaleTransition(
        scale: CurvedAnimation(parent: animation, curve: Curves.easeOutBack),
        child: FadeTransition(
          opacity: animation,
          child: widget,
        ),
      );
    },
    transitionDuration: const Duration(milliseconds: 300),
  );
}



