# Commissions Service

A service that consumes commission events from Apache Pulsar and stores commission details in PostgreSQL, associating them with users and campaigns, following hexagonal architecture and CQRS principles.

## Architecture

- **Hexagonal Architecture**: Domain logic isolated from external concerns.
- **CQRS**: Command-side implementation for handling commission events.

## Setup

1. Install dependencies:
   ```bash
   poetry install --no-root
   ```

2. Copy `.env.example` to `.env` and configure:
   - `DATABASE_URL`: PostgreSQL connection string.
   - `PULSAR_SERVICE_URL`: Pulsar service URL.
   - `PULSAR_TOKEN`: Pulsar authentication token.
   - `PULSAR_TOPIC`: Topic for commission events.

3. Set up PostgreSQL database.

4. Ensure Apache Pulsar is running.

## Running the Service

```bash
python main.py
```

The service will start consuming messages from the `assign-commission-to-partner` topic.

## Testing

Run the test producer to send a sample commission event:

```bash
python test_producer.py
```

Check the database to verify the commission was stored.

## Event Format

The service expects Avro-encoded events with the following schema:

```json
{
  "amount": 50.0,
  "partner_id": "partner123",
  "campaign_id": "campaign456",
  "commission_type": "CPA"
}