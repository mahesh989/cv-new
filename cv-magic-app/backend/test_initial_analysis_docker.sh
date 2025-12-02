#!/bin/bash
# Test script to run inside Docker container
# Usage: docker compose exec backend python test_initial_analysis.py

echo "🐳 Running test inside Docker container..."
echo ""

# Check if we're inside Docker
if [ -f /.dockerenv ]; then
    echo "✅ Running inside Docker container"
    BASE_URL="http://localhost:8000"
else
    echo "⚠️  Not inside Docker - will try to connect to backend service"
    BASE_URL="http://backend:8000"
fi

cd /app
python test_initial_analysis.py

