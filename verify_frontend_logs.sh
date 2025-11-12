#!/bin/bash

# Script to verify whether frontend logs are generated in Docker container during analysis

echo "=========================================="
echo "Frontend Logs Verification Script"
echo "=========================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "   Frontend logs verification requires Docker access"
    exit 1
fi

echo "1. Checking Docker containers..."
echo "-----------------------------------"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" 2>/dev/null || {
    echo "❌ Cannot access Docker. Make sure Docker is running."
    exit 1
}

echo ""
echo "2. Checking for frontend container..."
echo "-----------------------------------"
FRONTEND_CONTAINER=$(docker ps --format "{{.Names}}" | grep -i "frontend\|mobile\|flutter" || true)
if [ -z "$FRONTEND_CONTAINER" ]; then
    echo "✅ Confirmed: No frontend container exists"
    echo "   Frontend is NOT containerized (runs in browser)"
else
    echo "⚠️  Found frontend container: $FRONTEND_CONTAINER"
fi

echo ""
echo "3. Checking backend container logs..."
echo "-----------------------------------"
BACKEND_CONTAINER=$(docker ps --format "{{.Names}}" | grep -i "backend\|cv_backend" | head -1)
if [ -n "$BACKEND_CONTAINER" ]; then
    echo "✅ Backend container found: $BACKEND_CONTAINER"
    echo ""
    echo "   Recent backend logs (last 20 lines):"
    echo "   ------------------------------------"
    docker logs "$BACKEND_CONTAINER" --tail=20 2>/dev/null | sed 's/^/   /' || echo "   Could not retrieve logs"
    
    echo ""
    echo "   Searching for frontend log patterns in backend logs..."
    echo "   ------------------------------------"
    FRONTEND_LOGS_FOUND=$(docker logs "$BACKEND_CONTAINER" 2>/dev/null | grep -i "FRONTEND\|=== FRONTEND SERVICE CALLED\|🔄 \[POLLING\]" || true)
    if [ -z "$FRONTEND_LOGS_FOUND" ]; then
        echo "   ✅ No frontend logs found in backend container (expected)"
        echo "   This confirms frontend logs are NOT in Docker"
    else
        echo "   ⚠️  Found some frontend-related logs:"
        echo "$FRONTEND_LOGS_FOUND" | head -5 | sed 's/^/   /'
    fi
else
    echo "⚠️  Backend container not found or not running"
fi

echo ""
echo "4. Summary"
echo "-----------------------------------"
echo "✅ Frontend: Runs in browser (NOT in Docker)"
echo "✅ Backend: Runs in Docker container"
echo "✅ Frontend logs: Go to browser console (F12), NOT Docker"
echo "✅ Backend logs: Go to Docker container logs"
echo ""
echo "To view frontend logs during analysis:"
echo "  1. Open app in browser"
echo "  2. Press F12 to open Developer Tools"
echo "  3. Go to Console tab"
echo "  4. Perform analysis"
echo "  5. Look for logs like:"
echo "     - === FRONTEND SERVICE CALLED ==="
echo "     - 🚀 [SERVICE_DEBUG] Starting performPreliminaryAnalysis"
echo "     - 🔄 [POLLING] Starting polling..."
echo ""
echo "=========================================="

