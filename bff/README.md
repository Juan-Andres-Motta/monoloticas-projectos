# Alpes Partners BFF (Backend for Frontend)

A microservice that acts as a Backend for Frontend for the Alpes Partners platform, handling campaign management, evidence submission, and payment processing through Apache Pulsar messaging.

## Features

- **JWT Authentication**: Extracts userId from JWT tokens for request context
- **Pulsar Integration**: Command/response pattern using Apache Pulsar (DataStax Astra Streaming)
- **Clean Architecture**: Follows DDD principles with clear separation of concerns
- **Comprehensive DTOs**: Type-safe data transfer objects with Pydantic validation
- **CQRS Pattern**: Commands and responses through message queues
- **Avro Ready**: Structured for future Avro schema evolution

## API Endpoints

### Campaign Management
- `POST /api/v1/campaigns/{campaignId}/accept` - Accept campaign enrollment
- `GET /api/v1/campaigns/health` - Campaign service health check

### Evidence Management
- `POST /api/v1/campaigns/{campaignId}/evidence` - Upload campaign evidence
- `GET /api/v1/campaigns/evidence/health` - Evidence service health check

### Payment Management
- `POST /api/v1/payments/request` - Request partner payment
- `GET /api/v1/payments/health` - Payment service health check

### System
- `GET /` - Root endpoint
- `GET /health` - Overall service health

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer    │    │ Application     │    │   Messaging    │
│                 │    │   Layer         │    │                 │
│ • Routers       │───▶│ • Commands      │───▶│ • Pulsar Pub    │
│ • Schemas       │    │ • Handlers      │    │ • Pulsar Sub    │
│ • JWT Auth      │    │ • DTOs          │    │ • Topics        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Message Topics

### Command Topics (BFF → Services)
- `persistent://miso-1-2025/default/bff-campaign-accept-v1`
- `persistent://miso-1-2025/default/bff-evidence-upload-v1`
- `persistent://miso-1-2025/default/bff-payment-request-v1`

### Response Topics (Services → BFF)
- `persistent://miso-1-2025/default/bff-campaign-accept-responses-v1`
- `persistent://miso-1-2025/default/bff-evidence-upload-responses-v1`
- `persistent://miso-1-2025/default/bff-payment-request-responses-v1`

## DTOs Structure

### Command DTOs
- **Campaign Commands**: `AcceptCampaignCommandDto`, `CampaignStatusUpdateCommandDto`
- **Evidence Commands**: `UploadEvidenceCommandDto`, `EvidenceUpdateCommandDto`
- **Payment Commands**: `RequestPaymentCommandDto`, `PaymentStatusUpdateCommandDto`

### Response DTOs
- **Campaign Responses**: `AcceptCampaignResponseDto`, `CampaignListResponseDto`
- **Error Responses**: `ErrorResponseDto`, `ValidationErrorDto`, `BusinessRuleErrorDto`

### Integration Event DTOs
- **Cross-Service Events**: `CampaignAcceptedEventDto`, `EvidenceUploadedEventDto`, `PaymentRequestedEventDto`
- **System Events**: `SystemAlertEventDto`, `ComplianceViolationEventDto`

### Common DTOs
- **Base Types**: `TimestampMixin`, `UserContextMixin`, `PaginationRequest`
- **Value Objects**: `MoneyDto`, `AddressDto`, `ContactDto`

## Environment Configuration

```bash
# Pulsar Configuration (DataStax Astra Streaming)
PULSAR_SERVICE_URL=pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651
PULSAR_TOKEN=YOUR_PULSAR_TOKEN
PULSAR_TENANT=miso-1-2025
PULSAR_NAMESPACE=default
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or using poetry
poetry install

# Run the service
python main.py

# Or using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8002
```

## JWT Token Format

The service expects JWT tokens with userId in one of these claims:
- `userId`
- `user_id`
- `sub`
- `id`

Example JWT payload:
```json
{
  "userId": "user_123",
  "email": "partner@example.com",
  "roles": ["PARTNER"],
  "exp": 1640995200
}
```

## Message Format

All commands follow this structure:
```json
{
  "command_id": "uuid",
  "command_type": "accept_campaign|upload_evidence|request_payment",
  "user_id": "extracted_from_jwt",
  "timestamp": "2025-01-15T10:30:00Z",
  "payload": { /* command-specific data */ },
  "schema_version": "v1"
}
```

## Development

### Adding New Commands

1. Create command DTO in `api/dtos/commands/`
2. Create response DTO in `api/dtos/responses/`
3. Add handler in `application/handlers/`
4. Create router in `api/routers/`
5. Update Pulsar config with new topics

### Testing

```bash
# Run with sample JWT
curl -X POST "http://localhost:8002/api/v1/campaigns/camp123/accept" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{"partner_id": "partner123", ...}'
```

## Integration

The BFF integrates with:
- **Campaign Service**: Handles campaign enrollment and management
- **Evidence Service**: Processes content evidence validation
- **Payment Service**: Manages partner payment processing
- **Tracking Service**: Receives performance and conversion data

## Future Enhancements

- **Avro Schema Evolution**: Migrate from JSON to Avro for better versioning
- **Response Handling**: Implement full request-reply pattern for synchronous responses
- **Caching**: Add Redis for response caching and session management
- **Rate Limiting**: Implement rate limiting per partner
- **Monitoring**: Add comprehensive metrics and tracing