#!/bin/bash

# Quick SSH Fix Script
# Attempts immediate fixes for SSH hanging issues

set -e

VPS_HOST="cvagent.duckdns.org"
VPS_IP="13.210.217.204"
VPS_USER="ubuntu"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Quick SSH Fix Attempts                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Fix 1: Clean known_hosts entries
echo -e "${CYAN}[Fix 1/4]${NC} Cleaning known_hosts entries..."
if grep -q "$VPS_HOST\|$VPS_IP" ~/.ssh/known_hosts 2>/dev/null; then
    ENTRY_COUNT=$(grep -c "$VPS_HOST\|$VPS_IP" ~/.ssh/known_hosts 2>/dev/null || echo "0")
    echo "  Found $ENTRY_COUNT entries for this host"
    echo -n "  Remove them? (y/n): "
    read -r response
    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        ssh-keygen -R "$VPS_HOST" 2>/dev/null || true
        ssh-keygen -R "$VPS_IP" 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} Known hosts entries removed"
    else
        echo -e "  ${YELLOW}→${NC} Skipped"
    fi
else
    echo -e "  ${GREEN}✓${NC} No entries to clean"
fi
echo ""

# Fix 2: Ensure SSH agent is running and key is loaded
echo -e "${CYAN}[Fix 2/4]${NC} Ensuring SSH agent is running..."
if ! ssh-add -l &>/dev/null; then
    echo "  Starting SSH agent..."
    eval "$(ssh-agent -s)" 2>/dev/null
    if ssh-add ~/.ssh/id_ed25519 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} SSH agent started and key added"
    else
        echo -e "  ${YELLOW}⚠${NC} Key may require passphrase - enter it when prompted"
        ssh-add ~/.ssh/id_ed25519
    fi
else
    echo -e "  ${GREEN}✓${NC} SSH agent is running"
    if ssh-add -l | grep -q "ed25519"; then
        echo -e "  ${GREEN}✓${NC} Ed25519 key is loaded"
    else
        echo "  Adding key to agent..."
        ssh-add ~/.ssh/id_ed25519 2>/dev/null || ssh-add ~/.ssh/id_ed25519
    fi
fi
echo ""

# Fix 3: Test connection with IP instead of hostname
echo -e "${CYAN}[Fix 3/4]${NC} Testing connection with IP address..."
echo "  Attempting: ssh -i ~/.ssh/id_ed25519 -o ConnectTimeout=10 ${VPS_USER}@${VPS_IP} 'echo SUCCESS'"
echo ""

if timeout 15 ssh -i ~/.ssh/id_ed25519 \
    -o ConnectTimeout=10 \
    -o ServerAliveInterval=5 \
    -o ServerAliveCountMax=2 \
    -o StrictHostKeyChecking=no \
    -o BatchMode=yes \
    ${VPS_USER}@${VPS_IP} 'echo SUCCESS' 2>&1; then
    echo -e "  ${GREEN}✓${NC} Connection successful with IP!"
    echo ""
    echo -e "${GREEN}SUCCESS! SSH is working.${NC}"
    exit 0
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 124 ]; then
        echo -e "  ${RED}✗${NC} Connection still hanging with IP"
    else
        echo -e "  ${RED}✗${NC} Connection failed (exit code: $EXIT_CODE)"
    fi
fi
echo ""

# Fix 4: Test with hostname
echo -e "${CYAN}[Fix 4/4]${NC} Testing connection with hostname..."
echo "  Attempting: ssh -i ~/.ssh/id_ed25519 -o ConnectTimeout=10 ${VPS_USER}@${VPS_HOST} 'echo SUCCESS'"
echo ""

if timeout 15 ssh -i ~/.ssh/id_ed25519 \
    -o ConnectTimeout=10 \
    -o ServerAliveInterval=5 \
    -o ServerAliveCountMax=2 \
    -o StrictHostKeyChecking=no \
    -o BatchMode=yes \
    ${VPS_USER}@${VPS_HOST} 'echo SUCCESS' 2>&1; then
    echo -e "  ${GREEN}✓${NC} Connection successful with hostname!"
    echo ""
    echo -e "${GREEN}SUCCESS! SSH is working.${NC}"
    exit 0
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 124 ]; then
        echo -e "  ${RED}✗${NC} Connection still hanging with hostname"
    else
        echo -e "  ${RED}✗${NC} Connection failed (exit code: $EXIT_CODE)"
    fi
fi
echo ""

# Summary
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}All quick fixes failed. This is a SERVER-SIDE issue.${NC}"
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}IMMEDIATE ACTION REQUIRED:${NC}"
echo ""
echo "1. ${BLUE}AWS Console Reboot${NC} (Most likely to fix):"
echo "   • Go to: AWS Console → EC2 → Instances"
echo "   • Find instance: 13.210.217.204"
echo "   • Right-click → Instance State → Reboot"
echo "   • Wait 2-3 minutes, then try SSH again"
echo ""
echo "2. ${BLUE}Check AWS Security Group${NC}:"
echo "   • AWS Console → EC2 → Security Groups"
echo "   • Verify SSH (port 22) allows your IP: 115.128.98.21"
echo ""
echo "3. ${BLUE}AWS Systems Manager Session Manager${NC} (if enabled):"
echo "   • AWS Console → EC2 → Instances → Connect → Session Manager"
echo "   • This bypasses SSH entirely"
echo ""
echo -e "${CYAN}The server's SSH daemon is unresponsive.${NC}"
echo -e "${CYAN}This is almost certainly due to resource exhaustion or a hung sshd process.${NC}"
echo ""

