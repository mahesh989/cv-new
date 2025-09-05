#!/bin/bash

# =============================================================================
# FOLDER CLEANUP SCRIPT - NEW-CV PROJECT
# =============================================================================
# This script safely reorganizes the folder structure
# Option 1: Clean Migration (Recommended)

set -e

echo "🧹 Starting folder cleanup for new-cv project..."
echo ""

# =============================================================================
# SAFETY CHECKS
# =============================================================================

echo "📋 Current folder structure:"
ls -la | grep "drwx" | awk '{print "  " $9}'
echo ""

read -p "🤔 Do you want to proceed with cleanup? This will rename folders (y/N): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "❌ Cleanup cancelled."
    exit 0
fi

echo "✅ Proceeding with cleanup..."
echo ""

# =============================================================================
# BACKUP FIRST (SAFETY)
# =============================================================================

echo "💾 Creating backup of current structure..."
timestamp=$(date +%Y%m%d_%H%M%S)

if [ -d "back/" ]; then
    echo "  📦 Backing up original back/ folder..."
    cp -r back/ "back_backup_$timestamp/"
fi

if [ -d "backend/" ]; then
    echo "  📦 Backing up new backend/ folder..."
    cp -r backend/ "backend_backup_$timestamp/"
fi

echo "✅ Backup completed: back_backup_$timestamp/ and backend_backup_$timestamp/"
echo ""

# =============================================================================
# FOLDER REORGANIZATION
# =============================================================================

echo "🔄 Reorganizing folders..."

# Step 1: Remove empty front folder
if [ -d "front/" ]; then
    if [ -z "$(ls -A front/)" ]; then
        echo "  🗑️  Removing empty front/ folder..."
        rm -rf front/
    else
        echo "  ⚠️  front/ folder is not empty, keeping it..."
    fi
fi

# Step 2: Rename folders
echo "  📁 Renaming folders for clean structure..."

if [ -d "back/" ] && [ -d "backend/" ]; then
    echo "    back/ → back_legacy/ (preserving original system)"
    mv back/ back_legacy/
    
    echo "    backend/ → back/ (new organized structure becomes main)"
    mv backend/ back/
else
    echo "  ⚠️  Expected folders not found, skipping rename..."
fi

if [ -d "frontend/" ]; then
    echo "    frontend/ → front/ (consistent naming)"
    mv frontend/ front/
fi

# =============================================================================
# DATA MIGRATION
# =============================================================================

echo "📂 Migrating important data..."

# Copy environment file if exists
if [ -f "back_legacy/.env" ] && [ -d "back/" ]; then
    echo "  🔧 Copying .env file..."
    cp back_legacy/.env back/ 2>/dev/null || echo "    ℹ️  No .env file to copy"
fi

# Copy uploads if they exist
if [ -d "back_legacy/uploads/" ] && [ -d "back/data/uploads/" ]; then
    echo "  📁 Copying upload files..."
    cp -r back_legacy/uploads/* back/data/uploads/ 2>/dev/null || echo "    ℹ️  No upload files to copy"
fi

# Copy database if it exists
if [ -f "back_legacy/cv_app.db" ] && [ -d "back/data/database/" ]; then
    echo "  💾 Copying database file..."
    cp back_legacy/cv_app.db back/data/database/ 2>/dev/null || echo "    ℹ️  No database file to copy"
fi

# =============================================================================
# FINAL STRUCTURE VALIDATION
# =============================================================================

echo ""
echo "✅ Cleanup completed! New structure:"
echo ""
ls -la | grep "drwx" | awk '{print "  ✅ " $9}'
echo ""

# =============================================================================
# SUMMARY AND NEXT STEPS
# =============================================================================

echo "📊 Summary:"
echo "  ✅ Original system preserved in: back_legacy/"
echo "  ✅ New organized system is now: back/"
echo "  ✅ Frontend ready for development: front/"
echo "  ✅ Backups created with timestamp: $timestamp"
echo ""

if [ -d "back/" ]; then
    echo "🚀 Next steps:"
    echo "  1. cd back/"
    echo "  2. cp .env.example .env"
    echo "  3. Edit .env with your API keys"
    echo "  4. pip install -r requirements.txt"
    echo "  5. ./start_server.sh"
    echo ""
fi

echo "📚 Documentation: ./documentation/DOCUMENTATION_INDEX.md"
echo "🔄 Rollback: Use back_backup_$timestamp/ if needed"
echo ""
echo "🎉 Folder cleanup completed successfully!"
