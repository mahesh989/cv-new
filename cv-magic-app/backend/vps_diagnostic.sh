#!/bin/bash

echo "🔍 VPS Diagnostic Check"
echo "===================="
echo ""

echo "📁 Checking user directory structure:"
ls -la /root/cv-magic-app/backend/user/ 2>/dev/null || echo "No user directory found"
echo ""

echo "📁 Checking for saved jobs files:"
find /root/cv-magic-app/backend/user -name "saved_jobs.json" -exec echo "Found: {}" \; -exec cat {} \; 2>/dev/null || echo "No saved jobs files found"
echo ""

echo "📁 Checking for applied companies:"
find /root/cv-magic-app/backend/user -name "applied_companies" -type d -exec echo "Found: {}" \; -exec ls -la {} \; 2>/dev/null || echo "No applied companies found"
echo ""

echo "📁 Checking for tailored CV files:"
find /root/cv-magic-app/backend/user -name "*_tailored_cv_*.json" -exec echo "Found: {}" \; 2>/dev/null || echo "No tailored CV files found"
echo ""

echo "🐳 Checking Docker containers:"
docker ps 2>/dev/null || echo "Docker not accessible"
echo ""

echo "📋 Checking server logs (last 20 lines):"
docker logs --tail 20 cv-magic-app 2>/dev/null || echo "Could not get server logs"
echo ""

echo "🌐 Testing server health:"
curl -s http://localhost:8000/health || echo "Server not responding"
echo ""

echo "🔧 Diagnostic complete!"
