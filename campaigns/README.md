# Campaigns Service

A service that receives partner registration events from Apache Pulsar and stores them in PostgreSQL, following hexagonal architecture and CQRS principles.

## Architecture

- **Hexagonal Architecture**: Domain logic isolated from external concerns.
- **CQRS**: Command-side implementation for handling partner registration events.

## Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Copy `.env.example` to `.env` and configure:
   - `DATABASE_URL`: PostgreSQL connection string.
   - `PULSAR_SERVICE_URL`: Pulsar service URL (default: `pulsar://localhost:6650`, for Astra: `pulsar+ssl://pulsar-aws-useast2.streaming.datastax.com:6651`).
   - `PULSAR_TOKEN`: Pulsar authentication token (leave empty for no auth).
   - `PULSAR_TOPIC`: Topic name (default: `campaigns-partner-registration`, for Astra use persistent topic like `persistent://miso-1-2025/default/campaigns-partner-registration`).

3. Set up PostgreSQL database.

4. Ensure Apache Pulsar is running.

## Running the Service

```bash
python main.py
```

The service will start consuming messages from the `campaigns-partner-registration` topic, validating them against an Avro schema.

## Testing

Run the test producer to send a sample message:

```bash
python test_producer.py
```

Check the database to verify the record was inserted.