# Flutter Integration Guide for Enhanced JD Analysis

This guide shows you how to integrate the enhanced categorized JD analysis system with your Flutter UI's "Analyze Skills" button.

## 🚀 **Quick Integration**

### **Option 1: Simple Button Integration (Recommended)**

Replace your existing "Analyze Skills" button with the new `AnalyzeSkillsButton`:

```dart
import 'package:your_app/widgets/jd_analysis_widget.dart';

// In your existing widget
AnalyzeSkillsButton(
  companyName: "Australia_for_UNHCR", // Your company name
  onAnalysisComplete: () {
    // Handle completion - refresh UI, show results, etc.
    print('Analysis completed!');
  },
)
```

### **Option 2: Full Analysis Widget**

For a complete analysis experience with detailed results:

```dart
import 'package:your_app/widgets/jd_analysis_widget.dart';

// In your screen
JDAnalysisWidget(
  companyName: "Australia_for_UNHCR",
  showDetailedView: true,
  onAnalysisComplete: () {
    // Handle completion
  },
)
```

## 📱 **Complete Integration Examples**

### **1. Existing Screen Integration**

```dart
import 'package:flutter/material.dart';
import 'package:your_app/widgets/jd_analysis_widget.dart';
import 'package:your_app/services/jd_analysis_service.dart';

class YourExistingScreen extends StatefulWidget {
  final String companyName;
  
  const YourExistingScreen({Key? key, required this.companyName}) : super(key: key);
  
  @override
  _YourExistingScreenState createState() => _YourExistingScreenState();
}

class _YourExistingScreenState extends State<YourExistingScreen> {
  JDAnalysisResult? _analysisResult;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Your Screen')),
      body: Column(
        children: [
          // Your existing content
          
          // Add the analyze button
          Padding(
            padding: const EdgeInsets.all(16),
            child: AnalyzeSkillsButton(
              companyName: widget.companyName,
              onAnalysisComplete: () {
                _loadAnalysisResults();
              },
            ),
          ),
          
          // Show quick results if available
          if (_analysisResult != null) _buildQuickResults(),
        ],
      ),
    );
  }
  
  Widget _buildQuickResults() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Analysis Results', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildResultCard(
                    'Technical Skills',
                    '${_analysisResult!.requiredSkills.technical.length}',
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildResultCard(
                    'Soft Skills',
                    '${_analysisResult!.requiredSkills.softSkills.length}',
                    Colors.green,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildResultCard(String title, String value, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(value, style: TextStyle(fontSize: 18, color: color, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }
  
  Future<void> _loadAnalysisResults() async {
    try {
      final service = JDAnalysisService();
      final result = await service.getAnalysis(widget.companyName);
      setState(() {
        _analysisResult = result;
      });
    } catch (e) {
      print('Error loading results: $e');
    }
  }
}
```

### **2. Dedicated Analysis Screen**

```dart
import 'package:flutter/material.dart';
import 'package:your_app/screens/jd_analysis_screen.dart';

// Navigate to dedicated analysis screen
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => JDAnalysisScreen(
      companyName: "Australia_for_UNHCR",
    ),
  ),
);
```

## 🔧 **Service Usage Examples**

### **Direct Service Usage**

```dart
import 'package:your_app/services/jd_analysis_service.dart';

class YourWidget extends StatefulWidget {
  @override
  _YourWidgetState createState() => _YourWidgetState();
}

class _YourWidgetState extends State<YourWidget> {
  final JDAnalysisService _service = JDAnalysisService();
  JDAnalysisResult? _result;
  
  Future<void> _analyzeSkills() async {
    try {
      final result = await _service.analyzeSkills(
        companyName: "Australia_for_UNHCR",
        forceRefresh: false,
      );
      
      setState(() {
        _result = result;
      });
      
      // Access categorized results
      print('Technical skills: ${result.requiredSkills.technical}');
      print('Soft skills: ${result.requiredSkills.softSkills}');
      print('Experience: ${result.experienceYears} years');
      
    } catch (e) {
      print('Error: $e');
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: _analyzeSkills,
      child: const Text('Analyze Skills'),
    );
  }
}
```

### **Get Specific Skill Categories**

```dart
// Get only technical skills
final technicalSkills = await _service.getTechnicalSkills(
  companyName: "Australia_for_UNHCR",
  requiredOnly: true, // Only required skills
);

// Get only soft skills
final softSkills = await _service.getSoftSkills(
  companyName: "Australia_for_UNHCR",
  requiredOnly: false, // All soft skills
);

// Get experience requirements
final experience = await _service.getExperienceRequirements(
  companyName: "Australia_for_UNHCR",
);

// Get domain knowledge
final domainKnowledge = await _service.getDomainKnowledge(
  companyName: "Australia_for_UNHCR",
);
```

## 🎨 **Custom UI Components**

### **Skills Display Widget**

```dart
class SkillsDisplayWidget extends StatelessWidget {
  final List<String> skills;
  final String title;
  final Color color;
  final bool isRequired;
  
  const SkillsDisplayWidget({
    Key? key,
    required this.skills,
    required this.title,
    required this.color,
    this.isRequired = true,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isRequired ? Icons.check_circle : Icons.star,
                  color: color,
                ),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                const Spacer(),
                Chip(
                  label: Text('${skills.length}'),
                  backgroundColor: color.withOpacity(0.1),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: skills.map((skill) => Chip(
                label: Text(skill),
                backgroundColor: color.withOpacity(0.1),
                side: BorderSide(color: color),
              )).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

// Usage
SkillsDisplayWidget(
  skills: result.requiredSkills.technical,
  title: 'Required Technical Skills',
  color: Colors.red,
  isRequired: true,
)
```

### **Analysis Summary Widget**

```dart
class AnalysisSummaryWidget extends StatelessWidget {
  final JDAnalysisResult result;
  
  const AnalysisSummaryWidget({Key? key, required this.result}) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Analysis Summary',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildSummaryItem(
                    'Total Skills',
                    '${result.skillSummary.totalRequired + result.skillSummary.totalPreferred}',
                    Colors.blue,
                    Icons.analytics,
                  ),
                ),
                Expanded(
                  child: _buildSummaryItem(
                    'Experience',
                    '${result.experienceYears ?? 'N/A'} years',
                    Colors.purple,
                    Icons.work,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildSummaryItem(
                    'Required',
                    '${result.skillSummary.totalRequired}',
                    Colors.red,
                    Icons.check_circle,
                  ),
                ),
                Expanded(
                  child: _buildSummaryItem(
                    'Preferred',
                    '${result.skillSummary.totalPreferred}',
                    Colors.orange,
                    Icons.star,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildSummaryItem(String label, String value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            label,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
```

## 🔐 **Authentication Setup**

```dart
// In your app initialization
void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final JDAnalysisService _service = JDAnalysisService();
  
  @override
  void initState() {
    super.initState();
    _setupAuthentication();
  }
  
  void _setupAuthentication() {
    // Set your authentication token
    _service.setAuthToken('your_bearer_token_here');
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('JD Analysis App')),
      body: Center(
        child: AnalyzeSkillsButton(
          companyName: "Australia_for_UNHCR",
          onAnalysisComplete: () {
            print('Analysis completed!');
          },
        ),
      ),
    );
  }
}
```

## 🚨 **Error Handling**

```dart
Future<void> _analyzeWithErrorHandling() async {
  try {
    final result = await _service.analyzeSkills(
      companyName: widget.companyName,
    );
    
    // Success
    setState(() {
      _analysisResult = result;
    });
    
  } on JDAnalysisException catch (e) {
    // Handle specific analysis errors
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Analysis failed: ${e.message}'),
        backgroundColor: Colors.red,
      ),
    );
  } catch (e) {
    // Handle general errors
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Unexpected error: $e'),
        backgroundColor: Colors.red,
      ),
    );
  }
}
```

## 📊 **Data Models**

The service provides these data models:

- `JDAnalysisResult` - Complete analysis result
- `RequiredSkills` - Required skills by category
- `PreferredSkills` - Preferred skills by category
- `SkillSummary` - Summary statistics
- `AnalysisStatus` - Analysis status information
- `JDAnalysisException` - Custom exception for errors

## 🎯 **Key Features**

✅ **Simple Integration** - Just replace your existing button  
✅ **Categorized Results** - Technical, Soft Skills, Experience, Domain Knowledge  
✅ **Backward Compatibility** - Works with existing flat keyword lists  
✅ **Error Handling** - Comprehensive error management  
✅ **Loading States** - Built-in loading indicators  
✅ **Caching Support** - Automatic cache detection and management  
✅ **Flexible UI** - Multiple widget options for different use cases  

## 🚀 **Next Steps**

1. **Copy the service and widget files** to your Flutter project
2. **Update the base URL** in `JDAnalysisService` to match your backend
3. **Set up authentication** with your bearer token
4. **Replace your existing "Analyze Skills" button** with `AnalyzeSkillsButton`
5. **Test the integration** with your existing UI
6. **Customize the UI** as needed for your app's design

The system is now ready to provide rich, categorized job description analysis directly in your Flutter app! 🎉
