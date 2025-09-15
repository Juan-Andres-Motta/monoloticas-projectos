from abc import ABC, abstractmethod
from typing import List
from seedwork.domain.domain_event import DomainEvent


class DomainEventPublisher(ABC):
    """Abstract domain event publisher"""

    @abstractmethod
    async def publish(self, events: List[DomainEvent]) -> None:
        """Publish domain events"""
        pass


class InMemoryDomainEventPublisher(DomainEventPublisher):
    """In-memory domain event publisher for development/testing"""

    def __init__(self):
        self._handlers = {}

    def register_handler(self, event_type: str, handler):
        """Register an event handler for a specific event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, events: List[DomainEvent]) -> None:
        """Publish events to registered handlers"""
        for event in events:
            event_type = event.event_type()
            if event_type in self._handlers:
                for handler in self._handlers[event_type]:
                    try:
                        await handler.handle(event)
                    except Exception as e:
                        # Log error but don't stop processing other handlers
                        print(f"Error processing event {event_type}: {e}")
                        # In production, you'd use proper logging here
