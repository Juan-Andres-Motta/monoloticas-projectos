import asyncio
import os
import logging
import pulsar
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv
from src.infrastructure.adapters.postgres_partner_repository import (
    PostgresPartnerRepository,
)
from src.application.handlers.register_partner_handler import RegisterPartnerHandler
from src.infrastructure.adapters.postgres_campaign_repository import (
    PostgresCampaignRepository,
)
from src.application.handlers.register_campaign_handler import RegisterCampaignHandler
from src.infrastructure.adapters.postgres_campaign_partner_repository import (
    PostgresCampaignPartnerRepository,
)
from src.application.handlers.associate_partner_to_campaign_handler import (
    AssociatePartnerToCampaignHandler,
)
from src.infrastructure.adapters.postgres_content_repository import (
    PostgresContentRepository,
)
from src.application.handlers.register_content_handler import RegisterContentHandler
from src.infrastructure.adapters.pulsar_consumer import PulsarConsumer
from src.infrastructure.adapters.campaign_pulsar_consumer import CampaignPulsarConsumer
from src.infrastructure.adapters.campaign_partner_association_consumer import (
    CampaignPartnerAssociationConsumer,
)
from src.infrastructure.adapters.content_consumer import ContentConsumer
from src.infrastructure.adapters.models import metadata

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting campaigns service")

    # DB setup
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://user:password@localhost/campaigns"
    )
    logger.info(f"Connecting to database: {database_url}")
    engine = create_async_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    logger.info("Database tables created/verified")

    # Dependency injection
    session_partner = AsyncSession(engine)
    session_campaign = AsyncSession(engine)
    session_campaign_partner = AsyncSession(engine)
    session_content = AsyncSession(engine)
    partner_repo = PostgresPartnerRepository(session_partner)
    partner_handler = RegisterPartnerHandler(partner_repo)
    campaign_repo = PostgresCampaignRepository(session_campaign)
    campaign_handler = RegisterCampaignHandler(campaign_repo)
    campaign_partner_repo = PostgresCampaignPartnerRepository(session_campaign_partner)
    campaign_partner_handler = AssociatePartnerToCampaignHandler(campaign_partner_repo)
    content_repo = PostgresContentRepository(session_content)
    content_handler = RegisterContentHandler(content_repo)
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
    # Create consumers with separate clients
    partner_consumer = PulsarConsumer(
        partner_handler, pulsar_service_url, partner_topic, pulsar_token
    )
    campaign_consumer = CampaignPulsarConsumer(
        campaign_handler, pulsar_service_url, campaign_topic, pulsar_token
    )
    association_consumer = CampaignPartnerAssociationConsumer(
        campaign_partner_handler, pulsar_service_url, association_topic, pulsar_token
    )
    content_consumer = ContentConsumer(
        content_handler, pulsar_service_url, content_topic, pulsar_token
    )
    logger.info(
        f"Starting Pulsar consumers on {pulsar_service_url}, partner topic: {partner_topic}, campaign topic: {campaign_topic}, association topic: {association_topic}, content topic: {content_topic}"
    )

    # Start consumers
    partner_task = asyncio.create_task(partner_consumer.start())
    campaign_task = asyncio.create_task(campaign_consumer.start())
    association_task = asyncio.create_task(association_consumer.start())
    content_task = asyncio.create_task(content_consumer.start())
    try:
        await asyncio.gather(
            partner_task, campaign_task, association_task, content_task
        )
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        partner_task.cancel()
        campaign_task.cancel()
        association_task.cancel()
        content_task.cancel()
        try:
            await asyncio.gather(
                partner_task,
                campaign_task,
                association_task,
                content_task,
                return_exceptions=True,
            )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        partner_consumer.stop()
        campaign_consumer.stop()
        association_consumer.stop()
        content_consumer.stop()
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Closing database sessions")
        await session_partner.close()
        await session_campaign.close()
        await session_campaign_partner.close()
        await session_content.close()
        await engine.dispose()
        logger.info("Service shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
