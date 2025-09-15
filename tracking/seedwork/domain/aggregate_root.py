from abc import ABC
from dataclasses import dataclass, field
from typing import List
from uuid import UUID
from .domain_event import DomainEvent


@dataclass
class AggregateRoot(ABC):
    """Base aggregate root with domain events"""

    _domain_events: List[DomainEvent] = field(
        default_factory=list, init=False, repr=False
    )

    def add_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_domain_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
