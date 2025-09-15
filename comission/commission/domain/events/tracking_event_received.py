from dataclasses import dataclass
from uuid import UUID
from seedwork.domain.domain_event import DomainEvent


@dataclass
class TrackingEventReceived(DomainEvent):
    """Event representing received tracking event for commission processing"""

    tracking_event_id: UUID = None
    partner_id: str = None
    campaign_id: str = None
    visitor_id: str = None
    interaction_type: str = None

    def event_type(self) -> str:
        return "tracking_event.received.v1"
