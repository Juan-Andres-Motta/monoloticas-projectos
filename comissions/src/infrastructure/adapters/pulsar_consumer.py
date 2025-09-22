import pulsar
import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select
from pulsar.schema import AvroSchema
from src.application.handlers.register_commission_handler import (
    RegisterCommissionHandler,
)
from src.application.commands.register_commission_command import (
    RegisterCommissionCommand,
)
from src.domain.entities.commission import Commission
from .schemas import CommissionRecord
from .models import campaign_partners_table
from .pulsar_fail_tracking_publisher import PulsarFailTrackingPublisher

logger = logging.getLogger(__name__)


class PulsarConsumer:
    def __init__(
        self,
        handler: RegisterCommissionHandler,
        fail_tracking_publisher: PulsarFailTrackingPublisher,
        campaigns_db_url: str,
        pulsar_service_url: str = "pulsar://localhost:6650",
        topic: str = "persistent://miso-1-2025/default/assign-commission-to-partner",
        token: str = "",
    ):
        self.handler = handler
        self.fail_tracking_publisher = fail_tracking_publisher
        self.campaigns_db_url = campaigns_db_url
        self.pulsar_service_url = pulsar_service_url
        self.topic = topic
        self.token = token
        self.client = None
        self.consumer = None
        self.campaigns_engine = None
        self.campaigns_session = None

    async def connect_campaigns_db(self):
        logger.info(f"Connecting to campaigns DB at {self.campaigns_db_url}")
        self.campaigns_engine = create_async_engine(self.campaigns_db_url)
        self.campaigns_session = AsyncSession(self.campaigns_engine)
        logger.info("Connected to campaigns DB")

    async def start(self):
        await self.connect_campaigns_db()
        await self.fail_tracking_publisher.connect()
        logger.info(f"Connecting to Pulsar at {self.pulsar_service_url}")
        if self.token:
            self.client = pulsar.Client(
                self.pulsar_service_url,
                authentication=pulsar.AuthenticationToken(self.token),
            )
        else:
            self.client = pulsar.Client(self.pulsar_service_url)
        self.consumer = self.client.subscribe(
            self.topic, "commission-subscriber", schema=AvroSchema(CommissionRecord)
        )
        logger.info(f"Subscribed to topic: {self.topic}")

        while True:
            if asyncio.current_task().cancelled():
                break
            msg = None
            try:
                msg = self.consumer.receive()
                logger.info("Received commission message from Pulsar")
                record = msg.value()
                # Query campaigns DB for partner_id
                campaign_id = record.campaign_id
                stmt = select(campaign_partners_table.c.partner_id).where(
                    campaign_partners_table.c.campaign_id == campaign_id
                )
                result = await self.campaigns_session.execute(stmt)
                partner_id = result.scalar_one_or_none()
                if not partner_id:
                    logger.error(f"No partner found for campaign {campaign_id}")
                    try:
                        await self.fail_tracking_publisher.publish_fail_tracking_event(
                            record.tracking_id
                        )
                        logger.info(
                            f"Fail tracking event sent for tracking_id: {record.tracking_id}"
                        )
                    except Exception as publish_error:
                        logger.error(
                            f"Failed to send fail tracking event: {publish_error}"
                        )
                    self.consumer.negative_acknowledge(msg)
                    continue
                data = {
                    "amount": record.amount,
                    "partner_id": partner_id,
                    "campaign_id": record.campaign_id,
                    "commission_type": record.commission_type,
                    "tracking_id": record.tracking_id,
                }
                commission = Commission(**data)
                command = RegisterCommissionCommand(commission)
                await self.handler.handle(command)
                self.consumer.acknowledge(msg)
                logger.info(
                    f"Message processed successfully for partner: {commission.partner_id}"
                )
            except pulsar.Interrupted:
                logger.info("Consumer interrupted, shutting down")
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if msg:
                    try:
                        await self.fail_tracking_publisher.publish_fail_tracking_event(
                            record.tracking_id
                        )
                        logger.info(
                            f"Fail tracking event sent for tracking_id: {record.tracking_id}"
                        )
                    except Exception as publish_error:
                        logger.error(
                            f"Failed to send fail tracking event: {publish_error}"
                        )
                    self.consumer.negative_acknowledge(msg)

    def stop(self):
        logger.info("Stopping Pulsar consumer")
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()
        asyncio.create_task(self.fail_tracking_publisher.disconnect())
        if self.campaigns_session:
            asyncio.create_task(self.campaigns_session.close())
        if self.campaigns_engine:
            asyncio.create_task(self.campaigns_engine.dispose())
        logger.info("Pulsar consumer stopped")
