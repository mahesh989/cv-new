import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../core/theme/app_theme.dart';

class ResponsiveUtils {
  // Screen size breakpoints
  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 900;
  static const double desktopBreakpoint = 1200;

  // Check device types
  static bool isMobile(BuildContext context) {
    return MediaQuery.of(context).size.width < mobileBreakpoint;
  }

  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= mobileBreakpoint && width < tabletBreakpoint;
  }

  static bool isDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= tabletBreakpoint;
  }

  // Get responsive values
  static T getResponsiveValue<T>(
    BuildContext context, {
    required T mobile,
    T? tablet,
    T? desktop,
  }) {
    if (isDesktop(context) && desktop != null) return desktop;
    if (isTablet(context) && tablet != null) return tablet;
    return mobile;
  }

  // Get responsive padding
  static EdgeInsets getResponsivePadding(BuildContext context) {
    return getResponsiveValue(
      context,
      mobile: const EdgeInsets.all(16.0),
      tablet: const EdgeInsets.all(24.0),
      desktop: const EdgeInsets.all(32.0),
    );
  }

  // Get responsive margin
  static EdgeInsets getResponsiveMargin(BuildContext context) {
    return getResponsiveValue(
      context,
      mobile: const EdgeInsets.all(8.0),
      tablet: const EdgeInsets.all(12.0),
      desktop: const EdgeInsets.all(16.0),
    );
  }

  // Get responsive font sizes
  static double getResponsiveFontSize(
    BuildContext context, {
    required double mobile,
    double? tablet,
    double? desktop,
  }) {
    return getResponsiveValue(
      context,
      mobile: mobile,
      tablet: tablet ?? mobile * 1.1,
      desktop: desktop ?? mobile * 1.2,
    );
  }

  // Get responsive grid columns
  static int getResponsiveColumns(BuildContext context) {
    return getResponsiveValue(
      context,
      mobile: 1,
      tablet: 2,
      desktop: 3,
    );
  }

  // Get responsive card width
  static double getResponsiveCardWidth(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return getResponsiveValue(
      context,
      mobile: screenWidth - 32, // Full width minus padding
      tablet: (screenWidth - 64) / 2, // Half width for 2 columns
      desktop: (screenWidth - 96) / 3, // Third width for 3 columns
    );
  }

  // Check if device is in landscape mode
  static bool isLandscape(BuildContext context) {
    return MediaQuery.of(context).orientation == Orientation.landscape;
  }

  // Get safe area padding
  static EdgeInsets getSafeAreaPadding(BuildContext context) {
    return MediaQuery.of(context).padding;
  }

  // Get keyboard height
  static double getKeyboardHeight(BuildContext context) {
    return MediaQuery.of(context).viewInsets.bottom;
  }

  // Get app bar height for mobile
  static double getMobileAppBarHeight(BuildContext context) {
    return isMobile(context) ? 56.0 : kToolbarHeight;
  }

  // Get bottom navigation bar height
  static double getBottomNavHeight(BuildContext context) {
    return isMobile(context) ? 70.0 : 80.0;
  }

  // Check if touch device
  static bool isTouchDevice(BuildContext context) {
    return isMobile(context) || isTablet(context);
  }

  // Get responsive icon size
  static double getResponsiveIconSize(BuildContext context) {
    return getResponsiveValue(
      context,
      mobile: 24.0,
      tablet: 28.0,
      desktop: 32.0,
    );
  }

  // Get responsive button height
  static double getResponsiveButtonHeight(BuildContext context) {
    return getResponsiveValue(
      context,
      mobile: 48.0, // Minimum touch target for mobile
      tablet: 52.0,
      desktop: 56.0,
    );
  }

  // Get responsive dialog width
  static double getResponsiveDialogWidth(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    return getResponsiveValue(
      context,
      mobile: screenWidth * 0.9, // 90% of screen width
      tablet: screenWidth * 0.7, // 70% of screen width
      desktop: 600.0, // Fixed width for desktop
    );
  }
}

// Extension for easier context access
extension ResponsiveContext on BuildContext {
  bool get isMobile => ResponsiveUtils.isMobile(this);
  bool get isTablet => ResponsiveUtils.isTablet(this);
  bool get isDesktop => ResponsiveUtils.isDesktop(this);
  bool get isLandscape => ResponsiveUtils.isLandscape(this);
  bool get isTouchDevice => ResponsiveUtils.isTouchDevice(this);

  EdgeInsets get responsivePadding =>
      ResponsiveUtils.getResponsivePadding(this);
  EdgeInsets get responsiveMargin => ResponsiveUtils.getResponsiveMargin(this);
  EdgeInsets get safeAreaPadding => ResponsiveUtils.getSafeAreaPadding(this);

  double get keyboardHeight => ResponsiveUtils.getKeyboardHeight(this);
  double get mobileAppBarHeight => ResponsiveUtils.getMobileAppBarHeight(this);
  double get bottomNavHeight => ResponsiveUtils.getBottomNavHeight(this);
  double get responsiveIconSize => ResponsiveUtils.getResponsiveIconSize(this);
  double get responsiveButtonHeight =>
      ResponsiveUtils.getResponsiveButtonHeight(this);
}

/// 🎯 RESPONSIVE TYPOGRAPHY EXTENSION
/// Provides consistent font families, weights, and proportional scaling
/// across all devices while maintaining visual hierarchy
extension ResponsiveTypography on BuildContext {
  /// Get responsive scale factor based on screen width
  double get _typographyScale {
    final width = MediaQuery.of(this).size.width;
    if (width < 480) return 0.85; // Mobile - compact but readable
    if (width < 768) return 0.95; // Large mobile/small tablet
    if (width < 1024) return 1.0; // Tablet - baseline
    if (width < 1440) return 1.05; // Small desktop
    return 1.1; // Large desktop - generous spacing
  }

  // 🎯 DISPLAY & HERO TEXT - For landing pages and major headings
  TextStyle get displayLarge => GoogleFonts.manrope(
        fontSize: 32 * _typographyScale,
        fontWeight: FontWeight.w800,
        color: AppTheme.neutralGray900,
        letterSpacing: -0.8 * _typographyScale,
        height: 1.1,
      );

  TextStyle get displayMedium => GoogleFonts.manrope(
        fontSize: 28 * _typographyScale,
        fontWeight: FontWeight.w700,
        color: AppTheme.neutralGray900,
        letterSpacing: -0.6 * _typographyScale,
        height: 1.2,
      );

  TextStyle get displaySmall => GoogleFonts.manrope(
        fontSize: 24 * _typographyScale,
        fontWeight: FontWeight.w600,
        color: AppTheme.neutralGray800,
        letterSpacing: -0.4 * _typographyScale,
        height: 1.25,
      );

  // 🎯 HEADINGS - For content structure
  TextStyle get headingLarge => GoogleFonts.inter(
        fontSize: 22 * _typographyScale,
        fontWeight: FontWeight.w700,
        color: AppTheme.neutralGray900,
        letterSpacing: -0.3 * _typographyScale,
        height: 1.3,
      );

  TextStyle get headingMedium => GoogleFonts.inter(
        fontSize: 20 * _typographyScale,
        fontWeight: FontWeight.w600,
        color: AppTheme.neutralGray900,
        letterSpacing: -0.2 * _typographyScale,
        height: 1.35,
      );

  TextStyle get headingSmall => GoogleFonts.inter(
        fontSize: 18 * _typographyScale,
        fontWeight: FontWeight.w600,
        color: AppTheme.neutralGray800,
        letterSpacing: -0.1 * _typographyScale,
        height: 1.4,
      );

  // 📖 BODY TEXT - For readability and content
  TextStyle get bodyLarge => GoogleFonts.inter(
        fontSize: 16 * _typographyScale,
        fontWeight: FontWeight.w400,
        color: AppTheme.neutralGray700,
        letterSpacing: 0.0,
        height: 1.6,
      );

  TextStyle get bodyMedium => GoogleFonts.inter(
        fontSize: 15 * _typographyScale,
        fontWeight: FontWeight.w400,
        color: AppTheme.neutralGray600,
        letterSpacing: 0.0,
        height: 1.55,
      );

  TextStyle get bodySmall => GoogleFonts.inter(
        fontSize: 14 * _typographyScale,
        fontWeight: FontWeight.w400,
        color: AppTheme.neutralGray500,
        letterSpacing: 0.0,
        height: 1.5,
      );

  // 🏷️ LABELS & CAPTIONS - For metadata and UI elements
  TextStyle get labelLarge => GoogleFonts.inter(
        fontSize: 14 * _typographyScale,
        fontWeight: FontWeight.w500,
        color: AppTheme.neutralGray700,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.4,
      );

  TextStyle get labelMedium => GoogleFonts.inter(
        fontSize: 13 * _typographyScale,
        fontWeight: FontWeight.w500,
        color: AppTheme.neutralGray600,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.35,
      );

  TextStyle get labelSmall => GoogleFonts.inter(
        fontSize: 12 * _typographyScale,
        fontWeight: FontWeight.w500,
        color: AppTheme.neutralGray500,
        letterSpacing: 0.2 * _typographyScale,
        height: 1.3,
      );

  // 🔗 INTERACTIVE ELEMENTS - For buttons and links (STAR OF THE SHOW!)
  TextStyle get buttonLarge => GoogleFonts.inter(
        fontSize: 16 * _typographyScale,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.2 * _typographyScale,
        height: 1.2,
      );

  TextStyle get buttonMedium => GoogleFonts.inter(
        fontSize: 15 * _typographyScale,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.2,
      );

  TextStyle get buttonSmall => GoogleFonts.inter(
        fontSize: 14 * _typographyScale,
        fontWeight: FontWeight.w500,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.2,
      );

  // 💻 MONOSPACE - For code, technical content, CV filenames
  TextStyle get monoLarge => GoogleFonts.jetBrainsMono(
        fontSize: 16 * _typographyScale,
        fontWeight: FontWeight.w400,
        color: AppTheme.neutralGray700,
        letterSpacing: 0.0,
        height: 1.6,
      );

  TextStyle get monoMedium => GoogleFonts.jetBrainsMono(
        fontSize: 14 * _typographyScale,
        fontWeight: FontWeight.w400,
        color: AppTheme.neutralGray600,
        letterSpacing: 0.0,
        height: 1.5,
      );

  TextStyle get monoSmall => GoogleFonts.jetBrainsMono(
        fontSize: 12 * _typographyScale,
        fontWeight: FontWeight.w400,
        color: AppTheme.neutralGray500,
        letterSpacing: 0.0,
        height: 1.4,
      );

  // 🎨 ACCENT STYLES - For special emphasis
  TextStyle get accent => GoogleFonts.inter(
        fontSize: 15 * _typographyScale,
        fontWeight: FontWeight.w600,
        color: AppTheme.primaryTeal,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.4,
      );

  TextStyle get success => GoogleFonts.inter(
        fontSize: 14 * _typographyScale,
        fontWeight: FontWeight.w500,
        color: AppTheme.successGreen,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.4,
      );

  TextStyle get warning => GoogleFonts.inter(
        fontSize: 14 * _typographyScale,
        fontWeight: FontWeight.w500,
        color: AppTheme.warningOrange,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.4,
      );

  TextStyle get error => GoogleFonts.inter(
        fontSize: 14 * _typographyScale,
        fontWeight: FontWeight.w500,
        color: AppTheme.errorRed,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.4,
      );

  // 📝 CAPTIONS & METADATA - For timestamps, footnotes
  TextStyle get caption => GoogleFonts.inter(
        fontSize: 12 * _typographyScale,
        fontWeight: FontWeight.w400,
        color: AppTheme.neutralGray500,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.3,
      );

  TextStyle get captionBold => GoogleFonts.inter(
        fontSize: 12 * _typographyScale,
        fontWeight: FontWeight.w600,
        color: AppTheme.neutralGray600,
        letterSpacing: 0.1 * _typographyScale,
        height: 1.3,
      );

  // 🔗 LINK STYLES
  TextStyle get linkText => GoogleFonts.inter(
        fontSize: 15 * _typographyScale,
        fontWeight: FontWeight.w500,
        color: AppTheme.primaryTeal,
        letterSpacing: 0.0,
        height: 1.4,
        decoration: TextDecoration.underline,
        decorationColor: AppTheme.primaryTeal.withOpacity(0.6),
      );

  // 🌟 RESPONSIVE BUTTON STYLES - Consistent typography across devices
  ButtonStyle get primaryButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: AppTheme.primaryCosmic,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape:
            const RoundedRectangleBorder(borderRadius: AppTheme.buttonRadius),
        padding: EdgeInsets.symmetric(
          horizontal: 32 * _typographyScale,
          vertical: 18 * _typographyScale,
        ),
        textStyle: buttonLarge,
      );

  ButtonStyle get secondaryButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: AppTheme.neutralGray100,
        foregroundColor: AppTheme.neutralGray700,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape:
            const RoundedRectangleBorder(borderRadius: AppTheme.buttonRadius),
        padding: EdgeInsets.symmetric(
          horizontal: 28 * _typographyScale,
          vertical: 16 * _typographyScale,
        ),
        textStyle: buttonMedium,
      );

  ButtonStyle get compactButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: AppTheme.primaryTeal,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape:
            const RoundedRectangleBorder(borderRadius: AppTheme.buttonRadius),
        padding: EdgeInsets.symmetric(
          horizontal: 20 * _typographyScale,
          vertical: 12 * _typographyScale,
        ),
        textStyle: buttonSmall,
      );

  ButtonStyle get successButtonStyle => ElevatedButton.styleFrom(
        backgroundColor: AppTheme.successGreen,
        foregroundColor: Colors.white,
        elevation: 0,
        shadowColor: Colors.transparent,
        shape:
            const RoundedRectangleBorder(borderRadius: AppTheme.buttonRadius),
        padding: EdgeInsets.symmetric(
          horizontal: 32 * _typographyScale,
          vertical: 18 * _typographyScale,
        ),
        textStyle: buttonLarge,
      );

  ButtonStyle get outlineButtonStyle => OutlinedButton.styleFrom(
        foregroundColor: AppTheme.primaryCosmic,
        side: const BorderSide(color: AppTheme.primaryCosmic, width: 1.5),
        shape:
            const RoundedRectangleBorder(borderRadius: AppTheme.buttonRadius),
        padding: EdgeInsets.symmetric(
          horizontal: 28 * _typographyScale,
          vertical: 16 * _typographyScale,
        ),
        textStyle: buttonMedium,
      );

  ButtonStyle get ghostButtonStyle => TextButton.styleFrom(
        foregroundColor: AppTheme.primaryTeal,
        shape:
            const RoundedRectangleBorder(borderRadius: AppTheme.buttonRadius),
        padding: EdgeInsets.symmetric(
          horizontal: 20 * _typographyScale,
          vertical: 12 * _typographyScale,
        ),
        textStyle: buttonMedium,
      );
}
