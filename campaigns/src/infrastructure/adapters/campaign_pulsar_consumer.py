import pulsar
import json
import asyncio
import logging
from pulsar.schema import AvroSchema
from src.application.handlers.register_campaign_handler import RegisterCampaignHandler
from src.application.commands.register_campaign_command import RegisterCampaignCommand
from src.domain.entities.campaign import Campaign
from .campaign_schemas import CampaignRecord

logger = logging.getLogger(__name__)


class CampaignPulsarConsumer:
    def __init__(
        self,
        handler: RegisterCampaignHandler,
        pulsar_service_url: str = "pulsar://localhost:6650",
        topic: str = "persistent://miso-1-2025/default/campaign-creation",
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
        logger.info("Starting campaign Pulsar consumer")
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
                f"Attempting to subscribe to topic: {self.topic} with subscription: campaign-subscriber"
            )
            self.consumer = await asyncio.to_thread(
                self.client.subscribe,
                self.topic,
                "campaign-subscriber",
                schema=AvroSchema(CampaignRecord),
            )
            logger.info(
                f"Successfully subscribed to topic: {self.topic} with subscription: campaign-subscriber"
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
                    f"Campaign consumer waiting for message on topic: {self.topic}"
                )
                msg = await asyncio.to_thread(self.consumer.receive)
                logger.info(
                    f"Received campaign creation message from Pulsar on topic: {self.topic}"
                )
                record = msg.value()
                logger.info(f"Processing campaign record: {record.campaign_id}")
                data = {"campaign_id": record.campaign_id, "name": record.name}
                campaign = Campaign(**data)
                command = RegisterCampaignCommand(campaign)
                await self.handler.handle(command)
                self.consumer.acknowledge(msg)
                logger.info(
                    f"Message processed successfully for campaign: {campaign.campaign_id}"
                )
            except pulsar.Interrupted:
                logger.info("Campaign consumer interrupted, shutting down")
                break
            except Exception as e:
                logger.error(f"Error processing campaign message: {e}")
                if msg:
                    self.consumer.negative_acknowledge(msg)
                    logger.warning(f"Negatively acknowledged message for campaign")

    def stop(self):
        logger.info("Stopping Pulsar consumer")
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()
        logger.info("Pulsar consumer stopped")
