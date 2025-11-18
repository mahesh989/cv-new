#!/bin/bash

echo "Stopping log collection processes..."

# Kill all docker compose logs processes
pkill -f "docker compose logs -f backend"
pkill -f "docker compose logs -f nginx"

echo "✅ Logging stopped!"

