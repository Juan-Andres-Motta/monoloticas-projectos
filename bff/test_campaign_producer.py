import pulsar
import os
import logging
from dotenv import load_dotenv
from pulsar.schema import AvroSchema
from src.infrastructure.adapters.campaign_schemas import CampaignRecord

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
campaign_record = CampaignRecord(campaign_id="campaign123", name="Summer Sale Campaign")


def main():
    logger.info("Starting test producer for campaigns")
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    pulsar_topic = os.getenv("PULSAR_CAMPAIGN_TOPIC", "campaign-creation")
    logger.info(f"Connecting to Pulsar at {pulsar_service_url}, topic: {pulsar_topic}")
    if pulsar_token:
        client = pulsar.Client(
            pulsar_service_url, authentication=pulsar.AuthenticationToken(pulsar_token)
        )
    else:
        client = pulsar.Client(pulsar_service_url)
    producer = client.create_producer(pulsar_topic, schema=AvroSchema(CampaignRecord))

    producer.send(campaign_record)
    logger.info(f"Campaign event sent to Pulsar topic '{pulsar_topic}'")

    producer.close()
    client.close()
    logger.info("Test producer finished")


if __name__ == "__main__":
    main()
