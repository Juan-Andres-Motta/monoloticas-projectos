import pulsar
import logging
from pulsar.schema import AvroSchema
from .schemas import FailTrackingEventRecord

logger = logging.getLogger(__name__)


class PulsarFailTrackingPublisher:
    def __init__(
        self,
        pulsar_service_url: str,
        fail_tracking_topic: str,
        token: str = "",
    ):
        self.pulsar_service_url = pulsar_service_url
        self.fail_tracking_topic = fail_tracking_topic
        self.token = token
        self.client = None
        self.producer = None

    async def connect(self):
        logger.info(
            f"Connecting to Pulsar for fail tracking at {self.pulsar_service_url}"
        )
        if self.token:
            self.client = pulsar.Client(
                self.pulsar_service_url,
                authentication=pulsar.AuthenticationToken(self.token),
            )
        else:
            self.client = pulsar.Client(self.pulsar_service_url)
        self.producer = self.client.create_producer(
            self.fail_tracking_topic, schema=AvroSchema(FailTrackingEventRecord)
        )
        logger.info(
            f"Fail tracking producer created for topic: {self.fail_tracking_topic}"
        )

    async def publish_fail_tracking_event(self, tracking_id: str) -> None:
        record = FailTrackingEventRecord(tracking_id=tracking_id)
        self.producer.send(record)
        logger.info(f"Fail tracking event sent for tracking_id: {tracking_id}")

    async def disconnect(self):
        if self.producer:
            self.producer.close()
        if self.client:
            self.client.close()
        logger.info("Fail tracking producer disconnected")
