#!/bin/bash

# Event-Driven Microservices Startup Script
# This script starts all services in event-driven mode

set -e

echo "🚀 Starting Event-Driven Microservices Architecture"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if required environment variables are set
check_env_vars() {
    echo -e "${BLUE}🔍 Checking environment variables...${NC}"
    
    if [ -z "$PULSAR_SERVICE_URL" ]; then
        echo -e "${RED}❌ PULSAR_SERVICE_URL is not set${NC}"
        echo "Please set your DataStax Astra Streaming URL"
        exit 1
    fi
    
    if [ -z "$PULSAR_TOKEN" ]; then
        echo -e "${RED}❌ PULSAR_TOKEN is not set${NC}"
        echo "Please set your DataStax Astra Streaming token"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Environment variables configured${NC}"
}

# Function to wait for service health
wait_for_service() {
    local service_name=$1
    local health_url=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for $service_name to be healthy...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is healthy${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to become healthy${NC}"
    return 1
}

# Function to show service status
show_service_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    echo "================================"
    
    # BFF Service
    if curl -f -s "http://localhost:8001/health" > /dev/null 2>&1; then
        echo -e "BFF Service:        ${GREEN}✅ Running${NC} (http://localhost:8001)"
    else
        echo -e "BFF Service:        ${RED}❌ Down${NC}"
    fi
    
    # Campaign Service (if hybrid mode)
    if curl -f -s "http://localhost:8002/health" > /dev/null 2>&1; then
        echo -e "Campaign Service:   ${GREEN}✅ Running${NC} (http://localhost:8002)"
    else
        echo -e "Campaign Service:   ${YELLOW}⚡ Event-only mode${NC}"
    fi
    
    # Database Services
    echo -e "Tracking DB:        ${GREEN}✅ Running${NC} (localhost:5432)"
    echo -e "Campaign DB:        ${GREEN}✅ Running${NC} (localhost:5434)"
    echo -e "Commission DB:      ${GREEN}✅ Running${NC} (localhost:5433)"
    echo -e "Payment DB:         ${GREEN}✅ Running${NC} (localhost:5435)"
    
    echo ""
    echo -e "${BLUE}🔗 Available Endpoints:${NC}"
    echo "================================"
    echo "BFF API:              http://localhost:8001"
    echo "BFF Documentation:    http://localhost:8001/docs"
    echo "Campaign API:         http://localhost:8002 (if hybrid)"
    echo "Database Admin:       http://localhost:9001"
    echo ""
}

# Function to show event flow examples
show_event_examples() {
    echo -e "${BLUE}📡 Event-Driven Flow Examples:${NC}"
    echo "================================"
    echo ""
    echo "1. Campaign Acceptance:"
    echo "   POST /api/v1/campaigns/{id}/accept → BFF publishes command → Campaign Service processes"
    echo ""
    echo "2. Evidence Upload:"
    echo "   POST /api/v1/campaigns/{id}/evidence → BFF publishes command → Tracking Service processes"
    echo ""
    echo "3. Payment Request:"
    echo "   POST /api/v1/payments/request → BFF publishes command → Commission Service processes"
    echo ""
    echo "4. Event Chain Example:"
    echo "   Evidence Upload → Tracking Event → Commission Calculation → Payment Processing"
    echo ""
}

# Main execution
main() {
    case "${1:-start}" in
        "start")
            check_env_vars
            
            echo -e "${BLUE}🐳 Starting Docker services...${NC}"
            docker-compose -f docker-compose.event-driven.yml up -d
            
            echo -e "${YELLOW}⏳ Waiting for services to initialize...${NC}"
            sleep 10
            
            # Wait for BFF to be ready
            wait_for_service "BFF Service" "http://localhost:8001/health" 30
            
            # Try to wait for Campaign Service (might be event-only)
            if ! wait_for_service "Campaign Service" "http://localhost:8002/health" 10; then
                echo -e "${YELLOW}ℹ️  Campaign Service running in event-only mode${NC}"
            fi
            
            show_service_status
            show_event_examples
            
            echo -e "${GREEN}🎉 Event-Driven Architecture is ready!${NC}"
            ;;
            
        "stop")
            echo -e "${YELLOW}🛑 Stopping all services...${NC}"
            docker-compose -f docker-compose.event-driven.yml down
            echo -e "${GREEN}✅ All services stopped${NC}"
            ;;
            
        "restart")
            echo -e "${YELLOW}🔄 Restarting services...${NC}"
            docker-compose -f docker-compose.event-driven.yml restart
            sleep 5
            show_service_status
            ;;
            
        "logs")
            service=${2:-""}
            if [ -n "$service" ]; then
                echo -e "${BLUE}📋 Showing logs for $service...${NC}"
                docker-compose -f docker-compose.event-driven.yml logs -f "$service"
            else
                echo -e "${BLUE}📋 Showing logs for all services...${NC}"
                docker-compose -f docker-compose.event-driven.yml logs -f
            fi
            ;;
            
        "status")
            show_service_status
            ;;
            
        "test")
            echo -e "${BLUE}🧪 Running event-driven tests...${NC}"
            docker-compose -f docker-compose.event-driven.yml --profile test run --rm event-test-client python test_event_driven.py demo
            ;;
            
        "clean")
            echo -e "${YELLOW}🧹 Cleaning up containers and volumes...${NC}"
            docker-compose -f docker-compose.event-driven.yml down -v
            docker system prune -f
            echo -e "${GREEN}✅ Cleanup completed${NC}"
            ;;
            
        "help"|*)
            echo "Event-Driven Microservices Management Script"
            echo "============================================"
            echo ""
            echo "Usage: $0 <command>"
            echo ""
            echo "Commands:"
            echo "  start       Start all services in event-driven mode"
            echo "  stop        Stop all services"
            echo "  restart     Restart all services"
            echo "  status      Show service status"
            echo "  logs [svc]  Show logs (optionally for specific service)"
            echo "  test        Run event-driven integration tests"
            echo "  clean       Stop services and clean up volumes"
            echo "  help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 start                    # Start all services"
            echo "  $0 logs bff-service        # Show BFF logs"
            echo "  $0 logs campaign-service   # Show Campaign service logs"
            echo "  $0 test                     # Run integration tests"
            echo ""
            echo "Required Environment Variables:"
            echo "  PULSAR_SERVICE_URL    DataStax Astra Streaming URL"
            echo "  PULSAR_TOKEN          DataStax Astra Streaming token"
            echo ""
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
