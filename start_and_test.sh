#!/bin/bash
# Quick Service Startup and Testing Script

set -e

echo "🚀 Starting All Services in Event-Driven Mode"
echo "============================================="

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Start services with event-driven configuration
echo "📦 Starting services with docker-compose..."
if [ -f "docker-compose.event-driven.yml" ]; then
    echo "Using event-driven configuration..."
    docker-compose -f docker-compose.event-driven.yml up -d
else
    echo "Using default configuration..."
    docker-compose up -d
fi

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
    echo "❌ DOWN"
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
echo "🎯 Ready to Test Topics!"
echo "========================"
echo ""
echo "Commands to test individual services:"
echo "  python topic_tester.py campaign     # Test campaign service"
echo "  python topic_tester.py tracking     # Test tracking service"
echo "  python topic_tester.py commission   # Test commission service"  
echo "  python topic_tester.py payment      # Test payment service"
echo ""
echo "Or test all at once:"
echo "  python topic_tester.py all"
echo ""
echo "Check service logs:"
echo "  docker-compose logs -f campaign-service"
echo "  docker-compose logs -f tracking-service"
echo "  docker-compose logs -f commission-service"
echo "  docker-compose logs -f payment-service"
echo ""
echo "Environment variables needed:"
echo "  export PULSAR_TOKEN=your_datastax_token"
echo "  export PULSAR_SERVICE_URL=pulsar+ssl://pulsar-aws-useast1.streaming.datastax.com:6651"
echo ""

# Check if PULSAR_TOKEN is set
if [ -z "$PULSAR_TOKEN" ]; then
    echo "⚠️  PULSAR_TOKEN not set. Please set it:"
    echo "   export PULSAR_TOKEN=your_token_here"
else
    echo "✅ PULSAR_TOKEN is configured"
fi

echo ""
echo "🎉 All services are ready for topic testing!"
