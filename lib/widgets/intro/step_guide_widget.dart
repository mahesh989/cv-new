import 'package:flutter/material.dart';

class StepGuideWidget extends StatelessWidget {
  const StepGuideWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildStep(
          context,
          stepNumber: 1,
          title: 'Upload Your CV',
          description: 'Simply upload your existing CV in PDF or text format',
          icon: Icons.upload_file_rounded,
          color: Colors.blue,
        ),
        _buildConnector(),
        _buildStep(
          context,
          stepNumber: 2,
          title: 'Add Job Description',
          description: 'Paste or type the job description you\'re applying for',
          icon: Icons.work_rounded,
          color: Colors.green,
        ),
        _buildConnector(),
        _buildStep(
          context,
          stepNumber: 3,
          title: 'AI Analysis',
          description:
              'Our AI analyzes compatibility and suggests improvements',
          icon: Icons.auto_awesome_rounded,
          color: Colors.purple,
        ),
        _buildConnector(),
        _buildStep(
          context,
          stepNumber: 4,
          title: 'Get Optimized CV',
          description: 'Download your tailored, ATS-optimized CV instantly',
          icon: Icons.download_rounded,
          color: Colors.orange,
          isLast: true,
        ),
      ],
    );
  }

  Widget _buildStep(
    BuildContext context, {
    required int stepNumber,
    required String title,
    required String description,
    required IconData icon,
    required Color color,
    bool isLast = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.2),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Center(
              child: Text(
                stepNumber.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      icon,
                      color: color,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey[600],
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConnector() {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          const SizedBox(width: 23), // Center align with step numbers
          Container(
            width: 2,
            height: 20,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.grey.shade300,
                  Colors.grey.shade400,
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
