import 'package:flutter/material.dart';
import '../widgets/api_key_error_notification.dart';

class APIKeyErrorHandler {
  static void handleAPIKeyError(
    BuildContext context, {
    required String provider,
    required String providerDisplayName,
    String? errorMessage,
    VoidCallback? onConfigureAPIKey,
  }) {
    // Show error notification
    APIKeyErrorSnackBar.show(
      context,
      provider: provider,
      providerDisplayName: providerDisplayName,
      errorMessage: errorMessage,
      onConfigureAPIKey: onConfigureAPIKey,
    );
  }

  static void handleAPIKeyRequired(
    BuildContext context, {
    required String provider,
    required String providerDisplayName,
    VoidCallback? onConfigureAPIKey,
  }) {
    handleAPIKeyError(
      context,
      provider: provider,
      providerDisplayName: providerDisplayName,
      errorMessage: 'API key is required to use this provider',
      onConfigureAPIKey: onConfigureAPIKey,
    );
  }

  static void handleAPIKeyInvalid(
    BuildContext context, {
    required String provider,
    required String providerDisplayName,
    String? details,
    VoidCallback? onConfigureAPIKey,
  }) {
    handleAPIKeyError(
      context,
      provider: provider,
      providerDisplayName: providerDisplayName,
      errorMessage:
          'API key is invalid or expired${details != null ? ': $details' : ''}',
      onConfigureAPIKey: onConfigureAPIKey,
    );
  }
}
