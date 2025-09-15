from seedwork.domain.domain_event_handler import DomainEventHandler
from seedwork.domain.domain_event import DomainEvent
from ingestion.domain.events.tracking_event_recorded import TrackingEventRecorded


class PulsarEventHandler(DomainEventHandler):
    """Handles tracking events by publishing to Pulsar"""

    def __init__(self, pulsar_publisher=None):
        self._pulsar_publisher = pulsar_publisher

    async def handle(self, event: DomainEvent) -> None:
        """Process tracking event and publish to Pulsar"""
        if isinstance(event, TrackingEventRecorded):
            await self._publish_to_pulsar(event)

    async def _publish_to_pulsar(self, event: TrackingEventRecorded) -> None:
        """Publish tracking event to Pulsar for commission service consumption"""
        print(
            f"📡 Attempting to publish tracking event to Pulsar: {event.tracking_event_id}"
        )

        if self._pulsar_publisher:
            try:
                await self._pulsar_publisher.publish_tracking_event(
                    tracking_event_id=event.tracking_event_id,
                    partner_id=event.partner_id,
                    campaign_id=event.campaign_id,
                    visitor_id=event.visitor_id,
                    interaction_type=event.interaction_type,
                )
                print(
                    f"✅ Successfully published tracking event: {event.tracking_event_id}"
                )
            except Exception as e:
                print(f"❌ Failed to publish to Pulsar: {e}")
                print("🔄 Event processing continues without Pulsar")
        else:
            print("⚠️  Pulsar publisher not available - skipping event publishing")
