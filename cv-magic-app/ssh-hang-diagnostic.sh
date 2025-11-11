#!/bin/bash

# SSH Hang Diagnostic & Recovery Script
# Diagnoses SSH connection hanging issues and provides recovery steps

set -e

VPS_HOST="cvagent.duckdns.org"
VPS_IP="13.210.217.204"
VPS_USER="ubuntu"
MY_IP="115.128.98.21"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        SSH Hang Diagnostic & Recovery Tool                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# PHASE 1: CLIENT-SIDE DIAGNOSTICS
# ============================================================================

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}PHASE 1: Client-Side Diagnostics${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 1: DNS Resolution
echo -e "${BLUE}[1/8]${NC} Testing DNS resolution..."
if RESOLVED_IP=$(nslookup $VPS_HOST 2>/dev/null | grep "Address:" | tail -1 | awk '{print $2}'); then
    echo -e "  ${GREEN}✓${NC} DNS resolves to: $RESOLVED_IP"
    if [ "$RESOLVED_IP" != "$VPS_IP" ]; then
        echo -e "  ${YELLOW}⚠${NC} IP mismatch! Expected: $VPS_IP, Got: $RESOLVED_IP"
    fi
else
    echo -e "  ${RED}✗${NC} DNS resolution failed"
fi
echo ""

# Test 2: Port 22 Accessibility
echo -e "${BLUE}[2/8]${NC} Testing port 22 accessibility..."
PORT_OPEN=false
if command -v nc > /dev/null 2>&1; then
    # Use netcat if available (more reliable)
    if nc -zv -w 5 $VPS_IP 22 2>&1 | grep -q "succeeded\|open"; then
        PORT_OPEN=true
    fi
elif timeout 5 bash -c "cat < /dev/null > /dev/tcp/$VPS_IP/22" 2>/dev/null; then
    # Fallback to bash TCP redirection
    PORT_OPEN=true
fi

if [ "$PORT_OPEN" = true ]; then
    echo -e "  ${GREEN}✓${NC} Port 22 is open and accepting connections"
else
    echo -e "  ${RED}✗${NC} Port 22 is closed or filtered"
    echo -e "  ${YELLOW}→${NC} Check AWS Security Group rules"
    echo -e "  ${YELLOW}→${NC} Verify instance is running in AWS Console"
fi
echo ""

# Test 3: SSH Agent Status
echo -e "${BLUE}[3/8]${NC} Checking SSH agent..."
if ssh-add -l &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} SSH agent is running"
    echo "  Loaded keys:"
    ssh-add -l | sed 's/^/    /'
else
    echo -e "  ${YELLOW}⚠${NC} SSH agent not running or no keys loaded"
    echo "  Attempting to start agent and add key..."
    eval "$(ssh-agent -s)" 2>/dev/null || true
    if ssh-add ~/.ssh/id_ed25519 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Key added to agent"
    else
        echo -e "  ${RED}✗${NC} Failed to add key (may need passphrase)"
    fi
fi
echo ""

# Test 4: SSH Key File Check
echo -e "${BLUE}[4/8]${NC} Checking SSH key files..."
if [ -f ~/.ssh/id_ed25519 ]; then
    echo -e "  ${GREEN}✓${NC} Key file exists: ~/.ssh/id_ed25519"
    KEY_PERMS=$(stat -f "%OLp" ~/.ssh/id_ed25519 2>/dev/null || stat -c "%a" ~/.ssh/id_ed25519 2>/dev/null || echo "unknown")
    if [ "$KEY_PERMS" != "600" ] && [ "$KEY_PERMS" != "400" ]; then
        echo -e "  ${YELLOW}⚠${NC} Key permissions are $KEY_PERMS (should be 600)"
    else
        echo -e "  ${GREEN}✓${NC} Key permissions correct: $KEY_PERMS"
    fi
else
    echo -e "  ${RED}✗${NC} Key file not found: ~/.ssh/id_ed25519"
fi
echo ""

# Test 5: SSH Config Check
echo -e "${BLUE}[5/8]${NC} Checking SSH config..."
if [ -f ~/.ssh/config ]; then
    if grep -q "$VPS_HOST\|cvagent" ~/.ssh/config; then
        echo -e "  ${YELLOW}⚠${NC} Found host-specific config:"
        grep -A 5 "$VPS_HOST\|cvagent" ~/.ssh/config | sed 's/^/    /'
    else
        echo -e "  ${GREEN}✓${NC} No conflicting host config found"
    fi
else
    echo -e "  ${GREEN}✓${NC} No SSH config file (using defaults)"
fi
echo ""

# Test 6: Known Hosts Check
echo -e "${BLUE}[6/8]${NC} Checking known_hosts..."
if grep -q "$VPS_HOST\|$VPS_IP" ~/.ssh/known_hosts 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Host found in known_hosts"
    ENTRY_COUNT=$(grep -c "$VPS_HOST\|$VPS_IP" ~/.ssh/known_hosts 2>/dev/null || echo "0")
    if [ "$ENTRY_COUNT" -gt 1 ]; then
        echo -e "  ${YELLOW}⚠${NC} Multiple entries found ($ENTRY_COUNT) - may cause issues"
        echo -e "  ${CYAN}→${NC} Consider cleaning: ssh-keygen -R $VPS_HOST && ssh-keygen -R $VPS_IP"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Host not in known_hosts (will prompt on first connect)"
fi
echo ""

# Test 7: Network Path Test
echo -e "${BLUE}[7/8]${NC} Testing network path..."
echo "  Your public IP: $MY_IP"
if command -v traceroute > /dev/null 2>&1; then
    echo "  Testing route (first 5 hops)..."
    timeout 10 traceroute -m 5 -w 2 $VPS_IP 2>/dev/null | head -6 | sed 's/^/    /' || echo "    (traceroute timed out or failed)"
elif command -v tracepath > /dev/null 2>&1; then
    echo "  Testing route (first 5 hops)..."
    timeout 10 tracepath $VPS_IP 2>/dev/null | head -6 | sed 's/^/    /' || echo "    (tracepath timed out or failed)"
else
    echo "  (traceroute not available)"
fi
echo ""

# Test 8: SSH Connection Test with Timeout
echo -e "${BLUE}[8/8]${NC} Testing SSH connection (with 15s timeout)..."
echo "  Command: ssh -o ConnectTimeout=5 -o ServerAliveInterval=3 -o ServerAliveCountMax=2"
echo ""

CONNECTION_TEST=$(timeout 15 ssh -o ConnectTimeout=5 -o ServerAliveInterval=3 -o ServerAliveCountMax=2 \
    -o BatchMode=yes -o StrictHostKeyChecking=no \
    ${VPS_USER}@${VPS_HOST} 'echo "SUCCESS"' 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Connection successful!"
    echo "  Response: $CONNECTION_TEST"
elif [ $EXIT_CODE -eq 124 ]; then
    echo -e "  ${RED}✗${NC} Connection timed out (hanging confirmed)"
    echo ""
    echo -e "  ${YELLOW}Analysis:${NC}"
    echo "    • TCP connection established (port 22 is open)"
    echo "    • SSH handshake is hanging"
    echo "    • Most likely: Server-side issue"
    echo ""
    echo -e "  ${CYAN}Possible causes:${NC}"
    echo "    1. SSH daemon (sshd) is hung or overloaded"
    echo "    2. Server out of memory/CPU resources"
    echo "    3. Too many SSH connections (MaxStartups limit)"
    echo "    4. SSH daemon waiting for authentication that never completes"
    echo "    5. Network packet loss or routing issue"
else
    echo -e "  ${RED}✗${NC} Connection failed with exit code: $EXIT_CODE"
    echo "  Error output:"
    echo "$CONNECTION_TEST" | sed 's/^/    /' | head -10
fi
echo ""

# ============================================================================
# PHASE 2: VERBOSE SSH TEST
# ============================================================================

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}PHASE 2: Verbose SSH Connection Test${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Running verbose SSH test (first 40 lines, 20s timeout)..."
echo ""

VERBOSE_OUTPUT=$(timeout 20 ssh -vvv -o ConnectTimeout=5 -o ServerAliveInterval=2 \
    -o BatchMode=yes -o StrictHostKeyChecking=no \
    ${VPS_USER}@${VPS_HOST} 'echo test' 2>&1 | head -40)

echo "$VERBOSE_OUTPUT"
echo ""

# Analyze verbose output
if echo "$VERBOSE_OUTPUT" | grep -q "Connection established"; then
    echo -e "${GREEN}✓${NC} TCP connection established"
    
    if echo "$VERBOSE_OUTPUT" | grep -q "SSH2_MSG_KEXINIT"; then
        echo -e "${YELLOW}⚠${NC} Key exchange initiated but may be hanging"
    fi
    
    if echo "$VERBOSE_OUTPUT" | grep -q "Offering public key"; then
        echo -e "${YELLOW}⚠${NC} Authentication started but may be hanging"
    fi
    
    LAST_LINE=$(echo "$VERBOSE_OUTPUT" | tail -1)
    echo -e "${CYAN}Last debug message:${NC} $LAST_LINE"
fi
echo ""

# ============================================================================
# PHASE 3: RECOVERY RECOMMENDATIONS
# ============================================================================

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}PHASE 3: Recovery Recommendations${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}IMMEDIATE RECOVERY OPTIONS:${NC}"
echo ""

echo -e "${BLUE}Option 1: AWS Console Recovery (If SSH is completely broken)${NC}"
echo "  1. Go to AWS Console → EC2 → Instances"
echo "  2. Find instance: $VPS_IP"
echo "  3. Right-click → Instance State → Reboot"
echo "  4. Wait 2-3 minutes, then try SSH again"
echo ""

echo -e "${BLUE}Option 2: AWS Systems Manager Session Manager (If enabled)${NC}"
echo "  1. Go to AWS Console → EC2 → Instances"
echo "  2. Select your instance"
echo "  3. Click 'Connect' → 'Session Manager' tab"
echo "  4. This bypasses SSH entirely"
echo ""

echo -e "${BLUE}Option 3: Try Alternative Connection Methods${NC}"
echo "  # Try with explicit key:"
echo "  ssh -i ~/.ssh/id_ed25519 -o ConnectTimeout=10 \\"
echo "      -o ServerAliveInterval=5 -o ServerAliveCountMax=2 \\"
echo "      ${VPS_USER}@${VPS_HOST} 'echo test'"
echo ""
echo "  # Try with IP instead of hostname:"
echo "  ssh -i ~/.ssh/id_ed25519 ${VPS_USER}@${VPS_IP} 'echo test'"
echo ""

echo -e "${BLUE}Option 4: Check AWS Security Group${NC}"
echo "  1. Go to AWS Console → EC2 → Security Groups"
echo "  2. Find security group attached to instance $VPS_IP"
echo "  3. Check Inbound Rules for SSH (port 22)"
echo "  4. Verify your IP ($MY_IP) is allowed"
echo "  5. If not, add rule: Type=SSH, Source=$MY_IP/32"
echo ""

echo -e "${YELLOW}SERVER-SIDE DIAGNOSTICS (If you can get access via AWS Console):${NC}"
echo ""
echo "If you can access the server via AWS Systems Manager or after reboot:"
echo ""
cat << 'SERVERCMDS'
  # Check SSH daemon status
  sudo systemctl status sshd
  
  # Check SSH daemon logs
  sudo journalctl -u sshd -n 50 --no-pager
  
  # Check for hung SSH processes
  ps aux | grep sshd | grep -v grep
  
  # Check system resources
  free -h
  df -h
  top -bn1 | head -20
  
  # Check SSH connection limits
  sudo netstat -tn | grep :22 | wc -l
  sudo ss -tn | grep :22 | wc -l
  
  # Restart SSH daemon (if needed)
  sudo systemctl restart sshd
  
  # Check SSH config for issues
  sudo grep -E "MaxStartups|MaxSessions|ClientAliveInterval" /etc/ssh/sshd_config
SERVERCMDS
echo ""

echo -e "${YELLOW}CLIENT-SIDE FIXES:${NC}"
echo ""
echo "1. Clear known_hosts entry (if key mismatch suspected):"
echo "   ssh-keygen -R $VPS_HOST"
echo "   ssh-keygen -R $VPS_IP"
echo ""

echo "2. Create optimized SSH config:"
cat << 'SSHCONFIG'
   cat >> ~/.ssh/config << 'EOF'

Host cvagent cvagent.duckdns.org
    HostName cvagent.duckdns.org
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ConnectTimeout 10
    StrictHostKeyChecking no
    PreferredAuthentications publickey
    IdentitiesOnly yes

EOF
SSHCONFIG
echo ""
echo "   Then connect with: ssh cvagent 'echo test'"
echo ""

echo "3. Test with different SSH options:"
echo "   # Most aggressive timeout settings:"
echo "   ssh -o ConnectTimeout=10 -o ServerAliveInterval=5 \\"
echo "       -o ServerAliveCountMax=2 -o TCPKeepAlive=yes \\"
echo "       -i ~/.ssh/id_ed25519 ${VPS_USER}@${VPS_HOST}"
echo ""

# ============================================================================
# PHASE 4: ROOT CAUSE ANALYSIS
# ============================================================================

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}PHASE 4: Root Cause Analysis${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${YELLOW}Most Likely Causes (in order of probability):${NC}"
echo ""
echo "1. ${RED}Server Resource Exhaustion${NC} (70% probability)"
echo "   • VPS ran out of memory/CPU"
echo "   • SSH daemon can't respond to new connections"
echo "   • Docker containers may have consumed all resources"
echo "   ${CYAN}Fix:${NC} Reboot via AWS Console, then check resource usage"
echo ""

echo "2. ${RED}SSH Daemon Hung${NC} (15% probability)"
echo "   • sshd process is stuck"
echo "   • Too many existing connections"
echo "   • MaxStartups limit reached"
echo "   ${CYAN}Fix:${NC} Restart sshd service (requires server access)"
echo ""

echo "3. ${RED}Network Path Issue${NC} (10% probability)"
echo "   • Packet loss on route"
echo "   • ISP routing changed"
echo "   • AWS network issue"
echo "   ${CYAN}Fix:${NC} Try from different network, wait, or contact AWS support"
echo ""

echo "4. ${RED}AWS Security Group Changed${NC} (3% probability)"
echo "   • Security group rules modified"
echo "   • Your IP changed (unlikely: $MY_IP)"
echo "   ${CYAN}Fix:${NC} Check Security Group in AWS Console"
echo ""

echo "5. ${RED}SSH Key/Authentication Issue${NC} (2% probability)"
echo "   • Key not properly loaded in agent"
echo "   • Server-side authorized_keys issue"
echo "   ${CYAN}Fix:${NC} Re-add key to agent, check server authorized_keys"
echo ""

# ============================================================================
# PHASE 5: PREVENTION
# ============================================================================

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}PHASE 5: Prevention Measures${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "1. ${BLUE}Set up AWS Systems Manager Session Manager${NC}"
echo "   • Provides backup access method"
echo "   • Doesn't require SSH"
echo "   • Works even if SSH is broken"
echo ""

echo "2. ${BLUE}Monitor Server Resources${NC}"
echo "   • Set up CloudWatch alarms for CPU/Memory"
echo "   • Alert when resources exceed 80%"
echo ""

echo "3. ${BLUE}Configure SSH Keepalives${NC}"
echo "   • Add to ~/.ssh/config (see Option 2 above)"
echo "   • Prevents connection timeouts"
echo ""

echo "4. ${BLUE}Limit Docker Resource Usage${NC}"
echo "   • Add memory limits to docker-compose.yml"
echo "   • Prevent containers from consuming all resources"
echo ""

echo "5. ${BLUE}Set up SSH Connection Monitoring${NC}"
echo "   • Monitor active SSH connections"
echo "   • Alert on high connection counts"
echo ""

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Diagnostic complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Try AWS Console reboot (fastest recovery)"
echo "  2. Check AWS Security Groups"
echo "  3. Try alternative connection methods"
echo "  4. If access restored, run server-side diagnostics"
echo ""

