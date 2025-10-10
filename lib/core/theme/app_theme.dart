import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // 🎨 NEW PALETTE COLORS - Main Theme Colors
  static const Color primaryTeal = Color(0xFF1EBBD7); // Primary from palette
  static const Color secondaryBlue =
      Color(0xFF4B91F1); // Secondary from palette
  static const Color accentTeal = Color(0xFF1EBBD7); // Accent from palette
  static const Color backgroundWhite =
      Color(0xFFFFFFFF); // Background from palette

  // 🌟 COSMIC COLORS - Keep for buttons and small elements
  static const Color primaryCosmic = Color(0xFF6366F1); // Indigo
  static const Color primaryAurora = Color(0xFF8B5CF6); // Violet
  static const Color primaryNeon = Color(0xFF06B6D4); // Cyan
  static const Color primaryMagenta = Color(0xFFEC4899); // Pink
  static const Color primaryEmerald = Color(0xFF10B981); // Emerald
  static const Color primaryElectric = Color(0xFF3B82F6); // Blue

  // 🎨 ACCENT COLORS - Keep for small elements
  static const Color accentCoral = Color(0xFFFF6B6B);
  static const Color accentGolden = Color(0xFFFFD93D);
  static const Color accentMint = Color(0xFF6BCF7F);
  static const Color accentLavender = Color(0xFFB19CD9);
  static const Color accentPeach = Color(0xFFFFB347);
  static const Color accentSky = Color(0xFF87CEEB);

  // 🌈 NEON GLOW COLORS - Keep for effects
  static const Color neonPink = Color(0xFFFF1744);
  static const Color neonGreen = Color(0xFF00E676);
  static const Color neonBlue = Color(0xFF00B0FF);
  static const Color neonPurple = Color(0xFF7C4DFF);

  // 🌟 SEMANTIC COLORS - Enhanced
  static const Color successGreen = Color(0xFF22C55E); // Vibrant Success
  static const Color warningOrange = Color(0xFFF59E0B); // Bright Warning
  static const Color errorRed = Color(0xFFEF4444); // Clear Error
  static const Color infoBlue = Color(0xFF3B82F6); // Info Blue

  // 🎭 NEUTRAL COLORS - Sophisticated
  static const Color neutralGray50 = Color(0xFFFAFAFA);
  static const Color neutralGray100 = Color(0xFFF5F5F5);
  static const Color neutralGray200 = Color(0xFFE5E5E5);
  static const Color neutralGray300 = Color(0xFFD4D4D4);
  static const Color neutralGray400 = Color(0xFFA3A3A3);
  static const Color neutralGray500 = Color(0xFF737373);
  static const Color neutralGray600 = Color(0xFF525252);
  static const Color neutralGray700 = Color(0xFF404040);
  static const Color neutralGray800 = Color(0xFF262626);
  static const Color neutralGray900 = Color(0xFF171717);

  // 🌈 NEW PALETTE GRADIENTS - Main theme gradients
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryTeal, secondaryBlue],
    stops: [0.0, 1.0],
  );

  static const LinearGradient secondaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [secondaryBlue, primaryTeal],
    stops: [0.0, 1.0],
  );

  static const LinearGradient accentGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [accentTeal, secondaryBlue],
    stops: [0.0, 1.0],
  );

  // 🌟 COSMIC GRADIENTS - Keep for buttons and effects
  static const LinearGradient cosmicGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryCosmic, primaryAurora, primaryMagenta],
    stops: [0.0, 0.5, 1.0],
  );

  static const LinearGradient oceanGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryNeon, primaryElectric, primaryCosmic],
    stops: [0.0, 0.6, 1.0],
  );

  static const LinearGradient sunsetGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [accentPeach, accentCoral, primaryMagenta],
    stops: [0.0, 0.7, 1.0],
  );

  static const LinearGradient forestGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [accentMint, primaryEmerald, primaryNeon],
    stops: [0.0, 0.5, 1.0],
  );

  static const LinearGradient royalGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryCosmic, accentLavender, primaryAurora],
    stops: [0.0, 0.4, 1.0],
  );

  // 🌌 MAGICAL BACKGROUND GRADIENTS
  static const LinearGradient backgroundGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFFF8FAFF), // Soft white
      Color(0xFFF3F4FF), // Light cosmic
      Color(0xFFEEF2FF), // Deeper cosmic
      Color(0xFFE0E7FF), // Rich cosmic
    ],
    stops: [0.0, 0.3, 0.7, 1.0],
  );

  // ✨ GLOWING CARD GRADIENTS
  static const LinearGradient cardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Colors.white, Color(0xFFFEFEFF), Color(0xFFFAFBFF)],
    stops: [0.0, 0.5, 1.0],
  );

  static const LinearGradient glowCardGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFFFFFFF), Color(0xFFF8FAFF), Color(0xFFF3F4FF)],
    stops: [0.0, 0.6, 1.0],
  );

  // 🌟 SPECTACULAR SHADOWS WITH GLOW EFFECTS
  static List<BoxShadow> get cardShadow => [
        BoxShadow(
          color: primaryCosmic.withOpacity(0.12),
          blurRadius: 24,
          offset: const Offset(0, 8),
          spreadRadius: 0,
        ),
        BoxShadow(
          color: primaryAurora.withOpacity(0.08),
          blurRadius: 40,
          offset: const Offset(0, 16),
          spreadRadius: 0,
        ),
        BoxShadow(
          color: Colors.black.withOpacity(0.04),
          blurRadius: 6,
          offset: const Offset(0, 2),
          spreadRadius: 0,
        ),
      ];

  static List<BoxShadow> get elevatedShadow => [
        BoxShadow(
          color: primaryCosmic.withOpacity(0.2),
          blurRadius: 40,
          offset: const Offset(0, 12),
          spreadRadius: 0,
        ),
        BoxShadow(
          color: primaryMagenta.withOpacity(0.15),
          blurRadius: 60,
          offset: const Offset(0, 20),
          spreadRadius: 0,
        ),
        BoxShadow(
          color: Colors.black.withOpacity(0.08),
          blurRadius: 12,
          offset: const Offset(0, 4),
          spreadRadius: 0,
        ),
      ];

  static List<BoxShadow> get glowShadow => [
        BoxShadow(
          color: primaryNeon.withOpacity(0.3),
          blurRadius: 30,
          offset: const Offset(0, 0),
          spreadRadius: 2,
        ),
        BoxShadow(
          color: primaryCosmic.withOpacity(0.2),
          blurRadius: 20,
          offset: const Offset(0, 10),
          spreadRadius: 0,
        ),
      ];

  static List<BoxShadow> get neonGlow => [
        BoxShadow(
          color: neonBlue.withOpacity(0.4),
          blurRadius: 20,
          offset: const Offset(0, 0),
          spreadRadius: 3,
        ),
        BoxShadow(
          color: neonPurple.withOpacity(0.3),
          blurRadius: 40,
          offset: const Offset(0, 0),
          spreadRadius: 1,
        ),
      ];

  // 🎨 BEAUTIFUL BORDER RADIUS
  static const BorderRadius cardRadius = BorderRadius.all(Radius.circular(20));
  static const BorderRadius buttonRadius =
      BorderRadius.all(Radius.circular(16));
  static const BorderRadius inputRadius = BorderRadius.all(Radius.circular(14));
  static const BorderRadius pillRadius = BorderRadius.all(Radius.circular(50));

  // ⚡ SMOOTH ANIMATIONS
  static const Duration ultraFastAnimation = Duration(milliseconds: 150);
  static const Duration fastAnimation = Duration(milliseconds: 250);
  static const Duration normalAnimation = Duration(milliseconds: 400);
  static const Duration slowAnimation = Duration(milliseconds: 600);
  static const Duration dramaticAnimation = Duration(milliseconds: 800);

  // 🎭 STUNNING ANIMATION CURVES
  static const Curve defaultCurve = Curves.easeOutCubic;
  static const Curve bounceCurve = Curves.elasticOut;
  static const Curve smoothCurve = Curves.easeInOutCubic;
  static const Curve dramaticCurve = Curves.easeOutBack;

  // 🎯 CLEAN TYPOGRAPHY SYSTEM - Works everywhere without context

  // Display & Hero Text
  static TextStyle get displayLarge => GoogleFonts.manrope(
        fontSize: 32,
        fontWeight: FontWeight.w800,
        color: neutralGray900,
        letterSpacing: -0.8,
        height: 1.1,
      );

  static TextStyle get displayMedium => GoogleFonts.manrope(
        fontSize: 28,
        fontWeight: FontWeight.w700,
        color: neutralGray900,
        letterSpacing: -0.6,
        height: 1.2,
      );

  static TextStyle get displaySmall => GoogleFonts.manrope(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        color: neutralGray800,
        letterSpacing: -0.4,
        height: 1.25,
      );

  // Headings
  static TextStyle get headingLarge => GoogleFonts.inter(
        fontSize: 22,
        fontWeight: FontWeight.w700,
        color: neutralGray900,
        letterSpacing: -0.3,
        height: 1.3,
      );

  static TextStyle get headingMedium => GoogleFonts.inter(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: neutralGray900,
        letterSpacing: -0.2,
        height: 1.35,
      );

  static TextStyle get headingSmall => GoogleFonts.inter(
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: neutralGray800,
        letterSpacing: -0.1,
        height: 1.4,
      );

  // Body Text
  static TextStyle get bodyLarge => GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: neutralGray700,
        letterSpacing: 0.0,
        height: 1.6,
      );

  static TextStyle get bodyMedium => GoogleFonts.inter(
        fontSize: 15,
        fontWeight: FontWeight.w400,
        color: neutralGray600,
        letterSpacing: 0.0,
        height: 1.55,
      );

  static TextStyle get bodySmall => GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: neutralGray500,
        letterSpacing: 0.0,
        height: 1.5,
      );

  // Labels & UI
  static TextStyle get labelLarge => GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: neutralGray700,
        letterSpacing: 0.1,
        height: 1.4,
      );

  static TextStyle get labelMedium => GoogleFonts.inter(
        fontSize: 13,
        fontWeight: FontWeight.w500,
        color: neutralGray600,
        letterSpacing: 0.1,
        height: 1.35,
      );

  static TextStyle get labelSmall => GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: neutralGray500,
        letterSpacing: 0.2,
        height: 1.3,
      );

  // Interactive Elements
  static TextStyle get buttonLarge => GoogleFonts.inter(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.2,
        height: 1.2,
      );

  static TextStyle get buttonMedium => GoogleFonts.inter(
        fontSize: 15,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.1,
        height: 1.2,
      );

  static TextStyle get buttonSmall => GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.1,
        height: 1.2,
      );

  static TextStyle get linkText => GoogleFonts.inter(
        fontSize: 15,
        fontWeight: FontWeight.w500,
        color: primaryTeal,
        letterSpacing: 0.0,
        height: 1.4,
        decoration: TextDecoration.underline,
        decorationColor: primaryTeal.withOpacity(0.6),
      );

  // Monospace
  static TextStyle get monoLarge => GoogleFonts.jetBrainsMono(
        fontSize: 16,
        fontWeight: FontWeight.w400,
        color: neutralGray700,
        letterSpacing: 0.0,
        height: 1.6,
      );

  static TextStyle get monoMedium => GoogleFonts.jetBrainsMono(
        fontSize: 14,
        fontWeight: FontWeight.w400,
        color: neutralGray600,
        letterSpacing: 0.0,
        height: 1.5,
      );

  static TextStyle get monoSmall => GoogleFonts.jetBrainsMono(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        color: neutralGray500,
        letterSpacing: 0.0,
        height: 1.4,
      );

  // Accent Styles
  static TextStyle get accent => GoogleFonts.inter(
        fontSize: 15,
        fontWeight: FontWeight.w600,
        color: primaryTeal,
        letterSpacing: 0.1,
        height: 1.4,
      );

  static TextStyle get success => GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: successGreen,
        letterSpacing: 0.1,
        height: 1.4,
      );

  static TextStyle get warning => GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: warningOrange,
        letterSpacing: 0.1,
        height: 1.4,
      );

  static TextStyle get error => GoogleFonts.inter(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: errorRed,
        letterSpacing: 0.1,
        height: 1.4,
      );

  static TextStyle get caption => GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w400,
        color: neutralGray500,
        letterSpacing: 0.1,
        height: 1.3,
      );

  static TextStyle get captionBold => GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w600,
        color: neutralGray600,
        letterSpacing: 0.1,
        height: 1.3,
      );

  // Legacy compatibility
  static TextStyle get buttonText => buttonMedium;

  // 🎯 SPECTACULAR BUTTON STYLES - Enhanced with professional typography
  static ButtonStyle get primaryButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: primaryCosmic,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape: const RoundedRectangleBorder(borderRadius: buttonRadius),
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
        textStyle: buttonLarge.copyWith(color: Colors.white),
      );

  static ButtonStyle get secondaryButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: neutralGray100,
        foregroundColor: neutralGray700,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape: const RoundedRectangleBorder(borderRadius: buttonRadius),
        padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
        textStyle: buttonMedium.copyWith(color: neutralGray700),
      );

  static ButtonStyle get successButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: successGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape: const RoundedRectangleBorder(borderRadius: buttonRadius),
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
        textStyle: buttonLarge.copyWith(color: Colors.white),
      );

  static ButtonStyle get dangerButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: errorRed,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape: const RoundedRectangleBorder(borderRadius: buttonRadius),
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
        textStyle: buttonLarge.copyWith(color: Colors.white),
      );

  static ButtonStyle get cosmicButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: primaryMagenta,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape: const RoundedRectangleBorder(borderRadius: buttonRadius),
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
        textStyle: buttonLarge.copyWith(color: Colors.white),
      );

  // 🎨 ADDITIONAL BUTTON VARIANTS - For variety and hierarchy
  static ButtonStyle get compactButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: primaryTeal,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape: const RoundedRectangleBorder(borderRadius: buttonRadius),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        textStyle: buttonSmall.copyWith(color: Colors.white),
      );

  static ButtonStyle get outlineButtonStyle => OutlinedButton.styleFrom(
        foregroundColor: primaryCosmic,
        side: const BorderSide(color: primaryCosmic, width: 1.5),
        shape: const RoundedRectangleBorder(borderRadius: buttonRadius),
        padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 16),
        textStyle: buttonMedium.copyWith(color: primaryCosmic),
      );

  static ButtonStyle get ghostButtonStyle => TextButton.styleFrom(
        foregroundColor: primaryTeal,
        shape: const RoundedRectangleBorder(borderRadius: buttonRadius),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        textStyle: buttonMedium.copyWith(color: primaryTeal),
      );

  // 🎨 GORGEOUS INPUT DECORATION
  static InputDecoration getInputDecoration({
    required String hintText,
    Widget? prefixIcon,
    Widget? suffixIcon,
  }) =>
      InputDecoration(
        hintText: hintText,
        prefixIcon: prefixIcon,
        suffixIcon: suffixIcon,
        border: OutlineInputBorder(
          borderRadius: inputRadius,
          borderSide: BorderSide(color: neutralGray300, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: inputRadius,
          borderSide: BorderSide(color: neutralGray300, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: inputRadius,
          borderSide: const BorderSide(color: primaryTeal, width: 2.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: inputRadius,
          borderSide: const BorderSide(color: errorRed, width: 2),
        ),
        filled: true,
        fillColor: Colors.white,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        hintStyle: bodyMedium.copyWith(color: neutralGray400),
        labelStyle: labelLarge.copyWith(color: neutralGray600),
      );

  // 🏷️ VIBRANT CHIP COLORS
  static Map<String, Color> get chipColors => {
        'matched': const Color(0xFFDCFDF7), // Emerald 50
        'missed': const Color(0xFFFEE2E2), // Red 50
      };

  static Map<String, Color> get chipTextColors => {
        'matched': const Color(0xFF047857), // Emerald 700
        'missed': const Color(0xFFB91C1C), // Red 700
      };

  // 🌈 STATUS COLORS WITH PERSONALITY
  static Color getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'new':
      case 'recent':
        return successGreen;
      case 'pending':
        return accentGolden;
      case 'completed':
        return primaryCosmic;
      case 'excellent':
        return primaryEmerald;
      case 'warning':
        return warningOrange;
      case 'error':
      case 'failed':
        return errorRed;
      case 'magic':
        return primaryMagenta;
      default:
        return neutralGray500;
    }
  }

  // ✨ MAGICAL HELPER METHODS
  static Widget createGradientContainer({
    required Widget child,
    LinearGradient? gradient,
    BorderRadius? borderRadius,
    List<BoxShadow>? boxShadow,
    EdgeInsets? padding,
  }) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        gradient: gradient ?? cosmicGradient,
        borderRadius: borderRadius ?? cardRadius,
        boxShadow: boxShadow ?? elevatedShadow,
      ),
      child: child,
    );
  }

  static Widget createCard({
    required Widget child,
    EdgeInsets? padding,
    EdgeInsets? margin,
    Color? color,
    bool glowing = false,
  }) {
    return Container(
      margin: margin,
      padding: padding ?? const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: color ?? Colors.white,
        borderRadius: cardRadius,
        boxShadow: glowing ? glowShadow : cardShadow,
        border: Border.all(
          color: glowing ? primaryNeon.withOpacity(0.3) : neutralGray200,
          width: glowing ? 2 : 1,
        ),
        gradient: glowing ? glowCardGradient : null,
      ),
      child: child,
    );
  }

  static Widget createGradientButton({
    required String text,
    required VoidCallback onPressed,
    double? width,
    double? height,
    bool isLoading = false,
    IconData? icon,
  }) {
    return Container(
      width: width,
      height: height ?? 48,
      decoration: BoxDecoration(
        gradient: primaryGradient,
        borderRadius: BorderRadius.circular(12),
      ),
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.transparent,
          shadowColor: Colors.transparent,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        child: FittedBox(
          fit: BoxFit.scaleDown,
          alignment: Alignment.center,
          child: isLoading
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                  ),
                )
              : Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (icon != null) ...[
                      Icon(icon, color: Colors.white, size: 20),
                      const SizedBox(width: 8),
                    ],
                    Text(
                      text,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      softWrap: false,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
        ),
      ),
    );
  }

  static Widget createGlowingCard({
    required Widget child,
    EdgeInsets? padding,
    EdgeInsets? margin,
    LinearGradient? gradient,
  }) {
    return Container(
      margin: margin,
      padding: padding ?? const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: gradient ?? cosmicGradient,
        borderRadius: cardRadius,
        boxShadow: neonGlow,
      ),
      child: child,
    );
  }

  // 🎨 ANIMATED BACKGROUND
  static Widget createAnimatedBackground({required Widget child}) {
    return Container(
      decoration: const BoxDecoration(gradient: backgroundGradient),
      child: child,
    );
  }

  // Theme
  static ThemeData get lightTheme => ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: primaryTeal,
          brightness: Brightness.light,
        ),
        textTheme: GoogleFonts.interTextTheme(),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
        ),
      );
}
