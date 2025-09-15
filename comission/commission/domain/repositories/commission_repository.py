from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from ..aggregates.commission import Commission


class CommissionRepository(ABC):
    """Abstract repository for Commission aggregate"""

    @abstractmethod
    async def save(self, commission: Commission) -> None:
        """Save commission to repository"""
        pass

    @abstractmethod
    async def find_by_id(self, commission_id: UUID) -> Optional[Commission]:
        """Find commission by ID"""
        pass

    @abstractmethod
    async def find_by_tracking_event_id(
        self, tracking_event_id: UUID
    ) -> Optional[Commission]:
        """Find commission by tracking event ID"""
        pass

    @abstractmethod
    async def find_by_partner_id(
        self, partner_id: str, limit: int = 100
    ) -> List[Commission]:
        """Find commissions by partner ID"""
        pass

    @abstractmethod
    async def find_by_campaign_id(
        self, campaign_id: str, limit: int = 100
    ) -> List[Commission]:
        """Find commissions by campaign ID"""
        pass
