#!/bin/bash

# CV Magic App - Unified Deployment Script
# Usage: ./deploy.sh [--quick|--full|--check|--help]

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="13.210.217.204"
VPS_USER="ubuntu"
VPS_PATH="~/cv-new/cv-magic-app"
BRANCH="enhanced-vps-ghs"

# Default mode
MODE="full"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            MODE="quick"
            shift
            ;;
        --full)
            MODE="full"
            shift
            ;;
        --check)
            MODE="check"
            shift
            ;;
        --help|-h)
            echo "CV Magic App - Unified Deployment Script"
            echo ""
            echo "Usage: ./deploy.sh [OPTION]"
            echo ""
            echo "Options:"
            echo "  --quick    Quick deployment (fast, minimal cleanup)"
            echo "  --full     Full deployment (thorough, with cleanup) [default]"
            echo "  --check    Check deployment status only"
            echo "  --help     Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./deploy.sh           # Full deployment"
            echo "  ./deploy.sh --quick   # Quick deployment"
            echo "  ./deploy.sh --check   # Check status"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..50})${NC}"
}

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ] && [ ! -f ~/.ssh/id_ed25519 ]; then
    print_warning "No SSH key found. Make sure you have SSH access to the VPS."
fi

# Main deployment function
deploy_full() {
    print_header "🚀 Full VPS Deployment"
    print_info "Connecting to VPS: $VPS_USER@$VPS_HOST"
    print_info "Deploying branch: $BRANCH"
    print_info "Target path: $VPS_PATH"

    ssh $VPS_USER@$VPS_HOST << EOF
        set -e
        
        echo "🔍 Checking current directory and git status..."
        cd $VPS_PATH
        
        echo "📥 Pulling latest changes from $BRANCH branch..."
        git fetch origin
        git checkout $BRANCH
        git pull origin $BRANCH
        
        echo "🛑 Stopping existing containers..."
        docker compose down --volumes --remove-orphans || true
        
        echo "🧹 Cleaning up Docker resources..."
        docker system prune -f || true
        
        echo "🔨 Building new containers..."
        docker compose build --no-cache
        
        echo "🚀 Starting containers..."
        docker compose up -d
        
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        echo "🔍 Checking container status..."
        docker compose ps
        
        echo "📋 Checking logs for any errors..."
        docker compose logs --tail=20
        
        echo "🌐 Testing backend connectivity..."
        curl -f http://localhost:8000/health || echo "Health check failed, but deployment might still be successful"
        
        echo "✅ Full deployment completed!"
EOF

    if [ $? -eq 0 ]; then
        print_status "Full VPS deployment completed successfully!"
        print_info "Backend should be available at: https://cvagent.duckdns.org"
    else
        print_error "Full VPS deployment failed!"
        exit 1
    fi
}

# Quick deployment function
deploy_quick() {
    print_header "⚡ Quick VPS Deployment"
    print_info "Connecting to VPS: $VPS_USER@$VPS_HOST"

    ssh $VPS_USER@$VPS_HOST << EOF
        cd $VPS_PATH
        echo "📥 Pulling latest changes..."
        git pull origin $BRANCH
        echo "🔄 Restarting containers..."
        docker compose down
        docker compose up -d --build
        echo "✅ Quick deployment completed!"
EOF

    if [ $? -eq 0 ]; then
        print_status "Quick VPS deployment completed successfully!"
        print_info "Backend should be available at: https://cvagent.duckdns.org"
    else
        print_error "Quick VPS deployment failed!"
        exit 1
    fi
}

# Check deployment status function
check_deployment() {
    print_header "🔍 Checking VPS Deployment Status"

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
        curl -f https://cvagent.duckdns.org/health 2>/dev/null && echo "✅ External access working" || echo "❌ External access failed"
EOF

    echo ""
    print_info "Quick commands:"
    echo "  View logs: ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose logs -f'"
    echo "  Restart:   ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose restart'"
    echo "  Full logs: ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose logs --tail=100'"
}

# Execute based on mode
case $MODE in
    "full")
        deploy_full
        ;;
    "quick")
        deploy_quick
        ;;
    "check")
        check_deployment
        ;;
    *)
        print_error "Unknown mode: $MODE"
        exit 1
        ;;
esac

echo ""
print_header "🎉 Deployment script completed!"
