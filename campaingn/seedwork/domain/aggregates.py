"""
Aggregate Root Base Class
"""

from uuid import UUID
from typing import List
from .events import DomainEvent


class AggregateRoot:
    """Base class for aggregate roots in domain-driven design"""

    def __init__(self, aggregate_id: UUID):
        self.id = aggregate_id
        self._events: List[DomainEvent] = []

    def add_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published"""
        self._events.append(event)

    def clear_events(self) -> None:
        """Clear all domain events"""
        self._events.clear()

    @property
    def events(self) -> List[DomainEvent]:
        """Get all domain events"""
        return self._events.copy()

    def __eq__(self, other):
        if not isinstance(other, AggregateRoot):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(str(self.id))
