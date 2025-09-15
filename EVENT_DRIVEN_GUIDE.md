# Event-Driven Microservices with Apache Pulsar & Avro

This document explains how to implement a fully event-driven microservices architecture using Apache Pulsar with Avro schemas instead of traditional HTTP endpoints.

## 🎯 Architecture Overview

Instead of microservices calling each other via HTTP APIs, they communicate through **command events** and **domain events** using Pulsar topics with Avro schemas.

### Traditional vs Event-Driven

**Traditional HTTP-based:**
```
Client → HTTP POST → Campaign Service → HTTP POST → Tracking Service → HTTP POST → Commission Service
```

**Event-Driven:**
```
Client → Command Event → Campaign Service → Domain Event → Other Services
                     ↓
              Automatic Event Chain:
              Tracking Events → Commission Calculation → Payment Processing
```

## 📋 Event Types

### Command Events (Trigger Operations)
These events trigger operations in specific microservices:

- `campaign.create.command.v1` → Campaign Service
- `campaign.add_video.command.v1` → Campaign Service  
- `tracking.create_event.command.v1` → Tracking Service
- `commission.calculate.command.v1` → Commission Service
- `payment.process.command.v1` → Payment Service

### Domain Events (Notify Completion)
These events notify when operations complete:

- `campaign.created.v1` → Published by Campaign Service
- `video.added.v1` → Published by Campaign Service
- `tracking_event.created.v1` → Published by Tracking Service
- `commission.calculated.v1` → Published by Commission Service
- `payment.processed.v1` → Published by Payment Service

## 🏗️ Pulsar Topics Structure

```
# Command Topics (each service listens to one)
persistent://miso-1-2025/default/campaign-commands
persistent://miso-1-2025/default/tracking-commands
persistent://miso-1-2025/default/commission-commands
persistent://miso-1-2025/default/payment-commands

# Event Topics (services publish domain events)
persistent://miso-1-2025/default/campaign-events
persistent://miso-1-2025/default/tracking-events
persistent://miso-1-2025/default/commission-events
persistent://miso-1-2025/default/payment-events
```

## 📦 Avro Schema Benefits

1. **Type Safety**: Compile-time validation of message structure
2. **Schema Evolution**: Backward/forward compatibility
3. **Compact Serialization**: Smaller message sizes than JSON
4. **Documentation**: Self-documenting message formats
5. **Tooling**: Better IDE support and debugging

## 🚀 Implementation Guide

### 1. Install Dependencies

Add to each service's `pyproject.toml`:

```toml
[tool.poetry.dependencies]
pulsar-client = "^3.8.0"
fastavro = "^1.9.0"
```

### 2. Avro Schema Definition

Example schema for campaign creation command:

```python
class CreateCampaignCommandAvro(Record):
    # Command metadata
    command_id = String()
    command_type = String(default="campaign.create.command.v1")
    timestamp = Integer()  # Unix timestamp in milliseconds
    correlation_id = String()  # For tracking across services
    
    # Campaign data
    campaign_id = String()
    user_id = String()
    name = String()
    description = String(default="")
```

### 3. Event Publisher

```python
from messaging.avro_publisher import avro_pulsar_publisher

# Send command to Campaign Service
correlation_id = await avro_pulsar_publisher.send_create_campaign_command(
    campaign_id=uuid4(),
    user_id="user123",
    name="My Campaign",
    description="Campaign description"
)
```

### 4. Event Consumer

```python
from messaging.avro_consumer import CampaignServiceConsumer

# Set up consumer
consumer = CampaignServiceConsumer()
await consumer.start()

# Register handlers
consumer.register_handlers(
    create_campaign_handler=handle_create_campaign_command,
    add_video_handler=handle_add_video_command
)

# Start consuming
await consumer.start_consuming()
```

### 5. Command Handler

```python
async def handle_create_campaign_command(command_data, message_id):
    # Extract data from Avro record
    campaign_id = UUID(command_data.campaign_id)
    user_id = command_data.user_id
    name = command_data.name
    
    # Execute business logic
    campaign = Campaign.create(campaign_id, user_id, name)
    await repository.save(campaign)
    
    # Publish domain event
    await publisher.publish_domain_event(campaign.events[0], "campaign")
```

## 🔄 Event Flow Examples

### Example 1: Create Campaign with Video

```
1. Client sends: campaign.create.command.v1
   ↓
2. Campaign Service processes command
   ↓
3. Campaign Service publishes: campaign.created.v1
   ↓
4. Client sends: campaign.add_video.command.v1
   ↓
5. Campaign Service processes command  
   ↓
6. Campaign Service publishes: video.added.v1
```

### Example 2: Tracking Event Chain

```
1. Client sends: tracking.create_event.command.v1
   ↓
2. Tracking Service processes command
   ↓
3. Tracking Service publishes: tracking_event.created.v1
   ↓
4. Tracking Service auto-sends: commission.calculate.command.v1
   ↓
5. Commission Service calculates commission
   ↓
6. Commission Service publishes: commission.calculated.v1
```

## 🛠️ Service Modes

Each service can run in different modes:

### HTTP Mode (Traditional)
```bash
export CAMPAIGN_SERVICE_MODE=http
python main_event_driven.py
```

### Event-Driven Mode (Pure Events)
```bash
export CAMPAIGN_SERVICE_MODE=event
python main_event_driven.py
```

### Hybrid Mode (Both HTTP + Events)
```bash
export CAMPAIGN_SERVICE_MODE=hybrid
python main_event_driven.py
```

## 🔧 Configuration

### Environment Variables

```bash
# Service Mode
CAMPAIGN_SERVICE_MODE=event  # http | event | hybrid

# Pulsar Configuration
PULSAR_SERVICE_URL=pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651
PULSAR_TOKEN=your_datastax_token
PULSAR_TENANT=miso-1-2025
PULSAR_NAMESPACE=default
```

### Docker Compose Integration

```yaml
services:
  campaign-service:
    build: ./campaign
    environment:
      - CAMPAIGN_SERVICE_MODE=event
      - PULSAR_TOKEN=${PULSAR_TOKEN}
    depends_on:
      - campaign-db
```

## 🧪 Testing Event-Driven Services

### 1. Unit Testing Commands

```python
# Test command handler
async def test_create_campaign_handler():
    command_data = CreateCampaignCommandAvro(
        command_id=str(uuid4()),
        campaign_id=str(uuid4()),
        user_id="test-user",
        name="Test Campaign"
    )
    
    result = await handler.handle_create_campaign_command(command_data, "msg-id")
    assert result["success"] == True
```

### 2. Integration Testing

```python
# Send command and verify processing
correlation_id = await publisher.send_create_campaign_command(
    campaign_id=test_id,
    user_id="test-user",
    name="Integration Test"
)

# Wait for processing
await asyncio.sleep(2)

# Verify result in database
campaign = await repository.get_by_id(test_id)
assert campaign is not None
```

### 3. End-to-End Testing

```python
# Test complete workflow
async def test_campaign_workflow():
    # 1. Create campaign
    correlation_id_1 = await send_create_campaign_command(...)
    
    # 2. Add video URL
    correlation_id_2 = await send_add_video_command(...)
    
    # 3. Create tracking event
    correlation_id_3 = await send_tracking_event_command(...)
    
    # 4. Verify commission calculation
    # Check domain events were published correctly
```

## 📊 Monitoring & Debugging

### 1. Correlation IDs

Every command includes a correlation ID for tracking:

```python
# All related events share the same correlation ID
correlation_id = "workflow-12345"

await publisher.send_create_campaign_command(..., correlation_id=correlation_id)
await publisher.send_add_video_command(..., correlation_id=correlation_id)
```

### 2. Event Tracing

```python
# Log events with correlation ID
print(f"📤 Command sent: {command_type}")
print(f"🔗 Correlation ID: {correlation_id}")
print(f"⏰ Timestamp: {timestamp}")
```

### 3. Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "event-driven",
        "pulsar_connected": await check_pulsar_connection(),
        "topics_subscribed": list(consumer.subscriptions.keys())
    }
```

## 🔒 Error Handling

### 1. Command Processing Errors

```python
async def handle_command(command_data, message_id):
    try:
        # Process command
        result = await process_business_logic(command_data)
        
        # Acknowledge success
        consumer.acknowledge(msg)
        return {"success": True, "result": result}
        
    except ValidationError as e:
        # Don't retry validation errors
        consumer.acknowledge(msg)
        await publish_error_event(command_data, str(e))
        
    except Exception as e:
        # Retry transient errors
        consumer.negative_acknowledge(msg)
        raise
```

### 2. Dead Letter Topics

Configure dead letter topics for failed messages:

```python
consumer = client.subscribe(
    topic,
    subscription,
    schema=schema,
    dead_letter_policy=pulsar.ConsumerDeadLetterPolicy(
        max_redeliver_count=3,
        dead_letter_topic="campaign-commands-dlq"
    )
)
```

## 🚀 Benefits of Event-Driven Architecture

1. **Loose Coupling**: Services don't need to know about each other
2. **Scalability**: Easy to scale individual services
3. **Resilience**: Services continue working if others are down
4. **Flexibility**: Easy to add new services to event streams
5. **Auditability**: Complete event history for debugging
6. **Performance**: Asynchronous processing improves response times

## 📚 Additional Resources

- [Apache Pulsar Documentation](https://pulsar.apache.org/docs/)
- [Avro Schema Evolution](https://avro.apache.org/docs/current/spec.html#Schema+Evolution+Rules)
- [DataStax Astra Streaming](https://docs.datastax.com/en/streaming/astra-streaming/)
- [Event-Driven Architecture Patterns](https://microservices.io/patterns/data/event-driven-architecture.html)

## 🎯 Next Steps

1. **Migrate Existing Services**: Convert HTTP endpoints to event handlers
2. **Add Monitoring**: Implement event tracing and metrics
3. **Schema Registry**: Set up centralized schema management
4. **Testing**: Build comprehensive integration tests
5. **Documentation**: Document event flows and schemas
