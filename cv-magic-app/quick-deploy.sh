#!/bin/bash

# Quick VPS Deployment Script
# Simplified version for faster deployments

set -e

VPS_HOST="cvagent.duckdns.org"
VPS_USER="ubuntu"
VPS_PATH="~/cv-new/cv-magic-app"
BRANCH="enhanced-vps-ghs"

echo "🚀 Quick VPS Deployment..."

ssh $VPS_USER@$VPS_HOST << EOF
    cd $VPS_PATH
    git pull origin $BRANCH
    docker compose down
    docker compose up -d --build
    echo "✅ Quick deployment completed!"
EOF

echo "🎉 Done! Backend should be live at https://$VPS_HOST"
