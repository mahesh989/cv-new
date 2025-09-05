import 'package:flutter/material.dart';
import 'analysis_step_controller.dart';

/// Abstract base class for all analysis step widgets.
/// Defines the contract for displaying step results and states.
abstract class AnalysisStepWidget extends StatelessWidget {
  /// The controller for this step
  final AnalysisStepController controller;

  /// Whether to show the step header
  final bool showHeader;

  /// Whether to show progress indicators
  final bool showProgress;

  /// Whether to show error messages
  final bool showErrors;

  /// Custom styling for the step container
  final BoxDecoration? containerDecoration;

  /// Custom padding for the step content
  final EdgeInsetsGeometry? contentPadding;

  const AnalysisStepWidget({
    super.key,
    required this.controller,
    this.showHeader = true,
    this.showProgress = true,
    this.showErrors = true,
    this.containerDecoration,
    this.contentPadding,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: controller,
      builder: (context, _) {
        return Container(
          decoration: containerDecoration ?? _getDefaultDecoration(),
          padding: contentPadding ?? const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Step header
              if (showHeader) _buildStepHeader(),

              // Progress indicator
              if (showProgress && controller.isRunning) ...[
                const SizedBox(height: 12),
                _buildProgressIndicator(),
              ],

              // Error message
              if (showErrors && controller.error != null) ...[
                const SizedBox(height: 12),
                _buildErrorMessage(),
              ],

              // Step-specific content
              if (controller.hasResult) ...[
                const SizedBox(height: 12),
                buildStepContent(context),
              ],
            ],
          ),
        );
      },
    );
  }

  /// Build the step-specific content.
  /// Override this method to provide the actual UI for the step.
  Widget buildStepContent(BuildContext context);

  /// Build the step header with title and status
  Widget _buildStepHeader() {
    return Row(
      children: [
        // Step icon
        _buildStepIcon(),
        const SizedBox(width: 8),

        // Step title
        Expanded(
          child: Text(
            controller.title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),

        // Step status indicator
        _buildStatusIndicator(),
      ],
    );
  }

  /// Build the step icon
  Widget _buildStepIcon() {
    IconData iconData;
    Color iconColor;

    if (controller.isRunning) {
      iconData = Icons.hourglass_empty;
      iconColor = Colors.blue;
    } else if (controller.isCompleted) {
      iconData = Icons.check_circle;
      iconColor = Colors.green;
    } else if (controller.error != null) {
      iconData = Icons.error;
      iconColor = Colors.red;
    } else {
      iconData = Icons.radio_button_unchecked;
      iconColor = Colors.grey;
    }

    return Icon(iconData, color: iconColor, size: 20);
  }

  /// Build the status indicator
  Widget _buildStatusIndicator() {
    if (controller.isRunning) {
      return SizedBox(
        width: 16,
        height: 16,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[700]!),
        ),
      );
    } else if (controller.isCompleted) {
      return Icon(Icons.check_circle, color: Colors.green[700], size: 20);
    } else if (controller.error != null) {
      return Icon(Icons.error, color: Colors.red[700], size: 20);
    } else {
      return const SizedBox.shrink();
    }
  }

  /// Build the progress indicator
  Widget _buildProgressIndicator() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 16,
            height: 16,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.blue[700]!),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Running ${controller.title}...',
              style: TextStyle(
                color: Colors.blue[700],
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Build the error message
  Widget _buildErrorMessage() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red[200]!),
      ),
      child: Row(
        children: [
          Icon(Icons.error, color: Colors.red[700], size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              controller.error!,
              style: TextStyle(
                color: Colors.red[700],
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Get the default decoration for the step container
  BoxDecoration _getDefaultDecoration() {
    return BoxDecoration(
      color: Colors.grey[50],
      borderRadius: BorderRadius.circular(8),
      border: Border.all(color: Colors.grey[300]!),
    );
  }

  /// Get the step-specific decoration based on state
  BoxDecoration getStepDecoration() {
    if (controller.isRunning) {
      return BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue[200]!),
      );
    } else if (controller.isCompleted) {
      return BoxDecoration(
        color: Colors.green[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.green[200]!),
      );
    } else if (controller.error != null) {
      return BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red[200]!),
      );
    } else {
      return _getDefaultDecoration();
    }
  }

  /// Build a section header with icon and title
  Widget buildSectionHeader(String title, IconData icon, Color color) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 8),
        Text(
          title,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  /// Build a result container with title and content
  Widget buildResultContainer({
    required String title,
    required Widget content,
    required Color color,
    IconData? icon,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              if (icon != null) ...[
                Icon(icon, color: color, size: 16),
                const SizedBox(width: 8),
              ],
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: color,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          content,
        ],
      ),
    );
  }
}
