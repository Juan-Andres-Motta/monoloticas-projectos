# Microservices Project - Event-Driven Architecture

This project demonstrates **two architectural patterns** for microservice communication:

## 🏗️ Architecture Patterns

### 1. Traditional HTTP-based (Original)
- **Tracking Service**: HTTP API for recording tracking events
- **Commission Service**: HTTP API for commission calculations  
- **Campaign Service**: HTTP API for campaign management
- **Payment Service**: HTTP API for payment processing

### 2. Event-Driven with Avro Schemas (New)
- **Services communicate via Pulsar topics** instead of HTTP calls
- **Avro schemas** provide type safety and schema evolution
- **Command events** trigger operations in specific services
- **Domain events** notify when operations complete
- **Correlation IDs** for tracking workflows across services

## 🎯 Event-Driven Benefits

✅ **Loose Coupling**: Services don't need to know about each other  
✅ **Better Scalability**: Asynchronous processing improves performance  
✅ **Fault Tolerance**: Services work independently  
✅ **Type Safety**: Avro schemas prevent integration errors  
✅ **Schema Evolution**: Backward/forward compatibility  
✅ **Event Tracing**: Complete audit trail with correlation IDs

## Event-Driven Architecture

```
                    📡 Apache Pulsar Topics 📡
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │  campaign-commands  tracking-commands  commission-commands  │
    │  campaign-events    tracking-events    commission-events    │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
                    ▲                           ▲
                    │ Avro                     │ Avro  
                    │ Messages                 │ Messages
                    ▼                           ▼
    ┌─────────────────┐                   ┌──────────────────┐
    │  Campaign       │                   │  Commission      │
    │  Service        │                   │  Service         │
    │  (Event Mode)   │                   │  (Event Mode)    │
    └─────────────────┘                   └──────────────────┘
            │                                     │
            ▼                                     ▼
    ┌─────────────────┐                   ┌──────────────────┐
    │  PostgreSQL     │                   │  PostgreSQL      │
    │  campaign-db    │                   │  commission-db   │
    └─────────────────┘                   └──────────────────┘
                    ▲
                    │ Commands & Events
                    │
    ┌─────────────────┐                   ┌──────────────────┐
    │  Tracking       │                   │  Payment         │
    │  Service        │                   │  Service         │
    │  (Event Mode)   │                   │  (Event Mode)    │
    └─────────────────┘                   └──────────────────┘
            │                                     │
            ▼                                     ▼
    ┌─────────────────┐                   ┌──────────────────┐
    │  PostgreSQL     │                   │  PostgreSQL      │
    │  tracking-db    │                   │  payment-db      │
    └─────────────────┘                   └──────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- DataStax Astra Streaming token (configured in .env files)

### ✅ Project Status

**UNIFIED SETUP COMPLETE** - All services are now running from a single docker-compose.yml:

✅ **BFF Service**: Unified API with JWT authentication (port 8002)
✅ **Tracking Service**: Healthy and operational (port 8000)
✅ **Commission Service**: Processing events via Pulsar (background service)
✅ **PostgreSQL Databases**: Both tracking and commission DBs running
✅ **DataStax Pulsar Integration**: Event streaming working perfectly
✅ **Database Admin**: Adminer available for database management

**Event Flow Verified**: BFF → Pulsar (BFF Topics) → Future Services ✅
**Direct Event Flow**: Tracking → Pulsar → Commission ✅

### 1. Start All Services

```bash
# From the root directory
docker-compose up --build
```

This will start:
- **bff-service**: Backend for Frontend API (port 8002)
- **tracking-db**: PostgreSQL database for tracking service (port 5432)
- **commission-db**: PostgreSQL database for commission service (port 5433)
- **tracking-service**: Tracking microservice (port 8000)
- **commission-service**: Commission microservice (port 8001)
- **adminer**: Database administration tool (port 9001)

### 2. Access Services

- **BFF API**: http://localhost:8002
  - API Docs: http://localhost:8002/docs
  - Health Check: http://localhost:8002/health
  - JWT Token Generator: `cd bff && python generate_jwt.py`

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

#### Option A: Test via BFF (Recommended)

1. **Generate a JWT token**:
```bash
cd bff
python generate_jwt.py
# Copy the generated JWT token
```

2. **Test BFF endpoints** (replace YOUR_JWT_TOKEN with the generated token):

**Accept Campaign**:
```bash
curl -X POST "http://localhost:8002/api/v1/campaigns/camp123/accept" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "accepted_terms": true,
       "metadata": {"source": "mobile_app"}
     }'
```

**Upload Evidence**:
```bash
curl -X POST "http://localhost:8002/api/v1/evidence/upload" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "campaign_id": "camp123",
       "evidence_type": "photo",
       "file_url": "https://example.com/photo.jpg",
       "metadata": {"description": "Product photo"}
     }'
```

**Request Payment**:
```bash
curl -X POST "http://localhost:8002/api/v1/payments/request" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{
       "amount": 150.00,
       "currency": "USD",
       "payment_method": "paypal",
       "account_details": {"email": "user@example.com"}
     }'
```

#### Option B: Test Direct Services

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

# JWT Configuration for BFF
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_REQUIRE_VALIDATION=false

# Database passwords (can be customized)
TRACKING_DB_PASSWORD=tracking_password
COMMISSION_DB_PASSWORD=commission_password
```

### Individual Service .env Files

The individual services also have `.env` files for local development:
- `bff/.env` - Used when running BFF service individually
- `tracking/.env` - Used when running tracking service individually
- `comission/.env` - Used when running commission service individually

**Note**: When using docker-compose, the root `.env` file takes precedence.

## Development

### Running Individual Services (without Docker)

1. **Install dependencies** (for each service):
```bash
cd bff        # or tracking, or comission
poetry install
```

2. **Update database URLs** to point to localhost (for services that use DB):
```bash
# Tracking
DATABASE_URL=postgresql://juan:@localhost:5432/trackingdb

# Commission
DATABASE_URL=postgresql://commission_user:commission_password@localhost:5433/commissiondb
```

3. **Start the service**:
```bash
poetry run uvicorn main:app --reload --port 8002  # bff
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
curl http://localhost:8002/health                          # BFF
curl http://localhost:8000/api/v1/tracking/health          # Tracking
curl http://localhost:8001/api/v1/commission/health        # Commission
```

## Project Structure

```
.
├── docker-compose.yml          # 🐋 Unified Docker Compose configuration
├── .env                        # 🔧 Unified environment variables
├── .env.example               # 📋 Environment template
├── .gitignore                 # 🔒 Git ignore rules
├── README.md                  # 📖 This documentation
├── bff/                       # 🚀 Backend for Frontend Service
│   ├── Dockerfile
│   ├── .env.example           # BFF-specific environment
│   ├── main.py
│   ├── generate_jwt.py        # JWT token generator
│   ├── api/
│   │   ├── routers/          # FastAPI routers
│   │   └── schemas/          # Pydantic schemas
│   ├── application/          # Application layer
│   │   └── events/           # Integration events
│   ├── config/               # Configuration
│   ├── messaging/            # Pulsar integration
│   └── ...
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

### ✨ Key Features

**Architecture & Patterns**:
- **Clean Architecture**: Hexagonal architecture with clear layer separation
- **Domain-Driven Design**: Aggregate roots and bounded contexts
- **CQRS**: Command Query Responsibility Segregation
- **Event-Driven**: Apache Pulsar for async communication
- **Microservices**: Independent, loosely coupled services

**BFF Service**:
- **JWT Authentication**: Flexible token extraction without strict validation
- **Command Publishing**: Sends BFF-specific commands to dedicated Pulsar topics (not to tracking/commission)
- **Clean API**: RESTful endpoints for campaign, evidence, and payment operations
- **Schema Validation**: Comprehensive Pydantic DTOs for request/response validation
- **OpenAPI Documentation**: Auto-generated API docs with JWT security schemes

**Infrastructure**:
- **Unified Environment**: Single `.env` file manages all configuration
- **Simplified Setup**: All services configured from one location
- **Environment Template**: `.env.example` provides setup guidance
- **Better Security**: `.gitignore` prevents committing sensitive data
- **Quick Scripts**: `start.sh` and `stop.sh` for easy management

## 🎯 Event-Driven Implementation Summary

I've implemented a complete **event-driven microservices architecture** using **Apache Pulsar with Avro schemas**. Here's what was created:

### 📋 Key Components Created

1. **Avro Schema Definitions** (`messaging/schemas/avro_schemas.py`)
   - Command schemas for triggering operations
   - Domain event schemas for notifications
   - Type-safe message structures with schema evolution

2. **Event Publisher** (`messaging/avro_publisher.py`)
   - Publishes commands to trigger operations in other services
   - Publishes domain events when operations complete
   - Uses Avro schemas for type safety

3. **Event Consumer** (`messaging/avro_consumer.py`)
   - Listens to command topics for each service
   - Routes commands to appropriate handlers
   - Handles message acknowledgment and error handling

4. **Event Handlers** (`messaging/event_handlers.py`)
   - Process commands received via events instead of HTTP
   - Integrate with existing business logic
   - Maintain correlation IDs for tracing

5. **Service Modes**
   - **HTTP Mode**: Traditional REST API endpoints
   - **Event Mode**: Pure event-driven communication
   - **Hybrid Mode**: Both HTTP and events supported

### 🔄 Event Flow Examples

**Traditional HTTP:**
```
Client → POST /campaigns → Campaign Service → POST /tracking → Tracking Service
```

**Event-Driven:**
```
Client → campaign.create.command.v1 → Campaign Service → campaign.created.v1 → Other Services
```

### 🚀 Benefits Achieved

- ✅ **Loose Coupling**: Services communicate via events, not direct calls
- ✅ **Type Safety**: Avro schemas prevent integration errors
- ✅ **Scalability**: Asynchronous processing improves performance
- ✅ **Resilience**: Services work even if others are down
- ✅ **Traceability**: Correlation IDs track workflows across services
- ✅ **Schema Evolution**: Backward/forward compatible message formats

### 📖 Usage

```bash
# Test event-driven architecture
python test_event_driven.py demo

# Start service in event mode  
export CAMPAIGN_SERVICE_MODE=event
python main_event_driven.py

# Start with Docker Compose
docker-compose -f docker-compose.event-driven.yml up -d
```

### 📚 Documentation

- [`EVENT_DRIVEN_GUIDE.md`](./EVENT_DRIVEN_GUIDE.md) - Complete implementation guide
- [`test_event_driven.py`](./test_event_driven.py) - Demo script and examples
- [`docker-compose.event-driven.yml`](./docker-compose.event-driven.yml) - Event-driven deployment

This implementation demonstrates how to **transition from HTTP-based microservices to event-driven architecture** while maintaining backward compatibility and providing significant architectural improvements.
