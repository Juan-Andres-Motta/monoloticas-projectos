import pulsar
import json
import asyncio
import logging
from pulsar.schema import AvroSchema
from src.application.handlers.register_partner_handler import RegisterPartnerHandler
from src.application.commands.register_partner_command import RegisterPartnerCommand
from src.domain.entities.partner import Partner
from .schemas import PartnerRecord

logger = logging.getLogger(__name__)


class PulsarConsumer:
    def __init__(
        self,
        handler: RegisterPartnerHandler,
        pulsar_service_url: str = "pulsar://localhost:6650",
        topic: str = "persistent://miso-1-2025/default/campaigns-partner-registration",
        token: str = "",
        client=None,
    ):
        self.handler = handler
        self.pulsar_service_url = pulsar_service_url
        self.topic = topic
        self.token = token
        self.client = client
        self.consumer = None

    async def start(self):
        logger.info(f"Connecting to Pulsar at {self.pulsar_service_url}")
        if self.client is None:
            if self.token:
                self.client = pulsar.Client(
                    self.pulsar_service_url,
                    authentication=pulsar.AuthenticationToken(self.token),
                )
            else:
                self.client = pulsar.Client(self.pulsar_service_url)
        try:
            logger.info(
                f"Attempting to subscribe to topic: {self.topic} with subscription: partner-subscriber"
            )
            self.consumer = await asyncio.to_thread(
                self.client.subscribe,
                self.topic,
                "partner-subscriber",
                schema=AvroSchema(PartnerRecord),
            )
            logger.info(
                f"Successfully subscribed to topic: {self.topic} with subscription: partner-subscriber"
            )
        except Exception as e:
            logger.error(f"Failed to subscribe to topic {self.topic}: {e}")
            raise

        while True:
            if asyncio.current_task().cancelled():
                break
            msg = None
            try:
                logger.info(
                    f"Partner consumer waiting for message on topic: {self.topic}"
                )
                msg = await asyncio.to_thread(self.consumer.receive)
                logger.info(
                    f"Received partner registration message from Pulsar on topic: {self.topic}"
                )
                record = msg.value()
                logger.info(f"Processing partner record: {record.partner_id}")
                data = {
                    "partner_id": record.partner_id,
                    "partner_type": record.partner_type,
                    "acceptance_terms": {
                        "commission_type": record.acceptance_terms.commission_type,
                        "commission_rate": record.acceptance_terms.commission_rate,
                        "cookie_duration_days": record.acceptance_terms.cookie_duration_days,
                        "promotional_methods": record.acceptance_terms.promotional_methods,
                    },
                    "estimated_monthly_reach": record.estimated_monthly_reach,
                }
                partner = Partner(**data)
                command = RegisterPartnerCommand(partner)
                await self.handler.handle(command)
                self.consumer.acknowledge(msg)
                logger.info(
                    f"Message processed successfully for partner: {partner.partner_id}"
                )
            except pulsar.Interrupted:
                logger.info("Partner consumer interrupted, shutting down")
                break
            except Exception as e:
                logger.error(f"Error processing partner message: {e}")
                if msg:
                    self.consumer.negative_acknowledge(msg)
                    logger.warning(f"Negatively acknowledged message for partner")

    def stop(self):
        logger.info("Stopping Pulsar consumer")
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()
        logger.info("Pulsar consumer stopped")
