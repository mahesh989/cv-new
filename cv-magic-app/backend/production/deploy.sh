#!/bin/bash
# Production Deployment Script for CV Management API
# Phase 9: Final Production Deployment & Launch

set -e  # Exit on any error

# Configuration
APP_NAME="cv-management-api"
VERSION=${1:-"latest"}
ENVIRONMENT=${2:-"production"}
BACKUP_DIR="/var/backups/cv-app"
LOG_DIR="/var/log/cv-app"
DEPLOY_DIR="/opt/cv-app"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Starting pre-deployment checks..."
    
    # Check if running as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root or with sudo"
        exit 1
    fi
    
    # Check system requirements
    check_system_requirements
    
    # Check dependencies
    check_dependencies
    
    # Check disk space
    check_disk_space
    
    # Check network connectivity
    check_network_connectivity
    
    success "Pre-deployment checks completed successfully"
}

check_system_requirements() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ ! -f /etc/os-release ]]; then
        error "Cannot determine OS version"
        exit 1
    fi
    
    # Check memory
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $MEMORY_GB -lt 4 ]]; then
        warning "System has less than 4GB RAM (${MEMORY_GB}GB detected)"
    fi
    
    # Check CPU cores
    CPU_CORES=$(nproc)
    if [[ $CPU_CORES -lt 2 ]]; then
        warning "System has less than 2 CPU cores (${CPU_CORES} detected)"
    fi
    
    success "System requirements check completed"
}

check_dependencies() {
    log "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
        exit 1
    fi
    
    # Check PostgreSQL client
    if ! command -v psql &> /dev/null; then
        warning "PostgreSQL client not found - database operations may be limited"
    fi
    
    success "Dependencies check completed"
}

check_disk_space() {
    log "Checking disk space..."
    
    # Check available disk space
    AVAILABLE_SPACE=$(df / | awk 'NR==2{print $4}')
    REQUIRED_SPACE=10485760  # 10GB in KB
    
    if [[ $AVAILABLE_SPACE -lt $REQUIRED_SPACE ]]; then
        error "Insufficient disk space. Required: 10GB, Available: $(($AVAILABLE_SPACE / 1024 / 1024))GB"
        exit 1
    fi
    
    success "Disk space check completed"
}

check_network_connectivity() {
    log "Checking network connectivity..."
    
    # Check internet connectivity
    if ! ping -c 1 8.8.8.8 &> /dev/null; then
        error "No internet connectivity"
        exit 1
    fi
    
    # Check if ports are available
    PORTS=(8000 5432 6379 80 443)
    for port in "${PORTS[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            warning "Port $port is already in use"
        fi
    done
    
    success "Network connectivity check completed"
}

# Backup existing deployment
backup_existing_deployment() {
    log "Creating backup of existing deployment..."
    
    if [[ -d "$DEPLOY_DIR" ]]; then
        BACKUP_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
        
        mkdir -p "$BACKUP_PATH"
        
        # Backup application files
        cp -r "$DEPLOY_DIR" "$BACKUP_PATH/app"
        
        # Backup database
        if docker ps | grep -q postgres; then
            docker exec postgres pg_dump -U cv_app_user cv_app_prod > "$BACKUP_PATH/database.sql"
        fi
        
        # Backup configuration
        cp -r /etc/cv-app "$BACKUP_PATH/config" 2>/dev/null || true
        
        success "Backup created at $BACKUP_PATH"
    else
        log "No existing deployment found, skipping backup"
    fi
}

# Deploy new version
deploy_new_version() {
    log "Deploying new version $VERSION..."
    
    # Create deployment directory
    mkdir -p "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
    
    # Clone or update repository
    if [[ -d ".git" ]]; then
        log "Updating existing repository..."
        git fetch origin
        git checkout "$VERSION"
        git pull origin "$VERSION"
    else
        log "Cloning repository..."
        git clone https://github.com/your-org/cv-management-api.git .
        git checkout "$VERSION"
    fi
    
    # Set permissions
    chown -R cv-app:cv-app "$DEPLOY_DIR"
    chmod -R 755 "$DEPLOY_DIR"
    
    success "Code deployment completed"
}

# Build and start services
build_and_start_services() {
    log "Building and starting services..."
    
    cd "$DEPLOY_DIR"
    
    # Build Docker images
    log "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # Start services
    log "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Check service health
    check_service_health
    
    success "Services started successfully"
}

check_service_health() {
    log "Checking service health..."
    
    # Check if all containers are running
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        error "Some services failed to start"
        docker-compose -f docker-compose.prod.yml ps
        exit 1
    fi
    
    # Check API health
    for i in {1..30}; do
        if curl -f http://localhost:8000/monitoring/health &> /dev/null; then
            success "API health check passed"
            return 0
        fi
        log "Waiting for API to be ready... ($i/30)"
        sleep 10
    done
    
    error "API health check failed"
    exit 1
}

# Configure production environment
configure_production() {
    log "Configuring production environment..."
    
    # Create production configuration
    cat > "$DEPLOY_DIR/.env.production" << EOF
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://cv_app_user:secure_password@postgres:5432/cv_app_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security Configuration
JWT_SECRET_KEY=${JWT_SECRET_KEY:-$(openssl rand -base64 32)}
RATE_LIMIT_ENABLED=true
SECURITY_HEADERS_ENABLED=true

# Email Configuration
SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}
SMTP_PORT=587
SMTP_USERNAME=${SMTP_USERNAME}
SMTP_PASSWORD=${SMTP_PASSWORD}
FROM_EMAIL=${FROM_EMAIL:-noreply@cvapp.com}
FROM_NAME=CV App

# Monitoring Configuration
MONITORING_ENABLED=true
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true

# Performance Configuration
WORKERS=4
MAX_REQUEST_SIZE=10485760
REQUEST_TIMEOUT=30
KEEP_ALIVE_TIMEOUT=5

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# Session Configuration
SESSION_TIMEOUT=28800
MAX_SESSIONS_PER_USER=5
SESSION_CLEANUP_INTERVAL=3600
EOF
    
    # Set proper permissions
    chown cv-app:cv-app "$DEPLOY_DIR/.env.production"
    chmod 600 "$DEPLOY_DIR/.env.production"
    
    success "Production configuration completed"
}

# Setup monitoring and logging
setup_monitoring() {
    log "Setting up monitoring and logging..."
    
    # Create log directories
    mkdir -p "$LOG_DIR"
    chown -R cv-app:cv-app "$LOG_DIR"
    
    # Setup log rotation
    cat > /etc/logrotate.d/cv-app << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 cv-app cv-app
    postrotate
        docker-compose -f $DEPLOY_DIR/docker-compose.prod.yml restart cv-api
    endscript
}
EOF
    
    # Setup systemd service for monitoring
    cat > /etc/systemd/system/cv-app-monitor.service << EOF
[Unit]
Description=CV App Monitoring Service
After=network.target

[Service]
Type=simple
User=cv-app
Group=cv-app
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/bin/python3 $DEPLOY_DIR/scripts/monitoring.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable cv-app-monitor
    systemctl start cv-app-monitor
    
    success "Monitoring setup completed"
}

# Setup SSL/TLS
setup_ssl() {
    log "Setting up SSL/TLS..."
    
    # Create SSL directory
    mkdir -p /etc/nginx/ssl
    
    # Generate self-signed certificate (for testing)
    if [[ ! -f /etc/nginx/ssl/cv-app.crt ]]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/cv-app.key \
            -out /etc/nginx/ssl/cv-app.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=cvapp.com"
    fi
    
    # Configure Nginx with SSL
    cat > /etc/nginx/sites-available/cv-app << EOF
server {
    listen 80;
    server_name _;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;
    
    ssl_certificate /etc/nginx/ssl/cv-app.crt;
    ssl_certificate_key /etc/nginx/ssl/cv-app.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    # Enable site
    ln -sf /etc/nginx/sites-available/cv-app /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    
    success "SSL/TLS setup completed"
}

# Run post-deployment tests
run_post_deployment_tests() {
    log "Running post-deployment tests..."
    
    cd "$DEPLOY_DIR"
    
    # Run comprehensive tests
    python3 test_phase8.py
    
    # Run production readiness validation
    python3 scripts/validate_production_readiness.py --url http://localhost:8000
    
    success "Post-deployment tests completed"
}

# Main deployment function
main() {
    log "Starting production deployment for $APP_NAME v$VERSION"
    
    # Pre-deployment checks
    pre_deployment_checks
    
    # Backup existing deployment
    backup_existing_deployment
    
    # Deploy new version
    deploy_new_version
    
    # Configure production
    configure_production
    
    # Build and start services
    build_and_start_services
    
    # Setup monitoring
    setup_monitoring
    
    # Setup SSL/TLS
    setup_ssl
    
    # Run post-deployment tests
    run_post_deployment_tests
    
    success "Production deployment completed successfully!"
    log "Application is now running at https://localhost"
    log "Health check: https://localhost/monitoring/health"
    log "API documentation: https://localhost/docs"
}

# Run main function
main "$@"
