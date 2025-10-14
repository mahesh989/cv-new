# 🚀 CV Magic App - Deployment Guide

This guide covers how to deploy both the backend (VPS) and frontend (GitHub Pages) for the CV Magic App.

## 📋 Prerequisites

- SSH access to VPS (`cvagent.duckdns.org`)
- Git repository access
- Docker installed on VPS

## 🎯 Deployment Strategy

Both backend and frontend deploy from the **`enhanced-vps-ghs`** branch:

- **Backend**: VPS pulls from `enhanced-vps-ghs` branch
- **Frontend**: GitHub Actions deploys from `enhanced-vps-ghs` branch

## 🛠️ Available Deployment Scripts

### 1. Full Deployment (`deploy-vps.sh`)
Complete deployment with cleanup and health checks:

```bash
./cv-magic-app/deploy-vps.sh
```

**What it does:**
- Pulls latest changes from `enhanced-vps-ghs` branch
- Stops existing containers
- Cleans up Docker resources
- Builds new containers with `--no-cache`
- Starts containers
- Runs health checks
- Shows deployment status

### 2. Quick Deployment (`quick-deploy.sh`)
Fast deployment for minor changes:

```bash
./cv-magic-app/quick-deploy.sh
```

**What it does:**
- Pulls latest changes
- Restarts containers with build
- Minimal output for speed

### 3. Status Check (`check-deployment.sh`)
Check deployment status and health:

```bash
./cv-magic-app/check-deployment.sh
```

**What it shows:**
- Git status and recent commits
- Docker container status
- Health check results
- Recent logs
- External connectivity test

## 🔄 Manual Deployment Steps

If you prefer to deploy manually:

```bash
# SSH into VPS
ssh ubuntu@cvagent.duckdns.org

# Navigate to project directory
cd ~/cv-new/cv-magic-app

# Pull latest changes
git checkout enhanced-vps-ghs
git pull origin enhanced-vps-ghs

# Stop existing containers
docker compose down --volumes --remove-orphans

# Clean up Docker resources (optional)
docker system prune -f

# Build and start containers
docker compose build --no-cache
docker compose up -d

# Check status
docker compose ps
docker compose logs --tail=20
```

## 🌐 Frontend Deployment

Frontend automatically deploys via GitHub Actions when you push to `enhanced-vps-ghs` branch:

1. Push changes to `enhanced-vps-ghs`:
   ```bash
   git push origin enhanced-vps-ghs
   ```

2. GitHub Actions automatically:
   - Builds the Flutter web app
   - Deploys to GitHub Pages
   - Available at: `https://mahesh989.github.io/cv-new/`

## 🔍 Troubleshooting

### Check Backend Health
```bash
curl https://cvagent.duckdns.org/health
```

### View Backend Logs
```bash
ssh ubuntu@cvagent.duckdns.org 'cd ~/cv-new/cv-magic-app && docker compose logs -f'
```

### Restart Backend
```bash
ssh ubuntu@cvagent.duckdns.org 'cd ~/cv-new/cv-magic-app && docker compose restart'
```

### Check Frontend Deployment
- Visit: https://mahesh989.github.io/cv-new/
- Check GitHub Actions: https://github.com/mahesh989/cv-new/actions

## 📊 Deployment Status URLs

- **Backend Health**: https://cvagent.duckdns.org/health
- **Frontend**: https://mahesh989.github.io/cv-new/
- **GitHub Actions**: https://github.com/mahesh989/cv-new/actions

## 🚨 Common Issues

### 1. SSH Connection Failed
- Ensure SSH key is added to VPS
- Check VPS is running: `ping cvagent.duckdns.org`

### 2. Docker Build Failed
- Check Docker is running on VPS
- Ensure sufficient disk space
- Try: `docker system prune -f`

### 3. Frontend Not Updating
- Check GitHub Actions status
- Ensure changes are pushed to `enhanced-vps-ghs` branch
- Wait 2-3 minutes for deployment to complete

### 4. Backend Not Accessible
- Check container status: `docker compose ps`
- Check logs: `docker compose logs`
- Verify Nginx is running: `docker compose logs nginx`

## 📝 Quick Commands Reference

```bash
# Full deployment
./cv-magic-app/deploy-vps.sh

# Quick deployment
./cv-magic-app/quick-deploy.sh

# Check status
./cv-magic-app/check-deployment.sh

# Manual SSH
ssh ubuntu@cvagent.duckdns.org

# View logs
ssh ubuntu@cvagent.duckdns.org 'cd ~/cv-new/cv-magic-app && docker compose logs -f'

# Restart services
ssh ubuntu@cvagent.duckdns.org 'cd ~/cv-new/cv-magic-app && docker compose restart'
```

## 🎉 Success Indicators

✅ **Backend Deployed Successfully:**
- `curl https://cvagent.duckdns.org/health` returns 200 OK
- Docker containers are running
- No errors in logs

✅ **Frontend Deployed Successfully:**
- GitHub Actions shows green checkmark
- https://mahesh989.github.io/cv-new/ loads correctly
- AI features work with backend

---

**Happy Deploying! 🚀**
