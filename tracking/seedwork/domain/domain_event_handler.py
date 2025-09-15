from abc import ABC, abstractmethod
from seedwork.domain.domain_event import DomainEvent


class DomainEventHandler(ABC):
    """Base class for domain event handlers"""

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle a domain event"""
        pass
