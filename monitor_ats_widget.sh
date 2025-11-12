#!/bin/bash

# Real-time ATS Widget Monitoring Script
# Monitors backend logs for ATS widget activity

echo "=========================================="
echo "ATS Widget Real-Time Monitor"
echo "=========================================="
echo ""
echo "Monitoring backend logs for ATS widget activity..."
echo "Press Ctrl+C to stop"
echo ""
echo "Looking for:"
echo "  ✓ ATS result persisted"
echo "  ✓ GET /api/analysis-results/{company} 200 OK"
echo "  ✓ ATS result included in response"
echo ""
echo "----------------------------------------"
echo ""

# Monitor logs in real-time
ssh ubuntu@13.210.217.204 "docker logs cv_backend -f 2>&1" | grep --line-buffered -E "ATS|analysis-results|📊.*API.*Fetching|✅.*ATS|persisted|included.*response" | while IFS= read -r line; do
    timestamp=$(date '+%H:%M:%S')
    
    if echo "$line" | grep -qE "✅.*ATS.*result.*persisted"; then
        echo -e "[$timestamp] \033[0;32m✓ ATS RESULT PERSISTED\033[0m"
        echo "  $line"
    elif echo "$line" | grep -qE "GET.*analysis-results.*200"; then
        echo -e "[$timestamp] \033[0;32m✓ API ENDPOINT CALLED (200 OK)\033[0m"
        echo "  $line"
    elif echo "$line" | grep -qE "✅.*ATS.*result.*included.*response"; then
        echo -e "[$timestamp] \033[0;32m✓ ATS RESULT IN RESPONSE\033[0m"
        echo "  $line"
    elif echo "$line" | grep -qE "📊.*API.*Fetching"; then
        echo -e "[$timestamp] \033[0;33m→ API FETCH REQUEST\033[0m"
        echo "  $line"
    elif echo "$line" | grep -qE "FINAL SCORE"; then
        echo -e "[$timestamp] \033[0;36m📊 ATS SCORE CALCULATED\033[0m"
        echo "  $line"
    else
        echo "[$timestamp] $line"
    fi
    echo ""
done

