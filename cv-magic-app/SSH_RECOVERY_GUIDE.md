# SSH Connection Hang - Quick Recovery Guide

## 🚨 Immediate Actions (Try These First)

### 1. **AWS Console Reboot** (Fastest Recovery - 2 minutes)
```bash
# Steps:
1. Go to: AWS Console → EC2 → Instances
2. Find instance with IP: 13.210.217.204
3. Right-click → Instance State → Reboot
4. Wait 2-3 minutes
5. Try SSH again: ssh ubuntu@cvagent.duckdns.org 'echo test'
```

### 2. **Check AWS Security Group** (30 seconds)
```bash
# Steps:
1. Go to: AWS Console → EC2 → Security Groups
2. Find security group attached to your instance
3. Check Inbound Rules → SSH (port 22)
4. Verify your IP (115.128.98.21) is allowed
5. If missing, add: Type=SSH, Source=115.128.98.21/32
```

### 3. **Try Alternative Connection Methods**
```bash
# Method A: Explicit key with aggressive timeouts
ssh -i ~/.ssh/id_ed25519 \
    -o ConnectTimeout=10 \
    -o ServerAliveInterval=5 \
    -o ServerAliveCountMax=2 \
    ubuntu@cvagent.duckdns.org 'echo test'

# Method B: Use IP instead of hostname
ssh -i ~/.ssh/id_ed25519 ubuntu@13.210.217.204 'echo test'

# Method C: Try with different SSH options
ssh -o ConnectTimeout=10 \
    -o ServerAliveInterval=5 \
    -o ServerAliveCountMax=2 \
    -o TCPKeepAlive=yes \
    -i ~/.ssh/id_ed25519 \
    ubuntu@cvagent.duckdns.org 'echo test'
```

### 4. **AWS Systems Manager Session Manager** (If SSH is completely broken)
```bash
# Steps:
1. Go to: AWS Console → EC2 → Instances
2. Select your instance
3. Click "Connect" button
4. Choose "Session Manager" tab
5. Click "Connect" (bypasses SSH entirely)
```

---

## 🔍 Diagnostic Commands

### Run Full Diagnostic
```bash
cd /Users/mahesh/Documents/Github/cv-new/cv-magic-app
./ssh-hang-diagnostic.sh
```

### Quick Manual Tests
```bash
# Test DNS
nslookup cvagent.duckdns.org

# Test port 22
nc -zv 13.210.217.204 22

# Test SSH with verbose output (first 30 lines)
timeout 20 ssh -vvv -o ConnectTimeout=5 \
    ubuntu@cvagent.duckdns.org 'echo test' 2>&1 | head -30

# Check SSH agent
ssh-add -l

# Test connection with timeout
timeout 15 ssh -o ConnectTimeout=5 \
    -o ServerAliveInterval=3 \
    -o ServerAliveCountMax=2 \
    ubuntu@cvagent.duckdns.org 'echo test'
```

---

## 🎯 Root Cause Analysis

### Most Likely Causes (Based on Your Symptoms)

#### 1. **Server Resource Exhaustion** (70% probability)
**Symptoms:**
- Connection establishes but hangs
- Port 22 is open
- No error messages

**Why:** Your deployment script runs Docker operations that may have consumed all memory/CPU. SSH daemon can't respond when server is overloaded.

**Fix:**
1. Reboot via AWS Console (fastest)
2. Once access restored, check resources: `free -h && df -h`
3. Add resource limits to docker-compose.yml

#### 2. **SSH Daemon Hung** (15% probability)
**Symptoms:**
- Same as above
- May have many existing SSH connections

**Fix:**
1. Reboot via AWS Console
2. Or restart sshd (requires server access): `sudo systemctl restart sshd`

#### 3. **Network Path Issue** (10% probability)
**Symptoms:**
- Intermittent hangs
- Works from some networks but not others

**Fix:**
1. Try from different network (mobile hotspot)
2. Wait and retry (temporary routing issue)
3. Contact AWS support if persistent

#### 4. **AWS Security Group** (3% probability)
**Symptoms:**
- Connection refused (not hanging)
- Port 22 closed

**Fix:**
1. Check Security Group rules in AWS Console
2. Add your IP if missing

#### 5. **SSH Key/Authentication** (2% probability)
**Symptoms:**
- Authentication errors (not hanging)
- Key not found errors

**Fix:**
1. Re-add key to agent: `ssh-add ~/.ssh/id_ed25519`
2. Test with explicit key: `ssh -i ~/.ssh/id_ed25519 ubuntu@cvagent.duckdns.org`

---

## 🛠️ Server-Side Diagnostics (After Access Restored)

Once you regain SSH access, run these commands on the server:

```bash
# Check SSH daemon status
sudo systemctl status sshd

# Check SSH logs for errors
sudo journalctl -u sshd -n 50 --no-pager

# Check system resources
free -h
df -h
top -bn1 | head -20

# Check active SSH connections
sudo netstat -tn | grep :22 | wc -l
sudo ss -tn | grep :22 | wc -l

# Check SSH configuration
sudo grep -E "MaxStartups|MaxSessions|ClientAliveInterval" /etc/ssh/sshd_config

# Check for hung processes
ps aux | grep sshd | grep -v grep

# Check Docker resource usage
docker stats --no-stream
docker system df
```

---

## 🔒 Prevention Measures

### 1. Set Up AWS Systems Manager Session Manager
Provides backup access method that doesn't require SSH.

### 2. Add Resource Limits to Docker Compose
Edit `docker-compose.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### 3. Configure SSH Keepalives
Add to `~/.ssh/config`:
```
Host cvagent cvagent.duckdns.org
    HostName cvagent.duckdns.org
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ConnectTimeout 10
    StrictHostKeyChecking no
```

### 4. Set Up CloudWatch Alarms
Monitor CPU and memory usage, alert when > 80%.

### 5. Add Health Checks to Deployment Script
Check server resources before deployment:
```bash
# In deploy.sh, add before SSH commands:
ssh ubuntu@cvagent.duckdns.org << 'EOF'
    echo "Checking resources..."
    free -h
    df -h
    # Abort if memory < 500MB free
EOF
```

---

## 📋 Quick Reference Commands

### Test Connection
```bash
ssh ubuntu@cvagent.duckdns.org 'echo test'
```

### Test with Timeout
```bash
timeout 15 ssh -o ConnectTimeout=5 ubuntu@cvagent.duckdns.org 'echo test'
```

### Verbose Debug
```bash
ssh -vvv ubuntu@cvagent.duckdns.org 'echo test' 2>&1 | head -40
```

### Check Your Public IP
```bash
curl https://api.ipify.org
```

### Check DNS
```bash
nslookup cvagent.duckdns.org
```

### Check Port
```bash
nc -zv 13.210.217.204 22
```

---

## 🆘 If Nothing Works

1. **AWS Console → EC2 → Instances → Reboot** (most reliable)
2. **AWS Systems Manager Session Manager** (if enabled)
3. **Contact AWS Support** (if instance appears healthy but SSH still fails)
4. **Try from different network** (mobile hotspot, different location)

---

## 📝 Notes

- Your IP: `115.128.98.21` (stable)
- VPS IP: `13.210.217.204`
- VPS Hostname: `cvagent.duckdns.org`
- SSH Key: `~/.ssh/id_ed25519`
- Region: AWS Sydney (ap-southeast-2)

---

**Last Updated:** Based on current SSH hang issue
**Status:** Connection hanging after TCP establishment
**Most Likely Fix:** AWS Console reboot

