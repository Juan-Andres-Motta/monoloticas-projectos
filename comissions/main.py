import asyncio
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from dotenv import load_dotenv
from src.infrastructure.adapters.postgres_commission_repository import (
    PostgresCommissionRepository,
)
from src.application.handlers.register_commission_handler import (
    RegisterCommissionHandler,
)
from src.infrastructure.adapters.pulsar_consumer import PulsarConsumer
from src.infrastructure.adapters.pulsar_fail_tracking_publisher import (
    PulsarFailTrackingPublisher,
)
from src.infrastructure.adapters.models import metadata

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting commissions service")

    # DB setup
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://juan:@localhost/commissionsdb"
    )
    logger.info(f"Connecting to database: {database_url}")
    engine = create_async_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    logger.info("Database tables created/verified")

    # Dependency injection
    session = AsyncSession(engine)
    repo = PostgresCommissionRepository(session)
    handler = RegisterCommissionHandler(repo)
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    pulsar_topic = os.getenv(
        "PULSAR_TOPIC", "persistent://miso-1-2025/default/assign-commission-to-partner"
    )
    campaigns_db_url = os.getenv(
        "CAMPAIGNS_DATABASE_URL", "postgresql+asyncpg://juan:@localhost/campaignsdb"
    )
    fail_tracking_topic = os.getenv(
        "FAIL_TRACKING_TOPIC", "persistent://miso-1-2025/default/fail-tracking-events"
    )
    fail_tracking_publisher = PulsarFailTrackingPublisher(
        pulsar_service_url, fail_tracking_topic, pulsar_token
    )
    consumer = PulsarConsumer(
        handler,
        fail_tracking_publisher,
        campaigns_db_url,
        pulsar_service_url,
        pulsar_topic,
        pulsar_token,
    )
    logger.info(
        f"Starting Pulsar consumer on {pulsar_service_url}, topic: {pulsar_topic}"
    )

    # Start consumer
    consumer_task = asyncio.create_task(consumer.start())
    try:
        await consumer_task
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        consumer.stop()
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Closing database session")
        await session.close()
        await engine.dispose()
        logger.info("Service shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
