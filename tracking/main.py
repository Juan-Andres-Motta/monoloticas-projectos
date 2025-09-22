import asyncio
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
from src.infrastructure.adapters.postgres_tracking_event_repository import (
    PostgresTrackingEventRepository,
)
from src.application.handlers.register_tracking_event_handler import (
    RegisterTrackingEventHandler,
)
from src.application.handlers.fail_tracking_event_handler import (
    FailTrackingEventHandler,
)
from src.infrastructure.adapters.pulsar_consumer import PulsarConsumer
from src.infrastructure.adapters.fail_tracking_event_consumer import (
    FailTrackingEventConsumer,
)
from src.infrastructure.adapters.pulsar_producer import PulsarCommissionPublisher
from src.infrastructure.adapters.models import metadata

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting tracking service")

    # DB setup
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://juan:@localhost/trackingdb"
    )
    logger.info(f"Connecting to database: {database_url}")
    engine = create_async_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    logger.info("Database tables created/verified")

    # Dependency injection
    sessionmaker_instance = async_sessionmaker(engine, expire_on_commit=False)
    repo = PostgresTrackingEventRepository(sessionmaker_instance)
    pulsar_service_url = os.getenv("PULSAR_SERVICE_URL", "pulsar://localhost:6650")
    pulsar_token = os.getenv("PULSAR_TOKEN", "")
    pulsar_topic = os.getenv(
        "PULSAR_TOPIC", "persistent://miso-1-2025/default/campaign-tracking-events"
    )
    commission_topic = os.getenv(
        "PULSAR_COMMISSION_TOPIC",
        "persistent://miso-1-2025/default/assign-commission-to-partner",
    )
    commission_publisher = PulsarCommissionPublisher(
        pulsar_service_url, commission_topic, pulsar_token
    )
    await commission_publisher.connect()

    handler = RegisterTrackingEventHandler(repo, commission_publisher)
    consumer = PulsarConsumer(handler, pulsar_service_url, pulsar_topic, pulsar_token)
    logger.info(
        f"Starting Pulsar consumer on {pulsar_service_url}, topic: {pulsar_topic}"
    )

    print("Creating fail handler and consumer")
    fail_handler = FailTrackingEventHandler(repo)
    fail_topic = os.getenv(
        "PULSAR_FAIL_TOPIC",
        "persistent://miso-1-2025/default/fail-tracking-events-partition-0",
    )
    fail_consumer = FailTrackingEventConsumer(
        fail_handler, pulsar_service_url, fail_topic, pulsar_token
    )
    print(f"Fail consumer created: {fail_consumer}")
    print("Fail consumer created")
    logger.info(
        f"Starting fail tracking event consumer on {pulsar_service_url}, topic: {fail_topic}"
    )

    # Start consumers
    consumer_task = asyncio.create_task(consumer.start())
    fail_consumer_task = asyncio.create_task(fail_consumer.start())
    try:
        await asyncio.gather(consumer_task, fail_consumer_task)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        consumer_task.cancel()
        fail_consumer_task.cancel()
        try:
            await asyncio.gather(
                consumer_task, fail_consumer_task, return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        consumer.stop()
        fail_consumer.stop()
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("Disposing database engine")
        await engine.dispose()
        logger.info("Service shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
