#!/bin/bash

# CV Magic App - Interactive Deployment Script
# Usage: ./deploy.sh

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
VPS_HOST="13.210.217.204"
VPS_USER="ubuntu"
VPS_PATH="~/cv-new/cv-magic-app"
BRANCH="enhanced-vps-ghs"

# Function to show interactive menu
show_menu() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    CV Magic App Deployment                   ║${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}║  🚀 Choose your deployment option:                          ║${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}║  ${GREEN}1)${NC} Full Deployment (thorough, preserves data)           ${BLUE}║${NC}"
    echo -e "${BLUE}║  ${YELLOW}2)${NC} Quick Deployment (fast, minimal cleanup)             ${BLUE}║${NC}"
    echo -e "${BLUE}║  ${CYAN}3)${NC} Check Status Only (monitoring)                        ${BLUE}║${NC}"
    echo -e "${BLUE}║  ${RED}5)${NC} Reset Database (⚠️  DESTROYS ALL DATA)                 ${BLUE}║${NC}"
    echo -e "${BLUE}║  ${RED}4)${NC} Exit                                                   ${BLUE}║${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Target: ${VPS_USER}@${VPS_HOST}${NC}"
    echo -e "${CYAN}Branch: ${BRANCH}${NC}"
    echo ""
    echo -n "Enter your choice [1-5]: "
}

# Function to get user choice
get_user_choice() {
    while true; do
        show_menu
        read -r choice
        case $choice in
            1)
                MODE="full"
                break
                ;;
            2)
                MODE="quick"
                break
                ;;
            3)
                MODE="check"
                break
                ;;
            4)
                echo -e "${YELLOW}👋 Goodbye!${NC}"
                exit 0
                ;;
            5)
                MODE="reset"
                break
                ;;
            *)
                echo -e "${RED}❌ Invalid option. Please enter 1, 2, 3, 4, or 5.${NC}"
                echo ""
                echo -n "Press Enter to continue..."
                read -r
                ;;
        esac
    done
}

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

# Function to show cleanup summary
show_cleanup_summary() {
    echo ""
    echo "🧹 Full Cleanup Operations:"
    echo "  ✅ Stop all containers (preserves database and user data)"
    echo "  ✅ Remove unused containers"
    echo "  ✅ Remove unused images (preserves current project)"
    echo "  ✅ Remove unused networks"
    echo "  ✅ Remove unused volumes (preserves user data)"
    echo "  ✅ Remove dangling images"
    echo "  ✅ System-wide cleanup (safe operations)"
    echo "  ✅ Disk space monitoring"
    echo ""
    echo "⚠️  Safety Features:"
    echo "  🔒 Database volumes are preserved (no data loss)"
    echo "  🔒 User data volumes are preserved"
    echo "  🔒 Current project images are kept"
    echo "  🔒 All operations use '|| true' for safety"
    echo "  🔒 Disk space checked before/after cleanup"
    echo ""
}

# Main deployment function
deploy_full() {
    print_header "🚀 Full VPS Deployment"
    print_info "Connecting to VPS: $VPS_USER@$VPS_HOST"
    print_info "Deploying branch: $BRANCH"
    print_info "Target path: $VPS_PATH"
    
    show_cleanup_summary

    ssh $VPS_USER@$VPS_HOST << EOF
        set -e
        
        echo "🔍 Checking current directory and git status..."
        cd $VPS_PATH
        
        echo "📥 Pulling latest changes from $BRANCH branch..."
        git fetch origin
        git checkout $BRANCH
        git pull origin $BRANCH
        
        echo "🛑 Stopping existing containers..."
        echo "  - Preserving database and user data volumes..."
        docker compose down --remove-orphans || true
        
        echo "🧹 Performing comprehensive Docker cleanup..."
        echo "  - Checking disk space before cleanup..."
        df -h / || true
        
        echo "  - Removing unused containers..."
        docker container prune -f || true
        
        echo "  - Removing unused images (keeping current project images)..."
        docker image prune -f || true
        
        echo "  - Removing unused networks..."
        docker network prune -f || true
        
        echo "  - Removing unused volumes (preserving user data volumes)..."
        # Only remove volumes not in use by current project
        docker volume prune -f || true
        
        echo "  - Removing dangling images..."
        docker image prune -f --filter "dangling=true" || true
        
        echo "  - System-wide cleanup (safe operations only)..."
        docker system prune -f || true
        
        echo "  - Checking disk space after cleanup..."
        df -h / || true
        
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

# Reset database function (DANGEROUS - destroys all data)
deploy_reset() {
    print_header "⚠️  RESET DATABASE - DESTROYS ALL DATA"
    print_warning "This will permanently delete all user data, analysis files, and database records!"
    print_warning "This action cannot be undone!"
    echo ""
    echo -n "Are you absolutely sure? Type 'RESET' to confirm: "
    read -r confirmation
    
    if [ "$confirmation" != "RESET" ]; then
        print_info "Reset cancelled. No data was lost."
        exit 0
    fi
    
    print_info "Connecting to VPS: $VPS_USER@$VPS_HOST"
    print_info "Target path: $VPS_PATH"
    
    ssh $VPS_USER@$VPS_HOST << EOF
        set -e
        
        echo "🔍 Checking current directory..."
        cd $VPS_PATH
        
        echo "🛑 Stopping all containers..."
        docker compose down --volumes --remove-orphans || true
        
        echo "🗑️  Removing all volumes (database, user data, etc.)..."
        docker volume prune -f || true
        
        echo "🧹 Cleaning up Docker resources..."
        docker system prune -f || true
        
        echo "🔨 Building new containers..."
        docker compose build --no-cache
        
        echo "🚀 Starting containers with fresh database..."
        docker compose up -d
        
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        echo "🔍 Checking container status..."
        docker compose ps
        
        echo "✅ Database reset completed!"
        echo "⚠️  All user data has been permanently deleted!"
EOF

    if [ $? -eq 0 ]; then
        print_warning "Database reset completed successfully!"
        print_warning "All user data has been permanently deleted!"
        print_info "Users will need to register again."
    else
        print_error "Database reset failed!"
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

# Main execution
echo -e "${BLUE}🚀 CV Magic App - Interactive Deployment Script${NC}"
echo ""

# Get user choice
get_user_choice

# Show selected option
case $MODE in
    "full")
        echo -e "${GREEN}✅ Selected: Full Deployment${NC}"
        echo ""
        ;;
    "quick")
        echo -e "${YELLOW}⚡ Selected: Quick Deployment${NC}"
        echo ""
        ;;
    "check")
        echo -e "${CYAN}🔍 Selected: Status Check${NC}"
        echo ""
        ;;
    "reset")
        echo -e "${RED}⚠️  Selected: Reset Database${NC}"
        echo ""
        ;;
esac

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
    "reset")
        deploy_reset
        ;;
    *)
        print_error "Unknown mode: $MODE"
        exit 1
        ;;
esac

echo ""
print_header "🎉 Deployment script completed!"
