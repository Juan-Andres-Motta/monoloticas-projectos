# Commission Service

A microservice for calculating and managing commissions based on tracking events from the Tracking Service. This service uses event-driven architecture with Apache Pulsar for communication.

## Architecture

The service follows Domain-Driven Design (DDD) and Clean Architecture principles:

```
commission/
├── api/                          # API Layer (Controllers)
├── config/                       # Configuration & DI Container
├── commission/                   # Commission Bounded Context
│   ├── application/             # Application Services & Command Handlers
│   ├── domain/                  # Domain Models, Events, Repositories
│   └── infrastructure/          # Database Models, External Services
├── infrastructure/              # Cross-cutting Infrastructure
│   └── messaging/              # Pulsar Consumer/Publisher
└── seedwork/                   # Shared Domain Building Blocks
```

## Features

### Commission Calculation
- Automatic commission calculation based on tracking events
- Configurable commission rates by partner and interaction type
- Support for different interaction types (click, view, engagement)
- Premium partner bonuses

### Business Rules
- **Commission Rates**:
  - Click: 10% base rate ($2.00 base amount)
  - View: 5% base rate ($0.50 base amount)
  - Engagement: 15% base rate ($5.00 base amount)
- **Premium Partners**: 50% bonus on base rates
- **Duplicate Prevention**: Prevents duplicate commissions for same tracking event

### Event-Driven Architecture
- Consumes tracking events from Apache Pulsar
- Publishes commission calculated events
- Supports notification handlers for partner alerts

### REST API
- Calculate commissions manually
- Query commissions by ID, partner, or campaign
- Health check endpoints
- Pagination support

## Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your DataStax Astra Streaming token
# PULSAR_TOKEN=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. Start Infrastructure
```bash
# Start PostgreSQL databases (Pulsar is managed by DataStax)
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt
# or using poetry
poetry install
```

### 4. Run Commission Service
```bash  
cd ../comission
python main.py  # Port 8001
```

### 5. Test the Service
```bash
# Health check
curl http://localhost:8001/api/v1/commissions/health

# Calculate commission manually
curl -X POST http://localhost:8001/api/v1/commissions/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_event_id": "550e8400-e29b-41d4-a716-446655440000",
    "partner_id": "partner_premium_1", 
    "campaign_id": "campaign_123",
    "visitor_id": "visitor_456",
    "interaction_type": "click"
  }'
```

## Event Flow

1. **Tracking Service** records tracking event
2. **Tracking Service** publishes event to DataStax Astra Streaming topic `persistent://miso-1-2025/default/tracking-events`
3. **Commission Service** consumes event from Pulsar via shared subscription
4. **Commission Service** calculates commission using business rules
5. **Commission Service** stores commission in PostgreSQL database
6. **Commission Service** publishes `commission.calculated.v1` domain event
7. **Notification Handler** processes commission event (partner notifications, audit logs, etc.)

## API Endpoints

### Commission Management
- `POST /api/v1/commissions/calculate` - Calculate commission
- `GET /api/v1/commissions/{id}` - Get commission by ID
- `GET /api/v1/commissions/partner/{partner_id}` - Get partner commissions
- `GET /api/v1/commissions/campaign/{campaign_id}` - Get campaign commissions
- `GET /api/v1/commissions/health` - Service health check

## Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (default: commission database)
- `PULSAR_SERVICE_URL`: DataStax Astra Streaming URL (default: pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651)
- `PULSAR_TOKEN`: Your DataStax Astra Streaming authentication token (required)

### Database
- PostgreSQL database for commission storage
- Automatic table creation on startup
- Connection pooling enabled

### DataStax Astra Streaming Topics
- **Consumes**: `persistent://miso-1-2025/default/tracking-events` (tracking event notifications)
- **Publishes**: `persistent://miso-1-2025/default/commissions` (commission notifications)
- **Subscription**: `commission-service-subscription` (shared subscription for horizontal scaling)

## Development

### Project Structure
```
commission/
├── domain/
│   ├── aggregates/commission.py      # Commission aggregate root
│   ├── events/                       # Domain events  
│   └── repositories/                 # Repository interfaces
├── application/
│   ├── commands/                     # Application commands
│   └── handlers/                     # Command & event handlers
└── infrastructure/
    ├── models/                       # Database models
    └── repositories/                 # Repository implementations
```

### Key Components

**Commission Aggregate** (`commission/domain/aggregates/commission.py`)
- Core business entity for commission calculation
- Encapsulates commission business rules and validation
- Emits domain events when commissions are calculated

**Calculate Commission Handler** (`commission/application/handlers/calculate_commission_handler.py`)
- Application service for commission calculation
- Coordinates between domain and infrastructure layers
- Handles command processing and event publishing

**Pulsar Consumer** (`infrastructure/messaging/pulsar_consumer.py`)
- Consumes tracking events from Pulsar
- Converts events to application commands
- Handles message acknowledgment and error processing

## Testing

### Integration with Tracking Service
1. Start both services (tracking on :8000, commission on :8001)
2. Create tracking event via tracking service API
3. Verify commission is calculated automatically
4. Check commission via commission service API

### Manual Testing
```bash
# Create tracking event (triggers commission)
curl -X POST http://localhost:8000/api/v1/tracking/events \
  -H "Content-Type: application/json" \
  -d '{
    "partner_id": "partner_premium_1",
    "campaign_id": "campaign_123", 
    "visitor_id": "visitor_456",
    "interaction_type": "click",
    "source_url": "https://example.com",
    "destination_url": "https://destination.com"
  }'

# Check generated commission
curl http://localhost:8001/api/v1/commissions/partner/partner_premium_1
```

## Monitoring

### Logs
- Service startup and configuration logs
- Event processing logs (Pulsar consumption)
- Commission calculation results
- Error handling and recovery logs

### Health Checks
- Service health endpoint
- Database connectivity
- Pulsar connectivity (via consumer status)

## Production Considerations

### Scalability
- Horizontal scaling with shared Pulsar subscription
- Database connection pooling
- Stateless application design

### Reliability
- Message acknowledgment in Pulsar consumer
- Transaction support in database operations
- Error handling and retry mechanisms
- Duplicate prevention logic

### Security
- Database connection security
- API authentication (to be implemented)
- Message encryption in Pulsar (to be configured)

## Dependencies

### Core Framework
- FastAPI: Web framework
- SQLAlchemy: ORM and database toolkit
- Pydantic: Data validation
- Uvicorn: ASGI server

### Messaging
- pulsar-client: Apache Pulsar client

### Database
- psycopg2-binary: PostgreSQL adapter
- PostgreSQL: Primary database

### Development
- Poetry: Dependency management
- Docker: Containerization
- Docker Compose: Multi-service orchestration
