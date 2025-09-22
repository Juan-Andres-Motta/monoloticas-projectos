import pulsar
import asyncio
import logging
from pulsar.schema import AvroSchema
from src.application.handlers.register_tracking_event_handler import (
    RegisterTrackingEventHandler,
)
from src.application.commands.register_tracking_event_command import (
    RegisterTrackingEventCommand,
)
from src.domain.entities.tracking_event import TrackingEvent
from .schemas import TrackingEventRecord

logger = logging.getLogger(__name__)


class PulsarConsumer:
    def __init__(
        self,
        handler: RegisterTrackingEventHandler,
        pulsar_service_url: str = "pulsar://localhost:6650",
        topic: str = "persistent://miso-1-2025/default/campaign-tracking-events",
        token: str = "",
    ):
        self.handler = handler
        self.pulsar_service_url = pulsar_service_url
        self.topic = topic
        self.token = token
        self.client = None
        self.consumer = None

    async def start(self):
        logger.info(f"Connecting to Pulsar at {self.pulsar_service_url}")
        if self.token:
            self.client = pulsar.Client(
                self.pulsar_service_url,
                authentication=pulsar.AuthenticationToken(self.token),
            )
        else:
            self.client = pulsar.Client(self.pulsar_service_url)
        self.consumer = await asyncio.to_thread(
            self.client.subscribe,
            self.topic,
            "tracking-subscriber",
            schema=AvroSchema(TrackingEventRecord),
        )
        logger.info(f"Subscribed to topic: {self.topic}")

        while True:
            if asyncio.current_task().cancelled():
                break
            msg = None
            try:
                logger.info(
                    f"PulsarConsumer waiting for message on topic: {self.topic}"
                )
                msg = await asyncio.to_thread(self.consumer.receive)
                logger.info("Received tracking event message from Pulsar")
                record = msg.value()
                from datetime import datetime

                data = {
                    "campaign_id": record.campaign_id,
                    "event_type": record.event_type,
                    "timestamp": datetime.fromisoformat(
                        record.timestamp.replace("Z", "+00:00")
                    ).replace(tzinfo=None),
                }
                tracking_event = TrackingEvent(**data)
                command = RegisterTrackingEventCommand(tracking_event)
                await self.handler.handle(command)
                self.consumer.acknowledge(msg)
                logger.info(
                    f"Message processed successfully for campaign: {tracking_event.campaign_id}"
                )
            except pulsar.Interrupted:
                logger.info("Consumer interrupted, shutting down")
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if msg:
                    self.consumer.negative_acknowledge(msg)

    def stop(self):
        logger.info("Stopping Pulsar consumer")
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()
        logger.info("Pulsar consumer stopped")
