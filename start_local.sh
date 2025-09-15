#!/bin/bash

echo "🚀 Starting Alpes Partners Platform Locally"
echo "=========================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check required ports
echo "🔍 Checking ports..."
check_port 8001 || exit 1
check_port 5432 || echo "⚠️  PostgreSQL port 5432 in use (may be ok if you have local PostgreSQL)"

echo ""
echo "Choose how to run the platform:"
echo "1) Docker Compose (Full platform with databases)"
echo "2) Local Python (BFF only, requires manual database setup)"
echo "3) Hybrid (Local BFF + Docker databases)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🐳 Starting with Docker Compose..."
        docker-compose up -d
        echo ""
        echo "✅ Platform started! Services:"
        echo "   - BFF: http://localhost:8001"
        echo "   - API Docs: http://localhost:8001/docs"
        echo "   - Adminer: http://localhost:9001"
        echo ""
        echo "🔗 Test with:"
        echo "   curl http://localhost:8001/health"
        ;;
    2)
        echo "🐍 Starting with Local Python..."
        cd "$SCRIPT_DIR/bff"
        if ! command -v poetry &> /dev/null; then
            echo "❌ Poetry not found. Installing..."
            curl -sSL https://install.python-poetry.org | python3 -
        fi
        echo "📦 Installing dependencies..."
        poetry install
        echo "🚀 Starting BFF service..."
        poetry run python main_simple.py
        ;;
    3)
        echo "🔀 Starting Hybrid mode..."
        echo "🐳 Starting databases..."
        docker-compose up -d campaign-db tracking-db commission-db payment-db
        sleep 5
        echo "🐍 Starting BFF locally..."
        cd "$SCRIPT_DIR/bff"
        if ! command -v poetry &> /dev/null; then
            echo "❌ Poetry not found. Installing..."
            curl -sSL https://install.python-poetry.org | python3 -
        fi
        poetry install
        poetry run python main_simple.py
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
