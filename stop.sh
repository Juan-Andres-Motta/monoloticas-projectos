#!/bin/bash

echo "🛑 Stopping Microservices Project"
echo "================================="

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found."
    exit 1
fi

echo "📋 Stopping all services..."
docker-compose down

echo ""
echo "🧹 Cleaning up (optional):"
echo "  • To remove volumes: docker-compose down -v"
echo "  • To remove images: docker system prune -f"
echo ""
echo "✅ Services stopped successfully"
