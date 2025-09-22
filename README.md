# Campaign Management Microservices System

## Project Description

This is a microservices-based system designed for managing marketing campaigns, tracking evidence, calculating commissions, and processing payments. The architecture follows an event-driven approach using Apache Pulsar for inter-service communication, ensuring scalability and decoupling between services.

The system consists of five main services:
- **BFF (Backend for Frontend)**: Provides REST APIs for external clients and publishes events to initiate business processes.
- **Campaigns Service**: Manages campaign creation, partner registration, content association, and partner-campaign relationships.
- **Commissions Service**: Calculates and assigns commissions based on campaign activities and tracking events.
- **Payments Service**: Processes payment requests and maintains payment records.
- **Tracking Service**: Handles tracking of campaign evidence and events, including failure handling.

## Architecture Overview

### Architecture Pattern
- **Event-Driven Architecture**: Services communicate asynchronously through Apache Pulsar message broker.
- **Microservices**: Each service is independently deployable with its own database and responsibilities.
- **Domain-Driven Design (DDD)**: Each service follows DDD principles with clear domain entities, commands, handlers, and ports/adapters.

### Technologies Used
- **Programming Language**: Python 3.9+
- **Web Framework**: FastAPI (for BFF service)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Message Broker**: Apache Pulsar (DataStax Astra Streaming)
- **Containerization**: Docker & Docker Compose
- **Authentication**: JWT tokens
- **Serialization**: Avro schemas for event messages

### Service Architecture
Each microservice follows a layered architecture:
- **API Layer**: REST endpoints (BFF only) or event consumers
- **Application Layer**: Commands and handlers for business logic
- **Domain Layer**: Entities, value objects, and business rules
- **Infrastructure Layer**: Database repositories, external service adapters, and messaging

### Data Flow
1. BFF receives API requests and publishes events to Pulsar topics
2. Consumer services (Campaigns, Commissions, Payments, Tracking) listen to relevant topics
3. Services process events, update their databases, and may publish new events
4. Saga pattern is used for complex transactions spanning multiple services

### Databases
Each service maintains its own PostgreSQL database:
- `campaigns`: Campaign data, partners, content, associations
- `commissionsdb`: Commission calculations and saga logs
- `paymentsdb`: Payment records
- `trackingdb`: Tracking events and processed messages

## Configuration

### Environment Variables
The system uses environment variables for configuration. Each service has its own `.env.example` file with default values.

Key configuration includes:
- **Database URLs**: PostgreSQL connection strings for each service
- **Pulsar Configuration**: Service URL, authentication token, and topic names
- **JWT Settings**: For authentication (if implemented)

### Pulsar Topics
The system uses the following Pulsar topics for event communication:
- `campaigns-partner-registration`
- `campaign-creation`
- `campaign-partner-association`
- `campaign-content-association`
- `campaign-tracking-events`
- `assign-commission-to-partner`
- `payments-request`
- `fail-tracking-events`

## How to Run

### Prerequisites
- Docker Engine
- Docker Compose
- Git

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd monoliticas
   ```

2. **Configure environment** (optional):
   - Copy `.env.example` files to `.env` in each service directory if you need custom configuration
   - The default configuration should work for local development

3. **Build and run the services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the services**:
   - **BFF API**: http://localhost:8083
   - **Adminer (Database UI)**: http://localhost:8082
   - **Database Ports**:
     - Campaigns DB: localhost:5436
     - Commissions DB: localhost:5433
     - Payments DB: localhost:5434
     - Tracking DB: localhost:5435

### Development

Each service can be run individually for development:
1. Navigate to the service directory (e.g., `cd bff`)
2. Install dependencies: `poetry install`
3. Run the service: `poetry run python main.py`

For testing, each service includes test files and can be run with `poetry run pytest`.

### Stopping the System
```bash
docker-compose down
```

To remove volumes (including databases):
```bash
docker-compose down -v
```

## API Documentation

Once the BFF service is running, API documentation is available at:
- Swagger UI: http://localhost:8083/docs
- ReDoc: http://localhost:8083/redoc

## Monitoring and Debugging

- **Logs**: Each service outputs logs to stdout/stderr, visible in Docker Compose
- **Database Access**: Use Adminer at http://localhost:8082 to browse databases
- **Pulsar Monitoring**: Access DataStax Astra dashboard for message broker monitoring

## Contributing

1. Follow the established architecture patterns
2. Write tests for new functionality
3. Update documentation as needed
4. Ensure Docker builds work correctly

## License

[Add license information if applicable]