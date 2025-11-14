# VPS Docker Management Guide

## Quick SSH Access

Based on your configuration, here's how to SSH into your VPS:

```bash
ssh ubuntu@cvagent.duckdns.org
```

Or if the hostname doesn't work, use the IP:
```bash
ssh ubuntu@13.210.217.204
```

**Note:** Make sure you have SSH keys set up. If you need to use a password or specific key:
```bash
ssh -i ~/.ssh/your_key.pem ubuntu@cvagent.duckdns.org
```

---

## Once Connected: Navigate to Your Project

```bash
cd ~/cv-new/cv-magic-app
```

---

## Essential Docker Commands on VPS

### 1. **View Running Containers**
```bash
docker compose ps
```
or
```bash
docker ps
```

### 2. **View All Containers (including stopped)**
```bash
docker ps -a
```

### 3. **View Container Logs**
```bash
# All services
docker compose logs

# Follow logs in real-time
docker compose logs -f

# Specific service (backend, postgres, redis, nginx)
docker compose logs backend
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100

# Last 50 lines of backend only
docker compose logs --tail=50 backend
```

### 4. **Restart Containers**
```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart backend
```

### 5. **Stop Containers**
```bash
docker compose down
```

### 6. **Start Containers**
```bash
docker compose up -d
```

### 7. **Rebuild and Start**
```bash
docker compose up -d --build
```

### 8. **Execute Commands Inside a Container**
```bash
# Access backend container shell
docker compose exec backend bash

# Access postgres container
docker compose exec postgres psql -U mahesh -d cv_app

# Run a one-off command
docker compose exec backend python -m app.migrate
```

### 9. **View Container Resource Usage**
```bash
docker stats
```

### 10. **Check Container Health**
```bash
# Check if backend is responding
docker compose exec backend curl -f http://localhost:8000/health

# Or from outside the container
curl http://localhost:8000/health
```

### 11. **View Docker Images**
```bash
docker images
```

### 12. **View Docker Volumes**
```bash
docker volume ls
```

### 13. **Inspect a Container**
```bash
docker inspect cv_backend
```

### 14. **View Container Environment Variables**
```bash
docker compose exec backend env
```

---

## Quick One-Liners (Run from Your Local Machine)

You can also run commands directly from your local terminal without SSHing in:

### View Container Status
```bash
ssh ubuntu@cvagent.duckdns.org 'cd ~/cv-new/cv-magic-app && docker compose ps'
```

### View Logs
```bash
ssh ubuntu@cvagent.duckdns.org 'cd ~/cv-new/cv-magic-app && docker compose logs --tail=50'
```

### Restart Services
```bash
ssh ubuntu@cvagent.duckdns.org 'cd ~/cv-new/cv-magic-app && docker compose restart'
```

### Follow Logs in Real-Time
```bash
ssh ubuntu@cvagent.duckdns.org 'cd ~/cv-new/cv-magic-app && docker compose logs -f'
```

---

## Common Troubleshooting Commands

### Check if containers are running
```bash
docker compose ps
```

### Check disk space
```bash
df -h
```

### Check Docker disk usage
```bash
docker system df
```

### Clean up unused Docker resources
```bash
docker system prune -f
```

### View detailed container information
```bash
docker compose config
```

### Test database connection
```bash
docker compose exec postgres psql -U mahesh -d cv_app -c "SELECT version();"
```

### Test Redis connection
```bash
docker compose exec redis redis-cli ping
```

---

## Your Container Names

Based on your `docker-compose.yml`:
- **Backend**: `cv_backend`
- **Postgres**: `cv_postgres`
- **Redis**: `cv_redis`
- **Nginx**: `cv_nginx`

---

## Example Workflow

1. **SSH into VPS:**
   ```bash
   ssh ubuntu@cvagent.duckdns.org
   ```

2. **Navigate to project:**
   ```bash
   cd ~/cv-new/cv-magic-app
   ```

3. **Check status:**
   ```bash
   docker compose ps
   ```

4. **View logs if something's wrong:**
   ```bash
   docker compose logs -f backend
   ```

5. **Restart if needed:**
   ```bash
   docker compose restart backend
   ```

6. **Exit SSH:**
   ```bash
   exit
   ```

---

## Pro Tips

1. **Use `screen` or `tmux` for long-running commands:**
   ```bash
   screen -S docker-logs
   docker compose logs -f
   # Press Ctrl+A then D to detach
   # Reattach with: screen -r docker-logs
   ```

2. **Create an alias for quick access:**
   Add to your `~/.zshrc` or `~/.bashrc`:
   ```bash
   alias vps='ssh ubuntu@cvagent.duckdns.org'
   alias vps-docker='ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && docker compose"'
   ```

3. **Use your existing deploy script:**
   Your `deploy.sh` script already has a "Check Status" option that does most of this for you!

