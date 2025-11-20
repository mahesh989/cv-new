#!/bin/bash
# Usage: ./ssh_log_inspector.sh [user@host]
# Defaults to ubuntu@cvagent.duckdns.org

set -euo pipefail

SERVER="${1:-ubuntu@cvagent.duckdns.org}"
APP_PATH="/home/ubuntu/cv-new/cv-magic-app"

cat <<INFO
========================================
Connecting to $SERVER to fetch logs
Project path: $APP_PATH
========================================
INFO

ssh "$SERVER" bash <<'REMOTE_CMDS'
set -euo pipefail
APP_PATH="/home/ubuntu/cv-new/cv-magic-app"
cd "$APP_PATH"

echo "--- Backend log files available ---"
ls /app/logs || echo "(ls failed - check mount)"

echo "--- Frontend log files available ---"
ls /var/log/nginx_custom || echo "(ls failed - check mount)"

echo "\n=== Backend Logs (last 200 lines) ==="
docker compose exec backend tail -500 /app/logs/backend_logs.txt || echo "Backend log tail failed"

echo "\n=== Frontend Logs (last 200 lines) ==="
docker compose exec nginx tail -500 /var/log/nginx_custom/frontend_logs.txt || echo "Frontend log tail failed"
REMOTE_CMDS