class AppConfig {
  // Backend API configuration
  static const String baseUrl = 'http://localhost:8000';

  // Authentication token (this should be managed by your auth service)
  static String authToken = '';

  // API endpoints
  static const String apiKeysEndpoint = '/api/api-keys';
  static const String aiEndpoint = '/api/ai';

  // Update auth token
  static void setAuthToken(String token) {
    authToken = token;
  }

  // Get auth token
  static String getAuthToken() {
    return authToken;
  }
}
