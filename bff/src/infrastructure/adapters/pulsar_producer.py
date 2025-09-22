import pulsar
import logging
from pulsar.schema import AvroSchema
from src.domain.entities.partner import Partner
from src.domain.ports.event_publisher import EventPublisher
from .schemas import PartnerRecord, AcceptanceTermsRecord, TrackingEventRecord
from .campaign_schemas import (
    CampaignRecord,
    CampaignPartnerAssociationRecord,
    ContentAssociationRecord,
    FailTrackingEventRecord,
)

logger = logging.getLogger(__name__)


class PulsarEventPublisher(EventPublisher):
    def __init__(
        self,
        pulsar_service_url: str,
        partner_topic: str,
        campaign_topic: str,
        association_topic: str,
        content_topic: str,
        tracking_topic: str,
        fail_topic: str,
        token: str = "",
    ):
        self.pulsar_service_url = pulsar_service_url
        self.partner_topic = partner_topic
        self.campaign_topic = campaign_topic
        self.association_topic = association_topic
        self.content_topic = content_topic
        self.tracking_topic = tracking_topic
        self.fail_topic = fail_topic
        self.token = token
        self.client = None
        self.partner_producer = None
        self.campaign_producer = None
        self.association_producer = None
        self.content_producer = None
        self.tracking_producer = None
        self.fail_producer = None

    async def connect(self):
        logger.info(f"Connecting to Pulsar at {self.pulsar_service_url}")
        if self.token:
            self.client = pulsar.Client(
                self.pulsar_service_url,
                authentication=pulsar.AuthenticationToken(self.token),
            )
        else:
            self.client = pulsar.Client(self.pulsar_service_url)
        self.partner_producer = self.client.create_producer(
            self.partner_topic, schema=AvroSchema(PartnerRecord)
        )
        self.campaign_producer = self.client.create_producer(
            self.campaign_topic, schema=AvroSchema(CampaignRecord)
        )
        self.association_producer = self.client.create_producer(
            self.association_topic, schema=AvroSchema(CampaignPartnerAssociationRecord)
        )
        self.content_producer = self.client.create_producer(
            self.content_topic, schema=AvroSchema(ContentAssociationRecord)
        )
        self.tracking_producer = self.client.create_producer(
            self.tracking_topic, schema=AvroSchema(TrackingEventRecord)
        )
        self.fail_producer = self.client.create_producer(
            self.fail_topic, schema=AvroSchema(FailTrackingEventRecord)
        )
        logger.info(
            f"Producers created for topics: {self.partner_topic}, {self.campaign_topic}, {self.association_topic}, {self.content_topic}, {self.tracking_topic}, {self.fail_topic}"
        )

    async def publish_partner_event(self, partner: Partner) -> None:
        acceptance_terms = AcceptanceTermsRecord(
            commission_type=partner.acceptance_terms.commission_type,
            commission_rate=partner.acceptance_terms.commission_rate,
            cookie_duration_days=partner.acceptance_terms.cookie_duration_days,
            promotional_methods=partner.acceptance_terms.promotional_methods,
        )
        record = PartnerRecord(
            partner_id=partner.partner_id,
            partner_type=partner.partner_type,
            acceptance_terms=acceptance_terms,
            estimated_monthly_reach=partner.estimated_monthly_reach,
        )
        self.partner_producer.send(record)
        logger.info(f"Event sent for partner: {partner.partner_id}")

    async def publish_campaign_event(self, campaign_id: str, name: str) -> None:
        record = CampaignRecord(
            campaign_id=campaign_id,
            name=name,
        )
        self.campaign_producer.send(record)
        logger.info(f"Event sent for campaign: {campaign_id}")

    async def publish_association_event(
        self, campaign_id: str, partner_id: str
    ) -> None:
        record = CampaignPartnerAssociationRecord(
            campaign_id=campaign_id,
            partner_id=partner_id,
        )
        self.association_producer.send(record)
        logger.info(
            f"Event sent for campaign-partner association: {campaign_id} - {partner_id}"
        )

    async def publish_content_event(
        self, content_id: str, campaign_id: str, content_url: str
    ) -> None:
        record = ContentAssociationRecord(
            content_id=content_id,
            campaign_id=campaign_id,
            content_url=content_url,
        )
        self.content_producer.send(record)
        logger.info(
            f"Event sent for content association: {content_id} to campaign {campaign_id}"
        )

    async def publish_tracking_event(self, campaign_id: str, event_type: str) -> None:
        from datetime import datetime

        timestamp = datetime.utcnow().isoformat()
        record = TrackingEventRecord(
            campaign_id=campaign_id,
            event_type=event_type,
            timestamp=timestamp,
        )
        self.tracking_producer.send(record)
        logger.info(f"Event sent for tracking: {event_type} on campaign {campaign_id}")

    async def publish_fail_tracking_event(self, tracking_id: int) -> None:
        record = FailTrackingEventRecord(
            tracking_id=str(tracking_id),
        )
        self.fail_producer.send(record)
        logger.info(f"Fail event sent for tracking_id: {tracking_id}")

    async def disconnect(self):
        if self.partner_producer:
            self.partner_producer.close()
        if self.campaign_producer:
            self.campaign_producer.close()
        if self.association_producer:
            self.association_producer.close()
        if self.content_producer:
            self.content_producer.close()
        if self.tracking_producer:
            self.tracking_producer.close()
        if self.fail_producer:
            self.fail_producer.close()
        if self.client:
            self.client.close()
        logger.info("Pulsar producers disconnected")
