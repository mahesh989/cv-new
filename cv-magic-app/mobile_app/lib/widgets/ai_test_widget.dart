import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/theme/app_theme.dart';
import '../services/ai_model_service.dart';
import '../services/api_service.dart';

class AITestWidget extends StatefulWidget {
  const AITestWidget({super.key});

  @override
  State<AITestWidget> createState() => _AITestWidgetState();
}

class _AITestWidgetState extends State<AITestWidget> {
  final TextEditingController _promptController = TextEditingController();
  String _response = '';
  bool _isLoading = false;

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }

  Future<void> _testAICall() async {
    if (_promptController.text.isEmpty) return;

    setState(() {
      _isLoading = true;
      _response = '';
    });

    try {
      // This will automatically use the currently selected model
      final result = await AIAPI.generateText(
        prompt: _promptController.text,
        systemPrompt: 'You are a helpful assistant.',
      );

      setState(() {
        _response = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _response = 'Error: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AIModelService>(
      builder: (context, aiService, child) {
        return AppTheme.createCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Current Model Display
              Row(
                children: [
                  Icon(
                    Icons.psychology_rounded,
                    color: aiService.currentModel.color,
                    size: 24,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Current AI Model',
                          style: AppTheme.bodySmall.copyWith(
                            color: AppTheme.neutralGray600,
                          ),
                        ),
                        Text(
                          aiService.currentModel.name,
                          style: AppTheme.bodyMedium.copyWith(
                            fontWeight: FontWeight.bold,
                            color: aiService.currentModel.color,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Test Input
              TextField(
                controller: _promptController,
                decoration: InputDecoration(
                  labelText: 'Test Prompt',
                  hintText: 'Enter a prompt to test the AI...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),

              // Test Button
              SizedBox(
                width: double.infinity,
                child: AppTheme.createGradientButton(
                  text: _isLoading ? 'Testing...' : 'Test AI Call',
                  onPressed: _isLoading ? () {} : () => _testAICall(),
                  isLoading: _isLoading,
                ),
              ),
              const SizedBox(height: 16),

              // Response Display
              if (_response.isNotEmpty) ...[
                const Divider(),
                const SizedBox(height: 16),
                Text(
                  'AI Response:',
                  style: AppTheme.bodyMedium.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.neutralGray50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppTheme.neutralGray200),
                  ),
                  child: Text(
                    _response,
                    style: AppTheme.bodySmall,
                  ),
                ),
              ],
            ],
          ),
        );
      },
    );
  }
}
