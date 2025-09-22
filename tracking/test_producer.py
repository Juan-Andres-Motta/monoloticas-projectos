import pulsar
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pulsar.schema import AvroSchema
from src.infrastructure.adapters.schemas import TrackingEventRecord

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
tracking_event_record = TrackingEventRecord(
    campaign_id="campaign123",
    event_type="click",
    timestamp=datetime.utcnow().isoformat() + "Z",
)


def main():
    logger.info("Starting test producer for tracking")
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    pulsar_topic = os.getenv(
        "PULSAR_TOPIC", "persistent://miso-1-2025/default/campaign-tracking-events"
    )
    logger.info(f"Connecting to Pulsar at {pulsar_service_url}, topic: {pulsar_topic}")
    if pulsar_token:
        client = pulsar.Client(
            pulsar_service_url, authentication=pulsar.AuthenticationToken(pulsar_token)
        )
    else:
        client = pulsar.Client(pulsar_service_url)
    producer = client.create_producer(
        pulsar_topic, schema=AvroSchema(TrackingEventRecord)
    )

    producer.send(tracking_event_record)
    logger.info(f"Tracking event sent to Pulsar topic '{pulsar_topic}'")

    producer.close()
    client.close()
    logger.info("Test producer finished")


if __name__ == "__main__":
    main()
