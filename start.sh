#!/bin/bash

echo "🚀 Starting Microservices Project"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "📋 Starting all services..."
echo ""

# Start services with build
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🔍 Checking service health:"

# Check tracking service
if curl -f http://localhost:8000/api/v1/tracking/health &> /dev/null; then
    echo "✅ Tracking Service (http://localhost:8000) - Ready"
else
    echo "❌ Tracking Service - Not ready yet"
fi

# Check commission service  
if curl -f http://localhost:8001/api/v1/commission/health &> /dev/null; then
    echo "✅ Commission Service (http://localhost:8001) - Ready"
else
    echo "❌ Commission Service - Not ready yet"
fi

echo ""
echo "🌐 Available Services:"
echo "  • Tracking API: http://localhost:8000"
echo "  • Tracking Docs: http://localhost:8000/docs"
echo "  • Commission API: http://localhost:8001"  
echo "  • Commission Docs: http://localhost:8001/docs"
echo "  • Database Admin: http://localhost:9001"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "📝 To view logs: docker-compose logs -f [service-name]"
echo "🛑 To stop: docker-compose down"
