import pulsar
import logging
from pulsar.schema import AvroSchema
from .schemas import CommissionRecord

logger = logging.getLogger(__name__)


class PulsarCommissionPublisher:
    def __init__(
        self,
        pulsar_service_url: str,
        commission_topic: str,
        token: str = "",
    ):
        self.pulsar_service_url = pulsar_service_url
        self.commission_topic = commission_topic
        self.token = token
        self.client = None
        self.producer = None

    async def connect(self):
        logger.info(
            f"Connecting to Pulsar for commissions at {self.pulsar_service_url}"
        )
        if self.token:
            self.client = pulsar.Client(
                self.pulsar_service_url,
                authentication=pulsar.AuthenticationToken(self.token),
            )
        else:
            self.client = pulsar.Client(self.pulsar_service_url)
        self.producer = self.client.create_producer(
            self.commission_topic, schema=AvroSchema(CommissionRecord)
        )
        logger.info(f"Commission producer created for topic: {self.commission_topic}")

    async def publish_commission_event(
        self, amount: float, campaign_id: str, commission_type: str, tracking_id: int
    ) -> None:
        record = CommissionRecord(
            amount=amount,
            campaign_id=campaign_id,
            commission_type=commission_type,
            tracking_id=str(tracking_id),
        )
        self.producer.send(record)
        logger.info(
            f"Commission event sent: {commission_type} for campaign {campaign_id} with tracking_id {tracking_id}"
        )

    async def disconnect(self):
        if self.producer:
            self.producer.close()
        if self.client:
            self.client.close()
        logger.info("Commission producer disconnected")
