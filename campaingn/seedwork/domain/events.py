"""
Domain Events Base Classes
"""

from datetime import datetime
from uuid import UUID
from typing import Any, Dict
from abc import ABC, abstractmethod


class DomainEvent(ABC):
    """Base class for all domain events"""

    def __init__(self, aggregate_id: UUID):
        self.aggregate_id = aggregate_id
        self.occurred_on = datetime.utcnow()

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        pass

    def __eq__(self, other):
        if not isinstance(other, DomainEvent):
            return False
        return (
            self.aggregate_id == other.aggregate_id
            and self.occurred_on == other.occurred_on
        )

    def __hash__(self):
        return hash((str(self.aggregate_id), self.occurred_on))
