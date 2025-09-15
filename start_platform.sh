#!/bin/bash

# =================================================================
# UNIFIED EVENT-DRIVEN MICROSERVICES STARTUP SCRIPT
# =================================================================

set -e

echo "🚀 Starting Alpes Partners Event-Driven Microservices Platform"
echo "================================================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your settings"
    exit 1
fi

# Load environment variables
source .env

echo "📋 Configuration:"
echo "  - BFF Service Mode: ${BFF_SERVICE_MODE}"
echo "  - Campaign Service Mode: ${CAMPAIGN_SERVICE_MODE}" 
echo "  - Tracking Service Mode: ${TRACKING_SERVICE_MODE}"
echo "  - Commission Service Mode: ${COMMISSION_SERVICE_MODE}"
echo "  - Payment Service Mode: ${PAYMENT_SERVICE_MODE}"
echo "  - Pulsar Tenant: ${PULSAR_TENANT}"
echo "  - Pulsar Namespace: ${PULSAR_NAMESPACE}"
echo ""

# Build and start services
echo "🔨 Building and starting services..."
docker-compose build --no-cache
docker-compose up -d

echo ""
echo "⏳ Waiting for services to become healthy..."
sleep 20

# Check service health
echo ""
echo "🔍 Checking service health:"

services=(
    "bff-service:${BFF_SERVICE_PORT}"
    "campaign-service:${CAMPAIGN_SERVICE_PORT}"
)

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    echo -n "  - $name: "
    
    if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Unhealthy"
    fi
done

echo ""
echo "🎯 Services are starting up!"
echo ""
echo "📡 Available endpoints:"
echo "  - BFF API: http://localhost:${BFF_SERVICE_PORT}"
echo "  - BFF Docs: http://localhost:${BFF_SERVICE_PORT}/docs"
echo "  - Campaign API: http://localhost:${CAMPAIGN_SERVICE_PORT} (if hybrid mode)"
echo "  - Database Admin: http://localhost:${ADMINER_PORT}"
echo ""
echo "📋 Useful commands:"
echo "  - View logs: docker-compose logs -f [service-name]"
echo "  - Stop services: docker-compose down"
echo "  - Restart service: docker-compose restart [service-name]"
echo ""
echo "🎉 Platform is ready for event-driven operations!"
