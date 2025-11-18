#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Start backend logging in background
echo "Starting backend log collection..."
docker compose logs -f backend >> logs/backend_logs.txt 2>&1 &
BACKEND_LOG_PID=$!

# Start frontend/nginx logging in background
echo "Starting frontend log collection..."
docker compose logs -f nginx >> logs/frontend_logs.txt 2>&1 &
FRONTEND_LOG_PID=$!

echo "✅ Logging started!"
echo "Backend logs PID: $BACKEND_LOG_PID"
echo "Frontend logs PID: $FRONTEND_LOG_PID"
echo ""
echo "Logs are being saved to:"
echo "  - logs/backend_logs.txt"
echo "  - logs/frontend_logs.txt"
echo ""
echo "To stop logging, run: ./stop_logging.sh"
echo "To view logs, run: tail -f logs/backend_logs.txt"

