import pulsar
import os
import logging
from dotenv import load_dotenv
from pulsar.schema import AvroSchema
from src.infrastructure.adapters.schemas import PaymentRecord

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
import json

account_details = {"bank": "example_bank", "account_number": "123456789"}
payment_record = PaymentRecord(
    amount=100.0,
    currency="USD",
    payment_method="credit_card",
    account_details=json.dumps(account_details),
    user_id="user123",
)


def main():
    logger.info("Starting test producer for payments")
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    pulsar_topic = os.getenv(
        "PULSAR_TOPIC", "persistent://miso-1-2025/default/payments-request"
    )
    logger.info(f"Connecting to Pulsar at {pulsar_service_url}, topic: {pulsar_topic}")
    if pulsar_token:
        client = pulsar.Client(
            pulsar_service_url, authentication=pulsar.AuthenticationToken(pulsar_token)
        )
    else:
        client = pulsar.Client(pulsar_service_url)
    producer = client.create_producer(pulsar_topic, schema=AvroSchema(PaymentRecord))

    producer.send(payment_record)
    logger.info(f"Payment request sent to Pulsar topic '{pulsar_topic}'")

    producer.close()
    client.close()
    logger.info("Test producer finished")


if __name__ == "__main__":
    main()
