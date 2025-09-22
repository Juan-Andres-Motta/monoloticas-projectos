import pulsar
import os
import logging
from dotenv import load_dotenv
from pulsar.schema import AvroSchema
from src.infrastructure.adapters.schemas import FailTrackingEventRecord

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
fail_tracking_event_record = FailTrackingEventRecord(
    tracking_id="8",
)


def main():
    logger.info("Starting test producer for fail tracking")
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    pulsar_topic = os.getenv(
        "PULSAR_FAIL_TOPIC", "persistent://miso-1-2025/default/fail-tracking-events"
    )
    logger.info(f"Connecting to Pulsar at {pulsar_service_url}, topic: {pulsar_topic}")
    if pulsar_token:
        client = pulsar.Client(
            pulsar_service_url, authentication=pulsar.AuthenticationToken(pulsar_token)
        )
    else:
        client = pulsar.Client(pulsar_service_url)
    producer = client.create_producer(
        pulsar_topic, schema=AvroSchema(FailTrackingEventRecord)
    )

    producer.send(fail_tracking_event_record)
    logger.info(f"Fail tracking event sent to Pulsar topic '{pulsar_topic}'")

    producer.close()
    client.close()
    logger.info("Test producer finished")


if __name__ == "__main__":
    main()
