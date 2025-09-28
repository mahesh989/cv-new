class AppConfig {
  // Base URL for API and static assets - handles different platforms
  static String get baseUrl {
    // For web and desktop, use localhost
    // For mobile devices/simulators, you might need to use your computer's IP
    // For testing, try: ifconfig (Mac/Linux) or ipconfig (Windows) to get your IP
    return 'http://localhost:8000';

    // Alternative configurations for different environments:
    // For Android Emulator: 'http://10.0.2.2:8000'
    // For iOS Simulator: 'http://localhost:8000' or 'http://127.0.0.1:8000'
    // For physical devices: 'http://YOUR_COMPUTER_IP:8000' (e.g., 'http://192.168.1.100:8000')
  }

  // API endpoints
  static String get apiBaseUrl => '$baseUrl/api';

  // Video and media paths (now using YouTube embed)
  static const String youtubeVideoId = 'a9IUom_eUGI';

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
