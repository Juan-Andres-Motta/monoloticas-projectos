# 🚀 Local Development Guide

## Option 1: Docker Compose (Full Platform)

### Start the platform:
```bash
cd /path/to/your/project

# Start all services (databases + BFF)
docker-compose up -d

# Check status
docker ps

# View logs
docker-compose logs -f bff-service
```

### Test the BFF:
```bash
# Health check
curl http://localhost:8001/health

# Get JWT token
docker exec bff-service python generate_jwt.py

# Test API endpoint
curl -X POST "http://localhost:8001/api/v1/campaigns/camp_winter_sale/accept" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "partner_001", "partner_type": "INFLUENCER", "acceptance_terms": {"commission_type": "CPA", "commission_rate": 10.5, "cookie_duration_days": 30, "promotional_methods": ["social_media"]}, "estimated_monthly_reach": 50000}'
```

### Stop the platform:
```bash
docker-compose down
```

## Option 2: Local Python (BFF Only)

### Prerequisites:
```bash
cd /path/to/your/project/bff

# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

### Run BFF locally:
```bash
# Activate virtual environment
poetry shell

# Run with the simplified version (no Pulsar)
python main_simple.py

# Or run with uvicorn directly
uvicorn main_simple:app --host 0.0.0.0 --port 8001 --reload
```

### Test locally:
```bash
# Health check
curl http://localhost:8001/health

# Generate JWT token
python generate_jwt.py

# Access Swagger docs
open http://localhost:8001/docs
```

## Option 3: Hybrid (Local BFF + Docker Databases)

### Start only databases:
```bash
docker-compose up -d campaign-db tracking-db commission-db payment-db
```

### Run BFF locally:
```bash
cd bff
poetry shell
python main_simple.py
```

## 🔧 Development Workflow

### Live reload during development:
```bash
cd bff
poetry shell
uvicorn main_simple:app --host 0.0.0.0 --port 8001 --reload
```

### View API documentation:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
- OpenAPI JSON: http://localhost:8001/openapi.json

### Database access (when using Docker):
- Adminer: http://localhost:9001
- Direct PostgreSQL connections available on ports 5432-5435

## 📋 Environment Variables

If running locally, you can set these environment variables:
```bash
export BFF_SERVICE_PORT=8001
export BFF_SERVICE_MODE=http
export JWT_SECRET_KEY=your_jwt_secret_key_here_change_in_production
export JWT_ALGORITHM=HS256
export JWT_REQUIRE_VALIDATION=false
export LOG_LEVEL=INFO
```

## 🔍 Troubleshooting

### Port conflicts:
```bash
# Check what's using port 8001
lsof -i :8001

# Use different port
uvicorn main_simple:app --host 0.0.0.0 --port 8002
```

### Python dependencies:
```bash
# Reinstall dependencies
poetry install --no-cache

# Check installed packages
poetry show
```

### Docker issues:
```bash
# Clean up containers
docker-compose down -v
docker system prune -f

# Rebuild images
docker-compose build --no-cache
```
