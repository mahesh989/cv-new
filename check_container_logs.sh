#!/bin/bash
# Script to check Docker container logs for JD processing

echo "=========================================="
echo "Checking Docker Container Logs"
echo "=========================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not available in PATH"
    echo "Please run this script from a terminal where Docker is available"
    exit 1
fi

# Check if container is running
echo "📦 Checking container status..."
if docker ps --filter "name=cv_backend" --format "{{.Names}}" | grep -q cv_backend; then
    echo "✅ Container cv_backend is running"
    echo ""
    
    # Show recent logs (last 100 lines)
    echo "📋 Recent logs (last 100 lines):"
    echo "----------------------------------------"
    docker logs cv_backend --tail 100 2>&1
    echo ""
    echo "----------------------------------------"
    echo ""
    
    # Filter for JD processing logs
    echo "🔍 JD Processing related logs (last 50 lines):"
    echo "----------------------------------------"
    docker logs cv_backend --tail 500 2>&1 | grep -E "JD_PROCESSING|JOB_EXTRACTION|JD_PROCESSING_TRIGGER" | tail -50
    echo ""
    echo "----------------------------------------"
    echo ""
    
    # Show print statements (if any)
    echo "🖨️  Print statements (last 30 lines):"
    echo "----------------------------------------"
    docker logs cv_backend --tail 200 2>&1 | grep -E "\[JD_PROCESSING\]|\[JOB_EXTRACTION\]" | tail -30
    echo ""
    
else
    echo "⚠️  Container cv_backend is not running"
    echo ""
    echo "Checking all containers..."
    docker ps -a | grep -E "backend|cv_backend" || echo "No backend containers found"
    echo ""
    echo "To start the container, run:"
    echo "  cd cv-magic-app && docker-compose up -d backend"
fi

echo ""
echo "=========================================="
echo "To follow logs in real-time, run:"
echo "  docker logs cv_backend -f"
echo "=========================================="

