#!/bin/bash

# Backend Deployment Verification Script
# This script helps verify that the backend is deployed correctly with all changes

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

VPS_HOST="cvagent.duckdns.org"
VPS_USER="ubuntu"
VPS_PATH="~/cv-new/cv-magic-app"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Backend Deployment Verification Script              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Check GitHub Actions Status
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 1: Check GitHub Actions Deployment Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
print_info "Go to: https://github.com/mahesh989/cv-new/actions"
print_info "Check that the latest workflow run shows:"
echo "  - ✅ build-and-deploy-frontend (green checkmark)"
echo "  - ✅ deploy-backend (green checkmark)"
echo ""
read -p "Press Enter after checking GitHub Actions status..."

# 2. SSH into VPS and verify
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 2: SSH into VPS and Verify Deployment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ssh -T -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST << 'EOF'
    set -e
    
    echo "🔍 Checking deployment status..."
    cd ~/cv-new/cv-magic-app
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 2.1: Git Status - Verify Latest Code"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Current branch:"
    git branch --show-current
    echo ""
    echo "Latest commit:"
    git log -1 --oneline
    echo ""
    echo "Git status:"
    git status --short
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🐳 2.2: Docker Container Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker compose ps
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📁 2.3: Verify New Files Exist (Subcategorization)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ -f "backend/app/services/keyword_subcategorizer.py" ]; then
        echo "✅ keyword_subcategorizer.py exists"
        echo "   File size: $(stat -f%z backend/app/services/keyword_subcategorizer.py 2>/dev/null || stat -c%s backend/app/services/keyword_subcategorizer.py 2>/dev/null || echo 'unknown') bytes"
    else
        echo "❌ keyword_subcategorizer.py NOT FOUND"
    fi
    
    if [ -f "backend/app/services/integration_example_subcategorizer.py" ]; then
        echo "✅ integration_example_subcategorizer.py exists"
    else
        echo "❌ integration_example_subcategorizer.py NOT FOUND"
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 2.4: Check Backend Container Logs (Last 20 lines)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker compose logs --tail=20 backend
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🏥 2.5: Health Check from Inside VPS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if curl -f http://localhost:8000/health 2>/dev/null; then
        echo ""
        echo "✅ Backend health check passed"
    else
        echo "❌ Backend health check failed"
    fi
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 2.6: Verify Python Package Installation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    docker compose exec -T backend python -c "import fastapi; print('✅ FastAPI installed:', fastapi.__version__)" || echo "❌ FastAPI check failed"
    docker compose exec -T backend python -c "import app.services.keyword_subcategorizer; print('✅ keyword_subcategorizer module importable')" || echo "⚠️  keyword_subcategorizer not importable (may need restart)"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ VPS Verification Complete"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
EOF

if [ $? -eq 0 ]; then
    print_success "VPS verification completed"
else
    print_error "VPS verification failed"
fi

# 3. External Health Check
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 3: External Health Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

print_info "Testing external backend endpoint..."
if curl -f -s https://cvagent.duckdns.org/health > /dev/null; then
    print_success "External health check passed"
    echo "Response:"
    curl -s https://cvagent.duckdns.org/health | python3 -m json.tool 2>/dev/null || curl -s https://cvagent.duckdns.org/health
else
    print_error "External health check failed"
fi

# 4. Test API Endpoints
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 4: Test API Endpoints${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

print_info "Testing root endpoint..."
if curl -f -s https://cvagent.duckdns.org/ > /dev/null; then
    print_success "Root endpoint accessible"
    echo "Response:"
    curl -s https://cvagent.duckdns.org/ | python3 -m json.tool 2>/dev/null || curl -s https://cvagent.duckdns.org/
else
    print_error "Root endpoint not accessible"
fi

echo ""
print_info "Testing docs endpoint..."
if curl -f -s https://cvagent.duckdns.org/docs > /dev/null; then
    print_success "API docs accessible at: https://cvagent.duckdns.org/docs"
else
    print_warning "API docs may not be accessible (this is optional)"
fi

# 5. Summary
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Verification Summary                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "✅ Checked Items:"
echo "  1. GitHub Actions deployment status"
echo "  2. VPS deployment verification"
echo "  3. Docker container status"
echo "  4. New files presence (subcategorization)"
echo "  5. Backend health checks"
echo "  6. External API accessibility"
echo ""
echo -e "${GREEN}If all checks passed, your backend is deployed correctly!${NC}"
echo ""
echo "Next steps:"
echo "  - Test specific features (e.g., subcategorization)"
echo "  - Monitor logs: ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose logs -f backend'"
echo "  - Check frontend: https://mahesh989.github.io/cv-new/"
echo ""

