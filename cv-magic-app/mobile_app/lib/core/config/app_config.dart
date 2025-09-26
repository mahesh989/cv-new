class AppConfig {
  // Base URL for API and static assets
  static const String baseUrl = 'http://localhost:8000';

  // API endpoints
  static const String apiBaseUrl = '$baseUrl/api';

  // Video and media paths
  static const String videoPath = '$baseUrl/video';
  static const String introVideoPath = '$videoPath/info.mp4';

  // App constants
  static const String appName = 'CV Magic';
  static const String appVersion = '1.0.0';

  // Animation durations
  static const Duration defaultAnimationDuration = Duration(milliseconds: 300);
  static const Duration fastAnimationDuration = Duration(milliseconds: 150);
  static const Duration slowAnimationDuration = Duration(milliseconds: 600);

  // Spacing constants
  static const double defaultPadding = 16.0;
  static const double smallPadding = 8.0;
  static const double largePadding = 24.0;

  // Border radius
  static const double defaultBorderRadius = 12.0;
  static const double smallBorderRadius = 8.0;
  static const double largeBorderRadius = 16.0;

  // Video player settings
  static const double videoAspectRatio = 16 / 9;
  static const bool autoPlayVideo = false;
  static const bool loopVideo = true;

  // Feature flags
  static const bool enableVideoPlayer = true;
  static const bool enableAnimations = true;
  static const bool enableHapticFeedback = true;
}
