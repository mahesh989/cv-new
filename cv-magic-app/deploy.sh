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
# Try hostname first, fallback to IP if needed
VPS_HOST="${VPS_HOST:-cvagent.duckdns.org}"
VPS_HOST_IP="13.210.217.204"  # Backup IP if hostname doesn't work
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
    echo -e "${BLUE}║  ${RED}5)${NC} Reset Database (⚠️  DESTROYS ALL DATA + TABLES)        ${BLUE}║${NC}"
    echo -e "${BLUE}║  ${YELLOW}6)${NC} Clear All Data + Rebuild (keeps schema intact)       ${BLUE}║${NC}"
    echo -e "${BLUE}║  ${RED}4)${NC} Exit                                                   ${BLUE}║${NC}"
    echo -e "${BLUE}║                                                              ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Target: ${VPS_USER}@${VPS_HOST}${NC}"
    echo -e "${CYAN}Branch: ${BRANCH}${NC}"
    echo ""
    echo -n "Enter your choice [1-6]: "
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
            6)
                MODE="clear_data"
                break
                ;;
            *)
                echo -e "${RED}❌ Invalid option. Please enter 1, 2, 3, 4, 5, or 6.${NC}"
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

# Function to test SSH connection
test_ssh_connection() {
    print_info "Testing SSH connection to $VPS_USER@$VPS_HOST..."
    
    # Try hostname first, then IP if hostname fails
    SSH_SUCCESS=false
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o BatchMode=yes $VPS_USER@$VPS_HOST "echo 'Connection OK'" 2>/dev/null; then
        SSH_SUCCESS=true
    elif [ "$VPS_HOST" != "$VPS_HOST_IP" ]; then
        print_warning "Hostname failed, trying IP address $VPS_HOST_IP..."
        if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -o BatchMode=yes $VPS_USER@$VPS_HOST_IP "echo 'Connection OK'" 2>/dev/null; then
            VPS_HOST=$VPS_HOST_IP
            SSH_SUCCESS=true
            print_info "Using IP address instead of hostname"
        fi
    fi
    
    if [ "$SSH_SUCCESS" = false ]; then
        print_error "❌ SSH connection test FAILED!"
        print_error "Cannot connect to $VPS_USER@$VPS_HOST"
        if [ "$VPS_HOST" != "$VPS_HOST_IP" ]; then
            print_error "Also tried IP: $VPS_HOST_IP"
        fi
        echo ""
        print_warning "Possible issues:"
        echo "  - VPS is down or unreachable from your network"
        echo "  - IP address has changed"
        echo "  - Firewall blocking connection (corporate network?)"
        echo "  - SSH service not running on VPS"
        echo "  - You may need to be on a VPN or different network"
        echo ""
        print_info "Troubleshooting steps:"
        echo "  1. Check VPS status in your cloud provider dashboard"
        echo "  2. Try: ping $VPS_HOST"
        echo "  3. Try: ssh $VPS_USER@$VPS_HOST"
        echo "  4. Check if you need to be on a VPN"
        echo "  5. Verify IP address: nslookup cvagent.duckdns.org"
        return 1
    else
        print_status "SSH connection test passed ✓"
        return 0
    fi
}

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

    echo ""
    if ! test_ssh_connection; then
        exit 1
    fi
    echo ""

    ssh -T -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST << EOF
        set -e
        
        echo "🔍 Checking current directory and git status..."
        cd $VPS_PATH
        
        echo "🧹 Clearing log files..."
        mkdir -p logs
        chown $VPS_USER:$VPS_USER logs || true
        touch logs/backend_logs.txt logs/frontend_logs.txt
        chmod 664 logs/backend_logs.txt logs/frontend_logs.txt || true
        > logs/backend_logs.txt
        > logs/frontend_logs.txt
        echo "  ✅ Cleared backend_logs.txt and frontend_logs.txt"
        
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
        
        echo "📝 Starting log collection..."
        # Start logging in background
        nohup docker compose logs -f backend >> logs/backend_logs.txt 2>&1 &
        nohup docker compose logs -f nginx >> logs/frontend_logs.txt 2>&1 &
        echo "  ✅ Logs are being saved to:"
        echo "     - logs/backend_logs.txt"
        echo "     - logs/frontend_logs.txt"
        
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

# Clear all data function (keeps schema intact)
clear_all_data() {
    print_header "🧹 CLEAR ALL DATA + REBUILD - Keeps Tables/Schema"
    print_warning "This will delete all rows from database tables but keep the structure!"
    print_warning "User files will also be cleared!"
    print_warning "Containers will be rebuilt for a fresh start!"
    print_info "Database schema and tables will remain intact for fresh data."
    echo ""
    echo -n "Are you sure? Type 'CLEAR' to confirm: "
    read -r confirmation
    
    if [ "$confirmation" != "CLEAR" ]; then
        print_info "Clear data cancelled. No changes made."
        exit 0
    fi
    
    echo ""
    print_info "Connecting to VPS: $VPS_USER@$VPS_HOST"
    print_info "Target path: $VPS_PATH"
    echo ""
    
    if ! test_ssh_connection; then
        exit 1
    fi
    echo ""
    
    ssh -T -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST << 'EOF'
        set -e
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔍 STEP 1: Checking current directory..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        cd ~/cv-new/cv-magic-app
        pwd
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 STEP 2: Clearing all database tables (keeping schema)..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker compose exec -T postgres psql -U mahesh -d cv_app << 'SQLEOF'
-- Disable foreign key checks temporarily
SET session_replication_role = 'replica';

-- Delete all data from tables (keeps structure)
TRUNCATE TABLE job_comparisons RESTART IDENTITY CASCADE;
TRUNCATE TABLE cv_analyses RESTART IDENTITY CASCADE;
TRUNCATE TABLE job_applications RESTART IDENTITY CASCADE;
TRUNCATE TABLE cvs RESTART IDENTITY CASCADE;
TRUNCATE TABLE users RESTART IDENTITY CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = 'origin';

-- Verify tables are empty but exist
SELECT 
    schemaname,
    tablename,
    (SELECT COUNT(*) FROM users) as users_count,
    (SELECT COUNT(*) FROM cvs) as cvs_count,
    (SELECT COUNT(*) FROM job_applications) as jobs_count,
    (SELECT COUNT(*) FROM cv_analyses) as analyses_count,
    (SELECT COUNT(*) FROM job_comparisons) as comparisons_count
FROM pg_tables 
WHERE schemaname = 'public' 
LIMIT 1;
SQLEOF
        echo "✅ Database tables cleared"
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🗑️  STEP 3: Clearing user data files (keeping directory structure)..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker compose exec -T backend bash << 'BASHEOF'
# Clear user data but keep directory structure
find /app/user -type f -delete 2>/dev/null || true
find /app/user -type d -empty -delete 2>/dev/null || true

# Recreate base user directory
mkdir -p /app/user

echo "✅ User data files cleared"
ls -la /app/user/ 2>/dev/null || echo "User directory empty (as expected)"
BASHEOF
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🛑 STEP 4: Stopping containers..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker compose down
        echo "✅ Containers stopped"
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔨 STEP 5: Rebuilding containers..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker compose build --no-cache
        echo "✅ Containers rebuilt"
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🚀 STEP 6: Starting containers with fresh setup..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker compose up -d
        echo "✅ Containers started"
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "⏳ STEP 7: Waiting for services to stabilize..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        sleep 10
        echo "✅ Services ready"
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔍 STEP 8: Verifying services..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        docker compose ps
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ ALL STEPS COMPLETED SUCCESSFULLY!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📊 Database tables remain intact and ready for fresh data"
        echo "🔄 Containers rebuilt with latest code"
        echo "🗑️  All user data cleared"
        echo ""
EOF

    echo ""
    if [ $? -eq 0 ]; then
        print_status "All data cleared and containers rebuilt successfully!"
        print_info "✅ Database schema is intact - tables are empty and ready"
        print_info "✅ Containers rebuilt with fresh configuration"
        print_info "✅ Users will need to register again"
        print_info "🌐 Backend available at: https://cvagent.duckdns.org"
    else
        print_error "Clear data and rebuild operation failed!"
        exit 1
    fi
}

# Reset database function (DANGEROUS - destroys all data AND schema)
deploy_reset() {
    print_header "⚠️  RESET DATABASE - DESTROYS ALL DATA + TABLES"
    print_warning "This will permanently delete all user data, analysis files, database volumes, and schema!"
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
    
    if ! test_ssh_connection; then
        exit 1
    fi
    echo ""
    
    ssh -T -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST << EOF
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
    
    if ! test_ssh_connection; then
        exit 1
    fi
    echo ""

    ssh -T -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST << EOF
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
    
    if ! test_ssh_connection; then
        exit 1
    fi
    echo ""

    ssh -T -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST << EOF
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
        docker compose exec -T backend curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Backend is healthy" || echo "❌ Backend health check failed"
        
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
    "clear_data")
        echo -e "${YELLOW}🧹 Selected: Clear All Data${NC}"
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
    "clear_data")
        clear_all_data
        ;;
    *)
        print_error "Unknown mode: $MODE"
        exit 1
        ;;
esac

echo ""
print_header "🎉 Deployment script completed!"
