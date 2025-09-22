from abc import ABC, abstractmethod
from src.domain.entities.tracking_event import TrackingEvent


class TrackingEventRepository(ABC):
    @abstractmethod
    async def save(self, tracking_event: TrackingEvent) -> int:
        pass

    @abstractmethod
    async def update_status(self, tracking_id: int, status: str) -> None:
        pass
