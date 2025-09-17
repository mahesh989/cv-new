#!/bin/bash

# Monitor CV tailoring attempts in real-time
echo "📊 Monitoring CV Tailoring Service..."
echo "======================================="
echo ""

tail -f server.log | grep --line-buffered -E "tailoring|quantification|validation|Impact Statement|bullets|Attempt|AI generation" | while read line; do
    # Color code the output based on content
    if echo "$line" | grep -q "ERROR\|failed\|violation"; then
        echo -e "\033[31m❌ $line\033[0m"  # Red for errors
    elif echo "$line" | grep -q "WARNING\|warning"; then
        echo -e "\033[33m⚠️  $line\033[0m"  # Yellow for warnings  
    elif echo "$line" | grep -q "SUCCESS\|successful\|passed"; then
        echo -e "\033[32m✅ $line\033[0m"  # Green for success
    elif echo "$line" | grep -q "Attempt"; then
        echo -e "\033[36m🔄 $line\033[0m"  # Cyan for attempts
    else
        echo "$line"
    fi
done