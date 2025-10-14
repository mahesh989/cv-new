#!/bin/bash

# VPS Deployment Status Checker
# Check the status of your VPS deployment

VPS_HOST="cvagent.duckdns.org"
VPS_USER="ubuntu"
VPS_PATH="~/cv-new/cv-magic-app"

echo "🔍 Checking VPS Deployment Status..."
echo "=================================="

ssh $VPS_USER@$VPS_HOST << EOF
    echo "📁 Current directory:"
    pwd
    
    echo ""
    echo "🌿 Git status:"
    cd $VPS_PATH
    git status --short
    git log --oneline -3
    
    echo ""
    echo "🐳 Docker containers:"
    docker compose ps
    
    echo ""
    echo "📊 Container health:"
    docker compose exec backend curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Backend is healthy" || echo "❌ Backend health check failed"
    
    echo ""
    echo "📋 Recent logs (last 10 lines):"
    docker compose logs --tail=10
    
    echo ""
    echo "🌐 External connectivity test:"
    curl -f https://$VPS_HOST/health 2>/dev/null && echo "✅ External access working" || echo "❌ External access failed"
EOF

echo ""
echo "🎯 Quick commands:"
echo "  View logs: ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose logs -f'"
echo "  Restart:   ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose restart'"
echo "  Full logs: ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose logs --tail=100'"
