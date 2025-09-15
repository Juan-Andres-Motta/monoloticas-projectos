#!/bin/bash

# =================================================================
# UNIFIED MICROSERVICES STOP SCRIPT
# =================================================================

echo "🛑 Stopping Alpes Partners Event-Driven Microservices Platform"
echo "================================================================"

# Stop all services
echo "🔽 Stopping all services..."
docker-compose down

# Optional: Remove volumes (uncomment if you want to reset databases)
# echo "🗑️  Removing volumes..."
# docker-compose down -v

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "📋 To restart:"
echo "  ./start_platform.sh"
echo ""
echo "📋 To remove all data (reset databases):"
echo "  docker-compose down -v"
