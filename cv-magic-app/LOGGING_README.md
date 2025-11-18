# 📝 Persistent Logging System

## Overview
This system saves backend and frontend logs to persistent files that keep appending logs without overwriting.

## Files
- **`logs/backend_logs.txt`** - All backend (FastAPI/Python) logs
- **`logs/frontend_logs.txt`** - All frontend (Nginx) access and error logs

## Features
✅ Logs are **appended** (not overwritten)  
✅ Logs persist across container restarts  
✅ Automatically cleared on fresh deployments (option 1)  
✅ Easy to view and search  

## Usage

### On VPS (Automatic)
Logs are automatically collected when you deploy with option 1:
```bash
./deploy.sh
# Select option 1: Full Deployment
```

The deployment script will:
1. Clear old log files
2. Deploy the application
3. Start background log collection

### View Logs
```bash
# View backend logs (live tail)
ssh ubuntu@cvagent.duckdns.org "tail -f ~/cv-new/cv-magic-app/logs/backend_logs.txt"

# View frontend logs (live tail)
ssh ubuntu@cvagent.duckdns.org "tail -f ~/cv-new/cv-magic-app/logs/frontend_logs.txt"

# View last 100 lines of backend logs
ssh ubuntu@cvagent.duckdns.org "tail -100 ~/cv-new/cv-magic-app/logs/backend_logs.txt"

# Search for errors in backend logs
ssh ubuntu@cvagent.duckdns.org "grep ERROR ~/cv-new/cv-magic-app/logs/backend_logs.txt"

# Search for specific API endpoint
ssh ubuntu@cvagent.duckdns.org "grep 'continue-full-analysis' ~/cv-new/cv-magic-app/logs/backend_logs.txt"
```

### Download Logs Locally
```bash
# Download backend logs
scp ubuntu@cvagent.duckdns.org:~/cv-new/cv-magic-app/logs/backend_logs.txt ./backend_logs.txt

# Download frontend logs
scp ubuntu@cvagent.duckdns.org:~/cv-new/cv-magic-app/logs/frontend_logs.txt ./frontend_logs.txt
```

### Clear Logs Manually
```bash
# Clear all logs
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && > logs/backend_logs.txt && > logs/frontend_logs.txt"
```

### Manual Start/Stop (Local Development)
If running locally:
```bash
# Start logging
./start_logging.sh

# Stop logging
./stop_logging.sh
```

## Log Rotation
Logs are configured with Docker's built-in rotation:
- **Max size per file:** 50 MB
- **Max files kept:** 5
- **Total max size:** ~250 MB per service

## Troubleshooting

### Logs not appearing?
1. Check if log collection processes are running:
   ```bash
   ssh ubuntu@cvagent.duckdns.org "ps aux | grep 'docker compose logs'"
   ```

2. Restart log collection:
   ```bash
   ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && \
     pkill -f 'docker compose logs' && \
     nohup docker compose logs -f backend >> logs/backend_logs.txt 2>&1 & \
     nohup docker compose logs -f nginx >> logs/frontend_logs.txt 2>&1 &"
   ```

### Logs too large?
Clear them:
```bash
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && > logs/backend_logs.txt && > logs/frontend_logs.txt"
```

Or download and archive:
```bash
# Download and compress
scp ubuntu@cvagent.duckdns.org:~/cv-new/cv-magic-app/logs/backend_logs.txt ./
gzip backend_logs.txt

# Clear on VPS
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && > logs/backend_logs.txt"
```

## Debugging Workflow

### Example: Debug Widget Not Appearing
```bash
# 1. Clear logs before testing
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && > logs/backend_logs.txt && > logs/frontend_logs.txt"

# 2. Run your test (click Proceed button)

# 3. Check backend logs for the API call
ssh ubuntu@cvagent.duckdns.org "grep 'continue-full-analysis' ~/cv-new/cv-magic-app/logs/backend_logs.txt"

# 4. Check frontend logs for the HTTP request
ssh ubuntu@cvagent.duckdns.org "grep 'POST.*continue-full-analysis' ~/cv-new/cv-magic-app/logs/frontend_logs.txt"

# 5. Download full logs for detailed analysis
scp ubuntu@cvagent.duckdns.org:~/cv-new/cv-magic-app/logs/backend_logs.txt ./debug_backend.txt
```

## Integration with Deployment

The `deploy.sh` script (option 1) automatically:
1. ✅ Creates `logs/` directory
2. ✅ Clears `backend_logs.txt` and `frontend_logs.txt`
3. ✅ Deploys application
4. ✅ Starts background log collection processes

This ensures you always start with a clean slate for debugging new deployments!

