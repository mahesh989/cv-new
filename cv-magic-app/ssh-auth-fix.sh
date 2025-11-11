#!/bin/bash

# SSH Authentication Troubleshooting Script
# Fixes common SSH hanging/timeout issues

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           SSH Authentication Troubleshooter                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

VPS_HOST="cvagent.duckdns.org"
VPS_USER="ubuntu"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}Step 1: Check SSH Agent${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ssh-add -l &>/dev/null; then
    echo -e "${GREEN}✓${NC} SSH agent is running"
    echo "Loaded keys:"
    ssh-add -l
else
    echo -e "${YELLOW}⚠${NC} SSH agent not running or no keys loaded"
    echo "Starting SSH agent and adding key..."
    eval "$(ssh-agent -s)"
    if ssh-add ~/.ssh/id_ed25519 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Key added successfully"
    else
        echo -e "${RED}✗${NC} Failed to add key (may need passphrase)"
    fi
fi
echo ""

echo -e "${CYAN}Step 2: Test Connection with Timeout${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing SSH with 10 second timeout..."
if timeout 10 ssh -o ConnectTimeout=5 -o ServerAliveInterval=5 -o ServerAliveCountMax=2 \
    ${VPS_USER}@${VPS_HOST} 'echo "Success!"' 2>&1; then
    echo -e "${GREEN}✓${NC} Connection successful!"
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 124 ]; then
        echo -e "${RED}✗${NC} Connection timed out (hanging)"
        echo ""
        echo "This usually means:"
        echo "  1. SSH is connecting but authentication is hanging"
        echo "  2. Server is waiting for something (password prompt, key passphrase)"
        echo "  3. Network issue causing slow connection"
    else
        echo -e "${RED}✗${NC} Connection failed with exit code: $EXIT_CODE"
    fi
fi
echo ""

echo -e "${CYAN}Step 3: Check Known Hosts${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if grep -q "$VPS_HOST" ~/.ssh/known_hosts 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Host found in known_hosts"
else
    echo -e "${YELLOW}⚠${NC} Host not in known_hosts (will prompt on first connect)"
fi
echo ""

echo -e "${CYAN}Step 4: Check SSH Config${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f ~/.ssh/config ]; then
    if grep -q "$VPS_HOST\|cvagent" ~/.ssh/config; then
        echo -e "${YELLOW}⚠${NC} Host configuration found in ~/.ssh/config"
        echo "Configuration:"
        grep -A 10 "$VPS_HOST\|cvagent" ~/.ssh/config | head -15
    else
        echo "No specific configuration for this host"
    fi
else
    echo "No SSH config file found"
fi
echo ""

echo -e "${CYAN}Step 5: Test with Verbose Output (First 30 lines)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running: ssh -v -o ConnectTimeout=5 ${VPS_USER}@${VPS_HOST} 'echo test'"
echo ""
timeout 10 ssh -v -o ConnectTimeout=5 -o ServerAliveInterval=2 \
    ${VPS_USER}@${VPS_HOST} 'echo test' 2>&1 | head -30
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                   Quick Fix Commands                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "1. Add SSH key to agent (if not already added):"
echo "   eval \"\$(ssh-agent -s)\""
echo "   ssh-add ~/.ssh/id_ed25519"
echo ""
echo "2. Test connection with explicit key:"
echo "   ssh -i ~/.ssh/id_ed25519 ${VPS_USER}@${VPS_HOST} 'echo test'"
echo ""
echo "3. Test connection with more aggressive timeouts:"
echo "   ssh -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=2 \\"
echo "       ${VPS_USER}@${VPS_HOST} 'echo test'"
echo ""
echo "4. Remove host from known_hosts (if key mismatch):"
echo "   ssh-keygen -R ${VPS_HOST}"
echo "   ssh-keygen -R 13.210.217.204"
echo ""
echo "5. Test with password authentication (if key fails):"
echo "   ssh -o PreferredAuthentications=password ${VPS_USER}@${VPS_HOST}"
echo ""
echo "6. Check if your key needs a passphrase:"
echo "   ssh-keygen -y -f ~/.ssh/id_ed25519 > /dev/null"
echo "   (If it prompts for passphrase, you need to add it to agent)"
echo ""
echo "7. Create optimized SSH config:"
cat << 'EOF'
   cat >> ~/.ssh/config << 'SSHCONFIG'

Host cvagent
    HostName cvagent.duckdns.org
    User ubuntu
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ConnectTimeout 10
    StrictHostKeyChecking no

SSHCONFIG

EOF
echo ""
echo "   Then connect with: ssh cvagent 'echo test'"
echo ""

