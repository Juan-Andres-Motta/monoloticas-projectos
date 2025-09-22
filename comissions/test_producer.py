import pulsar
import os
import logging
from dotenv import load_dotenv
from pulsar.schema import AvroSchema
from src.infrastructure.adapters.schemas import CommissionRecord

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
commission_record = CommissionRecord(
    amount=50.0,
    partner_id="partner123",
    campaign_id="campaign456",
    commission_type="CPA",
)


def main():
    logger.info("Starting test producer for commissions")
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    pulsar_topic = os.getenv(
        "PULSAR_TOPIC", "persistent://miso-1-2025/default/assign-commission-to-partner"
    )
    logger.info(f"Connecting to Pulsar at {pulsar_service_url}, topic: {pulsar_topic}")
    if pulsar_token:
        client = pulsar.Client(
            pulsar_service_url, authentication=pulsar.AuthenticationToken(pulsar_token)
        )
    else:
        client = pulsar.Client(pulsar_service_url)
    producer = client.create_producer(pulsar_topic, schema=AvroSchema(CommissionRecord))

    producer.send(commission_record)
    logger.info(f"Commission event sent to Pulsar topic '{pulsar_topic}'")

    producer.close()
    client.close()
    logger.info("Test producer finished")


if __name__ == "__main__":
    main()
