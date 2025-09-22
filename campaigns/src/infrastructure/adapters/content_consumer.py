import pulsar
import json
import asyncio
import logging
from pulsar.schema import AvroSchema
from src.application.handlers.register_content_handler import RegisterContentHandler
from src.application.commands.register_content_command import RegisterContentCommand
from src.domain.entities.content import Content
from .campaign_schemas import ContentRecord

logger = logging.getLogger(__name__)


class ContentConsumer:
    def __init__(
        self,
        handler: RegisterContentHandler,
        pulsar_service_url: str = "pulsar://localhost:6650",
        topic: str = "persistent://miso-1-2025/default/campaign-content-association",
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
        logger.info("Starting content association Pulsar consumer")
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
                f"Attempting to subscribe to topic: {self.topic} with subscription: content-association-subscriber"
            )
            self.consumer = await asyncio.to_thread(
                self.client.subscribe,
                self.topic,
                "content-association-subscriber",
                schema=AvroSchema(ContentRecord),
            )
            logger.info(
                f"Successfully subscribed to topic: {self.topic} with subscription: content-association-subscriber"
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
                    f"Content association consumer waiting for message on topic: {self.topic}"
                )
                msg = await asyncio.to_thread(self.consumer.receive)
                logger.info(
                    f"Received content association message from Pulsar on topic: {self.topic}"
                )
                record = msg.value()
                logger.info(
                    f"Processing content association record: {record.content_id} for campaign {record.campaign_id}"
                )
                data = {
                    "content_id": record.content_id,
                    "campaign_id": record.campaign_id,
                    "content_url": record.content_url,
                }
                content = Content(**data)
                command = RegisterContentCommand(content)
                await self.handler.handle(command)
                await asyncio.to_thread(self.consumer.acknowledge, msg)
                logger.info(
                    f"Message processed successfully for content association: {content.content_id}"
                )
            except pulsar.Interrupted:
                logger.info("Content association consumer interrupted, shutting down")
                break
            except Exception as e:
                logger.error(f"Error processing content association message: {e}")
                if msg:
                    await asyncio.to_thread(self.consumer.negative_acknowledge, msg)
                    logger.warning(
                        f"Negatively acknowledged message for content association"
                    )

    def stop(self):
        logger.info("Stopping Pulsar consumer")
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()
        logger.info("Pulsar consumer stopped")
