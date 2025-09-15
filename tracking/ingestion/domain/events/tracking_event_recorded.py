from dataclasses import dataclass
from uuid import UUID
from seedwork.domain.domain_event import DomainEvent


@dataclass
class TrackingEventRecorded(DomainEvent):
    """Event published when tracking event is recorded"""

    tracking_event_id: UUID = None
    partner_id: str = None
    campaign_id: str = None
    visitor_id: str = None
    interaction_type: str = None

    def event_type(self) -> str:
        return "tracking_event.recorded.v1"
