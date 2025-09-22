import pulsar
import json
import asyncio
import logging
from pulsar.schema import AvroSchema
from src.application.handlers.associate_partner_to_campaign_handler import (
    AssociatePartnerToCampaignHandler,
)
from src.application.commands.associate_partner_to_campaign_command import (
    AssociatePartnerToCampaignCommand,
)
from src.domain.entities.campaign_partner import CampaignPartner
from .campaign_schemas import CampaignPartnerAssociationRecord

logger = logging.getLogger(__name__)


class CampaignPartnerAssociationConsumer:
    def __init__(
        self,
        handler: AssociatePartnerToCampaignHandler,
        pulsar_service_url: str = "pulsar://localhost:6650",
        topic: str = "persistent://miso-1-2025/default/campaign-partner-association",
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
        logger.info("Starting campaign-partner association Pulsar consumer")
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
                f"Attempting to subscribe to topic: {self.topic} with subscription: campaign-partner-association-subscriber"
            )
            self.consumer = await asyncio.to_thread(
                self.client.subscribe,
                self.topic,
                "campaign-partner-association-subscriber",
                schema=AvroSchema(CampaignPartnerAssociationRecord),
            )
            logger.info(
                f"Successfully subscribed to topic: {self.topic} with subscription: campaign-partner-association-subscriber"
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
                    f"Campaign-partner association consumer waiting for message on topic: {self.topic}"
                )
                msg = await asyncio.to_thread(self.consumer.receive)
                logger.info(
                    f"Received campaign-partner association message from Pulsar on topic: {self.topic}"
                )
                record = msg.value()
                logger.info(
                    f"Processing campaign-partner association record: {record.campaign_id} - {record.partner_id}"
                )
                data = {
                    "campaign_id": record.campaign_id,
                    "partner_id": record.partner_id,
                }
                campaign_partner = CampaignPartner(**data)
                command = AssociatePartnerToCampaignCommand(campaign_partner)
                await self.handler.handle(command)
                await asyncio.to_thread(self.consumer.acknowledge, msg)
                logger.info(
                    f"Message processed successfully for campaign-partner association: {campaign_partner.campaign_id} - {campaign_partner.partner_id}"
                )
            except pulsar.Interrupted:
                logger.info(
                    "Campaign-partner association consumer interrupted, shutting down"
                )
                break
            except Exception as e:
                logger.error(
                    f"Error processing campaign-partner association message: {e}"
                )
                if msg:
                    await asyncio.to_thread(self.consumer.negative_acknowledge, msg)
                    logger.warning(
                        f"Negatively acknowledged message for campaign-partner association"
                    )

    def stop(self):
        logger.info("Stopping Pulsar consumer")
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()
        logger.info("Pulsar consumer stopped")
