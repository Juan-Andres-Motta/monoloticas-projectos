#!/bin/bash
# Simple Service Startup Script - HTTP mode only for testing

set -e

echo "🚀 Starting Services in HTTP Mode Only"
echo "======================================"

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Start services with basic HTTP configuration
echo "📦 Starting services with docker-compose..."
docker-compose up -d

echo ""
echo "⏳ Waiting 30 seconds for services to initialize..."
sleep 30

echo ""
echo "📋 Service Status:"
docker-compose ps

echo ""
echo "🔍 Testing Service Health:"

# Test campaign service
echo -n "Campaign Service (8002): "
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ UP"
else
    echo "❌ DOWN - checking logs..."
    docker-compose logs campaign-service | tail -10
fi

# Test tracking service  
echo -n "Tracking Service (8003): "
if curl -s http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ UP"
else
    echo "❌ DOWN"
fi

# Test commission service
echo -n "Commission Service (8004): "
if curl -s http://localhost:8004/health > /dev/null 2>&1; then
    echo "✅ UP"
else
    echo "❌ DOWN"
fi

# Test payment service
echo -n "Payment Service (8005): "
if curl -s http://localhost:8005/health > /dev/null 2>&1; then
    echo "✅ UP"
else
    echo "❌ DOWN"
fi

echo ""
echo "🎯 Services Ready for Topic Testing!"
echo "===================================="
echo ""
echo "Environment variables needed for topic testing:"
echo "  export PULSAR_TOKEN=your_datastax_token"
echo "  export PULSAR_SERVICE_URL=pulsar+ssl://pulsar-aws-useast1.streaming.datastax.com:6651"
echo ""

# Check if PULSAR_TOKEN is set
if [ -z "$PULSAR_TOKEN" ]; then
    echo "⚠️  PULSAR_TOKEN not set. Set it with:"
    echo "   export PULSAR_TOKEN=your_token_here"
    echo ""
    echo "💡 Even without the token, HTTP services are running for development"
else
    echo "✅ PULSAR_TOKEN is configured"
    echo ""
    echo "🎯 Ready to test topics with:"
    echo "   python topic_tester.py all"
    echo "   python topic_tester.py campaign"
fi

echo ""
echo "📋 Check service logs:"
echo "   docker-compose logs -f campaign-service"
echo "   docker-compose logs -f tracking-service"
echo "   docker-compose logs -f commission-service"
echo "   docker-compose logs -f payment-service"
