import pulsar
import asyncio
import logging
import json
from pulsar.schema import AvroSchema
from src.application.handlers.fail_tracking_event_handler import (
    FailTrackingEventHandler,
)
from src.application.commands.fail_tracking_event_command import (
    FailTrackingEventCommand,
)
from src.domain.ports.processed_message_repository import ProcessedMessageRepository
from .schemas import FailTrackingEventRecord

logger = logging.getLogger(__name__)


class FailTrackingEventConsumer:
    def __init__(
        self,
        handler: FailTrackingEventHandler,
        processed_message_repository: ProcessedMessageRepository,
        pulsar_service_url: str = "pulsar://localhost:6650",
        topic: str = "persistent://miso-1-2025/default/fail-tracking-events",
        token: str = "",
    ):
        self.handler = handler
        self.processed_message_repository = processed_message_repository
        self.pulsar_service_url = pulsar_service_url
        self.topic = topic
        self.token = token
        self.client = None
        self.consumer = None

    async def start(self):
        print("Starting FailTrackingEventConsumer")
        logger.info(f"Starting FailTrackingEventConsumer")
        logger.info(f"Connecting to Pulsar at {self.pulsar_service_url}")
        try:
            if self.token:
                self.client = pulsar.Client(
                    self.pulsar_service_url,
                    authentication=pulsar.AuthenticationToken(self.token),
                )
            else:
                self.client = pulsar.Client(self.pulsar_service_url)
            logger.info("Pulsar client created")
            self.consumer = await asyncio.to_thread(
                self.client.subscribe,
                self.topic,
                "fail-tracking-consumer-debug2",
                schema=AvroSchema(FailTrackingEventRecord),
                initial_position=pulsar.InitialPosition.Earliest,
            )
            logger.info(f"Subscribed to topic: {self.topic}")
        except Exception as e:
            logger.error(f"Failed to start FailTrackingEventConsumer: {e}")
            raise

        while True:
            if asyncio.current_task().cancelled():
                break
            msg = None
            try:
                msg = await asyncio.to_thread(self.consumer.receive)
                logger.info("Received fail tracking event message from Pulsar")
                message_id = str(msg.message_id())
                if await self.processed_message_repository.is_processed(message_id):
                    logger.info(f"Message {message_id} already processed, skipping")
                    self.consumer.acknowledge(msg)
                    continue
                record = msg.value()
                tracking_id_str = record.tracking_id
                logger.info(f"Record received: tracking_id={tracking_id_str}")
                command = FailTrackingEventCommand(tracking_id=int(tracking_id_str))
                logger.info(f"Created command for tracking_id: {command.tracking_id}")
                await self.handler.handle(command)
                await self.processed_message_repository.mark_processed(message_id)
                self.consumer.acknowledge(msg)
                logger.info(
                    f"Fail tracking event processed successfully for tracking_id: {tracking_id_str}"
                )
            except pulsar.Interrupted:
                logger.info("Consumer interrupted, shutting down")
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if msg:
                    self.consumer.negative_acknowledge(msg)

    def stop(self):
        logger.info("Stopping fail tracking event consumer")
        if self.consumer:
            self.consumer.close()
        if self.client:
            self.client.close()
        logger.info("Fail tracking event consumer stopped")
