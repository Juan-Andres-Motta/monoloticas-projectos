# Payments Service

A service that consumes payment request events from Apache Pulsar and stores payment details in PostgreSQL, following hexagonal architecture and CQRS principles.

## Architecture

- **Hexagonal Architecture**: Domain logic isolated from external concerns.
- **CQRS**: Command-side implementation for handling payment request events.

## Setup

1. Install dependencies:
   ```bash
   poetry install --no-root
   ```

2. Copy `.env.example` to `.env` and configure:
   - `DATABASE_URL`: PostgreSQL connection string.
   - `PULSAR_SERVICE_URL`: Pulsar service URL.
   - `PULSAR_TOKEN`: Pulsar authentication token.
   - `PULSAR_TOPIC`: Topic for payment request events.

3. Set up PostgreSQL database.

4. Ensure Apache Pulsar is running.

## Running the Service

```bash
python main.py
```

The service will start consuming messages from the `payments-request` topic.

## Testing

Run the test producer to send a sample payment request event:

```bash
python test_producer.py
```

Check the database to verify the payment was stored.

## Event Format

The service expects Avro-encoded events with the following schema:

```json
{
  "amount": 100.0,
  "currency": "USD",
  "payment_method": "credit_card",
  "account_details": {"key": "value"},
  "user_id": "user123"
}