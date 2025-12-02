#!/bin/bash
# Script to remove API key from git history
# WARNING: This rewrites history - coordinate with team before running

set -e

echo "⚠️  WARNING: This will rewrite git history!"
echo "Make sure you coordinate with your team before proceeding."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Install git-filter-repo if not available
if ! command -v git-filter-repo &> /dev/null; then
    echo "Installing git-filter-repo..."
    pip install git-filter-repo
fi

# Backup current branch
echo "Creating backup branch..."
git branch backup-before-filter-$(date +%Y%m%d-%H%M%S)

# Remove the API key from test.py in all commits
echo "Removing API key from git history..."
git filter-repo \
    --path cv-magic-app/backend/test.py \
    --invert-paths \
    --force

# Re-add test.py with the fixed version (using env var)
echo "Re-adding test.py with environment variable..."
git checkout HEAD -- cv-magic-app/backend/test.py || true

# If test.py is in .gitignore, we need to force add it temporarily
if git check-ignore -q cv-magic-app/backend/test.py; then
    git add -f cv-magic-app/backend/test.py
    git commit -m "Security: Use environment variable for API key in test.py"
fi

echo "✅ Done! History has been rewritten."
echo ""
echo "Next steps:"
echo "1. Review the changes: git log --oneline"
echo "2. Force push: git push origin enhanced-vps-ghs --force"
echo "3. ⚠️  WARN YOUR TEAM - they'll need to re-clone or reset their branches"

