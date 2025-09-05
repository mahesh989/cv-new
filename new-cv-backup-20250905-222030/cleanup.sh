#!/bin/bash

# =============================================================================
# NEW-CV PROJECT CLEANUP SCRIPT
# =============================================================================
# This script cleans up the refactored project structure
# Run this after the refactoring is complete

set -e

echo "🧹 Starting new-cv project cleanup..."

# =============================================================================
# REMOVE OLD FILES AND DUPLICATES
# =============================================================================

echo "📂 Cleaning up old structure..."

# Remove old back folder (keeping as backup first)
if [ -d "back_old" ]; then
    echo "  ➜ Removing old backup folder..."
    rm -rf back_old
fi

if [ -d "back" ]; then
    echo "  ➜ Moving old 'back' to 'back_old' for safety..."
    mv back back_old
fi

# Remove old front folder content (if empty or contains only placeholders)
if [ -d "front" ] && [ ! "$(ls -A front)" ]; then
    echo "  ➜ Removing empty 'front' directory..."
    rm -rf front
fi

# =============================================================================
# CREATE MISSING DIRECTORIES
# =============================================================================

echo "📁 Creating missing directories..."

# Create .gitkeep files for important empty directories
touch backend/data/uploads/.gitkeep
touch backend/data/outputs/.gitkeep
touch backend/tests/.gitkeep
touch backend/scripts/.gitkeep
touch frontend/src/.gitkeep
touch frontend/public/.gitkeep
touch shared/types/.gitkeep
touch shared/constants/.gitkeep
touch shared/utils/.gitkeep

# =============================================================================
# CREATE MISSING INIT FILES
# =============================================================================

echo "🐍 Creating Python __init__.py files..."

# Backend init files
touch backend/app/__init__.py
touch backend/app/ai/__init__.py
touch backend/app/ai/providers/__init__.py
touch backend/app/api/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/utils/__init__.py
touch backend/app/middleware/__init__.py
touch backend/tests/__init__.py
touch backend/scripts/__init__.py

# =============================================================================
# CLEAN UP CACHE AND TEMP FILES
# =============================================================================

echo "🧽 Cleaning cache and temporary files..."

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
find . -name "*.pyd" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remove log files
find . -name "*.log" -delete 2>/dev/null || true

# =============================================================================
# SET PERMISSIONS
# =============================================================================

echo "🔐 Setting file permissions..."

# Make shell scripts executable
find . -name "*.sh" -exec chmod +x {} \;

# =============================================================================
# VALIDATE STRUCTURE
# =============================================================================

echo "✅ Validating new structure..."

required_dirs=(
    "backend"
    "backend/app"
    "backend/app/ai"
    "backend/app/api"
    "backend/data"
    "frontend"
    "documentation"
    "shared"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir exists"
    else
        echo "  ❌ $dir missing - creating..."
        mkdir -p "$dir"
    fi
done

required_files=(
    "README.md"
    "backend/.env.example"
    "backend/requirements.txt"
    ".gitignore"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ⚠️  $file missing"
    fi
done

# =============================================================================
# SUMMARY
# =============================================================================

echo ""
echo "🎉 Cleanup completed!"
echo ""
echo "📊 Project structure:"
tree -I '__pycache__|*.pyc|.git' -L 3 2>/dev/null || echo "Install 'tree' command to see structure visualization"
echo ""
echo "📋 Next steps:"
echo "  1. cd backend && cp .env.example .env"
echo "  2. Edit .env with your API keys"
echo "  3. pip install -r requirements.txt"
echo "  4. ./start_server.sh"
echo ""
echo "📚 Documentation: ./documentation/README.md"
echo "🏗️  Architecture: See REFACTOR_PLAN.md for details"
echo ""
