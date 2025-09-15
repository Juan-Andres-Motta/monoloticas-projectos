# Microservices Project - Tracking & Commission

This project contains two microservices connected via Apache Pulsar (DataStax Astra Streaming) for event-driven communication:

- **Tracking Service**: Records tracking events and publishes them to Pulsar
- **Commission Service**: Consumes tracking events and calculates commissions

## Architecture

```
┌─────────────────┐    Event     ┌──────────────────┐
│  Tracking       │─────────────▶│  Commission      │
│  Service        │   Pulsar     │  Service         │
│  (Port 8000)    │              │  (Port 8001)     │
└─────────────────┘              └──────────────────┘
        │                                 │
        ▼                                 ▼
┌─────────────────┐              ┌──────────────────┐
│  PostgreSQL     │              │  PostgreSQL      │
│  tracking-db    │              │  commission-db   │
│  (Port 5432)    │              │  (Port 5433)     │
└─────────────────┘              └──────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- DataStax Astra Streaming token (configured in .env files)

### ✅ Project Status

**UNIFIED SETUP COMPLETE** - All services are now running from a single docker-compose.yml:

✅ **Tracking Service**: Healthy and operational (port 8000)  
✅ **Commission Service**: Processing events via Pulsar (background service)  
✅ **PostgreSQL Databases**: Both tracking and commission DBs running  
✅ **DataStax Pulsar Integration**: Event streaming working perfectly  
✅ **Database Admin**: Adminer available for database management  

**Event Flow Verified**: Tracking → Pulsar → Commission ✅

### 1. Start All Services

```bash
# From the root directory
docker-compose up --build
```

This will start:
- **tracking-db**: PostgreSQL database for tracking service (port 5432)
- **commission-db**: PostgreSQL database for commission service (port 5433) 
- **tracking-service**: Tracking microservice (port 8000)
- **commission-service**: Commission microservice (port 8001)
- **adminer**: Database administration tool (port 9001)

### 2. Access Services

- **Tracking API**: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - Health Check: http://localhost:8000/api/v1/tracking/health

- **Commission API**: http://localhost:8001
  - API Docs: http://localhost:8001/docs  
  - Health Check: http://localhost:8001/api/v1/commission/health

- **Database Admin**: http://localhost:9001
  - Server: `tracking-db` or `commission-db`
  - Username: `tracking_user` / `commission_user`
  - Password: `tracking_password` / `commission_password`

### 3. Test the Integration

1. **Create a tracking event**:
```bash
curl -X POST "http://localhost:8000/api/v1/tracking/events" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "event_type": "purchase",
       "metadata": {"amount": 100.0, "product_id": "prod456"}
     }'
```

2. **Check if commission was created**:
```bash
curl "http://localhost:8001/api/v1/commission/commissions"
```

## Environment Configuration

### Unified .env File (Root Directory)

All configuration is now managed through a single `.env` file in the root directory:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env
```

Key variables to configure:
```env
# DataStax Astra Streaming
PULSAR_SERVICE_URL=pulsar+ssl://your-cluster.streaming.datastax.com:6651
PULSAR_TOKEN=your_datastax_token_here
PULSAR_TENANT=your-tenant-name
PULSAR_NAMESPACE=default
PULSAR_TOPIC=persistent://your-tenant-name/default/tracking-events

# Database passwords (can be customized)
TRACKING_DB_PASSWORD=tracking_password
COMMISSION_DB_PASSWORD=commission_password
```

### Individual Service .env Files

The individual services also have `.env` files for local development:
- `tracking/.env` - Used when running tracking service individually
- `comission/.env` - Used when running commission service individually

**Note**: When using docker-compose, the root `.env` file takes precedence.

## Development

### Running Individual Services (without Docker)

1. **Install dependencies** (for each service):
```bash
cd tracking  # or comission
poetry install
```

2. **Update database URLs** to point to localhost:
```
# Tracking
DATABASE_URL=postgresql://juan:@localhost:5432/trackingdb

# Commission  
DATABASE_URL=postgresql://commission_user:commission_password@localhost:5433/commissiondb
```

3. **Start the service**:
```bash
poetry run uvicorn main:app --reload --port 8000  # tracking
poetry run uvicorn main:app --reload --port 8001  # commission
```

### Useful Commands

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f tracking-service
docker-compose logs -f commission-service

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild and restart
docker-compose up --build --force-recreate
```

### Database Management

Access databases via Adminer at http://localhost:9001 or connect directly:

```bash
# Tracking database
docker exec -it tracking-postgres psql -U tracking_user -d trackingdb

# Commission database  
docker exec -it commission-postgres psql -U commission_user -d commissiondb
```

## Troubleshooting

### Pulsar Connection Issues
- Verify your DataStax Astra Streaming token is valid
- Ensure the tenant `miso-1-2025` exists in your DataStax console
- Check that the topic has proper permissions

### Database Connection Issues
- Ensure database containers are healthy: `docker-compose ps`
- Check database logs: `docker-compose logs tracking-db`
- Verify connection strings in .env files

### Service Health Checks
```bash
curl http://localhost:8000/api/v1/tracking/health
curl http://localhost:8001/api/v1/commission/health
```

## Project Structure

```
.
├── docker-compose.yml          # 🐋 Unified Docker Compose configuration
├── .env                        # 🔧 Unified environment variables
├── .env.example               # 📋 Environment template
├── .gitignore                 # 🔒 Git ignore rules
├── README.md                  # 📖 This documentation
├── start.sh                   # 🚀 Quick start script
├── stop.sh                    # 🛑 Stop services script
├── tracking/                  # 📊 Tracking microservice
│   ├── Dockerfile
│   ├── .env                   # (local development)
│   ├── main.py
│   ├── api/
│   ├── ingestion/
│   └── ...
└── comission/                 # 💰 Commission microservice  
    ├── Dockerfile
    ├── .env                   # (local development)
    ├── main.py
    ├── api/
    ├── commission/
    └── ...
```

### ✨ New Features

- **Unified Environment**: Single `.env` file manages all configuration
- **Simplified Setup**: All services configured from one location
- **Environment Template**: `.env.example` provides setup guidance
- **Better Security**: `.gitignore` prevents committing sensitive data
- **Quick Scripts**: `start.sh` and `stop.sh` for easy management
