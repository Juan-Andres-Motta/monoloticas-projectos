# Alpes Partners Event-Driven Microservices Platform

A FastAPI-based Backend for Frontend (BFF) service with event-driven microservices architecture using Apache Pulsar.

## 🚀 Quick Start

### Option 1: One-Command Startup
```bash
./start_local.sh
```

### Option 2: Docker Compose
```bash
# Start all services
docker-compose up -d

# Check status
docker ps

# View logs
docker-compose logs -f bff-service
```

### Option 3: Local Development
```bash
cd bff
poetry install
poetry run python main_simple.py
```

## 🔗 Access Points

- **BFF API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Database Admin**: http://localhost:9001 (when using Docker)

## 🧪 Testing

### Generate JWT Token:
```bash
# If using Docker
docker exec bff-service python generate_jwt.py

# If running locally
cd bff && python generate_jwt.py
```

### Test API Endpoints:
```bash
# Health check
curl http://localhost:8001/health

# Campaign acceptance (requires JWT)
curl -X POST "http://localhost:8001/api/v1/campaigns/camp_winter_sale/accept" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "partner_id": "partner_001",
    "partner_type": "INFLUENCER",
    "acceptance_terms": {
      "commission_type": "CPA",
      "commission_rate": 10.5,
      "cookie_duration_days": 30,
      "promotional_methods": ["social_media"]
    },
    "estimated_monthly_reach": 50000
  }'
```

## 🏗️ Architecture

- **BFF Service**: FastAPI application (Port 8001)
- **Databases**: PostgreSQL instances for each service
  - Campaign DB (Port 5432)
  - Tracking DB (Port 5433)
  - Commission DB (Port 5434)
  - Payment DB (Port 5435)
- **Message Broker**: Apache Pulsar (DataStax Astra Streaming)

## 🛑 Stopping Services

```bash
# Docker Compose
docker-compose down

# Remove volumes too
docker-compose down -v
```

## 📚 Documentation

See `run_local.md` for detailed setup instructions and troubleshooting.
