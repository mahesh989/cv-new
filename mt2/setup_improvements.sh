#!/bin/bash

# Flutter Improvements Setup Script
# This script helps set up the improved architecture in your existing Flutter project

set -e  # Exit on any error

echo "🚀 Setting up Flutter Improvements..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in a Flutter project
if [ ! -f "pubspec.yaml" ]; then
    echo -e "${RED}❌ Error: pubspec.yaml not found. Please run this script from your Flutter project root.${NC}"
    exit 1
fi

echo -e "${BLUE}📱 Detected Flutter project${NC}"

# Create backup
echo -e "${YELLOW}📦 Creating backup of existing files...${NC}"
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

# Backup important files if they exist
[ -f "lib/main.dart" ] && cp "lib/main.dart" "$backup_dir/"
[ -d "lib/core" ] && cp -r "lib/core" "$backup_dir/" 2>/dev/null || true

echo -e "${GREEN}✅ Backup created in $backup_dir${NC}"

# Check if core directory exists
if [ ! -d "lib/core" ]; then
    echo -e "${YELLOW}📁 Creating lib/core directory...${NC}"
    mkdir -p lib/core
fi

# Add dependencies to pubspec.yaml
echo -e "${YELLOW}📦 Checking dependencies in pubspec.yaml...${NC}"

dependencies_to_add=(
    "provider: ^6.0.5"
    "shared_preferences: ^2.2.0"
    "http: ^1.1.0"
    "crypto: ^3.0.3"
    "local_auth: ^2.1.6"
)

for dep in "${dependencies_to_add[@]}"; do
    dep_name=$(echo "$dep" | cut -d':' -f1)
    if ! grep -q "^[[:space:]]*$dep_name:" pubspec.yaml; then
        echo -e "${BLUE}➕ Adding dependency: $dep${NC}"
        # Add after dependencies: line
        sed -i.bak "/^dependencies:/a\\
  $dep" pubspec.yaml
    else
        echo -e "${GREEN}✅ $dep_name already exists${NC}"
    fi
done

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
flutter pub get

# Create core files status check
echo -e "${BLUE}📋 Checking core architecture files...${NC}"

core_files=(
    "lib/core/architecture.dart"
    "lib/core/state_management.dart"
    "lib/core/error_handling.dart"
    "lib/core/performance.dart"
    "lib/core/security.dart"
)

missing_files=()
for file in "${core_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${YELLOW}⚠️  $file missing${NC}"
        missing_files+=("$file")
    fi
done

# Check main_improved.dart
if [ -f "lib/main_improved.dart" ]; then
    echo -e "${GREEN}✅ lib/main_improved.dart exists${NC}"
else
    echo -e "${YELLOW}⚠️  lib/main_improved.dart missing${NC}"
    missing_files+=("lib/main_improved.dart")
fi

# Report status
if [ ${#missing_files[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All core architecture files are present!${NC}"
else
    echo -e "${YELLOW}📝 Missing files that need to be created:${NC}"
    for file in "${missing_files[@]}"; do
        echo -e "   - $file"
    done
fi

# Create a simple integration guide
echo -e "${BLUE}📄 Creating integration guide...${NC}"
cat > INTEGRATION_GUIDE.md << 'EOF'
# Integration Guide

## Quick Setup Steps

1. **Backup Complete** ✅
   - Your original files are backed up in `backup_*` directory

2. **Dependencies Added** ✅
   - Required packages added to pubspec.yaml
   - Run `flutter pub get` if not done automatically

3. **Next Steps**

### Option A: Replace main.dart (Recommended for new projects)
```bash
# Backup current main.dart (already done)
mv lib/main.dart lib/main_original.dart

# Use improved main.dart
cp lib/main_improved.dart lib/main.dart
```

### Option B: Gradual Integration (Recommended for existing projects)
```dart
// In your existing main.dart, add imports:
import 'core/architecture.dart';
import 'core/state_management.dart';
import 'core/error_handling.dart';

// Wrap your app:
return StateProvider(
  appState: appState,
  analysisState: analysisState,
  uiState: uiState,
  child: YourExistingApp(),
);
```

### Option C: Side-by-Side Testing
- Keep your existing main.dart
- Test with: `flutter run -t lib/main_improved.dart`

## File Checklist

Ensure these files exist in lib/core/:
- [ ] architecture.dart
- [ ] state_management.dart  
- [ ] error_handling.dart
- [ ] performance.dart
- [ ] security.dart

And:
- [ ] lib/main_improved.dart

## Testing the Setup

1. Run the app: `flutter run`
2. Check for any import errors
3. Verify state management is working
4. Test error handling and loading states

## Need Help?

- Read FLUTTER_IMPROVEMENTS.md for detailed documentation
- Check the backup directory if you need to restore anything
- Review the core files to understand the architecture

EOF

echo -e "${GREEN}✅ Integration guide created: INTEGRATION_GUIDE.md${NC}"

# Final status
echo -e "${BLUE}=====================================
📱 Flutter Improvements Setup Complete
=====================================${NC}"

if [ ${#missing_files[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All files are ready! You can now:
1. Read INTEGRATION_GUIDE.md for next steps
2. Review FLUTTER_IMPROVEMENTS.md for details
3. Test with: flutter run -t lib/main_improved.dart${NC}"
else
    echo -e "${YELLOW}⚠️  Setup incomplete. Missing files:${NC}"
    for file in "${missing_files[@]}"; do
        echo -e "   - $file"
    done
    echo -e "${YELLOW}Please create these files before proceeding.${NC}"
fi

echo -e "${BLUE}🚀 Happy coding!${NC}"
