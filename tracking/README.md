# Tracking Service

A service that consumes tracking events from Apache Pulsar and stores campaign tracking data in PostgreSQL, following hexagonal architecture and CQRS principles.

## Architecture

- **Hexagonal Architecture**: Domain logic isolated from external concerns.
- **CQRS**: Command-side implementation for handling tracking events.

## Setup

1. Install dependencies:
   ```bash
   poetry install --no-root
   ```

2. Copy `.env.example` to `.env` and configure:
   - `DATABASE_URL`: PostgreSQL connection string.
   - `PULSAR_SERVICE_URL`: Pulsar service URL.
   - `PULSAR_TOKEN`: Pulsar authentication token.
   - `PULSAR_TOPIC`: Topic for tracking events.

3. Set up PostgreSQL database.

4. Ensure Apache Pulsar is running.

## Running the Service

```bash
python main.py
```

The service will start consuming messages from the `campaign-tracking-events` topic.

## Testing

Run the test producer to send a sample tracking event:

```bash
python test_producer.py
```

Check the database to verify the tracking event was stored.

## Event Format

The service expects Avro-encoded events with the following schema:

```json
{
  "campaign_id": "campaign123",
  "event_type": "click",
  "timestamp": "2023-01-01T00:00:00Z"
}