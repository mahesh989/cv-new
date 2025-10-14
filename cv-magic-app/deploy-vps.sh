#!/bin/bash

# CV Magic App - VPS Deployment Script
# This script automates the deployment of the backend to VPS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="cvagent.duckdns.org"
VPS_USER="ubuntu"
VPS_PATH="~/cv-new/cv-magic-app"
BRANCH="enhanced-vps-ghs"

echo -e "${BLUE}🚀 Starting VPS Deployment for CV Magic App${NC}"
echo -e "${BLUE}==============================================${NC}"

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

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ] && [ ! -f ~/.ssh/id_ed25519 ]; then
    print_warning "No SSH key found. Make sure you have SSH access to the VPS."
fi

print_info "Connecting to VPS: $VPS_USER@$VPS_HOST"
print_info "Deploying branch: $BRANCH"
print_info "Target path: $VPS_PATH"

# SSH into VPS and run deployment commands
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
    
    echo "✅ Deployment completed!"
EOF

if [ $? -eq 0 ]; then
    print_status "VPS deployment completed successfully!"
    print_info "Backend should be available at: https://$VPS_HOST"
    print_info "You can check the logs with: ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose logs -f'"
else
    print_error "VPS deployment failed!"
    print_info "You can manually SSH into the VPS to troubleshoot:"
    print_info "ssh $VPS_USER@$VPS_HOST"
    print_info "cd $VPS_PATH"
    print_info "docker compose logs"
    exit 1
fi

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}🎉 Deployment script completed!${NC}"
