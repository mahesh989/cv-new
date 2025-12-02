#!/bin/bash
# Quick script to run the test inside Docker on remote server

echo "🐳 Copying test file to container..."
docker cp backend/test_initial_analysis.py cv_backend:/app/test_initial_analysis.py

echo "🚀 Running test inside container..."
docker exec cv_backend python /app/test_initial_analysis.py

echo ""
echo "✅ Test completed! Check output above."

