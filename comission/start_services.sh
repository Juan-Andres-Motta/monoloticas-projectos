#!/bin/bash

# 🚀 Start Services with Graceful Fallback

echo "🚀 Starting Microservices with DataStax Astra Streaming"
echo "========================================================"

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "❌ Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Check environment
echo ""
echo "1. Checking environment..."
cd /Users/juan/Desktop/uniandes/monoliticas/comission

if [ ! -f .env ]; then
    echo "❌ .env file not found - copying template"
    cp .env.example .env
    echo "⚠️  Please edit .env and set your PULSAR_TOKEN"
    echo "   Then run this script again"
    exit 1
fi

# Check ports
echo ""
echo "2. Checking ports..."
check_port 8000 || exit 1
check_port 8001 || exit 1

# Start databases
echo ""
echo "3. Starting databases..."
docker-compose up -d
sleep 5

# Start tracking service
echo ""
echo "4. Starting tracking service (port 8000)..."
cd /Users/juan/Desktop/uniandes/monoliticas/tracking

# Copy commission .env to tracking if needed
if [ ! -f .env ]; then
    cp ../comission/.env .env
fi

echo "   Starting in background..."
python main.py > tracking.log 2>&1 &
TRACKING_PID=$!
echo "   Tracking service PID: $TRACKING_PID"

# Wait a bit and check if it started
sleep 10
if kill -0 $TRACKING_PID 2>/dev/null; then
    echo "   ✅ Tracking service started"
    # Test health
    if curl -s http://localhost:8000/api/v1/tracking/health > /dev/null; then
        echo "   ✅ Tracking service health check passed"
    else
        echo "   ⚠️  Health check failed, but service is running"
    fi
else
    echo "   ❌ Tracking service failed to start"
    echo "   Check log: tail -f tracking.log"
fi

# Start commission service
echo ""
echo "5. Starting commission service (port 8001)..."
cd /Users/juan/Desktop/uniandes/monoliticas/comission

echo "   Starting in background..."
python main.py > commission.log 2>&1 &
COMMISSION_PID=$!
echo "   Commission service PID: $COMMISSION_PID"

# Wait a bit and check if it started
sleep 10
if kill -0 $COMMISSION_PID 2>/dev/null; then
    echo "   ✅ Commission service started"
    # Test health
    if curl -s http://localhost:8001/api/v1/commissions/health > /dev/null; then
        echo "   ✅ Commission service health check passed"
    else
        echo "   ⚠️  Health check failed, but service is running"
    fi
else
    echo "   ❌ Commission service failed to start"
    echo "   Check log: tail -f commission.log"
fi

echo ""
echo "🎯 Service Status:"
echo "=================="
echo "Tracking Service:    http://localhost:8000/api/v1/tracking/health"
echo "Commission Service:  http://localhost:8001/api/v1/commissions/health"
echo ""
echo "📊 Test Integration:"
echo "   ./test_integration.sh"
echo ""
echo "📋 View Logs:"
echo "   Tracking:   tail -f /Users/juan/Desktop/uniandes/monoliticas/tracking/tracking.log"
echo "   Commission: tail -f /Users/juan/Desktop/uniandes/monoliticas/comission/commission.log"
echo ""
echo "🛑 Stop Services:"
echo "   kill $TRACKING_PID $COMMISSION_PID"
echo ""

# Save PIDs for easy cleanup
echo "$TRACKING_PID" > tracking.pid
echo "$COMMISSION_PID" > commission.pid

echo "✅ Setup complete! Both services should be running."
echo "   Even if Pulsar connection fails, the services will work via API."
