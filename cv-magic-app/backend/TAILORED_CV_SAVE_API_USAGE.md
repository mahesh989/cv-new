# Tailored CV Save API Usage Guide

## New API Endpoint

I've added a new API endpoint to save edited tailored CV content back to the backend:

**Endpoint:** `PUT /api/cv/tailored-cv/save`

## How to Use

### 1. Frontend Integration (Flutter/Dart)

```dart
Future<bool> saveTailoredCV({
  required String companyName,
  required String cvContent, // or Map<String, dynamic> for structured content
  String? filename, // Optional: specify exact filename to update
}) async {
  try {
    final response = await http.put(
      Uri.parse('$baseUrl/api/cv/tailored-cv/save'),
      headers: {
        'Content-Type': 'application/json',
        // Add authorization headers if needed
      },
      body: jsonEncode({
        'company_name': companyName,
        'cv_content': cvContent,
        'filename': filename, // Optional
      }),
    );

    if (response.statusCode == 200) {
      final result = jsonDecode(response.body);
      print('✅ CV saved: ${result['message']}');
      return true;
    } else {
      final error = jsonDecode(response.body);
      print('❌ Save failed: ${error['error']}');
      return false;
    }
  } catch (e) {
    print('❌ Network error: $e');
    return false;
  }
}
```

### 2. Usage in Your CV Preview Widget

```dart
class CVPreviewWidget extends StatefulWidget {
  final String companyName;
  final String initialContent;
  
  @override
  _CVPreviewWidgetState createState() => _CVPreviewWidgetState();
}

class _CVPreviewWidgetState extends State<CVPreviewWidget> {
  late TextEditingController _contentController;
  bool _isEditing = false;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _contentController = TextEditingController(text: widget.initialContent);
  }

  Future<void> _saveChanges() async {
    setState(() => _isSaving = true);
    
    try {
      final success = await saveTailoredCV(
        companyName: widget.companyName,
        cvContent: _contentController.text,
      );
      
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ CV saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        setState(() => _isEditing = false);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('❌ Failed to save CV'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Edit/Save buttons
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            if (!_isEditing)
              ElevatedButton(
                onPressed: () => setState(() => _isEditing = true),
                child: Text('Edit CV'),
              ),
            if (_isEditing) ...[
              TextButton(
                onPressed: () {
                  _contentController.text = widget.initialContent;
                  setState(() => _isEditing = false);
                },
                child: Text('Cancel'),
              ),
              SizedBox(width: 8),
              ElevatedButton(
                onPressed: _isSaving ? null : _saveChanges,
                child: _isSaving 
                  ? SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text('Save'),
              ),
            ],
          ],
        ),
        SizedBox(height: 16),
        
        // CV Content
        Expanded(
          child: _isEditing
            ? TextField(
                controller: _contentController,
                maxLines: null,
                expands: true,
                decoration: InputDecoration(
                  border: OutlineInputBorder(),
                  hintText: 'Edit your CV content here...',
                ),
              )
            : Container(
                width: double.infinity,
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  _contentController.text,
                  style: TextStyle(fontSize: 14),
                ),
              ),
        ),
      ],
    );
  }
}
```

## API Request/Response Examples

### Request
```json
{
  "company_name": "Australia_for_UNHCR",
  "cv_content": "Updated CV content here...",
  "filename": "Australia_for_UNHCR_tailored_cv_20250921_111415.json"
}
```

### Success Response
```json
{
  "success": true,
  "message": "Tailored CV saved successfully",
  "company": "Australia_for_UNHCR",
  "filename": "Australia_for_UNHCR_tailored_cv_20250921_111415.json",
  "file_path": "cv-analysis/Australia_for_UNHCR/Australia_for_UNHCR_tailored_cv_20250921_111415.json",
  "updated_at": "2025-09-21T11:30:00.123456"
}
```

### Error Response
```json
{
  "error": "Company directory not found: InvalidCompany"
}
```

## Features

1. **Automatic File Detection**: If you don't specify a filename, it will update the most recent tailored CV file for that company
2. **Metadata Preservation**: Keeps existing metadata while updating the content
3. **Dual Save**: Saves to both the company directory and the `cvs/tailored` directory
4. **Edit Tracking**: Adds `manually_edited: true` flag and `updated_at` timestamp
5. **Flexible Content**: Handles both text content and structured JSON content

## Integration Steps

1. **Add the API call function** to your API service layer
2. **Update your CV preview widget** to include edit/save functionality
3. **Handle loading states** and user feedback
4. **Test the integration** with your existing tailored CV files

The API endpoint is now ready to use! Your edited CV content will be persisted to the backend files.
