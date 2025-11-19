# Docker Logging System Analysis

## 📋 Overview

The CV Magic application uses a **two-tier logging system**:
1. **Docker's built-in JSON logging** (managed by Docker)
2. **Persistent file logging** (custom script-based collection)

---

## 🏗️ Architecture

### Layer 1: Docker Container Logs (JSON File Driver)

**Location:** Managed by Docker daemon (typically `/var/lib/docker/containers/`)

**Configuration in `docker-compose.yml`:**

```yaml
backend:
  logging:
    driver: "json-file"
    options:
      max-size: "50m"      # Rotate when file reaches 50MB
      max-file: "5"        # Keep 5 rotated files (total ~250MB)

nginx:
  logging:
    driver: "json-file"
    options:
      max-size: "50m"
      max-file: "5"
```

**What this does:**
- Docker captures all `stdout` and `stderr` from containers
- Saves to JSON files (one per container)
- Automatically rotates when files reach 50MB
- Keeps 5 backup files (total ~250MB per service)
- Logs persist even if containers are stopped

**Access via Docker CLI:**
```bash
docker compose logs backend        # View backend logs
docker compose logs nginx         # View frontend logs
docker compose logs -f backend    # Follow backend logs (live)
```

---

### Layer 2: Persistent File Logging (Custom Collection)

**Location:** `~/cv-new/cv-magic-app/logs/` on VPS

**Files:**
- `logs/backend_logs.txt` - All backend container logs (appended)
- `logs/frontend_logs.txt` - All nginx container logs (appended)

**How it works:**

#### 1. **Log Collection Scripts**

**`start_logging.sh`** (lines 1-26):
```bash
#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Start backend logging in background
docker compose logs -f backend >> logs/backend_logs.txt 2>&1 &
BACKEND_LOG_PID=$!

# Start frontend/nginx logging in background
docker compose logs -f nginx >> logs/frontend_logs.txt 2>&1 &
FRONTEND_LOG_PID=$!
```

**What this does:**
- Runs `docker compose logs -f` (follow mode) for each service
- Redirects output (`>>`) to text files (appends, doesn't overwrite)
- Runs in background (`&`) so it doesn't block
- Captures both stdout and stderr (`2>&1`)

**`stop_logging.sh`** (lines 1-10):
```bash
#!/bin/bash

# Kill all docker compose logs processes
pkill -f "docker compose logs -f backend"
pkill -f "docker compose logs -f nginx"
```

---

#### 2. **Integration with Deployment**

**In `deploy.sh` (lines 201-266):**

```bash
# Step 1: Clear old logs (lines 201-205)
echo "🧹 Clearing log files..."
mkdir -p logs
> logs/backend_logs.txt          # Truncate to empty
> logs/frontend_logs.txt         # Truncate to empty
echo "  ✅ Cleared backend_logs.txt and frontend_logs.txt"

# ... (deployment steps) ...

# Step 2: Start log collection (lines 260-266)
echo "📝 Starting log collection..."
# Start logging in background
nohup docker compose logs -f backend >> logs/backend_logs.txt 2>&1 &
nohup docker compose logs -f nginx >> logs/frontend_logs.txt 2>&1 &
echo "  ✅ Logs are being saved to:"
echo "     - logs/backend_logs.txt"
echo "     - logs/frontend_logs.txt"
```

**Key points:**
- Uses `nohup` to ensure processes survive SSH disconnection
- Logs are cleared before deployment (fresh start)
- Log collection starts automatically after deployment
- Processes run in background indefinitely

---

## 🔄 Log Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Containers                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Backend (FastAPI)          Nginx (Frontend)                 │
│  ┌──────────────┐           ┌──────────────┐               │
│  │ stdout       │           │ stdout       │               │
│  │ stderr       │           │ stderr       │               │
│  └──────┬───────┘           └──────┬───────┘               │
│         │                          │                        │
└─────────┼──────────────────────────┼────────────────────────┘
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Docker JSON File Driver (Layer 1)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /var/lib/docker/containers/                                │
│  ├── cv_backend-*.log  (max 50MB, 5 files)                 │
│  └── cv_nginx-*.log    (max 50MB, 5 files)                 │
│                                                              │
└─────────┬──────────────────────────────────┬────────────────┘
          │                                  │
          │ docker compose logs -f           │
          │                                  │
          ▼                                  ▼
┌─────────────────────────────────────────────────────────────┐
│         Persistent File Collection (Layer 2)                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Background Processes:                                       │
│  ┌────────────────────────┐  ┌────────────────────────┐    │
│  │ docker compose logs    │  │ docker compose logs    │    │
│  │ -f backend             │  │ -f nginx               │    │
│  └───────────┬────────────┘  └───────────┬────────────┘    │
│              │                            │                  │
│              ▼                            ▼                  │
│  logs/backend_logs.txt      logs/frontend_logs.txt          │
│  (appended continuously)    (appended continuously)         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Log Storage Details

### Docker JSON Logs (Layer 1)

**Location:** Managed by Docker (not directly accessible)
- Backend: `/var/lib/docker/containers/<container_id>/<container_id>-json.log`
- Nginx: `/var/lib/docker/containers/<container_id>/<container_id>-json.log`

**Format:** JSON lines (one JSON object per log line)
```json
{"log":"2025-11-16 09:25:07 INFO: Starting CV Management API...\n","stream":"stdout","time":"2025-11-16T09:25:07.123456789Z"}
```

**Rotation:**
- When file reaches 50MB → Rotate to `.1`, `.2`, etc.
- Keeps 5 files → Total ~250MB per service
- Oldest files are deleted automatically

**Access:**
```bash
# View via Docker CLI
docker compose logs backend
docker compose logs --tail=100 backend
docker compose logs -f backend

# Direct access (if needed)
docker inspect cv_backend | grep LogPath
# Then: cat /var/lib/docker/containers/<id>/<id>-json.log
```

---

### Persistent Text Logs (Layer 2)

**Location:** `~/cv-new/cv-magic-app/logs/` on VPS

**Format:** Plain text (human-readable)
```
2025-11-16 09:25:07 INFO: Starting CV Management API...
2025-11-16 09:25:08 INFO: Database connection successful
2025-11-16 09:25:10 ERROR: Failed to process request
```

**Characteristics:**
- ✅ **Appended continuously** (never overwritten)
- ✅ **Persists across container restarts**
- ✅ **Easy to search** (grep, tail, etc.)
- ✅ **Cleared on fresh deployments** (option 1)
- ⚠️ **Grows indefinitely** (no automatic rotation)

**Access:**
```bash
# View logs (SSH)
ssh ubuntu@cvagent.duckdns.org "tail -f ~/cv-new/cv-magic-app/logs/backend_logs.txt"

# Download logs
scp ubuntu@cvagent.duckdns.org:~/cv-new/cv-magic-app/logs/backend_logs.txt ./

# Search logs
ssh ubuntu@cvagent.duckdns.org "grep ERROR ~/cv-new/cv-magic-app/logs/backend_logs.txt"
```

---

## 🔍 Key Differences

| Feature | Docker JSON Logs (Layer 1) | Persistent Text Logs (Layer 2) |
|---------|---------------------------|--------------------------------|
| **Location** | Docker-managed (`/var/lib/docker/`) | Project directory (`logs/`) |
| **Format** | JSON (structured) | Plain text (readable) |
| **Rotation** | ✅ Automatic (50MB, 5 files) | ❌ Manual (grows indefinitely) |
| **Access** | `docker compose logs` | Direct file access |
| **Persistence** | ✅ Survives container restarts | ✅ Survives container restarts |
| **Search** | Requires JSON parsing | ✅ Easy (grep, tail) |
| **Size Limit** | ~250MB per service | Unlimited (manual cleanup) |
| **Deployment** | Preserved | Cleared on fresh deployment |

---

## 🛠️ Management Commands

### View Logs

```bash
# Docker logs (Layer 1)
docker compose logs backend              # All backend logs
docker compose logs -f backend          # Follow backend logs
docker compose logs --tail=100 backend  # Last 100 lines

# Persistent logs (Layer 2)
ssh ubuntu@cvagent.duckdns.org "tail -f ~/cv-new/cv-magic-app/logs/backend_logs.txt"
ssh ubuntu@cvagent.duckdns.org "tail -100 ~/cv-new/cv-magic-app/logs/backend_logs.txt"
```

### Search Logs

```bash
# Search Docker logs
docker compose logs backend | grep ERROR

# Search persistent logs
ssh ubuntu@cvagent.duckdns.org "grep ERROR ~/cv-new/cv-magic-app/logs/backend_logs.txt"
ssh ubuntu@cvagent.duckdns.org "grep 'continue-full-analysis' ~/cv-new/cv-magic-app/logs/backend_logs.txt"
```

### Clear Logs

```bash
# Clear persistent logs (Layer 2)
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && > logs/backend_logs.txt && > logs/frontend_logs.txt"

# Clear Docker logs (Layer 1) - requires container restart
docker compose down
docker compose up -d
```

### Restart Log Collection

```bash
# Stop existing collection
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && pkill -f 'docker compose logs'"

# Start collection
ssh ubuntu@cvagent.duckdns.org "cd ~/cv-new/cv-magic-app && \
  nohup docker compose logs -f backend >> logs/backend_logs.txt 2>&1 & \
  nohup docker compose logs -f nginx >> logs/frontend_logs.txt 2>&1 &"
```

### Check Log Collection Status

```bash
# Check if log collection processes are running
ssh ubuntu@cvagent.duckdns.org "ps aux | grep 'docker compose logs'"

# Check log file sizes
ssh ubuntu@cvagent.duckdns.org "ls -lh ~/cv-new/cv-magic-app/logs/"
```

---

## ⚠️ Important Notes

### 1. **Log Collection Processes**

The persistent log collection runs as **background processes** on the VPS:
- Started automatically during deployment (option 1)
- Run indefinitely until manually stopped
- Survive SSH disconnection (thanks to `nohup`)
- Can be stopped with `pkill -f 'docker compose logs'`

### 2. **Log File Growth**

**Persistent logs (Layer 2) grow indefinitely:**
- No automatic rotation
- Must be manually cleared or archived
- Cleared automatically on fresh deployments (option 1)

**Docker logs (Layer 1) are automatically rotated:**
- Max 50MB per file
- Keeps 5 files (~250MB total)
- Oldest files deleted automatically

### 3. **Deployment Behavior**

**Full Deployment (Option 1):**
1. ✅ Clears `logs/backend_logs.txt` and `logs/frontend_logs.txt`
2. ✅ Deploys application
3. ✅ Starts fresh log collection

**Quick Deployment (Option 2):**
- Does NOT clear logs
- Does NOT restart log collection
- Logs continue appending

### 4. **Backend Internal Logging**

The backend also writes to `backend/log.txt` (see `backend/app/main.py` lines 45-58):
```python
log_file = backend_root / "log.txt"
file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
```

This is **separate** from Docker logs and is inside the container.

---

## 🎯 Best Practices

1. **For Debugging:**
   - Use persistent logs (Layer 2) for easy searching
   - Clear logs before testing to get clean output
   - Download logs locally for detailed analysis

2. **For Monitoring:**
   - Use Docker logs (Layer 1) for real-time monitoring
   - Set up log rotation alerts if files grow too large
   - Archive old persistent logs before clearing

3. **For Production:**
   - Monitor log file sizes regularly
   - Set up automated log rotation for persistent logs
   - Archive logs before clearing for compliance

---

## 📝 Summary

**Two-tier logging system:**

1. **Docker JSON Logs (Layer 1):**
   - Managed by Docker daemon
   - Automatic rotation (50MB, 5 files)
   - Access via `docker compose logs`
   - Structured JSON format

2. **Persistent Text Logs (Layer 2):**
   - Custom collection via background processes
   - Human-readable plain text
   - Easy to search and download
   - Cleared on fresh deployments
   - Grows indefinitely (manual cleanup)

**Deployment integration:**
- `deploy.sh` (option 1) automatically clears and restarts log collection
- Logs are saved to `logs/backend_logs.txt` and `logs/frontend_logs.txt`
- Processes run in background using `nohup`

**Key commands:**
- View: `tail -f logs/backend_logs.txt`
- Search: `grep ERROR logs/backend_logs.txt`
- Clear: `> logs/backend_logs.txt`
- Restart: `pkill -f 'docker compose logs'` then restart collection

