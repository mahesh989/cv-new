#!/bin/bash

# VPS Connection Diagnostics Script
# Helps troubleshoot SSH connection issues

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           VPS Connection Diagnostics Tool                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

VPS_HOST="cvagent.duckdns.org"
VPS_IP="13.210.217.204"
VPS_USER="ubuntu"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔍 Step 1: DNS Resolution Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if nslookup $VPS_HOST > /dev/null 2>&1; then
    RESOLVED_IP=$(nslookup $VPS_HOST 2>/dev/null | grep "Address:" | tail -1 | awk '{print $2}')
    if [ -n "$RESOLVED_IP" ]; then
        echo -e "${GREEN}✓${NC} DNS resolution successful"
        echo "  Hostname: $VPS_HOST"
        echo "  Resolved IP: $RESOLVED_IP"
        
        if [ "$RESOLVED_IP" != "$VPS_IP" ]; then
            echo -e "${YELLOW}⚠${NC} IP address has changed!"
            echo "  Expected: $VPS_IP"
            echo "  Got: $RESOLVED_IP"
        else
            echo -e "${GREEN}✓${NC} IP matches expected value"
        fi
    else
        echo -e "${RED}✗${NC} Could not extract IP from DNS response"
    fi
else
    echo -e "${RED}✗${NC} DNS resolution failed"
    echo "  Cannot resolve $VPS_HOST"
fi
echo ""

echo "🔍 Step 2: Network Connectivity Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing ping to hostname..."
if ping -c 3 -W 5 $VPS_HOST > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ping to $VPS_HOST successful"
else
    echo -e "${RED}✗${NC} Ping to $VPS_HOST failed"
fi

echo "Testing ping to IP..."
if ping -c 3 -W 5 $VPS_IP > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Ping to $VPS_IP successful"
else
    echo -e "${RED}✗${NC} Ping to $VPS_IP failed"
fi
echo ""

echo "🔍 Step 3: SSH Port Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing SSH port 22 on hostname..."
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$VPS_HOST/22" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Port 22 is open on $VPS_HOST"
else
    echo -e "${RED}✗${NC} Port 22 is closed or filtered on $VPS_HOST"
fi

echo "Testing SSH port 22 on IP..."
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$VPS_IP/22" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Port 22 is open on $VPS_IP"
else
    echo -e "${RED}✗${NC} Port 22 is closed or filtered on $VPS_IP"
fi
echo ""

echo "🔍 Step 4: SSH Connection Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing SSH connection with verbose output..."
echo "Command: ssh -v -o ConnectTimeout=10 -o BatchMode=yes $VPS_USER@$VPS_HOST 'echo test' 2>&1"
echo ""
ssh -v -o ConnectTimeout=10 -o BatchMode=yes $VPS_USER@$VPS_HOST 'echo test' 2>&1 | head -20
echo ""

echo "🔍 Step 5: SSH Key Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f ~/.ssh/id_rsa ] || [ -f ~/.ssh/id_ed25519 ]; then
    echo -e "${GREEN}✓${NC} SSH keys found in ~/.ssh/"
    ls -lh ~/.ssh/id_* 2>/dev/null | grep -v ".pub" || echo "  (No private keys found)"
else
    echo -e "${YELLOW}⚠${NC} No SSH keys found in ~/.ssh/"
fi

echo ""
echo "Checking SSH agent..."
if ssh-add -l > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} SSH agent is running"
    ssh-add -l
else
    echo -e "${YELLOW}⚠${NC} SSH agent is not running or has no keys"
fi
echo ""

echo "🔍 Step 6: Network Interface Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Your current IP address(es):"
if command -v curl > /dev/null 2>&1; then
    PUBLIC_IP=$(curl -s https://api.ipify.org 2>/dev/null || curl -s https://ifconfig.me 2>/dev/null || echo "Unable to determine")
    echo "  Public IP: $PUBLIC_IP"
    echo "  (This is the IP that needs to be allowed in AWS Security Group)"
fi

echo ""
echo "Local network interfaces:"
ifconfig 2>/dev/null | grep -E "inet |flags=" | head -10 || ip addr show 2>/dev/null | grep "inet " | head -5 || echo "  (Unable to list interfaces)"
echo ""

echo "🔍 Step 7: Route Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checking route to VPS..."
if command -v traceroute > /dev/null 2>&1; then
    traceroute -m 5 -w 2 $VPS_IP 2>/dev/null | head -10
elif command -v tracepath > /dev/null 2>&1; then
    tracepath $VPS_IP 2>/dev/null | head -10
else
    echo "  (traceroute/tracepath not available)"
fi
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Recommendations                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "Based on the diagnostics above, try these solutions:"
echo ""

echo "1. If DNS fails but IP ping works:"
echo "   → Use IP address directly: ssh $VPS_USER@$VPS_IP"
echo ""

echo "2. If ping fails:"
echo "   → Check if VPS is running in AWS Console"
echo "   → Verify Security Group allows your IP: $PUBLIC_IP"
echo "   → Check if VPS has been stopped or terminated"
echo ""

echo "3. If port 22 is closed:"
echo "   → Check Security Group inbound rules in AWS Console"
echo "   → Verify SSH service is running on VPS"
echo "   → Check if firewall is blocking (ufw/iptables)"
echo ""

echo "4. If SSH connection times out:"
echo "   → Try connecting from different network (mobile hotspot)"
echo "   → Check if corporate firewall is blocking"
echo "   → Try using VPN"
echo ""

echo "5. If authentication fails:"
echo "   → Verify SSH key: ssh-add -l"
echo "   → Check .ssh/config for conflicting settings"
echo "   → Try: ssh -i ~/.ssh/id_rsa $VPS_USER@$VPS_HOST"
echo ""

echo "6. Quick manual test commands:"
echo "   → nslookup $VPS_HOST"
echo "   → ping -c 3 $VPS_IP"
echo "   → nc -zv $VPS_IP 22  (if netcat is installed)"
echo "   → ssh -vvv $VPS_USER@$VPS_HOST"
echo ""

echo "7. AWS Security Group Check:"
echo "   → Go to: AWS Console → EC2 → Security Groups"
echo "   → Find your instance's security group"
echo "   → Check Inbound Rules for SSH (port 22)"
echo "   → Ensure your IP ($PUBLIC_IP) is allowed"
echo "   → Or use 0.0.0.0/0 for testing (less secure)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Diagnostics complete!"
echo ""

