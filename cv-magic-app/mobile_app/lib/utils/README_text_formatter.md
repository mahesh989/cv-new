# Text Formatter Utility

A reusable text formatting utility for Flutter applications that supports markdown-style formatting with customizable styling.

## Features

- **Markdown Support**: Headers (`##`, `###`), bold text (`**text**`), lists, bullet points
- **Special Formatting**: Decision indicators with emojis, probability percentages
- **Customizable**: Font sizes, colors, line heights
- **Reusable**: Multiple widget variants for different use cases
- **Performance**: Efficient text parsing and rendering

## Usage

### 1. Basic Formatted Text

```dart
import '../utils/text_formatter.dart';

FormattedTextWidget(
  text: '''## Main Header
### Sub Header
This is **bold text** and regular text.
- Bullet point 1
- Bullet point 2
1. Numbered item 1
2. Numbered item 2''',
)
```

### 2. Analyze Match Formatting

```dart
AnalyzeMatchFormattedText(
  text: '''🟢 STRONG PURSUE
## Candidate Assessment
### Technical Skills Match: 85%
**Strong technical background** in required technologies.''',
)
```

### 3. Skills Analysis Formatting

```dart
SkillsAnalysisFormattedText(
  text: '''## Technical Skills Analysis
### Frontend Technologies
**React Native** - Advanced level''',
  baseColor: Colors.blue,
)
```

### 4. Custom Formatting

```dart
FormattedTextWidget(
  text: "Your markdown text here",
  baseColor: Colors.green,
  fontSize: 14,
  textColor: Colors.purple,
  isAnalyzeMatch: false,
)
```

### 5. Programmatic Formatting

```dart
TextSpan formattedText = TextFormatter.formatText(
  text: "Your text",
  baseColor: Colors.blue,
  baseFontSize: 14,
  isAnalyzeMatch: true,
);
```

## Widget Classes

### `TextFormatter`
Static utility class with the main formatting logic.

### `FormattedTextWidget`
Generic widget for formatted text display with full customization options.

### `AnalyzeMatchFormattedText`
Specialized widget for analyze match results with decision indicators and probability formatting.

### `SkillsAnalysisFormattedText`
Specialized widget for skills analysis with color theming support.

## Supported Markdown Elements

- **Headers**: `## Main Header`, `### Sub Header`
- **Bold Text**: `**bold text**`
- **Bullet Points**: `- item` or `*   item`
- **Numbered Lists**: `1. item`, `2. item`
- **Decision Indicators**: `🟢 STRONG PURSUE`, `🟡 STRATEGIC PURSUE`, etc.
- **Probability**: Lines containing `%` symbols

## Customization Options

- `baseColor`: MaterialColor for theming
- `fontSize`: Base font size (default: 13)
- `textColor`: Text color (default: Colors.grey.shade700)
- `isAnalyzeMatch`: Enable special analyze match formatting
- `lineHeight`: Line height multiplier (default: 1.4)

## Migration from Old Formatters

Replace old formatter classes with the new utility:

**Before:**
```dart
_FormattedAnalyzeMatchText(text: analysis)
_FormattedAnalysisText(text: analysis, baseColor: color)
```

**After:**
```dart
AnalyzeMatchFormattedText(text: analysis)
SkillsAnalysisFormattedText(text: analysis, baseColor: color)
```

## Benefits

1. **DRY Principle**: Single source of truth for text formatting
2. **Maintainability**: Easy to update formatting logic in one place
3. **Consistency**: Uniform formatting across the app
4. **Flexibility**: Multiple widget variants for different use cases
5. **Performance**: Optimized text parsing and rendering
6. **Extensibility**: Easy to add new formatting features
