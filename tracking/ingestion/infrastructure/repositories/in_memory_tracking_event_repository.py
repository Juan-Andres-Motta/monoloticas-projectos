from typing import Dict, Optional
from uuid import UUID
from ...domain.repositories.tracking_event_repository import TrackingEventRepository
from ...domain.aggregates.tracking_event import TrackingEvent


class InMemoryTrackingEventRepository(TrackingEventRepository):
    """In-memory adapter for tracking event repository"""

    def __init__(self):
        self._tracking_events: Dict[UUID, TrackingEvent] = {}

    async def save(self, tracking_event: TrackingEvent) -> None:
        """Save tracking event to memory"""
        self._tracking_events[tracking_event.tracking_event_id] = tracking_event
        print(f"Saved tracking event: {tracking_event.tracking_event_id}")

    async def get_by_id(self, tracking_event_id: UUID) -> Optional[TrackingEvent]:
        """Get tracking event from memory"""
        return self._tracking_events.get(tracking_event_id)

    def get_all(self) -> Dict[UUID, TrackingEvent]:
        """Debug method to see all stored events"""
        return self._tracking_events.copy()
