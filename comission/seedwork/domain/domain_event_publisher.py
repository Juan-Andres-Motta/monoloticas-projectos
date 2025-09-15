from abc import ABC, abstractmethod
from typing import List, Dict, Type
from .domain_event import DomainEvent
from .domain_event_handler import DomainEventHandler


class DomainEventPublisher(ABC):
    """Abstract base class for domain event publishers"""

    @abstractmethod
    async def publish(self, events: List[DomainEvent]) -> None:
        """Publish domain events"""
        pass


class InMemoryDomainEventPublisher(DomainEventPublisher):
    """In-memory implementation of domain event publisher"""

    def __init__(self):
        self._handlers: Dict[str, List[DomainEventHandler]] = {}

    def register_handler(self, event_type: str, handler: DomainEventHandler) -> None:
        """Register a handler for a specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, events: List[DomainEvent]) -> None:
        """Publish events to registered handlers"""
        for event in events:
            event_type = event.event_type()
            handlers = self._handlers.get(event_type, [])

            for handler in handlers:
                await handler.handle(event)
