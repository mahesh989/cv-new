#!/bin/bash

# Setup SSL certificates for cvagent.duckdns.org
# This script will install Certbot and obtain SSL certificates

echo "🔐 Setting up SSL certificates for cvagent.duckdns.org"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script as root (use sudo)"
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
apt update

# Install Certbot and Nginx plugin
echo "🔧 Installing Certbot..."
apt install -y certbot python3-certbot-nginx

# Stop nginx if running
echo "⏹️ Stopping nginx..."
systemctl stop nginx

# Obtain SSL certificate
echo "🔐 Obtaining SSL certificate for cvagent.duckdns.org..."
certbot certonly --standalone -d cvagent.duckdns.org --non-interactive --agree-tos --email your-email@example.com

# Check if certificate was obtained successfully
if [ -f "/etc/letsencrypt/live/cvagent.duckdns.org/fullchain.pem" ]; then
    echo "✅ SSL certificate obtained successfully!"
    
    # Set up auto-renewal
    echo "🔄 Setting up auto-renewal..."
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
    
    echo "🎉 SSL setup complete!"
    echo "📋 Next steps:"
    echo "1. Update your docker-compose.yml to use the HTTPS configuration"
    echo "2. Restart your services with: docker-compose -f docker-compose-https.yml up -d"
    echo "3. Update your Flutter app config to use https://cvagent.duckdns.org"
else
    echo "❌ Failed to obtain SSL certificate"
    echo "🔍 Please check:"
    echo "  - Domain cvagent.duckdns.org points to this server"
    echo "  - Port 80 is accessible from the internet"
    echo "  - No firewall is blocking the connection"
    exit 1
fi
