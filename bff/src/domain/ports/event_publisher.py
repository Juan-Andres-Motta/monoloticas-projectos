from abc import ABC, abstractmethod
from src.domain.entities.partner import Partner
from src.domain.entities.payment import Payment


class EventPublisher(ABC):
    @abstractmethod
    async def publish_partner_event(self, partner: Partner) -> None:
        pass

    @abstractmethod
    async def publish_campaign_event(self, campaign_id: str, name: str) -> None:
        pass

    @abstractmethod
    async def publish_association_event(
        self, campaign_id: str, partner_id: str
    ) -> None:
        pass

    @abstractmethod
    async def publish_content_event(
        self, content_id: str, campaign_id: str, content_url: str
    ) -> None:
        pass

    @abstractmethod
    async def publish_tracking_event(self, campaign_id: str, event_type: str) -> None:
        pass

    @abstractmethod
    async def publish_fail_tracking_event(self, tracking_id: int) -> None:
        pass

    @abstractmethod
    async def publish_payment_event(self, payment: Payment) -> None:
        pass
