#!/bin/bash

# Commission Service Setup Script

echo "🚀 Setting up Commission Service with DataStax Astra Streaming"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and set your PULSAR_TOKEN"
    echo "   Get your token from: https://console.astra.datastax.com/"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Check if PULSAR_TOKEN is set
if grep -q "YOUR_PULSAR_TOKEN" .env; then
    echo "❌ Please set your actual PULSAR_TOKEN in .env file"
    echo "   Current: YOUR_PULSAR_TOKEN"
    echo "   Replace with your DataStax Astra Streaming token"
    exit 1
fi

echo "📦 Starting PostgreSQL databases..."
docker-compose up -d

echo "⏳ Waiting for databases to be ready..."
sleep 10

echo "🏥 Checking database health..."
docker-compose ps

echo ""
echo "✅ Setup complete! Now you can:"
echo "   1. Run tracking service: cd ../tracking && python main.py"
echo "   2. Run commission service: python main.py"
echo ""
echo "📚 Test with:"
echo "   curl http://localhost:8000/api/v1/tracking/health"
echo "   curl http://localhost:8001/api/v1/commissions/health"
