from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from seedwork.domain.aggregate_root import AggregateRoot
from ..events.tracking_event_recorded import TrackingEventRecorded


@dataclass
class TrackingEvent(AggregateRoot):
    """Tracking Event Aggregate Root"""

    partner_id: str
    campaign_id: str
    visitor_id: str
    interaction_type: str
    source_url: str
    destination_url: str
    tracking_event_id: UUID = field(default_factory=uuid4)
    recorded_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def record_new_interaction(
        cls,
        partner_id: str,
        campaign_id: str,
        visitor_id: str,
        interaction_type: str,
        source_url: str,
        destination_url: str,
    ) -> "TrackingEvent":
        """Factory method to create new tracking event"""

        tracking_event = cls(
            partner_id=partner_id,
            campaign_id=campaign_id,
            visitor_id=visitor_id,
            interaction_type=interaction_type,
            source_url=source_url,
            destination_url=destination_url,
        )

        # Apply business rules
        if not cls._is_valid_interaction(interaction_type):
            raise ValueError(f"Invalid interaction type: {interaction_type}")

        # Publish domain event
        event = TrackingEventRecorded(
            tracking_event_id=tracking_event.tracking_event_id,
            partner_id=partner_id,
            campaign_id=campaign_id,
            visitor_id=visitor_id,
            interaction_type=interaction_type,
        )
        tracking_event.add_domain_event(event)

        return tracking_event

    @staticmethod
    def _is_valid_interaction(interaction_type: str) -> bool:
        """Business rule: validate interaction types"""
        valid_types = ["click", "view", "engagement"]
        return interaction_type in valid_types
