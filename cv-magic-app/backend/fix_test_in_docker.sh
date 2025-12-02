#!/bin/bash
# Script to fix the test file inside Docker container
# Run this from outside the container

echo "🔧 Fixing test_initial_analysis.py in Docker container..."

# Fix the authentication part using sed
docker exec cv_backend sed -i 's/data={/json={/g' /app/app/test_initial_analysis.py
docker exec cv_backend sed -i 's/"username":/"email":/g' /app/app/test_initial_analysis.py

echo "✅ Fixed! Now run: docker exec cv_backend python3 /app/app/test_initial_analysis.py"

