import pulsar
import os
import logging
from dotenv import load_dotenv
from pulsar.schema import AvroSchema
from src.infrastructure.adapters.schemas import PartnerRecord, AcceptanceTermsRecord

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
acceptance_terms = AcceptanceTermsRecord(
    commission_type="CPA",
    commission_rate=15.0,
    cookie_duration_days=45,
    promotional_methods=["blog", "social_media", "video"],
)
partner_record = PartnerRecord(
    partner_id="partner_fashion_blogger_001",
    partner_type="CONTENT_CREATOR",
    acceptance_terms=acceptance_terms,
    estimated_monthly_reach=75000,
)


def main():
    logger.info("Starting test producer")
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    pulsar_topic = os.getenv(
        "PULSAR_TOPIC",
        "persistent://miso-1-2025/default/campaigns-partner-registration",
    )
    logger.info(f"Connecting to Pulsar at {pulsar_service_url}, topic: {pulsar_topic}")
    if pulsar_token:
        client = pulsar.Client(
            pulsar_service_url, authentication=pulsar.AuthenticationToken(pulsar_token)
        )
    else:
        client = pulsar.Client(pulsar_service_url)
    producer = client.create_producer(pulsar_topic, schema=AvroSchema(PartnerRecord))

    producer.send(partner_record)
    logger.info(f"Message sent to Pulsar topic '{pulsar_topic}'")

    producer.close()
    client.close()
    logger.info("Test producer finished")


if __name__ == "__main__":
    main()
