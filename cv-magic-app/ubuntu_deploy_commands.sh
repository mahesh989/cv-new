#!/bin/bash

# Ubuntu Server Deployment Commands
# Run these commands on your Ubuntu server: ubuntu@ip-172-31-14-251

echo "🚀 Deploying CV Magic App Fix to Ubuntu Server"
echo "=============================================="

# 1. Navigate to the project directory
echo "📁 Navigating to project directory..."
cd ~/cv-new/cv-magic-app

# 2. Pull the latest changes
echo "📥 Pulling latest changes..."
git pull origin enhanced-vps-ghs

# 3. Check the status
echo "📊 Checking git status..."
git status

# 4. Check if Docker containers are running
echo "🐳 Checking Docker containers..."
docker ps

# 5. Restart the application
echo "🔄 Restarting application..."
docker-compose down
docker-compose up -d

# 6. Check if containers are running
echo "✅ Checking if containers are running..."
sleep 10
docker ps

# 7. Check application logs
echo "📋 Checking application logs..."
docker logs --tail 20 cv-magic-app

# 8. Test the server
echo "🌐 Testing server health..."
curl -s http://localhost:8000/health || echo "Server not responding"

echo ""
echo "🎉 Deployment complete!"
echo "The 'NoneType' object is not iterable error should now be fixed."
echo "You can now test the job tracking tab in your application."
