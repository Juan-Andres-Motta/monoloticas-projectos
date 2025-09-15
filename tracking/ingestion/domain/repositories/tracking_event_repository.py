from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from ..aggregates.tracking_event import TrackingEvent


class TrackingEventRepository(ABC):
    """Port for tracking event persistence"""

    @abstractmethod
    async def save(self, tracking_event: TrackingEvent) -> None:
        """Save tracking event"""
        pass

    @abstractmethod
    async def get_by_id(self, tracking_event_id: UUID) -> Optional[TrackingEvent]:
        """Get tracking event by ID"""
        pass
