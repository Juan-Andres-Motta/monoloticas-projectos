import uvicorn
import os
import logging
from dotenv import load_dotenv
from src.infrastructure.adapters.pulsar_producer import PulsarEventPublisher
from src.application.handlers.publish_partner_handler import PublishPartnerHandler
from src.api import app, set_publisher

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def startup_event():
    global handler, publisher
    logger.info("Starting BFF service")
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    partner_topic = os.getenv(
        "PULSAR_PARTNER_TOPIC",
        "persistent://miso-1-2025/default/campaigns-partner-registration",
    )
    campaign_topic = os.getenv(
        "PULSAR_CAMPAIGN_TOPIC",
        "persistent://miso-1-2025/default/campaign-creation",
    )
    association_topic = os.getenv(
        "PULSAR_ASSOCIATION_TOPIC",
        "persistent://miso-1-2025/default/campaign-partner-association",
    )
    content_topic = os.getenv(
        "PULSAR_CONTENT_TOPIC",
        "persistent://miso-1-2025/default/campaign-content-association",
    )
    tracking_topic = os.getenv(
        "PULSAR_TRACKING_TOPIC",
        "persistent://miso-1-2025/default/campaign-tracking-events",
    )
    fail_topic = os.getenv(
        "PULSAR_FAIL_TOPIC",
        "persistent://miso-1-2025/default/fail-tracking-events",
    )
    payment_topic = os.getenv(
        "PULSAR_PAYMENT_TOPIC",
        "persistent://miso-1-2025/default/payments-request",
    )

    publisher = PulsarEventPublisher(
        pulsar_service_url,
        partner_topic,
        campaign_topic,
        association_topic,
        content_topic,
        tracking_topic,
        fail_topic,
        payment_topic,
        pulsar_token,
    )
    await publisher.connect()

    set_publisher(publisher)
    logger.info("BFF service started")


async def shutdown_event():
    logger.info("Shutting down BFF service")
    await publisher.disconnect()
    logger.info("BFF service shutdown complete")


app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
